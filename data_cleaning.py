import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from geoalchemy2 import Geometry, WKTElement
import matplotlib.pyplot as plt
import database_setup as cd
import numpy as np


def create_wkt_element(geom, srid):
    if geom.geom_type == 'Polygon':
        geom = MultiPolygon([geom])
    return WKTElement(geom.wkt, srid)


################## SA2 Data #############################

SA2 = gpd.read_file("SA2/SA2_2016_AUST.shp")
# Make all column names lowercase
SA2.columns = SA2.columns.str.lower()

#Keep only the rows that are part of greater sydney
SA2 = SA2[SA2["gcc_name16"].str.contains("Greater Sydney") == True]

# Removing redundent regional classifiers gcc_code16'
SA2 = SA2.drop(columns=['gcc_code16', 'gcc_name16', 'ste_code16', 'ste_name16'])

# Remove all entries with no geometry
null_geom = []

for index, row in SA2.iterrows():
    if row['geometry'] is None:
        null_geom.append(index)

SA2.drop(null_geom, axis=0, inplace=True)

# Convert the values from object to more usable forms
SA2['sa2_main16'] = SA2['sa2_main16'].astype('int64')
SA2['sa2_5dig16'] = SA2['sa2_5dig16'].astype('int64')
SA2['sa2_name16'] = SA2['sa2_name16'].astype('string')
SA2['sa3_code16'] = SA2['sa3_code16'].astype('int64')
SA2['sa3_name16'] = SA2['sa3_name16'].astype('string')
SA2['sa4_code16'] = SA2['sa4_code16'].astype('int64')
SA2['sa4_name16'] = SA2['sa4_name16'].astype('string')

# make the column names neater - remove the 16 from the column headings, as we kow all the data is from 2016
SA2.rename(
    columns={'sa2_main16': 'sa2_code', 'sa2_5dig16': 'sa2_5digit', 'sa2_name16': 'sa2_name', 'sa3_code16': 'sa3_code',
             'sa3_name16': 'sa3_name', 'sa4_code16': 'sa4_code', 'sa4_name16': 'sa4_name', 'areasqkm16': 'areasqkm'},
    inplace=True)

# convert geometry into a version that postGIS likes
srid = 4283  # this is the id of the Australian coordinate system

SA2['geom'] = SA2['geometry'].apply(lambda x: create_wkt_element(x, srid))  # applying the function
SA2 = SA2.drop(columns="geometry")  # deleting the old copy



##########################################################

neighbours = pd.read_csv("Neighbourhoods.csv")

# Summing all the ages groups into one 'young people' column
column_names = ['0-4', '5-9', '10-14', '15-19']
neighbours['total_young_people'] = neighbours[column_names].sum(axis=1)

# remove unnecessary index and businessses column. REmove the individual age columns now that we have a sum
neighbours = neighbours.drop(columns=['index', 'number_of_businesses', '0-4', '5-9', '10-14', '15-19'])

# remove punctioan from the random ones that have commas
neighbours['population'] = neighbours['population'].str.replace(r'[^\w\s]+', '')
neighbours['number_of_dwellings'] = neighbours['number_of_dwellings'].str.replace(r'[^\w]+', '')

# cast them all as nice data types
neighbours['area_name'] = neighbours['area_name'].astype('string')
neighbours['population'] = neighbours['population'].astype('float')
neighbours['number_of_dwellings'] = neighbours['number_of_dwellings'].astype('float')


# set empty cells to NaN
neighbours = neighbours.replace('', np.nan, regex=True)

# remove regions not an sa2
not_sa2_region = []
for index, row in neighbours.iterrows():
    if row['area_id'] not in list(SA2['sa2_code']):
        not_sa2_region.append(index)

neighbours.drop(not_sa2_region, axis=0, inplace=True)


############################################################

business_stats = pd.read_csv("BusinessStats.csv")
# Dropping business sctors that are not of intrest
business_stats = business_stats.drop(columns=['public_administration_and_safety', 'transport_postal_and_warehousing',
                                              'agriculture_forestry_and_fishing'])

# remove regions not an sa2
not_sa2_region = []
for index, row in business_stats.iterrows():
    if row['area_id'] not in list(SA2['sa2_code']):
        not_sa2_region.append(index)

business_stats.drop(not_sa2_region, axis=0, inplace=True)
 #cast as string
business_stats['area_name'] = business_stats['area_name'].astype('string')
###################################################################

break_and_enter = gpd.read_file("bae/BreakEnterDwelling_JanToDec2021.shp")

# make lower
break_and_enter.columns = break_and_enter.columns.str.lower()

#cast as string
break_and_enter['density'] = break_and_enter['density'].astype('string')

#change geometry datatype
srid = 4283  # this is the id of the Australian coordinate system
break_and_enter['geom'] = break_and_enter['geometry'].apply(lambda x: create_wkt_element(x, srid))  # applying the function

# remove columns we don't need
break_and_enter = break_and_enter.drop(columns=['contour', 'orig_fid',"geometry"])

# rename columns to something nice
break_and_enter.rename(
    columns={'shape_leng': 'shape_length'}, inplace=True)
##################################################################


catchments_future = gpd.read_file("catchments/catchments_future.shp")
catchments_primary = gpd.read_file("catchments/catchments_primary.shp")
catchments_secondary = gpd.read_file("catchments/catchments_secondary.shp")

#####################################################################


greenhouse_gas_emissions = gpd.read_file("greenhouse/Greenhouse_gas_emissions_profile_by_suburb.shp")

##########################################

walking_counts = pd.read_csv("Walking_count_surveys.csv")

# remove a weird formatting from the month column. Original "2013 - Weekday - October" --> "October"
for index, row in walking_counts.iterrows():
    month = row['Month'].split(' - ')
    walking_counts.iat[index, walking_counts.columns.get_loc('Month')] = month[2]

walking_c_sites = gpd.read_file("Walking_count_sites.geojson")
