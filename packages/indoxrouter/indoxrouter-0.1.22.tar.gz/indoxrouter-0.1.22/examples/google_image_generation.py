"""
Example script demonstrating Google image generation through indoxRouter.

This script shows how to generate images using Google's Imagen models
with their specific parameters, especially aspect_ratio instead of size.

Requirements:
- Install indoxRouter: pip install indoxrouter
- Set INDOX_ROUTER_API_KEY environment variable with your API key
"""

import os
from indoxrouter import Client

# Initialize client with API key from environment variable
api_key = os.environ.get("INDOX_ROUTER_API_KEY")
if not api_key:
    print("Please set the INDOX_ROUTER_API_KEY environment variable")
    exit(1)

client = Client(api_key=api_key)


def generate_image(model, prompt, **kwargs):
    """Generate an image with the specified Google model and parameters."""
    print(f"\n=== Generating image with {model} ===")
    print(f"Prompt: {prompt}")

    try:
        response = client.images(prompt=prompt, model=f"google/{model}", **kwargs)

        # Print the URL of the generated image
        if "data" in response and response["data"] and "url" in response["data"][0]:
            print(f"Image URL: {response['data'][0]['url']}")

        # Print usage/cost information if available
        if "usage" in response and "cost" in response["usage"]:
            print(f"Cost: ${response['usage']['cost']:.4f}")

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def main():
    """Main function demonstrating Google image generation."""

    # Basic example with square aspect ratio
    imagen_square = generate_image(
        model="imagen-3.0-generate-002",
        prompt="A serene Japanese garden with a koi pond",
        aspect_ratio="1:1",  # Use aspect_ratio instead of size
        response_format="url",
    )

    # Example with landscape aspect ratio
    imagen_landscape = generate_image(
        model="imagen-3.0-generate-002",
        prompt="A panoramic view of the Grand Canyon at sunset",
        aspect_ratio="16:9",  # Landscape orientation
        response_format="url",
    )

    # Example with portrait aspect ratio
    imagen_portrait = generate_image(
        model="imagen-3.0-generate-002",
        prompt="A tall redwood tree in a misty forest",
        aspect_ratio="9:16",  # Portrait orientation
        response_format="url",
    )

    # Example with additional parameters
    imagen_advanced = generate_image(
        model="imagen-3.0-generate-002",
        prompt="A cyberpunk cityscape with neon lights and flying vehicles",
        aspect_ratio="4:3",
        negative_prompt="cartoon, illustration, drawing, painting",  # What to avoid
        guidance_scale=12.0,  # Controls adherence to the text prompt (7-20)
        seed=12345,  # For reproducible results
        response_format="url",
    )

    # Close the client when done
    client.close()


if __name__ == "__main__":
    main()
