import argparse

from dotenv import dotenv_values

config = dotenv_values(".env")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse Args", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--image(s)",
        nargs="+",
        help="Path to images to use. This can be a url, an image path, or a directory of images.",
        required=False,
    )

    parser.add_argument(
        "-o", "--output", help="Path to save the output", required=False
    )

    parser.add_argument(
        "-c",
        "--custom-prompt",
        help="Custom prompt to use. This is useful if you want to override how to prompt Groq",
        required=False,
    )
