import streamlit as st
import argparse
import json
import os
from datetime import datetime
from pygeai import logger
from pygeai.chat.session import AgentChatSession
from pygeai.core.utils.console import Console
from pygeai.core.common.config import get_settings
from pygeai.lab.managers import AILabManager
from pygeai.lab.models import FilterSettings, AgentList
import sys


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Streamlit chat interface for pygeai agent")
    parser.add_argument("--agent-name", "-n", required=True, help="Name of the agent to interact with")
    args, unknown = parser.parse_known_args()  # Ignore Streamlit's args
    return args


def save_session_to_file(messages, file_path):
    """Helper function to save session to a server-side file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(messages, f, indent=2)
        logger.info(f"Session automatically saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving session to {file_path}: {e}")
        st.error(f"Failed to auto-save session: {e}")
        return False


def get_unique_file_path(base_path):
    """Generate a unique file path by appending a numeric suffix if the file exists."""
    if not os.path.exists(base_path):
        return base_path

    directory, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)
    counter = 1

    new_path = base_path
    while os.path.exists(new_path):
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(directory, new_filename)
        counter += 1

    return new_path


def get_session_file_path(agent_name, custom_filename=None):
    """Generate the session file path with date and agent name, or use a custom filename."""
    if custom_filename:
        if not custom_filename.endswith('.json'):
            custom_filename += '.json'
        return os.path.join("chats", custom_filename)
    current_date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join("chats", f"chat_session_{agent_name}_{current_date}.json")


def list_session_files():
    """List all JSON files in the 'chats' directory."""
    chats_dir = "chats"
    if not os.path.exists(chats_dir):
        return []
    try:
        return [f for f in os.listdir(chats_dir) if f.endswith('.json')]
    except Exception as e:
        logger.error(f"Error listing session files in {chats_dir}: {e}")
        return []


def load_session_from_file(file_path):
    """Load session data from a specified file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data, True
            else:
                return None, False
    except Exception as e:
        logger.error(f"Error loading session from {file_path}: {e}")
        return None, False


