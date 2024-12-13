from dataclasses import dataclass
import json
import logging
from typing import List

from groq import Groq

from utils.log_utils import config_logs # type: ignore

config_logs()
logger = logging.getLogger(__name__)

__all__ = ["GroqTaggingClient"]



class GroqTaggingClient:
    def __init__(
        self, api_key: str, model: str = "llama-3.2-11b-vision-preview"
    ) -> None:
        self.client = Groq(api_key=api_key.replace('"', "").replace("'", ""))
        self.model = model


    def message(self, caption_request: str, image_url: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption_request},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "high"},
                    },
                ],
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=1024,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        return response.choices[0].message.content.replace("\n", " ")
