import database_setup as ds
from geoalchemy2 import Geometry

db, conn = ds.pgconnect('Credentials.json')


# number of health services per 1000 people
sql = """
SELECT b.sa2_name, b.health_care_and_social_assistance/(n.population/1000) AS ratio,s.geom
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
LIMIT 5
"""
print(ds.query(conn, sql))



# ds.close_connection(conn, db)