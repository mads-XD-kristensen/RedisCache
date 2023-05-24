from fastapi import FastAPI
import redis
app = FastAPI()


@app.get("/")
def hello():
    return {"Hello what subway route are you looking for?? :D"}


@app.get("/search")
def search(route: str):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    output = r.get(route)
    if output: #Hvis redis allerede har en cachet route
        return {output}
    else:
        output = "a>c>h>i>p" # Hent fra database her og put i cache 
        r.set(route, output, 600) #cache i redis db med den søgte route som key og selve routen som value, bliver i redis db i 10 min
        return {output, "Route was not in cache but was in db, is now in cache for 10 min"} #placeholder
    