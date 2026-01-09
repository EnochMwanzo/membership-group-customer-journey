DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS conversions;
DROP TABLE IF EXISTS group_sessions;
DROP TABLE IF EXISTS triggers;
DROP TABLE IF EXISTS bookings;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    device TEXT,
    username TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    mental_health_challenge TEXT,
    paying_member BOOLEAN DEFAULT 'FALSE',
    qualified_for_leader BOOLEAN DEFAULT 'FALSE',
    leader BOOLEAN DEFAULT 'FALSE',
    days_since_signup INTEGER DEFAULT 0,
    days_since_membership INTEGER DEFAULT 0,
    days_since_last_session INTEGER DEFAULT 0
);

CREATE TABLE conversions /*action customer is to do after receiving email*/(
    customer_id INTEGER,
    signup BOOLEAN DEFAULT 'FALSE',
    upgrade BOOLEAN DEFAULT 'FALSE', 
    re_engage BOOLEAN DEFAULT 'FALSE',
    checked_features BOOLEAN DEFAULT 'FALSE',
    attend_first_session BOOLEAN DEFAULT 'FALSE',
    attend_first_paid_session BOOLEAN DEFAULT 'FALSE',
    lead_first_session BOOLEAN DEFAULT 'FALSE',
    test_group TEXT,
    FOREIGN KEY(customer_id) REFERENCES customer(id)
);

CREATE TABLE group_sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT,
    session_description TEXT,
    number_of_members INTEGER DEFAULT 0,
    tags TEXT,
    schedule TEXT
);

CREATE TABLE triggers /*things a customer does that lead to email*/(
    customer_id INTEGER,
    number_of_logins INTEGER DEFAULT 0,
    scheduled_new_session BOOLEAN DEFAULT 'FALSE',
    cancel BOOLEAN DEFAULT 'FALSE',
    lapsed BOOLEAN DEFAULT 'FALSE',
    qualified_for_leader BOOLEAN DEFAULT 'FALSE',
    FOREIGN KEY(customer_id) REFERENCES customer(id)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    booked_session_id INTEGER,
    group_role TEXT DEFAULT 'member',
    attended BOOLEAN DEFAULT 'FALSE',
    FOREIGN KEY(customer_id) REFERENCES customer(id),
    FOREIGN KEY(booked_session_id) REFERENCES group_sessions(id)
);

