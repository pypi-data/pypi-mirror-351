"""Fly.io deployment integration"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List


class FlyIODeployment:
    """Deploy PBT applications to Fly.io"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("FLY_API_TOKEN")
        self.org = os.getenv("FLY_ORG", "personal")
    
    async def create_app(
        self,
        app_name: str,
        region: str = "dfw",
        org: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Fly.io app"""
        cmd = [
            "flyctl", "apps", "create", app_name,
            "--org", org or self.org,
            "--json"
        ]
        
        try:
            result = await self._run_flyctl(cmd)
            if result["success"]:
                return {
                    "success": True,
                    "app_name": app_name,
                    "organization": org or self.org
                }
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def deploy_from_dockerfile(
        self,
        app_name: str,
        dockerfile_path: str = "Dockerfile",
        build_args: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Deploy app using Dockerfile"""
        cmd = ["flyctl", "deploy", "--app", app_name, "--dockerfile", dockerfile_path]
        
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
        
        try:
            result = await self._run_flyctl(cmd)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def set_secrets(
        self,
        app_name: str,
        secrets: Dict[str, str]
    ) -> Dict[str, Any]:
        """Set environment secrets"""
        cmd = ["flyctl", "secrets", "set", "--app", app_name]
        
        for key, value in secrets.items():
            cmd.append(f"{key}={value}")
        
        try:
            result = await self._run_flyctl(cmd)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scale_app(
        self,
        app_name: str,
        instances: int = 1,
        memory: str = "256mb"
    ) -> Dict[str, Any]:
        """Scale the application"""
        cmd = [
            "flyctl", "scale", "count", str(instances),
            "--app", app_name,
            "--memory", memory
        ]
        
        try:
            result = await self._run_flyctl(cmd)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_app_status(self, app_name: str) -> Dict[str, Any]:
        """Get app deployment status"""
        cmd = ["flyctl", "status", "--app", app_name, "--json"]
        
        try:
            result = await self._run_flyctl(cmd)
            if result["success"]:
                status_data = json.loads(result["output"])
                return {
                    "success": True,
                    "status": status_data.get("Status", "unknown"),
                    "hostname": status_data.get("Hostname", ""),
                    "deployed": status_data.get("Deployed", False)
                }
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_fly_toml(
        self,
        app_name: str,
        port: int = 8000,
        env_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate fly.toml configuration"""
        config = {
            "app": app_name,
            "kill_signal": "SIGINT",
            "kill_timeout": 5,
            "processes": [],
            "env": env_vars or {},
            "experimental": {
                "allowed_public_ports": [],
                "auto_rollback": True
            },
            "services": [
                {
                    "http_checks": [],
                    "internal_port": port,
                    "processes": ["app"],
                    "protocol": "tcp",
                    "script_checks": [],
                    "tcp_checks": [
                        {
                            "grace_period": "1s",
                            "interval": "15s",
                            "restart_limit": 0,
                            "timeout": "2s"
                        }
                    ],
                    "ports": [
                        {
                            "force_https": True,
                            "handlers": ["http"],
                            "port": 80
                        },
                        {
                            "handlers": ["tls", "http"],
                            "port": 443
                        }
                    ]
                }
            ]
        }
        
        # Convert to TOML format (simplified)
        toml_content = f"""app = "{app_name}"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[env]
"""
        
        if env_vars:
            for key, value in env_vars.items():
                toml_content += f'  {key} = "{value}"\n'
        
        toml_content += f"""
[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = {port}
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
"""
        
        return toml_content
    
    async def _run_flyctl(self, cmd: List[str]) -> Dict[str, Any]:
        """Run flyctl command"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode().strip()
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode().strip()
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": "flyctl not found. Please install Fly.io CLI"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }