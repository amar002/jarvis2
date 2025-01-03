import streamlit as st
from datetime import datetime, time, timedelta
import json
import random

# Initialize session state to store user data
if "habits_data" not in st.session_state:
    st.session_state.habits_data = [
        {"name": "Drink 2L water", "due": "Today", "status": "Pending"},
        {"name": "Read 15 pages", "due": "Today", "status": "Pending"},
        {"name": "Walk 5000 steps", "due": "Tomorrow", "status": "Upcoming"}
    ]

# Utility functions for habit data
def load_habits():
    try:
        with open("data/habits_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_habits(habits_data):
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

# Personalized habit suggestions
def get_personalized_habits(focus_areas):
    habit_suggestions = {
        "Health": ["Drink 2L water daily", "Walk 10,000 steps", "Stretch for 5 minutes"],
        "Education": ["Read 15 pages daily", "Review one chapter", "Learn 5 new words"]
    }
    suggestions = []
    for area in focus_areas:
        suggestions.extend(habit_suggestions.get(area, []))
    return suggestions

def display_suggestions():
    st.write("### Personalized Habit Suggestions")
    focus_areas = ["Health", "Education"]  # Replace with dynamic user focus areas
    suggested_habits = get_personalized_habits(focus_areas)
    for habit in suggested_habits:
        st.write(f"✅ {habit}")
        if st.button(f"Add '{habit}' to My Habits", key=habit):
            st.session_state.habits_data.append({"name": habit, "due": "Today", "status": "Pending"})
            st.success(f"Habit '{habit}' added successfully!")

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
    display_suggestions()
elif menu == "Reminders":
    display_reminder_options()

# Save data on app exit
save_habits(st.session_state.habits_data)

st.write("---")
st.write("Keep building small habits daily! 🚀")
