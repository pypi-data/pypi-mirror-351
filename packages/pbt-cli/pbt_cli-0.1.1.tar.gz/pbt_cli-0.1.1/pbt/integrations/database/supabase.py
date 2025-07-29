"""Supabase Integration for PBT"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client
from postgrest.exceptions import APIError


class SupabaseIntegration:
    """Supabase integration for auth, multi-user support, and prompt database"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided")
        
        self.client: Client = create_client(self.url, self.key)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required tables exist in Supabase"""
        # In production, these would be created via Supabase migrations
        # This is a reference for the expected schema
        pass
    
    # ===== Authentication =====
    
    async def sign_up(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_out(self) -> bool:
        """Sign out current user"""
        try:
            self.client.auth.sign_out()
            return True
        except:
            return False
    
    def get_current_user(self):
        """Get current authenticated user"""
        return self.client.auth.get_user()
    
    # ===== Prompt Management =====
    
    async def create_prompt(
        self,
        name: str,
        content: Dict[str, Any],
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new prompt in the database"""
        try:
            data = {
                "name": name,
                "content": json.dumps(content),
                "user_id": user_id,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("prompts").insert(data).execute()
            return {"success": True, "prompt": response.data[0]}
            
        except APIError as e:
            return {"success": False, "error": str(e)}
    
    async def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a prompt by ID"""
        try:
            response = self.client.table("prompts").select("*").eq("id", prompt_id).execute()
            if response.data:
                prompt = response.data[0]
                prompt["content"] = json.loads(prompt["content"])
                prompt["metadata"] = json.loads(prompt["metadata"])
                return prompt
            return None
        except:
            return None
    
    async def list_prompts(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List prompts with optional filtering"""
        try:
            query = self.client.table("prompts").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = query.limit(limit).offset(offset).execute()
            
            prompts = []
            for prompt in response.data:
                prompt["content"] = json.loads(prompt["content"])
                prompt["metadata"] = json.loads(prompt["metadata"])
                prompts.append(prompt)
            
            return prompts
        except:
            return []
    
    async def update_prompt(
        self,
        prompt_id: str,
        content: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing prompt"""
        try:
            data = {"updated_at": datetime.utcnow().isoformat()}
            
            if content is not None:
                data["content"] = json.dumps(content)
            
            if metadata is not None:
                data["metadata"] = json.dumps(metadata)
            
            self.client.table("prompts").update(data).eq("id", prompt_id).execute()
            return True
        except:
            return False
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        try:
            self.client.table("prompts").delete().eq("id", prompt_id).execute()
            return True
        except:
            return False
    
    # ===== Test Results Storage =====
    
    async def save_test_result(
        self,
        prompt_id: str,
        test_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Save test results to database"""
        try:
            data = {
                "prompt_id": prompt_id,
                "user_id": user_id,
                "test_data": json.dumps(test_data),
                "score": test_data.get("average_score", 0),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("test_results").insert(data).execute()
            return {"success": True, "result": response.data[0]}
            
        except APIError as e:
            return {"success": False, "error": str(e)}
    
    async def get_test_results(
        self,
        prompt_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get test results for a prompt"""
        try:
            response = self.client.table("test_results") \
                .select("*") \
                .eq("prompt_id", prompt_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            results = []
            for result in response.data:
                result["test_data"] = json.loads(result["test_data"])
                results.append(result)
            
            return results
        except:
            return []
    
    # ===== Team Collaboration =====
    
    async def create_team(
        self,
        name: str,
        owner_id: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new team"""
        try:
            data = {
                "name": name,
                "owner_id": owner_id,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("teams").insert(data).execute()
            team_id = response.data[0]["id"]
            
            # Add owner as team member
            await self.add_team_member(team_id, owner_id, "owner")
            
            return {"success": True, "team": response.data[0]}
            
        except APIError as e:
            return {"success": False, "error": str(e)}
    
    async def add_team_member(
        self,
        team_id: str,
        user_id: str,
        role: str = "member"
    ) -> bool:
        """Add a member to a team"""
        try:
            data = {
                "team_id": team_id,
                "user_id": user_id,
                "role": role,
                "joined_at": datetime.utcnow().isoformat()
            }
            
            self.client.table("team_members").insert(data).execute()
            return True
        except:
            return False
    
    async def share_prompt_with_team(
        self,
        prompt_id: str,
        team_id: str,
        permissions: List[str] = None
    ) -> bool:
        """Share a prompt with a team"""
        try:
            data = {
                "prompt_id": prompt_id,
                "team_id": team_id,
                "permissions": permissions or ["read"],
                "shared_at": datetime.utcnow().isoformat()
            }
            
            self.client.table("team_prompts").insert(data).execute()
            return True
        except:
            return False
    
    # ===== Deployment Management =====
    
    async def create_deployment(
        self,
        prompt_id: str,
        environment: str,
        config: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Track prompt deployments"""
        try:
            data = {
                "prompt_id": prompt_id,
                "environment": environment,
                "config": json.dumps(config),
                "user_id": user_id,
                "status": "deploying",
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("deployments").insert(data).execute()
            return {"success": True, "deployment": response.data[0]}
            
        except APIError as e:
            return {"success": False, "error": str(e)}
    
    async def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update deployment status"""
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if metadata:
                data["metadata"] = json.dumps(metadata)
            
            self.client.table("deployments").update(data).eq("id", deployment_id).execute()
            return True
        except:
            return False