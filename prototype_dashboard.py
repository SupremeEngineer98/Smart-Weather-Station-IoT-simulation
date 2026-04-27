##Interactive dashboard for sensor data!
#------------------------------------------
#-----------------Important----------------
# Before running the dashboard run the following command to collect data: py main.py
# To run the dashboard use the following command: py -m streamlit run prototype_dashboard.py
#------------------------------------------
#This streamlit app reads data from 'sensor_data.csv' and provides multiple visualization options:
# 1. Line chart of all sensors!
# 2. Histogram of all sensors!
# 3. Boxplot for sensor variation!
# 4. Scatter plot (temperature vs humidity)!
# 5. Gauge chart for current Temperature!
# 6. Rolling average trend for Temperature and Gas Resistance!


#Extra features for the assignment!
# 1. Rolling average lines!
# 2. Threshold highlighting!
# 3. Interactive sensor collection!
# 4. Date filtering!

##importing the required modules and libraries!
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from wifi_connection import Wifi #this is a custom library that you can find inside the folder. This library simulates the wifi connection process!
import datetime
from time import sleep
import plotly.graph_objects as go



#loading csv data!
csv_file = 'sensor_data.csv'




def load_data():
   
    #Loading and parsing sensor data from the CSV file produced by CSVLogger!

    #Reading 'sensor_data.csv' into a pandas DataFrame, parsing the timestamp
    #column using a mixed date format with day-first ordering to handle the
    #human-readable format written by CSVLogger!
    #Any rows with unparseable timestamps are silently dropped using errors='coerce'
    #to prevent the dashboard from crashing on malformed data!

    #Returning:
        #pd.DataFrame: A cleaned DataFrame with columns:
            #- 'timestamp' (datetime): Parsed datetime index for time-series plots!
           # - 'ldr' (float): Light intensity readings (0-100)!
            #- 'uv' (float): UV radiation readings (0-800)!
            #- 'temperature' (float): Temperature in Celsius!
            #- 'humidity' (float): Relative humidity percentage!
            #- 'pressure' (float): Atmospheric pressure in hPa!
            #- 'gas_resistance' (float): Gas resistance in Ohms!
   
    df = pd.read_csv('sensor_data.csv')
    #using errors='coerce' to turn any bad timestamps into NaT instead of crashing!
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=True, errors='coerce')
    # dropping! rows where timestamp could not be parsed!
    df = df.dropna(subset=['timestamp'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.warning(f"{csv_file} not found. Please run csv_logger/sensor_runner first!")
    st.stop()


#sidebar Filters!
st.sidebar.header("Filters")

# Date filtering using selectbox instead of date_input, so only dates that
# actually exist in the dataset are selectable. The end date list is dynamically
# filtered to only show dates >= start_date, preventing invalid date ranges.
available_dates = sorted(df['timestamp'].dt.date.unique())

start_date = st.sidebar.selectbox(
    "Start Date",
    options=available_dates,
    index=0,
    format_func=lambda d: d.strftime("%d %b %Y")
)

valid_end_dates = [d for d in available_dates if d >= start_date]
end_date = st.sidebar.selectbox(
    "End Date",
    options=valid_end_dates,
    index=len(valid_end_dates) - 1,
    format_func=lambda d: d.strftime("%d %b %Y")
)

df_filtered = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

#sensor selection!
sensor_options = ['ldr', 'uv', 'temperature', 'humidity', 'pressure', 'gas_resistance']
selected_sensors = st.sidebar.multiselect("Select Sensors", sensor_options, default=sensor_options)

#chart selection!
chart_type = st.sidebar.selectbox("Select Chart Type",
                                  ['Line Chart', 'Histogram', 'Boxplot', 'Scatter', 'Gauge', 'Rolling Average'])

# per-sensor alert thresholds - values above these limits trigger a warning in the dashboard!
# thresholds are based on typical environmental safety and comfort ranges!
thresholds = {
    "temperature": 30, # Celsius - above 30 considered uncomfortably hot!
    "humidity": 80, # % - above 80 indicates high moisture risk!
    "uv": 600, # sensor units - above 600 indicates strong UV exposure!
    "ldr": 90, # 0-100 scale - above 90 indicates very high light intensity!
    "pressure": 1020, # hPa - above 1020 indicates high pressure system!
    "gas_resistance": 20000 # Ohms - below 20000 may indicate VOC/pollution event!
}


#main Dashboard!

st.title("Smart Weather Station")


#line Chart!
if chart_type == 'Line Chart':
    st.subheader("Line Chart of Selected Sensors")
    df_plot = df_filtered.set_index('timestamp')

    
    # iterating over selected sensors and plotting each as a separate line chart
    # with a threshold warning displayed below if any values exceed the limit!
    for sensor in selected_sensors:
        st.markdown(f"**{sensor.capitalize()}**")  # adding a title above each chart!
        st.line_chart(df_plot[sensor], use_container_width=True)
        # checking if any readings exceed the defined threshold and alerting the user!
        over_thresh = df_plot[sensor] > thresholds.get(sensor, np.inf)
        if over_thresh.any():
            st.warning(f"⚠️ {sensor} values above threshold detected!")


#histogram!

elif chart_type == 'Histogram':
    st.subheader("Histogram")
    # creating one subplot per selected sensor, stacked vertically!
    fig, axs = plt.subplots(len(selected_sensors), 1, figsize=(10, 4*len(selected_sensors)))
    if len(selected_sensors) == 1:
        axs = [axs]
    for ax, sensor in zip(axs, selected_sensors):
        ax.set_title(f'{sensor.capitalize()} Distribution')
         # using 15 bins for a balance between detail and readability!
        ax.hist(df_filtered[sensor], bins=15, color='skyblue', edgecolor='black')
        
        ax.set_xlabel(sensor.capitalize())
        ax.set_ylabel("Frequency")
        plt.tight_layout(pad=3.0)##adding some space between each histogram!
    st.pyplot(fig)
    


#boxplot!
elif chart_type == 'Boxplot':
    st.subheader("Boxplot")
    # offering optional min-max normalisation so sensors with different units
    # can be compared side by side on a common 0-1 scale!
    normalize_box = st.checkbox("Normalize values (0-1 scale)", value=True)
    
    fig, ax = plt.subplots(figsize=(10,6))
    
    if normalize_box:
        # normalizing each sensor to 0-1 range using min-max scaling for comparison!
        df_box = df_filtered[selected_sensors].copy()
        df_box = (df_box - df_box.min()) / (df_box.max() - df_box.min())
    else:
        df_box = df_filtered[selected_sensors]
    
    df_box.boxplot(ax=ax)
    ax.set_title("Boxplot of Selected Sensors")
    ax.set_ylabel("Normalized Value (0-1)" if normalize_box else "Value")
    # overlaying red dashed threshold lines when displaying raw values
    # so the user can visually identify sensors operating near their limits!
    if not normalize_box:
        for i, sensor in enumerate(selected_sensors, 1):
            if sensor in thresholds:
                ax.hlines(thresholds[sensor], i-0.4, i+0.4, colors='red', linestyles='--', linewidth=1.5)
    
    st.pyplot(fig)
    
    


# interactive scatter plot!
elif chart_type == 'Scatter':
    st.subheader("Interactive Scatter Plot")
    # allowing the user to select any two numeric columns for the axes
    # making the scatter plot fully dynamic rather than fixed to temperature/humidity!
    numeric_cols = df_filtered.select_dtypes(include='number').columns.tolist()
    x_axis = st.sidebar.selectbox("X-axis", numeric_cols, index=numeric_cols.index('temperature'))
    y_axis = st.sidebar.selectbox("Y-axis", numeric_cols, index=numeric_cols.index('humidity'))

    fig = px.scatter(df_filtered, x=x_axis, y=y_axis,
                     color=y_axis,
                     title=f"{x_axis.capitalize()} vs {y_axis.capitalize()}",
                     height=500)
    
    # adding red dashed threshold lines for both axes if thresholds are defined
    # helping the user identify data points that exceed safe operating ranges!
    if x_axis in thresholds:
     fig.add_vline(x=thresholds[x_axis], line_dash="dash", line_color="red",
                  annotation_text=f"{x_axis} threshold",
                  annotation_position="top right",
                  annotation_yshift=20)
    if y_axis in thresholds:
     fig.add_hline(y=thresholds[y_axis], line_dash="dash", line_color="red",
                  annotation_text=f"{y_axis} threshold",
                  annotation_position="top left",
                  annotation_xshift=10)
    
    st.plotly_chart(fig)


#gauge (Temperature)!
elif chart_type == 'Gauge':
    st.subheader("Sensor Gauge")
    
     # allowing the user to choose which sensor to display on the gauge!
    gauge_sensor = st.selectbox("Select sensor for gauge", selected_sensors)
    latest_val = float(df_filtered[gauge_sensor].iloc[-1])
    mean_val = float(df_filtered[gauge_sensor].mean())
    min_val = float(df_filtered[gauge_sensor].min())
    max_val = float(df_filtered[gauge_sensor].max())
    threshold = thresholds.get(gauge_sensor, max_val)

    # building a three-zone colour-coded gauge:
    # green (0-70% of threshold), yellow (70-100%), red (above threshold)!
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_val,
        # delta compares the latest reading against the session mean!
        # red = rising above average, green = falling below average!
        delta={"reference": mean_val, "increasing": {"color": "red"}, "decreasing": {"color": "green"}},
        title={"text": f"Current {gauge_sensor.capitalize()} reading"},
        gauge={
            "axis": {"range": [min_val, max(max_val, threshold * 1.1)]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [min_val, threshold * 0.7],  "color": "#c8f7c5"},
                {"range": [threshold * 0.7, threshold], "color": "#fff3cd"},
                {"range": [threshold, max(max_val, threshold * 1.1)], "color": "#f8d7da"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.8,
                "value": threshold
            }
        }
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


#rolling average!

elif chart_type == 'Rolling Average':
    st.subheader("Rolling Average Trend")

    # allowing the user to adjust the rolling window size interactively!
     # larger windows produce smoother trends, smaller windows preserve short-term variation!
    window_size = st.slider("Rolling Window Size", 2, 20, 5)
    normalize = st.checkbox("Normalize values (0-1 scale)", value=True)
    
    fig, ax = plt.subplots(figsize=(10,6))
    for sensor in selected_sensors:
        # computing rolling mean over the user-selected window!
        rolling = df_filtered[sensor].rolling(window=window_size).mean()
        # applying min-max normalisation if selected, so all sensors plot on the same scale!
        if normalize:
            rolling = (rolling - rolling.min()) / (rolling.max() - rolling.min())
        ax.plot(df_filtered['timestamp'], rolling, label=f"{sensor} (rolling {window_size})")
        # overlaying threshold lines only when displaying raw values!
        if not normalize:
            thresh = thresholds.get(sensor)
            if thresh:
                ax.axhline(y=thresh, color='red', linestyle='--', label=f"⚠️ {sensor} Threshold")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Normalized Value (0-1)" if normalize else "Sensor Value")
    ax.set_title("Rolling Average Trend")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout() 
    st.pyplot(fig)



#raw Data table!
# displaying the full filtered dataset for manual inspection!
st.subheader("Raw Data")
st.dataframe(df_filtered)










