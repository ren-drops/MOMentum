# cd "C:\Users\minto\OneDrive\Desktop\Ren\Coding\HACKATHON 2"
# $env:STREAMLIT_CONFIG_DIR=".streamlit"
# python -m streamlit run MOMentum.py

import streamlit as st
import sqlite3 as sql
import requests

st.set_page_config(page_title="MOMentum", page_icon="🏃🏻‍♀️‍➡️", layout="wide")

# TITLE
st.title("MOMentum 🏃🏻‍♀️‍➡️")
st.caption("Reducing the mental load of families through AI assistance")

st.divider()

# DATABASES
conn = sql.connect("momentum.db", check_same_thread=False)
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT,
    role TEXT
)
""")
conn.commit()

# TASKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator TEXT,
    assigned_to TEXT,
    task TEXT,
    due_date DATE,
    status TEXT
)
""")
conn.commit()

# PERSONAL TASKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS personal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    task TEXT,
    due_date DATE,
    status TEXT
)
""")
conn.commit()

# GROCERY
cursor.execute("""
CREATE TABLE IF NOT EXISTS grocery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    assigned_to TEXT,
    quantity TEXT,
    status TEXT
)
""")
conn.commit()

# MESSENGER
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT
)
""")
conn.commit()

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = "Child"


