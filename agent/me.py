from pypdf import PdfReader
from typing import List, Dict, Any
import json

from config.settings import DATA_DIR, LLM_PROVIDER
from tools import TOOL_REGISTRY
from tools.schemas import tools
from agent.prompt import build_system_prompt
from agent.llm_client import create_llm_client


class Me:
    def __init__(self, llm_provider: str = LLM_PROVIDER) -> None:
        self.llm_client = create_llm_client(llm_provider)
        self.name = "Muhammad Ibrahim Malik"

        self.linkedin = self._load_linkedin()
        self.summary = self._load_summary()

        self.system_prompt = build_system_prompt(
            self.name,
            self.summary,
            self.linkedin,
        )

    def _load_linkedin(self) -> str:
        reader = PdfReader(DATA_DIR / "Muhammad_Ibrahim_Frontend_AI_Profile.pdf")
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _load_summary(self) -> str:
        return (DATA_DIR / "summary.txt").read_text(encoding="utf-8")

    def _handle_tool_calls(
        self, tool_calls: List[Any]
    ) -> List[Dict[str, Any]]:
        """Handle tool calls in unified OpenAI format."""
        results = []

        for call in tool_calls:
            tool = TOOL_REGISTRY.get(call.function.name)
            if not tool:
                continue

            args = json.loads(call.function.arguments)
            output = tool(**args)

            results.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(output),
            })

        return results

    def chat(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Handle chat interaction with tool calling support.
        Uses unified OpenAI SDK format for all providers.
        """
        messages = (
            [{"role": "system", "content": self.system_prompt}]
            + history
            + [{"role": "user", "content": message}]
        )

        for _ in range(5):  
            response = self.llm_client.chat_completion(
                messages=messages,
                tools=tools,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                assistant_msg = choice.message

                messages.append({
                    "role": "assistant",
                    "content": assistant_msg.content,
                    "tool_calls": assistant_msg.tool_calls,
                })

                tool_results = self._handle_tool_calls(assistant_msg.tool_calls)
                messages.extend(tool_results)

            else:
                return choice.message.content

        raise RuntimeError("Tool loop exceeded max iterations")
