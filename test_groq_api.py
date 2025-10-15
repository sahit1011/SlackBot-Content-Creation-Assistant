#!/usr/bin/env python3
"""Test script for Groq API connection"""

from groq import Groq
from app.config import Config
import json

def test_groq_api():
    print("Testing Groq API connection...")

    # Check if API key is configured
    api_key = Config.GROQ_API_KEY
    if not api_key or api_key == 'your_groq_api_key_here':
        print(" Groq API key not configured. Please set GROQ_API_KEY in your .env file.")
        return

    print(f" API key configured: {api_key[:8]}...")

    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        print(" Groq client initialized successfully")

        # Test with a simple query
        print("\nTesting simple query...")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello! Can you tell me what 2+2 equals?"
                }
            ],
            model="llama3-8b-8192",  # This model was decommissioned, let's try a current one
            temperature=0.1,
            max_tokens=100
        )

        result = response.choices[0].message.content
        print(f" Response received: {result}")

    except Exception as e:
        print(f" Error with llama3-8b-8192: {str(e)}")

        # Try with a different model
        try:
            print("\nTrying with a different model...")
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello! Can you tell me what 2+2 equals?"
                    }
                ],
                model="mixtral-8x7b-32768",  # Try a different model
                temperature=0.1,
                max_tokens=100
            )

            result = response.choices[0].message.content
            print(f" Response with mixtral-8x7b-32768: {result}")

        except Exception as e2:
            print(f" Error with mixtral-8x7b-32768: {str(e2)}")

            # Try with current Groq models
            current_models = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama-3.1-405b-instruct",
                "gemma-7b-it",
                "gemma2-9b-it"
            ]

            for model in current_models:
                try:
                    print(f"\nTrying with {model}...")
                    response = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant."
                            },
                            {
                                "role": "user",
                                "content": "Hello! Can you tell me what 2+2 equals?"
                            }
                        ],
                        model=model,
                        temperature=0.1,
                        max_tokens=100
                    )

                    result = response.choices[0].message.content
                    print(f" Response with {model}: {result}")
                    break  # Success, stop trying other models

                except Exception as e_model:
                    print(f" Error with {model}: {str(e_model)}")

            print("\n Available Groq models: https://console.groq.com/docs/models")
            print(" Update your GROQ_API_KEY in .env if needed")

if __name__ == "__main__":
    test_groq_api()