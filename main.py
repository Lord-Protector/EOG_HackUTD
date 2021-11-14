import websocket
import ast


def on_error(wsapp, message):
    """ A function to print any error messages """
    print(message)


pit_volume = 0


def on_message(wsapp, message):
    """ A function called for every message received.
        Stores data and sends back the results of the optimization algorithm. """

    global pit_volume

    # stores the data as a dictionary
    try:
        data = ast.literal_eval(message)
    except:
        print("Invalid data type.")
        print(f"{message}\n\n")
        return 0

    # tests whether the message sent is the data from the operations, or the results of the flow allocation
    if data["type"] == "CURRENT_STATE":

        # displays the data
        print(f"data = {message}")

        # creates the suitable framework for the flow allocation
        output = "["
        for i in range(0, len(data["operations"])):
            output = output + "{\"operationId\":\"" + data["operations"][i]["id"] + "\",\"flowRate\":" + str(
                allocate_flow(data)[i]) + "},"
        output = output[:-1] + "]"

        # prints and sends the flow allocation
        print(f"ouput = {output}")
        wsapp.send(output)
    else:
        print(f"response = {message}\n\n")
        pit_volume = data["currentPitVolume"]


def allocate_flow(data):
    """ Stores data and runs the optimization algorithm to determine flow allocation. """

    global pit_volume

    flowRateIn = data["flowRateIn"] + pit_volume
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
        for i in range(1, 21):
            dy = row[i] - row[i - 1]
            dx = 10000
            slope = dy / dx
            slopes_row.append(slope)
        slopes.append(slopes_row)
    maxindeces = []
    for row in points:
        maxindeces.append(row.index(max(row)))
    if sum(maxindeces) * 10000 > flowRateIn:
        while sum(maxindeces) * 10000 - flowRateIn > 10000:
            new = []
            for row in range(len(maxindeces)):
                new.append(max(points[row][:maxindeces[row]]))
            workingRow = 0
            workingDif = points[0][maxindeces[0]] - new[0]
            for row in range(len(maxindeces)):
                dif = points[row][maxindeces[row]] - new[row]
                if dif < workingDif:
                    workingRow = row
                    workingDif = dif
            maxindeces[workingRow] = points[workingRow].index(new[workingRow])
        if sum(maxindeces) * 10000 > flowRateIn:
            maxesofeach = []
            for row in range(len(points)):
                newint = max(points[row][:maxindeces[row]])
                ylimit = (points[row][maxindeces[row]] - slopes[row][maxindeces[row]-1] * (
                        sum(maxindeces) * 10000 - flowRateIn)) if maxindeces[row] != 0 else 0
                maxesofeach.append([max([newint, ylimit]), ylimit > newint])
            workingRow = maxesofeach.index(max(maxesofeach))
            if not maxesofeach[workingRow][1]:
                maxindeces[workingRow] = points[workingRow].index(maxesofeach[workingRow][0])
            else:
                maxindeces[workingRow] = maxindeces[workingRow] - sum(maxindeces) + flowRateIn / 10000
    for i in range(len(maxindeces)):
        maxindeces[i] = maxindeces[i] * 10000
    return maxindeces


def on_open(wsapp):
    wsapp.send("{\"setPitCapacity\": 100000}")


wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message, on_error=on_error,
                               on_open=on_open)
wsapp.run_forever()
