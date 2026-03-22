import streamlit as st
from database import add_member , fetch_all_members , get_expiring_soon , update_payment_status , run_query , init_db , update_member , delete_member , member_by_id , get_all_unpaid , get_members_by_date , total_revenue
import pandas as pd
from datetime import date , timedelta
from google import genai
from google.genai import types
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
init_db()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


password = os.getenv("APP_PASSWORD")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    user_password = st.text_input("Enter password")
    button = st.button("Submit")

    if button:
        if user_password == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Wrong password")
else:

    all_plans = {
            "1 Month" : 900 ,
            "3 Month" : 2100 ,
            "6 Month" : 3800 ,
            "12 Month" : 5500 ,
            "3 Month Student" : 1800 ,
            "1 Month PT" : 3000 
        }
    
    st.logo("static/logo.png")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("static/logo.png", width=200)
        st.title("Kailash Gym")

    page = st.sidebar.selectbox(
        "Options",
        ("Dashboard" , "Add Member" , "Update Status" , "Edit Members" ,"Charts", "Ask AI")
    )

    def color_status(val):
        if val == "Paid":
            return "background-color: #90EE90"
        elif val == "Unpaid":
            return "background-color: #ffcccc"
        
        return ""
    
    if page == "Dashboard":
        all_members = fetch_all_members()
        expiring_plan_members = get_expiring_soon()
        unpaid_members = get_all_unpaid()

        if expiring_plan_members:
            st.warning(f"{len(expiring_plan_members)} members plan expires soon !" ,icon="⚠️")
        checkbox = st.checkbox("Get all Expiring Plan Members ")
        checkbox2 = st.checkbox("Get all Fees UNPAID Members")
        checkbox3 = st.checkbox("Get all members having Due Amount")

        if checkbox:
            df = pd.DataFrame(expiring_plan_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
            df["Amount Due"] = df["Plan Amount"] - df["Amount Paid"]
            style_df = df.style.map(color_status , subset=["Status"])

            st.dataframe(style_df , hide_index=True)
            
        elif checkbox2:
            df = pd.DataFrame(unpaid_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
            df["Amount Due"] = df["Plan Amount"] - df["Amount Paid"]
            style_df = df.style.map(color_status ,subset=["Status"])

            st.dataframe(style_df , hide_index=True)
        elif checkbox3:
            df = pd.DataFrame(all_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
            df["Amount Due"] = df["Plan Amount"] - df["Amount Paid"]
            df = df[df["Amount Due"] > 0]
            st.dataframe(df[["Name" , "Amount Due"]] , hide_index= True) 

        else:
            df = pd.DataFrame(all_members , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
            df["Amount Due"] = df["Plan Amount"] - df["Amount Paid"]
            style_df = df.style.map(color_status , subset=["Status"])
            st.dataframe(style_df , hide_index=True)


    if page == "Add Member":

        
        today = date.today()

        name = st.text_input("Name")
        phone = st.text_input("Phone No ")
        gender = st.selectbox( "Gender" , ("Male" , "Female"))
        plan = st.selectbox("Plan" , ("1 Month" , "3 Month" , "6 Month" , "12 Month" , "3 Month Student" , "1 Month PT"))
        status = st.selectbox("Fees Status" , ("Paid" , "Unpaid"))
        joining_date = st.date_input("Joining Date")

        if plan == "1 Month" or plan == "1 Month PT":
            end_date = today + timedelta(days=31)

        elif plan == "3 Month" or plan == "3 Month Student":
            end_date = today + timedelta(days=92)

        elif plan == "6 Month" :
            end_date = today + timedelta(days=184)

        elif plan == "12 Month" :
            end_date = today + timedelta(days=365)


        subs_end_date = st.date_input("End date " , end_date)
        plan_amount = st.number_input("Plan Price" , all_plans[plan])
        amount_paid = st.number_input("Amount Paid")
        due_amount = st.number_input("Amount due" , plan_amount - amount_paid)

        button = st.button("Submit" , type="primary")

        if button:
            add_member(name , phone , gender , str(joining_date) , str(subs_end_date) ,plan , status , plan_amount , amount_paid)
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
                "columns : id , name , phone , gender , joining_date , subs_end_date , plan , status , plan_amount , amount_paid"  \
                "plan values : 1 Month , 3 Month , 6 Month , 12 Month , 3 Month Student , 1 Month PT"  \
                "Status Values : Paid , Unpaid" \
                "When ask a quwstion , return ONLY a valid PostgreSQL Select Query , nothing else . No instructions , No other Texts , Just query , just a raw sql"
                ),
            contents= ai_input
            )

            response = chat.text

            try:
                results = run_query(response)
                df = pd.DataFrame(results , columns=["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
                style_df = df.style.map(color_status , subset=["Status"])
                st.dataframe(style_df , hide_index=True)
            except :
                st.error("Could not understood the query , please try rephrasing the question ! ")


    if page == "Edit Members":

        up_del_search = st.text_input("Search Member ")

        all_members = fetch_all_members()

        filtered_updel = [m for m in all_members if up_del_search.lower() in m[1].lower()]

        member_options_up_del = {f"{m[1]} - {m[2]}" : m[0] for m in filtered_updel }
        selected_up_del_name = st.selectbox("Select Member" , list(member_options_up_del.keys()))
        selected_up_del_id = member_options_up_del[selected_up_del_name] 

        member = member_by_id(selected_up_del_id)

        if selected_up_del_name:
                
            name = st.text_input("Name" , value= member[1])
            phone = st.text_input("Phone No " , value=member[2])
            gender = st.selectbox( "Gender" , ("Male" , "Female") , index= ("Male" , "Female").index(member[3]))
            joining_date = st.date_input("Joining Date" , value = datetime.strptime(member[4] , "%Y-%m-%d").date())
            subs_end_date = st.date_input("End date " , value = datetime.strptime(member[5] , "%Y-%m-%d").date())
            
            plan = st.selectbox("Plan" , ("1 Month" , "3 Month" , "6 Month" , "12 Month" , "3 Month Student" , "1 Month PT") , index= ("1 Month" , "3 Month" , "6 Month" , "12 Month" , "3 Month Student" , "1 Month PT").index(member[6]))
            status = st.selectbox("Fees Status" , ("Paid" , "Unpaid") , index = ("Paid" , "Unpaid").index(member[7]))
           
            plan_amount = st.number_input("Plan Amount" , all_plans[plan])
            amount_paid = st.number_input("Amount Paid" , value = member[9])
            amount_due = st.number_input("Amount due" , plan_amount - amount_paid)

            button = st.button("UPDATE" , type="primary")
            delete_btn = st.button("DELETE" , type="secondary")
            if button:
                update_member(name , phone , gender , str(joining_date) , str(subs_end_date) ,plan , status , plan_amount , amount_paid , selected_up_del_id)
                st.success("Member Updated succesfully !")
            if delete_btn:
                delete_member(selected_up_del_id)
                st.success("Member Deleted Succesfully")

    if page == "Charts":
        date_range = st.date_input("Select Date Range" , value=(date.today() , date.today()))
        st.subheader("Members Joined")

        if len(date_range) == 2:
            start_date = str(date_range[0])
            end_date = str(date_range[1])

            members_in_range = get_members_by_date(start_date , end_date)
            total_revenue_ = total_revenue(start_date , end_date)

            df = pd.DataFrame(members_in_range , columns= ["ID" , "Name" , "Phone" , "Gender" , "Joining Date" , "End Date" , "Plan" , "Status" , "Plan Amount" , "Amount Paid"])
            df["Amount Due"] = df["Plan Amount"] - df["Amount Paid"]
            total_due = df["Amount Due"].sum()
            col1, col2 , col3 = st.columns(3)
            col1.metric("Members Joined", len(members_in_range))
            col2.metric("Total Revenue", f"₹{total_revenue_ or 0}")
            col3.metric("Total Due" , f"₹{max(0 ,total_due)}" )


            
            chart_data = df.groupby("Joining Date").size().reset_index(name="Members")
            st.line_chart(chart_data.set_index("Joining Date"))


            st.subheader("Revenue")
            revenue_chart = df.groupby("Joining Date")["Amount Paid"].sum()
            st.line_chart(revenue_chart)

            st.subheader("Due chart")
            due_chart = df.groupby("Joining Date")["Amount Due"].sum()
            st.line_chart(due_chart)





