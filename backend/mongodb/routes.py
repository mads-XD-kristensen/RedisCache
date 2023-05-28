import requests
import streamlit as st


@st.cache_data
def get_route(start, end):
    url = 'http://localhost:8000/search'
    r = requests.get(url, params={'start': start, 'stop': end})
    r.raise_for_status()
    return r.json()