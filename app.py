import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# formatting function for pie chart
def my_fmt(x):
    return '{:.1f}%\n({:.0f})'.format(x, totalWater*x/100)


# Title
st.title("EOG Optimization Dashboard")

# Columns setup
col1, col2 = st.columns(2)

with col1:
    # Revenue total
    revenue = 6000000
    deltathingy = 4000
    st.metric(label="Cumulative Revenue", value="$" + str(revenue), delta=deltathingy)

    st.subheader("Instantaneous Revenue (dollars/day)")
    # Line Chart for Revenue
    chart_data = pd.DataFrame([40000, 45000, 35000, 60000, 78000, 20000], columns=[''])
    st.line_chart(chart_data)


    st.subheader("Volume of Water in the Pit (bbls)")

    maxPit = 1000
    chart_data = pd.DataFrame([0, 6, 10, 2, 60, 30, 45], columns=[''])
    st.line_chart(chart_data)

with col2:
    # Pie chart
    totalWater = 10000 + 20000 + 30000 + 40000
    labels = ["Name1", "Name2", "Name3", "Name4"]
    sizes = [10000, 20000, 30000, 40000]
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice

    fig1, ax1 = plt.subplots()
    # explode=explode for the thing below
    plt.title("Current Distribution of Water between Operations")
    ax1.pie(sizes, labels=labels, autopct=my_fmt, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)  # pie chart drawing
