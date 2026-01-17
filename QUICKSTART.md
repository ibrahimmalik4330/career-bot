# Quick Reference: Unified OpenAI SDK Setup

## ✅ What Changed

**Before:** Separate SDKs for each provider  
**After:** Single OpenAI SDK for all providers

## 📦 Dependencies

```toml
dependencies = [
    "openai>=2.14.0",     # ✅ Single SDK for all providers
    # google-generativeai  # ❌ Removed - not needed
]
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Provider Selection
LLM_PROVIDER=openai          # or "gemini"

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Gemini (OpenAI-compatible endpoint)
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## 💻 Code Structure

### 1. Config (`config/settings.py`)

```python
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

### 2. Client (`agent/llm_client.py`)

```python
from openai import OpenAI

class LLMClient:
    def __init__(self, provider: str = "openai"):
        config = LLM_CONFIGS[provider]
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],  # 🔑 Key difference
        )

    def chat_completion(self, messages, tools=None):
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )
```

### 3. Agent (`agent/me.py`)

```python
class Me:
    def __init__(self, llm_provider: str = LLM_PROVIDER):
        self.llm_client = create_llm_client(llm_provider)

    def chat(self, message, history):
        response = self.llm_client.chat_completion(messages, tools)

        # Same interface for all providers!
        if response.choices[0].finish_reason == "tool_calls":
            self._handle_tool_calls(response.choices[0].message.tool_calls)
        else:
            return response.choices[0].message.content
```

## 🚀 Usage

### Switch Providers

```bash
# Use OpenAI
export LLM_PROVIDER=openai

# Use Gemini
export LLM_PROVIDER=gemini
```

### Run Application

```bash
python app.py
```

## 🎯 Key Benefits

| Aspect                | Before                 | After            |
| --------------------- | ---------------------- | ---------------- |
| **Dependencies**      | 2 SDKs                 | 1 SDK            |
| **Code Complexity**   | 200+ lines             | ~100 lines       |
| **Format Conversion** | Required               | Not needed       |
| **Interface**         | Different per provider | Unified          |
| **Maintenance**       | Multiple code paths    | Single code path |

## 🔍 Quick Test

```python
from agent.llm_client import LLMClient

# Test OpenAI
client = LLMClient("openai")
response = client.chat_completion([
    {"role": "user", "content": "Hello!"}
])
print(response.choices[0].message.content)

# Test Gemini (identical code!)
client = LLMClient("gemini")
response = client.chat_completion([
    {"role": "user", "content": "Hello!"}
])
print(response.choices[0].message.content)
```

## 📝 Common Tasks

### Add New Provider

1. Add to `LLM_CONFIGS`:

   ```python
   "anthropic": {
       "api_key": os.getenv("ANTHROPIC_API_KEY"),
       "base_url": "https://api.anthropic.com/v1",
       "model": "claude-3-5-sonnet-20241022",
   }
   ```

2. Set env vars:

   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Done! No code changes needed.

### Debug Issues

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# See all API requests/responses
client = LLMClient("gemini")
```

## 🆘 Troubleshooting

| Issue              | Solution                                              |
| ------------------ | ----------------------------------------------------- |
| "Invalid base URL" | Check `GEMINI_BASE_URL` includes `/openai/` path      |
| "Auth failed"      | Verify API key format (OpenAI: `sk-`, Gemini: `AIza`) |
| "Model not found"  | Check model name matches provider                     |

## 📚 Documentation

- Full Guide: [UNIFIED_SDK_GUIDE.md](UNIFIED_SDK_GUIDE.md)
- README: [README.md](README.md)
- Example Config: [.env.example](.env.example)

---

**Architecture:** OpenAI SDK Standard (Jan 2026)  
**Status:** ✅ Production Ready  
**Providers:** OpenAI, Gemini (easily extensible)
