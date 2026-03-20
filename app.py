import streamlit as st
from database import add_member , fetch_all_members , get_expiring_soon , update_payment_status , run_query , init_db
import pandas as pd
from datetime import date , timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
init_db()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.title("Kailash Gym")

page = st.sidebar.selectbox(
    "Options",
    ("Dashboard" , "Add Member" , "Update Status" , "Ask AI")
)


if page == "Dashboard":
    all_members = fetch_all_members()
    expiring_plan_members = get_expiring_soon()

    if expiring_plan_members:
        st.warning(f"{len(expiring_plan_members)} members plan expires soon !" ,icon="⚠️")
    checkbox = st.checkbox("Get all Expiring Plan Members ")

    if checkbox:
        st.dataframe(pd.DataFrame(expiring_plan_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status"]))
    else:
        df = pd.DataFrame(all_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status"])

        st.dataframe(df)

    

    


if page == "Add Member":

    today = date.today()

    name = st.text_input("Name")
    phone = st.text_input("Phone No ")
    gender = st.selectbox( "Gender" , ("Male" , "Female"))
    plan = st.selectbox("Plan" , ("1 Month" , "3 Month" , "6 Month" , "12 Month"))
    status = st.selectbox("Fees Status" , ("Paid" , "Unpaid"))
    joining_date = st.date_input("Joining Date")

    if plan == "1 Month":
        end_date = today + timedelta(days=31)

    elif plan == "3 Month" :
        end_date = today + timedelta(days=92)

    elif plan == "6 Month" :
        end_date = today + timedelta(days=184)

    elif plan == "12 Month" :
        end_date = today + timedelta(days=365)

    subs_end_date = st.date_input("End date " , end_date)

    button = st.button("Submit" , type="primary")

    if button:
        add_member(name , phone , gender , str(joining_date) , str(subs_end_date) ,plan , status )
        st.success("Member added succesfully !")

if page == "Update Status":

    all_members = fetch_all_members()

    search = st.text_input("Search")

    filtered = [m for m in all_members if search.lower() in m[1].lower()]

    member_options = {f"{m[1]} - {m[2]} ": m[0] for m in filtered}
    selected_name = st.selectbox("Select Member" , list(member_options.keys()))
    selected_id = member_options[selected_name]

    status = st.selectbox("Status",
                          ("Paid" , "Unpaid")
                          )
    
    button = st.button("Update" , type="primary")

    if button:
        update_payment_status(selected_id , status)
        st.success("Updated status Succesfully !")

if page == "Ask AI":

    ai_input = st.text_input("Enter a question to generate query . ")
    button = st.button("Ask")

    if button:

        chat = client.models.generate_content(
        model="gemini-3-flash-preview",
        config= types.GenerateContentConfig(
            system_instruction="You are a SQL expert for a gym management database" \
            "tables : members" \
            "columns : id , name , phone , gender , joining_date , subs_end_date , plan , status" \
            "plan values : 1 Months , 3 Months , 6 Months , 12 Months" \
            "Status Values : Paid , Unpaid" \
            "When ask a quwstion , return ONLY a valid SQlite Select Query , nothing else . No instructions , No other Texts , Just query , just a raw sql"
            ),
        contents= ai_input
        )

        response = chat.text

        try:
            results = run_query(response)
            st.dataframe(pd.DataFrame(results , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End date" , "Plan" , "Status"]))
        except :
            st.error("Could not understood the query , please try rephrasing the question ! ")
