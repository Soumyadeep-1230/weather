import streamlit as st
import pyowm
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import dates

# Set page title
st.set_page_config(page_title="Simple Weather App")

# Create header
st.title("Simple Weather App")
api_key = st.secrets["api_key"]
url = f"http://api.openweathermap.org/data/2.5/forecast?q=London&appid={api_key}"
# Setup PyOWM
owm = pyowm.OWM(api_key)
mgr = owm.weather_manager()

# User inputs
location = st.text_input("Enter City Name:", "")
units = st.selectbox("Temperature Unit:", ('celsius', 'fahrenheit'))
graph_type = st.selectbox("Graph Type:", ('Bar Graph', 'Line Graph'))

# Set degree symbol based on selected unit
degree_symbol = "°"
degree_letter = "C" if units == "celsius" else "F"

def get_forecast_data():
    """Get temperature forecast data for the next 5 days"""
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast
    
    days = []
    dates = []
    temp_min = []
    temp_max = []
    humidity_values = []
    
    for weather in forecast:
        day = datetime.utcfromtimestamp(weather.reference_time())
        date = day.date()
        
        if date not in dates:
            dates.append(date)
            temp_min.append(None)
            temp_max.append(None)
            humidity_values.append(None)
            days.append(date)
            
        temp = weather.temperature(unit=units)['temp']
        humidity = weather.humidity
        
        if not temp_min[-1] or temp < temp_min[-1]:
            temp_min[-1] = temp
        if not temp_max[-1] or temp > temp_max[-1]:
            temp_max[-1] = temp
        if not humidity_values[-1] or humidity > humidity_values[-1]:
            humidity_values[-1] = humidity
            
    return days, temp_min, temp_max, humidity_values

def display_current_weather():
    """Display current weather information"""
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    
    # Get weather icon
    icon_url = weather.weather_icon_url(size='4x')
    
    # Get current conditions
    temp = weather.temperature(unit=units)['temp']
    feels_like = weather.temperature(unit=units)['feels_like']
    humidity = weather.humidity
    wind_speed = weather.wind()['speed']
    clouds = weather.clouds
    status = weather.detailed_status
    
    # Create columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(icon_url)
        
    with col2:
        st.subheader(f"{status.title()}")
        st.write(f"**Temperature:** {round(temp)}{degree_symbol}{degree_letter}")
        st.write(f"**Feels like:** {round(feels_like)}{degree_symbol}{degree_letter}")
        st.write(f"**Humidity:** {humidity}%")
        st.write(f"**Wind speed:** {wind_speed} m/s")
        st.write(f"**Cloud cover:** {clouds}%")

def show_forecast():
    """Display temperature forecast as a graph"""
    days, temp_min, temp_max, _ = get_forecast_data()
    
    # Convert days to matplotlib format
    plot_days = dates.date2num(days)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    plt.xlabel('Date')
    plt.ylabel(f'Temperature ({degree_symbol}{degree_letter})')
    plt.title('5-Day Temperature Forecast')
    
    # Format x-axis dates
    plt.xticks(plot_days)
    axes = plt.gca()
    xaxis_format = dates.DateFormatter('%m/%d')
    axes.xaxis.set_major_formatter(xaxis_format)
    
    if graph_type == 'Bar Graph':
        # Create bar chart
        plt.bar(plot_days-0.2, temp_min, width=0.4, color='#42bff4', label='Min')
        plt.bar(plot_days+0.2, temp_max, width=0.4, color='#ff5349', label='Max')
        
        # Add temperature labels
        for i in range(len(plot_days)):
            plt.text(plot_days[i]-0.2, temp_min[i]+1, f"{int(temp_min[i])}{degree_symbol}", 
                     ha='center', va='bottom', color='black', fontsize=9)
            plt.text(plot_days[i]+0.2, temp_max[i]+1, f"{int(temp_max[i])}{degree_symbol}", 
                     ha='center', va='bottom', color='black', fontsize=9)
    else:
        # Create line chart
        plt.plot(plot_days, temp_min, marker='o', linestyle='-', color='#42bff4', label='Min')
        plt.plot(plot_days, temp_max, marker='o', linestyle='-', color='#ff5349', label='Max')
        
        # Add temperature labels
        for i in range(len(plot_days)):
            plt.text(plot_days[i], temp_min[i]-2, f"{int(temp_min[i])}{degree_symbol}", 
                     ha='center', va='top', color='black', fontsize=9)
            plt.text(plot_days[i], temp_max[i]+2, f"{int(temp_max[i])}{degree_symbol}", 
                     ha='center', va='bottom', color='black', fontsize=9)
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Display plot in Streamlit
    st.pyplot(plt)

