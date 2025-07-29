"""
Fly.io deployment integration for PBT.
Handles backend deployment and playground UI hosting.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
import aiohttp
import toml

from ..base import BaseIntegration


class FlyioIntegration(BaseIntegration):
    """Fly.io deployment integration for PBT backend and UI."""
    
    def __init__(self, api_token: Optional[str] = None, org_slug: Optional[str] = None):
        super().__init__()
        self.api_token = api_token
        self.org_slug = org_slug
        self.base_url = "https://api.machines.dev/v1"
        
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Fly.io integration."""
        try:
            self.api_token = config.get("api_token")
            self.org_slug = config.get("org_slug")
            
            if not self.api_token:
                raise ValueError("Fly.io API token is required")
                
            # Verify authentication
            return await self._verify_auth()
            
        except Exception as e:
            self.logger.error(f"Failed to configure Fly.io: {e}")
            return False
    
    async def _verify_auth(self) -> bool:
        """Verify Fly.io authentication."""
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/apps",
                    headers=headers
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.error(f"Auth verification failed: {e}")
            return False
    
    async def create_app(self, app_name: str, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Fly.io app."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "app_name": app_name,
                "org_slug": self.org_slug,
                **app_config
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/apps",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        self.logger.info(f"Created Fly.io app: {app_name}")
                        return result
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to create app: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to create Fly.io app: {e}")
            raise
    
    async def deploy_backend(self, project_path: Path, app_name: str, 
                           environment: str = "production") -> Dict[str, Any]:
        """Deploy PBT backend to Fly.io."""
        try:
            # Generate fly.toml configuration
            fly_config = self._generate_backend_config(app_name, environment)
            fly_config_path = project_path / "fly.toml"
            
            with open(fly_config_path, "w") as f:
                toml.dump(fly_config, f)
            
            # Generate Dockerfile if not exists
            dockerfile_path = project_path / "Dockerfile"
            if not dockerfile_path.exists():
                self._generate_backend_dockerfile(dockerfile_path)
            
            # Deploy using flyctl
            result = await self._run_flyctl_deploy(project_path, app_name)
            
            return {
                "app_name": app_name,
                "environment": environment,
                "url": f"https://{app_name}.fly.dev",
                "deployment_id": result.get("deployment_id"),
                "status": "deployed"
            }
            
        except Exception as e:
            self.logger.error(f"Backend deployment failed: {e}")
            raise
    
    async def deploy_playground(self, project_path: Path, app_name: str, 
                              backend_url: str) -> Dict[str, Any]:
        """Deploy PBT playground UI to Fly.io."""
        try:
            ui_app_name = f"{app_name}-ui"
            
            # Generate fly.toml for UI
            fly_config = self._generate_ui_config(ui_app_name, backend_url)
            fly_config_path = project_path / "fly-ui.toml"
            
            with open(fly_config_path, "w") as f:
                toml.dump(fly_config, f)
            
            # Generate UI Dockerfile
            dockerfile_path = project_path / "Dockerfile.ui"
            self._generate_ui_dockerfile(dockerfile_path, backend_url)
            
            # Deploy UI
            result = await self._run_flyctl_deploy(
                project_path, ui_app_name, config_file="fly-ui.toml"
            )
            
            return {
                "app_name": ui_app_name,
                "url": f"https://{ui_app_name}.fly.dev",
                "backend_url": backend_url,
                "deployment_id": result.get("deployment_id"),
                "status": "deployed"
            }
            
        except Exception as e:
            self.logger.error(f"Playground deployment failed: {e}")
            raise
    
    async def scale_app(self, app_name: str, scale_config: Dict[str, Any]) -> Dict[str, Any]:
        """Scale Fly.io app resources."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/apps/{app_name}/machines",
                    headers=headers,
                    json=scale_config
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Scaled app {app_name}")
                        return result
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to scale app: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to scale app: {e}")
            raise
    
    async def get_app_status(self, app_name: str) -> Dict[str, Any]:
        """Get Fly.io app status and metrics."""
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/apps/{app_name}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error = await response.text()
                        raise Exception(f"Failed to get app status: {error}")
                        
        except Exception as e:
            self.logger.error(f"Failed to get app status: {e}")
            raise
    
    async def get_logs(self, app_name: str, instance_id: Optional[str] = None,
                      lines: int = 100) -> List[str]:
        """Get application logs from Fly.io."""
        try:
            cmd = ["flyctl", "logs", "-a", app_name, "-n", str(lines)]
            if instance_id:
                cmd.extend(["-i", instance_id])
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )
            
            return result.stdout.split('\n')
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get logs: {e}")
            raise
    
    async def setup_secrets(self, app_name: str, secrets: Dict[str, str]) -> bool:
        """Set environment secrets for Fly.io app."""
        try:
            for key, value in secrets.items():
                cmd = ["flyctl", "secrets", "set", f"{key}={value}", "-a", app_name]
                
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"Failed to set secret {key}")
            
            self.logger.info(f"Set {len(secrets)} secrets for {app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup secrets: {e}")
            return False
    
    def _generate_backend_config(self, app_name: str, environment: str) -> Dict[str, Any]:
        """Generate fly.toml configuration for backend."""
        return {
            "app": app_name,
            "primary_region": "sjc",
            "build": {
                "dockerfile": "Dockerfile"
            },
            "env": {
                "ENVIRONMENT": environment,
                "PORT": "8080"
            },
            "services": [{
                "internal_port": 8080,
                "protocol": "tcp",
                "auto_stop_machines": True,
                "auto_start_machines": True,
                "min_machines_running": 0,
                "processes": ["app"],
                "ports": [{
                    "port": 80,
                    "handlers": ["http"]
                }, {
                    "port": 443,
                    "handlers": ["tls", "http"]
                }],
                "http_checks": [{
                    "interval": "10s",
                    "timeout": "2s",
                    "grace_period": "5s",
                    "method": "get",
                    "path": "/health"
                }]
            }],
            "metrics": {
                "port": 9091,
                "path": "/metrics"
            }
        }
    
    def _generate_ui_config(self, app_name: str, backend_url: str) -> Dict[str, Any]:
        """Generate fly.toml configuration for UI."""
        return {
            "app": app_name,
            "primary_region": "sjc",
            "build": {
                "dockerfile": "Dockerfile.ui"
            },
            "env": {
                "REACT_APP_API_URL": backend_url,
                "PORT": "3000"
            },
            "services": [{
                "internal_port": 3000,
                "protocol": "tcp",
                "auto_stop_machines": True,
                "auto_start_machines": True,
                "min_machines_running": 0,
                "processes": ["app"],
                "ports": [{
                    "port": 80,
                    "handlers": ["http"]
                }, {
                    "port": 443,
                    "handlers": ["tls", "http"]
                }],
                "http_checks": [{
                    "interval": "10s",
                    "timeout": "2s",
                    "grace_period": "5s",
                    "method": "get",
                    "path": "/"
                }]
            }]
        }
    
    def _generate_backend_dockerfile(self, dockerfile_path: Path):
        """Generate Dockerfile for PBT backend."""
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install PBT
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 pbtuser && chown -R pbtuser:pbtuser /app
USER pbtuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "-m", "pbt.server", "--host", "0.0.0.0", "--port", "8080"]
"""
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
    
    def _generate_ui_dockerfile(self, dockerfile_path: Path, backend_url: str):
        """Generate Dockerfile for PBT UI."""
        dockerfile_content = f"""FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Set environment variables
ENV REACT_APP_API_URL={backend_url}

# Build application
RUN npm run build

FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
    
    async def _run_flyctl_deploy(self, project_path: Path, app_name: str,
                                config_file: str = "fly.toml") -> Dict[str, Any]:
        """Run flyctl deploy command."""
        try:
            cmd = [
                "flyctl", "deploy",
                "--app", app_name,
                "--config", str(project_path / config_file),
                "--local-only"
            ]
            
            result = subprocess.run(
                cmd, cwd=project_path, capture_output=True, text=True, check=True
            )
            
            # Parse deployment result
            deployment_info = {
                "deployment_id": None,
                "status": "success",
                "output": result.stdout
            }
            
            # Extract deployment ID from output if available
            lines = result.stdout.split('\n')
            for line in lines:
                if "deployment" in line.lower() and "id" in line.lower():
                    # Extract deployment ID using regex or string parsing
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "deployment" in part.lower() and i + 1 < len(parts):
                            deployment_info["deployment_id"] = parts[i + 1]
                            break
            
            return deployment_info
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed: {e.stderr}")
            raise Exception(f"Deployment failed: {e.stderr}")