# LOGIN PAGE
def login_page():

    st.subheader("Login")

    username = st.text_input("Email or Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    col1, col2, col3 = st.columns([1, 1, 6])

    error_box = st.empty()

    with col1:
        if st.button("Login"):

            cursor.execute(
                """
                SELECT * FROM users
                WHERE (username=? OR email=?) AND password=?
            """,
                (username, username, password),
            )

            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[1]
                st.session_state.user_role = user[4]
                st.rerun()
            else:
                error_box.error("Invalid credentials")

    with col2:
        if st.button("Clear"):
            st.rerun()

    st.write("")
    st.markdown("Don't have an account?")

    if st.button("Sign Up"):
        st.session_state.page = "signup"
        st.rerun()


# SIGNUP PAGE
def signup_page():

    st.subheader("Create Account")

    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")

    role = st.selectbox("Role", ["Parent", "Child"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create Account"):
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields")

            else:
                try:
                    cursor.execute(
                        """
                                   INSERT INTO users (username, email, password, role)
                                   VALUES (?, ?, ?, ?)
                    """,
                        (new_username, new_email, new_password, role),
                    )

                    conn.commit()

                    st.success("Account created successfully! Redirecting to login...")

                    import time

                    time.sleep(2.5)

                    st.session_state.page = "login"
                    st.rerun()

                except Exception as e:
                    st.error(f"Signup error: {e}")

    st.write("Have an account?")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# DASHBOARD
def dashboard():

    role = st.session_state.user_role

    # STATE INIT
    if "dashboard_page" not in st.session_state:
        st.session_state.dashboard_page = "home"

    if "calendar_view" not in st.session_state:
        st.session_state.calendar_view = "daily"

    if "calendar_person" not in st.session_state:
        st.session_state.calendar_person = "All"

    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = "June 2025"

    # HEADER
    st.title(f"👋 Welcome {st.session_state.username}")
    st.caption(f"Account type: {role}")
    st.divider()

    # SIDEBAR NAVIGATION
    st.sidebar.title("Navigation")

    if st.sidebar.button("🏠 Home", key="home_btn"):
        st.session_state.dashboard_page = "home"

    if st.sidebar.button("📅 Family Calendar", key="calendar_btn"):
        st.session_state.dashboard_page = "calendar"

    if st.sidebar.button("✅ Task Manager", key="tasks_btn"):
        st.session_state.dashboard_page = "tasks"

    if st.sidebar.button("🛒 Grocery", key="grocery_btn"):
        st.session_state.dashboard_page = "grocery"

    if st.sidebar.button("💬 Family Messenger", key="message_btn"):
        st.session_state.dashboard_page = "messenger"

    if st.sidebar.button("🤖 AMM-AI", key="ai_btn"):
        st.session_state.dashboard_page = "ai"

    st.sidebar.divider()

    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.dashboard_page = "home"
        st.rerun()

    # HOME PAGE
    if st.session_state.dashboard_page == "home":

        if role == "Parent":
            st.subheader("👩‍👩‍👧 Parent Dashboard - Today")
        else:
            st.subheader("🧒 Child Dashboard - Today")

        st.markdown("### 📅 Today's Tasks")

        today = str(st.date_input("Today's Date", key="home_today"))
        found = False

        # PERSONAL TASKS DUE TODAY
        cursor.execute(
            """
                       SELECT task, due_date, status
                       FROM personal_tasks
                       WHERE username=?
        """,
            (st.session_state.username,),
        )

        personal_tasks = cursor.fetchall()

        for task_name, due_date, status in personal_tasks:
            if str(due_date) == today and status != "Done":
                found = True
                st.write(f"👤 Personal: {task_name} | 📅 {due_date} | 📌 {status}")

        # FAMILY TASKS DUE TODAY
        cursor.execute(
            """
                       SELECT task, assigned_to, due_date, status
                       FROM tasks
                       WHERE assigned_to=?
        """,
            (st.session_state.username,),
        )

        family_tasks = cursor.fetchall()

        for task_name, assigned_to, due_date, status in family_tasks:
            if str(due_date) == today and status != "Done":
                found = True
                st.write(f"👨‍👩‍👧 Family: {task_name} | 📅 {due_date} | 📌 {status}")

        if not found:
            st.info("No tasks scheduled for today 🎉")

    # TASKS PAGE
    elif st.session_state.dashboard_page == "tasks":

        st.subheader("📌 Tasks")

        tab1, tab2 = st.tabs(["👤 Personal Tasks", "👨‍👩‍👧 Family Tasks"])

        # PERSONAL TASKS
        with tab1:

            st.subheader("Add Personal Task")

            p_task = st.text_input("Task")
            p_due = st.date_input("Due Date (optional)", key="p_due")

            if st.button("Add Personal Task", key="add_personal_task"):
                if p_task:
                    cursor.execute(
                        """
                        INSERT INTO personal_tasks (username, task, due_date, status)
                        VALUES (?, ?, ?, ?)
                    """,
                        (st.session_state.username, p_task, p_due, "Pending"),
                    )
                    conn.commit()
                    st.success("Task added")
                else:
                    st.error("Enter a task")

            st.subheader("Your Tasks")

            cursor.execute(
                """
                SELECT * FROM personal_tasks
                WHERE username=?
            """,
                (st.session_state.username,),
            )

            tasks = cursor.fetchall()

            for t in tasks:
                st.write(f"""
                         Task: {t[2]}
                         Due: {t[3]}
                         Status: {t[4]}
                """)

                col1, col2 = st.columns(2)

                with col1:
                    if t[4] != "Done":
                        if st.button("Mark Done", key=f"done_personal_{t[0]}"):
                            cursor.execute(
                                """
                                           UPDATE personal_tasks
                                           SET status='Done'
                                           WHERE id=?
                            """,
                                (t[0],),
                            )
                            conn.commit()
                            st.rerun()

                with col2:
                    if st.button("Delete", key=f"del_personal_{t[0]}"):
                        cursor.execute(
                            """
                                       DELETE FROM personal_tasks
                                       WHERE id=?
                        """,
                            (t[0],),
                        )
                        conn.commit()
                        st.rerun()

                st.divider()

        # FAMILY TASKS
        with tab2:

            st.subheader("Add Family Task")

            task_text = st.text_input("Task", key="family_task")
            assigned_to = st.selectbox(
                "Assign To", ["Mom", "Dad", "Kid"], key="assign_to"
            )
            due_date = st.date_input("Due Date (optional)", key="family_due")

            if st.button("Add Family Task", key="add_family_task"):
                if task_text:
                    cursor.execute(
                        """
                        INSERT INTO tasks (creator, assigned_to, task, due_date, status)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            st.session_state.username,
                            assigned_to,
                            task_text,
                            due_date,
                            "Pending",
                        ),
                    )
                    conn.commit()
                    st.success("Task added")
                else:
                    st.error("Enter a task")

            st.subheader("Family Tasks")

            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()

            for t in tasks:
                st.write(f"""
                         Task: {t[3]}
                         Assigned: {t[2]}
                         Due: {t[4]}
                         Status: {t[5]}
                """)

                col1, col2 = st.columns(2)

                with col1:
                    if t[5] != "Done":
                        if st.button("Mark Done", key=f"done_family_{t[0]}"):
                            cursor.execute(
                                """
                                           UPDATE tasks
                                           SET status='Done'
                                           WHERE id=?
                            """,
                                (t[0],),
                            )
                            conn.commit()
                            st.rerun()

                with col2:
                    if st.button("Delete", key=f"del_family_{t[0]}"):
                        cursor.execute(
                            """
                                       DELETE FROM tasks
                                       WHERE id=?
                                       """,
                            (t[0],),
                        )
                        conn.commit()
                        st.rerun()

                st.divider()

    # GROCERY PAGE
    elif st.session_state.dashboard_page == "grocery":
        st.subheader("🛒 Grocery Manager")

        # ADD ITEM
        st.markdown("### ➕ Add Grocery Item")
        item = st.text_input("Item name", key="g_item")
        quantity = st.text_input("Quantity", key="g_qty")

        if st.button("Add Item", key="add_grocery"):
            if item:
                cursor.execute(
                    """
                               INSERT INTO grocery (item, quantity, status)
                               VALUES (?, ?, ?)
                """,
                    (item, quantity, "Pending"),
                )
                conn.commit()
                st.success("Item added to grocery list")
            else:
                st.error("Enter an item")

        st.divider()

        # VIEW LIST
        st.markdown("### 📋 Grocery List")

        cursor.execute("SELECT * FROM grocery")
        items = cursor.fetchall()

        for i in items:
            st.write(f"""
                     🛒 {i[1]}    
                     📦 Qty: {i[3]}  
                     📌 Status: {i[4]}
            """)

            col1, col2 = st.columns(2)

            with col1:
                if i[4] != "Done":
                    if st.button("Mark Bought", key=f"buy_{i[0]}"):
                        cursor.execute(
                            """
                                       UPDATE grocery
                                       SET status='Done'
                                       WHERE id=?
                        """,
                            (i[0],),
                        )
                        conn.commit()
                        st.rerun()

            with col2:
                if st.button("Delete", key=f"del_g_{i[0]}"):
                    cursor.execute(
                        """
                        DELETE FROM grocery
                        WHERE id=?
                    """,
                        (i[0],),
                    )
                    conn.commit()
                    st.rerun()

            st.divider()

    # MESSENGER
    elif st.session_state.dashboard_page == "messenger":
        st.subheader("💬 Family Messenger")

        st.caption("Send quick updates to family members")

        message_text = st.text_input("Type your message", key="message_input")

        if st.button("Send Message"):
            if message_text:
                cursor.execute(
                    """
                               INSERT INTO messages (sender, message)
                               VALUES (?, ?)
                """,
                    (st.session_state.username, message_text),
                )
                conn.commit()
                st.success("Message sent!")
                st.rerun()
            else:
                st.error("Enter a message")

        st.divider()

        st.subheader("Chat History")

        cursor.execute("""
                       SELECT id, sender, message
                       FROM messages
                       ORDER BY id DESC
        """)
        messages = cursor.fetchall()

        if not messages:
            st.info("No messages yet")

        else:
            for msg in messages:
                msg_id = msg[0]
                sender = msg[1]
                message = msg[2]

                st.write(f"**{sender}:** {message}")

                if sender == st.session_state.username:

                    col1, col2 = st.columns(2)

                    # DELETE MESSAGE
                    with col1:
                        if st.button("Delete", key=f"delete_msg_{msg_id}"):
                            cursor.execute(
                                """
                                           DELETE FROM messages
                                           WHERE id=?
                            """,
                                (msg_id,),
                            )
                            conn.commit()
                            st.rerun()

                    # EDIT MESSAGE
                    with col2:
                        new_message = st.text_input(
                            "Edit message", key=f"edit_input_{msg_id}"
                        )

                        if st.button("Update", key=f"update_msg_{msg_id}"):
                            if new_message:
                                cursor.execute(
                                    """
                                               UPDATE messages
                                               SET message=?
                                               WHERE id=?
                                """,
                                    (new_message, msg_id),
                                )
                                conn.commit()
                                st.rerun()

                    st.divider()

                else:
                    st.divider()

    # AMM-AI
    elif st.session_state.dashboard_page == "ai":

        st.subheader("🤖 AMM-AI")
        st.caption("Your family assistant (local AI via Ollama)")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("Ask AMM-AI something")

        if st.button("Send"):

            if user_input:

                # GET DATA FROM DATABASE
                cursor.execute("SELECT task, assigned_to, due_date, status FROM tasks")
                tasks = cursor.fetchall()

                cursor.execute(
                    "SELECT task, due_date, status FROM personal_tasks WHERE username=?",
                    (st.session_state.username,),
                )
                personal_tasks = cursor.fetchall()

                tasks_str = "\n".join(
                    [
                        f"- Task: {t[0]}, Assigned To: {t[1]}, Due Date: {t[2]}, Status: {t[3]}"
                        for t in tasks
                    ]
                )

                personal_str = "\n".join(
                    [
                        f"- Task: {t[0]}, Due Date: {t[1]}, Status: {t[2]}"
                        for t in personal_tasks
                    ]
                )

                # BUILD CONTEXT
                prompt = f"""
                You are AMM-AI, a family assistant.
                You MUST ONLY use the information provided below.
                Do NOT assume dates, rules, or logic not written here.
                
                User: {st.session_state.username}
                
                FAMILY TASKS:
                {tasks_str}
                
                PERSONAL TASKS:
                {personal_str}
                
                INSTRUCTIONS:
                - Answer only based on the tasks listed above.
                - Do NOT invent rules or calculate dates.
                - If a task exists, mention it clearly.
                - If none exist, say "No matching tasks found."
                
                User Question:
                {user_input}
                """

                try:
                    # OLLAMA REQUEST
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.2:1b",
                            "prompt": prompt,
                            "stream": False,
                        },
                        timeout=120,
                    )

                    result = response.json()
                    reply = result.get("response", "No response from model.")

                    st.session_state.chat_history.append(("You", user_input))
                    st.session_state.chat_history.append(("AMM-AI", reply))

                    st.rerun()

                except Exception as e:
                    st.error(f"Ollama error: {e}")

        st.divider()

        # CHAT DISPLAY
        for sender, msg in st.session_state.chat_history:
            if sender == "You":
                st.write(f"🧑 You: {msg}")
            else:
                st.write(f"🤖 AMM-AI: {msg}")

    # CALENDAR PAGE
    elif st.session_state.dashboard_page == "calendar":
        st.subheader("📅 Family Calendar")

        person = st.selectbox("View For:", ["All", "Mom", "Dad", "Kid"])

        view = st.radio("View Mode:", ["Daily", "Weekly", "Monthly"], horizontal=True)

        st.divider()

        cursor.execute("""
                       SELECT task, assigned_to, due_date, status
                       FROM tasks
        """)

        tasks = cursor.fetchall()

        # DAILY VIEW
        if view == "Daily":
            st.markdown("### 📅 Daily Tasks")

            found = False

            for task_name, assigned_to, due_date, status in tasks:
                if person != "All" and assigned_to != person:
                    continue

                found = True

                st.write(
                    f"📝 {task_name} | 👤 {assigned_to} | 📅 {due_date} | 📌 {status}"
                )

            if not found:
                st.info("No tasks found")

        # WEEKLY VIEW
        elif view == "Weekly":
            st.markdown("### 📆 Weekly Overview")

            found = False

            for task_name, assigned_to, due_date, status in tasks:
                if person != "All" and assigned_to != person:
                    continue

                found = True

                st.write(f"• {task_name} ({assigned_to}) → {due_date}")

            if not found:
                st.info("No tasks found")

        # MONTHLY VIEW
        elif view == "Monthly":
            st.markdown("### 🗓 Monthly Summary")

            found = False

            for task_name, assigned_to, due_date, status in tasks:
                if person != "All" and assigned_to != person:
                    continue

                found = True

                st.write(f"{due_date} → {task_name} ({assigned_to}) [{status}]")

            if not found:
                st.info("No tasks found")


# ROUTING
if st.session_state.logged_in:
    dashboard()

elif st.session_state.page == "signup":
    signup_page()

else:
    login_page()
