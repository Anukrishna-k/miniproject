# organizer.py
# organizer.py
# organizer.py
import getpass
from modules.db import connect_db, hash_password
from models import ORGANIZERS_TABLE, EVENTS_TABLE, SUBEVENTS_TABLE, RESULTS_TABLE, REGISTRATIONS_TABLE, USERS_TABLE


# ---------------------------
# SIGNUP
# ---------------------------
def signup():
    fullname = input("Full Name: ").strip()
    username = input("Choose a username: ").strip()
    dob = input("Date of Birth (YYYY-MM-DD): ").strip()

    # phone: loop until valid
    while True:
        phone = input("Phone Number (must contain 10 digits): ").strip()
        if phone.isdigit() and len(phone) == 10:
            break
        print("⚠️ Invalid Phone Number. It must contain exactly 10 digits.")

    # email: loop until valid
    while True:
        email = input("Email (must contain @gmail.com): ").strip()
        if email and email.lower().endswith("@gmail.com"):
            break
        print("⚠️ Invalid Email. It must be a Gmail address ending with @gmail.com.")

    address = input("Address: ").strip()

    # aadhaar: loop until valid
    while True:
        adhaar = input("Aadhaar Number (must contain 12 digits): ").strip()
        if adhaar.isdigit() and len(adhaar) == 12:
            break
        print("⚠️ Invalid Aadhaar Number. It must contain exactly 12 digits.")

    # optional: check duplicates (username/email)
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT id FROM {ORGANIZERS_TABLE} WHERE username=%s", (username,))
    if cursor.fetchone():
        db.close()
        print("⚠️ Username already taken. Please choose a different username.")
        return

    cursor.execute(f"SELECT id FROM {ORGANIZERS_TABLE} WHERE email=%s", (email,))
    if cursor.fetchone():
        db.close()
        print("⚠️ Email already registered. Try logging in or use a different email.")
        return

    # only ask password after all previous fields validated
    password = getpass.getpass("Choose a password: ")

    try:
        cursor.execute(f"""
            INSERT INTO {ORGANIZERS_TABLE}
            (fullname, username, dob, phone, email, address, adhaar, password, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (fullname, username, dob, phone, email, address, adhaar, hash_password(password), "pending"))
        db.commit()   # <- commit is necessary!
        print("✅ Signup successful!\n")
    except Exception as e:
        print("⚠️ Error:", e)
    finally:
        db.close()


# ---------------------------
# LOGIN + DASHBOARD
# ---------------------------
def login():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
    f"SELECT * FROM {ORGANIZERS_TABLE} WHERE username=%s AND password=%s",
    (username, hash_password(password))
)
    result = cursor.fetchone()
    db.close()

    if result:
        print(f"✅ Welcome, {result['fullname']}!\n")
        organizer_dashboard(result)  # pass full dict, not result["id"]

    else:
        print("❌ Invalid credentials.")


# ---------------------------
# VIEW & UPDATE PROFILE
# ---------------------------
def view_profile(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {ORGANIZERS_TABLE} WHERE id=%s", (org_id,))
    organizer = cursor.fetchone()
    db.close()

    if organizer:
        print("\n--- Organizer Profile ---")
        for key, value in organizer.items():
            if key not in ["password"]:
                print(f"{key.capitalize()}: {value}")


def update_profile(org_id):
    print("\n--- Update Profile ---")
    phone = input("New Phone (leave blank to skip): ")
    email = input("New Email (leave blank to skip): ")
    address = input("New Address (leave blank to skip): ")
    password = getpass.getpass("New Password (leave blank to skip): ")

    db = connect_db()
    cursor = db.cursor()

    updates, values = [], []
    if phone: updates.append("phone=%s"); values.append(phone)
    if email: updates.append("email=%s"); values.append(email)
    if address: updates.append("address=%s"); values.append(address)
    if password: updates.append("password=%s"); values.append(hash_password(password))

    if updates:
        sql = f"UPDATE {ORGANIZERS_TABLE} SET {', '.join(updates)} WHERE id=%s"
        values.append(org_id)
        cursor.execute(sql, tuple(values))
        db.commit()
        print("✅ Profile updated successfully.")
    else:
        print("⚠️ No changes made.")
    db.close()


# organizer.py
import getpass
from modules.db import connect_db, hash_password
from models import ORGANIZERS_TABLE, EVENTS_TABLE, SUBEVENTS_TABLE, RESULTS_TABLE


# ---------------------------
# CREATE EVENT + SUB-EVENTS
# ---------------------------
def create_event(org_id):
    db = connect_db()
    cursor = db.cursor()

    print("\n--- Create Event ---")
    event_name = input("Event Name: ")
    days = int(input("How many days? "))

    if days == 1:
        event_date = input("Enter the Date (YYYY-MM-DD): ")
        from_date = event_date
        to_date = event_date
    else:
        from_date = input("From Date (YYYY-MM-DD): ")
        to_date = input("To Date (YYYY-MM-DD): ")

    venue = input("Venue: ")  # Moved outside the if-else (it should always be asked)

    # ✅ FIX: Removed extra comma after %s in VALUES and use proper placeholders
    cursor.execute(f"""
        INSERT INTO {EVENTS_TABLE} (organizer_id, name, from_date, to_date, venue)
        VALUES (%s, %s, %s, %s, %s)
    """, (org_id, event_name, from_date, to_date, venue))
    db.commit()
    event_id = cursor.lastrowid

    sub_count = int(input("How many sub-events/programs: "))
    for i in range(sub_count):
        print(f"\n--- Sub-Event {i + 1} ---")
        sub_name = input("Sub-Event Name: ")
        sub_time = input("Time (HH:MM): ")
        sub_date = input("Date (YYYY-MM-DD): ")
        sub_venue = input("Venue: ")
        criteria = input("Participation Criteria: ")
        reg_limit = int(input("Registration Limit: "))
        fees = input("Registration Fees: ")
        desc = input("Description: ")
        first_prize = input("First Prize: ")
        second_prize = input("Second Prize: ")
        third_prize = input("Third Prize: ")

        # ✅ FIX: Removed quotes around column names — not needed, and will cause SQL error
        cursor.execute(f"""
            INSERT INTO {SUBEVENTS_TABLE}
            (event_id, name, time, date, venue, criteria, reg_limit,
             registration_fees, description, first_prize, second_prize, third_prize)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_id, sub_name, sub_time, sub_date, sub_venue, criteria,
              reg_limit, fees, desc, first_prize, second_prize, third_prize))
        db.commit()

    print("✅ Event and Sub-events created successfully!")
    db.close()


