from crewai.tools import BaseTool
from typing import Literal

class LLMReasoningTool(BaseTool):
    name: Literal["LLM Reasoning Tool"] = "LLM Reasoning Tool"
    description: Literal["Generates beliefs or inferences from provided observations or beliefs."] = "Generates beliefs or inferences from provided observations or beliefs."

    def _run(self, input_text: str) -> str:
        try:
            return f"Generated insight based on input: {input_text}"
        except Exception as e:
            return f"Error during reasoning: {e}"