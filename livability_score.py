import database_setup as ds
import pandas as pd
import geopandas as gpd
import statistics
import math

db, conn = ds.pgconnect('Credentials.json')

# Get df for Health care

health = gpd.read_postgis("""
SELECT b.sa2_name, b.health_care_and_social_assistance, (n.population/1000) AS per_1000, s.geom
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
""", conn)

health.loc[health['per_1000'] < 1, 'per_1000'] = 1
health['health_ratio'] = health['health_care_and_social_assistance'] / health['per_1000']
health.drop(columns=['health_care_and_social_assistance', 'per_1000'], inplace=True)

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
catchments['school_ratio'] = catchments['school_count'] / catchments['young_people']

# accom
accom = pd.read_sql("""
SELECT b.sa2_name, b.accommodation_and_food_services, (n.population/1000) AS per_1000
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER by per_1000 ASC
""", conn)

accom.loc[accom['per_1000'] < 1, 'per_1000'] = 1
accom['accom_ratio'] = accom['accommodation_and_food_services'] / accom['per_1000']
accom.drop(columns=['accommodation_and_food_services', 'per_1000'], inplace=True)

# retail
retail = pd.read_sql("""
SELECT b.sa2_name, b.retail_trade, (n.population/1000) AS per_1000
FROM business_stats b, neighborhoods n, sa2 s
WHERE b.sa2_name = n.sa2_name
AND s.sa2_name = n.sa2_name
ORDER BY per_1000
""", conn)

retail.loc[retail['per_1000'] < 1, 'per_1000'] = 1
retail['retail_ratio'] = retail['retail_trade'] / retail['per_1000']
retail.drop(columns=['retail_trade', 'per_1000'], inplace=True)
# merging them all into one

merged = pd.merge(retail, accom, how='outer', on='sa2_name')
merged = pd.merge(merged, catchments[['sa2_name', 'school_ratio']], how='outer', on='sa2_name')
merged = pd.merge(merged, b_and_e, how='outer', on='sa2_name')
merged = pd.merge(merged, health, how='outer', on='sa2_name')

geodata_to_plot = gpd.GeoDataFrame(merged, crs=4283, geometry='geom')

merged.drop(columns="geom", inplace=True)

merged['density'] = -merged['density']
merged = merged.fillna(0)

# ok now we have a dataframe made up of each column of all the rations we want, no NaN, the density column is
# negetive one correction we made is that if less than 1000 people live there, we made it 1000, so that the ratio
# wasn't inflated ie (30 shops / 6 people) = 30/(0.006) = 5000 which is obviosuly not right

# the next line just sums each row into the raw livability score
merged['l_score'] = merged[['retail_ratio', 'accom_ratio', 'school_ratio', 'density', 'health_ratio']].sum(axis=1)

# ok this one is a bit complicated. A few of the rows, had a hugely inflated livability score, because no one lived
# there. even after the correction, because we are basing a lot of these on the population, if an industrial area has
# loads of shops and almost no one lives there, it will get a very high score, but this isn't in line with the spirit
# of what we are calculating. So, if a suburbs livability score is more than 2 standard deviations above the mean,
# we are going to class it as an 'outlier' by realising how its score got so inflated. Then we are just going to set
# its score to the mean

merged.loc[merged['l_score'] > statistics.mean(merged['l_score']) + 2 * statistics.stdev(
    merged['l_score']), 'l_score'] = statistics.mean(merged['l_score'])


def normalise(column_string, dataset):  # [-5,5]
    return (10 * ((dataset[column_string] - dataset[column_string].min()) / (
            dataset[column_string].max() - dataset[column_string].min())) - 5)


# then we are going to map all the scores between -5 and 5 (see the function at the
merged['normalised'] = normalise('l_score', merged)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# finally we use the sigmoid function to calcualted the Livability score.
merged['FINAL_SCORE'] = merged['normalised'].apply(sigmoid)
merged.to_csv(r'task_2data.csv', index=False)



## TASK 3
# Greenhouse gas change over the past

greenhouse = pd.read_sql("""
SELECT s.sa2_name, g.suburb,  g.f2018_19, g.f2015_16, (CAST (n.population AS float)/1000) AS per_1000
FROM sa2 s
JOIN greenhouse_gas_per_suburb g ON (ST_OVERLAPS(s.geom, g.geom))
FULL OUTER JOIN neighborhoods n USING (sa2_code)
WHERE s.sa3_name = 'Sydney Inner City'
ORDER BY sa2_name;
""", conn)


greenhouse.loc[greenhouse['per_1000'] < 1, 'per_1000'] = 1
greenhouse = greenhouse.groupby(by=['sa2_name', 'per_1000']).agg({'f2018_19':'sum','f2015_16':'sum'})

greenhouse = greenhouse.reset_index()
greenhouse['change'] = greenhouse['f2015_16'] - greenhouse['f2018_19']
greenhouse['change_per_1000'] = greenhouse['change']/greenhouse['per_1000']
greenhouse.drop(columns = ['change', 'f2015_16', 'f2018_19', 'per_1000'], inplace=True)


ds.close_connection(conn, db)
