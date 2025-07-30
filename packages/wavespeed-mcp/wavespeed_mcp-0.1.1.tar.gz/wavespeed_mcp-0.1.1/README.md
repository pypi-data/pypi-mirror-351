# WavespeedMCP

WavespeedMCP is a Model Control Protocol (MCP) server implementation for WaveSpeed AI services. It provides a standardized interface for accessing WaveSpeed's image and video generation capabilities through the MCP protocol.

## Features

- **Image Generation**: Create high-quality images from text prompts or modify existing images
- **Video Generation**: Transform static images into dynamic videos with customizable parameters
- **Modular Architecture**: Clean, maintainable code structure with clear separation of concerns
- **Robust Error Handling**: Comprehensive exception handling and logging
- **Flexible Configuration**: Support for environment variables and configuration files

## Installation

### Prerequisites

- Python 3.8+
- WaveSpeed API key (obtain from [WaveSpeed AI](https://wavespeed.ai))

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/wavespeed-mcp.git
   cd wavespeed-mcp
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Create a `.env` file with your API credentials (see `.env.example` for reference):
   ```
   WAVESPEED_API_KEY=your_api_key_here
   WAVESPEED_API_HOST=https://api.wavespeed.ai
   ```

## Usage

### Running the Server

Start the WavespeedMCP server:

```bash
python -m wavespeed_mcp --api-key your_api_key_here
```

Or, if installed via pip:

```bash
wavespeed-mcp --api-key your_api_key_here
```

### Client Application

Use the included client application to interact with the server:

```bash
python -m wavespeed_mcp.client_app --tool generate_image --params '{"prompt": "A beautiful sunset over mountains"}'
```

Or, if installed via pip:

```bash
wavespeed-mcp-client --tool generate_image --params '{"prompt": "A beautiful sunset over mountains"}'
```

### API Reference

#### Image Generation

Generate images from text descriptions or modify existing images:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

async def generate_image():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "wavespeed_mcp", "--api-key", "your_api_key_here"]
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            
            params = {
                "prompt": "A beautiful mountain landscape",
                "size": "1024*1024",
                "num_images": 1
            }
            
            result = await client.call_tool("generate_image", params)
            
            # Process result
            for item in result:
                if item.type == "image":
                    print(f"Generated image URL: {item.url}")
```

#### Video Generation

Generate videos from static images:

```python
async def generate_video():
    # ... setup client as above ...
    
    params = {
        "image_url": "https://example.com/image.jpg",
        "prompt": "A scenic landscape with gentle movement",
        "duration": 5
    }
    
    result = await client.call_tool("generate_video", params)
    
    # Process result
    for item in result:
        if item.type == "text":
            print(item.text)  # Contains URL to generated video
```

## Configuration

WavespeedMCP can be configured through:

1. Environment variables (see `.env.example`)
2. Command-line arguments
3. Configuration file (see `wavespeed_mcp_config_demo.json`)

## Architecture

WavespeedMCP follows a clean, modular architecture:

- `server.py`: Core MCP server implementation with tool definitions
- `client.py`: API client for communicating with WaveSpeed services
- `utils.py`: Helper functions for file handling and other utilities
- `exceptions.py`: Custom exception classes for error handling
- `const.py`: Constants and default values

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.