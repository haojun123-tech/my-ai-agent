import streamlit as st
from research_agent import create_agent

st.set_page_config(page_title="Manus 研究型 Agent", page_icon="🤖")

st.title("🤖 Manus 研究型 Agent")
st.markdown("""
这是一个基于 **LangChain** 和 **GPT-4** 搭建的智能研究助手。
它具备联网搜索能力，可以回答关于最新时事、科学研究或任何需要实时信息的问题。
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 正在思考并搜索信息...")
        
        try:
            agent = create_agent()
            response = agent.invoke({"input": prompt})
            full_response = response["output"]
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            error_msg = f"抱歉，运行出错: {e}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
