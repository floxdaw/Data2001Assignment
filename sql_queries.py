import database_setup as ds
import pandas as pd
import geopandas as gpd





# import geoplot #https://stackoverflow.com/questions/70177062/cartopy-not-able-to-identify-geos-for-proj-install-on-windows
import mapclassify

db, conn = ds.pgconnect('Credentials.json')

# Burner query - just used for testing and debugging
sql = """
SELECT s.sa2_name, COUNT(c.use_desc), n.sa2_code
FROM sa2 s 
JOIN catchments c ON (ST_CONTAINS(s.geom, c.geom) OR ST_OVERLAPS(s.geom, c.geom))
FULL OUTER JOIN neighborhoods n USING (sa2_code)
GROUP BY s.sa2_name
ORDER BY count DESC
"""
print(ds.query(conn, sql))

# number of health services per 1000 people
sql = """
SELECT b.sa2_name, b.health_care_and_social_assistance/(n.population/1000) AS ratio
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by ratio DESC
"""
print(pd.DataFrame(ds.query(conn, sql)))

# number of school catchment areas per 1000 young people
sql = """
SELECT s.sa2_name, (CAST (COUNT (ca.use_desc) AS float)) AS s_count, (CAST (n.total_young_people AS float)/1000) AS young_people
FROM sa2 s 
JOIN catchments ca ON (ST_CONTAINS(s.geom, ca.geom) OR ST_OVERLAPS(s.geom, ca.geom))
FULL OUTER JOIN neighborhoods n USING (sa2_code)
GROUP BY s.sa2_name, young_people
"""
print(ds.query(conn, sql))

## green house gas question
sql = """
select suburb, SUM ( ROUND(cast((f2018_19 - f2015_16) AS numeric), 3)) as change
from greenhouse_gas_per_suburb
GROUP BY suburb
ORDER BY suburb;
"""
print(ds.query(conn, sql))



# ds.close_connection(conn, db)
