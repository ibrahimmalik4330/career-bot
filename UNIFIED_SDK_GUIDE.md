# Using OpenAI SDK for All LLM Providers

## Overview

This project uses a **unified OpenAI SDK approach** to call multiple LLM providers including OpenAI GPT and Google Gemini. This follows the industry standard as of January 2026, where OpenAI's API format has become the de facto standard for LLM interactions.

## Why This Approach?

### Benefits

1. **Single Dependency**: Only need `openai` package, no provider-specific SDKs
2. **Consistent Interface**: Same code structure across all providers
3. **Easy Provider Switching**: Change providers via configuration, not code changes
4. **Native Tool Support**: Function calling works uniformly across providers
5. **Future-Proof**: Easy to add new providers that support OpenAI format

### Industry Context (2026)

By January 2026, most major LLM providers have adopted OpenAI-compatible APIs:

- Google Gemini offers OpenAI-compatible endpoints
- Anthropic Claude supports OpenAI format
- Open-source models (via vLLM, Ollama) use OpenAI format
- Proxy services (OpenRouter, LiteLLM) provide unified access

## Architecture

### Configuration-Based Routing

Instead of using different SDKs, we use a **single OpenAI client** with different configurations:

```python
# config/settings.py
LLM_CONFIGS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash-exp",
    },
}
```

### Unified Client Implementation

```python
# agent/llm_client.py
from openai import OpenAI

class LLMClient:
    def __init__(self, provider: str = "openai"):
        config = LLM_CONFIGS[provider]

        # Single SDK, different configuration
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],  # Provider-specific endpoint
        )
        self.model = config["model"]

    def chat_completion(self, messages, tools=None):
        # Identical interface for all providers
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )
```

## Provider Setup

### OpenAI

**Standard OpenAI endpoint** (default):

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL defaults to https://api.openai.com/v1
```

### Google Gemini

**OpenAI-compatible Gemini endpoint**:

```env
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

Key points:

- Use the `/openai/` endpoint path
- Gemini API key format starts with `AIza`
- Supports all OpenAI message formats
- Function calling works identically

### Adding New Providers

To add any OpenAI-compatible provider:

1. **Add to config** in `config/settings.py`:

   ```python
   LLM_CONFIGS = {
       # ... existing providers
       "anthropic": {
           "api_key": os.getenv("ANTHROPIC_API_KEY"),
           "base_url": "https://api.anthropic.com/v1",
           "model": "claude-3-5-sonnet-20241022",
       },
   }
   ```

2. **Set environment variables**:

   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **No code changes needed!** The client works automatically.

## Code Examples

### Basic Usage

```python
from agent.llm_client import LLMClient

# Initialize for OpenAI
client = LLMClient(provider="openai")

# Or for Gemini (identical interface)
client = LLMClient(provider="gemini")

# Same code for both providers
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

response = client.chat_completion(messages)
print(response.choices[0].message.content)
```

### With Function Calling

```python
from agent.llm_client import LLMClient
from tools.schemas import tools

# Works identically for all providers
client = LLMClient(provider="gemini")

messages = [{"role": "user", "content": "Record email: user@example.com"}]

response = client.chat_completion(messages, tools=tools)

# Unified response format
if response.choices[0].finish_reason == "tool_calls":
    for call in response.choices[0].message.tool_calls:
        print(f"Tool: {call.function.name}")
        print(f"Args: {call.function.arguments}")
```

### Dynamic Provider Selection

```python
import os
from agent.me import Me

# Select provider at runtime
provider = os.getenv("LLM_PROVIDER", "openai")
agent = Me(llm_provider=provider)

# Chat works the same regardless of provider
response = agent.chat("Tell me about your experience", [])
```

## API Format Compatibility

### Message Format

Both providers use **identical OpenAI message format**:

```python
messages = [
    {
        "role": "system",
        "content": "System prompt"
    },
    {
        "role": "user",
        "content": "User message"
    },
    {
        "role": "assistant",
        "content": "Assistant response",
        "tool_calls": [...]  # If using tools
    },
    {
        "role": "tool",
        "tool_call_id": "call_123",
        "content": "{\"result\": \"success\"}"
    }
]
```

### Tool/Function Format

