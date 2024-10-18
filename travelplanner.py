import streamlit as st
import requests
import openrouteservice
import folium
from streamlit_folium import folium_static  # Install this package if you haven't
import json

# API Keys (replace with your own keys)
ORS_API_KEY = "5b3ce3597851110001cf6248dbc0d825bf6d4b69b125fac5de442cbf"
WEATHER_API_KEY = "32b81c71eced042b3edd4ffd4835d21d"
GOOGLE_MAPS_API_KEY = "AIzaSyD_MbTkxPCg2OS6xw5YOkM8KHaKENCoyf0"  # Your Google Maps API key

# Initialize OpenRouteService client
client = openrouteservice.Client(key=ORS_API_KEY)

# Function to get real-time weather data
def get_weather(city):
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(weather_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error getting weather: {e}")
        return None

# Function to get coordinates using Google Maps API
def get_coordinates(place):
    try:
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(geocode_url)
        response.raise_for_status()
        results = response.json()
        if results['status'] == 'OK':
            coords = results['results'][0]['geometry']['location']
            return (coords['lng'], coords['lat'])
        else:
            st.error("Place not found. Please try another location.")
            return None
    except requests.RequestException as e:
        st.error(f"Error getting coordinates: {e}")
        return None

# Function to get directions between two points
def get_directions(start_coords, end_coords):
    try:
        # Fetching directions
        route = client.directions(coordinates=[start_coords, end_coords], profile='driving-car', format='geojson')
        return route
    except Exception as e:
        st.error(f"Error getting directions: {e}")
        return None

# Streamlit UI styling
st.markdown("""<style>
body {
    background-image: url('https://www.yourimageurl.com/travel_bg.jpg');
    background-size: cover;
}
.stButton button {
    background-color: #4CAF50;
    color: white;
    border-radius: 12px;
    padding: 10px;
    font-size: 16px;
}
.stTextInput > div > input {
    background-color: #f1f1f1;
    border: 2px solid #ccc;
    padding: 10px;
}
h1, h2, h3 {
    color: #4CAF50;
}
</style>""", unsafe_allow_html=True)

# Streamlit app title
st.title("🌍 Advanced Travel Planner with Real-Time Maps")

# User inputs: Start and End points
start_point = st.text_input("📍 Enter your starting location:")
end_point = st.text_input("📍 Enter your destination:")

# Button to confirm
if st.button("🔍 Get Directions"):
    if start_point and end_point:
        st.write(f"Fetching directions from **{start_point}** to **{end_point}**...")

        # Get coordinates
        start_coords = get_coordinates(start_point)
        end_coords = get_coordinates(end_point)

        if start_coords and end_coords:
            # Get directions
            directions = get_directions(start_coords, end_coords)

            if directions:
                route = directions['features'][0]['geometry']['coordinates']
                st.success("Route fetched successfully!")

                # Create a Folium map centered between start and end points
                map_center = [(start_coords[1] + end_coords[1]) / 2, (start_coords[0] + end_coords[0]) / 2]
                m = folium.Map(location=map_center, zoom_start=13)

                # Add start and end points
                folium.Marker(location=[start_coords[1], start_coords[0]], popup='Start', icon=folium.Icon(color='green')).add_to(m)
                folium.Marker(location=[end_coords[1], end_coords[0]], popup='Destination', icon=folium.Icon(color='red')).add_to(m)

                # Add the route to the map
                folium.PolyLine(locations=[(coord[1], coord[0]) for coord in route], color='blue', weight=5, opacity=0.7).add_to(m)

                # Display the map
                st.subheader("Route Map:")
                folium_static(m)  # Use folium_static to render the map in Streamlit

                # Display real-time weather for start and destination
                start_weather = get_weather(start_point)
                end_weather = get_weather(end_point)

                if start_weather:
                    temp = start_weather['main']['temp']
                    description = start_weather['weather'][0]['description']
                    st.info(f"🌡️ Weather in {start_point}: {temp}°C, {description}")

                if end_weather:
                    temp = end_weather['main']['temp']
                    description = end_weather['weather'][0]['description']
                    st.info(f"🌡️ Weather in {end_point}: {temp}°C, {description}")

            else:
                st.error("No directions found. Please check the locations.")
        else:
            st.error("Error retrieving coordinates. Please check your input.")
    else:
        st.error("Please enter both starting and destination locations.")
