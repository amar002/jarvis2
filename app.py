import streamlit as st
from datetime import datetime, time, timedelta
import json
import os
import openai
import random

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state to store user data
if "habits_data" not in st.session_state:
    st.session_state.habits_data = [
        {"name": "Drink 2L water", "due": "Today", "status": "Pending"},
        {"name": "Read 15 pages", "due": "Today", "status": "Pending"},
        {"name": "Walk 5000 steps", "due": "Tomorrow", "status": "Upcoming"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Utility functions for habit data
def load_habits():
    try:
        with open("data/habits_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_habits(habits_data):
    os.makedirs("data", exist_ok=True)
    with open("data/habits_data.json", "w") as file:
        json.dump(habits_data, file)

# Function to parse habit input without NLP dependencies
def parse_habit_input(habit_text):
    words = habit_text.split()
    habit_name = " ".join(words[:-2]) if len(words) > 2 else habit_text
    frequency = "daily" if "every" in words else "one-time"
    return {
        "habit_name": habit_name,
        "frequency": frequency
    }

# GPT Suggestions

def get_gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def display_chat():
    st.write("### Chat with HabitFlow")

    # Display chat history
    for message in st.session_state.chat_history:
        role, content = message
        if role == "user":
            st.write(f"**You**: {content}")
        else:
            st.write(f"**HabitFlow**: {content}")

    # User input for new messages
    user_input = st.text_input("Ask me anything about habits or suggestions:")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append(("user", user_input))
            gpt_response = get_gpt_response(user_input)
            st.session_state.chat_history.append(("assistant", gpt_response))
            st.experimental_rerun()
        else:
            st.error("Please enter a valid message.")

# Dashboard View
def display_dashboard(habits_data):
    st.write("### Habit Dashboard")
    for habit in habits_data:
        progress = 100 if habit["status"] == "Completed" else 0
        st.write(f"📝 {habit['name']} - Status: {habit['status']}")
        st.progress(progress / 100)
        if st.button("Mark as Done", key=habit["name"]):
            habit["status"] = "Completed"
            st.success(f"Completed: {habit['name']}")

# Reminder utils
def schedule_reminder(habit_name, reminder_time):
    current_time = datetime.now().time()
    if reminder_time > current_time:
        st.success(f"Reminder for '{habit_name}' set at {reminder_time}.")
    else:
        st.warning(f"Reminder time for '{habit_name}' is in the past! Please choose a future time.")

def display_reminder_options():
    st.write("### Set Reminder for a Habit")
    habit_name = st.selectbox("Select a Habit", [habit["name"] for habit in st.session_state.habits_data])
    reminder_time = st.time_input("Reminder Time", value=datetime.now().time())
    if st.button("Set Reminder"):
        schedule_reminder(habit_name, reminder_time)

# Main Streamlit App
st.title("HabitFlow")
st.subheader("Build small habits, achieve big goals.")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add Habits", "Suggestions", "Reminders"])

if menu == "Dashboard":
    display_dashboard(st.session_state.habits_data)
elif menu == "Add Habits":
    st.write("### Create Habit from Natural Language")
    habit_input = st.text_input("Describe your habit:")
    if st.button("Create Habit"):
        if habit_input.strip():
            parsed_habit = parse_habit_input(habit_input)
            st.session_state.habits_data.append({
                "name": parsed_habit["habit_name"],
                "due": parsed_habit["frequency"],
                "status": "Pending"
            })
            st.success(f"Habit '{parsed_habit['habit_name']}' added successfully!")
        else:
            st.error("Please enter a valid habit description.")
elif menu == "Suggestions":
    display_chat()
elif menu == "Reminders":
    display_reminder_options()

# Save data on app exit
save_habits(st.session_state.habits_data)

st.write("---")
st.write("Keep building small habits daily! 🚀")
