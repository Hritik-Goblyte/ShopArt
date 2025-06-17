
def get_next_bill_number(conn, prefix='SA'):
    c = conn.cursor()
    
    # Get the next sequence number
    c.execute("SELECT next_number FROM bill_sequence WHERE prefix = ?", (prefix,))
    result = c.fetchone()
    
    if not result:
        # Initialize if not exists
        c.execute("INSERT INTO bill_sequence (prefix, next_number) VALUES (?, 1)", (prefix,))
        next_number = 1
    else:
        next_number = result[0]
    
    # Format the bill number
    bill_number = f"{prefix}{next_number:03d}"
    
    # Update the sequence
    c.execute("UPDATE bill_sequence SET next_number = next_number + 1 WHERE prefix = ?", (prefix,))
    conn.commit()
    
    return bill_number