import pandas as pd
import database_setup as ds

db, conn = ds.pgconnect('Credentials.json')

# will need to download Joshs file from FB
livability_scores = pd.read_csv('./livability_data.csv')

rent_and_income = pd.read_sql("""
SELECT n.sa2_name, n.median_annual_household_income as income, n. avg_monthly_rent as rent
FROM neighborhoods n
""", conn)

# removes any roes that are not in the livability dataset
array = []
for index, row in rent_and_income.iterrows():
    if row['sa2_name'] not in list(livability_scores['sa2_name']):
        array.append(index)

rent_and_income.drop(array, axis=0, inplace=True)

# join the 2 data frames using pandas .merge() function


# use the .corr() function to find the correlation between two columns
# Read this if you are lost: https://stackoverflow.com/questions/42579908/use-corr-to-get-the-correlation-between-two-columns
