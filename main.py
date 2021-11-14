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
        ave_flow = str(data["flowRateIn"] / len(data["operations"]))

        # creates the suitable framework for the flow allocation
        output = "["
        for i in range(0, len(data["operations"])):
            output = output + "{\"operationId\":\"" + data["operations"][i]["id"] + "\",\"flowRate\":" + ave_flow + "},"
        output = output[:-1] + "]"

        # prints and sends the flow allocation
        print(f"ouput = {output}")
        wsapp.send(output)
    else:
        print(f"response = {message}\n\n")


def allocate_flow(data):
    """ Stores data and runs the optimization algorithm to determine flow allocation. """

    flowRateIn = data["FlowRateIn"]
    operations = data["operations"]
    names = []
    points = []
    for operation in operations:
        points_row = []
        names.append(operation["name"])
        points_row.append(operation["revenueStructure"]["dollarsPerDay"])
        points.append(points_row)

    slopes = []
    for row in points:
        slopes_row = []
        for i in range(1, len(row)+1):
            dy = row[i] - row[i-1]
            dx = 10000
            slope = dy/dx
            slopes_row.append(slope)
        slopes.append(slopes_row)



wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message, on_error=on_error)
wsapp.run_forever()
