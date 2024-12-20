import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest

from main import process_images
from utils.image_utils import encode_image, is_image

# Test data setup
TEST_IMAGE_PATH = "tests/images/800px-Another_Day_in_NYC_(2539547867).jpg"
TEST_IMAGE_DIR = "tests/images/"
TEST_OUTPUT_PATH = "tests/output.json"
INVALID_IMAGE_PATH = "tests/images/non_existent_image.jpg"


# Mock image utility functions
def test_is_image():
    with patch("imghdr.what", return_value="jpeg"):
        assert is_image(TEST_IMAGE_PATH) is True

    with patch("imghdr.what", return_value=None):
        assert is_image(TEST_IMAGE_PATH) is False


def test_encode_image():
    with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
        result = encode_image(TEST_IMAGE_PATH)
        assert result == "ZmFrZV9pbWFnZV9kYXRh" 

@patch.dict(os.environ, {"GROQ_API_KEY": "mocked-api-key"})
def test_process_images_with_mocked_groq():
    mocked_client = Mock()
    mocked_client.message.return_value = json.dumps(
        {"tags": ["test"], "categories": ["example"]}
    )

    with patch("main.GroqTaggingClient", return_value=mocked_client):
        inputs = [TEST_IMAGE_PATH]
        custom_prompt = "Test prompt"
        model = "test-model"

        # Ensure output file is removed before the test
        if os.path.exists(TEST_OUTPUT_PATH):
            os.remove(TEST_OUTPUT_PATH)

        process_images(inputs, TEST_OUTPUT_PATH, custom_prompt, model)

        # Verify the output file is created
        assert os.path.exists(TEST_OUTPUT_PATH)

        # Verify the content of the output
        with open(TEST_OUTPUT_PATH, "r") as f:
            output_data = json.load(f)

        assert TEST_IMAGE_PATH in output_data
        assert output_data[TEST_IMAGE_PATH]["tags"] == ["test"]
        assert output_data[TEST_IMAGE_PATH]["categories"] == ["example"]

        # Clean up
        os.remove(TEST_OUTPUT_PATH)

@patch.dict(os.environ, {"GROQ_API_KEY": "mocked-api-key"})
def test_process_images_with_real_images():
    custom_prompt = "Real test prompt"
    model = "real-test-model"

    # Ensure output file is removed before the test
    if os.path.exists(TEST_OUTPUT_PATH):
        os.remove(TEST_OUTPUT_PATH)

    process_images([TEST_IMAGE_PATH], TEST_OUTPUT_PATH, custom_prompt, model)

    # Verify the output file is created
    assert os.path.exists(TEST_OUTPUT_PATH)

    # Verify the content of the output
    with open(TEST_OUTPUT_PATH, "r") as f:
        output_data = json.load(f)

    assert TEST_IMAGE_PATH in output_data

    # Clean up
    os.remove(TEST_OUTPUT_PATH)

def test_process_images_missing_api_key():
    custom_prompt = "Missing API Key Test"
    model = "test-model"

    # Temporarily unset the API key
    with patch.dict("os.environ", {"GROQ_API_KEY": ""}):
        with pytest.raises(ValueError, match="GROQ_API_KEY is not set in the .env file"):
            process_images([TEST_IMAGE_PATH], TEST_OUTPUT_PATH, custom_prompt, model)

@patch.dict(os.environ, {"GROQ_API_KEY": "mocked-api-key"})
def test_process_images_invalid_image_path():
    custom_prompt = "Invalid Image Path Test"
    model = "test-model"

    # Ensure output file is removed before the test
    if os.path.exists(TEST_OUTPUT_PATH):
        os.remove(TEST_OUTPUT_PATH)

    with pytest.raises(FileNotFoundError):
        process_images([INVALID_IMAGE_PATH], TEST_OUTPUT_PATH, custom_prompt, model)


# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", "--disable-warnings"])
