import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import main
import ast

st.set_page_config(layout="wide")


def my_fmt(x):
    """ formatting function for pie chart """

    return '{:.1f}%\n({:.0f})'.format(x, totalWater * x / 100)


# Title
st.title("EOG Optimization Dashboard")

# Columns setup
col1, col2 = st.columns(2)

with col1:
    # Revenue total
    revenue = sum(main.incrementalRevenue)
    deltathingy = main.incrementalRevenue[-1] - main.incrementalRevenue[-2]
    st.metric(label="Cumulative Revenue", value="$" + str(revenue), delta=deltathingy)

    st.subheader("Instantaneous Revenue (dollars/day)")
    # Line Chart for Revenue
    chart_data = pd.DataFrame(main.incrementalRevenue[-12:], columns=[''])
    st.line_chart(chart_data)

    st.subheader("Volume of Water in the Pit (bbls)")

    maxPit = 100000
    chart_data = pd.DataFrame(main.currentPitVolume[-12:], columns=[''])
    st.line_chart(chart_data)

with col2:
    # Pie chart
    totalWater = main.flowRateIn
    labels = []
    for operation in main.data["operations"]:
        labels.append(ast.literal_eval(operation)["name"])
    sizes = []
    for operation in main.output:
        sizes.append(ast.literal_eval(operation)["flowRate"])
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice

    fig1, ax1 = plt.subplots()
    # explode=explode for the thing below
    plt.title("Current Distribution of Water between Operations")
    ax1.pie(sizes, labels=labels, autopct=my_fmt, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)  # pie chart drawing
