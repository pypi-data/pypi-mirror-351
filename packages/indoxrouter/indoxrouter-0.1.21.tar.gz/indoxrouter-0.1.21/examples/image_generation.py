"""
Example script demonstrating image generation with various providers through indoxRouter.

This script shows how to generate images using different providers (OpenAI, xAI, Google)
and how to handle the responses to display or save the generated images.

Requirements:
- Install indoxRouter: pip install indoxrouter
- Set INDOX_ROUTER_API_KEY environment variable with your API key
"""

import os
import base64
from io import BytesIO
import requests
from datetime import datetime

from indoxrouter import Client

# For displaying images in notebooks
try:
    from IPython.display import Image, display

    in_notebook = True
except ImportError:
    in_notebook = False

# Initialize client with API key from environment variable
client = Client()


def save_image_from_url(url, filename):
    """Download and save an image from a URL."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {filename}")
    else:
        print(f"Failed to download image: {response.status_code}")


def save_image_from_b64(b64_data, filename):
    """Save an image from base64 data."""
    image_data = base64.b64decode(b64_data)
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"Image saved to {filename}")


def generate_and_save_image(provider, model, prompt):
    """Generate an image and save it to a file."""
    print(f"\n=== Generating image with {provider}/{model} ===")
    print(f"Prompt: {prompt}")

    try:
        # Generate the image
        response = client.images(
            prompt=prompt,
            model=f"{provider}/{model}",
            size="1024x1024",
        )

        print(f"Response received from {provider}:")
        print(f"- Success: {response['success']}")
        print(f"- Cost: ${response['usage']['cost']:.4f}")

        # Check if we have image data
        if "data" in response and response["data"]:
            image_data = response["data"][0]

            # Create a timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if "url" in image_data and image_data["url"]:
                filename = f"{provider}_{model}_{timestamp}.png"
                save_image_from_url(image_data["url"], filename)

                # Display in notebook if possible
                if in_notebook:
                    display(Image(url=image_data["url"]))

            elif "b64_json" in image_data and image_data["b64_json"]:
                filename = f"{provider}_{model}_{timestamp}.png"
                save_image_from_b64(image_data["b64_json"], filename)

                # Display in notebook if possible
                if in_notebook:
                    display(Image(data=base64.b64decode(image_data["b64_json"])))

            # Check for revised prompt (DALL-E 3 often revises prompts)
            if "revised_prompt" in image_data and image_data["revised_prompt"]:
                print(f"Revised prompt: {image_data['revised_prompt']}")
        else:
            print("No image data found in response")
            print("Response:", response)

    except Exception as e:
        print(f"Error generating image with {provider}/{model}: {str(e)}")


# Example prompts
prompts = {
    "landscape": "A beautiful mountain landscape with a lake at sunset",
    "animal": "A cute puppy playing with a ball in a garden",
    "abstract": "An abstract digital art piece with vibrant colors and geometric shapes",
    "space": "A realistic view of Earth from space with the moon in the background",
}


def main():
    # Test OpenAI models
    generate_and_save_image("openai", "dall-e-2", prompts["landscape"])
    generate_and_save_image("openai", "dall-e-3", prompts["animal"])

    # Test with gpt-image-1 if available
    try:
        generate_and_save_image("openai", "gpt-image-1", prompts["abstract"])
    except Exception as e:
        print(f"gpt-image-1 test skipped: {str(e)}")

    # Test xAI models
    try:
        generate_and_save_image("xai", "grok-2-image", prompts["space"])
    except Exception as e:
        print(f"xAI test skipped: {str(e)}")

    # Test Google models
    try:
        generate_and_save_image(
            "google", "imagen-3.0-generate-002", prompts["abstract"]
        )
    except Exception as e:
        print(f"Google test skipped: {str(e)}")

    # Close the client
    client.close()


if __name__ == "__main__":
    main()
