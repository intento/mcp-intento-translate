import json
import logging
import os
import requests
from mcp.server.fastmcp import FastMCP
from config import INTENTO_API_KEY, INTENTO_API_URL

# Constants
USER_AGENT = "Intento MCP Server/Python 1.0.0"

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/intento-translate.log'),
        logging.StreamHandler()  # Keep console output for debugging
    ]
)
logger = logging.getLogger("intento-translate")

# Create MCP server
mcp = FastMCP("intento-translate")

# Cache for language codes
language_codes_cache = {}

async def fetch_language_codes():
    """Fetch language codes from Intento API and cache them"""
    if language_codes_cache:
        return language_codes_cache
    
    headers = {
        "Content-Type": "application/json",
        "apikey": INTENTO_API_KEY,
        "User-Agent": USER_AGENT
    }
    
    try:
        # Fetch supported languages from Intento API
        response = requests.get(f"{INTENTO_API_URL}/languages", headers=headers)
        response.raise_for_status()
        languages = response.json()
        
        # Process and cache the language data
        for lang in languages:
            if 'code' in lang and 'name' in lang:
                language_codes_cache[lang['name'].lower()] = lang['code']
                # Also add common variations
                if 'aliases' in lang:
                    for alias in lang['aliases']:
                        language_codes_cache[alias.lower()] = lang['code']
        
        logger.info(f"Cached {len(language_codes_cache)} language codes")
        return language_codes_cache
    except Exception as e:
        logger.error(f"Failed to fetch language codes: {str(e)}")
        # Return a minimal set of common languages as fallback
        return {
            "english": "en",
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "russian": "ru",
            "japanese": "ja",
            "chinese": "zh",
            "auto": "auto"
        }

@mcp.resource("mcp://intento-translate/language-codes")
async def get_language_codes():
    """Resource that provides language codes (ISO codes) from Intento API"""
    codes = await fetch_language_codes()
    return {
        "description": "Language codes supported by Intento Translation API",
        "codes": codes
    }

def get_language_code(language: str) -> str:
    """Convert language name to ISO code using the cached codes"""
    language = language.lower().strip()
    return language_codes_cache.get(language, language)

@mcp.tool()
async def translate(text: str, target_language: str, source_language: str = "") -> str:
    """Translate text between different languages. Use ISO codes for the languages. For autodetect, use empty 'from' language."""
    # Ensure language codes are loaded
    if not language_codes_cache:
        await fetch_language_codes()
    
    # Convert language names to ISO codes
    to_code = get_language_code(target_language)
    
    # Handle autodetect case - use empty string instead of "auto"
    from_code = "" if source_language.lower() == "auto" else get_language_code(source_language)
    
    logger.info(f"Translation request: from={from_code or 'auto-detect'}, to={to_code}, text length={len(text)}")
    
    # Prepare the request to Intento API
    headers = {
        "Content-Type": "application/json",
        "apikey": INTENTO_API_KEY,
        "User-Agent": USER_AGENT
    }
    
    data = {
        "context": {
            "text": [text],
            "to": to_code
        },
        "service": {
            "routing": "best"
        }
    }
    
    # Only add "from" field if it's not empty (not autodetect)
    if from_code:
        data["context"]["from"] = from_code
    
    try:
        logger.debug(f"Sending request to Intento API: {json.dumps(data, ensure_ascii=False)}")
        # Make the API request
        response = requests.post(INTENTO_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        translated_text = result.get("results", [""])[0]
        
        logger.info(f"Translation successful: {translated_text[:50]}...")
        return translated_text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return f"Error during translation: {str(e)}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        return f"Error parsing API response: {str(e)}"

if __name__ == "__main__":
    import asyncio
    
    logger.info("Starting Intento Translation MCP Server...")
    logger.info(f"API URL: {INTENTO_API_URL}")
    logger.info("Server is ready to accept translation requests")
    
    try:
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        logger.info("Server shutdown complete") 