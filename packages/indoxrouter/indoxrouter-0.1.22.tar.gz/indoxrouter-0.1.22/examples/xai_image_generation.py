"""
Example script demonstrating xAI image generation through indoxRouter.

This script shows how to generate images using xAI's Grok model
with the correct parameters (avoiding 'size' which is not supported).

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


def generate_image(prompt, **kwargs):
    """Generate an image with xAI's Grok model."""
    print(f"\n=== Generating image with xAI Grok ===")
    print(f"Prompt: {prompt}")

    try:
        response = client.images(
            prompt=prompt,
            model="xai/grok-2-image",
            # DO NOT include 'size' parameter - it will cause an error
            **kwargs,
        )

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
    """Main function demonstrating xAI image generation."""

    # Basic example - minimal parameters
    basic_image = generate_image(
        prompt="A cybernetic fox in a futuristic city",
        # No size parameter - xAI doesn't support it
        response_format="url",  # One of the few parameters xAI supports
    )

    # Multiple images example
    multiple_images = generate_image(
        prompt="A colorful abstract painting of geometric shapes",
        n=2,  # Generate 2 images
        response_format="url",
    )

    # Example with long, detailed prompt
    detailed_prompt = generate_image(
        prompt=(
            "A steampunk-inspired mechanical dragonfly with brass gears, "
            "copper wings, and glowing blue energy cores, hovering above "
            "a Victorian-era cityscape with airships in the cloudy sky"
        ),
        response_format="url",
    )

    print("\n=== xAI Parameter Notes ===")
    print("xAI/Grok supports very few parameters compared to other providers:")
    print("- prompt: The text prompt (required)")
    print("- n: Number of images to generate (optional)")
    print("- response_format: 'url' or 'b64_json' (optional)")
    print("DO NOT include 'size', 'quality', 'style', or other parameters")

    # Close the client when done
    client.close()


if __name__ == "__main__":
    main()
