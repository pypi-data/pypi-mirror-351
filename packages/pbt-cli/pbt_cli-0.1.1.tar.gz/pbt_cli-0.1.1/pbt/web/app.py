"""
PBT Web UI - FastAPI application for prompt comparison
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Import PBT core components
from pbt.core.prompt_renderer import PromptRenderer
from pbt.core.prompt_evaluator import PromptEvaluator
from pbt.integrations.llm import get_llm_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PBT Web UI",
    description="Visual interface for Prompt Build Tool - Compare LLMs side by side",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class PromptRequest(BaseModel):
    prompt: str
    models: List[str]
    variables: Optional[Dict[str, Any]] = {}
    expected_output: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000

class ModelResponse(BaseModel):
    model: str
    output: str
    tokens: int
    cost: float
    response_time: float
    score: Optional[float] = None
    evaluation: Optional[Dict[str, float]] = None

class ComparisonResponse(BaseModel):
    request_id: str
    timestamp: str
    prompt: str
    variables: Dict[str, Any]
    models: List[ModelResponse]
    recommendations: Dict[str, str]
    has_expected_output: bool

class SavedPrompt(BaseModel):
    name: str
    description: str
    prompt: str
    variables: Dict[str, Any]
    models: List[str]
    expected_output: Optional[str]

# In-memory storage (replace with database in production)
saved_prompts: Dict[str, SavedPrompt] = {}
comparison_history: List[ComparisonResponse] = []

@app.get("/")
async def root():
    """Serve the main UI"""
    return HTMLResponse(content=open("pbt/web/static/index.html").read())

@app.get("/api/models")
async def get_available_models():
    """Get list of available LLM models"""
    return {
        "models": [
            {"id": "claude", "name": "Claude", "provider": "Anthropic"},
            {"id": "claude-3", "name": "Claude 3", "provider": "Anthropic"},
            {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI"},
            {"id": "mistral", "name": "Mistral", "provider": "Mistral AI"},
            {"id": "ollama", "name": "Ollama (Local)", "provider": "Local"}
        ]
    }

@app.post("/api/compare")
async def compare_models(request: PromptRequest):
    """Compare prompt across multiple models"""
    logger.info(f"Comparing prompt across models: {request.models}")
    logger.info(f"Expected output provided: {bool(request.expected_output)}")
    if request.expected_output:
        logger.info(f"Expected output preview: {request.expected_output[:100]}...")
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    results = []
    
    # Process each model in parallel
    tasks = []
    for model in request.models:
        tasks.append(process_model(model, request))
    
    model_responses = await asyncio.gather(*tasks)
    
    # Calculate scores if expected output provided
    if request.expected_output:
        logger.info(f"Calculating scores with expected output: {request.expected_output[:100]}...")
        for response in model_responses:
            logger.info(f"Evaluating model {response.model} output: {response.output[:100]}...")
            score, evaluation = await evaluate_output(
                response.output, 
                request.expected_output
            )
            response.score = score
            response.evaluation = evaluation
            logger.info(f"Model {response.model} scored: {score:.2f}/10")
            logger.info(f"Evaluation details: {evaluation}")
    else:
        logger.info("No expected output provided, skipping score calculation")
    
    # Generate recommendations
    recommendations = generate_recommendations(model_responses)
    
    # Create comparison response
    comparison = ComparisonResponse(
        request_id=request_id,
        timestamp=datetime.now().isoformat(),
        prompt=request.prompt,
        variables=request.variables,
        models=model_responses,
        recommendations=recommendations,
        has_expected_output=bool(request.expected_output)
    )
    
    # Log the final response
    logger.info(f"Comparison response - has_expected_output: {comparison.has_expected_output}")
    for model in comparison.models:
        logger.info(f"Model {model.model} - score: {model.score}, has evaluation: {bool(model.evaluation)}")
    
    # Save to history
    comparison_history.append(comparison)
    if len(comparison_history) > 100:  # Keep last 100
        comparison_history.pop(0)
    
    return comparison

async def process_model(model: str, request: PromptRequest) -> ModelResponse:
    """Process prompt with a single model"""
    try:
        # Get LLM provider
        provider = await get_llm_provider(model)
        
        # Render prompt with variables
        rendered_prompt = render_prompt_with_variables(request.prompt, request.variables)
        
        # Execute with model
        start_time = datetime.now()
        response = await provider.complete(
            prompt=rendered_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ModelResponse(
            model=model,
            output=response.content,
            tokens=response.usage.get("total_tokens", 0),
            cost=response.cost,
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Error processing model {model}: {e}")
        return ModelResponse(
            model=model,
            output=f"Error: {str(e)}",
            tokens=0,
            cost=0,
            response_time=0
        )

def render_prompt_with_variables(prompt: str, variables: Dict[str, Any]) -> str:
    """Simple variable substitution"""
    rendered = prompt
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        rendered = rendered.replace(f"{{{key}}}", str(value))
    return rendered

async def evaluate_output(output: str, expected: str) -> tuple[float, Dict[str, float]]:
    """Evaluate output against expected result"""
    # Handle edge cases
    if not output or not expected:
        return 0.0, {"contains_expected": 0.0}
    
    # Simplified evaluation focused on context match
    output_lower = output.lower()
    expected_lower = expected.lower()
    
    # Check if output contains the expected text
    contains_expected = 1.0 if expected_lower in output_lower else 0.0
    
    # If not exact substring, check word overlap
    if contains_expected == 0.0:
        word_overlap = calculate_word_overlap(output, expected)
        # Give partial credit for word overlap
        contains_expected = min(word_overlap * 1.5, 1.0)  # Boost word overlap score
    
    # Calculate overall score (weighted)
    exact_match = 1.0 if output.strip() == expected.strip() else 0.0
    length_ratio = min(len(output) / max(len(expected), 1), len(expected) / max(len(output), 1))
    
    # Weighted score: context match is most important
    score = (contains_expected * 0.5 + exact_match * 0.3 + length_ratio * 0.2) * 10
    
    evaluation = {
        "contains_expected": contains_expected
    }
    
    logger.info(f"Score: {score:.1f}, Context match: {contains_expected:.1%}")
    
    return score, evaluation

def calculate_word_overlap(text1: str, text2: str) -> float:
    """Calculate word overlap between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    overlap = len(words1.intersection(words2))
    total = len(words1.union(words2))
    
    return overlap / total if total > 0 else 0.0

