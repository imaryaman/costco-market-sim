"""
Costco AI - BMS5213 Group Project Part 4.
Two pages: the Market Simulator (proof) and SmartShop (the member-facing product, powered by RightBuy).
Run:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Costco · RightBuy", page_icon="🛒", layout="wide")

nav = st.navigation([
    st.Page("simulator.py", title="Market Simulator", icon="📊", default=True),
    st.Page("smartshop.py", title="SmartShop", icon="🛒"),
], position="top")
nav.run()
