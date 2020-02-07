# Maana Q Knowledge Microservice Template: Python (Ariadne)

- Uses the [Ariadne GraphQL framework](https://ariadnegraphql.org/)
- Uses the [ASGI Lifespan middlware](https://pypi.org/project/asgi-lifespan/)
- Concurrency, app server, and containerization is provided by the [Uvicorn+Gunicorn Docker](https://github.com/tiangolo/uvicorn-gunicorn-docker) base image

## Features

### Maana Q Client (i.e., peer-to-peer)

It is possible, though not generally preferred, for services to depend directly on other services, passing requests through a secure CKG endpoint.  This template includes the necessary authentication code for your convenience.  Simply supply environment settings and use the `client` from the GraphQL context:

```bash
#
# ---------------APPLICATION VARIABLES-------------------
#

MAANA_ENDPOINT_URL=


#
# ---------------AUTHENTICATION VARIABLES--------------------
#

# keycloak or auth0
AUTH_PROVIDER=

# URL for auth server (without path), i.e. https://keycloakdev.knowledge.maana.io:8443
AUTH_DOMAIN=

# Keycloak or auth0 client name/id.
AUTH_CLIENT_ID=

# Client secret for client credentials grant
AUTH_SECRET=

# Auth audience for JWT
# Set to same value as REACT_APP_PORTAL_AUTH_IDENTIFIER in Maana Q deployment ENVs)
# NOTE: For use of keycloak in this app, this value should match both the realm and audience values. 
AUTH_IDENTIFIER=
```

And, in your resolver:

```python
    # A resolver can access the graphql client via the context.
    client = info.context["client"]

    # Query all maana services.
    result = client.execute('''
    {
        allServices {
            id
            name
        }
    }
    ''')

    print(result)
```

## Build

```
pip install uvicorn gunicorn ariadne graphqlclient asgi-lifespan python-dotenv requests
```

## Containerize

Then you can build your image from the directory that has your Dockerfile, e.g:

```
docker build -t my-service ./
```

## Run Debug Locally

To run the GraphQL service locally with hot reload:

```
./start-reload.sh
```

and visit http://0.0.0.0:4000

For details, please refer to the [official documentation](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#development-live-reload).

## Run Locally (via Docker)

To run the GraphQL service locally (Via Docker):

```
docker run -it -p 4000:80 -t my-service
```

and visit http://0.0.0.0:4000

## Run Debug Locally (via Docker)

To run the GraphQL service via Docker with hot reload:

```
docker run -it -p 4000:80 -v $(pwd):/app my-service /start-reload-docker.sh
```

and visit http://0.0.0.0:4000

For details, please refer to the [official documentation](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#development-live-reload).

## Editing

To update any changes made to the service you will need to re run docker build.

Note that if you require additional packages such as pandas and numpy you need to add your packages to the pip install in the Dockerfile. There are a few difficulties with installing these additional packages, this: https://github.com/docker-library/python/issues/381 explains the issue and the resolution.

## Deploy

To simplify deployment to your Maana Q Kubernetes cluster, use the [CLI `mdeploy` command](https://github.com/maana-io/q-cli#mdeploy):

```
gql mdeploy
```

and follow the prompts.


## example Query

query{
  solverAssignmentWithGroups(
    costs: {
      id: "costs"
        row:  [
            {     id: "row0"
                  values: [90, 76, 75, 70, 50, 74]
            },
            {     id: "row1"
                  values: [35, 85, 55, 65, 48, 101]
            },
            {     id: "row2"
                  values: [125, 95, 90, 105, 59, 120]
            },
            {     id: "row3"
                  values: [45, 110, 95, 115, 104, 83]
            },
            {     id: "row4"
                  values: [60, 105, 80, 75, 59, 62]
            },
            {     id: "row5"
                  values: [45, 65, 110, 95, 47, 31]
            },
            {     id: "row6"
                  values: [38, 51, 107, 41, 69, 99]
            },
            {     id: "row7"
                  values: [47, 85, 57, 71, 92, 77]
            },
            {     id: "row8"
                  values: [39, 63, 97, 49, 118, 56]
            },
            {     id: "row9"
                  values: [47, 101, 71, 60, 88, 109]
            },
            {     id:"row10"
                  values: [17, 39, 103, 64, 61, 92]
            },
            {     id:"row11"
                  values: [101, 45, 83, 59, 92, 27]
            },

        ]

    }

    constraints: [
      { # these may need to be nested again within a dict if other parameters need passing in addition to just groups
        id: "group1"
        upperBound: 1
        lowerBound: 0
        nodeSet: false
        groupsMatrix:  [
        {     id: "row0"
                  values: [0, 0, 1, 1],      # Workers 2, 3
             },
            {     id: "row1"
                  values: [0, 1, 0, 1],      # Workers 1, 3
             },
            {     id: "row2"
                  values: [0, 1, 1, 0],      # Workers 1, 2
             },
            {     id: "row3"
                  values: [1, 1, 0, 0],      # Workers 0, 1
             },
            {     id: "row4"
                  values: [1, 0, 1, 0]
                  },
                  ]      # Workers 0, 2
       },
      {
        id: "group2"
        upperBound: 1
        lowerBound: 0
        nodeSet: false
        groupsMatrix:  [
        {     id: "row0"
                  values: [0, 0, 1, 1],      # Workers 6, 7
             },
            {     id: "row1"
                  values: [0, 1, 0, 1],      # Workers 5, 7
             },
            {     id: "row2"
                  values: [0, 1, 1, 0],      # Workers 5, 6
             },
            {     id: "row3"
                  values: [1, 1, 0, 0],      # Workers 4, 5
             },
            {     id: "row4"
                  values: [1, 0, 0, 1]
                  },
                  ]      # Workers 4, 7
       },
      {
        id: "group3"
        upperBound: 1
        lowerBound: 0
        nodeSet: false
        groupsMatrix:  [
        {     id: "row0"
                  values: [0, 0, 1, 1],      # Workers 10, 11
             },
            {     id: "row1"
                  values: [0, 1, 0, 1],      # Workers 9, 11
             },
            {     id: "row2"
                  values: [0, 1, 1, 0],      # Workers 9, 10
             },
            {     id: "row3"
                  values: [1, 0, 1, 0],      # Workers 8, 10
             },
            {     id: "row4"
                  values: [1, 0, 0, 1]
                  },
                  ]      # Workers 8, 11
      },
      {
        id: "ct"
        lowerBound: 1
        upperBound: 0
        nodeSet: true
        groupsMatrix:[{id: "row0"
        values: []
        }]
      }
    ]
    objective: {
      id: "obj"
      minimize: true
    }
  ) {
    id
    nodeSetA
    nodeSetB
    cost
    objectiveValue
    status

  }
}


{
  solverAssignmentWithSizes(
    costs: {
      id: "costs"
        row: [
            {     id: "row0"
                  values: [ 90, 76, 75, 70, 50, 74, 12, 68 ]
            },
            {     id: "row1"
                  values: [  35, 85, 55, 65, 48, 101, 70, 83 ]
            },
            {     id: "row2"
                  values: [  125, 95, 90, 105, 59, 120, 36, 73]
            },
            {     id: "row3"
                  values: [  45, 110, 95, 115, 104, 83, 37, 71]
            },
            {     id: "row4"
                  values: [  60, 105, 80, 75, 59, 62, 93, 88]
            },
            {     id: "row5"
                  values: [ 45, 65, 110, 95, 47, 31, 81, 34]
            },
            {     id: "row6"
                  values: [ 38, 51, 107, 41, 69, 99, 115, 48]
            },
            {     id: "row7"
                  values: [ 47, 85, 57, 71, 92, 77, 109, 36]
            },
            {     id: "row8"
                  values: [ 39, 63, 97, 49, 118, 56, 92, 61]
            },
            {     id: "row9"
                  values: [  47, 101, 71, 60, 88, 109, 52, 90]
            },
            {
               id:"row10"
               values: [3,45,76, 54, 88,99,11, 42]
            },
            
        ]
               
    }
    
    constraints: [
      {
        id: "ct1"
        lowerBound: 0
        upperBound: 15
        nodeSet: false
        vectorOfCoefficients: {
              id: "icv1"
              value: [
                {id:"v0", value:10}
                {id:"v1", value:7 }
                {id:"v2", value:3}
                {id:"v3", value:12}
                {id:"v4", value:15}
                {id:"v5", value:4}
                {id:"v6", value:11}
                {id:"v7", value:5}
               
              ]
        }
      },
      {
        id: "ct2"
        lowerBound: 1
        upperBound: 0
        nodeSet: true
        vectorOfCoefficients: {
              id: "icv2"
              value: []
        }
      }
         
    ]

    objective: {
      id: "obj"
      minimize: true
    }
  ) {
    id
    nodeSetA
    nodeSetB
    cost
    objectiveValue
    status
    
  }
}