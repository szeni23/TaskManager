import streamlit as st
from db_utils import connect_to_db, get_tasks_by_category, add_task, set_task_category, reset_past_due_tasks
import pandas as pd
from datetime import datetime, date, timedelta


def page2():
    con = connect_to_db()
    cur = con.cursor()

    reset_past_due_tasks(cur)


    no_category_tasks = get_tasks_by_category(cur, None)  # No category
    doit_tasks = get_tasks_by_category(cur, "DOIT")
    deliberateit_tasks = get_tasks_by_category(cur, "DeliberateIt")
    dumpit_tasks = get_tasks_by_category(cur, "DumpIt")

    # UI
    st.subheader('Start your day here.')
    new_task = st.text_input('Enter tasks, ideas and thoughts you need to save...')
    if st.button('Add'):
        if new_task:
            add_task(cur, new_task)
            con.commit()
            st.success('Task added!')
            st.experimental_rerun()
        else:
            st.warning('Enter a task first.')

    def display_tasks(task_data, header, columns_to_drop=None):
        if task_data:
            df = pd.DataFrame(task_data, columns=["ID", "Task Description", "Added Date", "Finished %", "Due Date",
                                                  "Level of Importance"]).drop(
                columns=["ID", "Finished %", "Level of Importance"])

            if columns_to_drop:
                df = df.drop(columns=columns_to_drop)

            st.subheader(header)
            st.table(df)
            return df
        return None

    category_descriptions = {
        'DOIT': 'Do it',
        'DeliberateIt': 'Deliberate it',
        'DumpIt': 'Dump it'
    }

    df_no_category = display_tasks(no_category_tasks, 'Categorize tasks', columns_to_drop=["Due Date"])
    if df_no_category is None and len(no_category_tasks) != 0:
        st.success('All tasks are categorized!')
    if df_no_category is not None:
        # UI for categorizing tasks without a category
        task_id_to_set = st.selectbox('Select a task to categorize', df_no_category['Task Description'].tolist())
        selected_description = st.selectbox('Select a category', list(category_descriptions.values()))
        category_to_set = next(key for key, value in category_descriptions.items() if value == selected_description)

        due_date = None
        if category_to_set == "DOIT":
            due_date = datetime.today().strftime('%Y-%m-%d')
        elif category_to_set == "DeliberateIt":
            min_date = datetime.today() + timedelta(days=1)
            due_date = st.date_input('Select a due date for this task', value=min_date, min_value=min_date)

        if st.button('Set Category'):
            matching_index = df_no_category[df_no_category['Task Description'] == task_id_to_set].index[0]
            task_id_for_db = no_category_tasks[matching_index][0]
            set_task_category(cur, task_id_for_db, category_to_set, due_date)
            st.success(f'Task updated with category: {category_to_set}')
            task_to_remove = next((task for task in no_category_tasks if task[0] == task_id_for_db), None)
            if task_to_remove:
                no_category_tasks.remove(task_to_remove)
            st.experimental_rerun()

    display_tasks(doit_tasks, 'DO IT')
    display_tasks(deliberateit_tasks, 'Deliberate It')
    display_tasks(dumpit_tasks, 'Dump It', columns_to_drop=["Due Date"])
