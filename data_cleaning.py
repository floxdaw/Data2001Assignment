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

# Keep only the rows that are part of greater sydney
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

neighbours.rename(
    columns={'area_id': 'sa2_code', 'area_name': 'sa2_name'}, inplace=True)

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
# cast as string
business_stats['area_name'] = business_stats['area_name'].astype('string')

business_stats.rename(
    columns={'area_id': 'sa2_code', 'area_name': 'sa2_name'}, inplace=True)
###################################################################

break_and_enter = gpd.read_file("bae/BreakEnterDwelling_JanToDec2021.shp")

# make lower
break_and_enter.columns = break_and_enter.columns.str.lower()

# cast as string
break_and_enter['density'] = break_and_enter['density'].astype('string')

# change geometry datatype
srid = 4283  # this is the id of the Australian coordinate system
break_and_enter['geom'] = break_and_enter['geometry'].apply(
    lambda x: create_wkt_element(x, srid))  # applying the function

# remove columns we don't need
break_and_enter = break_and_enter.drop(columns=['contour', 'orig_fid', "geometry"])

# rename columns to something nice
break_and_enter.rename(
    columns={'shape_leng': 'shape_length', 'objectid': 'object_id'}, inplace=True)
##################################################################

# reading all files
catchments_future = gpd.read_file("catchments/catchments_future.shp")
catchments_primary = gpd.read_file("catchments/catchments_primary.shp")
catchments_secondary = gpd.read_file("catchments/catchments_secondary.shp")

# combine the 3 catchment shapefiles into one
# remove the dud columns
catchments_all_rows = pd.concat([catchments_primary, catchments_secondary])
catchments_all_rows.drop(columns=['PRIORITY'], inplace=True)
catchments_all_rows = pd.concat([catchments_all_rows, catchments_future])
catchments_all_rows.drop(columns=['ADD_DATE'], inplace=True)

# make lower
catchments_all_rows.columns = catchments_all_rows.columns.str.lower()

catchments_all_rows['use_id'] = catchments_all_rows['use_id'].astype('int64')
catchments_all_rows['catch_type'] = catchments_all_rows['catch_type'].astype('string')
catchments_all_rows['use_desc'] = catchments_all_rows['use_desc'].astype('string')

# bollean convert
catchments_all_rows[
    ['kindergart', 'year1', 'year2', 'year3', 'year4', 'year5', 'year6', 'year7', 'year8', 'year9', 'year10', 'year11',
     'year12']] = catchments_all_rows[
    ['kindergart', 'year1', 'year2', 'year3', 'year4', 'year5', 'year6', 'year7', 'year8', 'year9', 'year10', 'year11',
     'year12']].eq('Y').mul(1)

# cast again
catchments_all_rows['kindergart'] = catchments_all_rows['kindergart'].astype('int64')
catchments_all_rows['year1'] = catchments_all_rows['year1'].astype('int64')
catchments_all_rows['year2'] = catchments_all_rows['year2'].astype('int64')
catchments_all_rows['year3'] = catchments_all_rows['year3'].astype('int64')
catchments_all_rows['year4'] = catchments_all_rows['year4'].astype('int64')
catchments_all_rows['year5'] = catchments_all_rows['year5'].astype('int64')
catchments_all_rows['year6'] = catchments_all_rows['year6'].astype('int64')
catchments_all_rows['year7'] = catchments_all_rows['year7'].astype('int64')
catchments_all_rows['year8'] = catchments_all_rows['year8'].astype('int64')
catchments_all_rows['year9'] = catchments_all_rows['year9'].astype('int64')
catchments_all_rows['year10'] = catchments_all_rows['year10'].astype('int64')
catchments_all_rows['year11'] = catchments_all_rows['year11'].astype('int64')
catchments_all_rows['year12'] = catchments_all_rows['year12'].astype('int64')

# make polygons nice
catchments_all_rows['geom'] = catchments_all_rows['geometry'].apply(
    lambda x: create_wkt_element(x, srid))  # applying the function
catchments_all_rows = catchments_all_rows.drop(columns="geometry")  # deleting the old copy

