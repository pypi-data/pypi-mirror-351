"""Notion integration for importing/exporting prompts"""

import os
import json
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml


class NotionImporter:
    """Import prompts from Notion"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("NOTION_TOKEN")
        self.api_base = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def import_from_database(self, database_id: str) -> List[Dict[str, Any]]:
        """Import prompts from a Notion database"""
        if not self.token:
            raise ValueError("Notion token not configured")
        
        prompts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Query database
                async with session.post(
                    f"{self.api_base}/databases/{database_id}/query",
                    headers=self.headers,
                    json={}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Notion API error: {error_text}")
                    
                    data = await response.json()
                    
                    for page in data.get("results", []):
                        prompt = await self._parse_page_to_prompt(page, session)
                        if prompt:
                            prompts.append(prompt)
        
        except Exception as e:
            raise Exception(f"Failed to import from Notion: {str(e)}")
        
        return prompts
    
    async def import_from_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Import a single prompt from a Notion page"""
        if not self.token:
            raise ValueError("Notion token not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get page
                async with session.get(
                    f"{self.api_base}/pages/{page_id}",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        return None
                    
                    page = await response.json()
                    return await self._parse_page_to_prompt(page, session)
        
        except:
            return None
    
    async def _parse_page_to_prompt(self, page: Dict[str, Any], session) -> Optional[Dict[str, Any]]:
        """Parse Notion page into PBT prompt format"""
        properties = page.get("properties", {})
        
        # Extract basic information
        name = self._get_title(properties.get("Name", properties.get("Title", {})))
        if not name:
            return None
        
        # Get page content
        content = await self._get_page_content(page["id"], session)
        
        # Build prompt structure
        prompt = {
            "name": name,
            "version": self._get_text(properties.get("Version", {})) or "1.0",
            "model": self._get_select(properties.get("Model", {})) or "claude",
            "template": content.get("template", ""),
            "variables": {},
            "metadata": {
                "imported_from": "notion",
                "notion_page_id": page["id"],
                "imported_at": datetime.utcnow().isoformat()
            }
        }
        
        # Extract variables
        variables_text = content.get("variables", "")
        if variables_text:
            try:
                prompt["variables"] = yaml.safe_load(variables_text)
            except:
                # Try parsing as simple list
                for line in variables_text.split("\n"):
                    if line.strip():
                        var_name = line.strip().replace("-", "").strip()
                        prompt["variables"][var_name] = {"type": "string"}
        
        # Extract metadata
        if "Tags" in properties:
            prompt["metadata"]["tags"] = self._get_multi_select(properties["Tags"])
        
        if "Description" in properties:
            prompt["description"] = self._get_text(properties["Description"])
        
        return prompt
    
    async def _get_page_content(self, page_id: str, session) -> Dict[str, str]:
        """Get content blocks from a Notion page"""
        content = {"template": "", "variables": ""}
        current_section = None
        
        async with session.get(
            f"{self.api_base}/blocks/{page_id}/children",
            headers=self.headers
        ) as response:
            if response.status != 200:
                return content
            
            data = await response.json()
            
            for block in data.get("results", []):
                block_type = block.get("type")
                
                # Handle headings as section markers
                if block_type in ["heading_1", "heading_2", "heading_3"]:
                    text = self._get_block_text(block)
                    if "template" in text.lower() or "prompt" in text.lower():
                        current_section = "template"
                    elif "variable" in text.lower():
                        current_section = "variables"
                
                # Handle content blocks
                elif block_type in ["paragraph", "code"]:
                    text = self._get_block_text(block)
                    if current_section == "template":
                        content["template"] += text + "\n"
                    elif current_section == "variables":
                        content["variables"] += text + "\n"
                    elif not current_section and text:
                        # Default to template if no section specified
                        content["template"] += text + "\n"
        
        # Clean up content
        content["template"] = content["template"].strip()
        content["variables"] = content["variables"].strip()
        
        return content
    
    def _get_title(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract title from property"""
        for title_item in prop.get("title", []):
            if "text" in title_item:
                return title_item["text"]["content"]
        return None
    
    def _get_text(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract text from property"""
        for text_item in prop.get("rich_text", []):
            if "text" in text_item:
                return text_item["text"]["content"]
        return None
    
    def _get_select(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract select value from property"""
        select = prop.get("select", {})
        return select.get("name")
    
    def _get_multi_select(self, prop: Dict[str, Any]) -> List[str]:
        """Extract multi-select values from property"""
        return [item["name"] for item in prop.get("multi_select", [])]
    
    def _get_block_text(self, block: Dict[str, Any]) -> str:
        """Extract text from a block"""
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        
        text_parts = []
        for text_item in block_data.get("rich_text", []):
            if "text" in text_item:
                text_parts.append(text_item["text"]["content"])
        
        return "".join(text_parts)


class NotionExporter:
    """Export prompts to Notion"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("NOTION_TOKEN")
        self.api_base = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def export_to_database(
        self,
        database_id: str,
        prompts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Export prompts to a Notion database"""
        if not self.token:
            raise ValueError("Notion token not configured")
        
        results = []
        
        for prompt in prompts:
            result = await self.create_page(database_id, prompt)
            results.append(result)
        
        return results
    
    async def create_page(
        self,
        database_id: str,
        prompt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a Notion page for a prompt"""
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": prompt.get("name", "Untitled Prompt")
                        }
                    }
                ]
            }
        }
        
        # Add version
        if "version" in prompt:
            properties["Version"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": prompt["version"]
                        }
                    }
                ]
            }
        
        # Add model
        if "model" in prompt:
            properties["Model"] = {
                "select": {
                    "name": prompt["model"]
                }
            }
        
        # Add description
        if "description" in prompt:
            properties["Description"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": prompt["description"]
                        }
                    }
                ]
            }
        
        # Add tags
        metadata = prompt.get("metadata", {})
        if "tags" in metadata:
            properties["Tags"] = {
                "multi_select": [
                    {"name": tag} for tag in metadata["tags"]
                ]
            }
        
        # Create page
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties,
            "children": self._create_content_blocks(prompt)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/pages",
                    headers=self.headers,
                    json=page_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to create page: {error_text}"
                        }
                    
                    page = await response.json()
                    return {
                        "success": True,
                        "page_id": page["id"],
                        "url": page.get("url", "")
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_content_blocks(self, prompt: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create content blocks for the prompt"""
        blocks = []
        
        # Add template section
        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"text": {"content": "Template"}}]
            }
        })
        
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"text": {"content": prompt.get("template", "")}}],
                "language": "plain text"
            }
        })
        
        # Add variables section
        if prompt.get("variables"):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": "Variables"}}]
                }
            })
            
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"text": {"content": yaml.dump(prompt["variables"], default_flow_style=False)}}],
                    "language": "yaml"
                }
            })
        
        # Add metadata section
        metadata = prompt.get("metadata", {})
        if metadata:
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": "Metadata"}}]
                }
            })
            
            # Format metadata as bullets
            for key, value in metadata.items():
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"text": {"content": f"{key}: {value}"}}]
                    }
                })
        
        return blocks