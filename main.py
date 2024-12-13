import argparse
from dataclasses import dataclass
import json
import logging
import os
from typing import List
from urllib.parse import urlparse

from dotenv import dotenv_values
from pydantic import BaseModel

from tag.groq_client import GroqTaggingClient
from utils.image_utils import encode_image, is_image
from utils.log_utils import config_logs

config_logs()
logger = logging.getLogger(__name__)

config = dotenv_values(".env")

@dataclass
class Tags(BaseModel):
    tags: List[str]
    categories: List[str]

def is_url(path: str) -> bool:
    print(urlparse(path).scheme)
    return urlparse(path).scheme in (
        "http",
        "https",
    )


def process_images(inputs: List[str], output: str, custom_prompt: str, model: str):
    client = GroqTaggingClient(api_key=config["GROQ_API_KEY"], model=model)

    # build up request
    image_messages = []
    for path in inputs:
        if is_url(path):
            image_messages.append(path)
        else:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if not is_image(file_path):
                        logger.error(f"{file_path} is not an image")
                        continue
                    image_messages.append(f"data:image/jpeg;base64,{encode_image(file_path)}")
            else:
                if not is_image(path):
                    logger.error(f"{path} is not an image")
                    continue
                image_messages.append(encode_image(path))

    # send request
    logger.debug(f'Inputs: {image_messages}')
    response = client.message(custom_prompt, image_messages)
    logger.info(f'Response: {response}')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse Args", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--images",
        nargs="+",
        help="Path to images to use. This can be a url, an image path, or a directory of images.",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to save the output",
        required=False,
        default="output.json",
    )

    parser.add_argument(
        "-c",
        "--custom-prompt",
        help="Custom prompt to use. This is useful if you want to override how to prompt Groq",
        required=False,
        default=f'You will be tagging the attached image similar to WD14 (1-2 word tags). You can supply as many tags as you like. This should not be a paragraph or sentence. The JSON object must use the schema: {json.dumps(Tags.model_json_schema(), indent=2)} and nothing else.',
    )

    parser.add_argument(
        "-m",
        "--model",
        help="Model to use. Please note that only certain models are capable of handling images",
        required=False,
        default="llama-3.2-11b-vision-preview",
    )

    args = parser.parse_args()
    process_images(args.images, args.output, args.custom_prompt, args.model)
