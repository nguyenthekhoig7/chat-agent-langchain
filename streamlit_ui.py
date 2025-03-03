import streamlit as st
from backend_agent import AgentWithChatGPT

def display_history_messages(session_state):
    for message in session_state.messages:
        role = message['role']
        content = message['content']
        display_message(role, content)

def display_message(role, content):
    with st.chat_message(role):
            st.markdown(content)

def get_user_message():
    if prompt := st.chat_input("Hi what is your concern that I can help with?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message("user", prompt)

def get_agent_response(model_processor):
    
    role = 'expertnha'
    # user_message is the lastest user message in st.session_state.messages
    user_message = st.session_state.messages[-1]\
            if len(st.session_state.messages) > 0\
            else {"role": "user", "content": "Hello"}
    assert user_message['role'] == 'user'
    
    model_response = model_processor(user_message['content'])
    st.session_state.messages.append({"role": role, "content": model_response})
    display_message(role, model_response)

if __name__ == "__main__":
    agent = AgentWithChatGPT()

    st.title("Ask me anything.")

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    display_history_messages(st.session_state)

    get_user_message()  

    get_agent_response(agent.answer_static)

