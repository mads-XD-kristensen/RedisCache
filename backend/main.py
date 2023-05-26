from fastapi import FastAPI
import redis
from graphdatascience import GraphDataScience
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
    route = f"{start},{stop}"

    output = r.get(route) #Henter route i redis db

    if output: #Hvis redis allerede har en cachet route
        return {output}
    else:
        gds = GraphDataScience(NEOURL, auth=(NEOUSER, NEOPASS), database="neo4j")
        cypher_query = """
        MATCH (a:Stop), (b:Stop)
        WHERE a.name = '{rstart}' AND b.name = '{rstop}'
        WITH a,b
        MATCH p = allshortestpaths((a)-[*]-(b))  
        WHERE NONE (x IN RELATIONSHIPS(p) WHERE type(x)='OPERATES')  
        RETURN p LIMIT 1
        """.format(rstart=start, rstop=stop)
        print(cypher_query)
        
        output = gds.run_cypher(cypher_query) # Hent fra database her og put i cache
        print(output)
        print("\n")
        #df = pd.DataFrame(output, columns=output.p)
        #print(df)
        gds.close()
        #r.set(route, "output", 600) #cache i redis db med den søgte route som key og selve routen som value, bliver i redis db i 10 min
        return {"output", "Route was not in cache but was in db, is now in cache for 10 min"} #placeholder
    