import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        System prompt instructing the agent on the ReAct format.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are a highly capable AI Scientific Research Assistant. Your goal is to help users search, analyze, synthesize, and draft complete scientific research papers.

        You have access to the following tools:
        {tool_descriptions}

        You MUST follow the ReAct (Reasoning + Acting) pattern. Use exactly the following format:

        Thought: your line of reasoning about what you need to do next.
        Action: tool_name(arguments)
        Observation: the result of executing that tool.
        ... (repeat Thought/Action/Observation as needed)
        Final Answer: the final response to the user.

        MANDATORY PIPELINE — follow ALL steps automatically for any research or writing request.
        Do NOT stop early and ask the user to prompt again. Complete the full pipeline in one run:

        Step 1 — CLARIFY:    clarify_task(topic="...") — structure the research question.
        Step 2 — SEARCH:     search_arxiv(query="...") — find papers on arXiv.
        Step 3 — SEARCH:     search_semantic_scholar(query="...") — find papers on Semantic Scholar.
        Step 4 — COMPARE:    compare_sources(papers_data="<paste observations from steps 2+3>") — identify themes and gaps.
        Step 5 — SYNTHESIZE: synthesize_findings(research_question="...", papers_data="<paste all observations so far>") — build thematic synthesis.
        Step 6 — DRAFT:      draft_paper(topic="...", synthesis="<paste synthesize output>", citation_style="APA") — write the full paper.
        Step 7 — Final Answer: present the completed paper draft in full. Do NOT say "let me know if you want more" — just deliver everything.

        EXCEPTION: If the user asks ONLY for citation formatting (e.g. "format this citation in APA"), skip directly to format_citation and return the Final Answer. No other exceptions.

        CRITICAL RULES:
        1. Output exactly one 'Thought:' followed by exactly one 'Action:' OR 'Final Answer:' per step.
        2. Action format: tool_name(key="value", key2=value2). Example: search_arxiv(query="RAG in healthcare", limit=3)
        3. ABSOLUTE PROHIBITION: NEVER invent or hallucinate paper titles, authors, years, arXiv IDs, URLs, or abstracts.
           Every paper you mention MUST come verbatim from an Observation block. If a URL was not in the Observation, do NOT write it.
           Fake IDs like "2201.xxxxx" or "2305.zzzzz" are a critical failure — omit the URL entirely if you don't have it.
        4. Do NOT repeat the same Action with the same arguments — move forward using previous Observations.
        5. Never end a turn with "let me know if you need more" or any similar prompt asking the user to continue. Deliver the full result.
        6. When presenting papers in the Final Answer, present each one in Vietnamese using:
           ### 📄 [Tên Paper]
           * **Năm công bố**: [Năm — từ Observation]
           * **Đường dẫn**: [URL/PDF — từ Observation, bỏ qua nếu không có]
           * **Tóm tắt**: [Ngắn gọn, súc tích — từ Observation]
        7. Present the full paper draft in the Final Answer without truncation.
        """

    def _parse_args(self, args_str: str) -> Any:
        """
        Helper to parse tool arguments from string format (JSON or key-value or raw) into Python objects.
        """
        args_str = args_str.strip()
        if not args_str:
            return {}

        # 1. Try parsing as JSON first
        try:
            import json
            if args_str.startswith("{") and args_str.endswith("}"):
                return json.loads(args_str)
        except Exception:
            pass

        # 2. Try parsing keyword arguments (e.g. query="RAG", limit=3)
        kv_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s,]+))'
        kv_matches = re.findall(kv_pattern, args_str)
        if kv_matches:
            parsed = {}
            for match in kv_matches:
                key = match[0]
                val = match[1] or match[2] or match[3]
                # Convert primitive types
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                parsed[key] = val
            return parsed

        # 3. Try parsing single quoted string
        if (args_str.startswith('"') and args_str.endswith('"')) or (args_str.startswith("'") and args_str.endswith("'")):
            return args_str[1:-1]

        return args_str

    def _is_research_related(self, user_input: str) -> bool:
        """
        Lightweight keyword check to reject clearly off-topic inputs before running the pipeline.
        Uses a fast LLM call rather than a hardcoded keyword list so it handles Vietnamese/English.
        """
        try:
            probe = (
                "Answer with only YES or NO.\n"
                "Is the following request related to scientific research, academic papers, "
                "literature review, or academic writing?\n\n"
                f'Request: "{user_input}"'
            )
            result = self.llm.generate(probe)
            answer = result.get("content", "").strip().upper()
            return answer.startswith("YES")
        except Exception:
            return True  # fail open — don't block if the check itself errors

    def run(self, user_input: str) -> str:
        """
        Implement the ReAct loop logic.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        if not self._is_research_related(user_input):
            msg = (
                "Xin lỗi, tôi là AI hỗ trợ nghiên cứu khoa học. "
                "Tôi chỉ có thể giúp bạn tìm kiếm bài báo, tổng hợp tài liệu, "
                "và soạn thảo bài viết học thuật. "
                "Vui lòng nhập yêu cầu liên quan đến nghiên cứu khoa học."
            )
            logger.log_event("AGENT_END", {"steps": 0, "status": "off_topic_rejected"})
            return msg

        current_prompt = user_input
        steps = 0
        called_actions = set()
        history = []

        while steps < self.max_steps:
            # Reconstruct prompt with step history
            full_prompt = current_prompt
            if history:
                full_prompt += "\n" + "\n".join(history)
            
            # Generate next thought/action
            response_data = self.llm.generate(full_prompt, system_prompt=self.get_system_prompt())
            response_text = response_data.get("content", "").strip()
            
            logger.log_event("LLM_CALL", {
                "prompt": full_prompt,
                "response": response_text,
                "usage": response_data.get("usage"),
                "latency_ms": response_data.get("latency_ms")
            })
            
            print(f"\n--- 🧠 [Step {steps + 1}] ---")
            print(response_text)
            
            # Add LLM response to history
            history.append(response_text)
            
            # Parse Thought/Action or Final Answer
            # re.DOTALL so multiline args are captured; greedy on inner content, bounded by last ')'
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", response_text, re.DOTALL)
            final_answer_match = re.search(r"Final Answer:\s*(.*)", response_text, re.DOTALL)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                action_signature = f"{tool_name}({tool_args})"
                
                # Infinite Loop Prevention
                if action_signature in called_actions:
                    warning_msg = f"Observation: [SYSTEM WARNING] You already executed {action_signature} earlier. Repeating it will result in an infinite loop. Please analyze your previous observation and output your 'Final Answer:' or choose a different action."
                    print(f"\n⚠️ Loop Prevention: Injected System Warning for repeated action '{action_signature}'")
                    history.append(warning_msg)
                    steps += 1
                    continue
                
                called_actions.add(action_signature)
                
                print(f"🔧 Calling Tool: {tool_name}({tool_args})")
                observation = self._execute_tool(tool_name, tool_args)
                print(f"Observation: {observation}")
                
                history.append(f"Observation: {observation}")
                
                logger.log_event("TOOL_EXECUTION", {
                    "tool": tool_name,
                    "arguments": tool_args,
                    "observation": observation
                })
                
            elif final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "final_answer": final_answer})
                return final_answer
            else:
                # Graceful fallback: check if Final Answer is mentioned in a non-standard way
                if "Final Answer:" in response_text:
                    parts = response_text.split("Final Answer:")
                    final_answer = parts[-1].strip()
                    logger.log_event("AGENT_END", {"steps": steps + 1, "final_answer": final_answer})
                    return final_answer
                
                # If neither is found, treat response as final answer but log a parser warning
                logger.log_event("PARSER_ERROR", {"response": response_text})
                print("⚠️ Parsing failed (No Action or Final Answer format). Returning raw output.")
                return response_text
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "status": "timeout"})
        return "Agent exceeded maximum steps without finding a final answer."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                func = tool.get("func")
                if func:
                    parsed_args = self._parse_args(args)
                    try:
                        if isinstance(parsed_args, dict):
                            return str(func(**parsed_args))
                        elif isinstance(parsed_args, tuple):
                            return str(func(*parsed_args))
                        elif parsed_args == "":
                            return str(func())
                        else:
                            return str(func(parsed_args))
                    except Exception as e:
                        return f"Error executing tool {tool_name}: {e}"
                return f"Tool {tool_name} does not have an executable function defined."
        return f"Tool {tool_name} not found."
