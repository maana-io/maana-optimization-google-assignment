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

## TODO change nodeSet to string so different categories of constraint can be passed? Worker, task, group
type AssignmentGroupConstraint {
  id: ID!
  groupsMatrix: [Row]
  upperBound: Int
  lowerBound: Int
  nodeSet: Boolean
}

input AssignmentGroupConstraintAsInput {
  id: ID!
  groupsMatrix: [RowAsInput]
  upperBound: Int
  lowerBound: Int
  nodeSet: Boolean
}

type AssignmentGroupSolution {
  id: ID!
  nodeSetA: [Int]
  nodeSetB: [Int]
  cost: [Int]
  objectiveValue: Float
  status: String
}

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

    solverAssignmentWithGroups(
        costs: CostMatrixAsInput, 
        constraints: [AssignmentGroupConstraintAsInput], 
        objective: AssignmentObjectiveAsInput
        ): AssignmentGroupSolution


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


# Assignment Resolver with Groups
@query.field("solverAssignmentWithGroups")
def resolve_solverAssignmentWithGroups(*_, costs, constraints, objective):
    id = "Assignment Incl Groups With CP-SAT"

    group_constraints_exist_flag = False

    print(f'DEBUG: here are costs {costs}')
    print(f'DEBUG: here are constraints {constraints}')

    groups_dict = {}
    groups_dict_workers = {}
    for item in constraints:
        if item["nodeSet"] is False: # hard coded variable name exclusion, therefore may need generalising
            group_constraints_exist_flag = True
            print(f'group dict item {item["groupsMatrix"]}')
            group_list_to_pass = []
            for row in item["groupsMatrix"]:

                print(f'NEW groups dict item from list {row["values"]}')
                group_list_to_pass.append(row["values"])

            groups_dict[item["id"]] = group_list_to_pass
            print(f'here finally we have the matrix {group_list_to_pass}')

    print(f'here is groups dict {groups_dict}')

    print(f'group dict keys {groups_dict.keys()}')

    print(f'here is objective {objective}')


    # Create model
    model = cp_model.CpModel()
    # Get the number of workers
    num_workers = len(costs["row"])
    # Get the number of tasks
    num_tasks = len(costs["row"][0]["values"])

    # Create the variables

    x = []
    for i in range(num_workers):
        t = []
        for j in range(num_tasks):
            t.append(model.NewIntVar(0, 1, "x[%i,%i]" % (i, j)))
        x.append(t)


    # Constraints

    # Each task is assigned to at least one worker.
    [model.Add(sum(x[i][j] for i in range(num_workers)) == 1)
     for j in range(num_tasks)]

    # Each worker is assigned to at most one task.
    [model.Add(sum(x[i][j] for j in range(num_tasks)) <= 1)
     for i in range(num_workers)]

    #
    # Constraints

    # hard coded constraints

    ## the following is hard coded in - feels wrong and that is should be passed as a contraint

    # Each worker is assigned to at most one task.
    [model.Add(sum(x[i][j] for j in range(num_tasks)) <= 1)
     for i in range(num_workers)]

    # Create variables for each worker, indicating whether they work on some task.
    work = []
    for i in range(num_workers):
        work.append(model.NewIntVar(0, 1, "work[%i]" % i))

    for i in range(num_workers):
        for j in range(num_tasks):
            model.Add(work[i] == sum(x[i][j] for j in range(num_tasks)))



    ##### passed constraints

    for constraint in constraints:
        if (constraint["nodeSet"]):
            # this is a constraint about workers
#            [model.Add(sum(x[i][j] for i in range(num_workers)) >= constraint["lowerBound"]) for j in range(num_tasks)]
            # not sure about the evaluation of num_workers
            [model.Add(sum(x[i][j] for i in range(num_workers)) <= constraint["lowerBound"]) for j in range(num_tasks)]
#    print(f'here is model {model}')
        else:

    # Define the allowed groups of workers - this should work independently of number of groups passed in via constraints
            if group_constraints_exist_flag:
                group_item_counter = 0
                for key in groups_dict.keys():
                    generated_worker_list = []
                    if len(groups_dict[key]) > 0:
                        if len(groups_dict[key][0]) > 0:
                            group_item_counter += len(groups_dict[key][0])
                            for worker_item in list(range((group_item_counter - len(groups_dict[key][0])), group_item_counter)):
                                generated_worker_list.append(work[worker_item])
                            print(f'DEBUG: for {key} generated workers are {generated_worker_list}')
                            model.AddAllowedAssignments(generated_worker_list, groups_dict[key])


    # # Create the objective function
    if objective["minimize"]:
        model.Minimize(sum([costs["row"][i]["values"][j] * x[i][j] for i in range(num_workers)
                            for j in range(num_tasks)]))

    # Run the solver and return results

    # declare solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)


    if status != cp_model.OPTIMAL:
        print(f'non-optimal status{status}')
    else:
        print(f'optimal status {status}')
    #
        status = "OPTIMAL"
    #
    nodeSetA = []
    nodeSetB = []
    cost = []
    #
    for i in range(num_workers):
        for j in range(num_tasks):
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
