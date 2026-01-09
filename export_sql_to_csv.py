import sqlite3
import pandas as pd

con = sqlite3.connect("mental-health-group.db", check_same_thread=False)
cur = con.cursor()

pd.read_sql(
    "SELECT * FROM group_sessions", con
).to_csv('./tables/groups.csv')
pd.read_sql(
    "SELECT * FROM customers", con
).to_csv('./tables/customers.csv')
pd.read_sql(
    "SELECT * FROM conversions", con
).to_csv('./tables/conversions.csv')
pd.read_sql(
    "SELECT * FROM triggers", con
).to_csv('./tables/triggers.csv')
pd.read_sql(
    "SELECT * FROM bookings", con
).to_csv('./tables/bookings.csv')
