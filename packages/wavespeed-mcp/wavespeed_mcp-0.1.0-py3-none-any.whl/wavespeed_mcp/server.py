"""
WaveSpeed MCP Server

This server connects to WaveSpeed AI API endpoints which may involve costs.
Any tool that makes an API call is clearly marked with a cost warning.

Note: Always ensure you have proper API credentials before using these tools.
"""

import os
import requests
import time
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from wavespeed_mcp.utils import (
    build_output_path,
    build_output_file,
    validate_loras,
    get_image_as_base64,
    process_image_input,
)
from wavespeed_mcp.const import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_NUM_INFERENCE_STEPS,
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_NUM_IMAGES,
    DEFAULT_SEED,
    DEFAULT_STRENGTH,
    DEFAULT_IMAGE_LORA,
    ENV_WAVESPEED_API_KEY,
    ENV_WAVESPEED_API_HOST,
    ENV_WAVESPEED_MCP_BASE_PATH,
    ENV_RESOURCE_MODE,
    RESOURCE_MODE_URL,
    RESOURCE_MODE_BASE64,
    API_VERSION,
    API_BASE_PATH,
    API_IMAGE_ENDPOINT,
    API_VIDEO_ENDPOINT,
)
from wavespeed_mcp.exceptions import WavespeedRequestError, WavespeedAuthError, WavespeedTimeoutError
from wavespeed_mcp.client import WavespeedAPIClient

# Load environment variables
load_dotenv()

# Configure logging

logging.basicConfig(
    level="INFO", format="%(asctime)s - wavespeed-mcp - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wavespeed-mcp")

# Get configuration from environment variables
api_key = os.getenv(ENV_WAVESPEED_API_KEY)
api_host = os.getenv(ENV_WAVESPEED_API_HOST, "https://api.wavespeed.ai")
base_path = os.getenv(ENV_WAVESPEED_MCP_BASE_PATH) or str(Path.home() / "Desktop")
resource_mode = os.getenv(ENV_RESOURCE_MODE, RESOURCE_MODE_URL)

# Validate required environment variables
if not api_key:
    raise ValueError(f"{ENV_WAVESPEED_API_KEY} environment variable is required")

# Initialize MCP server and API client
mcp = FastMCP(
    # "WaveSpeed", log_level=os.getenv(ENV_FASTMCP_LOG_LEVEL, DEFAULT_LOG_LEVEL)
    "WaveSpeed",
    log_level="INFO",
)
api_client = WavespeedAPIClient(api_key, f"{api_host}{API_BASE_PATH}/{API_VERSION}")


class FileInfo(BaseModel):
    """Information about a local file."""

    path: str
    index: int


class Base64Info(BaseModel):
    """Information about a base64 encoded resource."""

    data: str
    mime_type: str
    index: int


class WaveSpeedResult(BaseModel):
    """Unified model for WaveSpeed generation results."""

    status: str = "success"
    urls: List[str] = []
    base64: List[Base64Info] = []
    local_files: List[FileInfo] = []
    error: Optional[str] = None
    processing_time: float = 0.0

    def to_json(self) -> str:
        """Convert the result to a JSON string."""
        return json.dumps(self.model_dump(), indent=2)


