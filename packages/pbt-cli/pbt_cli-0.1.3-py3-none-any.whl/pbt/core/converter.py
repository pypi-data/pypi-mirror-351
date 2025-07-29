"""Converter for PBT - converts Python agents to YAML format"""

import re
import ast
import yaml
from pathlib import Path
from typing import List, Dict


class PromptExtractor:
    """Extract prompts from Python code"""
    
    def __init__(self, python_file: str):
        self.python_file = Path(python_file)
        self.prompts = []
        
    def extract(self) -> List[Dict]:
        """Extract prompt patterns from Python code"""
        with open(self.python_file, 'r') as f:
            code = f.read()
            
        # Parse the code
        tree = ast.parse(code)
        
        # Find all functions that look like agents
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if 'agent' in node.name or 'prompt' in node.name:
                    prompt_info = self._extract_prompt_from_function(node, code)
                    if prompt_info:
                        self.prompts.append(prompt_info)
                        
        return self.prompts
    
    def _extract_prompt_from_function(self, func_node: ast.FunctionDef, full_code: str) -> Dict:
        """Extract prompt information from a function"""
        # Get function source
        func_lines = full_code.split('\n')[func_node.lineno - 1:func_node.end_lineno]
        func_source = '\n'.join(func_lines)
        
        # Look for prompt patterns
        prompt_patterns = [
            r'prompt\s*=\s*f?["\'](.+?)["\']',
            r'message\s*=\s*f?["\'](.+?)["\']',
            r'content\s*=\s*f?["\'](.+?)["\']',
            r'["\']role["\']:\s*["\']user["\'],\s*["\']content["\']:\s*f?["\'](.+?)["\']'
        ]
        
        for pattern in prompt_patterns:
            match = re.search(pattern, func_source, re.DOTALL)
            if match:
                prompt_template = match.group(1)
                
                # Extract variables from f-string
                variables = re.findall(r'\{(\w+)\}', prompt_template)
                
                # Get function parameters
                params = [arg.arg for arg in func_node.args.args if arg.arg != 'self']
                
                # Extract model from code
                model = self._extract_model(func_source)
                
                return {
                    'name': func_node.name.replace('_agent', '').replace('_prompt', '').title(),
                    'function_name': func_node.name,
                    'template': prompt_template,
                    'variables': list(set(variables)),
                    'parameters': params,
                    'model': model
                }
                
        return None
    
    def _extract_model(self, func_source: str) -> str:
        """Extract model name from function source"""
        model_patterns = [
            r'model\s*=\s*["\']([^"\']+)["\']',
            r'engine\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, func_source)
            if match:
                return match.group(1)
                
        # Default model names
        if 'gpt' in func_source.lower():
            return 'gpt-4'
        elif 'claude' in func_source.lower():
            return 'claude-3'
        else:
            return 'gpt-4'  # default


def convert_agent_file(python_file: str, output_dir: str = "agents") -> Dict:
    """Convert a Python file with agents to PBT format with minimal documentation"""
    
    # Ensure output_dir is a string
    if hasattr(output_dir, '__fspath__'):
        output_dir = str(output_dir)
    
    # Extract prompts
    extractor = PromptExtractor(python_file)
    prompts = extractor.extract()
    
    if not prompts:
        return {
            'prompts_extracted': 0,
            'yaml_files': [],
            'python_file': None
        }
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate YAML files
    yaml_files = []
    for prompt in prompts:
        yaml_file = output_path / f"{prompt['function_name'].replace('_agent', '')}.prompt.yaml"
        
        # Create YAML content
        yaml_content = {
            'name': prompt['name'],
            'version': '1.0',
            'model': prompt['model'],
            'template': prompt['template'].replace('\\n', '\n')
        }
        
        # Add variables if any
        if prompt['variables']:
            yaml_content['variables'] = {var: {'type': 'string'} for var in prompt['variables']}
        
        # Write YAML file
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
            
        yaml_files.append(str(yaml_file))
    
    # Generate converted Python file
    converted_file = _generate_converted_python(python_file, prompts, output_dir)
    
    return {
        'prompts_extracted': len(prompts),
        'yaml_files': yaml_files,
        'python_file': converted_file
    }


def _generate_converted_python(original_file: str, prompts: List[Dict], output_dir: str) -> str:
    """Generate the converted Python file with minimal comments"""
    
    original_path = Path(original_file)
    converted_file = original_path.parent / f"{original_path.stem}_converted.py"
    
    # Read original file
    with open(original_file, 'r') as f:
        original_code = f.read()
    
    # Generate new code
    lines = []
    
    # Header
    lines.append(f"# PBT-converted from {original_path.name}")
    lines.append("from pbt.runtime import PromptRunner")
    lines.append("")
    
    # Import other necessary modules from original
    imports = _extract_imports(original_code)
    for imp in imports:
        if 'openai' not in imp and 'anthropic' not in imp:
            lines.append(imp)
    
    lines.append("")
    lines.append("# PBT runners")
    
    # Create runners
    for prompt in prompts:
        runner_name = f"{prompt['function_name'].replace('_agent', '')}_runner"
        yaml_file = f"{prompt['function_name'].replace('_agent', '')}.prompt.yaml"
        lines.append(f'{runner_name} = PromptRunner("{output_dir}/{yaml_file}")')
    
    lines.append("")
    
    # Convert functions
    for prompt in prompts:
        lines.append(f"def {prompt['function_name']}({', '.join(prompt['parameters'])}):")
        lines.append(f'    """Run {prompt["name"].lower()} prompt via PBT"""')
        
        runner_name = f"{prompt['function_name'].replace('_agent', '')}_runner"
        
        # Create variables dict
        if prompt['variables']:
            var_dict = "{" + ", ".join([f'"{var}": {var}' for var in prompt['variables']]) + "}"
            lines.append(f"    return {runner_name}.run({var_dict})")
        else:
            lines.append(f"    return {runner_name}.run({{}})")
        
        lines.append("")
    
    # Write converted file
    with open(converted_file, 'w') as f:
        f.write('\n'.join(lines))
    
    return str(converted_file)


def _extract_imports(code: str) -> List[str]:
    """Extract import statements from code"""
    imports = []
    for line in code.split('\n'):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            imports.append(line)
    return imports