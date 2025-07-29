import streamlit as st
import argparse
from pygeai import logger
from pygeai.chat.session import AgentChatSession
from pygeai.core.utils.console import Console
import sys
import html


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Streamlit chat interface for pygeai agent")
    parser.add_argument("--agent-name", "-n", required=True, help="Name of the agent to interact with")
    args, unknown = parser.parse_known_args()  # Ignore Streamlit's args
    return args


def run_streamlit_chat():
    """Run a Streamlit chat interface for the specified agent."""
    args = parse_args()
    agent_name = args.agent_name
    try:
        chat_session = AgentChatSession(agent_name)

        # Initialize session state for messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Get agent introduction
            intro = chat_session.get_answer(
                ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                 "stating who you are and what you do. Nothing else."]
            )
            if "Agent not found" in str(intro):
                st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                return
            # Add introduction as a regular assistant message
            st.session_state.messages.append({"role": "assistant", "content": intro})

        # Set page title
        st.title(f"Chat with {agent_name}")

        # Reset chat button
        if st.button("Reset Chat"):
            st.session_state.messages = []
            # Re-fetch agent introduction
            intro = chat_session.get_answer(
                ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                 "stating who you are and what you do. Nothing else."]
            )
            if "Agent not found" in str(intro):
                st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                return
            st.session_state.messages.append({"role": "assistant", "content": intro})
            st.rerun()  # Refresh the app to reflect cleared history

        # Error container for empty input
        error_container = st.empty()

        # Display chat history with consistent styling
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                sanitized_content = message["content"]
                st.markdown(sanitized_content)

        # "Complete Answer" button logic (only show if the last message is from the assistant)
        if (st.session_state.messages and
            st.session_state.messages[-1]["role"] == "assistant" and
            "complete_answer_triggered" not in st.session_state):
            if st.button("Complete Answer"):
                st.session_state.complete_answer_triggered = True
                last_assistant_message = st.session_state.messages[-1]["content"]
                continuation_prompt = (
                    f"The previous answer was: '{last_assistant_message}'. "
                    "It seems incomplete. Please continue and complete the answer."
                )
                # Add a system/user message to request continuation
                st.session_state.messages.append({"role": "user", "content": continuation_prompt})
                # Display the continuation request
                with st.chat_message("user"):
                    st.markdown(continuation_prompt)
                # Stream the continued response
                with st.chat_message("assistant"):
                    with st.spinner("Continuing answer..."):
                        response_placeholder = st.empty()
                        continued_answer = ""
                        result = chat_session.stream_answer(st.session_state.messages)
                        for chunk in result:
                            continued_answer += chunk
                            sanitized_answer = continued_answer
                            response_placeholder.markdown(f'{sanitized_answer}')
                        # Append the continued answer as a new message
                        st.session_state.messages.append({"role": "assistant", "content": continued_answer})
                # Clear the trigger to allow future "Complete Answer" requests
                del st.session_state.complete_answer_triggered
                st.rerun()  # Refresh to update the UI

        # Chat input
        if user_input := st.chat_input(f"Ask {agent_name}"):
            # Check for empty or whitespace-only input
            if not user_input.strip():
                logger.warning(f"Empty input submitted for agent {agent_name}")
                with error_container.container():
                    st.error(f"Unable to communicate with the agent {agent_name}")
                return  # Exit early to prevent any further processing

            # Clear any previous error
            error_container.empty()
            # Display user message
            with st.chat_message("user"):
                sanitized_input = user_input
                st.markdown(f"{sanitized_input}")
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Get and stream agent response with spinner
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response_placeholder = st.empty()
                    answer = ""
                    result = chat_session.stream_answer(st.session_state.messages)
                    for chunk in result:
                        answer += chunk
                        sanitized_answer = answer
                        response_placeholder.markdown(f'{sanitized_answer}')
                    st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")
        Console.write_stderr("An unexpected error has occurred. Please contact the developers.")
        sys.exit(1)


if __name__ == "__main__":
    run_streamlit_chat()