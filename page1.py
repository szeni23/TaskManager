import streamlit as st
from db_utils import connect_to_db, add_task, get_all_tasks

def page1():
    # Connect to the database
    con = connect_to_db()
    cur = con.cursor()

    # UI
    st.subheader('jot stuff here. Then forget about it until you Start your day.')
    new_task = st.text_input('')
    if st.button('Add'):
        if new_task:
            add_task(cur, new_task)
            con.commit()
            st.success('Task added!')
        else:
            st.warning('Enter a task first.')