def check_profile_status(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # ✅ FIX: Include status column in SELECT
    cursor.execute(f"SELECT fullname, status FROM {ORGANIZERS_TABLE} WHERE id=%s", (org_id,))
    organizer = cursor.fetchone()
    db.close()

    if organizer:
        print("\n--- Profile Status ---")
        print(f"Organizer: {organizer['fullname']}")
        print(f"Status: {organizer['status'].capitalize()}")
        if organizer["status"] == "pending":
            print("⚠️ Your profile is pending admin approval. You cannot access event operations yet.")
        elif organizer["status"] == "approved":
            print("✅ Your profile has been approved. You can now access event operations.")
        elif organizer["status"] == "rejected":
            print("❌ Your profile was rejected by admin.")
        else:
            print("ℹ️ Unknown status.")
    else:
        print("⚠️ Organizer not found.")

# ---------------------------
# UPDATE EVENT OR SUB-EVENTS
# ---------------------------
def update_event(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # show events list
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE} WHERE organizer_id=%s", (org_id,))
    events = cursor.fetchall()

    if not events:
        print("⚠️ No events found.")
        db.close()
        return

    print("\n--- Your Events ---")
    for ev in events:
        print(f"{ev['id']}. {ev['name']} | {ev['from_date']} to {ev['to_date']} | {ev['venue']}")

    event_id = input("Enter Event ID to update: ")

    # ask for main event updates
    new_name = input("New Event Name (leave blank to skip): ")
    new_venue = input("New Venue (leave blank to skip): ")
    from_date = input("New From Date (leave blank to skip): ")
    to_date = input("New To Date (leave blank to skip): ")

    updates, values = [], []
    if new_name: updates.append("name=%s"); values.append(new_name)
    if new_venue: updates.append("venue=%s"); values.append(new_venue)
    if from_date: updates.append("from_date=%s"); values.append(from_date)
    if to_date: updates.append("to_date=%s"); values.append(to_date)

    if updates:
        sql = f"UPDATE {EVENTS_TABLE} SET {', '.join(updates)} WHERE id=%s AND organizer_id=%s"
        values.extend([event_id, org_id])
        cursor.execute(sql, tuple(values))
        db.commit()
        print("✅ Event updated successfully!")

    else:
        # No main event updates → show sub-events for update
        while True:
            cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
            subs = cursor.fetchall()
            if not subs:
                print("⚠️ No sub-events found for this event.")
                break

            print("\n--- Sub-Events ---")
            for s in subs:
                print(f"{s['id']}. {s['name']} | {s['date']} {s['time']} | Venue: {s['venue']} | Fees: {s['registration_fees']}")

            sub_id = input("Enter Sub-Event ID to update (or 'q' to quit): ")
            if sub_id.lower() == 'q':
                break

            # ask for sub-event updates
            new_sub_name = input("New Sub-Event Name (leave blank to skip): ")
            new_sub_time = input("New Time (HH:MM, leave blank to skip): ")
            new_sub_date = input("New Date (YYYY-MM-DD, leave blank to skip): ")
            new_sub_venue = input("New Venue (leave blank to skip): ")
            new_criteria = input("New Participation Criteria (leave blank to skip): ")
            new_reg_limit = input("New Registration Limit (leave blank to skip): ")
            new_fees = input("New Registration Fees (leave blank to skip): ")
            new_desc = input("New Description (leave blank to skip): ")
            new_first = input("New First Prize (leave blank to skip): ")
            new_second = input("New Second Prize (leave blank to skip): ")
            new_third = input("New Third Prize (leave blank to skip): ")

            sub_updates, sub_values = [], []
            if new_sub_name: sub_updates.append("name=%s"); sub_values.append(new_sub_name)
            if new_sub_time: sub_updates.append("time=%s"); sub_values.append(new_sub_time)
            if new_sub_date: sub_updates.append("date=%s"); sub_values.append(new_sub_date)
            if new_sub_venue: sub_updates.append("venue=%s"); sub_values.append(new_sub_venue)
            if new_criteria: sub_updates.append("criteria=%s"); sub_values.append(new_criteria)
            if new_reg_limit: sub_updates.append("reg_limit=%s"); sub_values.append(int(new_reg_limit))
            if new_fees: sub_updates.append("registration_fees=%s"); sub_values.append(new_fees)
            if new_desc: sub_updates.append("description=%s"); sub_values.append(new_desc)
            if new_first: sub_updates.append("first_prize=%s"); sub_values.append(new_first)
            if new_second: sub_updates.append("second_prize=%s"); sub_values.append(new_second)
            if new_third: sub_updates.append("third_prize=%s"); sub_values.append(new_third)

            if sub_updates:
                sql = f"UPDATE {SUBEVENTS_TABLE} SET {', '.join(sub_updates)} WHERE id=%s AND event_id=%s"
                sub_values.extend([sub_id, event_id])
                cursor.execute(sql, tuple(sub_values))
                db.commit()
                print("✅ Sub-event updated successfully.")
            else:
                print("⚠️ No changes made.")

    db.close()

# ---------------------------
# DELETE EVENT
# ---------------------------
def delete_event(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # fetch all events of this organizer
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE} WHERE organizer_id=%s", (org_id,))
    events = cursor.fetchall()

    if not events:
        print("⚠️ No events found.")
        db.close()
        return

    print("\n--- Your Events ---")
    for ev in events:
        print(f"{ev['id']}. {ev['name']} | {ev['from_date']} to {ev['to_date']} | Venue: {ev['venue']}")

    event_id = input("Enter Event ID to delete: ")

    # confirm delete whole event?
    delete_whole = input("Do you want to delete the whole event and all its sub-events? (y/n): ").lower()

    if delete_whole == 'y':
        cursor.execute(f"DELETE FROM {EVENTS_TABLE} WHERE id=%s AND organizer_id=%s", (event_id, org_id))
        db.commit()
        print("✅ Event and all sub-events deleted successfully!")

    else:
        # fetch sub-events
        cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
        subs = cursor.fetchall()

        if not subs:
            print("⚠️ No sub-events found for this event.")
        else:
            print("\n--- Sub-Events ---")
            for s in subs:
                print(f"{s['id']}. {s['name']} | Date: {s['date']} {s['time']} | Venue: {s['venue']} | Fees: {s['registration_fees']}")

            sub_id = input("Enter Sub-Event ID to delete: ")
            cursor.execute(f"DELETE FROM {SUBEVENTS_TABLE} WHERE id=%s AND event_id=%s", (sub_id, event_id))
            db.commit()
            print("✅ Sub-event deleted successfully!")

    db.close()

# ---------------------------
# VIEW EVENTS
# ---------------------------
def view_events(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE} WHERE organizer_id=%s", (org_id,))
    events = cursor.fetchall()

    if not events:
        print("⚠️ No events found.")
        return

    for ev in events:
        print(f"\n📌 Event: {ev['name']} | Venue: {ev['venue']} | {ev['from_date']} to {ev['to_date']}")

        cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (ev['id'],))
        subs = cursor.fetchall()

        for s in subs:
            print(f"   🔹 {s['name']} | Date: {s['date']} {s['time']} | Venue: {s['venue']}")
            print(f"      Criteria: {s['criteria']} | Limit: {s['reg_limit']}")
            print(f"      Prizes: 🥇 {s['first_prize']} 🥈 {s['second_prize']} 🥉 {s['third_prize']}")
    db.close()


