import websocket
import ast


def on_error(wsapp, message):
    """ A function to print any error messages """
    print(message)


def on_message(wsapp, message):
    """ A function called for every message received.
        Stores data and sends back the results of the optimization algorithm. """

    # stores the data as a dictionary
    data = ast.literal_eval(message)

    # tests whether the message sent is the data from the operations, or the results of the flow allocation
    if data["type"] == "CURRENT_STATE":

        # displays the data
        print(f"data = {message}")

        # creates the suitable framework for the flow allocation
        output = "["
        for i in range(0, len(data["operations"])):
            output = output + "{\"operationId\":\"" + data["operations"][i]["id"] + "\",\"flowRate\":" + allocate_flow(data)[i] + "},"
        output = output[:-1] + "]"

        # prints and sends the flow allocation
        print(f"ouput = {output}")
        wsapp.send(output)
    else:
        print(f"response = {message}\n\n")


def allocate_flow(data):
    """ Stores data and runs the optimization algorithm to determine flow allocation. """

    flowRateIn = data["flowRateIn"]
    operations = data["operations"]
    names = []
    points = []
    for operation in operations:
        points_row = []
        names.append(operation["name"])
        for i in range(21):
           points_row.append(operation["revenueStructure"][i]["dollarsPerDay"])
        points.append(points_row)
    slopes = []
    for row in points:
        slopes_row = []
        for i in range(1,21):
            dy = row[i] - row[i-1]
            dx = 10000
            slope = dy/dx
            slopes_row.append(slope)
        slopes.append(slopes_row)
    maxindeces=[]
    for row in points:
        maxindeces.append(row.index(max(row)))
    if sum(maxindeces)*10000<=flowRateIn:
        for i in range(len(maxindeces)):
            maxindeces[i]=maxindeces[i]*10000
        return(maxindeces)
    else:
        while sum(maxindeces)*10000-flowRateIn>10000:
            new=[]
            for row in maxindeces:
                new.append(max(points[row][0:maxindeces[row]-1]))
            workingRow=0
            workingDif=points[0][maxindeces[0]]-new[0]
            for row in range(len(maxindeces)):
                dif=points[row][maxindeces[row]]-new[row]
                if dif<workingDif:
                    workingRow=row
                    workingDif=dif
            maxindeces[workingRow]=points[workingRow].index([new[workingRow]])
            if sum(maxindeces)*10000>flowRateIn:
                maxesofeach=[]
                for row in range(len(points)):
                    newint=max(points[row][0:maxindeces[row]-1])
                    ylimit=points[row][maxindeces[row]]-slopes[row][maxindeces[row]]*(sum(maxindeces)*10000-flowRateIn)
                    maxesofeach.append([max([newint,ylimit]),ylimit>newint])
                workingRow=maxesofeach.index(max(maxesofeach))
                if not maxesofeach[workingRow][1]:
                    maxindeces[workingRow]=points[workingRow].index(maxesofeach[workingRow][0])
                else:
                    maxindeces[workingRow]=maxindeces[workingRow]-sum(maxindeces)+flowRateIn/10000
            for i in range(len(maxindeces)):
                maxindeces[i]=maxindeces[i]*10000
            return(maxindeces)


wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message, on_error=on_error)
wsapp.run_forever()
