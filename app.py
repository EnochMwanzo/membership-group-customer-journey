from flask import Flask, request, render_template
import sqlite3

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
con = sqlite3.connect("mental-health-group.db", check_same_thread=False)
cur = con.cursor()

def convert_to_dict(result):
    columns = [description[0] for description in result.description]
    for row in result.fetchall():
        result = dict(zip(columns, row))
    return result

def email(template, customer_data_dict):
    customer = customer_data_dict
    sender_email = "MentalHealthGroup@localhost.pc"
    receiver_email = customer['username'] + ''.join("@localhost.pc")
    password='abc'
    message = MIMEMultipart("alternative")
    message["Subject"] = "Message from MHG"
    message["From"] = sender_email
    message["To"] = receiver_email

    part = MIMEText(template, "html")

    message.attach(part)

    with smtplib.SMTP("localhost", 25) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

@app.route("/signup", methods=["POST"])
def signup():
    customer_id = (request.json.get('customer_id'))
    cur.execute(
        "UPDATE conversions SET signup = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    result = convert_to_dict(cur.execute(
        "SELECT signup FROM conversions WHERE customer_id = ?", [customer_id] 
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
    ))
    template = render_template("email.html", customer=customer_data)
    email(template)
    return f'{result}\n'

@app.route("/upgrade", methods=["POST"])
def upgrade():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE conversions SET upgrade = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    cur.execute(
        "UPDATE customers SET paying_member = 'TRUE' WHERE id = ?", [customer_id]
    )
    con.commit()
    result = cur.execute(
        "SELECT upgrade FROM conversions WHERE customer_id = ?", [customer_id]
    ).fetchone()
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
    ))
    group_recommendation_one = convert_to_dict(cur.execute(
        "SELECT * FROM group_sessions ORDER BY RANDOM() LIMIT 1"
    ))
    group_recommendation_two = convert_to_dict(cur.execute(
        "SELECT * FROM group_sessions ORDER BY RANDOM() LIMIT 1"
    ))
    groups = [group_recommendation_one, group_recommendation_two]
    template = render_template("thanks-for-joining.html", customer=customer_data, groups=groups)
    email(template, customer_data)
    return f'{result}\n'

@app.route("/logins", methods=["POST"])
def logins():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE triggers SET number_of_logins = number_of_logins + 1 WHERE customer_id = ?", [customer_id]
    )
    result = cur.execute(
        "SELECT number_of_logins FROM triggers WHERE customer_id = ?", [customer_id]
    ).fetchone()
    return f"Number of logins, {result[0]}\n"

@app.route("/lapsed", methods=["POST"])
def lapsed():
    customer_id = request.json.get('customer_id')
    last = cur.execute(
        "SELECT days_since_last_session FROM customers WHERE id = ?", [customer_id]
    ).fetchone()
    if last[0] > 90:
        cur.execute(
        "UPDATE triggers SET lapsed = 'TRUE' WHERE customer_id = ?", [customer_id]
        )
        con.commit()
        result = convert_to_dict(cur.execute(
            "SELECT lapsed FROM triggers WHERE customer_id = ?", [customer_id]
        ))
        customer_data = convert_to_dict(cur.execute(
            "SELECT * FROM customers WHERE id = ?", [customer_id]
        ))
        template = render_template("lapsed.html", customer=customer_data)
        email(template, customer_data)
        return f'{result}\n'
    else:
        return "Days until lapse", 90 - last

@app.route("/re-engage", methods=["POST"])
def re_engage():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE conversions SET re_engage = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    cur.execute(
        "UPDATE triggers SET lapsed = 'FALSE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    cur.execute(
        "UPDATE customers SET days_since_last_session = 0 WHERE customer_id = ?", [customer_id]
    )
    result = convert_to_dict(cur.execute(
        "SELECT * FROM conversions WHERE customer_id = ?", [customer_id]
    ))
    return f'{result}\n'

@app.route("/checked-features", methods=["POST"])
def checked_features():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE conversions SET checked_features = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    result = convert_to_dict(cur.execute(
        "SELECT checked_features FROM conversions WHERE customer_id = ?", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
    ))
    template = render_template("checked-features.html", customer=customer_data)
    email(template, customer_data)
    return f'{result}\n'

@app.route("/attend-first-session", methods=["POST"])
def attend_first_session():
    response = request.json.get('customer_id')
    cur.execute(
        "UPDATE conversions SET attend_first_session = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    result = convert_to_dict(cur.execute(
        "SELECT * FROM conversions WHERE customer_id = ?", [customer_id]
    ))
    return f'{result}\n'

@app.route("/attend-first-paid-session", methods=["POST"])
def attend_first_paid_session():
    customer_id = request.json.get('customer_id')
    status = cur.execute(
        "SELECT paying_member FROM customers WHERE id = ?", [customer_id]
    ).fetchone()[0]
    if status == 'FALSE':
        return "Can't attend paid\n"
    else:
        #probably should check bookings if there is at least COUNT one session booked by the customer id
        cur.execute(
            "UPDATE conversions SET attend_first_paid_session = 'TRUE' WHERE customer_id = ?", [customer_id]
        )
        con.commit()
        result = convert_to_dict(cur.execute(
            "SELECT * FROM conversions WHERE customer_id = ?", [customer_id]
        ))
        template = render_template("first-paid-session.html", customer=result)
        email(template, result)
        return f'{result}\n'

@app.route("/cancel", methods=["POST"])
def cancel():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE customers SET paying_member = 'FALSE' WHERE id = ?", [customer_id]
    )
    con.commit()
    cur.execute(
        "UPDATE triggers SET cancel = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    result = convert_to_dict(cur.execute(
        "SELECT paying_member, cancel FROM customers JOIN triggers ON id=customer_id WHERE customer_id = ?", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
            "SELECT * FROM customers WHERE id = ?", [customer_id]
        ))
    template = render_template("cancel.html", customer=customer_data)
    email(template, customer_data)
    return f'{result}\n'

@app.route("/renew", methods=["POST"])
def renew():
    customer_id = request.json.get('customer_id')
    cur.execute(
        "UPDATE customers SET paying_member = 'TRUE' WHERE id = ?", [customer_id]
    )
    con.commit()
    cur.execute(
        "UPDATE triggers SET cancel = 'FALSE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
    result = convert_to_dict(cur.execute(
        "SELECT paying_member, cancel FROM customers JOIN triggers ON id=customer_id WHERE customer_id = ?", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
    ))
    group_recommendation_one = convert_to_dict(cur.execute(
        "SELECT * FROM group_sessions ORDER BY RANDOM() LIMIT 1"
    ))
    group_recommendation_two = convert_to_dict(cur.execute(
        "SELECT * FROM group_sessions ORDER BY RANDOM() LIMIT 1"
    ))
    groups = [group_recommendation_one, group_recommendation_two]
    template = render_template("renew.html", customer=customer_data, groups=groups)
    email(template, customer_data)
    return f'{result}\n'

@app.route("/bookings", methods=["POST"])
def bookings():
    customer_id = (request.json.get('customer_id'))
    booked_session_id = (request.json.get('booked_session_id'))
    cur.execute(
        "INSERT INTO bookings (customer_id, booked_session_id) VALUES (?, ?)", [customer_id, booked_session_id]
    )
    con.commit()
    #in order to retrieve the right result, you must know the specific booked session, since a customer can book the same group multiple times. here the result will be the latest booking
    result = convert_to_dict(cur.execute(
        "SELECT MAX(id), * FROM bookings WHERE customer_id = ?", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers JOIN bookings ON customers.id = bookings.customer_id WHERE customers.id = ?", [customer_id]
    ))
    group_data = convert_to_dict(cur.execute(
        "SELECT MAX(bookings.id) as booked_session_id, session_name FROM group_sessions JOIN bookings ON group_sessions.id = bookings.booked_session_id WHERE booked_session_id = ?", [booked_session_id]
    ))
    template = render_template("booked-session-confirmation.html", customer=customer_data, group=group_data)
    email(template, customer_data)
    return f'{result}\n{group_data}\n'

@app.route("/qualify-for-group-leader", methods=["POST"])
def qualify():
    customer_id = (request.json.get('customer_id'))
    number_of_sessions = convert_to_dict(cur.execute(
        "SELECT COUNT (*) AS number_of_sessions FROM bookings WHERE customer_id = ? AND attended = 'TRUE'", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers JOIN bookings ON customers.id = bookings.customer_id WHERE customers.id = ?", [customer_id]
        ))
    if number_of_sessions['number_of_sessions'] > 50 and customer_data['paying_member'] == 'TRUE':
        cur.execute(
            "UPDATE customers SET qualified_for_leader = 'TRUE' WHERE id = ?", [customer_id]
        )
        template = render_template("qualify-for-leader.html", customer=customer_data)
        return f'qualified to be group leader\n'
    else:
        return f'not qualfied for group leader\n'

@app.route("/approved", methods=["POST"])
def approved():
    customer_id = request.json.get('customer_id')
    booked_session_id = request.json.get('booked_session_id')
    cur.execute(
        "UPDATE customers SET leader = 'TRUE' WHERE id = ?", [customer_id]
    )
    con.commit()
    result = convert_to_dict(cur.execute(
        "SELECT leader FROM customers WHERE id = ?", [customer_id]
    ))
    customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers JOIN bookings ON customers.id = bookings.customer_id WHERE customers.id = ?", [customer_id]
    ))
    group_data = convert_to_dict(cur.execute(
        "SELECT *, session_name FROM group_sessions JOIN bookings ON group_sessions.id = bookings.booked_session_id WHERE booked_session_id = ?", [booked_session_id]
    ))
    template = render_template("approved.html", customer=customer_data, group=group_data)
    email(template, customer_data)
    return f'{result}\n'

@app.route("/lead-first-session", methods=["POST"])
def lead_first_session():
    customer_id = (request.json.get('customer_id'))
    check = cur.execute(
        "SELECT COUNT(role) FROM bookings WHERE role = 'leader' and customer_id = ?", [customer_id]
    ).fetchone()[0]
    if check == 1:
        cur.execute(
            "UPDATE conversions SET lead_first_session = 'TRUE' WHERE customer_id = ?", [customer_id]
        )
        con.commit()
        result = convert_to_dict(cur.execute(
            "SELECT leader FROM customers WHERE id = ?", [customer_id]
        ))
        customer_data = convert_to_dict(cur.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
        ))
        template = render_template("lead-first-session.html", customer=customer_data)
        email(template, customer_data)
        return f'{result}\n'

if __name__ == '__main__':
    app.run(debug=True, port='5001')
