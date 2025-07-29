"""Prompt optimization module for PBT - auto-shorten and refine prompts"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class OptimizationStrategy(Enum):
    """Optimization strategies for prompts"""
    SHORTEN = "shorten"
    CLARIFY = "clarify"
    COST_REDUCE = "cost_reduce"
    PERFORMANCE = "performance"
    EMBEDDING = "embedding"


@dataclass
class OptimizationResult:
    """Result of prompt optimization"""
    original_prompt: str
    optimized_prompt: str
    strategy: OptimizationStrategy
    metrics: Dict[str, Any]
    suggestions: List[str]
    cost_savings: Optional[float] = None


class PromptOptimizer:
    """Optimize prompts for various objectives"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.optimization_templates = self._load_optimization_templates()
    
    def _load_optimization_templates(self) -> Dict[OptimizationStrategy, str]:
        """Load templates for different optimization strategies"""
        return {
            OptimizationStrategy.SHORTEN: """
You are a prompt optimization expert. Your task is to shorten the following prompt while maintaining its effectiveness.

Original prompt:
{prompt}

Requirements:
1. Preserve all essential information and intent
2. Remove redundant words and phrases
3. Use concise language
4. Maintain clarity
5. Keep any important constraints or examples

Provide the optimized prompt and explain what was changed.

Respond with JSON:
{{
    "optimized_prompt": "shortened version",
    "changes": ["change 1", "change 2"],
    "token_reduction": percentage,
    "preserved_elements": ["element 1", "element 2"]
}}
""",
            
            OptimizationStrategy.CLARIFY: """
You are a prompt clarity expert. Improve the clarity of this prompt.

Original prompt:
{prompt}

Requirements:
1. Make instructions unambiguous
2. Add structure if needed
3. Clarify any vague terms
4. Ensure output format is clear
5. Add examples if helpful

Respond with JSON:
{{
    "optimized_prompt": "clarified version",
    "improvements": ["improvement 1", "improvement 2"],
    "clarity_score": 1-10,
    "added_elements": ["element 1", "element 2"]
}}
""",
            
            OptimizationStrategy.COST_REDUCE: """
You are a cost optimization expert for LLM prompts. Reduce token usage while maintaining quality.

Original prompt:
{prompt}

Token costs:
- Input tokens: $0.01 per 1K tokens
- Output tokens: $0.03 per 1K tokens

Requirements:
1. Minimize token count
2. Use efficient phrasing
3. Remove unnecessary examples
4. Compress verbose sections
5. Estimate cost savings

Respond with JSON:
{{
    "optimized_prompt": "cost-optimized version",
    "original_tokens": number,
    "optimized_tokens": number,
    "estimated_savings_percent": percentage,
    "optimization_techniques": ["technique 1", "technique 2"]
}}
""",

            OptimizationStrategy.EMBEDDING: """
You are a RAG optimization expert. Optimize this prompt for use in retrieval systems.

Original prompt:
{prompt}

Requirements:
1. Use semantically rich keywords
2. Avoid ambiguous pronouns
3. Include relevant context terms
4. Structure for chunking
5. Optimize for vector similarity

Respond with JSON:
{{
    "optimized_prompt": "RAG-optimized version",
    "key_terms": ["term1", "term2"],
    "semantic_improvements": ["improvement 1"],
    "chunk_boundaries": ["boundary 1"],
    "retrieval_score": 1-10
}}
"""
        }
    
    def optimize(
        self,
        prompt: str,
        strategy: OptimizationStrategy = OptimizationStrategy.SHORTEN,
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """Optimize a prompt using the specified strategy"""
        
        if self.llm_client:
            # Use LLM for optimization
            optimization_prompt = self.optimization_templates[strategy].format(
                prompt=prompt
            )
            
            response = self.llm_client.generate(optimization_prompt, model="gpt-4")
            
            try:
                result_data = json.loads(response)
                optimized_prompt = result_data.get('optimized_prompt', prompt)
                
                # Calculate metrics based on strategy
                metrics = self._calculate_metrics(prompt, optimized_prompt, strategy, result_data)
                suggestions = self._extract_suggestions(strategy, result_data)
                
            except json.JSONDecodeError:
                # Fallback to rule-based optimization
                optimized_prompt, metrics, suggestions = self._rule_based_optimization(
                    prompt, strategy, constraints
                )
        else:
            # Use rule-based optimization
            optimized_prompt, metrics, suggestions = self._rule_based_optimization(
                prompt, strategy, constraints
            )
        
        # Calculate cost savings if applicable
        cost_savings = None
        if strategy == OptimizationStrategy.COST_REDUCE:
            original_tokens = len(prompt.split()) * 1.3  # Rough token estimate
            optimized_tokens = len(optimized_prompt.split()) * 1.3
            cost_savings = (original_tokens - optimized_tokens) * 0.00001  # $0.01 per 1K tokens
        
        return OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized_prompt,
            strategy=strategy,
            metrics=metrics,
            suggestions=suggestions,
            cost_savings=cost_savings
        )
    
    def _rule_based_optimization(
        self,
        prompt: str,
        strategy: OptimizationStrategy,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any], List[str]]:
        """Apply rule-based optimizations"""
        
        optimized = prompt
        metrics = {}
        suggestions = []
        
        if strategy == OptimizationStrategy.SHORTEN:
            # Remove common redundancies
            redundant_phrases = [
                (r'\bplease\s+', ''),
                (r'\bkindly\s+', ''),
                (r'\bI would like you to\s+', ''),
                (r'\bCan you please\s+', ''),
                (r'\bMake sure to\s+', ''),
                (r'\s+in order to\s+', ' to '),
                (r'\s+due to the fact that\s+', ' because '),
                (r'\s+at this point in time\s+', ' now '),
                (r'\s+in the event that\s+', ' if '),
            ]
            
            for pattern, replacement in redundant_phrases:
                if re.search(pattern, optimized, re.IGNORECASE):
                    optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                    suggestions.append(f"Removed redundant phrase: {pattern.strip()}")
            
            # Remove duplicate spaces
            optimized = re.sub(r'\s+', ' ', optimized).strip()
            
            # Calculate reduction
            original_len = len(prompt.split())
            optimized_len = len(optimized.split())
            metrics['token_reduction'] = ((original_len - optimized_len) / original_len) * 100
            metrics['original_tokens'] = original_len
            metrics['optimized_tokens'] = optimized_len
            
        elif strategy == OptimizationStrategy.CLARIFY:
            # Add structure markers
            if '\n' not in optimized and len(optimized) > 200:
                # Add line breaks for long prompts
                sentences = re.split(r'(?<=[.!?])\s+', optimized)
                if len(sentences) > 3:
                    optimized = '\n'.join(sentences)
                    suggestions.append("Added line breaks for clarity")
            
            # Ensure output format is specified
            if 'output' not in optimized.lower() and 'format' not in optimized.lower():
                optimized += "\n\nProvide your response in a clear, structured format."
                suggestions.append("Added output format instruction")
            
            metrics['clarity_improvements'] = len(suggestions)
            
        elif strategy == OptimizationStrategy.COST_REDUCE:
            # Remove examples if present
            example_pattern = r'(?:Example|e\.g\.|For instance)[^.]*\.'
            example_matches = re.findall(example_pattern, optimized, re.IGNORECASE)
            if example_matches:
                optimized = re.sub(example_pattern, '', optimized, flags=re.IGNORECASE)
                suggestions.append(f"Removed {len(example_matches)} examples to reduce tokens")
            
            # Compress lists
            list_pattern = r'(?:First|Second|Third|1\.|2\.|3\.)[^.]*\.'
            if re.search(list_pattern, optimized):
                optimized = re.sub(r'\s*(?:First|1\.)\s*', ' • ', optimized)
                optimized = re.sub(r'\s*(?:Second|2\.)\s*', ' • ', optimized)
                optimized = re.sub(r'\s*(?:Third|3\.)\s*', ' • ', optimized)
                suggestions.append("Compressed list formatting")
            
            metrics['compression_ratio'] = len(optimized) / len(prompt)
            
        elif strategy == OptimizationStrategy.EMBEDDING:
            # Add semantic keywords
            keywords = self._extract_keywords(prompt)
            if keywords and not all(kw in optimized for kw in keywords[:3]):
                optimized = f"Keywords: {', '.join(keywords[:5])}\n\n{optimized}"
                suggestions.append("Added semantic keywords for better retrieval")
            
            # Replace pronouns with specific terms
            pronoun_replacements = []
            if 'it' in optimized.lower():
                suggestions.append("Consider replacing 'it' with specific terms")
            if 'this' in optimized.lower():
                suggestions.append("Consider replacing 'this' with specific references")
            
            metrics['semantic_density'] = len(keywords)
        
        return optimized, metrics, suggestions
    
    def _calculate_metrics(
        self,
        original: str,
        optimized: str,
        strategy: OptimizationStrategy,
        result_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimization metrics"""
        metrics = {
            'original_length': len(original),
            'optimized_length': len(optimized),
            'compression_ratio': len(optimized) / len(original) if len(original) > 0 else 1.0
        }
        
        # Add strategy-specific metrics from LLM response
        if strategy == OptimizationStrategy.SHORTEN:
            metrics['token_reduction'] = result_data.get('token_reduction', 0)
        elif strategy == OptimizationStrategy.CLARIFY:
            metrics['clarity_score'] = result_data.get('clarity_score', 0)
        elif strategy == OptimizationStrategy.COST_REDUCE:
            metrics['estimated_savings'] = result_data.get('estimated_savings_percent', 0)
        elif strategy == OptimizationStrategy.EMBEDDING:
            metrics['retrieval_score'] = result_data.get('retrieval_score', 0)
        
        return metrics
    
    def _extract_suggestions(
        self,
        strategy: OptimizationStrategy,
        result_data: Dict[str, Any]
    ) -> List[str]:
        """Extract suggestions from optimization result"""
        suggestions = []
        
        if strategy == OptimizationStrategy.SHORTEN:
            suggestions = result_data.get('changes', [])
        elif strategy == OptimizationStrategy.CLARIFY:
            suggestions = result_data.get('improvements', [])
        elif strategy == OptimizationStrategy.COST_REDUCE:
            suggestions = result_data.get('optimization_techniques', [])
        elif strategy == OptimizationStrategy.EMBEDDING:
            suggestions = result_data.get('semantic_improvements', [])
        
        return suggestions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for semantic optimization"""
        # Simple keyword extraction - in production, use NLP library
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    def bulk_optimize(
        self,
        prompts: List[Dict[str, str]],
        strategy: OptimizationStrategy = OptimizationStrategy.SHORTEN
    ) -> List[OptimizationResult]:
        """Optimize multiple prompts in bulk"""
        results = []
        
        for prompt_data in prompts:
            prompt_text = prompt_data.get('template', prompt_data.get('prompt', ''))
            if prompt_text:
                result = self.optimize(prompt_text, strategy)
                results.append(result)
        
        return results
    
    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt and suggest all applicable optimizations"""
        suggestions = {
            'applicable_strategies': [],
            'priority_optimizations': [],
            'metrics': {}
        }
        
        # Check length
        word_count = len(prompt.split())
        if word_count > 100:
            suggestions['applicable_strategies'].append(OptimizationStrategy.SHORTEN)
            suggestions['priority_optimizations'].append("Consider shortening - prompt is verbose")
        
        # Check clarity
        if not any(marker in prompt.lower() for marker in ['step', 'first', '1.', 'format']):
            suggestions['applicable_strategies'].append(OptimizationStrategy.CLARIFY)
            suggestions['priority_optimizations'].append("Add structure for better clarity")
        
        # Check cost
        if word_count > 200:
            suggestions['applicable_strategies'].append(OptimizationStrategy.COST_REDUCE)
            estimated_cost = word_count * 0.00001  # Rough estimate
            suggestions['priority_optimizations'].append(f"High token count - estimated cost ${estimated_cost:.4f} per call")
        
        # Check for RAG optimization
        if any(term in prompt.lower() for term in ['search', 'find', 'retrieve', 'lookup']):
            suggestions['applicable_strategies'].append(OptimizationStrategy.EMBEDDING)
            suggestions['priority_optimizations'].append("Consider RAG optimization for retrieval tasks")
        
        suggestions['metrics'] = {
            'word_count': word_count,
            'estimated_tokens': int(word_count * 1.3),
            'has_structure': bool(re.search(r'\n|[0-9]\.|bullet|step', prompt, re.IGNORECASE)),
            'has_examples': bool(re.search(r'example|e\.g\.|for instance', prompt, re.IGNORECASE))
        }
        
        return suggestions