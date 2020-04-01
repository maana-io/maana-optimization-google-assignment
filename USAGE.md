## Features

solverAssignmentWithGroups

solverAssignmentWithSizes


## Queries

## With Groups

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


## With Sizes
query {
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
