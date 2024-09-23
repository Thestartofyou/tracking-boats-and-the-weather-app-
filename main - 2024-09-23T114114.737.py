import requests
import folium
from haversine import haversine

# Replace 'YOUR_API_KEY' and 'YOUR_WEATHER_API_KEY' with your actual API keys
API_KEY = 'YOUR_API_KEY'
WEATHER_API_KEY = 'YOUR_WEATHER_API_KEY'
API_URL = 'https://services.marinetraffic.com/api/exportvesseltrack'

# Function to calculate the distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return haversine((lat1, lon1), (lat2, lon2))

# Function to get weather data for a specific location
def get_weather_data(lat, lon):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)
    if weather_response.status_code == 200:
        return weather_response.json()
    else:
        return None

# Function to check proximity alerts between boats
def check_proximity_alert(boats, threshold=0.5):  # Threshold in nautical miles
    for i, boat1 in enumerate(boats):
        for j, boat2 in enumerate(boats):
            if i != j:
                distance = calculate_distance(boat1['Lat'], boat1['Lon'], boat2['Lat'], boat2['Lon'])
                if distance < threshold:
                    print(f"⚠️ Alert: {boat1['VesselName']} and {boat2['VesselName']} are too close! Distance: {distance:.2f} nautical miles")

# Function to plot boats on a map
def plot_boats_on_map(boats):
    # Create a folium map centered on Boston Harbor
    m = folium.Map(location=[42.3601, -71.0589], zoom_start=12)
    
    for boat in boats:
        weather = get_weather_data(boat['Lat'], boat['Lon'])
        weather_info = ''
        if weather:
            weather_info = f"\nWeather: {weather['weather'][0]['description']}, Temp: {weather['main']['temp']}°C"
        
        # Add a marker for each boat
        folium.Marker(
            [boat['Lat'], boat['Lon']],
            popup=f"{boat['VesselName']} (Type: {boat['VesselType']}, Speed: {boat['Speed']} knots){weather_info}"
        ).add_to(m)
    
    # Save map to an HTML file
    m.save('boats_in_boston_harbor.html')
    print("Map has been saved to 'boats_in_boston_harbor.html'")

# Function to get boats in Boston Harbor from the MarineTraffic API
def get_boats_in_boston_harbor():
    params = {
        'apikey': API_KEY,
        'v': '1',  # API version
        'msgtype': 'getvessels',
        'lat': '42.3601',  # Latitude for Boston Harbor
        'lon': '-71.0589',  # Longitude for Boston Harbor
        'radius': '10'  # Radius in nautical miles
    }
    
    # Make the API request
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        boats = response.json()

        # Display boat information and proximity alerts
        for boat in boats:
            print(f"Vessel Name: {boat['VesselName']}, "
                  f"Type: {boat['VesselType']}, "
                  f"Latitude: {boat['Lat']}, "
                  f"Longitude: {boat['Lon']}, "
                  f"Speed: {boat['Speed']} knots")
        
        # Check for proximity alerts
        check_proximity_alert(boats)

        # Plot the boats on a map
        plot_boats_on_map(boats)
    else:
        print("Error fetching data:", response.status_code, response.text)

if __name__ == "__main__":
    get_boats_in_boston_harbor()
