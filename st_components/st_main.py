import ast

import streamlit as st
from gpt_all_star.core.steps.steps import StepType

from settings import settings


def st_main():
    if not st.session_state["chat_ready"]:
        introduction()
    else:
        handle_chat_interaction()


def handle_chat_interaction():
    prompt = st.chat_input()
    if prompt:
        st.session_state.messages.append({"name": "user", "content": prompt})

    display_messages()

    if prompt:
        process_prompt(prompt, StepType.SPECIFICATION, "specifications.md")
        process_prompt(None, StepType.SYSTEM_DESIGN, "technologies.md")
        process_prompt(None, StepType.DEVELOPMENT, None)
        process_prompt(None, StepType.UI_DESIGN, None)
        process_prompt(None, StepType.ENTRYPOINT, None)


def process_prompt(prompt, step_type, markdown_file):
    with st.chat_message("assistant"):
        st.markdown(f"Next Step: **{step_type}**")
    for chunk in st.session_state.gpt_all_star.chat(
        message=prompt,
        step=step_type,
        project_name=st.session_state["project_name"],
    ):
        if chunk.get("messages") and chunk.get("next") is None:
            for message in chunk.get("messages"):
                process_message(message)

    if markdown_file:
        display_markdown_file(
            f"projects/{st.session_state['project_name']}/docs/{markdown_file}"
        )


def process_message(message):
    if message.name is not None:
        setting = next((s for s in settings if s["name"] == message.name), None)
        with st.chat_message(message.name, avatar=setting["avatar_url"]):
            try:
                content_data = ast.literal_eval(message.content)
                st.write(f"{message.name} is working...")
                st.info("TODO LIST", icon="ℹ️")
                st.json(content_data, expanded=False)
            except (SyntaxError, ValueError):
                st.write(f"{message.name} is working...")
                st.markdown(message.content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message.content)


def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["name"]):
            st.markdown(message["content"])


def load_markdown_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def display_markdown_file(path):
    md_content = load_markdown_file(path)
    with st.chat_message("assistant"):
        st.info("OUTPUT", icon="ℹ️")
        st.markdown(md_content, unsafe_allow_html=True)


def introduction():
    """
    Introduction:
    Display introductory messages for the user.
    """
    st.info("Hey, we're very happy to see you here.", icon="👋")
    st.info("Set API Key, to be able to build your application.", icon="👉️")
