##So the steps I have taken so far:

####File 1 - database_setup.py

Here, I pretty much copied 1-for-1 the helper functions from Wk4 and Wk9 tutorials so that we can connect to the database and add tables.
Use the "Credentials.json" file to connect to my database.

####File 2 - data_cleaning.py

This is the file where I ingested and cleaned all th data with python scripts using pandas mostly.

I will explain the cleaning for each data set:

- SA2: this is the big shape file with all the government areas. 
    1. first I made all the column names lowercase otherwise sql doesn't like them apparently 
    2. Then I removed all rows that werent part of greater sydney
    2. Then I dropped the columns that we wont be using ie the Australian states and Capital city ares. we only want local governement areas
    3. A bunch of the entries had no geometry, like PO boxes and stuff I think. Anyway it was tripping up the code so I removed them. Later i will get a list of these weird entries for the report
    4. All of the stuff in the database was being stored as 'object' so I converted them all (except the geometry) to nice data types ie int and string 
    5. Removed the messy '16' that was at the end of all the column names to make them neater
    6. converted the polygon geometry to a version that postGIS can use. This was in the WK9 tutorial

- Neighbourhood: this one is much smaller, much easier to deal with.
    1. Summed all the columns of young people into one column where young people is 0 - 19
    2. Removed a column that just had the row index
    2. Removed unnecessary business types based oin the assignment specs
    3. removed punctuation from columns that are meant ot be numbers
    4. cast all the values that are 'objects' to nicer data types
    5. set empty cells as NaN
    6. remove the rows whos neighbourhoods are not in greater sydney
    
- catchments

- break and Enter

- Greenhouse gas emissions

- walking counts

- walking count sites