Tools use **OpenAI function calling schema**:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param"]
        }
    }
}]
```

### Response Format

All providers return **OpenAI ChatCompletion object**:

```python
response.choices[0].message.content          # Text response
response.choices[0].message.tool_calls       # Tool calls (if any)
response.choices[0].finish_reason            # "stop" or "tool_calls"
response.usage.prompt_tokens                 # Token usage
response.usage.completion_tokens
```

## Gemini-Specific Details

### OpenAI-Compatible Endpoint

Google provides an OpenAI-compatible endpoint for Gemini:

```
https://generativelanguage.googleapis.com/v1beta/openai/
```

This endpoint:

- Accepts OpenAI request format
- Returns OpenAI response format
- Supports function calling
- Works with OpenAI SDK directly

### Model Names

Use Gemini model names as-is:

```python
GEMINI_MODEL=gemini-2.0-flash-exp      # Latest experimental
GEMINI_MODEL=gemini-1.5-pro            # Stable pro model
GEMINI_MODEL=gemini-1.5-flash          # Stable flash model
```

### API Key Format

Gemini API keys typically start with `AIza`:

```env
GEMINI_API_KEY=AIzaSy...
```

### Authentication

The API key is passed via OpenAI SDK's standard auth:

```python
client = OpenAI(
    api_key="AIza...",  # Gemini key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

## Testing Both Providers

### Quick Test Script

Create `test_providers.py`:

```python
from agent.llm_client import LLMClient

def test_provider(provider_name):
    print(f"\n=== Testing {provider_name.upper()} ===")

    client = LLMClient(provider=provider_name)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one sentence."}
    ]

    response = client.chat_completion(messages)
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.usage.total_tokens}")

# Test both
test_provider("openai")
test_provider("gemini")
```

Run:

```bash
python test_providers.py
```

### Comparing Responses

```python
from agent.me import Me

def compare_providers():
    openai_agent = Me(llm_provider="openai")
    gemini_agent = Me(llm_provider="gemini")

    question = "What is 2+2?"

    print("OpenAI:", openai_agent.chat(question, []))
    print("Gemini:", gemini_agent.chat(question, []))

compare_providers()
```

## Migration Guide

### From Multiple SDKs to Unified SDK

If you previously used separate SDKs (e.g., `google-generativeai`):

**Before:**

```python
from openai import OpenAI
import google.generativeai as genai

# Different SDKs, different interfaces
openai_client = OpenAI()
genai.configure(api_key="...")
gemini_model = genai.GenerativeModel("gemini-pro")

# Different method calls
openai_response = openai_client.chat.completions.create(...)
gemini_response = gemini_model.generate_content(...)
```

**After:**

```python
from openai import OpenAI

# Single SDK, unified interface
openai_client = OpenAI(base_url="https://api.openai.com/v1")
gemini_client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Identical method calls
openai_response = openai_client.chat.completions.create(...)
gemini_response = gemini_client.chat.completions.create(...)
```

### Benefits of Migration

1. **Code Simplification**: ~200 lines removed (no format conversion)
2. **Single Dependency**: Removed `google-generativeai` from requirements
3. **Easier Testing**: Same interface = same test code
4. **Better Maintainability**: One code path instead of multiple

## Troubleshooting

### Common Issues

**Issue: "Invalid base URL"**

```
Solution: Verify the base URL includes the full path
Gemini: https://generativelanguage.googleapis.com/v1beta/openai/
OpenAI: https://api.openai.com/v1
```

**Issue: "Authentication failed"**

```
Solution: Check API key format
- OpenAI keys start with: sk-proj-... or sk-...
- Gemini keys start with: AIza...
```

**Issue: "Model not found"**

```
Solution: Verify model name is correct
- OpenAI: gpt-4o-mini, gpt-4o, etc.
- Gemini: gemini-2.0-flash-exp, gemini-1.5-pro, etc.
```

**Issue: "Function calling not working"**

```
Solution: Ensure you're using the correct endpoint
- For Gemini, must use /openai/ path
- Tool schema must be in OpenAI format
```

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now you'll see all API requests/responses
client = LLMClient(provider="gemini")
response = client.chat_completion(messages)
```

## Performance Considerations

### Speed Comparison

Typical latencies (as of Jan 2026):

- **GPT-4o-mini**: ~500-800ms
- **Gemini 2.0 Flash**: ~300-600ms
- **GPT-4o**: ~1-2s
- **Gemini 1.5 Pro**: ~1-2s

### Cost Comparison

Approximate costs per 1M tokens:

- **GPT-4o-mini**: $0.15 input / $0.60 output
- **Gemini 2.0 Flash**: $0.075 input / $0.30 output (free tier available)
- **GPT-4o**: $2.50 input / $10 output
- **Gemini 1.5 Pro**: $1.25 input / $5 output

### Optimization Tips

1. **Use Flash models** for speed-sensitive applications
2. **Cache system prompts** when possible
3. **Batch requests** for multiple queries
4. **Monitor token usage** across providers
5. **Switch providers** based on workload

## Advanced Usage

### Custom Base URLs

For self-hosted or proxy endpoints:

```env
# Using OpenRouter (proxy for multiple models)
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Using local vLLM server
OPENAI_BASE_URL=http://localhost:8000/v1

# Using Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
```

### Provider-Specific Parameters

Some providers support additional parameters:

```python
response = client.chat_completion(
    messages=messages,
    temperature=0.7,
    top_p=0.9,
    max_tokens=1000,
    # Provider-specific (if supported)
    extra_body={
        "top_k": 40,  # Gemini-specific
    }
)
```

### Retry Logic

Implement retries for reliability:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def resilient_chat(client, messages):
    return client.chat_completion(messages)

# Use it
response = resilient_chat(client, messages)
```

## Best Practices

1. **Use environment variables** for all configuration
2. **Validate API keys** at startup
3. **Handle rate limits** gracefully
4. **Log provider and model** for debugging
5. **Test with both providers** in development
6. **Monitor costs** per provider
7. **Fallback to alternative provider** on errors

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [OpenRouter (Multi-Provider Proxy)](https://openrouter.ai/)
- [LiteLLM (Unified Interface)](https://github.com/BerriAI/litellm)

## Summary

The unified OpenAI SDK approach provides:

- ✅ Single dependency (`openai` package only)
- ✅ Consistent interface across providers
- ✅ Configuration-based provider switching
- ✅ Native tool/function calling support
- ✅ Easy to extend with new providers
- ✅ Industry-standard format (2026)

This is the modern, maintainable way to work with multiple LLM providers!

---

Last Updated: January 2026
