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
import base64
import logging
import os
from datetime import datetime
from typing import Optional


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def setup_logging(
    logs_dir: str = "logs",
    logs_prefix="general_log",
    logger_name: Optional[str] = None,
    level: Optional[int] = logging.INFO,
) -> logging.Logger:
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"{logs_prefix}_{timestamp}.log")

    logger = logging.getLogger(name=logger_name)
    logger.handlers = []
    logger.setLevel(level)

    # Create file handler but don't create the file until the first emit
    file_handler = logging.FileHandler(log_file, mode="w", delay=True)
    file_handler.setLevel(level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
