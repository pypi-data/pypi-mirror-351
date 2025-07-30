# xa
Accessing information on population in the word.

To install:	```pip install xa```

## Description
The `xa` package provides tools for accessing and estimating population data based on geographical locations. It utilizes MongoDB to store and query geographical and population data, which must be pre-loaded into a MongoDB collection named `geo_pop_density` within a database called `util`.

The main functionalities include:
- Retrieving the population of the nearest location given latitude and longitude.
- Estimating the population within a specified radius of a given point.
- Advanced methods for approximating population based on population density and fuzzy logic approaches.

The data is expected to be in a specific format, derived from the Global Rural-Urban Mapping Project (GRUMP), available from the Socioeconomic Data and Applications Center (SEDAC).

## Usage Examples

### Initializing the GeoPop Class
```python
from xa import Geopop

# Create an instance of Geopop
geo = Geopop()
```

### Getting Population of the Nearest Point
```python
# Latitude and Longitude of New York City
latitude = 40.7128
longitude = -74.0060

# Get population of the nearest point
population = geo.population_of_nearest_latlon(latitude, longitude)
print(f"The population at the nearest point is: {population}")
```

### Estimating Population Within a Radius
```python
# Define radius in kilometers
radius = 50  # 50 km radius

# Estimate population within this radius
estimated_population = geo.population_within_radius(latitude, longitude, radius)
print(f"Estimated population within {radius} km: {estimated_population}")
```

### Advanced Usage: Population Density Approach
```python
# This method estimates population based on density and has not been fully verified.
estimated_population_density = geo.population_within_radius_density_approach_not_verified(latitude, longitude, radius)
print(f"Estimated population using density approach within {radius} km: {estimated_population_density}")
```

## Documentation of Key Functions/Classes

### Class `Geopop`
- `__init__(self, pop_db='util', pop_col='geo_pop_density', ...)`: Initializes the data access connection with MongoDB.
- `population_of_nearest_latlon(self, lat, lon)`: Returns the population of the nearest location to the given latitude and longitude.
- `population_within_radius(self, lat, lon, radius_km)`: Estimates the population within a specified radius of a given point. Uses a simple nearest data point calculation if no data points are within the radius.
- `population_within_radius_density_approach_not_verified(self, lat, lon, radius_km)`: Estimates population using a density approach. Not verified and should be used with caution.

### Helper Functions
- `_import_data_into_mongo(filepath='gl_centroids_utf8.csv', ...)`: Imports data into MongoDB from a specified CSV file. This function is crucial for setting up the database for the `Geopop` class.

## Installation
Ensure that MongoDB is installed and running on your system. Import your geographical and population data into MongoDB using the provided `_import_data_into_mongo` function before using the `Geopop` class functionalities.

For more detailed examples and advanced usage, refer to the function documentation within the code.
