import sqlite3, random
import pandas as pd

con = sqlite3.connect("mental-health-group.db")
cur = con.cursor()

def generate_data():
    with open('schema.sql') as f:
        cur.executescript(f.read())
    for i in range(11):
        cur.execute('INSERT INTO customers (username, age, gender, mental_health_challenge, device) VALUES (?, ?, ?, ?, ?)', [
            ''.join(random.choices(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], k=6)),
            random.randint(18, 65),
            random.choice(['M', 'F']),
            random.choice(['mental health challenge A', 'mental health challenge B', 'mental health challenge C', 'mental health challenge D', 'N/A']),
            random.choice(['Desktop', 'Mobile', 'Tablet'])
        ])
        con.commit()
        cur.execute(
            "INSERT INTO conversions (customer_id) VALUES (?)", [i]
        )
        con.commit()
        cur.execute(
            "INSERT INTO triggers (customer_id) VALUES (?)", [i]
        )
        con.commit()
        cur.execute(
            "INSERT INTO bookings (customer_id) VALUES (?)", [i]
        )
        con.commit()
    groups = [
        ['A','Mens','Young'],
        ['B','Mens','Young'],
        ['C','Mens','Young'],
        ['D','Mens','Young'],
        ['General','Mens','Young'],
        ['A','Womens','Young'],
        ['B','Womens','Young'],
        ['C','Womens','Young'],
        ['D','Womens','Young'],
        ['General',	'Womens','Young'],
        ['A','Mixed','Young'],
        ['B','Mixed','Young'],
        ['C','Mixed','Young'],
        ['D','Mixed','Young'],
        ['General',	'Mixed','Young'],
        ['A','Mens','Older'],
        ['B','Mens','Older'],
        ['C','Mens','Older'],
        ['D','Mens','Older'],
        ['General',	'Mens','Older'],
        ['A','Womens','Older'],
        ['B','Womens','Older'],
        ['C','Womens','Older'],
        ['D','Womens','Older'],
        ['General',	'Womens','Older'],
        ['A','Mixed','Older'],
        ['B','Mixed','Older'],
        ['C','Mixed','Older'],
        ['D','Mixed','Older'],
        ['General',	'Mixed','Older']
    ]
    for i in groups:
        cur.execute(
            "INSERT INTO group_sessions (session_name, session_description, schedule) VALUES (?, ?, ?)", [f'{i[2]} {i[1]} group for mental health challenge {i[0]}', f'This group is for {i[2]} {i[1]} who are dealing with mental health challenge {i[0]}. It is a safe place to talk about {i[1]} and find solutions to your problems.', random.choice(['weekly', 'bi-weekly', 'monthly'])]
        )
        con.commit()

generate_data()
con.close()
