# user.py
# user.py
import getpass
from modules.db import connect_db, hash_password
from models import USERS_TABLE, ORGANIZERS_TABLE, EVENTS_TABLE, SUBEVENTS_TABLE, RESULTS_TABLE, REGISTRATIONS_TABLE
from tabulate import tabulate   # ✅ add this line
from modules.db import connect_db, get_dict_cursor


def signup():
    fullname = input("Full Name: ")
    username = input("Choose a username: ")
    phone = input("Phone Number (must contain 10 digits): ")
    email = input("Email (must contain @gmail.com): ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    address = input("Address: ")
    password = getpass.getpass("Choose a password: ")

    # ---------------------------
    # VALIDATIONS
    # ---------------------------
    if not phone.isdigit() or len(phone) != 10:
        print("⚠️ Invalid Phone Number. It must contain exactly 10 digits.")
        return

    if not email.endswith("@gmail.com"):
        print("⚠️ Invalid Email. It must be a Gmail address.")
        return

    # ---------------------------
    # DATABASE INSERTION
    # ---------------------------
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute(f"""
            INSERT INTO {USERS_TABLE} 
            (fullname, username, phone, email, dob, address, password)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (fullname, username, phone, email, dob, address, hash_password(password)))
        db.commit()
        print("✅ Signup successful!\n")
    except Exception as e:
        print("⚠️ Error:", e)
    finally:
        db.close()


def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute(f"SELECT * FROM {USERS_TABLE} WHERE username=%s AND password=%s",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    db.close()

    if user:
        print("✅ Login successful!\n")
        return user
    else:
        print("❌ Invalid credentials.")
        return None


def view_profile(user_id):
    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f"SELECT * FROM {USERS_TABLE} WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    db.close()

    print("\n--- Profile ---")
    for k, v in user.items():
        if k != "password":
            print(f"{k}: {v}")


def update_profile(user_id):
    db = connect_db()
    cursor = db.cursor()

    print("\n--- Update Profile ---")
    fullname = input("Full Name (leave blank to skip): ")
    phone = input("Phone Number (leave blank to skip): ")
    email = input("Email (leave blank to skip): ")
    dob = input("Date of Birth (YYYY-MM-DD, leave blank to skip): ")
    address = input("Address (leave blank to skip): ")
    password = getpass.getpass("New Password (leave blank to skip): ")

    updates, values = [], []
    if fullname: updates.append("fullname=%s"); values.append(fullname)
    if phone: updates.append("phone=%s"); values.append(phone)
    if email: updates.append("email=%s"); values.append(email)
    if dob: updates.append("dob=%s"); values.append(dob)
    if address: updates.append("address=%s"); values.append(address)
    if password: updates.append("password=%s"); values.append(hash_password(password))

    if updates:
        sql = f"UPDATE {USERS_TABLE} SET {', '.join(updates)} WHERE id=%s"
        values.append(user_id)
        cursor.execute(sql, tuple(values))
        db.commit()
        print("✅ Profile updated successfully!")
    else:
        print("⚠️ No changes made.")

    db.close()


def view_events(user_id):
    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE}")
    events = cursor.fetchall()
    if not events:
        print("⚠️ No events available.")
        db.close()
        return

    print("\n--- Events ---")
    print(tabulate(events, headers="keys", tablefmt="grid"))

    event_id = input("Enter Event ID to view sub-events: ")
    cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
    subs = cursor.fetchall()

    if not subs:
        print("⚠️ No sub-events found.")
    else:
        print("\n--- Sub-Events ---")
        print(tabulate(subs, headers="keys", tablefmt="grid"))

        choice = input("Do you want to register for a sub-event? (y/n): ").lower()
        if choice == 'y':
            sub_id = input("Enter Sub-Event ID to register: ")
            pay_method = input("Payment Method (UPI/GPay/PhonePe/Card): ")
            pay_id = input("Payment ID: ")
            pay_pin = getpass.getpass("Payment PIN: ")

            cursor.execute(f"""
                INSERT INTO {REGISTRATIONS_TABLE} 
                (user_id, subevent_id, payment_method, payment_id, payment_pin)
                VALUES (%s,%s,%s,%s,%s)
            """, (user_id, sub_id, pay_method, pay_id, pay_pin))
            db.commit()
            print("✅ Registration successful!")

    db.close()


def cancel_registration(user_id):
    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)


    cursor.execute(f"""
        SELECT r.id, e.name AS event_name, s.name AS subevent_name
        FROM {REGISTRATIONS_TABLE} r
        JOIN {SUBEVENTS_TABLE} s ON r.subevent_id=s.id
        JOIN {EVENTS_TABLE} e ON s.event_id=e.id
        WHERE r.user_id=%s
    """, (user_id,))
    regs = cursor.fetchall()

    if not regs:
        print("⚠️ You have no registrations.")
    else:
        print("\n--- Your Registrations ---")
        print(tabulate(regs, headers="keys", tablefmt="grid"))

        reg_id = input("Enter Registration ID to cancel: ")
        cursor.execute(f"DELETE FROM {REGISTRATIONS_TABLE} WHERE id=%s AND user_id=%s", (reg_id, user_id))
        db.commit()
        print("✅ Registration cancelled!")

    db.close()


def view_results():
    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)


    cursor.execute(f"SELECT * FROM {EVENTS_TABLE}")
    events = cursor.fetchall()
    if not events:
        print("⚠️ No events available.")
        db.close()
        return

    print("\n--- Events ---")
    print(tabulate(events, headers="keys", tablefmt="grid"))

    event_id = input("Enter Event ID to view results: ")
    cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
    subs = cursor.fetchall()

    if not subs:
        print("⚠️ No sub-events found.")
    else:
        print("\n--- Sub-Events ---")
        print(tabulate(subs, headers="keys", tablefmt="grid"))

        sub_id = input("Enter Sub-Event ID to view results: ")
        cursor.execute(f"SELECT * FROM {RESULTS_TABLE} WHERE subevent_id=%s", (sub_id,))
        results = cursor.fetchone()

        if results:
            print("\n--- Winners ---")
            print(f"🥇 First Prize: {results['first']}")
            print(f"🥈 Second Prize: {results['second']}")
            print(f"🥉 Third Prize: {results['third']}")
        else:
            print("⚠️ Results not declared yet.")

    db.close()




def user_module_menu():
    while True:
        print("\n--- User Module ---")
        print("1. Sign Up")
        print("2. Log In")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            signup()
        elif choice == "2":
            user = login()
            if user:
                user_id = user["id"]
                while True:
                    print("\n--- User Dashboard ---")
                    print("1. View Profile")
                    print("2. Update Profile")
                    print("3. View Events & Register")
                    print("4. Cancel Registration")
                    print("5. View Results")
                    print("6. Logout")

                    c = input("Enter your choice: ")
                    if c == "1":
                        view_profile(user_id)
                    elif c == "2":
                        update_profile(user_id)
                    elif c == "3":
                        view_events(user_id)
                    elif c == "4":
                        cancel_registration(user_id)
                    elif c == "5":
                        view_results()
                    elif c == "6":
                        break
                    else:
                        print("⚠️ Invalid choice.")
        elif choice == "3":
            break
        else:
            print("⚠️ Invalid choice.")
