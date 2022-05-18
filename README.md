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
    7. cast the area_name as a string
    
- break and Enter - at this stage I am starting to re peat a lot of the cleaning stuff so I'll keep it short
    1. make all the column labels lowercase
    2. Cast density as a string
    3. change the geometry types
    4. remove redundant columns
    5. rename columns

- Catchments - ok this one was a pain in my ass
    1. comboine the 3 shapefiles into 1
    2. also remove redundant columns
    3. make lowercase
    4. cast as useful types
    5. convert all of the columns with Y and N to {1,0}
    6. cast again
    7. make polygons noice
    8. rename 1 column
    9. I realsied that school show up in more than one of the shapefiles, so some scools where in the main dataframe like 3 times. so I had to aggregate and combine the rows with the same Use_id

- Greenhouse gas emissions
    1. lower and cast as usual
    2. rename columns to be nicer
    3. 

- walking counts
    1. first we have to do a weird split thing. The moth column is originally in the format "2013 - Weekday - October" which is weird and confusing so I just extracted the moth word eg October
    2. lower coluns again
    3. then I summed the values for each hour into morning, afternoon and evening corresponding to 6am -11am, 12pm - 6pm, 7pm - 12am blocks
    4. I then dropped the old per/hour measurment columns
    5. casting and renaming finally  

- walking count sites
    1. lower and cast
    2. fix point geometry
    3. rename
    4. then ran a quick fix to remove any walking measuremnts rows from the previous table (walking counts) so that we could reference the site_id

