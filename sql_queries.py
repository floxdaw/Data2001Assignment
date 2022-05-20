import database_setup as ds
from geoalchemy2 import Geometry

db, conn = ds.pgconnect('Credentials.json')

sql = """
SELECT sa2_name, ST_Area(geom) AS total_area
FROM sa2
LIMIT 5
"""

sql = """
SELECT sa2_name
FROM business_stats
LIMIT 5
"""

print(ds.query(conn, sql))



# ds.close_connection(conn, db)