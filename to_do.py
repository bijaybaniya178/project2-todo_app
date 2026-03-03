import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os


load_dotenv()
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")

   
try:

    conn = psycopg.connect(
        host=host,
        dbname=db_name,
        user=username,
        password=db_password,
        port=port)
    with conn.cursor(row_factory=dict_row) as curr:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS user_tasks(
                id SERIAL PRIMARY KEY,  
                username VARCHAR(50) NOT NULL,
                task VARCHAR(255) NOT NULL ,
                status BOOLEAN DEFAULT FALSE,
                createdAt TIMESTAMP DEFAULT date_trunc('second', NOW())
                );
            """
        curr.execute(create_table_query)
        conn.commit()
        print("DATABASE CONNECTED!!!")
        # a="""
        #     DROP TABLE IF EXISTS user_tasks;"""
        # curr.execute(a)
        # conn.commit()

except Exception as v:
    print("Database Error Occur", v)
    exit(1)


def add_task(username, task):
    try:
        with conn.cursor() as curr:
            insert_data = """
            INSERT INTO user_tasks (username,task )
            VALUES(%s ,%s)"""
            curr.execute(insert_data, (username, task))
            conn.commit()
            print("Task Added")
    except Exception as var:
        print("Something Goes Wrong ", var)
        conn.rollback()


def handle_add_task(username):
    task = input("Enter The Task: ").strip().title()
    if not task:                          # ✅ check if empty
        print(" Task cannot be empty!")
        return
    add_task(username, task)


def view_task(username):
    try:
        with conn.cursor(row_factory=dict_row) as curr:
            curr.execute(
                "SELECT * FROM user_tasks WHERE username=%s ORDER BY id", (
                    username,)
            )
            tasks = curr.fetchall()
            
            if not tasks:
                print(f"\nNo tasks found for '{username}'")
                return
            print(f"{'Task_ID':<7} | {'Task':^30} | {'Status':<12} | {'Created at'}")
            for row in tasks:
                row['status'] = "Pending" if row['status'] == False else "Completed"

                print(
                    f"{row['id']:^7} | {row['task']:<30} | {row['status']:<12} | {row['createdat']}")

    except Exception as var:
        print("ERROR", var)


def handle_view_tasks(username):
    view_task(username)


def update_task(task_id, username, new_task):
    try:
        with conn.cursor()as curr:
            curr.execute("UPDATE user_tasks SET task=%s WHERE id=%s AND username=%s ",
                         (new_task, task_id, username))
            conn.commit()
            print(" Task Updated!")
            
    except Exception as e:
        print("ERROR", e)
        conn.rollback()


def update_task_status(task_id, username, new_status):
    try:
        with conn.cursor()as curr:
            curr.execute("UPDATE user_tasks SET status=%s WHERE id=%s AND username=%s  ",
                         (new_status, task_id, username))
            conn.commit()
            print("Task Status Updates!!!")
    except Exception as e:
        print("ERROR", e)
        conn.rollback()


def handle_update_task(username):
    view_task(username)
    try:
        task_id = int(input("Enter The Task_id you want to update: "))
        with conn.cursor(row_factory=dict_row)as curr:
            curr.execute("SELECT id FROM user_tasks WHERE id=%s AND username=%s",(task_id,username))
            checking_task_id = curr.fetchone()
            if not checking_task_id:
                print(f"❌ Task not found with Task ID: {task_id}!")
                return     
        print("""Update Options:
            1: Update Task only
            2: Update Task Status only
            3: Update Both Task and Task Status
            """)

        options = input("Enter your choice 1,2 or 3: ").strip()
        if options == "1":
            new_task = input("Update The Task: ").strip().title()
            if new_task:
                update_task(task_id, username, new_task)
            else:
                 print("Task cannot be empty!")
   
        elif options == "2":
            changing_status = input("Enter 1 to mark completed and 2 for pending: ").strip()
            if changing_status in ["1", "2"]:
                new_status = True if changing_status == "1" else False
                update_task_status(task_id, username, new_status)
            else:
                print("Invalid Input! Please Try Again")
        elif options == "3":
            new_task = input("Update The Task: ").strip().title()
            if not new_task:
                print("Task cannot be empty!")
                return
            update_task(task_id, username, new_task)
                 
            changing_status = input(
                "Enter 1 to mark completed and 2 for pending: ")
            if changing_status in ["1", "2"]:
                new_status = True if changing_status == "1" else False
                update_task_status(task_id, username, new_status)
            else:
                print("Invalid Input! Please Try Again")
        else:
            print("Invalid Input! Please Try Again")

    except ValueError:
        print(" Invalid task ID!")


def del_task(username, task_id):
    try:
        with conn.cursor(row_factory=dict_row)as curr:
            curr.execute(
                "DELETE FROM user_tasks  WHERE id=%s AND username=%s RETURNING task ", (task_id, username))
            deleted_task=curr.fetchone()
            conn.commit()
            if deleted_task:
                print(f"Task: {deleted_task['task']} is Deleted")
            else:
                print("Task not found with this Task_id!!!")
    except Exception as e:
        print("ERROR", e)
        conn.rollback()


def handle_del_task(username):
    view_task(username)
    try:
        task_id = int(input("Enter The Task_id you want to delete: "))
        del_task(username, task_id)
    except ValueError:
        print(" Invalid task ID!")


options = {
    "1": "View Tasks",
    "2": "Add Task",
    "3": "Update Task",
    "4": "Delete Task",
    "5": "Exit",

}
operations = {
    1: handle_view_tasks,
    2: handle_add_task,
    3: handle_update_task,
    4: handle_del_task,
}

username = input("Enter Your Unique Username: ").strip()
if not username:

    print("Username cannot be empty!Please try again")
    exit()
while True:
    for key, values in options.items():
        print(f"{key}:{values}")
    try:
        choice = int(input("Enter your choice (1-5): "))
        if choice in operations:
            operations[choice](username)
        elif choice == 5:
            print(" Thank you for using TODO Application!")
            conn.close()
            break
        else:
            print("Enter a number from 1-5")
    except ValueError:
        print("Invalid input! Please enter a number from 1-5")
