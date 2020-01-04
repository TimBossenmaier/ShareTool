import DB_Connection
import psycopg2
from os import listdir

"""
    This python script initializes the db in the required structure.
    Has to be executed only once.
"""

#initialize the connection to the specified data base (empty so far)
connection_db = DB_Connection.connect_to_db()

cursor_db = connection_db.cursor()

# create a list of all sql files required for the initialization
list_sql_files = listdir('./data/sql/')

# execute each sql file
for eachFile in list_sql_files:

    try:
        curr_sql_file = open('./data/sql/' + eachFile,'r')
        cursor_db.execute(curr_sql_file.read())
        curr_sql_file.close()
        connection_db.commit()
        print(eachFile[8:-4] + ' created successfully in database ' + DB_Connection.get_db_name() + '.')

    except (Exception, psycopg2.Error) as error:
        print("Error while creating " + eachFile[8:-4], error, sep= "\n")