#
catchments_all_rows.rename(
    columns={'kindergart': 'kindergarten'}, inplace=True)

#
aggregation_functions = {'use_id': 'first', 'kindergarten': 'sum', 'year1': 'sum', 'year2': 'sum', 'year3': 'sum',
                         'year4': 'sum',
                         'year5': 'sum', 'year6': 'sum', 'year7': 'sum', 'year8': 'sum', 'year9': 'sum',
                         'year10': 'sum', 'year11': 'sum', 'year12': 'sum', 'catch_type': 'first',
                         'use_desc': 'first', 'geom': 'first'}
catchments_all_rows = catchments_all_rows.groupby(catchments_all_rows['use_id']).aggregate(aggregation_functions)

#####################################################################


greenhouse_gas_emissions = gpd.read_file("greenhouse/Greenhouse_gas_emissions_profile_by_suburb.shp")
greenhouse_gas_emissions.columns = greenhouse_gas_emissions.columns.str.lower()
greenhouse_gas_emissions['area_subur'] = greenhouse_gas_emissions['area_subur'].astype('string')
greenhouse_gas_emissions['data_categ'] = greenhouse_gas_emissions['data_categ'].astype('string')
greenhouse_gas_emissions['geom'] = greenhouse_gas_emissions['geometry'].apply(
    lambda x: create_wkt_element(x, srid))  # applying the function

# remove columns we don't need
greenhouse_gas_emissions = greenhouse_gas_emissions.drop(columns=["geometry"])

greenhouse_gas_emissions.rename(
    columns={'objectid1': 'object_id', 'area_subur': 'suburb', 'data_categ': 'data_category',
             'shape__are': 'shape_area',
             'shape__len': 'shape_length'}, inplace=True)

bad_col = []

for index, row in greenhouse_gas_emissions.iterrows():
    if row['data_category'] == 'Waste Water (Disaggregated)' or row['data_category'] == 'Other Scope 3 (Disaggregated)':
        bad_col.append(index)

greenhouse_gas_emissions.drop(bad_col, axis=0, inplace=True)
##########################################

walking_counts = pd.read_csv("Walking_count_surveys.csv")

# remove a weird formatting from the month column. Original "2013 - Weekday - October" --> "October"
for index, row in walking_counts.iterrows():
    month = row['Month'].split(' - ')
    walking_counts.iat[index, walking_counts.columns.get_loc('Month')] = month[2]
walking_counts.columns = walking_counts.columns.str.lower()

walking_counts['morning'] = walking_counts.iloc[:, 9:14].sum(axis=1)
walking_counts['afternoon'] = walking_counts.iloc[:, 15:21].sum(axis=1)
walking_counts['night'] = walking_counts.iloc[:, 22:27].sum(axis=1)

walking_counts.drop(walking_counts.iloc[:, 9:27], axis=1, inplace=True)

walking_counts['location'] = walking_counts['location'].astype('string')
walking_counts['description'] = walking_counts['description'].astype('string')
walking_counts['period'] = walking_counts['period'].astype('string')
walking_counts['season'] = walking_counts['season'].astype('string')
walking_counts['month'] = walking_counts['month'].astype('string')

walking_counts.rename(
    columns={'objectid': 'object_id', 'siteid': 'site_id'}, inplace=True)

#################################


walking_c_sites = gpd.read_file("Walking_count_sites.geojson")

walking_c_sites.columns = walking_c_sites.columns.str.lower()

walking_c_sites['location'] = walking_c_sites['location'].astype('string')
walking_c_sites['sitedescription'] = walking_c_sites['sitedescription'].astype('string')

walking_c_sites['geom'] = walking_c_sites['geometry'].apply(lambda x: WKTElement(x.wkt, srid=srid))
walking_c_sites.rename(
    columns={'objectid': 'object_id', 'sitedescription': 'site_description', 'geometry': 'geom'}, inplace=True)

not_in_walking_sites = []
for index, row in walking_counts.iterrows():
    if row['site_id'] not in list(walking_c_sites['site_id']):
        not_in_walking_sites.append(index)

walking_counts.drop(not_in_walking_sites, axis=0, inplace=True)
