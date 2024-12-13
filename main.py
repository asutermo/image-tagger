import argparse
import json
import logging
import os
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse

from dotenv import dotenv_values
from pydantic import BaseModel  # type: ignore

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


def prompt_groq(client: GroqTaggingClient, custom_prompt: str, image_url: str) -> dict:
    try:
        return json.loads(client.message(custom_prompt, image_url))
    except Exception as e:
        logger.error(
            f"Error processing {image_url}: {e}. Check https://console.groq.com/docs/vision for reasons why this may occur"
        )
        return {
            "error": f"Error. Check https://console.groq.com/docs/vision for reasons why this may occur"
        }


def process_images(inputs: List[str], output: str, custom_prompt: str, model: str):
    api_key = config.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file")

    client = GroqTaggingClient(api_key=api_key, model=model)

    out_json = {}
    for path in inputs:
        if is_url(path):
            out_json[path] = prompt_groq(client, custom_prompt, path)
        else:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if not is_image(file_path):
                        logger.error(f"{file_path} is not an image")
                        continue
                    out_json[file_path] = prompt_groq(
                        client,
                        custom_prompt,
                        f"data:image/jpeg;base64,{encode_image(file_path)}",
                    )
            else:
                if not is_image(path):
                    logger.error(f"{path} is not an image")
                    continue
                out_json[path] = prompt_groq(
                    client,
                    custom_prompt,
                    f"data:image/jpeg;base64,{encode_image(file_path)}",
                )

    logger.info(f"Output: {out_json}")
    with open(output, "w") as f:
        json.dump(out_json, f, indent=2)


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
        default=f"You will be tagging the attached image using 1-2 words per tag. You can supply as many tags as you like. Please add 1 or 2 categories as well. This should not be a paragraph or sentence. The JSON object must use the schema: {json.dumps(Tags.model_json_schema(), indent=2)} and nothing else. What is in the image?",
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
