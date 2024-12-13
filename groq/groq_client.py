import logging
from typing import List

from groq import Groq  # type: ignore

logger = logging.getLogger(__name__)

__all__ = ["GroqTaggingClient"]


class GroqTaggingClient:
    def __init__(
        self, api_key: str, model: str = "llama-3.2-11b-vision-preview"
    ) -> None:
        self.client = Groq(api_key=api_key.replace('"', "").replace("'", ""))
        self.model = model

    def message(self, caption_request: str, image_urls: List[str]) -> str:
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
            }
            for image_url in image_urls
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=1024,
            stream=False,
            stop=None,
        )
        logger.info(response.choices[0].message.content)
        return response.choices[0].message.content
