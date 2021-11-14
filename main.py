import streamlit
import websocket
import ast
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import asyncio


def on_error(wsapp, message):
    """ A function to print any error messages """
    print(message)


pit_volume = 0  # initializing some variables
incrementalRevenue = []
deltathingy = 0
currentPitVolume = []
flowRateIn = 0
names = []
flowRateOut = []


def on_message(wsapp, message):
    """ A function called for every message received.
        Stores data and sends back the results of the optimization algorithm. """

    global pit_volume
    global incrementalRevenue
    global deltathingy
    global currentPitVolume
    global flowRateIn
    global names
    global flowRateOut

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

        names = [data["operations"][i]["name"] for i in range(len(data["operations"]))]

        # creates the suitable framework for the flow allocation
        output = "["
        for i in range(0, len(data["operations"])):
            output = output + "{\"operationId\":\"" + data["operations"][i]["id"] + "\",\"flowRate\":" + str(
                allocate_flow(data)[i]) + "},"
        output = output[:-1] + "]"

        flowRateOut = [allocate_flow(data)[i] for i in range(len(data["operations"]))]

        # prints and sends the flow allocation
        print(f"ouput = {output}")
        wsapp.send(output)
    else:
        print(f"response = {message}\n\n")
        # storing the data we need to graph
        pit_volume = data["currentPitVolume"]
        incrementalRevenue.append(int(data["incrementalRevenue"]))
        deltathingy = incrementalRevenue[-1] - incrementalRevenue[-2]
        currentPitVolume.append(data["currentPitVolume"])
        flowRateIn = data["flowRateIn"]
        # app()
        asyncio.run(main())


def allocate_flow(data):
    """ Stores data and runs the optimization algorithm to determine flow allocation. """

    global pit_volume
    global incrementalRevenue
    global deltathingy

    flowRateIn = data["flowRateIn"] + pit_volume
    operations = data["operations"]
    names = []
    points = []
    for operation in operations:
        # makes a 2d array of the revenue points organized by their operation and then location
        points_row = []
        names.append(operation["name"])
        for i in range(21):
            # the index implies the flow rate of the point because flow=index*10000
            points_row.append(operation["revenueStructure"][i]["dollarsPerDay"])
        points.append(points_row)
    slopes = []
    for row in points:
        # 2d array of the slopes between each point
        # linear interpolation, baby
        slopes_row = []
        for i in range(1, 21):
            dy = row[i] - row[i - 1]
            dx = 10000
            slope = dy / dx
            slopes_row.append(slope)
        slopes.append(slopes_row)
    maxindeces = []
    for row in points:
        # initializing our output as the flow rates that maximize the profit for each operation without considering the limit on inflow
        maxindeces.append(row.index(max(row)))
    if sum(maxindeces) * 10000 > flowRateIn:  # continue only if the current water use is out of bounds
        moves = []
        while sum(maxindeces) * 10000 - flowRateIn > 10000:
            new = []
            for row in range(len(maxindeces)):  # the maximum revenues that cost less water than the current maxes
                new.append((max(points[row][0:maxindeces[row]])) if maxindeces[
                                                                        row] != 0 else -99999999)  # hoping -99999999 is low enough to keep dif so high it's out of competition
            workingRow = 0
            workingDif = points[0][maxindeces[0]] - new[0]
            for row in range(len(maxindeces)):
                dif = points[row][maxindeces[row]] - new[row]
                if dif < workingDif:
                    workingRow = row  # finding the minimum difference and corresponding row
                    workingDif = dif
            moves.append(
                [workingDif, maxindeces[workingRow], maxindeces[workingRow] - points[workingRow].index(new[workingRow]),
                 workingRow])  # keeping track of the jumps to cheaper peaks
            maxindeces[workingRow] = points[workingRow].index(new[workingRow])  # updating the maxindeces solution set
        if sum(maxindeces) * 10000 > flowRateIn:  # checking if sliding down from one of the current maxes will make it cross the water threshhold
            maxesofeach = []
            for row in range(len(points)):
                newint = max(points[row][0:maxindeces[
                    row]])  # here we consider the next left peaks (newint) and the points where the slide would bring us (ylimit)
                ylimit = (points[row][maxindeces[row]] - slopes[row][maxindeces[row] - 1] * (
                            sum(maxindeces) * 10000 - flowRateIn)) if maxindeces[row] != 0 else 0
                maxesofeach.append([max([newint, ylimit]),
                                    ylimit > newint])  # array shenanigans to help compare everything and keep track of where it's from
            workingRow = maxesofeach.index(max(maxesofeach))
            if not maxesofeach[workingRow][1]:
                moves.append([points[workingRow][maxindeces[workingRow]] - max(maxesofeach)[0], maxindeces[workingRow],
                              maxindeces[workingRow] - points[workingRow].index(max(maxesofeach)[0]), workingRow])
                maxindeces[workingRow] = points[workingRow].index(maxesofeach[workingRow][0])
                while True:  # undoing sacrifices that we got enough water to undo in the last jump
                    for move in moves:
                        if move[2] > flowRateIn / 10000 - sum(maxindeces):
                            moves.remove(move)
                    if len(moves) == 0:
                        break
                    undoing = max(moves)
                    maxindeces[undoing[3]] = undoing[1]
                    moves.remove(
                        undoing)  # it removes moves it can't afford and moves it does until the moveset is empty
            else:
                maxindeces[workingRow] = maxindeces[workingRow] - sum(
                    maxindeces) + flowRateIn / 10000  # the fated slide
    for i in range(len(maxindeces)):
        maxindeces[i] = maxindeces[i] * 10000  # converts from indeces to actual flow rates
    return maxindeces


def on_open(wsapp):
    wsapp.send("{\"setPitCapacity\": 100000}")
    #app()


async def app():
    global incrementalRevenue
    global deltathingy
    global currentPitVolume
    global flowRateIn
    global names
    global flowRateOut

    st.set_page_config(layout="wide")

    # formatting function for pie chart
    def my_fmt(x):
        return '{:.1f}%\n({:.0f})'.format(x, totalWater * x / 100)

    # Title
    st.title("EOG Optimization Dashboard")

    # Columns setup
    col1, col2 = st.columns(2)

    with col1:
        # Revenue total
        revenue = sum(incrementalRevenue)
        # deltathingy = 4000
        st.metric(label="Cumulative Revenue", value="$" + str(revenue), delta=deltathingy)

        st.subheader("Revenue in last 5 seconds (dollars)")
        # Line Chart for Revenue
        chart_data = pd.DataFrame(incrementalRevenue[-12:] if len(incrementalRevenue) > 11 else incrementalRevenue, columns=[''])
        st.line_chart(chart_data)

        st.subheader("Volume of Water in the Pit (bbls)")

        maxPit = 100000
        chart_data = pd.DataFrame(currentPitVolume[-12:] if len(currentPitVolume) > 11 else currentPitVolume, columns=[''])
        st.line_chart(chart_data)

    with col2:
        # Pie chart
        totalWater = flowRateIn
        labels = names
        sizes = flowRateOut
        # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice

        fig1, ax1 = plt.subplots()
        # explode=explode for the thing below
        plt.title("Current Distribution of Water between Operations")
        ax1.pie(sizes, labels=labels, autopct=my_fmt, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)  # pie chart drawing


async def main():
    task = asyncio.create_task(app())

    await task


wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message, on_error=on_error,
                               on_open=on_open)
wsapp.run_forever()
