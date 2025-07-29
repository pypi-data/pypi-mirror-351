# Getting Started with PBT (Prompt Build Tool)

## Welcome to PBT 🚀

PBT is an infrastructure-grade prompt engineering CLI tool that helps you build, test, and deploy production-ready prompts with confidence. This guide will get you up and running in minutes.

## Prerequisites

### System Requirements
- **Python 3.9+** (Python 3.11+ recommended)
- **4GB RAM** minimum (8GB+ recommended)
- **2GB disk space** for installation and cache
- **Internet connection** for API integrations

### Supported Platforms
- ✅ **macOS** 10.15+
- ✅ **Ubuntu** 18.04+
- ✅ **Windows** 10+
- ✅ **Docker** (all platforms)

## Installation

### Option 1: Quick Install (Recommended)
```bash
# Install PBT using pip
pip install prompt-build-tool

# Verify installation
pbt --version
```

### Option 2: From Source
```bash
# Clone the repository
git clone https://github.com/your-org/pbt-prompt-build-tool.git
cd pbt-prompt-build-tool

# Install in development mode
pip install -e .

# Verify installation
pbt --version
```

### Option 3: Using Docker
```bash
# Pull the official image
docker pull pbt/prompt-build-tool:latest

# Run PBT in a container
docker run -it --rm -v $(pwd):/workspace pbt/prompt-build-tool:latest

# Create an alias for convenience
echo "alias pbt='docker run -it --rm -v \$(pwd):/workspace pbt/prompt-build-tool:latest'" >> ~/.bashrc
source ~/.bashrc
```

## First Steps

### 1. Create Your First Project

Let's create a simple project to get familiar with PBT:

```bash
# Create a new project
pbt init my-first-project

# Navigate to the project directory
cd my-first-project

# Check the project structure
ls -la
```

You should see:
```
my-first-project/
├── pbt.yaml                 # Project configuration
├── .env.example            # Environment template
├── prompts/                # Your prompt files
├── tests/                  # Test definitions
├── evaluations/           # Evaluation reports
├── chains/                # Multi-step workflows
└── chunks/                # Text chunking configs
```

### 2. Set Up API Keys

Copy the environment template and add your API keys:

```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Add at least one LLM provider API key:

```bash
# For Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For OpenAI
OPENAI_API_KEY=sk-your-key-here

# For Azure OpenAI
AZURE_OPENAI_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

### 3. Explore the Example Prompt

PBT creates an example prompt to help you get started:

```bash
# View the example prompt
cat prompts/example_summarizer.prompt.yaml
```

This shows you the basic prompt format:
```yaml
name: "Example-Text-Summarizer"
version: "1.0"
model: "claude"
description: "Example prompt that summarizes text content"

template: |
  Summarize the following text concisely:
  
  Text: {{ text }}
  
  Please provide a brief summary highlighting the key points.

variables:
  text:
    type: string
    description: "Text content to summarize"
    required: true
```

### 4. Test Your First Prompt

Let's test the example prompt:

```bash
# Run the example test
pbt test prompts/example_summarizer.prompt.yaml

# Or test with custom input
pbt render prompts/example_summarizer.prompt.yaml --vars '{"text": "Artificial Intelligence is transforming how we work and live. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions that were previously impossible."}'
```

## Core Concepts

### Prompts
- **Prompts** are the fundamental unit in PBT
- Stored as `.prompt.yaml` files with templates, variables, and metadata
- Support Jinja2 templating for dynamic content
- Include versioning and configuration settings

### Tests
- **Tests** validate prompt behavior and quality
- Defined in `.test.yaml` files
- Support multiple test types: functional, safety, performance, style
- Can be auto-generated using AI

### Evaluations
- **Evaluations** provide detailed quality assessments
- Generate comprehensive reports with scores and recommendations
- Support multi-dimensional analysis (correctness, clarity, etc.)
- Enable A/B testing and model comparison

## Common Workflows

### Creating a New Prompt

1. **Generate a prompt using AI**:
```bash
pbt generate "Create a professional email response" --style=formal --model=claude
```

2. **Edit the generated prompt**:
```bash
# Open the generated file in your editor
code prompts/professional_email_response.prompt.yaml
```

3. **Test the prompt**:
```bash
pbt test prompts/professional_email_response.prompt.yaml
```

4. **Auto-generate additional tests**:
```bash
pbt test prompts/professional_email_response.prompt.yaml --auto-generate --count=5
```

### Comparing Models

Compare how different models perform with your prompt:

```bash
pbt compare prompts/professional_email_response.prompt.yaml --models=claude,gpt-4,gpt-3.5-turbo
```

### Optimizing for Cost

Reduce costs while maintaining quality:

```bash
pbt optimize prompts/professional_email_response.prompt.yaml --target=cost
```

## Understanding Project Structure

### Configuration File (pbt.yaml)
The project configuration controls how PBT behaves:

