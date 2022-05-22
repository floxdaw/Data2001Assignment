import database_setup as ds
import pandas as pd
import geopandas as gpd

db, conn = ds.pgconnect('Credentials.json')


def normalise(column_string, dataset):
    return (dataset[column_string] - dataset[column_string].min()) / (
            dataset[column_string].max() - dataset[column_string].min())


### Get df for Health care

health = gpd.read_postgis("""
SELECT b.sa2_name, b.health_care_and_social_assistance/(n.population/1000) AS health_ratio, s.geom
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
""", conn)

# to correct for a business district with very few people living there, so that the later normalisation isn't whacked
# out
health.loc[health['health_ratio'] > 40, 'health_ratio'] = 40

# fill an na values with 0
health['health_ratio'] = health['health_ratio'].fillna(0)

# add a normalised column
# health['normalised_ratio'] = normalise('health_ratio', health)

# break and enter

b_and_e = pd.read_sql("""
SELECT sa2_name,
       COUNT(CASE WHEN UPPER(A.density) LIKE 'LOW%%' THEN 1
            WHEN UPPER(A.density) LIKE 'MEDIUM%%'THEN 2
            WHEN UPPER(A.density) LIKE 'HIGH%%' THEN 3
       END) / B.areasqkm AS "density"
  FROM b_and_e A JOIN sa2 B ON (ST_CONTAINS(B.geom, A.geom) OR ST_OVERLAPS(B.geom, A.geom))
 GROUP BY B.sa2_name, B.areasqkm
 ORDER BY "density" DESC
""", conn)

# Catchments
catchments = pd.read_sql("""
SELECT s.sa2_name, (CAST (COUNT (ca.use_desc) AS float)) AS school_count, (CAST (n.total_young_people AS float)/1000) AS young_people
FROM sa2 s 
JOIN catchments ca ON (ST_CONTAINS(s.geom, ca.geom) OR ST_OVERLAPS(s.geom, ca.geom))
FULL OUTER JOIN neighborhoods n USING (sa2_code)
GROUP BY s.sa2_name, young_people
""", conn)

catchments.loc[catchments['young_people'] < 1, 'young_people'] = 1
catchments['school_ratio'] = catchments['school_count']/catchments['young_people']

# accom
accom = pd.read_sql("""
SELECT b.sa2_name, b.accommodation_and_food_services/(n.population/1000) AS accom_ratio
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by accom_ratio DESC
""", conn)

# retail
retail = pd.read_sql("""
SELECT b.sa2_name, b.retail_trade/(n.population/1000) AS retail_ratio
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by retail_ratio DESC
""", conn)

# merging them all into one

merged = pd.merge(retail, accom, how='outer', on='sa2_name')
merged = pd.merge(merged, catchments[['sa2_name','school_ratio']], how='outer', on='sa2_name')
merged = pd.merge(merged, b_and_e, how='outer', on='sa2_name')
merged = pd.merge(merged, health, how='outer', on='sa2_name')


geodata_to_plot = gpd.GeoDataFrame(merged, crs=4283, geometry='geom')

merged.drop(columns="geom", inplace=True)
merged.to_csv(r'task_2data.csv', index = False)


ds.close_connection(conn, db)