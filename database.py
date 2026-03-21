import sqlite3
from datetime import date , timedelta


def init_db():

    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    gender TEXT NULL,
                    joining_date TEXT NULL,
                    subs_end_date TEXT NULL,
                    plan TEXT NULL,
                    status TEXT NULL
                )
                   
                """
                )
    
    conn.commit()
    conn.close()


def add_member(name , phone , gender , joining_date , subs_end_date , plan , status):

    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()

    cursor.execute("""
                    INSERT INTO members (name , phone , gender , joining_date , subs_end_date , plan , status) VALUES ( ? , ? , ? , ? , ? , ? , ?)
                   """,(name , phone , gender , joining_date , subs_end_date , plan , status)
    )
    conn.commit()
    conn.close()

# add_member("dev" , "8282828" , "male" , "2026-03-10" , "2026-03-22" , "3 months" , "paid")

def fetch_all_members():
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    
    members = cursor.fetchall()

    conn.close()

    return members

def get_expiring_soon():

    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()

    today = date.today()
    ten_days_later = today + timedelta(days=10)

    today_str = today.strftime("%Y-%m-%d")
    ten_days_later_str = ten_days_later.strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM members WHERE subs_end_date BETWEEN ? AND ?" , (today_str , ten_days_later_str))

    members = cursor.fetchall()

    conn.close()

    return members

def update_payment_status(member_id , status):
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE members SET status = ? WHERE id = ? " , (status , member_id))

    conn.commit()
    conn.close()

def run_query(sql):
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()

    return result

def delete_member(member_id):
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = ?" , (member_id , ))
    conn.commit()
    conn.close()

def update_member(name , phone , gender , joining_date , subs_end_date , plan , status , member_id):
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET name = ? , phone = ? , gender = ? , joining_date = ? , subs_end_date = ? , plan = ? , status = ? WHERE id = ?" , (name , phone , gender , joining_date , subs_end_date , plan , status , member_id ) )
    conn.commit()
    conn.close()

def member_by_id(memberid):
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ? " , (memberid ,))
    member = cursor.fetchone()
    conn.close()
    return member

def get_all_unpaid():
    status = "Unpaid"
    conn = sqlite3.connect("kailash_gym.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE STATUS = ?" , (status ,))

    members = cursor.fetchall()
    conn.close()
    return members

