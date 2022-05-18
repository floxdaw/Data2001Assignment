import data_cleaning as dc
import database_setup as ds
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry





db, conn = ds.pgconnect('Credentials.json')
# Creating SQLAlchemy's engine to use




conn.execute("""
DROP TABLE IF EXISTS sa2;
CREATE TABLE sa2(
   sa2_main16 INTEGER PRIMARY KEY,
   sa2_5dig16 INTEGER,
   sa2_name16 VARCHAR(100),
   sa3_code16 INTEGER,
   sa3_name16 VARCHAR(100),
   sa4_code16 INTEGER,
   sa4_name16 VARCHAR(100),
   areasqkm16 FLOAT,
   geom GEOMETRY(MULTIPOLYGON,4283)
);""")
SA2 = dc.SA2
SA2.to_sql('sa2', conn, if_exists='append', index=False, dtype={'geom': Geometry(geometry_type='MULTIPLOYGON', srid= 4283)})

neighbours = dc.neighbours

ds.close_connection(conn, db)