@mcp.tool(
    description="""Generate an image using WaveSpeed AI.
    COST WARNING: This tool makes an API call to WaveSpeed which may incur costs.
    Only use when explicitly requested by the user.

    Args:
        prompt (str): Text description of the image to generate.
        image (str, optional): URL of an input image for image-to-image generation.
        mask_image (str, optional): URL of a mask image for inpainting.
        loras (list, optional): List of LoRA models to use, each with a path and scale.
        strength (float, optional): Strength of the input image influence (0.0-1.0).
        size (str, optional): Size of the output image in format "width*height".
        num_inference_steps (int, optional): Number of denoising steps.
        guidance_scale (float, optional): Guidance scale for text adherence.
        num_images (int, optional): Number of images to generate.
        seed (int, optional): Random seed (-1 for random).
        enable_safety_checker (bool, optional): Whether to enable safety filtering.
        output_directory (str, optional): Directory to save the generated images.

    Returns:
        WaveSpeedResult object with the result of the image generation.
    """
)
def generate_image(
    prompt: str,
    image: str = "",
    mask_image: str = "",
    loras: Optional[List[Dict[str, Union[str, float]]]] = None,
    strength: float = DEFAULT_STRENGTH,
    size: str = DEFAULT_IMAGE_SIZE,
    num_inference_steps: int = DEFAULT_NUM_INFERENCE_STEPS,
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE,
    num_images: int = DEFAULT_NUM_IMAGES,
    seed: int = DEFAULT_SEED,
    enable_safety_checker: bool = True,
    output_directory: str = None,
):
    """Generate an image using WaveSpeed AI."""
    begin = time.time()

    if not prompt:
        return TextContent(type="text", text="Prompt is required for image generation")

    # Validate and set default loras if not provided
    if not loras:
        loras = [DEFAULT_IMAGE_LORA]
    else:
        loras = validate_loras(loras)

    # Prepare API payload
    payload = {
        "prompt": prompt,
        "image": image,
        "mask_image": mask_image,
        "strength": strength,
        "loras": loras,
        "size": size,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        # "num_images": num_images,
        "seed": seed,
        "enable_base64_output": False,  # 使用URL，后续自己转换为base64
        "enable_safety_checker": enable_safety_checker,
    }

    try:
        # Make API request
        response_data = api_client.post(API_IMAGE_ENDPOINT, json=payload)
        request_id = response_data.get("data", {}).get("id")

        if not request_id:
            return TextContent(type="text", text="Failed to get request ID from response. Please try again.")

        logger.info(f"Image generation request submitted with ID: {request_id}")

        # Poll for results
        result = api_client.poll_result(request_id)
        outputs = result.get("outputs", [])

        if not outputs:
            return TextContent(type="text", text="No image outputs received. Please try again.")

        end = time.time()
        processing_time = end - begin

        logger.info(f"Image generation completed in {processing_time:.2f} seconds")

        # 准备返回结果
        result = WaveSpeedResult(urls=outputs, processing_time=processing_time)

        # 处理不同的资源模式
        if resource_mode == RESOURCE_MODE_URL:
            # 只返回URLs
            pass
        elif resource_mode == RESOURCE_MODE_BASE64:
            # 获取base64编码
            for i, url in enumerate(outputs):
                try:
                    # 获取图像的base64编码和MIME类型
                    base64_data, mime_type = get_image_as_base64(url)
                    result.base64.append(
                        Base64Info(data=base64_data, mime_type=mime_type, index=i)
                    )
                    logger.info(
                        f"Successfully encoded image {i+1}/{len(outputs)} to base64"
                    )
                except Exception as e:
                    logger.error(f"Failed to encode image {i+1}: {str(e)}")
        else:
            # 保存到本地文件
            output_path = build_output_path(output_directory, base_path)

            for i, image_url in enumerate(outputs):
                try:
                    output_file_name = build_output_file(
                        "image", f"{i}_{prompt}", output_path, "jpeg"
                    )
                    output_path.mkdir(parents=True, exist_ok=True)

                    image_response = requests.get(image_url)
                    image_response.raise_for_status()

                    with open(output_file_name, "wb") as f:
                        f.write(image_response.content)

                    result.local_files.append(
                        FileInfo(path=str(output_file_name), index=i)
                    )
                    logger.info(
                        f"Successfully saved image {i+1}/{len(outputs)} to {output_file_name}"
                    )
                except Exception as e:
                    logger.error(f"Failed to save image {i+1}: {str(e)}")

        # 返回统一的JSON结构
        return TextContent(type="text", text=result.to_json())

    except (WavespeedAuthError, WavespeedRequestError, WavespeedTimeoutError) as e:
        logger.error(f"Image generation failed: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"Failed to generate image: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())
    except Exception as e:
        logger.exception(f"Unexpected error during image generation: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"An unexpected error occurred: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())


