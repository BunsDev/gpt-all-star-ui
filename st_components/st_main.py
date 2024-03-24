import ast

import streamlit as st
from gpt_all_star.core.message import Message
from gpt_all_star.core.steps.steps import StepType

from settings import settings


def st_main():
    if not st.session_state["chat_ready"]:
        introduction()
    else:
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                Message.create_human_message(
                    message="Hey there, What type of application would you like to build?",
                )
            ]

        for message in st.session_state.messages:
            process_message(message)

        step_type = StepType[st.session_state["step_type"]]
        steps = get_steps(step_type)

        if prompt := st.chat_input():
            user_message = Message.create_human_message(name="user", message=prompt)
            st.session_state.messages.append(user_message)
            process_message(user_message)

            if prompt.lower() in ["y", "n"]:
                if prompt == "y":
                    execute_application()
                else:
                    st.stop()
            else:
                for step in steps:
                    process_step(prompt, step)

                execute_message = Message.create_human_message(
                    message="Would you like to execute the application?(y/n)"
                )
                st.session_state.messages.append(execute_message)
                process_message(execute_message)


def get_steps(step_type: StepType):
    if step_type == StepType.NONE:
        return []
    elif step_type == StepType.DEFAULT:
        return [
            StepType.SPECIFICATION,
            StepType.SYSTEM_DESIGN,
            StepType.DEVELOPMENT,
            StepType.UI_DESIGN,
            StepType.ENTRYPOINT,
        ]
    else:
        return [step_type]


def process_step(prompt, step_type):
    step_message = Message.create_human_message(message=f"Next Step: **{step_type}**")
    st.session_state.messages.append(step_message)
    process_message(step_message)

    with st.spinner("Running..."):
        for chunk in st.session_state.gpt_all_star.chat(
            message=prompt,
            step=step_type,
            project_name=st.session_state["project_name"],
        ):
            if chunk.get("messages") and chunk.get("next") is None:
                for message in chunk.get("messages"):
                    st.session_state.messages.append(step_message)
                    process_message(message)

    if step_type is StepType.SPECIFICATION:
        display_markdown_file(
            f"projects/{st.session_state['project_name']}/docs/specifications.md"
        )
    elif step_type is StepType.SYSTEM_DESIGN:
        display_markdown_file(
            f"projects/{st.session_state['project_name']}/docs/technologies.md"
        )


def execute_application():
    step_message = Message.create_human_message(message="Next Step: **execution**")
    st.session_state.messages.append(step_message)
    process_message(step_message)

    with st.spinner("Running..."):
        for chunk in st.session_state.gpt_all_star.execute(
            project_name=st.session_state["project_name"]
        ):
            if chunk.get("messages") and chunk.get("next") is None:
                for message in chunk.get("messages"):
                    process_message(message)


def process_message(message):
    if message.name in [setting["name"] for setting in settings]:
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
    elif message.name is not None:
        with st.chat_message(message.name):
            st.markdown(message.content, unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            if "URL:" in message.content:
                url = message.content.split("URL:")[1].strip()
                st.markdown(
                    f'<iframe src="{url}" width="800" height="600" style="border: 2px solid #ccc;"></iframe>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(message.content, unsafe_allow_html=True)


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
