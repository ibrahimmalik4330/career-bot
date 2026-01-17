# Career Bot

A professional career assistant chatbot powered by AI, featuring support for multiple LLM providers through a unified OpenAI SDK interface.

## Features

- 🤖 **Unified OpenAI SDK**: Single SDK for all LLM providers (OpenAI, Gemini, and more)
- 🔧 **Function Calling**: Built-in tools for recording user details and unknown questions
- 📄 **LinkedIn Integration**: Loads and processes LinkedIn profile from PDF
- 🎨 **Gradio Interface**: Clean web interface for interactions
- 🔔 **Pushover Notifications**: Real-time notifications for user interactions
- 🏗️ **Clean Architecture**: Industry-standard patterns as of January 2026

## Architecture

The project follows a modular architecture leveraging the **OpenAI SDK standard** (Jan 2026):

```
career_bot/
├── agent/                  # Core agent logic
│   ├── llm_client.py      # Unified LLM client (OpenAI SDK)
│   ├── me.py              # Main agent implementation
│   └── prompt.py          # Prompt building utilities
├── config/                # Configuration management
│   └── settings.py        # Provider configs with base URLs
├── tools/                 # Tool implementations
│   ├── handlers.py        # Tool execution handlers
│   ├── schemas.py         # Tool schemas (OpenAI format)
│   └── notifications.py   # Notification services
├── data/me/              # Personal data storage
│   ├── summary.txt       # Career summary
│   └── *.pdf             # LinkedIn profile PDF
└── app.py                # Application entry point
```

### Why Unified OpenAI SDK?

As of 2026, the OpenAI API format has become the industry standard:

- **Single Dependency**: One SDK for all providers
- **Consistent Interface**: Same code structure across providers
- **Easy Provider Switching**: Configuration-based routing
- **Native Tool Support**: Function calling works uniformly

## LLM Provider Support

### How It Works

The implementation uses OpenAI SDK with provider-specific **base URLs**:

```python
# OpenAI (default)
base_url = "https://api.openai.com/v1"

# Gemini (OpenAI-compatible endpoint)
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
```

### Supported Models

#### OpenAI

- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-4-turbo`
- All OpenAI chat models

#### Google Gemini

- `gemini-2.0-flash-exp` (default, as of Jan 2026)
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- All models with OpenAI-compatible API

### Provider Selection

Set the `LLM_PROVIDER` environment variable:

```bash
# Use OpenAI (default)
LLM_PROVIDER=openai

# Use Google Gemini
LLM_PROVIDER=gemini
```

## Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd career_bot
   ```

2. **Install dependencies**

   ```bash
   # Using pip
   pip install -e .

   # Or using uv (recommended for faster installs)
   uv pip install -e .
   ```

3. **Configure environment variables**

   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env with your credentials
   ```

4. **Set up your data**
   - Place your LinkedIn PDF in `data/me/`
   - Update `data/me/summary.txt` with your career summary

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Provider Configuration
LLM_PROVIDER=openai  # or "gemini"

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Google Gemini Configuration
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Notification Services
PUSHOVER_TOKEN=your_token
PUSHOVER_USER=your_user
```

### Getting API Keys

**OpenAI:**

