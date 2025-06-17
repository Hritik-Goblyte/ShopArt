def get_tax_rate(conn):
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='tax_rate'")
    row = c.fetchone()
    return float(row[0]) if row else 0.05

def set_tax_rate(conn, new_rate):
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='tax_rate'", (str(new_rate),))
    conn.commit()
    print(f"✅ Tax rate updated to {new_rate*100:.2f}%")



def update_password(file_path, new_password):
    lines = []
    key_found = False

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('PASSWORD='):
                # Handle quotes if present
                quote = "'" if "'" in line else '"' if '"' in line else ''
                lines.append(f'PASSWORD={quote}{new_password}{quote}\n')
                key_found = True
            else:
                lines.append(line)
    
    if not key_found:
        # Add PASSWORD line if not present
        lines.append(f'PASSWORD=\'{new_password}\'\n')

    with open(file_path, 'w') as file:
        file.writelines(lines)



