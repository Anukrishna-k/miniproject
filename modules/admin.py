# admin.py
# admin.py
from tabulate import tabulate
from modules.db import connect_db
from models import USERS_TABLE, ORGANIZERS_TABLE, EVENTS_TABLE, ADMIN_TABLE
import getpass
from modules.db import connect_db, hash_password
from models import ADMIN_TABLE
from models import REGISTRATIONS_TABLE, SUBEVENTS_TABLE  
import psycopg2.extras



def admin_login():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM {ADMIN_TABLE} WHERE username=%s AND password=%s",
        (username, password)
    )

    result = cursor.fetchone()
    db.close()

    if result:
        print("✅ Login successful!\n")
        return True
    else:
        print("❌ Invalid credentials.")
        return False


def view_users():
    db = connect_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f"SELECT id, fullname, username, email, phone, dob, address FROM {USERS_TABLE}")
    users = cursor.fetchall()
    db.close()

    if not users:
        print("\n⚠️ No users found.")
        return

    print("\n📋 Registered Users:")
    print(tabulate(users, headers="keys", tablefmt="psql"))


def view_organizers():
    db = connect_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f"""
    SELECT id, fullname, username, email, phone, dob, address, adhaar, status
    FROM {ORGANIZERS_TABLE}
""")
    orgs = cursor.fetchall()
    db.close()

    if not orgs:
        print("\n⚠️ No organizers found.")
        return

    print("\n📋 Registered Organizers:")
    print(tabulate(orgs, headers="keys", tablefmt="psql"))


def view_events():
    db = connect_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f"SELECT id, name, from_date, to_date, venue,  organizer_id FROM {EVENTS_TABLE}")
    events = cursor.fetchall()
    db.close()

    if not events:
        print("\n⚠️ No events found.")
        return

    print("\n📋 All Events:")
    print(tabulate(events, headers="keys", tablefmt="psql"))


def delete_event():
    db = connect_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # ❌ Fixed: removed extra comma after 'venue'
    cursor.execute(f"SELECT id, name, venue FROM {EVENTS_TABLE}")
    events = cursor.fetchall()

    if not events:
        print("\n⚠️ No events available to delete.")
        db.close()
        return

    # ✅ Display events
    print("\n📋 Events List:")
    print(tabulate(events, headers="keys", tablefmt="psql"))

    # ✅ Validate event ID input
    event_id = input("Enter Event ID to delete: ").strip()

    # ✅ Check if event exists before deleting
    cursor.execute(f"SELECT * FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if not event:
        print("⚠️ Invalid Event ID. Please try again.")
        db.close()
        return

    confirm = input(f"⚠️ Are you sure you want to delete '{event['name']}' (Event ID: {event_id})? (y/n): ").lower()
    if confirm == "y":
        cursor.execute(f"DELETE FROM {EVENTS_TABLE} WHERE id = %s", (event_id,))
        db.commit()
        print("🗑 Event deleted successfully.")
    else:
        print("❌ Deletion cancelled.")

    db.close()

def approve_organizers():
    db = connect_db()
    import psycopg2.extras
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)


    # Fetch only pending organizers
    cursor.execute(f"SELECT id, fullname, username, email, phone, status FROM {ORGANIZERS_TABLE} WHERE status='pending'")
    organizers = cursor.fetchall()

    if not organizers:
        print("\nℹ No organizers pending approval.")
        db.close()
        return

    print("\n📋 Pending Organizers:")
    print(tabulate(organizers, headers="keys", tablefmt="psql"))

    org_id = input("Enter Organizer ID to review: ")
    action = input("Approve (a) / Reject (r): ").lower()

    if action == "a":
        cursor.execute(f"UPDATE {ORGANIZERS_TABLE} SET status='approved' WHERE id=%s", (org_id,))
        db.commit()
        print("✅ Organizer approved!")
    elif action == "r":
        cursor.execute(f"UPDATE {ORGANIZERS_TABLE} SET status='rejected' WHERE id=%s", (org_id,))
        db.commit()
        print("❌ Organizer rejected!")
    else:
        print("⚠️ Invalid action.")

    db.close()

def view_attendees():
    db = connect_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # 1. Show Events
    cursor.execute(f"SELECT id, name FROM {EVENTS_TABLE}")
    events = cursor.fetchall()
    if not events:
        print("\n⚠️ No events available.")
        db.close()
        return

    print("\n📋 Available Events:")
    print(tabulate(events, headers="keys", tablefmt="psql"))

    event_id = input("Enter Event ID to view sub-events: ")

    # 2. Show Sub-events of chosen Event
    cursor.execute(f"SELECT id, name FROM {SUBEVENTS_TABLE} WHERE event_id=%s", (event_id,))
    subevents = cursor.fetchall()
    if not subevents:
        print("\n⚠️ No sub-events available for this event.")
        db.close()
        return

    print("\n📋 Sub-events:")
    print(tabulate(subevents, headers="keys", tablefmt="psql"))

    subevent_id = input("Enter Sub-event ID to view attendees: ")

    # 3. Show Attendees of chosen Sub-event
    query = f"""
        SELECT r.id, u.fullname AS participant, u.email, u.phone
        FROM {REGISTRATIONS_TABLE} r
        JOIN {USERS_TABLE} u ON r.user_id = u.id
        WHERE r.subevent_id = %s
    """
    cursor.execute(query, (subevent_id,))
    attendees = cursor.fetchall()
    db.close()

    if not attendees:
        print("\n⚠️ No attendees registered for this sub-event.")
        return

    print("\n📋 Attendees for Selected Sub-event:")
    print(tabulate(attendees, headers="keys", tablefmt="psql"))




def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. View Users")
        print("2. View Organizers")
        print("3. View Events")
        print("4. Approve Organizers")   # ✅ changed
        print("6. Delete Event")
        print("7. View Attendees")      # ✅ new
        print("8. Logout")

        choice = input("Enter choice: ")
        if choice == "1":
            view_users()
        elif choice == "2":
            view_organizers()
        elif choice == "3":
            view_events()
        elif choice == "4":
            approve_organizers()
        elif choice == "6":
            delete_event()
        elif choice == "7":
            view_attendees()
        elif choice == "8":
            break
        else:
            print("⚠️ Invalid choice.")
