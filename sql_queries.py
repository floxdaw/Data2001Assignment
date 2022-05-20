import database_setup as ds
from geoalchemy2 import Geometry
import matplotlib.pyplot as plt
import geopandas as gpd

db, conn = ds.pgconnect('Credentials.json')

#Burner query - just used for testing and debugging
sql = """
SELECT b.sa2_name, b.health_care_and_social_assistance AS count, (n.population/1000) AS pop
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by count DESC
"""
print(ds.query(conn, sql))


# number of health services per 1000 people
sql = """
SELECT b.sa2_name, b.health_care_and_social_assistance/(n.population/1000) AS ratio,s.geom
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by ratio DESC
"""
print(ds.query(conn, sql))
health = gpd.read_postgis("""
SELECT b.sa2_name, b.health_care_and_social_assistance/(n.population/1000) AS ratio,s.geom
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
""", conn)

health.plot(cmap='Set2', figsize=(10, 10))

# number of schools catchment areas per 1000 ’young people
sql = """
SELECT c.use_id, c.catch_type, c.use_desc
FROM catchments c
"""
print(ds.query(conn, sql))


# ds.close_connection(conn, db)