"""
Chatbot Baseline — no tools, no ReAct loop.
Makes a single LLM call per query and returns the response directly.
Used as the control condition when comparing against the ReActAgent.
"""

import sys
from dotenv import load_dotenv

load_dotenv()

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

SYSTEM_PROMPT = """
You are an AI Scientific Research Assistant. Answer the user's academic research questions
as helpfully and accurately as possible based on your training knowledge.

Guidelines:
- Respond in the same language as the user (Vietnamese or English).
- For research queries, present information in structured, academic prose.
- If asked about specific papers, provide what you know but clearly note that you cannot
  verify real-time publication data, citation counts, or exact URLs.
- Do NOT fabricate specific arXiv IDs, DOIs, or URLs you are not certain about.
"""


class ResearchChatbot:
    """
    Baseline chatbot: one LLM call per user message, no tool use, no multi-step reasoning.
    Contrast with ReActAgent which uses Thought → Action → Observation loops.
    """

    def __init__(self, llm: LLMProvider = None):
        self.llm = llm or LLMProvider()

    def chat(self, user_input: str) -> str:
        if not user_input or not user_input.strip():
            return "Vui lòng nhập câu hỏi."

        logger.log_event("CHATBOT_CALL", {"input": user_input, "model": self.llm.model_name})

        response_data = self.llm.generate(user_input, system_prompt=SYSTEM_PROMPT)
        content = response_data.get("content", "").strip()

        logger.log_event("CHATBOT_RESPONSE", {
            "response": content,
            "usage": response_data.get("usage"),
            "latency_ms": response_data.get("latency_ms"),
        })

        return content


def main():
    print("=" * 60)
    print("💬 AI RESEARCH CHATBOT BASELINE (No Tools, No ReAct)")
    print("=" * 60)
    print("Đây là chatbot cơ bản — trả lời trực tiếp từ LLM, không dùng tools.")
    print("Gõ 'exit' để thoát.\n")

    try:
        chatbot = ResearchChatbot()
        print("✅ LLM khởi tạo thành công.\n")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        sys.exit(1)

    while True:
        try:
            query = input("🧑‍🎓 Câu hỏi > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye!")
                break

            print("\n🤖 Đang trả lời...")
            answer = chatbot.chat(query)
            print("\n" + "-" * 50)
            print(answer)
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
