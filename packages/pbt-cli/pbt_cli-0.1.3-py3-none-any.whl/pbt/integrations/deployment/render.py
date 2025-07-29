"""Render.com deployment integration"""

import os
import json
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime


class RenderDeployment:
    """Deploy PBT applications to Render.com"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RENDER_API_KEY")
        self.api_base = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_web_service(
        self,
        name: str,
        repo_url: str,
        branch: str = "main",
        build_command: str = "pip install -e .",
        start_command: str = "pbt serve --host 0.0.0.0 --port $PORT",
        env_vars: Optional[Dict[str, str]] = None,
        region: str = "oregon"
    ) -> Dict[str, Any]:
        """Create a new web service on Render"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        service_data = {
            "type": "web_service",
            "name": name,
            "repo": repo_url,
            "branch": branch,
            "buildCommand": build_command,
            "startCommand": start_command,
            "region": region,
            "plan": "starter",
            "envVars": []
        }
        
        # Add environment variables
        if env_vars:
            for key, value in env_vars.items():
                service_data["envVars"].append({
                    "key": key,
                    "value": value
                })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/services",
                    headers=self.headers,
                    json=service_data
                ) as response:
                    if response.status in [200, 201]:
                        service = await response.json()
                        return {
                            "success": True,
                            "service_id": service["id"],
                            "url": f"https://{service['slug']}.onrender.com"
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": error_text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def deploy_static_site(
        self,
        name: str,
        repo_url: str,
        branch: str = "main",
        build_command: str = "pbt docs",
        publish_path: str = "docs",
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Deploy static documentation site"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        site_data = {
            "type": "static_site",
            "name": name,
            "repo": repo_url,
            "branch": branch,
            "buildCommand": build_command,
            "publishPath": publish_path,
            "envVars": []
        }
        
        if env_vars:
            for key, value in env_vars.items():
                site_data["envVars"].append({
                    "key": key,
                    "value": value
                })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/services",
                    headers=self.headers,
                    json=site_data
                ) as response:
                    if response.status in [200, 201]:
                        site = await response.json()
                        return {
                            "success": True,
                            "site_id": site["id"],
                            "url": f"https://{site['slug']}.onrender.com"
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": error_text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def deploy_background_worker(
        self,
        name: str,
        repo_url: str,
        branch: str = "main",
        build_command: str = "pip install -e .",
        start_command: str = "pbt worker",
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Deploy background worker for async tasks"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        worker_data = {
            "type": "background_worker",
            "name": name,
            "repo": repo_url,
            "branch": branch,
            "buildCommand": build_command,
            "startCommand": start_command,
            "plan": "starter",
            "envVars": []
        }
        
        if env_vars:
            for key, value in env_vars.items():
                worker_data["envVars"].append({
                    "key": key,
                    "value": value
                })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/services",
                    headers=self.headers,
                    json=worker_data
                ) as response:
                    if response.status in [200, 201]:
                        worker = await response.json()
                        return {
                            "success": True,
                            "worker_id": worker["id"],
                            "name": worker["name"]
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": error_text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_service_status(self, service_id: str) -> Dict[str, Any]:
        """Get deployment status of a service"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/services/{service_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        service = await response.json()
                        return {
                            "success": True,
                            "status": service.get("suspended", False) and "suspended" or "active",
                            "url": service.get("url", ""),
                            "created_at": service.get("createdAt", ""),
                            "updated_at": service.get("updatedAt", "")
                        }
                    else:
                        return {"success": False, "error": "Service not found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def trigger_deploy(self, service_id: str) -> Dict[str, Any]:
        """Manually trigger a deployment"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/services/{service_id}/deploys",
                    headers=self.headers,
                    json={}
                ) as response:
                    if response.status in [200, 201]:
                        deploy = await response.json()
                        return {
                            "success": True,
                            "deploy_id": deploy["id"],
                            "status": deploy["status"]
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": error_text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def update_env_vars(
        self,
        service_id: str,
        env_vars: Dict[str, str]
    ) -> Dict[str, Any]:
        """Update environment variables for a service"""
        if not self.api_key:
            return {"success": False, "error": "Render API key not configured"}
        
        env_var_list = [
            {"key": key, "value": value}
            for key, value in env_vars.items()
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.api_base}/services/{service_id}/env-vars",
                    headers=self.headers,
                    json=env_var_list
                ) as response:
                    if response.status == 200:
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": error_text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}