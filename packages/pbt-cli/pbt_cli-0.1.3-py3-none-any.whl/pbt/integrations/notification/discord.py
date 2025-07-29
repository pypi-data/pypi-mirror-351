"""Discord notification integration"""

import os
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime


class DiscordNotifier:
    """Send notifications to Discord channels"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    
    async def send_message(
        self,
        content: str,
        username: Optional[str] = "PBT Bot",
        avatar_url: Optional[str] = None,
        embeds: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send message to Discord"""
        if not self.webhook_url:
            return False
        
        payload = {
            "content": content,
            "username": username
        }
        
        if avatar_url:
            payload["avatar_url"] = avatar_url
        
        if embeds:
            payload["embeds"] = embeds
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload
                ) as response:
                    return response.status in [200, 204]
        except:
            return False
    
    async def notify_prompt_published(
        self,
        prompt_name: str,
        version: str,
        author: str,
        environment: str = "production"
    ):
        """Notify when a prompt is published"""
        embed = {
            "title": "🚀 Prompt Published",
            "color": 0x00ff00,  # Green
            "fields": [
                {"name": "Prompt", "value": prompt_name, "inline": True},
                {"name": "Version", "value": version, "inline": True},
                {"name": "Author", "value": author, "inline": True},
                {"name": "Environment", "value": environment, "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PBT Deployment"}
        }
        
        content = f"**{prompt_name}** v{version} has been published to {environment}!"
        
        await self.send_message(content, embeds=[embed])
    
    async def notify_test_results(
        self,
        prompt_name: str,
        test_type: str,
        passed: int,
        failed: int,
        score: float
    ):
        """Notify test results"""
        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Determine color based on results
        if failed == 0:
            color = 0x00ff00  # Green
            status = "✅ PASSED"
        elif passed > failed:
            color = 0xffff00  # Yellow
            status = "⚠️ PARTIAL"
        else:
            color = 0xff0000  # Red
            status = "❌ FAILED"
        
        embed = {
            "title": f"Test Results: {prompt_name}",
            "color": color,
            "fields": [
                {"name": "Test Type", "value": test_type, "inline": True},
                {"name": "Status", "value": status, "inline": True},
                {"name": "Score", "value": f"{score:.1f}/10", "inline": True},
                {"name": "Passed", "value": str(passed), "inline": True},
                {"name": "Failed", "value": str(failed), "inline": True},
                {"name": "Pass Rate", "value": f"{pass_rate:.1f}%", "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PBT Test Results"}
        }
        
        content = f"Test completed for **{prompt_name}**: {status}"
        
        await self.send_message(content, embeds=[embed])
    
    async def notify_deployment(
        self,
        prompt_name: str,
        environment: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Notify deployment status"""
        color_map = {
            "started": 0x3498db,    # Blue
            "success": 0x00ff00,    # Green
            "failed": 0xff0000,     # Red
            "rollback": 0xffff00    # Yellow
        }
        
        emoji_map = {
            "started": "🔄",
            "success": "✅",
            "failed": "❌",
            "rollback": "⚠️"
        }
        
        color = color_map.get(status, 0x808080)
        emoji = emoji_map.get(status, "📌")
        
        fields = [
            {"name": "Prompt", "value": prompt_name, "inline": True},
            {"name": "Environment", "value": environment, "inline": True},
            {"name": "Status", "value": f"{emoji} {status.upper()}", "inline": True}
        ]
        
        if details:
            for key, value in details.items():
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value),
                    "inline": True
                })
        
        embed = {
            "title": "Deployment Update",
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PBT Deployment"}
        }
        
        content = f"Deployment {status}: **{prompt_name}** → {environment}"
        
        await self.send_message(content, embeds=[embed])
    
    async def notify_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Notify errors"""
        fields = [
            {"name": "Error Type", "value": error_type, "inline": True},
            {"name": "Message", "value": error_message[:1024], "inline": False}
        ]
        
        if context:
            for key, value in context.items():
                fields.append({
                    "name": key.replace("_", " ").title(),
                    "value": str(value)[:1024],
                    "inline": True
                })
        
        embed = {
            "title": "⚠️ PBT Error",
            "color": 0xff0000,  # Red
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PBT Error Handler"}
        }
        
        content = f"Error occurred: **{error_type}**"
        
        await self.send_message(content, embeds=[embed])
    
    async def notify_batch_operation(
        self,
        operation: str,
        total: int,
        succeeded: int,
        failed: int,
        details: Optional[List[str]] = None
    ):
        """Notify batch operation results"""
        success_rate = (succeeded / total * 100) if total > 0 else 0
        
        if failed == 0:
            color = 0x00ff00  # Green
            status = "✅ Complete"
        elif succeeded > failed:
            color = 0xffff00  # Yellow  
            status = "⚠️ Partial Success"
        else:
            color = 0xff0000  # Red
            status = "❌ Failed"
        
        fields = [
            {"name": "Operation", "value": operation, "inline": True},
            {"name": "Status", "value": status, "inline": True},
            {"name": "Total", "value": str(total), "inline": True},
            {"name": "Succeeded", "value": str(succeeded), "inline": True},
            {"name": "Failed", "value": str(failed), "inline": True},
            {"name": "Success Rate", "value": f"{success_rate:.1f}%", "inline": True}
        ]
        
        if details and len(details) > 0:
            details_text = "\n".join(details[:10])  # Limit to 10 items
            if len(details) > 10:
                details_text += f"\n... and {len(details) - 10} more"
            
            fields.append({
                "name": "Details",
                "value": details_text[:1024],
                "inline": False
            })
        
        embed = {
            "title": f"Batch Operation: {operation}",
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "PBT Batch Operations"}
        }
        
        content = f"Batch operation completed: **{operation}** - {status}"
        
        await self.send_message(content, embeds=[embed])