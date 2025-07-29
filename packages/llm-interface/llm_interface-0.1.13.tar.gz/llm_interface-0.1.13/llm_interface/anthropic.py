# Copyright 2024 Niels Provos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from anthropic import Anthropic, APIConnectionError, APIError, APITimeoutError
from ollama import ListResponse

from . import errors
from .utils import encode_image_to_base64


def translate_tools_for_anthropic(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Translate a list of tools from Ollama/API format to Anthropic format.

    Args:
        tools (List[Tool]): List of tool objects from the Ollama/API.

    Returns:
        List[Dict[str, Any]]: Translated tools ready for Anthropic API consumption.
    """
    anthropic_tools = []

    for tool in tools:
        # Extract the function from the tool
        function = tool["function"]

        # Assuming Tool objects have keys 'name', 'description', and 'parameters' which is a dict
        translated_tool = {
            "name": function["name"],
            "description": function["description"],
            "input_schema": {
                "type": "object",
                "properties": function["parameters"]["properties"],
                "required": function["parameters"]["required"],
            },
        }
        anthropic_tools.append(translated_tool)

    return anthropic_tools


def translate_messages_for_anthropic(
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Translate messages from Ollama/API format to Anthropic format.

    Args:
        messages (List[Dict[str, Any]]): List of message dictionaries in Ollama format

    Returns:
        List[Dict[str, Any]]: Translated messages in Anthropic format
    """
    translated_messages = []

    for msg in messages:
        if "images" in msg and msg["images"]:
            content = [{"type": "text", "text": msg["content"]}]
            for image in msg["images"]:
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "data": encode_image_to_base64(image),
                            "media_type": "image/jpeg",
                        },
                    }
                )
            translated_messages.append({"role": "user", "content": content})
        elif msg["role"] == "user":
            # Regular user messages pass through unchanged
            translated_messages.append({"role": "user", "content": msg["content"]})

        elif msg["role"] == "assistant" and "tool_calls" in msg:
            # Convert assistant tool calls to Anthropic format
            tool_call = msg["tool_calls"][0]  # Assume single tool call for now
            translated_messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": f"<thinking>I need to use {tool_call['function']['name']} to help answer this question.</thinking>",
                        },
                        {
                            "type": "tool_use",
                            "id": tool_call["id"],
                            "name": tool_call["function"]["name"],
                            "input": tool_call["function"]["arguments"],
                        },
                    ],
                }
            )

        elif msg["role"] == "tool":
            # Convert tool response to Anthropic's tool_result format
            translated_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_call_id"],
                            "content": msg["content"],
                        }
                    ],
                }
            )
        elif msg["role"] == "assistant":
            translated_messages.append(msg)
        else:
            raise ValueError(f"Unknown message role: {msg['role']}")

    return translated_messages


def convert_anthropic_models_to_ollama_response(
    models_data: Dict[str, Any],
) -> ListResponse:
    """
    Converts Anthropic model list API response to Ollama format.

    Args:
        models_data: The response from Anthropic's models API endpoint.

    Returns:
        An instance of ollama's ListResponse.
    """
    ollama_models = []
    for model_data in models_data["data"]:
        # Convert creation time from ISO format to datetime
        created_at = datetime.fromisoformat(
            model_data["created_at"].replace("Z", "+00:00")
        )

        model = {
            "model": model_data["id"],
            "modified_at": created_at,
            "digest": "unknown",
            "size": 0,
            "details": {
                "parent_model": "",
                "format": "unknown",
                "family": "claude",
                "families": ["claude"],
                "parameter_size": "unknown",
                "quantization_level": "unknown",
                "display_name": model_data["display_name"],
            },
        }
        ollama_models.append(ListResponse.Model(**model))

    return ListResponse(models=ollama_models)


class AnthropicWrapper:
    def __init__(self, api_key: str, max_tokens: int = 4096, timeout: float = 600.0):
        self.client = Anthropic(api_key=api_key, timeout=timeout)
        self.api_key = api_key
        self.max_tokens = max_tokens

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Conduct a chat conversation using the Anthropic API.

        Args:
            messages (list[Mapping[str, str]]): A list of message dictionaries, each containing 'role' and 'content'.
            **kwargs: Additional arguments to pass to the generate function.

        Returns:
            A dictionary containing the Anthropic response formatted to match Ollama's expected output.
        """
        # Extract the system message from the messages and prepare it as a separate argument
        system_message = next(
            (msg["content"] for msg in messages if msg["role"] == "system"), None
        )

        # Filter out the system message to prevent duplication if it's not needed in the messages parameter
        filtered_messages = [msg for msg in messages if msg["role"] != "system"]

        # Translate messages into Anthropic format
        if any(msg["role"] == "tool" for msg in filtered_messages) or any(
            "images" in msg for msg in filtered_messages
        ):
            filtered_messages = translate_messages_for_anthropic(filtered_messages)

        # Common parameters
        params = {
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": filtered_messages,
            "model": kwargs.get("model", "claude-3-5-sonnet-20240620"),
        }

        # Only include system parameter if it has a value
        if system_message is not None:
            params["system"] = system_message

        # Conditionally add temperature if it exists in kwargs
        if "options" in kwargs:
            if "temperature" in kwargs["options"]:
                params["temperature"] = kwargs["options"]["temperature"]

        if tools:
            # Translate tools into Anthropic format
            anthropic_tools = translate_tools_for_anthropic(tools)
            params["tools"] = anthropic_tools

        try:
            # Call the function with the constructed parameters
            response = self.client.messages.create(**params)

            # Extract usage information
            usage = response.usage
            usage_info = {
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "cached_tokens": usage.cache_read_input_tokens,
                "total_tokens": usage.input_tokens + usage.output_tokens,
            }

            # Handle tool calls if present
            if any(block.type == "tool_use" for block in response.content):
                # Find all tool use blocks
                tool_use_blocks = [
                    block for block in response.content if block.type == "tool_use"
                ]

                return {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": tool_block.id,
                                "name": tool_block.name,
                                "arguments": tool_block.input,  # Anthropic uses 'input' instead of 'arguments'
                            }
                            for tool_block in tool_use_blocks
                        ],
                    },
                    "usage": usage_info,
                    "done": response.stop_reason == "end_turn",
                }

            # Extract content blocks as text and simulate Ollama-like response
            content = "".join(
                block.text for block in response.content if block.type == "text"
            )

            return {
                "message": {"content": content},
                "usage": usage_info,
                "done": response.stop_reason == "end_turn",
            }

        except APITimeoutError as e:
            error_message = f"Anthropic API timeout: {str(e)}"
            logging.error(error_message)
            return {
                "error": error_message,
                "error_type": errors.TIMEOUT,
                "content": None,
                "done": False,
                "usage": None,
            }
        except APIConnectionError as e:
            error_message = f"Anthropic API connection error: {str(e)}"
            logging.error(error_message)
            return {
                "error": error_message,
                "error_type": errors.CONNECTION,
                "content": None,
                "done": False,
                "usage": None,
            }
        except APIError as e:
            error_message = f"Anthropic API error: {str(e)}"
            logging.error(error_message)
            return {
                "error": error_message,
                "error_type": errors.PROVIDER_SPECIFIC,
                "content": None,
                "done": False,
                "usage": None,
            }

    def list(self) -> ListResponse:
        """
        Returns a list of available Anthropic models in Ollama format.
        Uses the Anthropic API to get the current list of models.
        """
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}

        response = requests.get("https://api.anthropic.com/v1/models", headers=headers)
        response.raise_for_status()

        return convert_anthropic_models_to_ollama_response(response.json())
