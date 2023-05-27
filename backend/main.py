from fastapi import FastAPI
import redis
from graphdatascience import GraphDataScience
from neo4j import GraphDatabase as gd
import pandas as pd
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

@app.get("/")
def hello():
    return {"Hello what subway route are you looking for? Use url /search?start='start place'&stop='stop place' without '' quotes"}


@app.get("/search")
def search(start: str, stop: str):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    route = f"{start}-{stop}"
    
    output = r.get(route) #Henter route i redis db
    if output: #Hvis redis allerede har en cachet route
        route_string = f"The route from, {route}, is:, {output}"
        return {route_string}
    else:
        with gd.driver(NEOURL, auth=(NEOUSER, NEOPASS)) as driver: #opretter forbindelse til neo4j db
            driver.verify_connectivity()
            full_route = []

            records, summary, keys = driver.execute_query(
                "MATCH (a:Stop), (b:Stop) WHERE a.name = $start AND b.name = $stop WITH a,b MATCH p = allshortestpaths((a)-[*]-(b)) WHERE NONE (x IN RELATIONSHIPS(p) WHERE type(x)='OPERATES') RETURN nodes(p) LIMIT 1",
                start=start, stop=stop)
            
            if len(records) > 0: #Tjekker om der kommer noget tilbage fra neo4j, hvis der ikke kommer noget er der ikke nogen rute
                #Siden der er en limit 1 på cypher query så kommer der max 1 record
                for subway in records: #Dette for-loop er for at få dataene ud af det dictionary man får fra neo4j, neo4j giver et dictionary med 1 key som hedder nodes(p) og valuen er en liste af dictionary 
                    output = subway.data()
                    output = output["nodes(p)"]

                for route_stop in output: #Dette for-loop er for at gå igennem den liste af dictionary og hente values ud
                    # route_stop.values() indeholder alle labels for hver node i den rute der bliver fundet men vi er kun interraseret i det første element derfor laves det til en list og [0] henter første element
                    full_route.append(list(route_stop.values())[0])  
                full_route_string = str(full_route) #Laver hele ruten til en string for at kunne gemme det i redis
                r.set(route, full_route_string, 600) #cache i redis db med den søgte route som key og selve routen som value, bliver i redis db i 10 min

            else:
                output = "No route exists"
                return {output}
        route_string = f"The route from, {route}, is:, {full_route_string}"
        return {route_string}