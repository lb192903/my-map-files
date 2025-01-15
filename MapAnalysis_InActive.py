# %%

# %% [markdown]
# Fetching InActive API data
# 

# %%
import requests
import pandas as pd;

# API URL
inactive_url = "https://d4sys.azure-api.net/mywater_services/mw/Inactive_Data_Devices_Report_Bi"

# API Headers (replace with actual values)
headers = {
    "Authorization": "Ocp-Apim-Subscription-Key",  # Replace with your actual API Key if needed
    "Ocp-Apim-Subscription-Key": "789e8f42fa5a4811ab8e7405fc92eba1"  # Replace with your actual Subscription Key
}

# Function to fetch data from the API
def fetch_data(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Data fetched successfully from {url}")
            # Print the full JSON response to inspect its structure
            json_data = response.json()  # Get the JSON data
            print(json_data)  # Print the entire response JSON to understand its structure
            # After inspecting the structure, adjust this line if needed
            return pd.DataFrame(json_data)  # Directly convert the entire JSON to a DataFrame for now
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

# Fetch data from Work Order Report API
wo = fetch_data(inactive_url)

# Save fetched data locally if not empty
if not wo.empty:
    wo.to_csv('inactive.csv', index=False)
    print("In Active data saved as CSV!")
else:
    print("No data fetched. CSV not created.")


# %% [markdown]
# Load Data All Device

# %%
import pandas as pd

# Google Sheets export URL
sheet_url = 'https://docs.google.com/spreadsheets/d/1fcIQm-_-7O7M-TSPQRk20f7T3_uM-jGPJlxLuPiMgo0/export?format=csv'

# Use pandas to read the CSV directly from the Google Sheets link
all_device_df = pd.read_csv(sheet_url)

# Display the first few rows of the data
print(all_device_df.head())


# %%
all_device_df.shape

# %% [markdown]
# Load Data Inactive

# %%
import pandas as pd

# Load the CSV file into a pandas DataFrame
inactive_df = pd.read_csv('inactive.csv')
inactive_df['Cell_Carrier'] =inactive_df['Cell_Carrier'].fillna('N/A')

# Display the first few rows of the DataFrame to check the data
print(inactive_df.head())

# %%
inactive_df.shape

# %%
inactive_df['Cell_Carrier'].value_counts()

# %% [markdown]
# Inner Join Merged Data Frame InActive x All Device
# 

# %%
import pandas as pd

# Perform the inner join
merged_df_inactive = pd.merge(inactive_df, all_device_df, on='sale_order_id', how='inner', suffixes=('_inactive', '_device'))

# Select all columns from work_order_df and add '_wo' suffix to non-'sale_order_id' columns
columns_to_select = [col + '_inactive' if (col != 'sale_order_id' and col in all_device_df.columns) else col for col in inactive_df.columns]

# Add longitude_latitude column from all_device_df
columns_to_select += ['longitude_latitude']

# Select only the desired columns
merged_df_inactive = merged_df_inactive[columns_to_select]

# Split the 'longitude_latitude' column into two separate columns
merged_df_inactive[['longitude', 'latitude']] = merged_df_inactive['longitude_latitude'].str.split(',', expand=True)

# Drop the original 'longitude_latitude' column
merged_df_inactive = merged_df_inactive.drop(columns=['longitude_latitude'])

merged_df_inactive.loc[:, 'latitude'] = pd.to_numeric(merged_df_inactive['latitude'], errors='coerce')
merged_df_inactive.loc[:, 'longitude'] = pd.to_numeric(merged_df_inactive['longitude'], errors='coerce')

# Print the merged DataFrame
print(merged_df_inactive)

# %%
merged_df_inactive['last_data_recived'] = pd.to_datetime(
    merged_df_inactive['last_data_recived'],
    errors='coerce',  # Invalid formats will become NaT
    dayfirst=False     # Ensures correct date parsing (if necessary for your region)
)

# %%
# Format the date as '8 May 2024'
merged_df_inactive['last_data_recived_date'] = merged_df_inactive['last_data_recived'].dt.strftime('%d %B %Y')
# Display the result
print(merged_df_inactive[['last_data_recived', 'last_data_recived_date']])

# %%
merged_df_inactive['last_data_recived_date'].isna().value_counts()

# %%
merged_df_inactive.shape

# %%
merged_df_inactive['Cell_Carrier'].value_counts()

# %% [markdown]
# Maps

# %%
import folium
from IPython.display import display
import pandas as pd
import requests

# %%
# Initialize the map with Pakistan's coordinates
pak_coordinates = [30.3753, 69.3451]  # Pakistan's approximate center
mymap = folium.Map(location=pak_coordinates,
                   zoom_start=6,  # Adjust zoom level to focus more on Pakistan
                   tiles='CartoDB positron')  # Clean map style

# Coordinates for Karachi and Lahore offices
khi_office = (24.8294535, 67.0996171)
lhe_office = (31.4441555, 74.3152238)
isb_office = (33.72615, 73.08500)

# Path to the office logo image
logo_url = 'C:\Laiba\MapAnalysis_Python\Logo.png'  # Adjust this path to match your logo location

# Create separate CustomIcon objects for each marker
khi_icon = folium.CustomIcon(
    icon_image=logo_url,  # Path to the image
    icon_size=(20, 20)    # Adjust size to your preference
)

lhe_icon = folium.CustomIcon(
    icon_image=logo_url,  # Path to the image
    icon_size=(20, 20)    # Adjust size to your preference
)

isb_icon = folium.CustomIcon(
    icon_image=logo_url,  # Path to the image
    icon_size=(20, 20)    # Adjust size to your preference
)

# Add Marker for Karachi Office
folium.Marker(
    location=khi_office,
    popup="Mywater HeadQuarters, Karachi",
    tooltip="Mywater HeadQuarters, Karachi",
    icon=khi_icon
).add_to(mymap)

# Add Marker for Lahore Office
folium.Marker(
    location=lhe_office,
    popup="Mywater, Lahore",
    tooltip="Mywater, Lahore",
    icon=lhe_icon
).add_to(mymap)

# Add Marker for Isb Office
folium.Marker(
    location=isb_office,
    popup="Mywater, Islamabad",
    tooltip="Mywater, Islamabad",
    icon=isb_icon
).add_to(mymap)

# Display the map
mymap

# %%
import requests
import folium
from IPython.display import display

# URL for the outer boundary GeoJSON data (PAK_adm0.json)
geojson_url = 'https://raw.githubusercontent.com/PakData/GISData/master/PAK-GeoJSON/PAK_adm0.json'

# Fetch GeoJSON data
try:
    geojson_data = requests.get(geojson_url).json()

    # Adding the outer boundary of Pakistan from the fetched GeoJSON to the map
    folium.GeoJson(
        geojson_data,
        name="Pakistan Outer Boundary",
        style_function=lambda x: {
            'fillColor': 'transparent',  # Transparent fill (only the outline is visible)
            'color': 'black',            # Border color
            'weight': 2,                 # Thickness of the outline
            'opacity': 1.0        # Full opacity
        }).add_to(mymap)

    # Display the map
    display(mymap)

except Exception as e:
    print(f"Error loading GeoJSON: {e}")

# %%
import folium
from geopy.distance import geodesic
from folium import plugins
from IPython.display import display

# Remove rows with missing latitude or longitude values
merged_df_inactive_notna = merged_df_inactive.dropna(subset=['latitude', 'longitude'])

# Add a new column for the activation year
merged_df_inactive_notna['activation_year'] = pd.to_datetime(merged_df_inactive_notna['activation_date']).dt.year

# Define the city groups for each office
karachi_cities = ["Karachi", "Hyderabad", "Thata"]  # Cities to calculate distance from Karachi office
lahore_cities = ["Lahore", "Sialkot"]  # Cities to calculate distance from Lahore office
isb_cities = ["Rawalpindi","Islamabad Capital Territory"]

# Check for Ufone condition based on the ccid
merged_df_inactive_notna['Cell_Carrier'] = merged_df_inactive_notna.apply(
    lambda row: "Ufone" if str(row['ccid_inactive']).startswith("89410") else row['Cell_Carrier'], axis=1
)

carrier_colors = {
    "JAZZ": "#FF5733",   # Jazz: Bold red
    "ZONG": "#F1C40F",    # Zong: Warm gold (distinct from red)
    "N/A": "#3498DB",     # WiFi (N/A): Blue (cool tone to contrast with gold)
    "Ufone": "#1ABC9C"    # Ufone: Teal (greenish blue)
}

# Count the occurrences of each carrier
carrier_counts = merged_df_inactive_notna['Cell_Carrier'].value_counts()

# Add all points with respective colors based on the Cell_Carrier
for index, row in merged_df_inactive_notna.iterrows():
    # Get the carrier color
    carrier = row['Cell_Carrier']
    color = carrier_colors.get(carrier, 'gray')  # Default to gray if carrier is unknown

     # Get the activation year color
    city = row['city_inactive']  # Get the city for the current row
    activation_year = row['activation_year']
    # Check if the city belongs to Karachi or Lahore group and calculate distance
    if city in karachi_cities:
        city_location = khi_office
        distance_to_city = geodesic(city_location, (row['latitude'], row['longitude'])).km
    elif city in lahore_cities:
        city_location = lhe_office
        distance_to_city = geodesic(city_location, (row['latitude'], row['longitude'])).km
    elif city in isb_cities:
        city_location = isb_office
        distance_to_city = geodesic(city_location, (row['latitude'], row['longitude'])).km
    else:
        nearest_city = "Unknown City"
        distance_to_city = None

   # Prepare tooltip with required details
    tooltip_text = f"""
    <b>Customer Name:</b> {' '.join(row['full_name'].split(' ')[:2])}</b><br>
    <b>Activation Year:</b> {row['activation_year']}<br>
    <b>ID:</b> {row['device_id_inactive']}<br>
    <b>Area:</b> {row['area']}<br>
    <b>Last Data Recieved:</b> {row['last_data_recived_date']}<br>
    <b>Distance:</b> {distance_to_city:.2f} km<br>
    """

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,  # Small circle size
        color=color,  # Use dynamic color based on Cell_Carrier
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=tooltip_text,
        tooltip=tooltip_text
    ).add_to(mymap)

# Create the legend with counts
legend_html = '''
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 250px;
    height: auto;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding: 10px;
    border-radius: 8px;
">
    <b>Inactive Fleet</b><br>
    <ul style="list-style: none; padding: 0; margin: 0;">
'''
for carrier, color in carrier_colors.items():
    display_name = "WiFi" if carrier == "N/A" else carrier  # Rename NA to WiFi
    count = carrier_counts.get(carrier, 0)  # Get the count for the carrier
    legend_html += f'<li style="margin-bottom: 5px;"><span style="background-color:{color}; width: 12px; height: 12px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span>{display_name}: {count}</li>'

legend_html += '</ul></div>'

# Add the legend to the map
mymap.get_root().html.add_child(folium.Element(legend_html))

# Save the map as an HTML file
mymap.save("inactive_fleet.html")

# Display a message confirming the map has been saved
print("Map has been saved as inactive_fleet.html in your browser to view the map.")

display(mymap)
