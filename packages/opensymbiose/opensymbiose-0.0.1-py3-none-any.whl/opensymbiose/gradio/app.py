import logging
import time
from dataclasses import asdict

import gradio as gr
from gradio import ChatMessage
from mistralai import Mistral, ToolReferenceChunk

import opensymbiose.config
from opensymbiose.agents.create_agents import get_agents

logger = logging.getLogger(__name__)
client = Mistral(api_key=opensymbiose.config.MISTRAL_API_KEY)
model = "mistral-medium-latest"


def get_mistral_answer(message: str, history):
    # Start global execution timer
    global_start_time = time.time()

    # Dictionary to track tool execution times
    tool_timers = {}

    agents = get_agents()
    main_agent = agents["test_agent_tools"]
    stream_response = client.beta.conversations.start_stream(
        agent_id=main_agent.id, inputs=message, store=False
    )
    messages = []
    # Add an initial empty message for the assistant's response
    messages.append(asdict(ChatMessage(role="assistant", content="")))
    yield messages
    full_response = ""
    for chunk in stream_response:
        print(chunk)
        if chunk.event == "message.output.delta":
            if isinstance(chunk.data.content, str):
                full_response += chunk.data.content
            if isinstance(chunk.data.content, ToolReferenceChunk):
                full_response += f"([{chunk.data.content.title}]({chunk.data.content.url})) "
            # Update the last message with the current full response
            messages[-1] = asdict(ChatMessage(role="assistant", content=full_response))
            yield messages
        elif chunk.event == "tool.execution.started":
            # Start timer for this tool
            tool_timers[chunk.data.name] = time.time()
            # Add a new message for tool execution start
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"🛠️ Using tool {chunk.data.name}..."})))
            yield messages
        elif chunk.event == "tool.execution.done":
            # Calculate tool execution duration
            tool_duration = time.time() - tool_timers.get(chunk.data.name, time.time())
            # Add a new message for tool execution completion
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"🛠️ Finished using {chunk.data.name}.",
                                                         "duration": round(tool_duration, 2)})))
            # Add a new empty message for the continuing assistant response
            messages.append(asdict(ChatMessage(role="assistant", content=full_response)))
            yield messages
        elif chunk.event == "agent.handoff.started":
            # Start timer for agent handoff
            tool_timers["agent_handoff"] = time.time()
            # Add a new message for agent handoff start
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={
                                                   "title": f"🔄 Handing off from agent {chunk.data.previous_agent_name}..."})))
            yield messages
        elif chunk.event == "agent.handoff.done":
            # Calculate handoff duration
            handoff_duration = time.time() - tool_timers.get("agent_handoff", time.time())
            # Add a new message for agent handoff completion
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={
                                                   "title": f"✅ Handoff complete. Now using agent {chunk.data.next_agent_name}.",
                                                   "duration": round(handoff_duration, 2)})))
            # Add a new empty message for the continuing assistant response
            messages.append(asdict(ChatMessage(role="assistant", content=full_response)))
            yield messages
        elif chunk.event == "function.call.delta":
            # Start timer for function call
            function_start_time = time.time()
            # Add function call information to the response
            function_info = f"Calling function: {chunk.data.name} with arguments: {chunk.data.arguments}"
            # Store the function name for potential future duration calculation
            tool_timers[f"function_{chunk.data.name}"] = function_start_time
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"📞 {function_info}"})))
            yield messages
        elif chunk.event == "conversation.response.started":
            # Add a new message for conversation response start
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"🚀 Symbiose agent is starting...",
                                                         "log": f"{chunk.data.conversation_id}"})))
            yield messages
        elif chunk.event == "conversation.response.done":
            # Calculate global execution duration
            global_duration = time.time() - global_start_time
            # Add a new message for conversation response completion
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"✅ Conversation response complete.",
                                                         "log": f"Tokens: Prompt: {chunk.data.usage.prompt_tokens}, Completion: {chunk.data.usage.completion_tokens}, Total: {chunk.data.usage.total_tokens} Connectors: {chunk.data.usage.connector_tokens}",
                                                         "duration": round(global_duration, 2)})))
            yield messages
        elif chunk.event == "conversation.response.error":
            # Add a new message for conversation response error
            error_message = f"Error: {chunk.data.message} (Code: {chunk.data.code})"
            messages.append(asdict(ChatMessage(role="assistant", content="",
                                               metadata={"title": f"❌ {error_message}"})))
            yield messages
        else:
            # For other events, just update the last message
            messages[-1] = asdict(ChatMessage(role="assistant", content=full_response))
            yield messages


with gr.Blocks() as demo:
    gr.ChatInterface(
        fn=get_mistral_answer,
        type="messages",
        title="Open-Symbiose🧬",
        description="OpenSymbiose is an open-source biotechnology / biology research AI agent designed to support researcher",
        examples=["search internet: CEO of google", "Use your calculator agent to do 1273*3/12^2"],
        save_history=True,
        flagging_mode="manual"

    )

if __name__ == "__main__":
    demo.launch()
