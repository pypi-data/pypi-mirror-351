from typing import Dict, List
from content.state import ToolResult
from toolset.tool_setup import agent

_chat_history: List[Dict[str, str]] = []

def _format_chat_context(context: List[Dict[str, str]]) -> str:
    formatted = []
    for entry in context:
        role    = entry.get("role", "unknown").capitalize()
        content = entry.get("content", "")
        formatted.append(f"[{role}]: {content}")
    return "\n".join(formatted)

def run(inputs: Dict[str, str]) -> ToolResult:
    """
    Receives user text, builds the full prompt including history,
    sends it via urllib to the LLM API, and returns the response.
    """
    text = inputs.get("text", "")
    if not text:
        return {"response": "Error: No input text provided."}

    while text != "Q" and text != "q" and text != "quit" and text != "Quit":
        formatted_context = _format_chat_context(_chat_history)
        _chat_history.append({"role": "user", "content": text})
        
        full_prompt = (
            f"Recent Chat History:\n{formatted_context}\n\n"
#               f"knowledge: {knowledge}\n\n"
            f"Input: {text}\n\n"
            "Provide only a concise final answer that directly addresses the query."
        )
        data = agent.llm.chat(full_prompt)

        # 6) Extract reply
        reply = data.get("response") or data.get("content")
        if not reply:
            return {"response": "Error: Malformed API response"}
        print(f"<<<[A]: {reply}")
        # 7) Append reply to history and return
        _chat_history.append({"role": "assistant", "content": reply})
        # 8) ready for next input
        text = input("\nYou are now in chat mode, using q, Q, quit or Quit to exit chat mode.\n>>>[Q]: ")

    sumover_context = _format_chat_context(_chat_history)
    sumover_prompt = (
        f"Based on the chat history:\n{sumover_context}\n\n"
        "Please summarize the conversation in a concise manner, highlighting key points and conclusions.\n\n"
    )
    sumover = agent.llm.send_request(sumover_prompt)


    return  ToolResult(
        output=sumover,
        stop=False
    )
