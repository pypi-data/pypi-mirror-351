"""Slack notification integration"""

import os
import json
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime


class SlackNotifier:
    """Send notifications to Slack channels"""
    
    def __init__(self, webhook_url: Optional[str] = None, token: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.api_base = "https://slack.com/api"
    
    async def send_webhook_message(
        self,
        text: str,
        channel: Optional[str] = None,
        username: Optional[str] = "PBT Bot",
        icon_emoji: Optional[str] = ":robot_face:",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send message via webhook"""
        if not self.webhook_url:
            return False
        
        payload = {
            "text": text,
            "username": username,
            "icon_emoji": icon_emoji
        }
        
        if channel:
            payload["channel"] = channel
        
        if attachments:
            payload["attachments"] = attachments
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def send_api_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message via Slack API"""
        if not self.token:
            return {"success": False, "error": "No Slack token configured"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            data["blocks"] = blocks
        
        if thread_ts:
            data["thread_ts"] = thread_ts
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat.postMessage",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    return {
                        "success": result.get("ok", False),
                        "ts": result.get("ts"),
                        "error": result.get("error")
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def notify_prompt_published(
        self,
        prompt_name: str,
        version: str,
        author: str,
        environment: str = "production"
    ):
        """Notify when a prompt is published"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 Prompt Published"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Prompt:*\n{prompt_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Version:*\n{version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Author:*\n{author}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{environment}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Published at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                ]
            }
        ]
        
        text = f"Prompt '{prompt_name}' v{version} published to {environment} by {author}"
        
        if self.webhook_url:
            await self.send_webhook_message(text, attachments=[{"blocks": blocks}])
        elif self.token:
            await self.send_api_message("#deployments", text, blocks=blocks)
    
    async def notify_test_results(
        self,
        prompt_name: str,
        test_type: str,
        passed: int,
        failed: int,
        score: float
    ):
        """Notify test results"""
        emoji = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
        color = "good" if failed == 0 else "warning" if passed > failed else "danger"
        
        attachments = [{
            "color": color,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *Test Results for {prompt_name}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Test Type:*\n{test_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Results:*\n{passed} passed, {failed} failed"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Score:*\n{score:.1f}/10"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{'PASSED' if failed == 0 else 'FAILED'}"
                        }
                    ]
                }
            ]
        }]
        
        text = f"Test results for '{prompt_name}': {passed}/{passed+failed} passed (Score: {score:.1f}/10)"
        
        await self.send_webhook_message(text, attachments=attachments)
    
    async def notify_deployment(
        self,
        prompt_name: str,
        environment: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Notify deployment status"""
        emoji_map = {
            "started": "🔄",
            "success": "✅",
            "failed": "❌",
            "rollback": "⚠️"
        }
        
        color_map = {
            "started": "#3AA3E3",
            "success": "good",
            "failed": "danger",
            "rollback": "warning"
        }
        
        emoji = emoji_map.get(status, "📌")
        color = color_map.get(status, "#3AA3E3")
        
        fields = [
            {
                "type": "mrkdwn",
                "text": f"*Prompt:*\n{prompt_name}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Environment:*\n{environment}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Status:*\n{status.upper()}"
            }
        ]
        
        if details:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Details:*\n{json.dumps(details, indent=2)}"
            })
        
        attachments = [{
            "color": color,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *Deployment Update*"
                    }
                },
                {
                    "type": "section",
                    "fields": fields
                }
            ]
        }]
        
        text = f"Deployment {status}: '{prompt_name}' to {environment}"
        
        await self.send_webhook_message(text, attachments=attachments)