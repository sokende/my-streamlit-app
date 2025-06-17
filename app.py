import streamlit as st
import geemap.foliumap as geemap
import geopandas as gpd
import ee

# Initialize Earth Engine
ee.Initialize()

st.set_page_config(layout="wide")

st.title("🌍 Interactive Farm Analysis Web App")
st.markdown("This app displays geospatial data layers for a farm in Spain.")

# Sidebar file upload or use preset shapefile
with st.sidebar:
    st.header("🗂 Upload Shapefile")
    st.write("Currently using a built-in shapefile")
    # For now, use local file
    shapefile_path = 'data/examplefarm.shp'

# Create Map
Map = geemap.Map(center=(37.38, -2.39), zoom=14)

# Load and convert shapefile to EE
gdf = gpd.read_file(shapefile_path)
ee_fc = geemap.geopandas_to_ee(gdf)
farm_ee = ee_fc.geometry()

# Layers
Map.add_basemap('SATELLITE')
Map.addLayer(ee_fc, {'color': 'red', 'width': 2}, 'Farm Boundary')

# 1. Land Cover
landcover = ee.Image('ESA/WorldCover/v100/2020').select('Map')
landcover_vis = {
    'min': 10, 'max': 100,
    'palette': [
        '006400', 'ffbb22', 'ffff4c', 'f096ff', 'fa0000', 'b4b4b4', 'f0f0f0',
        '0064c8', '0096a0', '00cf75', 'fae6a0'
    ]
}
Map.addLayer(landcover.clip(farm_ee), landcover_vis, 'Land Cover')

# 2. Soil Organic Carbon
soil = ee.Image('OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02').select('b0')
soil_vis = {
    'min': 0, 'max': 10,
    'palette': ['ffffa0', 'f7fcb9', 'd9f0a3', 'addd8e', '78c679', '41ab5d', '238443', '005b29']
}
Map.addLayer(soil.clip(farm_ee), soil_vis, 'Soil Organic Carbon')

# 3. Precipitation
precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
    .filterBounds(farm_ee) \
    .filterDate('2024-01-01', '2024-12-31') \
    .sum()

precip_vis = {'min': 0, 'max': 500, 'palette': ['white', 'blue']}
Map.addLayer(precip.clip(farm_ee), precip_vis, 'Precipitation')

# 4. Slope
elevation = ee.Image('USGS/SRTMGL1_003')
slope = ee.Terrain.slope(elevation)
slope_vis = {'min': 0, 'max': 20, 'palette': ['white', 'brown']}
Map.addLayer(slope.clip(farm_ee), slope_vis, 'Slope')

# 5. Drought Risk
drought = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD') \
    .filterBounds(farm_ee) \
    .filterDate('2024-01-01', '2024-12-31') \
    .mean()
drought_vis = {'min': -2, 'max': 2, 'palette': ['red', 'yellow', 'green']}
Map.addLayer(drought.clip(farm_ee), drought_vis, 'Drought Risk')

# 6. NDVI
ndvi = ee.ImageCollection('COPERNICUS/S2') \
    .filterBounds(farm_ee) \
    .filterDate('2024-06-01', '2024-06-30') \
    .mean().normalizedDifference(['B8', 'B4'])
ndvi_vis = {'min': -1, 'max': 1, 'palette': ['brown', 'yellow', 'green']}
Map.addLayer(ndvi.clip(farm_ee), ndvi_vis, 'NDVI')

# 7. Temperature Anomaly (with check)
temperature_collection = ee.ImageCollection('NASA/GLDAS/V021/NOAH/G025/T3H') \
    .filterBounds(farm_ee) \
    .filterDate('2024-01-01', '2024-12-31')

if temperature_collection.size().getInfo() > 0:
    temperature_anomaly = temperature_collection.mean().select('Tair_f_inst')
    temperature_vis = {'min': 250, 'max': 320, 'palette': ['blue', 'yellow', 'red']}
    Map.addLayer(temperature_anomaly.clip(farm_ee), temperature_vis, 'Temperature Anomaly')

# 8. River Basin
river_basins = ee.FeatureCollection("WWF/HydroSHEDS/v1/Basins/hybas_6")
basin_vis = {'color': 'blue', 'width': 2}
Map.addLayer(river_basins, basin_vis, 'River Basin Outlines')

# Display the map
Map.to_streamlit(height=700)
