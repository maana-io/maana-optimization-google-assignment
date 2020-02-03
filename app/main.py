from ariadne import ObjectType, QueryType, MutationType, gql, make_executable_schema
from ariadne.asgi import GraphQL
from asgi_lifespan import Lifespan, LifespanMiddleware
from graphqlclient import GraphQLClient

# HTTP request library for access token call
import requests
# .env
from dotenv import load_dotenv
import os


from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

# Load environment variables
load_dotenv()


def getAuthToken():
    authProvider = os.getenv('AUTH_PROVIDER')
    authDomain = os.getenv('AUTH_DOMAIN')
    authClientId = os.getenv('AUTH_CLIENT_ID')
    authSecret = os.getenv('AUTH_SECRET')
    authIdentifier = os.getenv('AUTH_IDENTIFIER')

    # Short-circuit for 'no-auth' scenario.
    if(authProvider == ''):
        print('Auth provider not set. Aborting token request...')
        return None

    url = ''
    if authProvider == 'keycloak':
        url = f'{authDomain}/auth/realms/{authIdentifier}/protocol/openid-connect/token'
    else:
        url = f'https://{authDomain}/oauth/token'

    payload = {
        'grant_type': 'client_credentials',
        'client_id': authClientId,
        'client_secret': authSecret,
        'audience': authIdentifier
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, data=payload, headers=headers)
    response_data = r.json()
    print("Finished auth token request...")
    return response_data['access_token']


def getClient():

    graphqlClient = None

    # Build as closure to keep scope clean.

    def buildClient(client=graphqlClient):
        # Cached in regular use cases.
        if (client is None):
            print('Building graphql client...')
            token = getAuthToken()
            if (token is None):
                # Short-circuit for 'no-auth' scenario.
                print('Failed to get access token. Abandoning client setup...')
                return None
            url = os.getenv('MAANA_ENDPOINT_URL')
            client = GraphQLClient(url)
            client.inject_token('Bearer '+token)
        return client
    return buildClient()


# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback
type_defs = gql("""
type AssignmentConstraint {
  id: ID!
  vectorOfCoefficients: IntegerCoefficientVector
  upperBound: Int
  lowerBound: Int
  nodeSet: Boolean
}

input AssignmentConstraintAsInput {
  id: ID!
  vectorOfCoefficients: IntegerCoefficientVectorAsInput
  upperBound: Int
  lowerBound: Int
  nodeSet: Boolean
}

type AssignmentObjective {
  id: ID!
  minimize: Boolean
}

input AssignmentObjectiveAsInput {
  id: ID!
  minimize: Boolean
}

type AssignmentSolution {
  id: ID!
  nodeSetA: [Int]
  nodeSetB: [Int]
  cost: [Int]
  objectiveValue: Float
  status: String
}

type IntegerLinearCoefficient {
  id: ID!
  value: Int
}

input IntegerLinearCoefficientAsInput {
  id: ID!
  value: Int
}
type IntegerCoefficientVector {
  id: ID!
  value: [IntegerLinearCoefficient]
}

input IntegerCoefficientVectorAsInput {
  id: ID!
  value: [IntegerLinearCoefficientAsInput]
}

type CostMatrix {
  id: ID!
  row: [Row]
}

input CostMatrixAsInput {
  id: ID!
  row: [RowAsInput]
}

type Row {
  id: ID!
  values: [Int]
}

input RowAsInput {
  id: ID!
  values: [Int]
}
###

type Query {

    solverAssignmentWithSizes(
        costs: CostMatrixAsInput, 
        constraints: [AssignmentConstraintAsInput], 
        objective: AssignmentObjectiveAsInput
        ): AssignmentSolution

}
""")

# Map resolver functions to Query fields using QueryType
query = QueryType()

# Resolvers are simple python functions


# Map resolver functions to custom type fields using ObjectType

# Assignment Resolver
@query.field("solverAssignmentWithSizes")
def resolve_solverAssignmentWithSizes(*_, costs, constraints, objective):
    id = "Assignment With CP-SAT"

    # Create model
    model = cp_model.CpModel()
    # Get the number of workers
    num_workers = len(costs["row"])
    # Get the number of tasks
    num_tasks = len(costs["row"][0]["values"])

    #Create the variables

    x = []
    for i in range(num_workers):
        t = []
        for j in range(num_tasks):
          t.append(model.NewIntVar(0, 1, "x[%i,%i]" % (i, j)))
        x.append(t)
  
    # Constraints
    for constraint in constraints:
      if(constraint["nodeSet"]):
           #this is a constraint about workers
           [model.Add(sum(x[i][j] for i in range(num_workers)) >= constraint["lowerBound"]) for j in range(num_tasks)]
      else:
    #       #this is a constraint about task
        [model.Add(sum(constraint["vectorOfCoefficients"]["value"][j]["value"] * x[i][j] for j in range(num_tasks)) <= constraint["upperBound"]) for i in range(num_workers)]

    # # Create the objective function
    if objective["minimize"]:
       model.Minimize(sum([ costs["row"][i]["values"][j] * x[i][j] for i in range(num_workers)
                                                                  for j in range(num_tasks) ]))
      
     # Run the solver and return results

         #declare solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

#if status != cp_model.OPTIMAL:
#      print(status)
#else:
    status = "OPTIMAL"
  
    nodeSetA = []
    nodeSetB = []
    cost = []

    for i in range(num_workers):
      for j in  range(num_tasks):
        if solver.Value(x[i][j]) == 1:
          nodeSetA.append(i)
          nodeSetB.append(j)
          cost.append(costs["row"][i]["values"][j])
    
    return {
      "id": id,
      "nodeSetA": nodeSetA,
      "nodeSetB": nodeSetB,
      "cost": cost,
      "objectiveValue": solver.ObjectiveValue(),
      "status": status
    }




# Create executable GraphQL schema
schema = make_executable_schema(type_defs, [query])

# --- ASGI app

# Create an ASGI app using the schema, running in debug mode
# Set context with authenticated graphql client.
app = GraphQL(
    schema, debug=True, )

# 'Lifespan' is a standalone ASGI app.
# It implements the lifespan protocol,
# and allows registering lifespan event handlers.
lifespan = Lifespan()


@lifespan.on_event("startup")
async def startup():
    print("Starting up...")
    print("... done!")


@lifespan.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
    print("... done!")

# 'LifespanMiddleware' returns an ASGI app.
# It forwards lifespan requests to 'lifespan',
# and anything else goes to 'app'.
app = LifespanMiddleware(app, lifespan=lifespan)
