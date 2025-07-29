"""Prompt rendering and model comparison for PBT"""

import json
import yaml
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RenderResult:
    """Result of prompt rendering"""
    prompt_file: str
    model: str
    rendered_prompt: str
    variables: Dict[str, Any]
    template_stats: Dict[str, Any]
    estimated_cost: float
    timestamp: str


@dataclass
class ModelComparisonResult:
    """Result of comparing multiple models"""
    prompt_file: str
    models: List[str]
    variables: Dict[str, Any]
    results: Dict[str, Dict[str, Any]]  # model -> result data
    recommendations: Dict[str, str]
    timestamp: str


class PromptRenderer:
    """Renders prompts and compares across models"""
    
    def __init__(self):
        self.cost_per_token = {
            "claude": 0.000008,
            "claude-3": 0.000008,
            "gpt-4": 0.00003,
            "gpt-4-turbo": 0.00001,
            "gpt-3.5-turbo": 0.000002,
            "mistral": 0.000007
        }
    
    def render_prompt(
        self, 
        prompt_file: Path, 
        variables: Dict[str, Any], 
        model: str = None
    ) -> RenderResult:
        """Render a single prompt with variables"""
        
        # Load prompt file
        with open(prompt_file) as f:
            prompt_data = yaml.safe_load(f)
        
        # Use model from prompt file if not specified
        if model is None:
            model = prompt_data.get("model", "claude")
        
        # Render template
        template = prompt_data.get("template", "")
        rendered_prompt = self._render_template(template, variables)
        
        # Calculate stats
        template_stats = self._calculate_template_stats(template, rendered_prompt, variables)
        
        # Estimate cost
        estimated_cost = self._estimate_cost(rendered_prompt, model)
        
        return RenderResult(
            prompt_file=str(prompt_file),
            model=model,
            rendered_prompt=rendered_prompt,
            variables=variables,
            template_stats=template_stats,
            estimated_cost=estimated_cost,
            timestamp=datetime.now().isoformat()
        )
    
    def compare_models(
        self,
        prompt_file: Path,
        variables: Dict[str, Any],
        models: List[str]
    ) -> ModelComparisonResult:
        """Compare prompt rendering across multiple models"""
        
        # Load prompt file
        with open(prompt_file) as f:
            prompt_data = yaml.safe_load(f)
        
        template = prompt_data.get("template", "")
        rendered_prompt = self._render_template(template, variables)
        
        results = {}
        
        for model in models:
            # Execute with each model (mock for now)
            start_time = time.time()
            output = self._execute_with_model(rendered_prompt, model)
            response_time = time.time() - start_time
            
            # Calculate stats
            token_count = self._estimate_tokens(output)
            cost = self._estimate_cost(rendered_prompt + output, model)
            quality_score = self._estimate_quality_score(output, model)
            
            results[model] = {
                "output": output,
                "stats": {
                    "tokens": token_count,
                    "cost": cost,
                    "response_time": response_time,
                    "quality_score": quality_score
                }
            }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results)
        
        return ModelComparisonResult(
            prompt_file=str(prompt_file),
            models=models,
            variables=variables,
            results=results,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables using Jinja2-style syntax"""
        
        rendered = template
        
        # Replace variables in {{ variable }} format
        for key, value in variables.items():
            placeholder = f"{{{{ {key} }}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _calculate_template_stats(
        self, 
        template: str, 
        rendered: str, 
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate template statistics"""
        
        original_tokens = self._estimate_tokens(template)
        final_tokens = self._estimate_tokens(rendered)
        substitutions = len([k for k in variables.keys() if f"{{{{ {k} }}}}" in template])
        
        return {
            "original_tokens": original_tokens,
            "final_tokens": final_tokens,
            "variable_substitutions": substitutions,
            "expansion_ratio": final_tokens / original_tokens if original_tokens > 0 else 1.0
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def _estimate_cost(self, text: str, model: str) -> float:
        """Estimate cost for model execution"""
        tokens = self._estimate_tokens(text)
        cost_per_token = self.cost_per_token.get(model, 0.00001)
        return tokens * cost_per_token
    
    def _execute_with_model(self, prompt: str, model: str) -> str:
        """Execute prompt with specified model (mock implementation)"""
        
        prompt_lower = prompt.lower()
        
        # Model-specific response patterns
        if model.startswith("claude"):
            return self._claude_style_response(prompt_lower)
        elif model.startswith("gpt-4"):
            return self._gpt4_style_response(prompt_lower)
        elif model.startswith("gpt-3.5"):
            return self._gpt35_style_response(prompt_lower)
        elif model.startswith("mistral"):
            return self._mistral_style_response(prompt_lower)
        else:
            return self._generic_response(prompt_lower)
    
    def _claude_style_response(self, prompt: str) -> str:
        """Claude-style response (typically more detailed and structured)"""
        if "summarize" in prompt:
            return """The text discusses machine learning's transformative impact across industries. Key points include:

• Automation capabilities revolutionizing business processes
• Data-driven decision making enabling better outcomes  
• Enhanced efficiency through intelligent systems
• Widespread adoption across healthcare, finance, and manufacturing sectors

This technological advancement represents a significant shift toward more intelligent, adaptive business operations."""
        
        elif "translate" in prompt:
            return "Machine learning está transformando las industrias a través de la automatización, análisis de datos y toma de decisiones inteligente."
        
        elif "email" in prompt:
            return """Subject: Professional Update

Dear John,

I hope this message finds you well. I wanted to provide you with a comprehensive update on our current project status.

Our team has made significant progress across several key areas:

• Development milestones have been achieved ahead of schedule
• Quality assurance processes are performing exceptionally well
• Stakeholder feedback has been overwhelmingly positive

I'm confident we're well-positioned for a successful delivery. Please let me know if you'd like to discuss any specific aspects in greater detail.

Best regards,
[Your name]"""
        
        else:
            return "I understand your request and will provide a thoughtful, comprehensive response that addresses the key aspects of your query while maintaining clarity and precision."
    
    def _gpt4_style_response(self, prompt: str) -> str:
        """GPT-4 style response (typically comprehensive and analytical)"""
        if "summarize" in prompt:
            return """Machine learning technology is revolutionizing various industries by enabling automated decision-making, predictive analytics, and intelligent process optimization. Key sectors experiencing transformation include healthcare (diagnostic accuracy), finance (fraud detection and algorithmic trading), retail (personalized recommendations), and manufacturing (predictive maintenance and quality control). This technological evolution represents a fundamental shift toward data-driven operations and enhanced efficiency across business functions."""
        
        elif "translate" in prompt:
            return "El aprendizaje automático está transformando las industrias mediante la automatización de procesos, análisis predictivo y optimización inteligente de operaciones empresariales."
        
        elif "email" in prompt:
            return """Subject: Project Status Update

Dear John,

I trust this email finds you in good health and spirits. I am writing to provide you with a detailed update regarding the current status of our ongoing project initiatives.

Key Progress Highlights:
- Development Phase: Completed 85% of core functionality
- Testing & Quality Assurance: Rigorous testing protocols implemented
- Timeline: Currently ahead of schedule by approximately 1 week
- Budget: Operating within approved financial parameters

Next Steps:
1. Finalize remaining development components
2. Conduct comprehensive user acceptance testing
3. Prepare deployment documentation

I welcome the opportunity to discuss these developments further at your convenience.

Warm regards,
[Your Name]"""
        
        else:
            return "I appreciate your inquiry and am prepared to provide a detailed, analytically-driven response that comprehensively addresses your requirements while incorporating relevant context and actionable insights."
    
    def _gpt35_style_response(self, prompt: str) -> str:
        """GPT-3.5 style response (typically concise and direct)"""
        if "summarize" in prompt:
            return "Machine learning is changing how industries work by automating tasks, analyzing data, and improving decision-making. Many sectors like healthcare, finance, and manufacturing are benefiting from increased efficiency and new capabilities."
        
        elif "translate" in prompt:
            return "El aprendizaje automático está transformando las industrias al automatizar tareas y proporcionar información basada en datos."
        
        elif "email" in prompt:
            return """Subject: Project Update

Hi John,

Hope you're doing well! I wanted to give you a quick update on our project.

We're making good progress and are currently on track with our timeline. The team has completed the main development work and we're now in the testing phase.

Key updates:
• Development: 90% complete
• Testing: In progress
• Timeline: On schedule

Let me know if you have any questions!

Best,
[Your name]"""
        
        else:
            return "Thanks for your question! I'm happy to help and will provide a clear, helpful response to address what you're looking for."
    
    def _mistral_style_response(self, prompt: str) -> str:
        """Mistral style response (balanced between detail and conciseness)"""
        if "summarize" in prompt:
            return "Machine learning is transforming industries through automation and intelligent data analysis. Key benefits include improved efficiency, better decision-making, and enhanced operational capabilities across sectors like healthcare, finance, and manufacturing."
        
        elif "translate" in prompt:
            return "L'apprentissage automatique transforme les industries grâce à l'automatisation et à l'analyse intelligente des données."
        
        elif "email" in prompt:
            return """Subject: Project Update

Dear John,

I hope this email finds you well. I'd like to share an update on our current project progress.

Current Status:
• Development work is progressing smoothly
• We're meeting our planned milestones
• Quality checks are showing positive results

The team remains focused on delivering quality results within our timeline. Please feel free to reach out if you need additional details.

Best regards,
[Your name]"""
        
        else:
            return "I understand your request and will provide a balanced, informative response that addresses your needs effectively."
    
    def _generic_response(self, prompt: str) -> str:
        """Generic response for unknown models"""
        return "This is a response generated for your prompt. The output would vary based on the specific model and configuration used."
    
    def _estimate_quality_score(self, output: str, model: str) -> float:
        """Estimate quality score based on output characteristics"""
        
        base_scores = {
            "claude": 9.1,
            "claude-3": 9.3,
            "gpt-4": 9.3,
            "gpt-4-turbo": 9.2,
            "gpt-3.5-turbo": 8.7,
            "mistral": 8.9
        }
        
        base_score = base_scores.get(model, 8.5)
        
        # Adjust based on output characteristics
        if len(output) < 20:
            base_score -= 1.0
        elif len(output) > 500:
            base_score += 0.2
        
        # Add some randomness to simulate real evaluation
        import random
        adjustment = random.uniform(-0.2, 0.2)
        
        return min(max(base_score + adjustment, 1.0), 10.0)
    
    def _generate_recommendations(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Generate recommendations based on comparison results"""
        
        # Find best in each category
        best_quality = max(results.items(), key=lambda x: x[1]["stats"]["quality_score"])
        best_cost = min(results.items(), key=lambda x: x[1]["stats"]["cost"])
        best_speed = min(results.items(), key=lambda x: x[1]["stats"]["response_time"])
        
        return {
            "best_quality": f"{best_quality[0]} ({best_quality[1]['stats']['quality_score']:.1f}/10)",
            "best_value": f"{best_cost[0]} (${best_cost[1]['stats']['cost']:.5f})",
            "fastest": f"{best_speed[0]} ({best_speed[1]['stats']['response_time']:.1f}s)",
            "recommendation": self._get_overall_recommendation(results)
        }
    
    def _get_overall_recommendation(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Get overall recommendation based on balanced criteria"""
        
        # Score each model on combined criteria
        model_scores = {}
        
        for model, result in results.items():
            stats = result["stats"]
            
            # Normalize scores (0-1 scale)
            quality_norm = stats["quality_score"] / 10.0
            cost_norm = 1.0 - min(stats["cost"] / 0.01, 1.0)  # Lower cost is better
            speed_norm = 1.0 - min(stats["response_time"] / 5.0, 1.0)  # Faster is better
            
            # Weighted combination (quality 50%, cost 30%, speed 20%)
            combined_score = (quality_norm * 0.5) + (cost_norm * 0.3) + (speed_norm * 0.2)
            model_scores[model] = combined_score
        
        best_overall = max(model_scores.items(), key=lambda x: x[1])
        
        return f"Use {best_overall[0]} for best overall balance of quality, cost, and speed."
    
    def export_to_json(self, result: RenderResult) -> Dict[str, Any]:
        """Export render result to JSON format"""
        return {
            "prompt_file": result.prompt_file,
            "model": result.model,
            "rendered_prompt": result.rendered_prompt,
            "variables": result.variables,
            "template_stats": result.template_stats,
            "estimated_cost": result.estimated_cost,
            "timestamp": result.timestamp
        }
    
    def export_comparison_to_json(self, result: ModelComparisonResult) -> Dict[str, Any]:
        """Export comparison result to JSON format"""
        return {
            "prompt_file": result.prompt_file,
            "models": result.models,
            "variables": result.variables,
            "results": result.results,
            "recommendations": result.recommendations,
            "timestamp": result.timestamp
        }