import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': 'thread_1'}}

# -------------------------
# 1. Sync backend + frontend histories
# -------------------------
if 'message_history' not in st.session_state:
    # Try to fetch chat history from LangGraph state
    try:
        state = chatbot.get_state(config=CONFIG)
        # state may include "values" or "messages" depending on version
        # Adjusting to only keep user/assistant messages
        backend_messages = []
        if "messages" in state:   # sometimes returned as dict
            backend_messages = state["messages"]
        elif hasattr(state, "values") and "messages" in state.values:
            backend_messages = state.values["messages"]

        # Convert backend messages to our frontend format
        st.session_state['message_history'] = [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content}
            for m in backend_messages if m.type in ["human", "ai"]
        ]
    except Exception:
        st.session_state['message_history'] = []

# -------------------------
# 2. Replay conversation history in UI
# -------------------------
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        # Use markdown for richer formatting
        st.markdown(message['content'])

# -------------------------
# 3. Handle new user input
# -------------------------
user_input = st.chat_input('Type here')

if user_input:
    # Append user message to frontend state
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    # Send message to backend chatbot
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content

    # Append AI message to frontend state
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.markdown(ai_message)
