import streamlit as st
import requests
from datetime import datetime
import pandas as pd

@st.cache_data(ttl=300)
def get_water_level():
    url = "https://pegelonline.wsv.de/webservices/rest-api/v2/stations/a6ee8177-107b-47dd-bcfd-30960ccc6e9c/W.json?includeCurrentMeasurement=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['currentMeasurement']['value']
    else:
        return "Error fetching data"

@st.cache_data(ttl=300)
def get_forecast_data():
    url = "https://pegelonline.wsv.de/webservices/rest-api/v2/stations/a6ee8177-107b-47dd-bcfd-30960ccc6e9c/WV/measurements.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            return []
    else:
        return []

def format_measurement(measurement):
    """Format measurement data for table display."""
    timestamp = measurement.get('time', '1970-01-01T00:00:00')
    try:
        dt = datetime.fromisoformat(timestamp)
    except ValueError:
        dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')  # Adjust the format if needed
    return {
        'Time': dt.strftime('%d.%m.%Y %H:%M:%S'),
        'Value': f"{measurement.get('value', 'N/A')} cm",
        'Unit': measurement.get('unit', 'N/A')
    }

# Streamlit application code
st.title('Köln Current Water Level and Time Display🌊💧')


# Display the current water level and time
water_level = get_water_level()
current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

st.write(f"The current water level is: {water_level} cm")
st.write(f"Current date and time: {current_time}")

# Display the forecast table
st.subheader('Pegel-Vorhersage Köln')

forecast_data = get_forecast_data()
if forecast_data:
    # Convert the forecast data to a DataFrame for easier handling
    df = pd.DataFrame([format_measurement(item) for item in forecast_data])
    
    # Display the table
    st.table(df)

    # Prepare data for plotting
    df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S')
    df['Value'] = df['Value'].str.replace(' cm', '').astype(float)

    st.subheader('Pegel Diagramm')
    
    # Plot the data
    st.line_chart(df.set_index('Time')['Value'])
else:
    st.write("No forecast data available")

# Checkbox to toggle Markdown text
show_markdown = st.checkbox('Show Additional Information')

if show_markdown:
    st.markdown("""
    ## Additional Information

    This section provides additional information about the water level forecasts and measurements.
    
    - **Measurement Time**: The timestamp when the measurement was taken.
    - **Value**: The measured water level in centimeters (cm).
    - **Unit**: The unit of measurement, which is typically 'cm' for water level measurements.

    For more details, please refer to the official API documentation or local guidelines.
    """)
