import os
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
API_KEY = os.getenv("API_KEY")
CACHE_TTL = 300

AVAILABLE_MODELS = {
    "llama-3.1-8b": "@cf/meta/llama-3.1-8b-instruct-fast",
    "llama-3.1-70b": "@cf/meta/llama-3.1-70b-instruct",
    "mistral-7b": "@cf/mistral/mistral-7b-instruct-v0.1",
}