def show_humidity_forecast():
    """Display humidity forecast"""
    days, _, _, humidity_values = get_forecast_data()
    
    # Convert days to matplotlib format
    plot_days = dates.date2num(days)
    
    # Create figure
    plt.figure(figsize=(10, 6))
    plt.xlabel('Date')
    plt.ylabel('Humidity (%)')
    plt.title('5-Day Humidity Forecast')
    
    # Format x-axis dates
    plt.xticks(plot_days)
    axes = plt.gca()
    xaxis_format = dates.DateFormatter('%m/%d')
    axes.xaxis.set_major_formatter(xaxis_format)
    
    # Create bar chart
    plt.bar(plot_days, humidity_values, color='#42bff4')
    
    # Add humidity labels
    for i in range(len(plot_days)):
        plt.text(plot_days[i], humidity_values[i]+2, f"{humidity_values[i]}%", 
                 ha='center', va='bottom', color='black', fontsize=9)
    
    plt.grid(True, alpha=0.3)
    
    # Display plot in Streamlit
    st.pyplot(plt)

def show_sunrise_sunset():
    """Display sunrise and sunset times"""
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    
    sunrise_unix = datetime.utcfromtimestamp(int(weather.sunrise_time()))
    sunset_unix = datetime.utcfromtimestamp(int(weather.sunset_time()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sunrise")
        st.write(f"**Date:** {sunrise_unix.date()}")
        st.write(f"**Time:** {sunrise_unix.time().strftime('%H:%M:%S')}")
        
    with col2:
        st.subheader("Sunset")
        st.write(f"**Date:** {sunset_unix.date()}")
        st.write(f"**Time:** {sunset_unix.time().strftime('%H:%M:%S')}")

def show_weather_alerts():
    """Display upcoming weather alerts"""
    forecaster = mgr.forecast_at_place(location, '3h')
    
    # Create columns for alerts
    col1, col2 = st.columns(2)
    
    alerts = []
    
    if forecaster.will_have_clouds():
        alerts.append("☁️ Clouds expected")
    if forecaster.will_have_rain():
        alerts.append("🌧️ Rain expected")
    if forecaster.will_have_snow():
        alerts.append("❄️ Snow expected")
    if forecaster.will_have_fog():
        alerts.append("🌫️ Fog expected")
    if forecaster.will_have_storm():
        alerts.append("⛈️ Storm expected")
    if forecaster.will_have_hurricane():
        alerts.append("🌀 Hurricane expected")
    if forecaster.will_have_tornado():
        alerts.append("🌪️ Tornado expected")
    
    with col1:
        st.subheader("Weather Alerts")
    
    with col2:
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("No weather alerts")

# Main application logic
if st.button("Get Weather"):
    if not location:
        st.warning("Please enter a city name")
    else:
        try:
            # Create sections with separators
            st.markdown("---")
            st.header("Current Weather")
            display_current_weather()
            
            st.markdown("---")
            st.header("5-Day Forecast")
            show_forecast()
            
            st.markdown("---")
            st.header("Humidity Forecast")
            show_humidity_forecast()
            
            st.markdown("---")
            st.header("Sunrise & Sunset")
            show_sunrise_sunset()
            
            st.markdown("---")
            st.header("Weather Alerts")
            show_weather_alerts()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("If city not found, try format: 'city, country code' (e.g. 'London, GB')")

# Footer
st.markdown("---")
st.caption("Data provided by OpenWeatherMap")