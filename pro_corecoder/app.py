import streamlit as st
from corecoder.agent import Agent
from corecoder.llm import LLM, LiteLLM
from corecoder.config import Config
import builtins
import tkinter as tk
from tkinter import messagebox


def manual_review_input(prompt=""):
    """Intercept native input, pop up a top-level visual review window"""
    # Initialize a hidden main window
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)  # Force top-level to prevent being covered by the browser
    root.withdraw()  # Hide the main window

    # Pop up the OS native Yes/No confirmation box
    # messagebox.askyesno perfectly blocks the program, waiting for your click
    is_approved = messagebox.askyesno(
        title="⚠️ CoreCoder Security Review",
        message=f"Agent is requesting dangerous operation permissions, please review:\n\n{prompt}"
    )

    root.destroy()  # Destroy window after click to release resources

    # Map the click result to 'y' or 'n' required by underlying code
    return "y" if is_approved else "n"


# Inject patch: turn all input() in underlying tools into this popup
builtins.input = manual_review_input

# ==========================================
# 1. Page configuration and global styles
# ==========================================
st.set_page_config(
    page_title="CoreCoder Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. State management (Session State initialization)
# ==========================================
if "agent" not in st.session_state:
    config = Config.from_env()

    if not config.api_key:
        st.error("API Key not found. Please set CORECODER_API_KEY or related environment variables in the .env file.")
        st.stop()

    llm_cls = LiteLLM if config.provider == "litellm" else LLM
    llm = llm_cls(
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    st.session_state.agent = Agent(llm=llm, max_context_tokens=config.max_context_tokens)
    st.session_state.config = config
    st.session_state.ui_messages = [
        {"role": "assistant", "content": "Hello! I am CoreCoder Pro, your exclusive minimal AI assistant. How can I help you today?",
         "tools": []}]

agent = st.session_state.agent
config = st.session_state.config

# ==========================================
# 3. Sidebar configuration
# ==========================================
with st.sidebar:
    st.title("🤖 CoreCoder Pro")
    st.caption("Minimal open-source Agent framework")
    st.divider()
    st.markdown("### ⚙️ Current Configuration")
    st.info(f"**Model:** `{config.model}`")
    if config.base_url:
        st.caption(f"**Base URL:** {config.base_url}")

    st.divider()
    if st.button("🧹 Clear chat history (/reset)", use_container_width=True):
        agent.reset()
        st.session_state.ui_messages = [
            {"role": "assistant", "content": "Conversation reset. We can start a new topic!", "tools": []}]
        st.rerun()

# ==========================================
# 4. Main chat stream rendering (Render history)
# ==========================================
for msg in st.session_state.ui_messages:
    with st.chat_message(msg["role"]):
        for tool in msg.get("tools", []):
            with st.expander(f"✅ Tool `{tool['name']}` executed successfully"):
                st.write("**Parameters:**")
                st.json(tool["args"])
        if msg.get("content"):
            st.markdown(msg["content"])

# ==========================================
# 5. User input and interactive stream processing
# ==========================================
if user_input := st.chat_input("Example: Write a Python script to analyze stock data..."):

    st.session_state.ui_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        tool_container = st.container()
        text_placeholder = st.empty()

        current_tools_used = []
        # Use a list container to store streamed text, bypassing Python's global variable reassignment scope limits
        streamed_text_container = [""]


        # --- Define core callback functions ---
        def on_token(token: str):
            """Handle streamed text output, implementing a typewriter effect"""
            streamed_text_container[0] += token
            text_placeholder.markdown(streamed_text_container[0] + " ▌")


        def on_tool(name: str, kwargs: dict):
            """Handle tool calls, using st.status for dynamic prompt boxes"""
            current_tools_used.append({"name": name, "args": kwargs})
            with tool_container:
                with st.status(f"🛠️ Executing tool: `{name}` ...", expanded=True) as status:
                    st.write("**Parameters:**")
                    st.json(kwargs)
                    status.update(label=f"✅ Tool `{name}` executed successfully", state="complete", expanded=False)


        try:
            # Capture the Agent's final complete return text
            final_response = agent.chat(user_input, on_token=on_token, on_tool=on_tool)

            text_placeholder.markdown(final_response)

            st.session_state.ui_messages.append({
                "role": "assistant",
                "content": final_response,
                "tools": current_tools_used
            })

        except Exception as e:
            st.error(f"Agent execution error: {str(e)}")