import streamlit as st
import json
from hashlib import sha256
import aws_main as aws
import azure_main as azure
import gemini_main as gemini
import ollama_main as ollama

# Define JSON file paths for user data, chat logs, and accuracy logs
USERS_FILE = 'users.json'
CHAT_LOGS_FILE = 'chat_logs.json'
ACCURACY_LOGS_FILE = 'accuracy_logs.json'

# Function to hash passwords for secure storage
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Load users from JSON file
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    return users

# Save users to JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Registration Page
def register_user(username, password):
    users = load_users()
    if username in users:
        return "Username already exists, please choose a unique username."
    else:
        users[username] = {'password': hash_password(password)}
        save_users(users)
        return "User registered successfully."

# Login Page
def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]['password'] == hash_password(password):
        return True
    return False

# Load chat logs from JSON file
def load_chat_logs():
    try:
        with open(CHAT_LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save chat logs to JSON file
def save_chat_logs(chat_logs):
    with open(CHAT_LOGS_FILE, 'w') as f:
        json.dump(chat_logs, f, indent=4)

# Load accuracy logs from JSON file
def load_accuracy_logs():
    try:
        with open(ACCURACY_LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save accuracy logs to JSON file
def save_accuracy_logs(accuracy_logs):
    with open(ACCURACY_LOGS_FILE, 'w') as f:
        json.dump(accuracy_logs, f, indent=4)

# Calculate accuracy based on response length or other metrics
def calculate_accuracy(response):
    return len(response)  # Example metric: response length

# Streamlit UI
st.set_page_config(page_title="Multi-Bot Chat", page_icon="🤖", layout="wide")

# Login/Register UI
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.title("Welcome to Multi-Bot Chat")
    st.markdown("### Please log in or register to continue.")

    choice = st.radio("Choose an option", ("Login", "Register"))

    if choice == "Register":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if password == confirm_password:
                st.success(register_user(username, password))
            else:
                st.error("Passwords do not match. Please try again.")
    elif choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# Main Chat Interface
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.sidebar.title("Configuration")
    temperature = st.sidebar.slider("Set Temperature", 0.0, 1.0, 0.7)

    st.title(f"Hi, {st.session_state.username}! Welcome to Multi-Bot Chat.")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Ask a question...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Collect responses from chatbots
        responses = {
            'AWS': aws.LLM_QnA_agent(prompt, temperature),
            'Azure': azure.LLM_QnA_agent(prompt, temperature),
            'Gemini': gemini.LLM_QnA_agent(prompt, temperature),
            'Ollama': ollama.LLM_QnA_agent(prompt, temperature),
        }

        # Calculate accuracy
        accuracies = {bot: calculate_accuracy(responses[bot]) for bot in responses}
        total_accuracy = sum(accuracies.values())
        percentages = {bot: (acc / total_accuracy) * 100 for bot, acc in accuracies.items()}
        best_bot = max(percentages, key=percentages.get)

        # Log response
        best_response = responses[best_bot]
        st.session_state.messages.append({"role": "assistant", "content": best_response})
        with st.chat_message("assistant"):
            st.markdown(f"**{best_response}**")
            st.markdown(f"*Provided by: {best_bot} ({percentages[best_bot]:.2f}% accuracy)*")

        # Save logs
        chat_logs = load_chat_logs()
        chat_logs.append({
            'user': st.session_state.username,
            'prompt': prompt,
            'response': best_response,
            'bot': best_bot,
            'accuracies': {bot: f"{percent:.2f}%" for bot, percent in percentages.items()},
        })
        save_chat_logs(chat_logs)

        accuracy_logs = load_accuracy_logs()
        accuracy_logs.append({
            'user': st.session_state.username,
            'prompt': prompt,
            'accuracies': {bot: f"{percent:.2f}%" for bot, percent in percentages.items()},
            'best_bot': best_bot,
        })
        save_accuracy_logs(accuracy_logs)

# Styling
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #243B55, #141E30);
            color: #FFFFFF;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stChatMessage {
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
        .stTextInput, .stButton {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)
