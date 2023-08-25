import sqlite3
from datetime import datetime


def connect_to_db():
    return sqlite3.connect('tasks.db')


def add_task(cur, task_description):
    today = datetime.today().strftime('%Y-%m-%d')
    cur.execute(
        "INSERT INTO tasks (task_description, category, added_date, finished, due_date, levelofimportance) VALUES (?, ?, ?, ?, ?, ?)",
        (task_description, None, today, 0, None, None)
    )


def get_all_tasks(cur):
    cur.execute(
        "SELECT ID, task_description, category, added_date, due_date, levelofimportance FROM tasks WHERE finished = 0")
    return cur.fetchall()


def get_tasks_by_category(cursor, category):
    """Retrieve tasks by category from the database."""
    if category:
        cursor.execute(
            "SELECT ID, task_description, added_date, finished, due_date, levelofimportance FROM tasks WHERE category = ?",
            (category,))
    else:
        cursor.execute(
            "SELECT ID, task_description, added_date, finished, due_date, levelofimportance FROM tasks WHERE category IS NULL")
    return cursor.fetchall()


def set_task_category(cur, task_id, category, due_date=None):
    """Assign a category to a task and set its due date if provided."""
    if due_date:
        cur.execute("UPDATE tasks SET category = ?, due_date = ? WHERE ID = ?", (category, due_date, task_id))
    else:
        cur.execute("UPDATE tasks SET category = ? WHERE ID = ?", (category, task_id))
    cur.connection.commit()


def reset_past_due_tasks(cur):
    today = datetime.today().strftime('%Y-%m-%d')
    cur.execute("UPDATE tasks SET category = NULL WHERE due_date < ? AND due_date IS NOT NULL", (today,))
    cur.connection.commit()


def get_all_tasks_today(cur):
    today_date = datetime.today().strftime('%Y-%m-%d')
    cur.execute("SELECT * FROM tasks WHERE Due_Date=?", (today_date,))
    return cur.fetchall()


def set_task_importance_level(cur, task_id, importance_level):
    cur.execute("UPDATE tasks SET LevelOfImportance=? WHERE ID=?", (importance_level, task_id))
    cur.connection.commit()


