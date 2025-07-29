"""Example test to verify test setup is working"""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from pbt.cli.main import app
from pbt.core.converter import PromptExtractor, convert_agent_file


def test_cli_version():
    """Test CLI version command"""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    
    assert result.exit_code == 0
    assert "PBT (Prompt Build Tool)" in result.output
    assert "version" in result.output


def test_cli_help():
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "Prompt Build Tool" in result.output
    assert "Commands" in result.output


def test_prompt_extractor_basic():
    """Test basic prompt extraction"""
    # Create a simple test file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
def test_agent(input_text):
    """Test agent function"""
    prompt = f"Process this: {input_text}"
    return prompt
''')
        temp_file = f.name
    
    try:
        extractor = PromptExtractor(temp_file)
        prompts = extractor.extract()
        
        assert len(prompts) == 1
        assert prompts[0]['name'] == 'Test'
        assert prompts[0]['template'] == 'Process this: {input_text}'
        assert 'input_text' in prompts[0]['variables']
    finally:
        Path(temp_file).unlink()


def test_convert_agent_file_basic(temp_dir):
    """Test basic agent file conversion"""
    # Create test agent file
    agent_file = temp_dir / "test_agent.py"
    agent_file.write_text('''
def summarizer_agent(text):
    """Summarize text"""
    prompt = f"Summarize: {text}"
    return call_llm(prompt)
''')
    
    # Convert
    result = convert_agent_file(str(agent_file), str(temp_dir / "output"))
    
    # Verify results
    assert result['prompts_extracted'] == 1
    assert len(result['yaml_files']) == 1
    assert result['python_file'] is not None
    
    # Check YAML file exists
    yaml_file = Path(result['yaml_files'][0])
    assert yaml_file.exists()
    assert yaml_file.suffix == '.yaml'


@pytest.mark.parametrize("command", [
    "init",
    "generate",
    "test", 
    "validate",
    "convert",
    "compare",
    "gentests"
])
def test_command_help(command):
    """Test that all commands have help text"""
    runner = CliRunner()
    result = runner.invoke(app, [command, "--help"])
    
    assert result.exit_code == 0
    assert command in result.output.lower() or "usage:" in result.output.lower()