import json

import mongodb
import redis
from fastapi import FastAPI
from geojson import Feature, FeatureCollection, LineString
from neo4j import GraphDatabase as gd

app = FastAPI()

NEOURL = "neo4j://localhost:7687"
NEOUSER = "neo4j"
NEOPASS = "12345678"
"""MATCH (a:Stop), (b:Stop)
WHERE a.name = "Bergen St" AND b.name = "Wall St"
WITH a,b
MATCH p = allshortestpaths((a)-[*]-(b))  
WHERE NONE (x IN RELATIONSHIPS(p) WHERE type(x)="OPERATES")  
RETURN p  
LIMIT 10  """

def path_to_geojson(path):
    lines = FeatureCollection([
        Feature(
            geometry=LineString(
                ((rel.start_node['lon'], rel.start_node['lat']), (rel.end_node['lon'], rel.end_node['lat']))
            ),
            properties={
                'departure': rel.start_node['departure_time'],
                'arrival': rel.end_node['arrival_time'],
                'start_parent': rel.start_node['parent_station'],
                'end_parent': rel.end_node['parent_station'],
            }
        ) for rel in path.relationships if rel.type == 'PRECEDES']
    )
    return lines

@app.get("/")
def hello():
    return {"Hello what subway route are you looking for? Use url /search?start='start place'&stop='stop place' without '' quotes"}


@app.get("/search")
def search(start: str, stop: str):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    route = f"{start}-{stop}"
    
    output = r.get(route) #Henter route i redis db
    if output: #Hvis redis allerede har en cachet route
        return json.loads(output) #Returner cached route
    else:
        with gd.driver(NEOURL, auth=(NEOUSER, NEOPASS)) as driver: #opretter forbindelse til neo4j db
            driver.verify_connectivity()

            records, summary, keys = driver.execute_query(
                "MATCH (a:Stop), (b:Stop) WHERE a.id = $start AND b.id = $stop WITH a,b MATCH p = allshortestpaths((a)-[*]-(b)) WHERE NONE (x IN relationships(p) WHERE type(x)='OPERATES') AND NONE (s IN nodes(p) WHERE 'Trip' IN labels(s)) RETURN p LIMIT 1",
                start=start, stop=stop)
            
            if len(records) > 0: #Tjekker om der kommer noget tilbage fra neo4j, hvis der ikke kommer noget er der ikke nogen rute
                #Siden der er en limit 1 på cypher query så kommer der max 1 record
                path = records[0]['p'] #Henter path fra record
                output = path_to_geojson(path) #Konverterer path til geojson
                
                r.set(route, json.dumps(output), 600) #cache i redis db med den søgte route som key og selve routen som value, bliver i redis db i 10 min
                return output
            else:
                return None

@app.get("/subway_stops")
def subways():
    return mongodb.subway_stops.get_all()
