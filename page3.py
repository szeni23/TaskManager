import streamlit as st
from db_utils import connect_to_db, get_all_tasks_today, set_task_importance_level
import pandas as pd
from datetime import datetime

def page3():
    # Connect to the database
    con = connect_to_db()
    cur = con.cursor()

    # Display title and current day
    st.subheader(f"My Day - {datetime.today().strftime('%Y-%m-%d')}")

    # Fetch today's tasks
    today_tasks = get_all_tasks_today(cur) or []
    if not today_tasks:
        st.warning("No tasks available for today.")
        return

    with st.expander("Categorize Tasks", expanded=False):
        st.markdown("""
    First, categorize all of today's tasks based on their level of importance. 
    You can divide your tasks into 4 categories:
    - **Red**: If you could just do one thing today, what would be the most important task? 
    - **Orange**: Other tasks that are important today.
    - **Green**: Tasks that would be nice to get done today, but they are not crucial.
    - **Grey**: Easy tasks that take less than 5 minutes to do.
    """)

        # Display the selectbox only if there are tasks available
        task_to_categorize_or_change = st.selectbox(
            'Select a task to categorize or change importance',
            today_tasks,
            format_func=lambda x: x[1]
        )

        selected_task_id = task_to_categorize_or_change[0]
        current_importance = task_to_categorize_or_change[8]

        if current_importance:
            st.write(f"Current importance level: **{current_importance}**")

        importance_level = st.selectbox("Select New Importance Level", ["Red", "Orange", "Green", "Grey"])

        if st.button('Set/Change Importance Level'):
            try:
                set_task_importance_level(cur, selected_task_id, importance_level)
                st.success(f'Task {task_to_categorize_or_change[1]} categorized as {importance_level}')

                today_tasks = get_all_tasks_today(cur)
                for task in today_tasks:
                    if task[0] == selected_task_id:
                        current_importance = task[8]
                        if current_importance:
                            st.write(f"Updated importance level: **{current_importance}**")
                        break
            except Exception as e:
                st.error(f"An error occurred: {e}")

    categorized_tasks = [task for task in today_tasks if task[8]]
    if not categorized_tasks:
        st.warning("No categorized tasks for today.")
        return

    columns = ["ID", "Task Description", "Category", "Completion", "Added Date", "Finish Date", "Finished", "Due Date", "Level of Importance"]
    df_categorized_tasks = pd.DataFrame(categorized_tasks, columns=columns)
    df_categorized_tasks = df_categorized_tasks.drop(columns=["ID", "Finish Date", "Finished", "Category", "Added Date"])
    order = {"Red": 1, "Orange": 2, "Green": 3, "Grey": 4}
    df_categorized_tasks = df_categorized_tasks.sort_values(by="Level of Importance", key=lambda x: x.map(order))
    st.subheader("Today's Tasks")
    st.table(df_categorized_tasks)
    with st.expander("Update completion status", expanded=False):
        task_to_update = st.selectbox('Select a task to update completion', categorized_tasks, format_func=lambda x: x[1])
        selected_task_id_update = task_to_update[0]

        col1, col2 = st.columns(2)

        with col1:
            completion_percentage = st.slider("Completion Percentage", 0, 100, task_to_update[3])
            if st.button('Update Completion'):
                try:
                    if completion_percentage == 100:
                        cur.execute("UPDATE tasks SET completion = ?, finish_date = ? WHERE ID = ?", (completion_percentage, datetime.today().strftime('%Y-%m-%d'), selected_task_id_update))
                    else:
                        cur.execute("UPDATE tasks SET completion = ? WHERE ID = ?", (completion_percentage, selected_task_id_update))

                    con.commit()
                    st.success(f'Task {task_to_update[1]} updated to {completion_percentage}%')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred while updating completion: {e}")

        with col2:
            if st.button('Mark as Completed'):
                try:
                    cur.execute("UPDATE tasks SET completion = 100, finish_date = ? WHERE ID = ?", (datetime.today().strftime('%Y-%m-%d'), selected_task_id_update))
                    con.commit()
                    st.success(f'Task {task_to_update[1]} marked as completed')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred while marking as completed: {e}")

    con.close()
