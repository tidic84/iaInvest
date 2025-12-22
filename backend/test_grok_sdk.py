"""Test script pour comprendre le SDK xAI"""
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

# Charger la clé API
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("XAI_API_KEY")

if not API_KEY or not API_KEY.startswith("xai-"):
    print("❌ XAI_API_KEY non configurée ou invalide")
    exit(1)

print(f"✅ API Key configurée: {API_KEY[:10]}...")

client = Client(api_key=API_KEY)

print("\n=== Test 1: Simple chat sans tools ===")
chat = client.chat.create(
    model="grok-2-1212",
    messages=[user("What is 2+2? Answer in JSON: {\"result\": number}")]
)

print(f"Type de chat: {type(chat)}")
print(f"Attributes: {[attr for attr in dir(chat) if not attr.startswith('_')][:10]}")

if hasattr(chat, 'messages'):
    print(f"\n✅ chat.messages existe, count: {len(chat.messages)}")
    for i, msg in enumerate(chat.messages):
        print(f"  Message {i}: role={getattr(msg, 'role', '?')}, content_type={type(msg.content)}")
        if hasattr(msg, 'content'):
            content_preview = str(msg.content)[:100]
            print(f"    Content: {content_preview}")
else:
    print("\n❌ chat.messages n'existe pas")

print("\n=== Test 2: Chat avec tools (web_search) ===")
try:
    chat2 = client.chat.create(
        model="grok-2-1212",
        messages=[user("What's the weather today in Paris? Answer in JSON")],
        tools=[web_search()]
    )

    print(f"Type de chat2: {type(chat2)}")

    if hasattr(chat2, 'messages'):
        print(f"✅ chat2.messages existe, count: {len(chat2.messages)}")
        for i, msg in enumerate(chat2.messages):
            print(f"  Message {i}: role={getattr(msg, 'role', '?')}")
    else:
        print("❌ chat2.messages n'existe pas")

except Exception as e:
    print(f"❌ Erreur avec tools: {type(e).__name__}: {e}")

print("\n=== Fin des tests ===")
