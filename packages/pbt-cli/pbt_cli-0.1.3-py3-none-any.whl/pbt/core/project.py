"""PBT Project management and initialization"""

import os
import yaml
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter for structured logging
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
log_dir = Path('./logs')
log_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_dir / 'pbt_core.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PBTProject:
    """Manages PBT project structure and configuration"""
    
    def __init__(self, project_dir: Path, config: Dict[str, Any]):
        self.project_dir = Path(project_dir)
        self.config = config
        
    @classmethod
    def init(cls, project_dir: Path, project_name: str, template: str = "default") -> "PBTProject":
        """Initialize a new PBT project"""
        logger.info(f"Initializing PBT project: {project_name} at {project_dir} with template: {template}")
        
        project_dir = Path(project_dir)
        try:
            project_dir.mkdir(exist_ok=True)
            logger.debug(f"Created project directory: {project_dir}")
        except Exception as e:
            logger.error(f"Failed to create project directory {project_dir}: {e}")
            raise
        
        # Create directory structure
        directories = [
            "prompts",
            "tests", 
            "evaluations",
            "chains",
            "chunks"
        ]
        
        logger.debug(f"Creating directory structure: {directories}")
        for dir_name in directories:
            try:
                dir_path = project_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to create directory {dir_name}: {e}")
                raise
        
        # Create pbt.yaml configuration
        config = {
            "name": project_name,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "prompts_dir": "prompts",
            "tests_dir": "tests",
            "evaluations_dir": "evaluations",
            "models": {
                "default": "claude",
                "available": [
                    "claude",
                    "claude-3", 
                    "gpt-4",
                    "gpt-3.5-turbo",
                    "mistral"
                ]
            },
            "settings": {
                "test_timeout": 30,
                "max_retries": 3,
                "save_reports": True,
                "optimization": {
                    "max_token_reduction": 0.7,
                    "preserve_examples": True
                }
            }
        }
        
        # Save configuration
        config_path = project_dir / "pbt.yaml"
        try:
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Created configuration file: {config_path}")
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            raise
        
        # Create .env.example
        env_example = """# PBT Environment Variables
# Copy this file to .env and add your API keys

# Required for Claude support
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Required for OpenAI models
OPENAI_API_KEY=sk-your-key-here

# Optional: Mistral AI
MISTRAL_API_KEY=your-key-here

# Optional: Default settings
PBT_DEFAULT_MODEL=claude
PBT_TEST_TIMEOUT=30

# Optional: Cloud deployment
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
"""
        
        env_path = project_dir / ".env.example"
        try:
            with open(env_path, "w") as f:
                f.write(env_example)
            logger.debug(f"Created environment example file: {env_path}")
        except Exception as e:
            logger.error(f"Failed to create .env.example: {e}")
            raise
        
        # Create example prompt if using default template
        if template == "default":
            try:
                cls._create_example_prompt(project_dir)
                logger.info("Created example prompt files")
            except Exception as e:
                logger.error(f"Failed to create example prompt: {e}")
                raise
        
        logger.info(f"Successfully initialized PBT project: {project_name}")
        return cls(project_dir, config)
    
    @staticmethod
    def _create_example_prompt(project_dir: Path):
        """Create an example prompt for new projects"""
        logger.debug("Creating example prompt and test files")
        example_prompt = {
            "name": "Example-Text-Summarizer",
            "version": "1.0",
            "model": "claude",
            "description": "Example prompt that summarizes text content",
            "template": """Summarize the following text concisely:

Text: {{ text }}

Please provide a brief summary highlighting the key points.""",
            "variables": {
                "text": {
                    "type": "string",
                    "description": "Text content to summarize",
                    "required": True
                }
            },
            "metadata": {
                "tags": ["example", "summarization"],
                "author": "PBT",
                "created": datetime.now().isoformat()[:10]
            }
        }
        
        prompts_dir = project_dir / "prompts"
        prompt_file = prompts_dir / "example_summarizer.prompt.yaml"
        try:
            with open(prompt_file, "w") as f:
                yaml.dump(example_prompt, f, default_flow_style=False, sort_keys=False)
            logger.debug(f"Created example prompt: {prompt_file}")
        except Exception as e:
            logger.error(f"Failed to create example prompt file: {e}")
            raise
        
        # Create example test
        example_test = {
            "prompt_file": "prompts/example_summarizer.prompt.yaml",
            "test_cases": [
                {
                    "name": "short_text",
                    "inputs": {
                        "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
                    },
                    "expected_keywords": ["machine learning", "AI", "algorithms", "data"],
                    "quality_criteria": "Should mention key concepts: ML, AI, algorithms, learning from data"
                },
                {
                    "name": "longer_text", 
                    "inputs": {
                        "text": "Climate change refers to long-term shifts in global temperatures and weather patterns. While these shifts may be natural, human activities have been the main driver since the 1800s, primarily through burning fossil fuels."
                    },
                    "expected_keywords": ["climate change", "temperature", "human activities", "fossil fuels"],
                    "quality_criteria": "Should summarize main points about climate change causes"
                }
            ]
        }
        
        tests_dir = project_dir / "tests"
        test_file = tests_dir / "example_summarizer.test.yaml"
        try:
            with open(test_file, "w") as f:
                yaml.dump(example_test, f, default_flow_style=False, sort_keys=False)
            logger.debug(f"Created example test: {test_file}")
        except Exception as e:
            logger.error(f"Failed to create example test file: {e}")
            raise
    
    @classmethod
    def load(cls, project_dir: Path = None) -> Optional["PBTProject"]:
        """Load existing PBT project"""
        if project_dir is None:
            project_dir = Path.cwd()
        
        logger.debug(f"Loading PBT project from: {project_dir}")
        
        config_file = project_dir / "pbt.yaml"
        if not config_file.exists():
            logger.warning(f"No pbt.yaml found in {project_dir}")
            return None
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded PBT project: {config.get('name', 'Unknown')}")
            return cls(project_dir, config)
        except Exception as e:
            logger.error(f"Failed to load project configuration: {e}")
            raise
    
    def get_prompts_dir(self) -> Path:
        """Get prompts directory path"""
        return self.project_dir / self.config.get("prompts_dir", "prompts")
    
    def get_tests_dir(self) -> Path:
        """Get tests directory path"""
        return self.project_dir / self.config.get("tests_dir", "tests")
    
    def get_evaluations_dir(self) -> Path:
        """Get evaluations directory path"""
        return self.project_dir / self.config.get("evaluations_dir", "evaluations")
    
    def get_default_model(self) -> str:
        """Get default model for the project"""
        return self.config.get("models", {}).get("default", "claude")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.config.get("models", {}).get("available", ["claude", "gpt-4"])
    
    def save_config(self):
        """Save project configuration"""
        config_path = self.project_dir / "pbt.yaml"
        try:
            with open(config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved project configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save project configuration: {e}")
            raise