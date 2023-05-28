from geojson import FeatureCollection

from mongodb.connection import db


def get_all():
    attractions = db.attractions.find({}, { "_id": 0 } )
    return FeatureCollection(list(attractions))

# deprecated
def _get_like(name, case_sensitive=False):
    options = 'i' if not case_sensitive else ''
    query = {
        "$regex": name,
        "$options": options
    }
    
    attractions = db.attractions.find({
        "$or": [
            { "properties.name": query },
            { "properties.scen_lm_na": query },
            { "properties.area_name": query },
            { "properties.lpc_name": query }
        ]
    }, { "_id": 0 } )
    return FeatureCollection(list(attractions))

def get_like(name, case_sensitive=False):
    options = 'i' if not case_sensitive else ''
    query = {
        "$regex": name,
        "$options": options
    }
    
    attractions = db.attractions.find({"properties.name": query }, { "_id": 0 } )
    return FeatureCollection(list(attractions))

def get_near(coords, max_distance=1000):
    attractions = db.attractions.find({
        "geometry": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "$maxDistance": max_distance
            }
        }
    }, { "_id": 0 })
    return FeatureCollection(list(attractions))
