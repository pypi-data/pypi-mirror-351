"""AI-powered prompt generation for PBT"""

import json
import yaml
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class PromptGenerator:
    """Generates prompts using AI assistance"""
    
    def __init__(self):
        self.generation_templates = self._load_generation_templates()
    
    def _load_generation_templates(self) -> Dict[str, str]:
        """Load templates for prompt generation"""
        return {
            "basic": """You are a prompt engineering expert. Create a high-quality prompt template for the following goal:

Goal: {goal}
Style: {style}
Variables: {variables}

Requirements:
1. Create a clear, effective prompt template
2. Use Jinja2-style variables ({{ variable_name }})
3. Include appropriate instructions and context
4. Make it production-ready
5. Follow best practices for prompt engineering

Return a YAML structure with these fields:
- name: (kebab-case name)
- version: "1.0"
- model: "{model}"
- description: (brief description)
- template: (the actual prompt template)
- variables: (variable definitions with type and description)
- metadata: (tags, author, created date)

Example format:
```yaml
name: example-prompt
version: "1.0"
model: claude
description: "Brief description of what this prompt does"
template: |
  Your instructions here.
  
  Input: {{ input_variable }}
  
  Please provide a response that...
variables:
  input_variable:
    type: string
    description: "Description of what this variable contains"
    required: true
metadata:
  tags: ["category", "type"]
  author: "PBT"
  created: "{date}"
```

Generate the prompt now:""",
            
            "with_examples": """You are a prompt engineering expert. Create a high-quality prompt template with examples for the following goal:

Goal: {goal}
Style: {style}
Variables: {variables}

Requirements:
1. Create a clear, effective prompt template
2. Include 1-2 examples in the template
3. Use Jinja2-style variables ({{ variable_name }})
4. Make it production-ready and robust
5. Include error handling instructions

Return only valid YAML without any markdown formatting:""",
            
            "conversational": """Create a conversational AI prompt for:

Goal: {goal}
Style: {style}
Variables: {variables}

The prompt should:
1. Be natural and engaging
2. Handle follow-up questions
3. Maintain context and personality
4. Include appropriate tone and style
5. Be suitable for multi-turn conversations

Return YAML format:"""
        }
    
    def generate(
        self, 
        goal: str, 
        model: str = "claude", 
        style: str = "professional",
        variables: List[str] = None,
        template_type: str = "basic"
    ) -> Dict[str, Any]:
        """Generate a prompt based on the goal and requirements"""
        
        if variables is None:
            variables = []
        
        # Format variables for the generation prompt
        variables_str = ", ".join(variables) if variables else "auto-detect from goal"
        
        # Get the appropriate template
        generation_prompt = self.generation_templates.get(template_type, self.generation_templates["basic"])
        
        # Format the generation prompt
        formatted_prompt = generation_prompt.format(
            goal=goal,
            style=style,
            variables=variables_str,
            model=model,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # For now, create a simulated response since we don't have LLM integration here
        # In a real implementation, this would call the LLM API
        generated_content = self._simulate_ai_generation(goal, model, style, variables)
        
        try:
            # Try to parse as YAML
            if "```yaml" in generated_content:
                yaml_content = self._extract_yaml_from_markdown(generated_content)
            else:
                yaml_content = generated_content
            
            prompt_yaml = yaml.safe_load(yaml_content)
            
            # Validate the structure
            if self._validate_prompt_structure(prompt_yaml):
                return {
                    "success": True,
                    "prompt_yaml": prompt_yaml,
                    "raw_content": generated_content
                }
            else:
                return {
                    "success": False,
                    "error": "Generated prompt structure is invalid",
                    "raw_content": generated_content
                }
                
        except yaml.YAMLError as e:
            return {
                "success": False,
                "error": f"Failed to parse generated YAML: {e}",
                "raw_content": generated_content
            }
    
    def _simulate_ai_generation(self, goal: str, model: str, style: str, variables: List[str]) -> str:
        """Simulate AI generation for demo purposes"""
        
        # Create a name from the goal
        name = self._goal_to_name(goal)
        
        # Determine likely variables from goal if not provided
        if not variables:
            variables = self._extract_variables_from_goal(goal)
        
        # Create template based on goal
        template = self._create_template_from_goal(goal, variables, style)
        
        # Generate YAML structure
        prompt_yaml = {
            "name": name,
            "version": "1.0",
            "model": model,
            "description": f"AI-generated prompt for: {goal}",
            "template": template,
            "variables": {},
            "metadata": {
                "tags": self._extract_tags_from_goal(goal),
                "author": "PBT",
                "created": datetime.now().strftime("%Y-%m-%d")
            }
        }
        
        # Add variable definitions
        for var in variables:
            prompt_yaml["variables"][var] = {
                "type": "string",
                "description": f"Input {var.replace('_', ' ')} for the prompt",
                "required": True
            }
        
        return yaml.dump(prompt_yaml, default_flow_style=False, sort_keys=False)
    
    def _goal_to_name(self, goal: str) -> str:
        """Convert goal to a kebab-case name"""
        # Extract key words and convert to kebab case
        words = re.findall(r'\b\w+\b', goal.lower())
        # Take first 4-5 significant words
        significant_words = [w for w in words if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'that', 'this']]
        name_words = significant_words[:4]
        return "-".join(name_words)
    
    def _extract_variables_from_goal(self, goal: str) -> List[str]:
        """Extract likely variables from the goal description"""
        # Common patterns that suggest variables
        variables = []
        
        if "summarize" in goal.lower():
            variables.append("text")
        if "translate" in goal.lower():
            variables.extend(["text", "target_language"])
        if "analyze" in goal.lower():
            variables.append("content")
        if "email" in goal.lower():
            variables.extend(["recipient", "topic", "tone"])
        if "feedback" in goal.lower():
            variables.append("feedback_text")
        if "classify" in goal.lower() or "categorize" in goal.lower():
            variables.extend(["text", "categories"])
        if "question" in goal.lower() or "answer" in goal.lower():
            variables.extend(["question", "context"])
        if "review" in goal.lower():
            variables.append("content")
        if "generate" in goal.lower() or "create" in goal.lower():
            variables.extend(["topic", "style"])
        
        # Default fallback
        if not variables:
            variables = ["input"]
        
        return list(set(variables))  # Remove duplicates
    
    def _create_template_from_goal(self, goal: str, variables: List[str], style: str) -> str:
        """Create a template based on the goal and variables"""
        
        goal_lower = goal.lower()
        
        if "summarize" in goal_lower:
            return f"""Summarize the following text concisely:

Text: {{{{ text }}}}

Please provide a brief summary highlighting the key points."""
        
        elif "translate" in goal_lower:
            return f"""Translate the following text to {{{{ target_language }}}}:

Text: {{{{ text }}}}

Translation:"""
        
        elif "email" in goal_lower:
            return f"""Write a {style} email to {{{{ recipient }}}} about {{{{ topic }}}}.

The tone should be {{{{ tone }}}}.

Email:"""
        
        elif "analyze" in goal_lower and "feedback" in goal_lower:
            return f"""Analyze the following customer feedback and provide actionable insights:

Feedback: {{{{ feedback_text }}}}

Please provide:
1. Key themes (3-5 bullet points)
2. Sentiment analysis
3. Recommended actions"""
        
        elif "classify" in goal_lower:
            return f"""Classify the following text:

Text: {{{{ text }}}}

Classification:"""
        
        elif "question" in goal_lower or "answer" in goal_lower:
            return f"""Answer the following question based on the provided context:

Context: {{{{ context }}}}

Question: {{{{ question }}}}

Answer:"""
        
        else:
            # Generic template
            var_placeholders = "\n".join([f"{var.replace('_', ' ').title()}: {{{{ {var} }}}}" for var in variables])
            return f"""Complete the following task:

{var_placeholders}

Please provide a {style} response."""
    
    def _extract_tags_from_goal(self, goal: str) -> List[str]:
        """Extract relevant tags from the goal"""
        tags = []
        goal_lower = goal.lower()
        
        # Category tags
        if "email" in goal_lower:
            tags.append("email")
        if "summarize" in goal_lower or "summary" in goal_lower:
            tags.append("summarization")
        if "translate" in goal_lower:
            tags.append("translation")
        if "analyze" in goal_lower or "analysis" in goal_lower:
            tags.append("analysis")
        if "classify" in goal_lower or "classification" in goal_lower:
            tags.append("classification")
        if "feedback" in goal_lower:
            tags.append("feedback")
        if "customer" in goal_lower:
            tags.append("customer-service")
        if "question" in goal_lower or "answer" in goal_lower:
            tags.append("qa")
        if "review" in goal_lower:
            tags.append("review")
        
        # Default tags
        if not tags:
            tags = ["general", "ai-generated"]
        
        return tags
    
    def _extract_yaml_from_markdown(self, content: str) -> str:
        """Extract YAML content from markdown code blocks"""
        # Find YAML code block
        yaml_match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        if yaml_match:
            return yaml_match.group(1)
        
        # Find generic code block
        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        return content
    
    def _validate_prompt_structure(self, prompt: Dict[str, Any]) -> bool:
        """Validate that the prompt has required structure"""
        required_fields = ["name", "template"]
        return all(field in prompt for field in required_fields)
    
    def generate_jsonl_tests(self, prompt_content: str, num_tests: int = 5) -> Dict[str, Any]:
        """Generate JSONL test cases for a prompt"""
        
        try:
            prompt_yaml = yaml.safe_load(prompt_content)
            
            # Extract variables and goal from prompt
            variables = prompt_yaml.get("variables", {})
            template = prompt_yaml.get("template", "")
            name = prompt_yaml.get("name", "")
            
            # Generate test cases based on prompt content
            test_cases = self._generate_test_cases(template, variables, name, num_tests)
            
            return {
                "success": True,
                "test_cases": test_cases
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate test cases: {e}"
            }
    
    def _generate_test_cases(self, template: str, variables: Dict[str, Any], name: str, num_tests: int) -> List[Dict[str, Any]]:
        """Generate test cases based on prompt template and variables"""
        
        test_cases = []
        template_lower = template.lower()
        
        # Generate different types of test cases based on prompt type
        for i in range(num_tests):
            test_case = {
                "test_name": f"test_case_{i+1}",
                "inputs": {},
                "quality_criteria": "Should produce relevant and accurate output"
            }
            
            # Generate inputs based on variable types and template content
            for var_name, var_config in variables.items():
                test_case["inputs"][var_name] = self._generate_test_input(var_name, template_lower, i)
            
            # Add expected keywords/qualities based on prompt type
            if "summarize" in template_lower:
                test_case["expected_keywords"] = ["summary", "key points", "main"]
                test_case["quality_criteria"] = "Should create concise summary with main points"
            elif "translate" in template_lower:
                test_case["expected_keywords"] = ["translation"]
                test_case["quality_criteria"] = "Should provide accurate translation"
            elif "email" in template_lower:
                test_case["expected_keywords"] = ["email", "subject", "greeting"]
                test_case["quality_criteria"] = "Should be professional and well-structured"
            elif "analyze" in template_lower:
                test_case["expected_keywords"] = ["analysis", "insights"]
                test_case["quality_criteria"] = "Should provide detailed analysis with insights"
            
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_test_input(self, var_name: str, template_lower: str, test_index: int) -> str:
        """Generate test input for a specific variable"""
        
        # Sample data based on variable name and context
        if var_name == "text":
            samples = [
                "Machine learning is transforming industries across the globe.",
                "Climate change is one of the most pressing issues of our time.",
                "The benefits of renewable energy sources are becoming increasingly clear.",
                "Artificial intelligence will reshape how we work and live.",
                "Remote work has changed the traditional office environment."
            ]
            return samples[test_index % len(samples)]
        
        elif var_name == "feedback_text":
            samples = [
                "Great product, fast shipping and excellent customer service!",
                "The item arrived damaged and the packaging was poor.",
                "Good quality but took longer than expected to deliver.",
                "Amazing experience, will definitely order again!",
                "Product was okay but customer support could be improved."
            ]
            return samples[test_index % len(samples)]
        
        elif var_name == "recipient":
            samples = ["client", "team", "manager", "customer", "colleague"]
            return samples[test_index % len(samples)]
        
        elif var_name == "topic":
            samples = ["project update", "quarterly results", "meeting recap", "new product launch", "system maintenance"]
            return samples[test_index % len(samples)]
        
        elif var_name == "tone":
            samples = ["professional", "casual", "formal", "friendly", "urgent"]
            return samples[test_index % len(samples)]
        
        elif var_name == "target_language":
            samples = ["Spanish", "French", "German", "Italian", "Portuguese"]
            return samples[test_index % len(samples)]
        
        elif var_name == "question":
            samples = [
                "What are the benefits of renewable energy?",
                "How does machine learning work?",
                "What is the impact of climate change?",
                "Why is cybersecurity important?",
                "How can we improve productivity?"
            ]
            return samples[test_index % len(samples)]
        
        elif var_name == "context":
            samples = [
                "Based on recent research and industry reports",
                "According to the latest scientific studies", 
                "From the company's internal documentation",
                "Based on customer feedback and market analysis",
                "According to expert opinions and best practices"
            ]
            return samples[test_index % len(samples)]
        
        else:
            # Generic test data
            return f"Sample {var_name.replace('_', ' ')} data for testing"
    
    def save_jsonl_tests(self, test_cases: List[Dict[str, Any]], filename: str) -> bool:
        """Save test cases to JSONL file"""
        try:
            with open(filename, 'w') as f:
                for test_case in test_cases:
                    f.write(json.dumps(test_case) + '\n')
            return True
        except Exception:
            return False