```yaml
name: "My Project"
version: "1.0.0"

# Model settings
models:
  default: "claude"
  available: ["claude", "gpt-4", "gpt-3.5-turbo"]

# Testing settings
settings:
  test_timeout: 30
  max_retries: 3
  save_reports: true

# Cost optimization
optimization:
  target: "balanced"
  max_token_reduction: 0.3
```

### Prompt Files (.prompt.yaml)
Each prompt is a structured YAML file:

```yaml
# Basic information
name: "My-Prompt"
version: "1.0"
model: "claude"
description: "What this prompt does"

# The actual prompt template
template: |
  You are a helpful assistant.
  
  Task: {{ task }}
  Context: {{ context }}
  
  Please provide a detailed response.

# Input variables
variables:
  task:
    type: string
    description: "The task to complete"
    required: true
  context:
    type: string
    description: "Additional context"
    default: "No additional context provided"

# Metadata
metadata:
  tags: ["assistant", "general"]
  author: "your-email@company.com"
  created: "2024-01-15"
```

### Test Files (.test.yaml)
Tests define how to validate your prompts:

```yaml
prompt_file: "prompts/my_prompt.prompt.yaml"
description: "Tests for my prompt"

test_cases:
  - name: "basic_functionality"
    inputs:
      task: "Explain quantum computing"
      context: "For a general audience"
    expected_criteria:
      - "Mentions quantum mechanics"
      - "Uses simple language"
      - "No technical jargon"
    quality_thresholds:
      min_score: 0.8
      max_length: 500
```

## Next Steps

### 🎯 Essential Next Steps

1. **Add more prompts**: Create prompts for your specific use cases
2. **Set up integrations**: Connect Slack, Notion, or other tools
3. **Explore advanced features**: Try chains, RAG optimization, and i18n
4. **Deploy to production**: Use Render or Fly.io for hosting

### 🔧 Intermediate Features

1. **Multi-agent chains**: Link prompts together for complex workflows
2. **RAG optimization**: Enhance prompts with retrieval-augmented generation
3. **Internationalization**: Support multiple languages
4. **Visual content**: Generate diagrams and videos for your prompts

### 🚀 Advanced Features

1. **Custom integrations**: Build your own integrations using the plugin system
2. **Marketplace**: Publish and sell your prompt packs
3. **Enterprise deployment**: Set up team collaboration and governance
4. **Performance monitoring**: Track usage, costs, and quality metrics

## Getting Help

### Documentation
- 📖 **[User Manual](user_manual.md)** - Comprehensive usage guide
- 🔧 **[API Reference](API.md)** - Complete API documentation
- 🏗️ **[Architecture Guide](architecture_deep_dive.md)** - System design details
- 🔍 **[Troubleshooting](troubleshooting_guide.md)** - Common issues and solutions

### Community & Support
- 💬 **GitHub Discussions** - Ask questions and share ideas
- 🐛 **GitHub Issues** - Report bugs and request features
- 📧 **Email Support** - contact@pbt.dev for enterprise support
- 📱 **Discord Community** - Real-time chat with other users

### Quick Commands Reference
```bash
# Get help for any command
pbt --help
pbt generate --help

# Check system status
pbt status

# Validate your configuration
pbt config validate

# View logs
pbt logs --tail=50

# Update PBT
pip install --upgrade prompt-build-tool
```

## Examples to Try

### 1. Customer Service Assistant
```bash
pbt generate "Customer service email response assistant" --style=empathetic
```

### 2. Code Review Helper
```bash
pbt generate "Code review feedback generator" --style=constructive
```

### 3. Content Summarizer
```bash
pbt generate "Technical documentation summarizer" --style=concise
```

### 4. Translation Assistant
```bash
pbt generate "Professional document translator" --style=formal
```

## Tips for Success

### 🎯 Best Practices
1. **Start simple**: Begin with basic prompts and gradually add complexity
2. **Test early**: Write tests as you develop prompts
3. **Version everything**: Use semantic versioning for your prompts
4. **Document well**: Add clear descriptions and metadata
5. **Monitor performance**: Track quality and costs regularly

### ⚡ Performance Tips
1. **Use caching**: Enable response caching for faster iterations
2. **Batch operations**: Test multiple prompts together
3. **Optimize prompts**: Run optimization regularly
4. **Use local models**: Try Ollama for development and testing

### 🔒 Security Tips
1. **Protect API keys**: Never commit keys to version control
2. **Use environment variables**: Store sensitive config in .env files
3. **Enable safety filters**: Use content filtering for production
4. **Regular audits**: Review prompts for bias and safety issues

## Ready to Build? 🛠️

You're now ready to start building amazing prompts with PBT! Here's what to do next:

1. **Create your first real prompt** for your use case
2. **Set up testing** to ensure quality
3. **Explore integrations** that fit your workflow
4. **Join the community** to learn from other users

Happy prompt engineering! 🎉

---

**Need help?** Check out our [Troubleshooting Guide](troubleshooting_guide.md) or reach out to the community in [GitHub Discussions](https://github.com/your-org/pbt/discussions).