import openai
from openai import OpenAI
import streamlit as st
import time
import pyttsx3


# TTS 기능
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

assistant_id ="asst_j1lz0Uh3lGWdBvnT9RmFojur"

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "Get an OpenAI API key: [https://platform.openai.com/account/api-keys]"

    client = OpenAI(api_key=openai_api_key)
    
    thread_id = st.text_input("Thread ID")

    thread_btn = st.button("Create a new thread")

    if thread_btn:
        thread = client.beta.threads.create()
        thread_id = thread.id

        st.subheader(f"{thread_id}", divider="rainbow")
        st.info("스레드가 생성되었습니다.")

uploaded_file = st.file_uploader("파일을 업로드하세요.", type=['txt','docx'])
if uploaded_file is not None:
    file_details = client.files.create(
        file=uploaded_file,
        purpose="assistants"  # 또는 "fine-tune"
    )
    st.write(file_details) 

st.title("💬 Career Buddy")
st.caption("🚀 Career Buddy ChatBot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "무엇을 도와드릴까요?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt:=st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    if not thread_id:
        st.info("Please add your thread ID to continue.")
        st.stop()

# 업로드된 파일의 내용을 가져와서 OpenAI API로 전송
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            file_content = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/msword" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(uploaded_file)
            file_content = "\n".join([para.text for para in doc.paragraphs])


        response = client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=file_content,
        )        

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=prompt,
        )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
        )

    run_id = run.id

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
            )
        if run.status == "completed":
            break
        else:
            time.sleep(2)

    thread_messages = client.beta.threads.messages.list(thread_id)

    msg = thread_messages.data[0].content[0].text.value
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    text_to_speech(msg)  # 챗봇의 대답을 음성으로 변환하여 재생