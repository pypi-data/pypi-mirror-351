"""
Midjourney integration for PBT.
Handles image generation for prompt visualization and visual content creation.
"""

import asyncio
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import aiohttp
import aiofiles
import time

from ..base import BaseIntegration


class MidjourneyIntegration(BaseIntegration):
    """Midjourney integration for image generation in prompt workflows."""
    
    def __init__(self, api_key: Optional[str] = None, server_id: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.server_id = server_id
        self.base_url = "https://discord.com/api/v10"
        self.bot_token = None
        
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Midjourney integration."""
        try:
            self.api_key = config.get("api_key") or config.get("discord_token")
            self.server_id = config.get("server_id")
            self.bot_token = config.get("bot_token")
            
            if not self.api_key:
                raise ValueError("Discord token is required for Midjourney")
            
            # Test connection
            return await self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to configure Midjourney: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test Midjourney/Discord API connection."""
        try:
            headers = {
                "Authorization": f"Bot {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/@me",
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Midjourney connection test failed: {e}")
            return False
    
    async def generate_image(self, prompt: str, style: str = "default",
                           aspect_ratio: str = "1:1", quality: str = "standard") -> Dict[str, Any]:
        """Generate image using Midjourney."""
        try:
            # Construct Midjourney prompt with parameters
            mj_prompt = self._build_midjourney_prompt(prompt, style, aspect_ratio, quality)
            
            # Send command to Midjourney bot
            result = await self._send_midjourney_command(f"/imagine {mj_prompt}")
            
            return {
                "job_id": result.get("job_id"),
                "prompt": prompt,
                "midjourney_prompt": mj_prompt,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "quality": quality,
                "status": "generating",
                "estimated_completion": time.time() + 60  # Rough estimate
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
    
    async def generate_prompt_visualization(self, prompt_content: str,
                                          visualization_type: str = "concept") -> Dict[str, Any]:
        """Generate visual representation of prompt concepts."""
        try:
            # Create visualization prompt based on type
            viz_prompt = self._create_visualization_prompt(prompt_content, visualization_type)
            
            # Generate image with appropriate style
            style = self._get_style_for_visualization(visualization_type)
            
            result = await self.generate_image(
                prompt=viz_prompt,
                style=style,
                aspect_ratio="16:9",
                quality="high"
            )
            
            return {
                "original_prompt": prompt_content,
                "visualization_type": visualization_type,
                "visualization_prompt": viz_prompt,
                "image_result": result
            }
            
        except Exception as e:
            self.logger.error(f"Prompt visualization failed: {e}")
            raise
    
    async def create_prompt_thumbnails(self, prompt_file: Path, 
                                     thumbnail_styles: List[str]) -> Dict[str, Any]:
        """Create thumbnail images for prompt files."""
        try:
            # Read prompt content
            async with aiofiles.open(prompt_file, "r") as f:
                prompt_content = await f.read()
            
            thumbnails = []
            
            for style in thumbnail_styles:
                thumb_prompt = f"""
                Create a thumbnail image representing: {prompt_content[:200]}...
                
                Style: {style}
                Layout: Clean, professional, readable
                Elements: Icon, text preview, visual hierarchy
                Purpose: File thumbnail for prompt library
                """
                
                result = await self.generate_image(
                    prompt=thumb_prompt,
                    style=style,
                    aspect_ratio="4:3",
                    quality="standard"
                )
                
                thumbnails.append({
                    "style": style,
                    "result": result
                })
            
            return {
                "prompt_file": str(prompt_file),
                "thumbnails": thumbnails
            }
            
        except Exception as e:
            self.logger.error(f"Thumbnail creation failed: {e}")
            raise
    
    async def generate_workflow_diagram(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate workflow diagram images."""
        try:
            # Create diagram prompt
            steps_description = "\n".join([
                f"{i+1}. {step['name']}: {step.get('description', '')}"
                for i, step in enumerate(workflow_steps)
            ])
            
            diagram_prompt = f"""
            Create a professional workflow diagram showing these steps:
            
            {steps_description}
            
            Style: Clean, modern, business diagram
            Elements: Boxes, arrows, clear labels, logical flow
            Layout: Left-to-right or top-to-bottom flow
            Colors: Professional color scheme
            """
            
            result = await self.generate_image(
                prompt=diagram_prompt,
                style="diagram",
                aspect_ratio="16:9",
                quality="high"
            )
            
            return {
                "workflow_steps": workflow_steps,
                "diagram_result": result
            }
            
        except Exception as e:
            self.logger.error(f"Workflow diagram generation failed: {e}")
            raise
    
    async def create_style_variations(self, base_prompt: str, 
                                    styles: List[str]) -> Dict[str, Any]:
        """Create style variations of the same prompt."""
        try:
            variations = []
            
            for style in styles:
                result = await self.generate_image(
                    prompt=base_prompt,
                    style=style,
                    aspect_ratio="1:1",
                    quality="standard"
                )
                
                variations.append({
                    "style": style,
                    "result": result
                })
            
            return {
                "base_prompt": base_prompt,
                "variations": variations,
                "total_variations": len(variations)
            }
            
        except Exception as e:
            self.logger.error(f"Style variation generation failed: {e}")
            raise
    
    async def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of image generation."""
        try:
            # Check Discord messages for completion
            # This is a simplified implementation
            headers = {
                "Authorization": f"Bot {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Get recent messages from the channel
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/channels/{self.server_id}/messages",
                    headers=headers,
                    params={"limit": 50}
                ) as response:
                    if response.status == 200:
                        messages = await response.json()
                        
                        # Look for completed generation
                        for message in messages:
                            if job_id in message.get("content", ""):
                                return {
                                    "job_id": job_id,
                                    "status": "completed",
                                    "message": message,
                                    "attachments": message.get("attachments", [])
                                }
                        
                        return {
                            "job_id": job_id,
                            "status": "generating",
                            "progress": "unknown"
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to get status: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to get generation status: {e}")
            raise
    
    async def download_image(self, job_id: str, output_path: Union[str, Path]) -> List[Path]:
        """Download generated images."""
        try:
            # Get generation status to find attachments
            status = await self.get_generation_status(job_id)
            
            if status["status"] != "completed":
                raise Exception(f"Generation not ready. Status: {status['status']}")
            
            attachments = status.get("attachments", [])
            if not attachments:
                raise Exception("No images found in completed generation")
            
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            for i, attachment in enumerate(attachments):
                if attachment.get("content_type", "").startswith("image/"):
                    image_url = attachment["url"]
                    filename = attachment.get("filename", f"image_{i}.png")
                    file_path = output_path / filename
                    
                    # Download the image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                async with aiofiles.open(file_path, "wb") as f:
                                    async for chunk in response.content.iter_chunked(8192):
                                        await f.write(chunk)
                                
                                downloaded_files.append(file_path)
                                self.logger.info(f"Downloaded image: {file_path}")
            
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"Image download failed: {e}")
            raise
    
    def _build_midjourney_prompt(self, prompt: str, style: str, 
                               aspect_ratio: str, quality: str) -> str:
        """Build Midjourney-formatted prompt with parameters."""
        try:
            mj_prompt = prompt
            
            # Add style parameters
            if style != "default":
                style_map = {
                    "photorealistic": "--style raw --v 6",
                    "artistic": "--style expressive --v 6",
                    "anime": "--niji 6",
                    "diagram": "--style raw --v 6",
                    "minimalist": "--style raw --v 6",
                    "professional": "--style raw --v 6"
                }
                mj_prompt += f" {style_map.get(style, '--v 6')}"
            
            # Add aspect ratio
            if aspect_ratio != "1:1":
                mj_prompt += f" --ar {aspect_ratio}"
            
            # Add quality
            if quality == "high":
                mj_prompt += " --q 2"
            
            return mj_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to build Midjourney prompt: {e}")
            return prompt
    
    def _create_visualization_prompt(self, prompt_content: str, 
                                   visualization_type: str) -> str:
        """Create visualization prompt based on content and type."""
        try:
            if visualization_type == "concept":
                return f"""
                Abstract conceptual representation of: {prompt_content[:300]}
                
                Style: Modern, clean, conceptual art
                Elements: Symbolic, metaphorical, flowing
                Colors: Professional, harmonious palette
                Avoid: Literal text, specific people, busy details
                """
            
            elif visualization_type == "workflow":
                return f"""
                Professional workflow diagram representing: {prompt_content[:300]}
                
                Style: Clean business diagram, infographic style
                Elements: Boxes, arrows, clear flow, minimal text
                Layout: Logical progression, easy to follow
                Colors: Professional blue/gray scheme
                """
            
            elif visualization_type == "icon":
                return f"""
                Simple icon representing the concept: {prompt_content[:200]}
                
                Style: Modern, minimalist icon design
                Elements: Simple shapes, clear symbolism
                Colors: Single or dual color scheme
                Format: Clean, scalable, professional
                """
            
            else:
                return f"""
                Visual representation of: {prompt_content[:300]}
                
                Style: Professional, clean, informative
                Balance: Abstract and recognizable elements
                Purpose: Illustrative, engaging, clear
                """
                
        except Exception as e:
            self.logger.error(f"Visualization prompt creation failed: {e}")
            return prompt_content[:300]
    
    def _get_style_for_visualization(self, visualization_type: str) -> str:
        """Get appropriate style for visualization type."""
        style_map = {
            "concept": "artistic",
            "workflow": "diagram", 
            "icon": "minimalist",
            "thumbnail": "professional"
        }
        return style_map.get(visualization_type, "professional")
    
    async def _send_midjourney_command(self, command: str) -> Dict[str, Any]:
        """Send command to Midjourney bot."""
        try:
            # This is a simplified implementation
            # In practice, you'd use Discord's slash command API
            
            headers = {
                "Authorization": f"Bot {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "content": command
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/channels/{self.server_id}/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "job_id": result["id"],
                            "command": command,
                            "timestamp": result["timestamp"]
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Command failed: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to send Midjourney command: {e}")
            raise
    
    async def batch_generate_images(self, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate multiple images in batch."""
        try:
            tasks = []
            
            for prompt_config in prompts:
                task = self.generate_image(
                    prompt=prompt_config["prompt"],
                    style=prompt_config.get("style", "default"),
                    aspect_ratio=prompt_config.get("aspect_ratio", "1:1"),
                    quality=prompt_config.get("quality", "standard")
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "prompt_config": prompts[i],
                        "error": str(result),
                        "success": False
                    })
                else:
                    result["prompt_config"] = prompts[i]
                    result["success"] = True
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch image generation failed: {e}")
            raise