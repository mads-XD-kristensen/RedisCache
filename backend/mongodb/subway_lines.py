from geojson import FeatureCollection
from mongodb.connection import db


def get_all():
    stops = db.lines.find({}, { "_id": 0 } )
    return FeatureCollection(list(stops))