# ---------------------------
# SHARE RESULTS
# ---------------------------
def share_results(org_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # 1. Show events
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE} WHERE organizer_id=%s", (org_id,))
    events = cursor.fetchall()

    if not events:
        print("⚠️ No events available.")
        return

    print("\n--- Select Event ---")
    for ev in events:
        print(f"{ev['id']}. {ev['name']}")
    event_id = input("Enter Event ID: ")

    # 2. Show sub-events
    cursor.execute(f"SELECT * FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
    subs = cursor.fetchall()
    if not subs:
        print("⚠️ No sub-events found.")
        return

    print("\n--- Select Sub-Event ---")
    for s in subs:
        print(f"{s['id']}. {s['name']}")
    sub_id = input("Enter Sub-Event ID: ")

    # 3. Show registered participants
    cursor.execute(f"""
        SELECT r.id, u.fullname, u.username, u.phone
        FROM {REGISTRATIONS_TABLE} r
        JOIN {USERS_TABLE} u ON r.user_id = u.id
        WHERE r.subevent_id=%s
    """, (sub_id,))
    participants = cursor.fetchall()

    if not participants:
        print("⚠️ No participants registered for this sub-event.")
        return

    print("\n--- Registered Participants ---")
    for p in participants:
        print(f"{p['id']}. {p['fullname']} ({p['username']}) | {p['phone']}")

    # 4. Enter winners
    first = input("Enter First Prize Winner ID: ")
    second = input("Enter Second Prize Winner ID: ")
    third = input("Enter Third Prize Winner ID: ")

    # get names based on IDs
    winners = {}
    for pid in [first, second, third]:
        cursor.execute(f"SELECT fullname FROM {USERS_TABLE} u JOIN {REGISTRATIONS_TABLE} r ON u.id=r.user_id WHERE r.id=%s", (pid,))
        row = cursor.fetchone()
        if row:
            winners[pid] = row["fullname"]

    cursor.execute(f"""
        INSERT INTO {RESULTS_TABLE} (subevent_id, first, second, third)
        VALUES (%s,%s,%s,%s)
    """, (sub_id, winners.get(first), winners.get(second), winners.get(third)))
    db.commit()
    db.close()

    print("✅ Results shared successfully!")

# ---------------------------
# DASHBOARD
# ---------------------------
def organizer_dashboard(organizer):
    while True:
        print("\n--- Organizer Dashboard ---")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. Check Profile Status")  # moved to option 3
        print("4. Create Event")          # moved to option 4
        print("5. Update Event")
        print("6. Delete Event")
        print("7. View Events")
        print("8. Share Results")
        print("9. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_profile(organizer["id"])
        elif choice == "2":
            update_profile(organizer["id"])
        elif choice == "3":  # Check Profile Status
            check_profile_status(organizer["id"])
        elif choice == "4":  # Create Event
            if organizer["status"] != "approved":
                print("⚠️ You cannot access this option until admin approval.")
            else:
                create_event(organizer["id"])
        elif choice == "5":
            if organizer["status"] != "approved":
                print("⚠️ You cannot access this option until admin approval.")
            else:
                update_event(organizer["id"])
        elif choice == "6":
            if organizer["status"] != "approved":
                print("⚠️ You cannot access this option until admin approval.")
            else:
                delete_event(organizer["id"])
        elif choice == "7":
            if organizer["status"] != "approved":
                print("⚠️ You cannot access this option until admin approval.")
            else:
                view_events(organizer["id"])
        elif choice == "8":
            if organizer["status"] != "approved":
                print("⚠️ You cannot access this option until admin approval.")
            else:
                share_results(organizer["id"])
        elif choice == "9":
            print("👋 Logged out.")
            break
        else:
            print("⚠️ Invalid choice.")

# ---------------------------
# MAIN ENTRY
# ---------------------------
def organizer_module_menu():
    while True:
        print("\n--- Organizer Module ---")
        print("1. Sign Up")
        print("2. Log In")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1": signup()
        elif choice == "2": login()
        elif choice == "3": break
        else: print("⚠️ Invalid choice.")
