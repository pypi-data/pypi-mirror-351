"""
Prompt Build Tool (PBT) - Infrastructure-grade prompt engineering for AI teams.

PBT is an open-source prompt operating system designed for teams that need 
dbt + Terraform for LLM prompts. It works across Claude, GPT-4, Mistral, 
Azure, Ollama with a Visual Prompt IDE + CLI for authoring, diffing, testing, 
and deploying prompts.
"""

import os
from pathlib import Path

# Automatically load .env files on import
try:
    from dotenv import load_dotenv
    
    # Look for .env files in current directory and parent directories
    current_dir = Path.cwd()
    
    # Try current directory first
    env_file = current_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Look in parent directories
        for parent in current_dir.parents:
            env_file = parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                break
        else:
            # Try home directory
            home_env = Path.home() / ".pbt" / ".env"
            if home_env.exists():
                load_dotenv(home_env)
            
            # Also try loading without explicit path (searches upward)
            load_dotenv()
            
except ImportError:
    # python-dotenv not available, skip loading
    pass

from pbt.__version__ import __version__
from pbt.runtime import PromptRunner

# Add PromptPack for backward compatibility
class PromptPack:
    """Load and run prompts from YAML files"""
    
    def __init__(self, prompts_dir):
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self._load_prompts()
    
    @classmethod
    def load(cls, prompts_dir):
        """Load prompts from directory"""
        return cls(prompts_dir)
    
    def _load_prompts(self):
        """Load all YAML prompt files"""
        import glob
        pattern = os.path.join(self.prompts_dir, "*.yaml")
        for yaml_file in glob.glob(pattern):
            prompt_name = os.path.basename(yaml_file).replace('.yaml', '')
            self.prompts[prompt_name] = PromptRunner(yaml_file)
    
    def run(self, prompt_name, model=None, **kwargs):
        """Run a prompt with the specified model and variables"""
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found in {self.prompts_dir}")
        
        return self.prompts[prompt_name].run(kwargs, model=model)

__all__ = ["__version__", "PromptRunner", "PromptPack"]