"""Test script pour comprendre chat.sample()"""
import os
from xai_sdk import Client
from xai_sdk.chat import user

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("XAI_API_KEY")
client = Client(api_key=API_KEY)

print("=== Test chat.sample() ===")
chat = client.chat.create(
    model="grok-2-1212",
    messages=[user("What is 2+2? Answer ONLY in JSON format: {\"result\": number, \"explanation\": \"text\"}")]
)

print("Calling chat.sample()...")
response = chat.sample()

print(f"\nType of response: {type(response)}")
print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')][:15]}")

if hasattr(response, 'content'):
    print(f"\n✅ response.content exists")
    print(f"Content type: {type(response.content)}")
    print(f"Content: {response.content}")

if hasattr(response, 'message'):
    print(f"\n✅ response.message exists")
    print(f"Message type: {type(response.message)}")

# Essayer d'extraire le texte
if hasattr(response, 'content'):
    content = response.content
    if isinstance(content, str):
        print(f"\n📝 Response text (string): {content}")
    elif isinstance(content, list):
        print(f"\n📝 Response content (list) length: {len(content)}")
        for i, item in enumerate(content):
            print(f"  Item {i}: {type(item)}")
            if hasattr(item, 'text'):
                print(f"    text: {item.text}")

print("\n=== End ===")