def generate_recommendations(responses: List[ModelResponse]) -> Dict[str, str]:
    """Generate recommendations based on comparison results"""
    if not responses:
        return {}
    
    # Sort by different criteria
    by_quality = sorted(responses, key=lambda x: x.score or 0, reverse=True)
    by_speed = sorted(responses, key=lambda x: x.response_time)
    by_cost = sorted(responses, key=lambda x: x.cost)
    
    # Calculate balanced score
    for r in responses:
        quality_score = (r.score or 5) / 10
        speed_score = 1 - (r.response_time / max(x.response_time for x in responses))
        cost_score = 1 - (r.cost / max(x.cost for x in responses if x.cost > 0))
        r.balanced_score = (quality_score * 0.5 + speed_score * 0.3 + cost_score * 0.2)
    
    by_balanced = sorted(responses, key=lambda x: x.balanced_score, reverse=True)
    
    return {
        "best_quality": by_quality[0].model if by_quality[0].score else "N/A",
        "best_speed": by_speed[0].model,
        "best_cost": by_cost[0].model,
        "balanced": by_balanced[0].model
    }

@app.post("/api/prompts/save")
async def save_prompt(prompt: SavedPrompt):
    """Save a prompt for later use"""
    try:
        if not prompt.name:
            raise HTTPException(status_code=400, detail="Prompt name is required")
        
        prompt_id = prompt.name.lower().replace(" ", "_")
        saved_prompts[prompt_id] = prompt
        logger.info(f"Saved prompt: {prompt_id}")
        return {"message": "Prompt saved successfully", "id": prompt_id}
    except Exception as e:
        logger.error(f"Error saving prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")

@app.get("/api/prompts")
async def get_saved_prompts():
    """Get all saved prompts"""
    return {"prompts": list(saved_prompts.values())}

@app.get("/api/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get a specific saved prompt"""
    if prompt_id not in saved_prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return saved_prompts[prompt_id]

@app.get("/api/history")
async def get_comparison_history(limit: int = 10):
    """Get recent comparison history"""
    return {"history": comparison_history[-limit:]}

@app.post("/api/logs")
async def receive_log(log_entry: dict):
    """Receive and process frontend logs"""
    try:
        logger.info(f"Frontend Log [{log_entry.get('type', 'info').upper()}]: {log_entry.get('message', 'No message')}")
        
        # Store critical logs for debugging
        if log_entry.get('type') == 'error':
            # You could store in database, send to monitoring service, etc.
            pass
            
        return {"status": "success", "message": "Log received"}
    except Exception as e:
        logger.error(f"Error processing frontend log: {e}")
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time streaming responses"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            # Create proper request object
            request = PromptRequest(**data)
            logger.info(f"WebSocket request - Expected output: {bool(request.expected_output)}")
            
            # Collect all responses first
            model_responses = []
            
            # Stream responses as they complete
            for model in data["models"]:
                # Simulate streaming (replace with actual streaming)
                await websocket.send_json({
                    "type": "model_start",
                    "model": model
                })
                
                # Process model
                response = await process_model(model, request)
                model_responses.append(response)
                
                await websocket.send_json({
                    "type": "model_complete",
                    "model": model,
                    "response": response.model_dump()
                })
            
            # Calculate scores if expected output provided
            if request.expected_output:
                logger.info("Calculating scores for WebSocket responses...")
                for response in model_responses:
                    score, evaluation = await evaluate_output(
                        response.output, 
                        request.expected_output
                    )
                    response.score = score
                    response.evaluation = evaluation
                    logger.info(f"WebSocket - Model {response.model} scored: {score:.2f}/10")
                    
                    # Send score update
                    await websocket.send_json({
                        "type": "score_update",
                        "model": response.model,
                        "score": score,
                        "evaluation": evaluation
                    })
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse("pbt/web/static/index.html")

@app.get("/table")
async def table_view():
    """Serve the table layout version"""
    return FileResponse("pbt/web/static/table.html")

# Mount static files
app.mount("/static", StaticFiles(directory="pbt/web/static"), name="static")

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    Path("pbt/web/static").mkdir(parents=True, exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "pbt.web.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )