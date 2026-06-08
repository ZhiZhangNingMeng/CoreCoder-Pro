import streamlit as st
from corecoder.agent import Agent
from corecoder.llm import LLM, LiteLLM
from corecoder.config import Config
import builtins
import tkinter as tk
from tkinter import messagebox
from corecoder.session import save_session, load_session, list_sessions

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

    st.markdown("### 💾 Session Management")

    # 1. 保存当前会话
    if st.button("💾 Save Current Session", use_container_width=True):
        # 调用 session.py 原生的保存机制，只保存大模型的底层记忆
        session_id = save_session(agent.messages, config.model)

        # 为了让网页端也能完美恢复 UI，我们偷偷在这个原生目录下存一份 UI 专用的副本
        import json
        from corecoder.session import _session_path

        ui_path = str(_session_path(session_id)).replace(".json", "_ui.json")
        with open(ui_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.ui_messages, f, ensure_ascii=False)

        st.toast(f"Session saved: {session_id}", icon="✅")

    # 2. 列出并加载历史会话
    available_sessions = list_sessions()
    if available_sessions:
        # 将会话列表格式化为下拉菜单选项：时间 + 预览内容
        session_options = {
            f"{s['saved_at']} | {s['preview'][:20]}...": s['id']
            for s in available_sessions
        }

        selected_label = st.selectbox("Load previous session:", list(session_options.keys()))

        if st.button("📂 Load Selected", use_container_width=True):
            session_id = session_options[selected_label]
            loaded_data = load_session(session_id)

            if loaded_data:
                agent_msgs, loaded_model = loaded_data
                agent.messages = agent_msgs  # 恢复大模型记忆

                import os
                from corecoder.session import _session_path

                ui_path = str(_session_path(session_id)).replace(".json", "_ui.json")
                if os.path.exists(ui_path):
                    import json

                    with open(ui_path, "r", encoding="utf-8") as f:
                        st.session_state.ui_messages = json.load(f)
                else:
                    st.session_state.ui_messages = [
                        {"role": "assistant", "content": "Session loaded from CLI. Context restored.", "tools": []}]

                st.toast(f"Session {session_id} loaded!", icon="🎉")
                st.rerun()
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

    if user_input.startswith("/ingest "):
        filepath = user_input[8:].strip()

        with st.chat_message("assistant"):
            with st.spinner("⏳ Chunking and embedding into the vector database..."):
                from corecoder.rag_storage import ingest_document

                result_msg = ingest_document(filepath)

                # Friendly UI prompts
                if result_msg.startswith("Success"):
                    st.success(result_msg)
                else:
                    st.error(result_msg)

        # Save results to history to ensure they persist after page refresh
        st.session_state.ui_messages.append({
            "role": "assistant",
            "content": result_msg,
            "tools": []
        })
        st.stop()

    elif user_input.strip() == "/compact":
        with st.chat_message("assistant"):
            with st.spinner("⏳ Compacting LLM Context..."):
                # 调用 context.py 中的摘要机制
                compressed = agent.context._summarize_old(agent.messages, agent.llm, keep_recent=2)

                if compressed:
                    st.success(
                        "✅ Context successfully compacted! The AI has summarized the old history to save tokens.")
                else:
                    st.info("ℹ️ Context is too short to compact right now.")

        # 将提示信息加入 UI 历史
        st.session_state.ui_messages.append({
            "role": "assistant",
            "content": "✅ **Context Compacted:** Old conversation history has been summarized to save tokens.",
            "tools": []
        })
        st.stop()  # 刹车：执行完 /compact 也停下


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