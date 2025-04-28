# Intento Translation MCP Server

This is an MCP server that provides translation capabilities using the Intento API.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Intento API credentials

There are two options:

2.a. Setting Intento API credentials for the MCP server (all your MCP clients will use the same credentials)

To set up Intento API credentials for the MCP server:
   - Create a `.env` file in the project root
   - Add your Intento API key:
   ```
   INTENTO_API_KEY=your_api_key_here
   ```

2.b. Setting Intento API credentials for the specific MCP integration, say, Claude Desktop (different MCP clients may use different credentials)

To set up Intento API credentials for the specific MCP integration:
   - Use the "env" section of your MCP config JSON file to specify the "INTENTO_API_KEY" variable. See the [Claude Desktop Integration](#claude-desktop-integration) part as an example


## Usage

1. Start the server:
```bash
python server.py
```

2. The server provides the following tools and resources:

### translate
Translates text between languages. Accepts both language names and ISO codes.

Parameters:
- `text` (required): The text to translate
- `target_language` (required): Target language (e.g., "Spanish" or "es")
- `source_language` (optional): Source language (defaults to empty string for automatic detection)

Example:
```python
# Translate with automatic language detection
result = await translate("Hello world", target_language="Spanish")

# Translate with specific source language
result = await translate("Hello world", target_language="Spanish", source_language="English")
```

### language-codes (Resource)
Resource URL: `mcp://intento-translate/language-codes`

Provides a mapping of language names to their ISO codes as supported by the Intento API.

This resource allows agents to:
- Discover available languages
- Look up the correct ISO code for a language name
- Ensure compatibility with the Intento API

Example of using the resource:
```python
# Get the language codes resource
language_codes = await get_resource("mcp://intento-translate/language-codes")

# Look up a language code
spanish_code = language_codes["codes"]["spanish"]  # Returns "es"

# Use the code in a translation
result = await translate("Hello world", target_language=spanish_code)
```

## Language Support

The server dynamically fetches language codes from the Intento API and makes them available as a resource. This approach has several advantages:

1. **Dynamic Updates**: Language support is always up-to-date with the Intento API
2. **Agent Autonomy**: Agents can discover and use the correct language codes themselves
3. **Flexibility**: The server can handle both language names and ISO codes

### Automatic Language Detection

When the `source_language` parameter is empty (the default), the server will:
- Omit the source language field in the API request
- Let Intento automatically detect the source language
- Log the request as using "auto-detect" for clarity

If the API request fails, the server falls back to a minimal set of common language codes.

## Error Handling

The server includes comprehensive error handling and logging:
- All operations are logged to `logs/intento-translate.log`
- API errors are caught and returned with descriptive messages
- Invalid language codes are handled gracefully

## Claude Desktop Integration

To use this MCP server with Claude Desktop:

1. Create a `claude-mcp-config.json` file in your Claude Desktop configuration directory:
   - Windows: `%APPDATA%\Claude\claude-mcp-config.json`
   - macOS: `~/Library/Application Support/Claude/claude-mcp-config.json`
   - Linux: `~/.config/Claude/claude-mcp-config.json`

2. Add the following configuration (adjust paths to match your installation):

```json
{
    "mcpServers": {
        "intento-translate": {
            "command": "python",
            "args": ["/path/to/your/mcp-intento-translate/server.py"],
            "cwd": "/path/to/your/mcp-intento-translate",
            "env": {
                "INTENTO_API_KEY": "<YOUR_API_KEY>" 
            }
        }
    }
}
```

The "env" part with "INTENTO_API_KEY" is required only if you want to use specific credentials for the integration and not use MCP server-specific credentials.

3. Restart Claude Desktop to load the new configuration.

The server will now be available to Claude Desktop, providing translation capabilities and language code information through the MCP protocol. 