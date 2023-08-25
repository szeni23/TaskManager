import os
import pandas as pd
import sqlite3
import streamlit as st
from page1 import page1
from page2 import page2
from page3 import page3

# Set page config at the top of the script
st.set_page_config(
    page_title="Adrians Notes",
    layout="wide"
)

tabs = {
    "Quick Note Taker": page1,
    "Organize your tasks": page2,
    "My Tasks": page3,
}


# Database initialization
def init_db():
    con = sqlite3.connect('tasks.db')
    cur = con.cursor()

    # Create the table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            task_description TEXT NOT NULL,
            category TEXT,
            completion int,
            added_date DATE,
            finish_date DATE,
            finished BOOLEAN, 
            due_date DATE,
            levelofimportance TEXT
        )
    ''')
    con.close()


init_db()


def main():
    selection = st.sidebar.radio(" ", list(tabs.keys()))

    page = tabs[selection]
    with st.spinner(f"Load {selection}..."):
        page()


if __name__ == "__main__":
    main()
