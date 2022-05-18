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
   area_id INTEGER PRIMARY KEY REFERENCES sa2(sa2_code),
   area_name VARCHAR(100) REFERENCES sa2(sa2_name),
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
   area_id INTEGER PRIMARY KEY REFERENCES sa2(sa2_code),
   area_name VARCHAR(100) REFERENCES sa2(sa2_name),
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
   objectid INTEGER PRIMARY KEY,
   density varchar(50),
   shape_length FLOAT,
   shape_area FLOAT,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")

break_and_enter = dc.break_and_enter
break_and_enter.to_sql('b_and_e', conn, if_exists='append', index=False,
           dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid=4283)})



#ds.close_connection(conn, db)