@mcp.tool(
    description="""Generate a video using WaveSpeed AI.
    
    COST WARNING: This tool makes an API call to WaveSpeed which may incur costs. 
    Only use when explicitly requested by the user.

    Args:
        image (str): URL, base64 string, or local file path of the input image to animate.
        prompt (str): Text description of the video to generate.
        negative_prompt (str, optional): Text description of what to avoid in the video.
        loras (list, optional): List of LoRA models to use, each with a path and scale.
        size (str, optional): Size of the output video in format "width*height".
        num_inference_steps (int, optional): Number of denoising steps.
        duration (int, optional): Duration of the video in seconds. enum: [5, 10]
        guidance_scale (float, optional): Guidance scale for text adherence.
        flow_shift (int, optional): Shift of the flow in the video.
        seed (int, optional): Random seed (-1 for random).
        enable_safety_checker (bool, optional): Whether to enable safety filtering.
        output_directory (str, optional): Directory to save the generated video.

    Returns:
        WaveSpeedResult object with the result of the video generation.
    """
)
def generate_video(
    image: str,
    prompt: str,
    negative_prompt: str = "",
    loras: Optional[List[Dict[str, Union[str, float]]]] = None,
    size: str = "832*480",
    num_inference_steps: int = 30,
    duration: int = 5,
    guidance_scale: float = 5,
    flow_shift: int = 3,
    seed: int = -1,
    enable_safety_checker: bool = True,
    output_directory: str = None,
):
    """Generate a video using WaveSpeed AI."""
    begin = time.time()

    if not image:
        # raise WavespeedRequestError("Input image is required for video generation")
        return TextContent(type="text", text="Input image is required for video generation. Can use generate_image tool to generate an image first.")

    if not prompt:
        # raise WavespeedRequestError("Prompt is required for video generation")
        return TextContent(type="text", text="Prompt is required for video generation. Please use en-US as the language.")

    # Validate and set default loras if not provided
    if not loras:
        loras = []
    else:
        loras = validate_loras(loras)

    if duration not in [5, 10]:
        return TextContent(type="text", text="Duration must be 5 or 10 seconds. Please set it to 5 or 10.")

    # handle image input
    try:
        processed_image = process_image_input(image)
        logger.info("Successfully processed input image")
    except Exception as e:
        logger.error(f"Failed to process input image: {str(e)}")
        return TextContent(type="text", text=f"Failed to process input image: {str(e)}")

    # Prepare API payload
    payload = {
        "image": processed_image,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "loras": loras,
        "size": size,
        "num_inference_steps": num_inference_steps,
        "duration": duration,
        "guidance_scale": guidance_scale,
        "flow_shift": flow_shift,
        "seed": seed,
        "enable_safety_checker": enable_safety_checker,
    }

    try:
        # Make API request
        response_data = api_client.post(API_VIDEO_ENDPOINT, json=payload)
        request_id = response_data.get("data", {}).get("id")

        if not request_id:
            return TextContent(type="text", text="Failed to get request ID from response. Please try again.")

        logger.info(f"Video generation request submitted with ID: {request_id}")

        # Poll for results
        result = api_client.poll_result(request_id)
        outputs = result.get("outputs", [])

        if not outputs:
            return TextContent(type="text", text="No video outputs received. Please try again.")

        video_url = outputs[0]  # Usually just one video is returned

        end = time.time()
        processing_time = end - begin

        logger.info(f"Video generation completed in {processing_time:.2f} seconds")

        # prepare result
        result = WaveSpeedResult(urls=outputs, processing_time=processing_time)

        # handle different resource mode
        if resource_mode == RESOURCE_MODE_URL:
            # only return URLs
            pass
        elif resource_mode == RESOURCE_MODE_BASE64:
            # get base64 encoding
            try:
                response = requests.get(video_url)
                response.raise_for_status()

                # convert to base64
                import base64

                base64_data = base64.b64encode(response.content).decode("utf-8")

                result.base64.append(
                    Base64Info(data=base64_data, mime_type="video/mp4", index=0)
                )

                logger.info("Successfully encoded video to base64")
            except Exception as e:
                logger.error(f"Failed to encode video: {str(e)}")
        else:
            # save to local file
            output_path = build_output_path(output_directory, base_path)

            try:
                filename = build_output_file("video", prompt, output_path, "mp4")
                output_path.mkdir(parents=True, exist_ok=True)

                response = requests.get(video_url, stream=True)
                response.raise_for_status()

                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                result.local_files.append(FileInfo(path=str(filename), index=0))

                logger.info(f"Successfully saved video to {filename}")
            except Exception as e:
                logger.error(f"Failed to save video: {str(e)}")

        # return result
        return TextContent(type="text", text=result.to_json())

    except (WavespeedAuthError, WavespeedRequestError, WavespeedTimeoutError) as e:
        logger.error(f"Video generation failed: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"Failed to generate video: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())
    except Exception as e:
        logger.exception(f"Unexpected error during video generation: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"An unexpected error occurred: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())


def main():
    print("Starting WaveSpeed MCP server")
    """Run the WaveSpeed MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
