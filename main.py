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

        # uses the average flow as a placeholder for the allocation
        # allocated_flows = allocate_flow(data)

        # creates the suitable framework for the flow allocation
        output = "["
        for i in range(len(data["operations"])):
            output = output + "{\"operationId\":\"" + data["operations"][i]["id"] + "\",\"flowRate\":" + str(data["flowRateIn"]/len(data["operations"])) + "},"
        output = output[:-1] + "]"

        # prints and sends the flow allocation
        print(f"output = {output}")
        wsapp.send(output)
    else:
        print(f"response = {message}\n\n")


def allocate_flow(data):
    """ Stores data and runs the optimization algorithm to determine flow allocation. """

    flowRateIn = data["flowRateIn"]
    operations = data["operations"]
    names = []

    # step 1
    points = []
    for operation in operations:
        points_row = []
        names.append(operation["name"])
        points_row.append(operation["revenueStructure"]["dollarsPerDay"])
        points.append(points_row)

    # step 2
    slopes = []
    for row in points:
        slopes_row = []
        for i in range(1, len(row)+1):
            dy = row[i] - row[i-1]
            dx = 10000
            slope = dy/dx
            slopes_row.append(slope)
        slopes.append(slopes_row)


    # step 3
    flow_at_maxes = []
    for row in points:
        max_index = row.index(max(row))
        flow_at_maxes.append(max_index * 10000)

    if sum(flow_at_maxes) < flowRateIn:
        return flow_at_maxes
    else:
        slopes_before_maxes = []
        for slope_row in slopes:
            slopes_before_maxes.append(slope_row[max_index-1])

        min_slope = min(slopes_before_maxes)
        min_slope_index = slopes_before_maxes.index(min_slope)



wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message, on_error=on_error)
wsapp.run_forever()
