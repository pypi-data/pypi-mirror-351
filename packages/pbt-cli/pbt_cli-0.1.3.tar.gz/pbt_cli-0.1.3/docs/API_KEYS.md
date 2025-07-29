# 🔑 PBT API Keys Guide

## Required API Keys

### 🎯 **ANTHROPIC_API_KEY** (Required)
- **Purpose**: Core prompt generation, evaluation, and Claude judge
- **Get from**: [console.anthropic.com](https://console.anthropic.com)
- **Cost**: Pay-per-use (~$0.01-0.10 per prompt)
- **Setup**: 
  1. Create Anthropic account
  2. Go to API Keys section
  3. Create new key starting with `sk-ant-`
- **Usage**: Used for 90% of PBT functionality

### 🤖 **OPENAI_API_KEY** (Recommended)
- **Purpose**: GPT-4 prompt generation and model comparison
- **Get from**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Cost**: Pay-per-use (~$0.03-0.12 per prompt)
- **Setup**: 
  1. Create OpenAI account
  2. Add payment method
  3. Create API key starting with `sk-`
- **Usage**: For comparing Claude vs GPT-4 outputs

## Optional API Keys

### 🗄️ **SUPABASE_URL & SUPABASE_KEY** (Optional)
- **Purpose**: Database for storing prompts, evaluations, user data
- **Get from**: [supabase.com](https://supabase.com)
- **Cost**: Free up to 500MB, then ~$25/month
- **Setup**:
  1. Create Supabase project
  2. Copy Project URL and anon public key
  3. Run database schema from `pbt/server/db/schema.sql`
- **Usage**: Enables marketplace, analytics, prompt sharing

### 💳 **STRIPE_SECRET_KEY** (Optional)
- **Purpose**: Payment processing for marketplace
- **Get from**: [dashboard.stripe.com](https://dashboard.stripe.com)
- **Cost**: 2.9% + 30¢ per transaction
- **Setup**:
  1. Create Stripe account
  2. Get test/live secret keys
  3. Configure products and prices
- **Usage**: Selling and buying prompt packs

### 📢 **SLACK_WEBHOOK_URL** (Optional)
- **Purpose**: Team notifications when prompts are created/tested
- **Get from**: [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)
- **Cost**: Free
- **Setup**:
  1. Create Slack app
  2. Enable incoming webhooks
  3. Add webhook to workspace
- **Usage**: Real-time team collaboration

### 💬 **DISCORD_WEBHOOK_URL** (Optional)
- **Purpose**: Community notifications
- **Get from**: Discord server settings > Integrations > Webhooks
- **Cost**: Free
- **Setup**:
  1. Go to Discord server settings
  2. Create webhook
  3. Copy webhook URL
- **Usage**: Community prompt sharing

### 📝 **NOTION_TOKEN** (Optional)
- **Purpose**: Export prompts to Notion workspaces
- **Get from**: [notion.so/my-integrations](https://www.notion.so/my-integrations)
- **Cost**: Free
- **Setup**:
  1. Create Notion integration
  2. Get integration token
  3. Share database with integration
- **Usage**: Documentation and knowledge management

## Quick Start - Minimum Setup

**To get started immediately, you only need:**

1. **ANTHROPIC_API_KEY** - This enables:
   - Prompt generation
   - Prompt testing
   - Evaluation and scoring
   - Basic CLI functionality

```bash
# 1. Get Anthropic API key
# Visit: https://console.anthropic.com

# 2. Install PBT
./install_system.sh

# 3. Create project and add key
mkdir my-prompts && cd my-prompts
pbt init --name "My Prompts"
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-your-key

# 4. Start using PBT
pbt generate --goal "Summarize customer feedback"
pbt test your_prompt.yaml
```

## Full Setup - All Features

**For complete functionality, add these keys:**

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
OPENAI_API_KEY=sk-your-openai-key

# Database (enables marketplace, analytics)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Marketplace (enables selling/buying prompts)
STRIPE_SECRET_KEY=sk_test_your-stripe-key

# Notifications (enables team collaboration)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Export (enables Notion integration)
NOTION_TOKEN=secret_your-notion-token
```

## Security Best Practices

### ✅ **Do's**
- Keep API keys in `.env` file (never commit to git)
- Use test/development keys for testing
- Rotate keys regularly
- Monitor API usage and costs
- Use environment-specific keys (dev/staging/prod)

### ❌ **Don'ts**
- Never commit API keys to version control
- Don't share keys in chat/email
- Don't use production keys for development
- Don't hardcode keys in source code

## Cost Management

### **Free Tier Usage**
- **Anthropic**: $5 free credit for new accounts
- **OpenAI**: $5 free credit for new accounts  
- **Supabase**: 500MB database free
- **Stripe**: No monthly fees, just transaction costs

### **Estimated Monthly Costs**
- **Light usage** (100 prompts/month): ~$5-10
- **Medium usage** (1000 prompts/month): ~$20-50
- **Heavy usage** (10000 prompts/month): ~$100-300

### **Cost Optimization Tips**
- Start with just Anthropic key
- Use shorter prompts for testing
- Cache results when possible
- Monitor usage in provider dashboards
- Set billing alerts

## Troubleshooting

### **Invalid API Key Errors**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Verify key format
# Anthropic: sk-ant-...
# OpenAI: sk-...
# Supabase: long alphanumeric string
```

### **Rate Limit Errors**
- Check your API usage limits
- Implement exponential backoff
- Upgrade to higher tier if needed

### **Permission Errors**
- Ensure API keys have correct permissions
- Check if billing is set up (required for OpenAI)
- Verify workspace access (for Notion/Slack)

## Need Help?

- **API Key Issues**: Check provider documentation
- **PBT Setup**: Run `pbt --help` or see [INSTALL.md](INSTALL.md)
- **Feature Questions**: See main [README.md](README.md)