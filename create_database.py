import data_cleaning as dc
import database_setup as ds
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry

db, conn = ds.pgconnect('Credentials.json')

conn.execute("""
DROP TABLE IF EXISTS sa2;
CREATE TABLE sa2(
   sa2_code INTEGER PRIMARY KEY,
   sa2_5digit INTEGER,
   sa2_name VARCHAR(100) UNIQUE,
   sa3_code INTEGER,
   sa3_name VARCHAR(100),
   sa4_code INTEGER,
   sa4_name VARCHAR(100),
   areasqkm FLOAT,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")

SA2 = dc.SA2
SA2.to_sql('sa2', conn, if_exists='append', index=False,
           dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid=4283)})


conn.execute("""
DROP TABLE IF EXISTS neighborhoods;
CREATE TABLE neighborhoods(
   sa2_code INTEGER PRIMARY KEY REFERENCES sa2(sa2_code),
   sa2_name VARCHAR(100) REFERENCES sa2(sa2_name),
   land_area FLOAT,
   population FLOAT,
   number_of_dwellings FLOAT,
   median_annual_household_income FLOAT,
   avg_monthly_rent FLOAT,
   total_young_people INTEGER
);""")

neighbours = dc.neighbours
neighbours.to_sql('neighborhoods', conn, if_exists='append', index=False)

conn.execute("""
DROP TABLE IF EXISTS business_stats;
CREATE TABLE business_stats(
   sa2_code INTEGER PRIMARY KEY REFERENCES sa2(sa2_code),
   sa2_name VARCHAR(100) REFERENCES sa2(sa2_name),
   number_of_businesses INTEGER,
   accommodation_and_food_services INTEGER,
   retail_trade INTEGER,
   health_care_and_social_assistance INTEGER
);""")

business_stats = dc.business_stats
business_stats.to_sql('business_stats', conn, if_exists='append', index=False)


conn.execute("""
DROP TABLE IF EXISTS b_and_e;
CREATE TABLE b_and_e(
   object_id INTEGER PRIMARY KEY,
   density varchar(50),
   shape_length FLOAT,
   shape_area FLOAT,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")

break_and_enter = dc.break_and_enter
break_and_enter.to_sql('b_and_e', conn, if_exists='append', index=False,
           dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid=4283)})



conn.execute("""
DROP TABLE IF EXISTS catchments;
CREATE TABLE catchments(
   use_id INTEGER PRIMARY KEY,
   catch_type varchar(50),
   use_desc VARCHAR(50),
   kindergarten INTEGER,
   year1 INTEGER,
   year2 INTEGER,
   year3 INTEGER,
   year4 INTEGER,
   year5 INTEGER,
   year6 INTEGER,
   year7 INTEGER,
   year8 INTEGER,
   year9 INTEGER,
   year10 INTEGER,
   year11 INTEGER,
   year12 INTEGER,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")

catchments_all_rows = dc.catchments_all_rows
catchments_all_rows.to_sql('catchments', conn, if_exists='append', index=False,
           dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid=4283)})



conn.execute("""
DROP TABLE IF EXISTS greenhouse_gas_per_suburb;
CREATE TABLE greenhouse_gas_per_suburb(
   object_id INTEGER PRIMARY KEY,
   suburb varchar(50),
   data_category VARCHAR(50),
   f2005_06 FLOAT,
   f2006_07 FLOAT,
   f2007_08 FLOAT,
   f2008_09 FLOAT,
   f2009_10 FLOAT,
   f2010_11 FLOAT,
   f2011_12 FLOAT,
   f2012_13 FLOAT,
   f2013_14 FLOAT,
   f2014_15 FLOAT,
   f2015_16 FLOAT,
   f2016_17 FLOAT,
   f2017_18 FLOAT,
   f2018_19 FLOAT,
   shape_area FLOAT,
   shape_length FLOAT,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")

greenhouse_gas_emissions = dc.greenhouse_gas_emissions
greenhouse_gas_emissions.to_sql('greenhouse_gas_per_suburb', conn, if_exists='append', index=False,
           dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid=4283)})


conn.execute("""
DROP TABLE IF EXISTS walking_counts;
CREATE TABLE walking_counts(
   object_id INTEGER PRIMARY KEY,
   site_id INTEGER REFERENCES walking_sites(site_id),
   location VARCHAR(100) ,
   description VARCHAR(200),
   period VARCHAR(50),
   year INTEGER,
   season VARCHAR(50),
   totalcount INTEGER,
   month VARCHAR(15),
   morning INTEGER,
   afternoon INTEGER,
   night INTEGER
);""")

walking_counts = dc.walking_counts
walking_counts.to_sql('walking_counts', conn, if_exists='append', index=False)


conn.execute("""
DROP TABLE IF EXISTS walking_sites;
CREATE TABLE walking_sites(
   object_id INTEGER PRIMARY KEY,
   site_id INTEGER UNIQUE,
   location VARCHAR(100),
   site_description VARCHAR(200),
   geom GEOMETRY(POINT,4283)
);""")

walking_c_sites = dc.walking_c_sites
walking_c_sites.to_sql('walking_sites', conn, if_exists='append', index=False, dtype={'geom': Geometry('POINT', 4283)})
#ds.close_connection(conn, db)
