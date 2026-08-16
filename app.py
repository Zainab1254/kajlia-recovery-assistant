import streamlit as st
import sqlite3
import pandas as pd
import requests
import os

KEY = os.getenv("ANTHROPIC_API_KEY")
if not KEY:
    try:
        KEY = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        KEY = None

st.title("Kajlia Recovery Assistant")
st.write("36 flats · payment recovery data")

conn = sqlite3.connect("kajlia_demo.db")
flats = pd.read_sql("SELECT * FROM flats", conn)
payments = pd.read_sql("SELECT * FROM payments", conn)

payments["date"] = pd.to_datetime(payments["date"], errors="coerce")
payments["cheque_date"] = pd.to_datetime(payments["cheque_date"], errors="coerce")

cleared = payments[~payments["cheque_status"].isin(["pending", "returned"])]

total_recovery = cleared["amount"].sum()
flat_sale = flats["sale"].sum()
outstanding = flat_sale - total_recovery
pending = payments.loc[payments["cheque_status"] == "pending", "amount"].sum()
unsecured = outstanding - pending

c1, c2, c3 = st.columns(3)
c1.metric("Total sale", f"{flat_sale/10000000:.1f} cr")
c2.metric("Recovered", f"{total_recovery/10000000:.2f} cr")
c3.metric("Unsecured", f"{unsecured/10000000:.1f} cr")
cleared = cleared.copy()
cleared["month"] = cleared["date"].dt.to_period("M").astype(str)
monthly = cleared.groupby("month")["amount"].sum() / 10000000

st.subheader("Monthly recovery (crore)")
st.bar_chart(monthly)

def llm_call(prompt):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-5",
            "max_tokens": 800,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return r.json()["content"][0]["text"]
 

overdue_data = payments[payments["cheque_status"] == "pending"]

data_text = f"""
Total sale: {flat_sale/10000000:.1f} crore
Recovered: {total_recovery/10000000:.2f} crore
Outstanding: {outstanding/10000000:.1f} crore
Pending (secured by cheque): {pending/10000000:.2f} crore
Unsecured: {unsecured/10000000:.1f} crore

Number of flats: {len(flats)}
Number of payments: {len(payments)}

Monthly recovery in crore:
{monthly.to_string()}
"""
c4, c5 = st.columns(2)
with c4:
    if st.button("What the data shows", key="btn1"):

        prompt = f"""
    Respond in English.

    {data_text}

    Numbers are already in crore. Use them exactly as given. Do NOT recalculate.

    State only what this data shows. Three short observations, each with the number.
    No recommendations. No advice. No suggested actions. Do not say what should be done.
    If a number looks unusual compared to the others, point it out.
    """
        with st.spinner("Thinking..."):
            st.write(llm_call(prompt))
with c5:
    if st.button("What's missing from the data", key="btn2"):
        prompt = f"""
    Respond in English.

    {data_text}

    Based only on what is here, what important information is MISSING from this data?
    List three things that would be needed to understand the recovery position properly.
    No recommendations. No advice. Only state what data is missing and why it matters. Do not add, subtract, or calculate any numbers yourself. Only use the numbers exactly as given above.
    """
        with st.spinner("Thinking..."):
            st.write(llm_call(prompt))
