# API

## Table of contents

- [Usage](#usage)
- [Redis cache](#redis-cache)
- [MongoDB](#mongodb)
  - [Setup](#setup)
  - [Data sources](#data-sources)
  - [Imports](#imports)
    - [jq](#jq)
    - [Aggregation](#aggregation)
  - [Build indexes](#build-indexes)
  - [Updates](#updates)

## Usage

To start api use pip to install everything in requirements.txt

```shell
pip install -r requirements.txt
```

Make sure that all the databases are running (neo4j, redis, and mongodb). You might need to change user and password for neo4j driver in main.py

Next go to backend `cd backend` and run `uvicorn main:app --reload`

The api is now running and you should be able to test it on `http://127.0.0.1:8000/`

## Redis cache

First-time-setup: For redis use `docker-compose up -d` and a docker container should start with redis installed.

## MongoDB

### Setup

- Restore database from dump file.
- Alternatively build it from scratch with [instructions](#imports)

Once we do replication and/or sharding, these commands might change, but maybe not.

The dump was created with `mongodump -d exam --archive=data/dump_archive.gzip --gzip`, so to restore it, run the following:

```shell
mongorestore --archive=data/dump_archive.gzip --gzip
```

This will create the `exam` database and rebuild indexes.

### Data sources

Our data came from publicly available datasets published by the city and state of New York.

- [MTA General Transit Feed Specification (GTFS) Static Data](https://data.ny.gov/Transportation/MTA-General-Transit-Feed-Specification-GTFS-Static/fgm6-ccue)
- [Subway Stations](https://data.cityofnewyork.us/Transportation/Subway-Stations/arq3-7z49)
- [Subway Lines](https://data.cityofnewyork.us/Transportation/Subway-Lines/3qz8-muuu)
- [Places](https://data.cityofnewyork.us/Health/Places/mzbd-kucq)
- [New York City Museums](https://data.cityofnewyork.us/Recreation/New-York-City-Museums/ekax-ky3z)
- [New York City Art Galleries](https://data.cityofnewyork.us/Recreation/New-York-City-Art-Galleries/tgyc-r5jh)
- [Theaters](https://data.cityofnewyork.us/Recreation/Theaters/kdu2-865w)
- [Individual Landmark Sites](https://data.cityofnewyork.us/Housing-Development/Individual-Landmark-Sites/ts56-fkf5)
- [Scenic Landmarks](https://data.cityofnewyork.us/Housing-Development/Scenic-Landmarks/gi7d-8gt5)
- [Historic Districts](https://data.cityofnewyork.us/Housing-Development/Historic-Districts/xbvj-gfnw)

All the data in the MongoDB database is in GeoJSON format. This allows us to perform geospatial operations and to plot the documents on a map.

The following sections concern what we did to import and setup the data in the database. If you want to recreate the database, simply [restore it](#setup). Only if you wish to recreate the database from scratch the way we did, should you follow the following instructions yourself.

### Imports

- [`jq`](https://stedolan.github.io/jq/) into [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/)
- Alternatively, you can import the files as is and use an aggregation pipeline.

#### jq

The easiest way to import the GeoJSON data is to install a tool called [jq](https://stedolan.github.io/jq/). Because the data is formatted as a `FeatureCollection` and we want each `Feature` to be a separate document, we need to extract the `features` property which is an array.

An example looks like this:

```shell
jq -c '.features' stops.geojson | mongoimport -d exam -c transit --jsonArray
```

#### Aggregation

Alternatively, you can import the files as is, meaning each document is the whole of `FeatureCollection` in the file, and then use the following aggregation pipeline on each collection:

```javascript
db.transit.aggregrate([
  {
    '$unwind': {
      'path': '$features'
    }
  }, {
    '$replaceWith': '$features'
  }, {
    '$out': 'transit'
  }
])
```

### Build indexes

We need to build geospatial indexes in order to perform geospatial operations on the collections.

```javascript
db.transit.createIndex({geometry: '2dsphere'})
db.attractions.createIndex({geometry: '2dsphere'})
```

### Updates

Attractions have different name fields depending on what file they came from and what type of attraction they are. This caused issues with displaying them on the map. There were a couple options for fixing this:

1. Renaming them in code.
2. Renaming them in the database.
3. Projecting them from the database with the same name.

We opted for renaming them in the database as this would also speed up search queries because we don't need an `$or` operator.

If you restore from dump file, you don't have to do anything, but if you create the database from scratch, run these update queries one by one. Renaming the fields in the same query didn't work.

```javascript
db.attractions.updateMany({}, {
  $rename: {
    'properties.scen_lm_na': 'properties.name'
  }
})
db.attractions.updateMany({}, {
  $rename: {
    'properties.area_name': 'properties.name'
  }
})
db.attractions.updateMany({}, {
  $rename: {
    'properties.lpc_name': 'properties.name'
  }
})
```