def delete_session_file(file_path):
    """Helper function to delete a session file from the file system."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Session file deleted: {file_path}")
            return True, f"Session file {os.path.basename(file_path)} deleted successfully."
        else:
            logger.warning(f"Session file not found: {file_path}")
            return False, f"Session file {os.path.basename(file_path)} not found."
    except Exception as e:
        logger.error(f"Error deleting session file {file_path}: {e}")
        return False, f"Error deleting session file {os.path.basename(file_path)}: {str(e)}"


def get_alias_list():
    """Get list of available aliases from settings."""
    try:
        settings = get_settings()
        aliases = list(settings.list_aliases().keys())
        return ["-"] + aliases  # Add "-" as default no-selection option
    except Exception as e:
        logger.error(f"Error fetching alias list: {e}")
        st.error(f"Failed to fetch alias list: {e}")
        return ["-"]


def get_agent_list(alias, project_id):
    """Get list of agents for a given alias and project ID."""
    try:
        if alias == "-" or not project_id:
            return ["-"]
        ai_lab_manager = AILabManager(alias=alias)
        filter_settings = FilterSettings(
            allow_external=False,
            allow_drafts=True,
            access_scope="private"
        )
        result = ai_lab_manager.get_agent_list(
            project_id=project_id,
            filter_settings=filter_settings
        )
        if isinstance(result, AgentList) and result.agents:
            return ["-"] + [f"{agent.name} (ID: {agent.id})" for agent in result.agents]
        else:
            st.error(f"No agents found for project ID {project_id} or errors occurred: {result.errors if hasattr(result, 'errors') else 'Unknown error'}")
            return ["-"]
    except Exception as e:
        logger.error(f"Error fetching agents for project ID {project_id} with alias {alias}: {e}")
        st.error(f"Failed to fetch agents for project: {e}")
        return ["-"]


def run_streamlit_chat():
    """Run a Streamlit chat interface for the specified agent."""
    args = parse_args()
    initial_agent_name = args.agent_name
    try:
        # Initialize current agent session
        if "current_agent_name" not in st.session_state:
            st.session_state.current_agent_name = initial_agent_name
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = AgentChatSession(st.session_state.current_agent_name)

        # Define the default server-side file path for auto-saving with date
        if "custom_filename" not in st.session_state:
            st.session_state.custom_filename = ""
        SESSION_FILE_PATH = get_session_file_path(st.session_state.current_agent_name, st.session_state.custom_filename)

        # Initialize session state for messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
            if os.path.exists(SESSION_FILE_PATH):
                try:
                    with open(SESSION_FILE_PATH, 'r') as f:
                        restored_data = json.load(f)
                        if isinstance(restored_data, list):
                            st.session_state.messages = restored_data
                            st.success(f"Session automatically restored from {SESSION_FILE_PATH}")
                        else:
                            logger.warning(f"Invalid session data in {SESSION_FILE_PATH}. Starting fresh.")
                            intro = st.session_state.chat_session.get_answer(
                                ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                                 "stating who you are and what you do. Nothing else."]
                            )
                            if "Agent not found" in str(intro):
                                st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                                logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                                return
                            st.session_state.messages.append({"role": "assistant", "content": intro})
                except Exception as e:
                    logger.error(f"Error auto-restoring session from {SESSION_FILE_PATH}: {e}")
                    intro = st.session_state.chat_session.get_answer(
                        ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                         "stating who you are and what you do. Nothing else."]
                    )
                    if "Agent not found" in str(intro):
                        st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                        logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                        return
                    st.session_state.messages.append({"role": "assistant", "content": intro})
            else:
                intro = st.session_state.chat_session.get_answer(
                    ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                     "stating who you are and what you do. Nothing else."]
                )
                if "Agent not found" in str(intro):
                    st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                    logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                    return
                st.session_state.messages.append({"role": "assistant", "content": intro})
                save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                st.rerun()

        # Set page title
        st.title(f"Chat with {st.session_state.current_agent_name}")

        # Display the session save path in the main area for better readability
        st.info(f"Session will be saved as: {SESSION_FILE_PATH}", icon="ℹ️")

        # Sidebar for session management and agent selection
        with st.sidebar:
            st.header("Session Management")

            with st.expander("Help: Session Saving & Restoring", expanded=False):
                st.markdown("""
                **Session Saving & Restoring Explained:**
                - **Auto-Save Session**: When toggled on, your chat history is automatically saved to a server-side file in the 'chats' directory (e.g., `chats/chat_session_{agent_name}_YYYY-MM-DD.json`) after each message or action. This ensures your session persists across app restarts or browser closures.
                - **Custom Session Filename**: Enter a custom name for the session file to save it with a specific identifier instead of the default name.
                - **Save Session (JSON)**: Click this button to download a local copy of your chat history to your machine (typically to your 'Downloads' folder). This is useful for backups or transferring sessions.
                - **Restore Session (JSON)**: Upload a previously saved JSON file to load a specific chat history. This overwrites the current session.
                - **Available Sessions**: Below, you can see a list of saved session files in the 'chats' directory. Click any file to load that session into the current chat.
                - **Reset Chat**: Clears the current session and starts fresh with the agent's introduction.
                """)

            # Custom filename input without displaying the info message in the sidebar
            custom_filename = st.text_input("Custom Session Filename (optional)", value=st.session_state.custom_filename, placeholder="e.g., my_custom_session")
            if custom_filename != st.session_state.custom_filename:
                st.session_state.custom_filename = custom_filename
                SESSION_FILE_PATH = get_session_file_path(st.session_state.current_agent_name, custom_filename)
                if st.session_state.messages:
                    save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                    st.rerun()

            uploaded_file = st.file_uploader("Restore Session (JSON)", type=["json"])
            if uploaded_file is not None and "session_restored" not in st.session_state:
                try:
                    restored_data = json.load(uploaded_file)
                    if isinstance(restored_data, list):
                        st.session_state.messages = restored_data
                        st.session_state.session_restored = True
                        save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                        st.success(f"Session restored from {uploaded_file.name}")
                        st.rerun()
                    else:
                        st.error("Invalid session file: Must contain a list of messages in JSON format.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in uploaded file.")
                except Exception as e:
                    st.error(f"Error restoring session: {e}")
                    logger.error(f"Error restoring session: {e}")

            if st.session_state.messages:
                session_json = json.dumps(st.session_state.messages, indent=2)
                current_date = datetime.now().strftime("%Y-%m-%d")
                st.download_button(
                    label="Save Session (JSON)",
                    data=session_json,
                    file_name=f"chat_session_{st.session_state.current_agent_name}_{current_date}.json",
                    mime="application/json"
                )

            auto_save = st.toggle("Auto-Save Session", value=True)

            # Available Sessions with Delete Option
            st.subheader("Available Sessions")
            session_files = list_session_files()
            feedback_placeholder = st.empty()  # Placeholder for feedback messages outside columns
            if session_files:
                st.markdown("Click a file to load the session, or use the trash icon to delete:")
                for file in session_files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(file, key=f"load_{file}", use_container_width=True):
                            file_path = os.path.join("chats", file)
                            loaded_data, success = load_session_from_file(file_path)
                            if success:
                                st.session_state.messages = loaded_data
                                st.success(f"Session loaded from {file}")
                                if auto_save:
                                    save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                                st.rerun()
                            else:
                                st.error(f"Failed to load session from {file}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{file}", help=f"Delete {file}"):
                            file_path = os.path.join("chats", file)
                            if os.path.abspath(file_path) == os.path.abspath(SESSION_FILE_PATH):
                                with feedback_placeholder.container():
                                    st.markdown("---")
                                    st.error("Cannot delete the currently active session file. Please switch to another session or reset the chat first.", icon="🚫")
                                    st.markdown("---")
                            else:
                                try:
                                    os.remove(file_path)
                                    logger.info(f"Deleted session file: {file_path}")
                                    with feedback_placeholder.container():
                                        st.markdown("---")
                                        st.success(f"Deleted {file}", icon="✅")
                                        st.markdown("---")
                                    st.rerun()
                                except Exception as e:
                                    logger.error(f"Error deleting session file {file_path}: {e}")
                                    with feedback_placeholder.container():
                                        st.markdown("---")
                                        st.error(f"Failed to delete {file}: {e}", icon="❌")
                                        st.markdown("---")
            else:
                st.markdown("No saved sessions found in 'chats' directory.")

            # New Feature: Agent Selection
            st.header("Switch Agent")
            with st.expander("Help: Switching Agents", expanded=False):
                st.markdown("""
                **Switching Agents Explained:**
                - **Select Alias**: Choose a profile (alias) to access specific API configurations.
                - **Enter Project ID**: Provide the ID of the project to list available agents.
                - **Select Agent**: Pick an agent to chat with. You'll be prompted to confirm before switching.
                - Switching to a new agent starts a fresh session.
                """)

            # Initialize session state for alias, project ID, and agent selection
            if "selected_alias" not in st.session_state:
                st.session_state.selected_alias = "-"
            if "project_id_input" not in st.session_state:
                st.session_state.project_id_input = ""
            if "selected_agent" not in st.session_state:
                st.session_state.selected_agent = "-"
            if "confirm_switch" not in st.session_state:
                st.session_state.confirm_switch = False

            # Alias Selection
            alias_list = get_alias_list()
            selected_alias = st.selectbox("Select Alias (Profile)", alias_list, index=alias_list.index(st.session_state.selected_alias))
            if selected_alias != st.session_state.selected_alias:
                st.session_state.selected_alias = selected_alias
                st.session_state.selected_agent = "-"
                st.rerun()

            # Project ID Input
            project_id_input = st.text_input("Enter Project ID", value=st.session_state.project_id_input, placeholder="e.g., 2ca6883f-6778-40bb-bcc1-85451fb11107")
            if project_id_input != st.session_state.project_id_input:
                st.session_state.project_id_input = project_id_input
                st.session_state.selected_agent = "-"
                st.rerun()

            # Agent Selection
            agent_list = get_agent_list(st.session_state.selected_alias, st.session_state.project_id_input) if st.session_state.selected_alias != "-" and st.session_state.project_id_input else ["-"]
            selected_agent = st.selectbox("Select Agent", agent_list, index=agent_list.index(st.session_state.selected_agent) if st.session_state.selected_agent in agent_list else 0)
            if selected_agent != st.session_state.selected_agent:
                st.session_state.selected_agent = selected_agent
                st.session_state.confirm_switch = False

            # Confirmation for switching agent
            if st.session_state.selected_agent != "-" and st.session_state.selected_agent.split(" (ID: ")[0] != st.session_state.current_agent_name:
                if not st.session_state.confirm_switch:
                    st.warning(f"Do you wish to chat with {st.session_state.selected_agent.split(' (ID: ')[0]}? This will start a new session.", icon="⚠️")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Switch"):
                            st.session_state.confirm_switch = True
                            # Extract agent name from selected agent string
                            new_agent_name = st.session_state.selected_agent.split(" (ID: ")[0]
                            st.session_state.current_agent_name = new_agent_name
                            st.session_state.chat_session = AgentChatSession(new_agent_name)
                            st.session_state.messages = []
                            intro = st.session_state.chat_session.get_answer(
                                ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                                 "stating who you are and what you do. Nothing else."]
                            )
                            if "Agent not found" in str(intro):
                                st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                                logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                                return
                            st.session_state.messages.append({"role": "assistant", "content": intro})
                            SESSION_FILE_PATH = get_session_file_path(st.session_state.current_agent_name, st.session_state.custom_filename)
                            if auto_save:
                                save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                            st.rerun()
                    with col2:
                        if st.button("Cancel"):
                            st.session_state.selected_agent = "-"
                            st.session_state.confirm_switch = False
                            st.rerun()
                else:
                    st.success(f"Switched to agent {st.session_state.selected_agent.split(' (ID: ')[0]}!", icon="✅")

        # Reset chat button
        if st.button("Reset Chat"):
            st.session_state.messages = []
            intro = st.session_state.chat_session.get_answer(
                ["You're about to speak to a user. Introduce yourself in a clear and concise manner, "
                 "stating who you are and what you do. Nothing else."]
            )
            if "Agent not found" in str(intro):
                st.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                logger.error("The specified agent doesn't seem to exist. Please review the name and try again.")
                return
            st.session_state.messages.append({"role": "assistant", "content": intro})
            if auto_save:
                save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
            st.rerun()

        error_container = st.empty()

        # Display chat history with consistent styling
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                sanitized_content = message["content"]
                st.markdown(sanitized_content)

        # "Complete Answer" button logic
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
                st.session_state.messages.append({"role": "user", "content": continuation_prompt})
                with st.chat_message("user"):
                    st.markdown(continuation_prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Continuing answer..."):
                        response_placeholder = st.empty()
                        continued_answer = ""
                        result = st.session_state.chat_session.stream_answer(st.session_state.messages)
                        for chunk in result:
                            continued_answer += chunk
                            sanitized_answer = continued_answer
                            response_placeholder.markdown(f'{sanitized_answer}')
                        st.session_state.messages.append({"role": "assistant", "content": continued_answer})
                if auto_save:
                    save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                del st.session_state.complete_answer_triggered
                st.rerun()

        # Chat input
        if user_input := st.chat_input(f"Ask {st.session_state.current_agent_name}"):
            if not user_input.strip():
                logger.warning(f"Empty input submitted for agent {st.session_state.current_agent_name}")
                with error_container.container():
                    st.error(f"Unable to communicate with the agent {st.session_state.current_agent_name}")
                return
            error_container.empty()
            with st.chat_message("user"):
                sanitized_input = user_input
                st.markdown(f"{sanitized_input}")
            st.session_state.messages.append({"role": "user", "content": user_input})

            if auto_save:
                save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)

            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response_placeholder = st.empty()
                    answer = ""
                    result = st.session_state.chat_session.stream_answer(st.session_state.messages)
                    for chunk in result:
                        answer += chunk
                        sanitized_answer = answer
                        response_placeholder.markdown(f'{sanitized_answer}')
                    st.session_state.messages.append({"role": "assistant", "content": answer})

            if auto_save:
                save_session_to_file(st.session_state.messages, SESSION_FILE_PATH)
                st.rerun()

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")
        Console.write_stderr("An unexpected error has occurred. Please contact the developers.")
        sys.exit(1)


if __name__ == "__main__":
    run_streamlit_chat()