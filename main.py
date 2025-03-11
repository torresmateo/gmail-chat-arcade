from openai import OpenAI
import streamlit as st
import dotenv
import os

dotenv.load_dotenv()
model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
api_key = os.environ.get("ARCADE_API_KEY")


def call_openai(client: OpenAI, history: list[dict], user: str):
    return client.chat.completions.create(
        messages=history,
        model="gpt-4o-mini",
        user=user,
        tools=[
            "Google.SendEmail", "Google.SendDraftEmail",
            "Google.WriteDraftEmail", "Google.UpdateDraftEmail",
            "Google.DeleteDraftEmail", "Google.TrashEmail",
            "Google.ListDraftEmails", "Google.ListEmailsByHeader",
            "Google.ListEmails", "Google.SearchThreads",
            "Google.ListThreads", "Google.GetThread",
        ],
        tool_choice="generate",
        stream=True,
    )


def reset_message_history():
    st.session_state.messages = []


client = OpenAI(
    api_key=os.environ["ARCADE_API_KEY"],
    base_url="https://api.arcade.dev/v1",
)


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

reset_message_history()

st.title("ChatGPT-like clone")

current_user = st.text_input("Email (change to reset chat)",
                             on_change=reset_message_history)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if current_user:
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            history = [{"role": m["role"], "content": m["content"]}
                       for m in st.session_state.messages]
            stream = call_openai(client, history, current_user)
            response = st.write_stream(stream)
        st.session_state.messages.append(
            {"role": "assistant", "content": response})
