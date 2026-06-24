import streamlit as st
import requests
import json

st.set_page_config(page_title="Crypto Accounting AI Assistant", layout="wide")

st.title("Adarsh's Crypto AI Assistant")

# -----------------------------
# CONFIG
# -----------------------------
MODEL = "mistral"
MAX_HISTORY = 5  # sliding window size

SYSTEM_PROMPT = """
You are a crypto fund accountant.

Rules:
- Be precise and structured
- Do not guess if unsure
- Explain step-by-step
- Focus on accounting accuracy (FIFO, PnL, NAV, fees)
"""

# -----------------------------
# INIT SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# DISPLAY CHAT
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------
user_input = st.chat_input("Ask something about crypto/accounting...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # -----------------------------
    # BUILD CONTEXT (Sliding Window)
    # -----------------------------
    recent_messages = st.session_state.messages[-MAX_HISTORY:]

    conversation = ""
    for msg in recent_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n"

    # Final prompt with structure
    final_prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{conversation}

Assistant:
"""

    # -----------------------------
    # CALL OLLAMA
    # -----------------------------
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": final_prompt,
                "stream": True
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode())
                token = data.get("response", "")
                full_response += token
                response_placeholder.markdown(full_response)

    # Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.title("Controls")

if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []