# membership-group-customer-journey
There are many different tools for automating marketing campaigns like Braze, Klaviyo, Iterable, Cordial, and others. I created this project to show how I would code a customer journey using Python, since I am already familiar with it. I use a membership group that hosts group sessions to talk about for mental health as an example, and I use Flask to handle creating and sending emails to a fake SMTP server running locally, <a href=https://github.com/rnwood/smtp4dev/tree/master> smtp4dev </a>. I hope this project demonstrates that I understand the fundaments of email automation and that these ideas can be applied using a variety ESPs.

### What is the goal of the campaign
The goal of the group would be to have loyal group members paying for their membership. Customers will not start out that way, so by working backwards we would realize that in order to be loyal the customer has to interact with the group for some time, and the customer has to feel the value of the group before they start paying. One process for getting the customer to this could be:

- Customer signs up to become part of the group
- Customer joins a free group session
- Customer upgrades to a paid membership
- Customer joins paid group sessions
- Customer joins group sessions on a regular basis and can be considered loyal

These are conversions events that we would want to keep track of. We can use a database (Tracking of customer sessions will come later):

```sql
CREATE TABLE conversions(
    signup BOOLEAN DEFAULT 'FALSE',
    upgrade BOOLEAN DEFAULT 'FALSE', 
    attend_first_session BOOLEAN DEFAULT 'FALSE',
    attend_first_paid_session BOOLEAN DEFAULT 'FALSE'
);
```
### who will be customers
The group serves people dealing with certain mental health challenges or people who simply want to joing a group focused on wellness. The group may be more appealing to certain demographics, and we will want to use specific customer attributes in messaging, so we can track these as well:
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    device TEXT,
    username TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    mental_health_challenge TEXT,
    paying_member BOOLEAN DEFAULT 'FALSE'
);
```
### Sending messages
Now that we have all this information, we can use it to message the customers. For example if we want to send a welcome email to a customer after signing up, we would send a request like `curl -X POST -H "Content-Type: application/json" -d '{"customer_id": [customer_id]' [server url]}`
:
```py
@app.route("/signup", methods=["POST"])
def signup():
    customer_id = (request.json.get('customer_id'))
```
Then we would update the database to show that the customer did sign up
```py
    cur.execute(
        "UPDATE conversions SET signup = 'TRUE' WHERE customer_id = ?", [customer_id]
    )
    con.commit()
```
To check if the database was updated, I select the data I just updated and return it to the terminal. The `convert_to_dict` function was based on <a href="https://www.slingacademy.com/article/python-converting-an-sqlite-database-to-json-and-vice-versa/">this</a> and makes the result easier to read.
```py
    result = convert_to_dict(cur.execute(
        "SELECT signup FROM conversions WHERE customer_id = ?", [customer_id] 
    ))
    return f'{result}\n'
```
Customer data is selected to use as data to be inserted into an email template, and sent to the customer
```py
customer_data = convert_to_dict(cur.execute(
    "SELECT * FROM customers WHERE id = ?", [customer_id]
))
template = render_template("email.html", customer=customer_data)
email(template)
```
Snippet of the html
```html
<p>
  Dear {{ customer['username'] }},
</p>
<p style="margin: auto 2em;">
  {{ customer['mental_health_challenge'] }} is hard to deal with on your own. Our group can help. We have sessions for {% if customer['age'] < 30 %} young {% endif %} {% if customer['gender'] =='F' %} women {% else %} men {% endif %} going through the same thing. When you're ready, check out what other people have to say about the group. {% if customer['device'] in ['Mobile', 'Tablet'] %} You may want to download our <a href="#"> {{ customer['device'] }} app.</a> {% endif %}
</p>
<p>
  Sincerely, The Mental Health Group Team
</p>
```
Here are a couple examples of how the final email would look in an inbox. I used random functions to generate usernames and random customer attributes.
<div style="display:flex; justify-content:space-between;"> 
<img src="https://github.com/EnochMwanzo/membership-group-customer-journey/blob/main/examples/welcome-email-example-1.png" alt="welcome email example 1" style="display: inline-block; width: 40%;">
<img src="https://github.com/EnochMwanzo/membership-group-customer-journey/blob/main/examples/welcome-email-example-2.png" alt="welcome email example 2" style="display: inline-block; width: 40%;">
</div>
The code has similar functions for every conversion event and some other situations I thought of where the group may need to email a customer. The database also has data on the groups and sessions that customers sign up for. I will eventually write about them all here. For example I included a sequence where a loyal paying member can become a leader for group sessions.

```py
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
```
