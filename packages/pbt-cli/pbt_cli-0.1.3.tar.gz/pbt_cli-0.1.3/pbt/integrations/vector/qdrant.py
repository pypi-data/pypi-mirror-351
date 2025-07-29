"""Qdrant vector database integration"""

import os
import uuid
from typing import Dict, Any, List, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.http import models


class QdrantIntegration:
    """Qdrant integration for similarity-based prompt search and eval fallback"""
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        prefer_grpc: bool = True
    ):
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        
        # Initialize client
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            prefer_grpc=prefer_grpc
        )
    
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,  # OpenAI embedding size
        distance: str = "Cosine"
    ) -> Dict[str, Any]:
        """Create a new collection for prompts"""
        try:
            distance_map = {
                "Cosine": models.Distance.COSINE,
                "Euclidean": models.Distance.EUCLID,
                "Dot": models.Distance.DOT
            }
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, models.Distance.COSINE)
                )
            )
            
            return {"success": True, "collection": collection_name}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def index_prompt(
        self,
        collection_name: str,
        prompt_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Index a prompt with its embedding"""
        try:
            point = models.PointStruct(
                id=prompt_id,
                vector=embedding,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            return {"success": True, "point_id": prompt_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_similar_prompts(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar prompts"""
        try:
            # Build filter if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchAny(any=value)
                            )
                        )
                    else:
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value)
                            )
                        )
                
                if conditions:
                    query_filter = models.Filter(must=conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            similar_prompts = []
            for result in results:
                similar_prompts.append({
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload
                })
            
            return similar_prompts
            
        except Exception as e:
            return []
    
    async def get_fallback_prompts(
        self,
        collection_name: str,
        failed_prompt_embedding: List[float],
        context: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get fallback prompts when evaluation fails"""
        try:
            # Search for similar prompts with high success rates
            filters = {
                "success_rate": [0.8, 0.9, 1.0],  # High success rates only
                "use_case": context.get("use_case", "")
            }
            
            fallback_candidates = await self.search_similar_prompts(
                collection_name=collection_name,
                query_embedding=failed_prompt_embedding,
                limit=limit * 2,  # Get more candidates
                score_threshold=0.6,  # Lower threshold for fallbacks
                filters=filters
            )
            
            # Sort by success rate and similarity
            sorted_candidates = sorted(
                fallback_candidates,
                key=lambda x: (
                    x["metadata"].get("success_rate", 0),
                    x["score"]
                ),
                reverse=True
            )
            
            return sorted_candidates[:limit]
            
        except Exception as e:
            return []
    
    async def update_prompt_metrics(
        self,
        collection_name: str,
        prompt_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Update prompt performance metrics"""
        try:
            # Get existing point
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=[prompt_id],
                with_payload=True
            )
            
            if not points:
                return False
            
            # Update payload with new metrics
            existing_payload = points[0].payload
            existing_payload.update(metrics)
            
            # Upsert with updated payload
            point = models.PointStruct(
                id=prompt_id,
                vector=points[0].vector,
                payload=existing_payload
            )
            
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            return True
            
        except Exception as e:
            return False
    
    async def create_prompt_clusters(
        self,
        collection_name: str,
        cluster_count: int = 10
    ) -> Dict[str, Any]:
        """Create clusters of similar prompts"""
        try:
            # This would typically use Qdrant's clustering capabilities
            # For now, we'll simulate by grouping by tags/categories
            
            all_points = self.client.scroll(
                collection_name=collection_name,
                limit=1000,
                with_payload=True,
                with_vectors=True
            )[0]  # Get points from tuple
            
            # Group by tags/categories
            clusters = {}
            for point in all_points:
                tags = point.payload.get("tags", [])
                category = point.payload.get("category", "uncategorized")
                
                cluster_key = f"{category}_{','.join(sorted(tags[:2]))}"
                
                if cluster_key not in clusters:
                    clusters[cluster_key] = []
                
                clusters[cluster_key].append({
                    "id": point.id,
                    "metadata": point.payload
                })
            
            return {
                "success": True,
                "clusters": clusters,
                "cluster_count": len(clusters)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = self.client.get_collection(collection_name)
            
            return {
                "success": True,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.name,
                "status": info.status.name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_prompt(
        self,
        collection_name: str,
        prompt_id: str
    ) -> bool:
        """Delete a prompt from the collection"""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[prompt_id]
                )
            )
            return True
            
        except Exception as e:
            return False
    
    async def bulk_index_prompts(
        self,
        collection_name: str,
        prompts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk index multiple prompts"""
        try:
            points = []
            for prompt in prompts:
                point = models.PointStruct(
                    id=prompt.get("id", str(uuid.uuid4())),
                    vector=prompt["embedding"],
                    payload=prompt["metadata"]
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            return {
                "success": True,
                "indexed_count": len(points)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}