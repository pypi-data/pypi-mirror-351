"""
Example script demonstrating image generation with Google's Imagen model through indoxRouter.

This script shows how to properly format parameters for Google's image generation API,
including the special handling of aspect ratios and other Google-specific parameters.

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
api_key = os.environ.get("INDOX_ROUTER_API_KEY")
if not api_key:
    print("Please set the INDOX_ROUTER_API_KEY environment variable")
    exit(1)

client = Client(api_key=api_key)


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


def generate_google_image(prompt, aspect_ratio="1:1", **kwargs):
    """
    Generate an image using Google's Imagen model.

    Args:
        prompt: The text prompt to generate an image from
        aspect_ratio: The aspect ratio of the image (e.g., "1:1", "4:3", "16:9")
        **kwargs: Additional parameters to pass to the API
    """
    print(f"\n=== Generating image with Google Imagen ===")
    print(f"Prompt: {prompt}")
    print(f"Aspect ratio: {aspect_ratio}")

    try:
        # Generate the image
        # Note: The client will automatically convert "1024x1024" to "1:1" for Google models,
        # but it's more explicit to use the correct format directly
        response = client.images(
            prompt=prompt,
            model="google/imagen-3.0-generate-002",
            size=aspect_ratio,  # Google uses aspect ratios instead of pixel dimensions
            **kwargs,
        )

        print(f"Response received from Google:")
        print(f"- Success: {response['success']}")
        print(f"- Cost: ${response['usage']['cost']:.4f}")

        # Check if we have image data
        if "data" in response and response["data"]:
            image_data = response["data"][0]

            # Create a timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if "url" in image_data and image_data["url"]:
                filename = (
                    f"google_imagen_{aspect_ratio.replace(':', 'x')}_{timestamp}.png"
                )
                save_image_from_url(image_data["url"], filename)

                # Display in notebook if possible
                if in_notebook:
                    display(Image(url=image_data["url"]))

            elif "b64_json" in image_data and image_data["b64_json"]:
                filename = (
                    f"google_imagen_{aspect_ratio.replace(':', 'x')}_{timestamp}.png"
                )
                save_image_from_b64(image_data["b64_json"], filename)

                # Display in notebook if possible
                if in_notebook:
                    display(Image(data=base64.b64decode(image_data["b64_json"])))
        else:
            print("No image data found in response")
            print("Response:", response)

    except Exception as e:
        print(f"Error generating image with Google Imagen: {str(e)}")


def main():
    """Main function demonstrating Google Imagen image generation."""

    # Basic example with 1:1 aspect ratio (square image)
    generate_google_image(
        prompt="A tranquil zen garden with cherry blossoms and a small pond"
    )

    # Example with 16:9 aspect ratio (widescreen)
    generate_google_image(
        prompt="A wide panoramic view of a futuristic city skyline at sunset with flying vehicles",
        aspect_ratio="16:9",
    )

    # Example with 9:16 aspect ratio (portrait/mobile)
    generate_google_image(
        prompt="A tall waterfall surrounded by lush greenery in a tropical forest",
        aspect_ratio="9:16",
    )

    # Example with negative prompt to influence the generation
    generate_google_image(
        prompt="A detailed watercolor painting of a coastal village with boats in the harbor",
        negative_prompt="dark, moody, sketch, black and white, blurry",
    )

    # Example with more parameters
    generate_google_image(
        prompt="A beautiful tiger resting in a lush jungle environment",
        aspect_ratio="4:3",
        negative_prompt="cartoon, illustration, low quality",
        seed=123456,  # Consistent results with the same seed
        guidance_scale=7.5,  # Controls how closely the model follows the prompt (usually between 1-20)
        safety_filter_level="block_none",  # Less restrictive safety filter
    )

    # Close the client when done
    client.close()


if __name__ == "__main__":
    main()
