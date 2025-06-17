import datetime

def validate_date(date_str):
    """Validate date format and return date object"""
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")



from database.db import get_connection
import datetime

def add_user(conn,name, phone=None, email=None):
    if not name:
        raise ValueError("Name is required")
    
    cursor = conn.cursor()

    # Check if user exists by phone or email
    cursor.execute(
        '''SELECT id FROM users WHERE phone = ? OR email = ?''',
        (phone, email)
    )
    result = cursor.fetchone()

    if result:
        # print(f"[INFO] User already exists: {name}")
        # conn.close()
        return result[0]  # return existing user_id

    # Insert new user
    cursor.execute(
    '''INSERT INTO users (name, phone, email, created_at)
       VALUES (?, ?, ?, ?)''',
    (name, phone , email if email else None, datetime.datetime.now())
)
    user_id = cursor.lastrowid
    conn.commit()
    
    # print(f"[OK] New user added: {name}")
    return user_id
