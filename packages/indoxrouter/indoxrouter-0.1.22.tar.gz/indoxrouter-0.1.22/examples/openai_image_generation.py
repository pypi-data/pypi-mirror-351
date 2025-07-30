"""
Example script demonstrating OpenAI image generation through indoxRouter.

This script shows how to generate images using different OpenAI models:
- DALL-E 2
- DALL-E 3
- GPT-image-1

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
    """Generate an image with the specified model and parameters."""
    print(f"\n=== Generating image with {model} ===")
    print(f"Prompt: {prompt}")

    try:
        response = client.images(prompt=prompt, model=f"openai/{model}", **kwargs)

        # Print the URL of the generated image
        if "data" in response and response["data"] and "url" in response["data"][0]:
            print(f"Image URL: {response['data'][0]['url']}")

            # Check for revised prompt (DALL-E 3 often revises prompts)
            if "revised_prompt" in response["data"][0]:
                print(f"Revised prompt: {response['data'][0]['revised_prompt']}")

        # Print usage/cost information if available
        if "usage" in response and "cost" in response["usage"]:
            print(f"Cost: ${response['usage']['cost']:.4f}")

        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def main():
    """Main function demonstrating OpenAI image generation."""

    # Basic DALL-E 2 example
    dalle2_response = generate_image(
        model="dall-e-2",
        prompt="A beautiful mountain landscape at sunset",
        size="1024x1024",  # Required parameter
        response_format="url",  # Optional parameter
    )

    # DALL-E 3 with quality and style options
    dalle3_response = generate_image(
        model="dall-e-3",
        prompt="A futuristic city with flying cars and tall skyscrapers",
        size="1024x1024",  # Required parameter
        quality="hd",  # Optional parameter ('standard' or 'hd')
        style="vivid",  # Optional parameter ('vivid' or 'natural')
        response_format="url",
    )

    # GPT-image-1 example
    # Note: For GPT-image-1, don't include response_format unless you need it
    gpt_image_response = generate_image(
        model="gpt-image-1",
        prompt="A whimsical fantasy castle with dragons flying around it",
        size="1024x1024",  # Required parameter
        # response_format is omitted as it can cause errors with gpt-image-1
    )

    # Close the client when done
    client.close()


if __name__ == "__main__":
    main()
