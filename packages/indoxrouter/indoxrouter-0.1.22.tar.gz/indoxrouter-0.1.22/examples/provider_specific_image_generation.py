"""
Example script demonstrating image generation with different providers through indoxRouter.

This script shows how to generate images using different providers (OpenAI, Google, xAI)
with their provider-specific parameters and handling.

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


def display_response_image(response, provider, model):
    """Display image from response and save it."""
    try:
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
    except Exception as e:
        print(f"Error displaying/saving image: {str(e)}")


def main():
    """Main function demonstrating image generation with different providers."""

    # Example prompt for all providers
    prompt = "A tranquil zen garden with cherry blossoms and a small pond"

    print("\n=== OpenAI (DALL-E 2) ===")
    print("Uses pixel dimensions (e.g., '1024x1024')")
    try:
        openai_response = client.images(
            prompt=prompt,
            model="openai/dall-e-2",
            size="1024x1024",  # OpenAI uses pixel dimensions
        )
        print(f"Response received - Success: {openai_response.get('success', False)}")
        print(f"Cost: ${openai_response.get('usage', {}).get('cost', 0):.4f}")
        display_response_image(openai_response, "openai", "dall-e-2")
    except Exception as e:
        print(f"Error with OpenAI: {str(e)}")

    print("\n=== OpenAI (GPT-image-1) ===")
    print("Uses pixel dimensions (e.g., '1024x1024')")
    try:
        # For GPT-image-1, don't include response_format parameter unless you specify it
        gpt_image_response = client.images(
            prompt=prompt,
            model="openai/gpt-image-1",
            size="1024x1024",  # OpenAI uses pixel dimensions
            # Note: don't include response_format parameter unless explicitly needed
        )
        print(
            f"Response received - Success: {gpt_image_response.get('success', False)}"
        )
        print(f"Cost: ${gpt_image_response.get('usage', {}).get('cost', 0):.4f}")
        display_response_image(gpt_image_response, "openai", "gpt-image-1")
    except Exception as e:
        print(f"Error with GPT-image-1: {str(e)}")

    print("\n=== Google (Imagen) ===")
    print("Uses aspect ratios (e.g., '1:1', '16:9') instead of pixel dimensions")
    try:
        google_response = client.images(
            prompt=prompt,
            model="google/imagen-3.0-generate-002",
            # Note: Use 'aspect_ratio' instead of 'size' for Google
            aspect_ratio="1:1",  # Google uses aspect ratios
            negative_prompt="cartoon, illustration, drawing, painting",
        )
        print(f"Response received - Success: {google_response.get('success', False)}")
        print(f"Cost: ${google_response.get('usage', {}).get('cost', 0):.4f}")
        display_response_image(google_response, "google", "imagen")
    except Exception as e:
        print(f"Error with Google: {str(e)}")

    print("\n=== xAI (Grok) ===")
    print("Does not use size parameter, only supports specific parameters")
    try:
        xai_response = client.images(
            prompt=prompt,
            model="xai/grok-2-image",
            # Note: xAI doesn't support size parameter, so we don't include it
            # Only include specific parameters that xAI supports
            response_format="url",  # xAI supports response_format
        )
        print(f"Response received - Success: {xai_response.get('success', False)}")
        print(f"Cost: ${xai_response.get('usage', {}).get('cost', 0):.4f}")
        display_response_image(xai_response, "xai", "grok-2-image")
    except Exception as e:
        print(f"Error with xAI: {str(e)}")

    # Advanced example with DALL-E 3
    print("\n=== OpenAI (DALL-E 3) with Advanced Parameters ===")
    try:
        dalle3_response = client.images(
            prompt="A beautiful underwater scene with coral reef and tropical fish",
            model="openai/dall-e-3",
            size="1024x1024",
            quality="standard",  # 'standard' or 'hd'
            style="vivid",  # 'vivid' or 'natural'
            response_format="url",
        )
        print(f"Response received - Success: {dalle3_response.get('success', False)}")
        print(f"Cost: ${dalle3_response.get('usage', {}).get('cost', 0):.4f}")
        display_response_image(dalle3_response, "openai", "dall-e-3")
    except Exception as e:
        print(f"Error with DALL-E 3: {str(e)}")

    print("\n=== Provider-Specific Parameter Examples ===")
    print("Each provider supports different parameters:")
    print("OpenAI: size, quality, style, background, response_format...")
    print("Google: aspect_ratio, negative_prompt, guidance_scale, seed...")
    print("xAI: n, response_format (minimal parameters)")
    print(
        "\nRefer to the documentation for the complete list of parameters for each provider."
    )

    # Close the client when done
    client.close()


if __name__ == "__main__":
    main()
