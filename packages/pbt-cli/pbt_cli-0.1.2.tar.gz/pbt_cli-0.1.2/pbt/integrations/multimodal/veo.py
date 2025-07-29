"""
Veo integration for PBT.
Handles video generation and processing for prompt visualization and video content creation.
"""

import asyncio
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import aiohttp
import aiofiles
import json
import time

from ..base import BaseIntegration


class VeoIntegration(BaseIntegration):
    """Veo integration for video generation in prompt workflows."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = "https://aiplatform.googleapis.com/v1"
        self.model_name = "veo-v1"
        
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Veo integration."""
        try:
            self.api_key = config.get("api_key") or config.get("google_api_key")
            self.project_id = config.get("project_id")
            self.model_name = config.get("model", "veo-v1")
            
            if not self.api_key or not self.project_id:
                raise ValueError("Google API key and project ID are required for Veo")
            
            # Test connection
            return await self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to configure Veo: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test Veo API connection."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{self.project_id}/locations",
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Veo connection test failed: {e}")
            return False
    
    async def generate_video(self, prompt: str, duration: int = 5,
                           resolution: str = "720p", style: str = "realistic") -> Dict[str, Any]:
        """Generate video from text prompt."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare video generation request
            request_data = {
                "instances": [{
                    "prompt": prompt,
                    "duration_seconds": duration,
                    "resolution": resolution,
                    "style": style,
                    "aspect_ratio": "16:9",
                    "frame_rate": 24
                }],
                "parameters": {
                    "model": self.model_name,
                    "quality": "high",
                    "safety_filter": True
                }
            }
            
            endpoint = f"{self.base_url}/projects/{self.project_id}/locations/us-central1/publishers/google/models/{self.model_name}:predict"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=request_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Process the response
                        video_data = result.get("predictions", [{}])[0]
                        
                        return {
                            "video_id": video_data.get("video_id"),
                            "status": "generating",
                            "prompt": prompt,
                            "duration": duration,
                            "resolution": resolution,
                            "style": style,
                            "estimated_completion": time.time() + (duration * 10)  # Rough estimate
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Video generation failed: {error}")
                        
        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            raise
    
    async def generate_video_from_image(self, image_path: Union[str, Path], prompt: str,
                                      duration: int = 5, motion_intensity: str = "medium") -> Dict[str, Any]:
        """Generate video from image and text prompt."""
        try:
            image_path = Path(image_path)
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read and encode image
            async with aiofiles.open(image_path, "rb") as image_file:
                image_data = await image_file.read()
                image_base64 = base64.b64encode(image_data).decode()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            request_data = {
                "instances": [{
                    "prompt": prompt,
                    "image": {
                        "bytes_base64_encoded": image_base64
                    },
                    "duration_seconds": duration,
                    "motion_intensity": motion_intensity,
                    "aspect_ratio": "16:9"
                }],
                "parameters": {
                    "model": self.model_name,
                    "quality": "high"
                }
            }
            
            endpoint = f"{self.base_url}/projects/{self.project_id}/locations/us-central1/publishers/google/models/{self.model_name}:predict"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=request_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        video_data = result.get("predictions", [{}])[0]
                        
                        return {
                            "video_id": video_data.get("video_id"),
                            "status": "generating",
                            "prompt": prompt,
                            "source_image": str(image_path),
                            "duration": duration,
                            "motion_intensity": motion_intensity
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Image-to-video generation failed: {error}")
                        
        except Exception as e:
            self.logger.error(f"Image-to-video generation failed: {e}")
            raise
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get status of video generation."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            endpoint = f"{self.base_url}/projects/{self.project_id}/operations/{video_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "video_id": video_id,
                            "status": result.get("done", False) and "completed" or "generating",
                            "progress": result.get("metadata", {}).get("progress", 0),
                            "result": result.get("response") if result.get("done") else None,
                            "error": result.get("error")
                        }
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to get video status: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to get video status: {e}")
            raise
    
    async def download_video(self, video_id: str, output_path: Union[str, Path]) -> Path:
        """Download generated video."""
        try:
            # First get the video status to get download URL
            status = await self.get_video_status(video_id)
            
            if status["status"] != "completed":
                raise Exception(f"Video not ready. Status: {status['status']}")
            
            video_url = status["result"].get("video_url")
            if not video_url:
                raise Exception("No video URL in result")
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the video
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(output_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        self.logger.info(f"Downloaded video: {output_path}")
                        return output_path
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to download video: {error}")
                        
        except Exception as e:
            self.logger.error(f"Video download failed: {e}")
            raise
    
    async def create_prompt_visualization(self, prompt_content: str, 
                                        visualization_type: str = "concept") -> Dict[str, Any]:
        """Create video visualization of prompt concepts."""
        try:
            # Generate visualization prompt based on the original prompt
            viz_prompt = await self._generate_visualization_prompt(prompt_content, visualization_type)
            
            # Create the video
            video_result = await self.generate_video(
                prompt=viz_prompt,
                duration=8,
                resolution="1080p",
                style="cinematic"
            )
            
            return {
                "original_prompt": prompt_content,
                "visualization_prompt": viz_prompt,
                "video_result": video_result,
                "type": visualization_type
            }
            
        except Exception as e:
            self.logger.error(f"Prompt visualization failed: {e}")
            raise
    
    async def create_prompt_demo(self, prompt_file: Path, demo_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create demonstration videos showing prompt usage."""
        try:
            demo_videos = []
            
            for scenario in demo_scenarios:
                scenario_prompt = f"""
                Create a demonstration video showing: {scenario['description']}
                
                Context: This is demonstrating the prompt: {prompt_file.name}
                Scenario: {scenario.get('scenario', 'General usage')}
                Expected outcome: {scenario.get('expected_outcome', 'Successful execution')}
                
                Style: Professional, educational, clear visual storytelling
                """
                
                video_result = await self.generate_video(
                    prompt=scenario_prompt,
                    duration=scenario.get('duration', 10),
                    resolution="1080p",
                    style="educational"
                )
                
                demo_videos.append({
                    "scenario": scenario,
                    "video_result": video_result
                })
            
            return {
                "prompt_file": str(prompt_file),
                "demo_videos": demo_videos,
                "total_scenarios": len(demo_scenarios)
            }
            
        except Exception as e:
            self.logger.error(f"Prompt demo creation failed: {e}")
            raise
    
    async def generate_explainer_video(self, topic: str, key_points: List[str],
                                     duration: int = 30) -> Dict[str, Any]:
        """Generate explainer video for prompt engineering concepts."""
        try:
            explainer_prompt = f"""
            Create an educational explainer video about: {topic}
            
            Key points to cover:
            {chr(10).join(f"- {point}" for point in key_points)}
            
            Style: Clean, modern, educational animation
            Tone: Professional but accessible
            Visual elements: Diagrams, text overlays, smooth transitions
            Pacing: Clear and easy to follow
            """
            
            video_result = await self.generate_video(
                prompt=explainer_prompt,
                duration=duration,
                resolution="1080p",
                style="animated"
            )
            
            return {
                "topic": topic,
                "key_points": key_points,
                "video_result": video_result,
                "duration": duration
            }
            
        except Exception as e:
            self.logger.error(f"Explainer video generation failed: {e}")
            raise
    
    async def _generate_visualization_prompt(self, prompt_content: str, 
                                           visualization_type: str) -> str:
        """Generate visualization prompt based on content and type."""
        try:
            if visualization_type == "concept":
                return f"""
                Create a conceptual visualization representing the ideas in this prompt:
                
                "{prompt_content}"
                
                Visual style: Abstract, conceptual, flowing animations
                Focus on: Key themes, emotions, and concepts
                Avoid: Literal interpretations, text, specific people
                """
            
            elif visualization_type == "workflow":
                return f"""
                Create a workflow visualization showing the process described in:
                
                "{prompt_content}"
                
                Visual style: Clean diagrams, process flows, step-by-step animation
                Focus on: Logical flow, connections, progression
                Include: Arrows, stages, clear visual hierarchy
                """
            
            elif visualization_type == "outcome":
                return f"""
                Create a video showing the potential outcomes and results of:
                
                "{prompt_content}"
                
                Visual style: Realistic, professional, showcase-style
                Focus on: End results, benefits, successful implementation
                Show: Before/after, transformations, achievements
                """
            
            else:
                return f"""
                Create a general visualization for the prompt concept:
                
                "{prompt_content}"
                
                Visual style: Professional, engaging, informative
                Balance: Abstract and concrete elements
                """
                
        except Exception as e:
            self.logger.error(f"Visualization prompt generation failed: {e}")
            return prompt_content
    
    async def batch_generate_videos(self, prompts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate multiple videos in batch."""
        try:
            tasks = []
            
            for prompt_config in prompts:
                task = self.generate_video(
                    prompt=prompt_config["prompt"],
                    duration=prompt_config.get("duration", 5),
                    resolution=prompt_config.get("resolution", "720p"),
                    style=prompt_config.get("style", "realistic")
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
            self.logger.error(f"Batch video generation failed: {e}")
            raise