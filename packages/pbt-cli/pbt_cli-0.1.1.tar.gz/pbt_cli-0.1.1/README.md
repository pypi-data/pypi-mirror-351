# 🚀 PBT (Prompt Build Tool)

**The dbt + Terraform for LLM Prompts**

[![PyPI version](https://badge.fury.io/py/pbt-cli.svg)](https://badge.fury.io/py/pbt-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-green.svg)](./docs/getting_started.md)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)](./docs/implementation_status.md)

## 🎯 Why PBT?

### The Problem
AI teams face critical challenges when working with LLM prompts:
- **No Version Control**: Prompts live in notebooks, chat windows, or hardcoded strings
- **No Testing**: Hope the prompt works in production like it did in development
- **No Optimization**: Manual tweaking without systematic improvement
- **Model Lock-in**: Rewriting prompts when switching between GPT-4, Claude, or Mistral
- **Team Chaos**: No collaboration, review process, or deployment pipeline

### The Solution
PBT brings software engineering best practices to prompt development:
```bash
# Instead of hardcoded prompts scattered everywhere...
# Use versioned, tested, optimized prompt files:
pbt generate --goal "Analyze customer sentiment"
pbt test sentiment.prompt.yaml
pbt optimize sentiment.prompt.yaml --strategy cost_reduce
pbt deploy --provider supabase --env production
```

## 🏆 Use Cases

### 1. **AI Product Teams**
Build reliable AI features with confidence:
```bash
# Generate prompt from requirements
pbt generate --goal "Extract action items from meeting notes"

# Test across different scenarios
pbt test meeting-analyzer.prompt.yaml

# Compare models visually in browser
pbt web  # Opens interactive UI at http://localhost:8080
```

### 2. **Cost Optimization**
Reduce API costs by 60-80% without sacrificing quality:
```bash
# Analyze current costs
pbt optimize chatbot.yaml --analyze
# Word count: 2,547 | Estimated tokens: 3,211 | Monthly cost: $125

# Optimize for cost
pbt optimize chatbot.yaml --strategy cost_reduce
# Reduced to 821 tokens | New monthly cost: $32 | Savings: 74%
```

### 3. **Multi-Model Development**
Write once, deploy anywhere:
```yaml
# customer-support.prompt.yaml
name: customer-support
models:
  - claude-3-opus
  - gpt-4
  - gpt-3.5-turbo
template: |
  Analyze this customer message and provide:
  1. Sentiment (positive/negative/neutral)
  2. Intent classification
  3. Suggested response
  
  Message: {{ message }}
```

```bash
# Compare outputs across all models
pbt compare customer-support.prompt.yaml --input "My order never arrived!"
```

### 4. **RAG Pipeline Optimization**
Build better retrieval systems:
```bash
# Create embedding-optimized chunks
pbt chunk docs/ --strategy prompt_aware --max-tokens 512 --rag

# Test retrieval quality
pbt testcomp rag-query.prompt.yaml --aspects faithfulness,relevance
```

### 5. **Enterprise Compliance**
Meet regulatory requirements:
```bash
# Add compliance metadata
pbt badge medical-advisor.yaml --add HIPAA-compliant --add FDA-reviewed

# Comprehensive safety testing
pbt testcomp medical-advisor.yaml tests/safety.yaml --aspects safety,accuracy
# ✅ Safety: 9.8/10 | ✅ Accuracy: 9.2/10 | APPROVED FOR PRODUCTION
```

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install pbt-cli

# Or install from source
git clone https://github.com/prompt-build-tool/pbt
cd pbt
pip install -e .
```

### Getting Started

```bash
# Initialize project
pbt init my-ai-product
cd my-ai-product

# Set up API keys (see docs/API_KEYS.md for details)
cp .env.example .env
# Add: ANTHROPIC_API_KEY=sk-ant-...

# Start building!
pbt generate --goal "Summarize legal documents"
```

### ✨ NEW: Draft Command

Convert any plain text into a structured, reusable prompt:

```bash
# Simple conversion
pbt draft "Analyze customer sentiment and suggest improvements"

# With variables and custom output
pbt draft "Translate the following text to Spanish" \
  --var text --var tone \
  --output translator.prompt.yaml

# Interactive mode for refinement
pbt draft "Review this code for security issues" \
  --goal "Security code reviewer" \
  --interactive

# Short version
pbt d "Extract key insights from meeting notes"
```

This creates a properly structured prompt file with:
- Template with variable placeholders
- Input/output specifications
- Test cases (auto-generated)
- Model configurations

## 📸 Visual Examples

### Interactive Web UI (`pbt web`)
Compare models side-by-side in real-time:
```bash
pbt web
# Opens browser with interactive comparison UI
```

**Features:**
- Real-time model comparison
- Visual diff highlighting
- Response time metrics
- Token usage tracking
- Export results as JSON/CSV

### Example: Customer Service Bot

```bash
# 1. Generate prompt from requirements
pbt generate --goal "Handle customer complaints professionally"

# 2. Creates customer-complaint-handler.prompt.yaml:
```

```yaml
name: customer-complaint-handler
version: 1.0.0
models:
  - claude-3-opus
  - gpt-4
template: |
  You are a professional customer service representative.
  
  Customer Message: {{ message }}
  Customer History: {{ history }}
  
  Respond professionally addressing their concern.
  
variables:
  message:
    type: string
    required: true
  history:
    type: string
    default: "New customer"
    
tests:
  - name: angry_customer
    inputs:
      message: "This is unacceptable! I want a refund NOW!"
    expected_contains:
      - "apologize"
      - "understand your frustration"
      - "help resolve"
```

```bash
# 3. Test the prompt
pbt test customer-complaint-handler.prompt.yaml
# ✅ All tests passed (3/3)

# 4. Compare models in web UI
pbt web
# Then test with: "My package is 2 weeks late!"

# 5. Optimize for production
pbt optimize customer-complaint-handler.prompt.yaml --strategy clarity
# Improved clarity score: 8.5 → 9.2

# 6. Deploy when ready
pbt deploy --provider supabase --env production
```

### Example: Multi-Agent Chain

```yaml
# research-assistant-chain.yaml
name: research-assistant
agents:
  - name: researcher
    prompt_file: search-papers.prompt.yaml
    outputs: [papers, summaries]
    
  - name: analyzer  
    prompt_file: analyze-findings.prompt.yaml
    inputs:
      papers: list
      summaries: list
    outputs: [insights, gaps]
    
  - name: writer
    prompt_file: write-report.prompt.yaml
    inputs:
      insights: string
      gaps: list
    outputs: [report]
```

```bash
# Execute the chain
pbt chain execute research-assistant-chain.yaml \
  --input "quantum computing applications in cryptography"

# Results:
# ✅ Researcher: Found 23 relevant papers
# ✅ Analyzer: Identified 5 key insights, 3 research gaps  
# ✅ Writer: Generated 2,500 word report
# 📄 Output saved to: outputs/research_report_2024-01-15.md
```

## 🎯 What Problems Does PBT Solve?

### 1. **Prompt Versioning & Collaboration**
- **Problem**: Prompts scattered in notebooks, no version control
- **Solution**: `.prompt.yaml` files work with Git, enabling PR reviews

### 2. **Quality Assurance**
- **Problem**: Prompts break in production without warning
- **Solution**: Automated testing with `pbt test` and `pbt testcomp`

### 3. **Cost Management**
- **Problem**: GPT-4 bills skyrocketing with verbose prompts
- **Solution**: `pbt optimize` reduces tokens by 60-80%

### 4. **Model Portability**
- **Problem**: Rewriting prompts for each LLM provider
- **Solution**: Single prompt works across all models

### 5. **Team Scaling**
- **Problem**: No process for prompt review and deployment
- **Solution**: CI/CD pipeline with `pbt validate` and `pbt deploy`

## 📦 Core Features

| Feature | Command | Description |
|---------|---------|-------------|
| **Generate** | `pbt generate` | AI creates prompts from goals |
| **Draft** | `pbt draft` | Convert plain text to structured prompts |
| **Test** | `pbt test` | Automated prompt testing |
| **Optimize** | `pbt optimize` | Reduce costs, improve clarity |
| **Compare** | `pbt compare` | A/B test across models |
| **Web UI** | `pbt web` | Visual comparison dashboard |
| **Deploy** | `pbt deploy` | Push to production |
| **Chain** | `pbt chain` | Multi-agent workflows |
| **Chunk** | `pbt chunk` | RAG-optimized splitting |

## 🏗️ Project Structure

```
my-ai-product/
├── prompts/              # Version-controlled prompts
│   ├── classifier.prompt.yaml
│   └── summarizer.prompt.yaml
├── tests/               # Test cases
│   └── test_cases.yaml
├── chains/              # Multi-agent workflows
│   └── pipeline.yaml
├── pbt.yaml            # Project config
└── .env                # API keys
```

## 📚 Documentation

- [Getting Started Guide](./docs/getting_started.md)
- [API Keys Setup](./docs/API_KEYS.md)
- [Command Reference](./docs/COMMANDS.md)
- [Web UI Guide](./docs/web_ui_guide.md)
- [Examples](./examples.md)

## 🛣️ Roadmap

- [x] Core prompt engineering toolkit
- [x] Web UI for visual comparison
- [x] Multi-model support
- [x] Cost optimization
- [ ] Prompt marketplace
- [ ] VSCode extension
- [ ] Hosted cloud version

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](./CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](./LICENSE)

---

**Get Started:** `pip install pbt-cli` | **Questions?** [GitHub Issues](https://github.com/prompt-build-tool/pbt/issues) | **Built with ❤️ by the PBT Team**