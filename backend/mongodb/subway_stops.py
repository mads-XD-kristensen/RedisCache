import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    stops = db.transit.find({'properties.location_type': "1"}, { "_id": 0 } )
    return FeatureCollection(list(stops))

@st.cache_data
def get_near(coords, max_distance=1000, limit=10):
    """Get subway stops near a given point.
    
    max_distance=None to remove the $maxDistance filter.
    
    limit=None to remove the $limit filter.
    """
    max_distance = { 'maxDistance': max_distance } if max_distance is not None else {}
    limit = { '$limit': limit } if limit is not None else {}
    
    stops = db.transit.aggregate([
        {
            '$geoNear': {
                'near': {
                    'type': 'Point', 
                    'coordinates': coords
                }, 
                'distanceField': 'distance', 
                **max_distance
            }
        },
        limit
        , {
            '$project': {
                '_id': 0
            }
        }
    ])
    return FeatureCollection(list(stops))
