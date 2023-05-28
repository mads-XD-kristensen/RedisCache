import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    stops = db.lines.find({}, { "_id": 0 } )
    return FeatureCollection(list(stops))
