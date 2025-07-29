"""PostgreSQL with pgvector extension integration"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
import asyncpg
import numpy as np


class PgVectorIntegration:
    """PostgreSQL + pgvector integration for prompt similarity search"""
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = (
                f"postgresql://"
                f"{user or os.getenv('POSTGRES_USER', 'postgres')}:"
                f"{password or os.getenv('POSTGRES_PASSWORD', 'password')}@"
                f"{host or os.getenv('POSTGRES_HOST', 'localhost')}:"
                f"{port or os.getenv('POSTGRES_PORT', 5432)}/"
                f"{database or os.getenv('POSTGRES_DB', 'pbt')}"
            )
        
        self.connection = None
    
    async def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = await asyncpg.connect(self.connection_string)
            
            # Enable pgvector extension
            await self.connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            return True
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            await self.connection.close()
    
    async def create_prompts_table(self, table_name: str = "prompts") -> bool:
        """Create prompts table with vector column"""
        try:
            await self.connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content JSONB NOT NULL,
                    embedding vector(1536),
                    metadata JSONB,
                    success_rate FLOAT DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create vector index for similarity search
            await self.connection.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                ON {table_name} USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            # Create metadata indexes
            await self.connection.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_metadata_idx 
                ON {table_name} USING GIN (metadata)
            """)
            
            return True
        except Exception as e:
            print(f"Failed to create table: {e}")
            return False
    
    async def insert_prompt(
        self,
        table_name: str,
        prompt_id: str,
        name: str,
        content: Dict[str, Any],
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Insert a new prompt"""
        try:
            await self.connection.execute(
                f"""
                INSERT INTO {table_name} 
                (id, name, content, embedding, metadata)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                """,
                prompt_id,
                name,
                json.dumps(content),
                embedding,
                json.dumps(metadata or {})
            )
            return True
        except Exception as e:
            print(f"Failed to insert prompt: {e}")
            return False
    
    async def search_similar_prompts(
        self,
        table_name: str,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar prompts using cosine similarity"""
        try:
            # Build filter conditions
            where_conditions = ["1=1"]
            params = [query_embedding, limit]
            param_count = 2
            
            if filters:
                for key, value in filters.items():
                    param_count += 1
                    if key == "success_rate_min":
                        where_conditions.append(f"success_rate >= ${param_count}")
                        params.append(value)
                    elif key == "tags":
                        where_conditions.append(f"metadata->'tags' ? ${param_count}")
                        params.append(value)
                    elif key == "category":
                        where_conditions.append(f"metadata->>'category' = ${param_count}")
                        params.append(value)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    id,
                    name,
                    content,
                    metadata,
                    success_rate,
                    usage_count,
                    1 - (embedding <=> $1) as similarity
                FROM {table_name}
                WHERE {where_clause}
                    AND 1 - (embedding <=> $1) >= {similarity_threshold}
                ORDER BY embedding <=> $1
                LIMIT $2
            """
            
            rows = await self.connection.fetch(query, *params)
            
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "name": row["name"],
                    "content": json.loads(row["content"]),
                    "metadata": json.loads(row["metadata"]),
                    "success_rate": row["success_rate"],
                    "usage_count": row["usage_count"],
                    "similarity": float(row["similarity"])
                })
            
            return results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    async def get_fallback_prompts(
        self,
        table_name: str,
        failed_prompt_embedding: List[float],
        context: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get high-performing fallback prompts"""
        try:
            # Search for prompts with high success rates
            filters = {
                "success_rate_min": 0.8,
                "category": context.get("category", "")
            }
            
            # Remove empty category filter
            if not filters["category"]:
                del filters["category"]
            
            fallbacks = await self.search_similar_prompts(
                table_name=table_name,
                query_embedding=failed_prompt_embedding,
                limit=limit * 2,
                similarity_threshold=0.5,  # Lower threshold for fallbacks
                filters=filters
            )
            
            # Sort by success rate first, then similarity
            sorted_fallbacks = sorted(
                fallbacks,
                key=lambda x: (x["success_rate"], x["similarity"]),
                reverse=True
            )
            
            return sorted_fallbacks[:limit]
            
        except Exception as e:
            print(f"Fallback search failed: {e}")
            return []
    
    async def update_prompt_metrics(
        self,
        table_name: str,
        prompt_id: str,
        success_rate: Optional[float] = None,
        usage_count_increment: int = 1
    ) -> bool:
        """Update prompt performance metrics"""
        try:
            updates = ["updated_at = NOW()"]
            params = []
            param_count = 0
            
            if success_rate is not None:
                param_count += 1
                updates.append(f"success_rate = ${param_count}")
                params.append(success_rate)
            
            if usage_count_increment > 0:
                updates.append(f"usage_count = usage_count + {usage_count_increment}")
            
            param_count += 1
            params.append(prompt_id)
            
            query = f"""
                UPDATE {table_name}
                SET {', '.join(updates)}
                WHERE id = ${param_count}
            """
            
            await self.connection.execute(query, *params)
            return True
            
        except Exception as e:
            print(f"Failed to update metrics: {e}")
            return False
    
    async def get_prompt_analytics(
        self,
        table_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get prompt usage analytics"""
        try:
            # Get top performing prompts
            top_prompts = await self.connection.fetch(f"""
                SELECT id, name, success_rate, usage_count
                FROM {table_name}
                WHERE updated_at >= NOW() - INTERVAL '{days} days'
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT 10
            """)
            
            # Get category breakdown
            category_stats = await self.connection.fetch(f"""
                SELECT 
                    metadata->>'category' as category,
                    COUNT(*) as count,
                    AVG(success_rate) as avg_success_rate
                FROM {table_name}
                WHERE metadata->>'category' IS NOT NULL
                GROUP BY metadata->>'category'
                ORDER BY count DESC
            """)
            
            # Get overall stats
            overall_stats = await self.connection.fetchrow(f"""
                SELECT 
                    COUNT(*) as total_prompts,
                    AVG(success_rate) as avg_success_rate,
                    SUM(usage_count) as total_usage
                FROM {table_name}
            """)
            
            return {
                "success": True,
                "period_days": days,
                "top_prompts": [dict(row) for row in top_prompts],
                "category_breakdown": [dict(row) for row in category_stats],
                "overall_stats": dict(overall_stats)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_prompt_clusters(
        self,
        table_name: str,
        cluster_count: int = 10
    ) -> Dict[str, Any]:
        """Create semantic clusters of prompts"""
        try:
            # Get all embeddings
            rows = await self.connection.fetch(f"""
                SELECT id, name, embedding, metadata
                FROM {table_name}
                WHERE embedding IS NOT NULL
            """)
            
            if len(rows) < cluster_count:
                return {"success": False, "error": "Not enough prompts for clustering"}
            
            # Extract embeddings
            embeddings = []
            prompt_data = []
            
            for row in rows:
                embeddings.append(list(row["embedding"]))
                prompt_data.append({
                    "id": row["id"],
                    "name": row["name"],
                    "metadata": json.loads(row["metadata"])
                })
            
            # Simple clustering based on categories for now
            # In production, you'd use proper clustering algorithms
            clusters = {}
            for i, data in enumerate(prompt_data):
                category = data["metadata"].get("category", "uncategorized")
                if category not in clusters:
                    clusters[category] = []
                clusters[category].append(data)
            
            return {
                "success": True,
                "clusters": clusters,
                "cluster_count": len(clusters)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_prompt(self, table_name: str, prompt_id: str) -> bool:
        """Delete a prompt"""
        try:
            await self.connection.execute(
                f"DELETE FROM {table_name} WHERE id = $1",
                prompt_id
            )
            return True
        except Exception as e:
            print(f"Failed to delete prompt: {e}")
            return False
    
    async def bulk_insert_prompts(
        self,
        table_name: str,
        prompts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk insert multiple prompts"""
        try:
            async with self.connection.transaction():
                for prompt in prompts:
                    await self.insert_prompt(
                        table_name=table_name,
                        prompt_id=prompt["id"],
                        name=prompt["name"],
                        content=prompt["content"],
                        embedding=prompt["embedding"],
                        metadata=prompt.get("metadata", {})
                    )
            
            return {
                "success": True,
                "inserted_count": len(prompts)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}