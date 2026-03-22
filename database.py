from datetime import date , timedelta
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
        return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    gender TEXT ,
                    joining_date TEXT ,
                    subs_end_date TEXT ,
                    plan TEXT ,
                    status TEXT 
                )
                   
                """
                )
    
    conn.commit()
    conn.close()
    


def add_member(name , phone , gender , joining_date , subs_end_date , plan , status , plan_amount , amount_paid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                    INSERT INTO members (name , phone , gender , joining_date , subs_end_date , plan , status , plan_amount , amount_paid) VALUES ( %s , %s , %s , %s , %s , %s , %s , %s , %s)
                   """,(name , phone , gender , joining_date , subs_end_date , plan , status , plan_amount , amount_paid)
    )
    conn.commit()
    conn.close()

def fetch_all_members():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    
    members = cursor.fetchall()

    conn.close()
    return members

def get_expiring_soon():

    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()
    ten_days_later = today + timedelta(days=10)

    today_str = today.strftime("%Y-%m-%d")
    ten_days_later_str = ten_days_later.strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM members WHERE subs_end_date BETWEEN %s AND %s" , (today_str , ten_days_later_str))

    members = cursor.fetchall()
    conn.close()
    return members

def update_payment_status(member_id , status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE members SET status = %s  WHERE id = %s " , (status , member_id))

    conn.commit()
    conn.close()

def run_query(sql):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    
    conn.close()
    return result

def delete_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = %s" , (member_id , ))
    conn.commit()
    conn.close()

def update_member(name , phone , gender , joining_date , subs_end_date , plan , status , plan_amount , amount_paid , member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET name = %s , phone = %s , gender = %s , joining_date = %s , subs_end_date = %s , plan = %s , status = %s , plan_amount = %s , amount_paid = %s WHERE id = %s" , (name , phone , gender , joining_date , subs_end_date , plan , status, plan_amount , amount_paid , member_id ) )
    conn.commit()
    conn.close()

def member_by_id(memberid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = %s " , (memberid ,))
    member = cursor.fetchone()
    conn.close()
    return member

def get_all_unpaid():
    status = "Unpaid"
    conn =get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE STATUS = %s" , (status ,))

    members = cursor.fetchall()
    conn.close()
    return members

def get_members_by_date(start_date , end_date):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * from members  WHERE joining_date BETWEEN  %s AND %s" , (start_date , end_date))
    all_members = cursor.fetchall()
    conn.close()
    return all_members

def total_revenue(start_date , end_date):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount_paid) FROM members  WHERE joining_date BETWEEN %s AND %s" , (start_date , end_date))
    all_members = cursor.fetchone()[0]
    conn.close()
    return all_members