1. Visit [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Create a new secret key

**Google Gemini:**

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Use with OpenAI-compatible endpoint (configured automatically)

## Usage

### Running the Application

```bash
python app.py
```

The Gradio interface will launch automatically. Access it at `http://localhost:7860`

### Switching LLM Providers

**Method 1: Environment Variable**

```bash
# In .env file
LLM_PROVIDER=gemini
```

**Method 2: Programmatic**

```python
from agent.me import Me

# Use Gemini
agent = Me(llm_provider="gemini")

# Use OpenAI
agent = Me(llm_provider="openai")
```

## Development

### Project Structure Highlights

#### LLM Client (`agent/llm_client.py`)

Implements a **unified client** using OpenAI SDK for all providers:

```python
class LLMClient:
    """Unified client using OpenAI SDK with configurable base URLs."""

    def __init__(self, provider: str = "openai"):
        config = LLM_CONFIGS[provider]
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],  # Provider-specific endpoint
        )
```

**Key Benefits:**

- Single SDK dependency (no provider-specific SDKs)
- Consistent API across all providers
- Easy to add new providers (just config)
- Native OpenAI format (no conversion needed)

#### Agent Implementation (`agent/me.py`)

The `Me` class handles:

- LLM client initialization via dependency injection
- Document loading (LinkedIn PDF, summary)
- Tool execution in unified OpenAI format
- Conversation management with tool loop handling

**Clean implementation:**

```python
# All providers use identical interface
response = self.llm_client.chat_completion(messages, tools)
if response.choices[0].finish_reason == "tool_calls":
    # Handle tool calls uniformly
    self._handle_tool_calls(response.choices[0].message.tool_calls)
```

### Adding New Tools

1. **Define the tool handler** in `tools/handlers.py`:

   ```python
   def my_new_tool(param1: str, param2: int) -> Dict[str, str]:
       # Implementation
       return {"result": "success"}
   ```

2. **Add tool schema** in `tools/schemas.py`:

   ```python
   my_tool_json = {
       "name": "my_new_tool",
       "description": "What this tool does",
       "parameters": {
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "..."},
               "param2": {"type": "integer", "description": "..."}
           },
           "required": ["param1"],
           "additionalProperties": False
       }
   }

   tools.append({"type": "function", "function": my_tool_json})
   ```

3. **Register in the tool registry** in `tools/__init__.py`:

   ```python
   from tools.handlers import my_new_tool

   TOOL_REGISTRY = {
       # ... existing tools
       "my_new_tool": my_new_tool,
   }
   ```

### Best Practices Implemented

1. **OpenAI SDK Standard**: Industry-standard interface (2026)
2. **Configuration-Based Design**: Provider switching via config, not code
3. **Dependency Injection**: LLM client injected into agent
4. **Factory Pattern**: `create_llm_client()` for object creation
5. **Type Hints**: Comprehensive type annotations throughout
6. **Error Handling**: Graceful handling of API failures
7. **Tool Loop Protection**: Max iterations to prevent infinite loops
8. **Modular Architecture**: Clear separation of concerns

## Testing

```bash
# Test OpenAI integration
LLM_PROVIDER=openai python app.py

# Test Gemini integration
LLM_PROVIDER=gemini python app.py
```

## Troubleshooting

### Common Issues

**Issue: "API key not found"**

- Ensure your `.env` file exists and contains the correct API key
- Verify the key format matches the provider requirements

**Issue: "Module not found"**

- Run `pip install -e .` to install dependencies
- Ensure you're using Python 3.12+

**Issue: "Tool calls not working"**

- Verify tool schemas match the expected format
- Check tool registry includes all defined tools
- Ensure tool handlers return proper JSON-serializable dicts

**Issue: "Gemini format conversion errors"**

- No conversion needed! Gemini now supports OpenAI format natively
- Ensure you're using the correct base URL
- Verify API key has proper permissions

## Dependencies

- **gradio**: Web interface framework
- **openai**: Unified OpenAI SDK (supports multiple providers)
- **pypdf**: PDF processing
- **python-dotenv**: Environment variable management
- **requests**: HTTP library for notifications

## License

[Your License Here]

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure and style
4. Add tests for new functionality
5. Submit a pull request

## Future Enhancements

- [ ] Support for additional LLM providers (Anthropic Claude, Cohere)
- [ ] Streaming responses
- [ ] Conversation history persistence
- [ ] Enhanced error recovery
- [ ] Rate limiting and retry logic
- [ ] Model performance metrics
- [ ] A/B testing between providers

## Contact

For questions or support, please contact Muhammad Ibrahim Malik.
