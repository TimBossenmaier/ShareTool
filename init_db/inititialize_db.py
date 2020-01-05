import DB_Communication
import psycopg2
from os import listdir
import csv
import pandas as pd

"""
    This python script initializes the db in the required structure.
    Has to be executed only once.
"""

#initialize the connection to the specified data base (empty so far)
connection_db = DB_Communication.connect_to_db()

cursor_db = connection_db.cursor()

# create a list of all sql files required for the initialization
list_sql_files = listdir('./data/sql/init/')

# execute each sql file
for each_file in list_sql_files:

    try:
        curr_sql_file = open('./data/sql/init/' + each_file, 'r')
        cursor_db.execute(curr_sql_file.read())
        curr_sql_file.close()
        connection_db.commit()
        print(each_file[8:-4] + ' created successfully in database ' + DB_Communication.get_db_name() + '.')

    except (Exception, psycopg2.Error) as error:
        print("Error while creating " + each_file[8:-4], error, sep="\n")



list_filenames = listdir('./data/')
list_filenames_csv = [filename for filename in list_filenames if filename.endswith('csv')]

for each_csv_file in list_filenames_csv:

    try:
        # open each csv file and encode it accordingly (due to umlauts
        with open('./data/' + each_csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter=';')

            # skip header
            next(csv_reader)

            # craete data frame representation of each file
            df = pd.read_csv('./data/' + each_csv_file, sep=';')
            df.columns = DB_Communication.get_column_names_from_db_table(cursor_db, each_csv_file[:-4])

            for each_row in csv_reader:

                # insert each row into the db
                cursor_db.execute(
                    DB_Communication.create_insert_into_statement_for_df(df, each_csv_file[:-4]),
                    each_row
                )

             #commit the sql statements
            connection_db.commit()

        print('Data from ' + each_csv_file + ' inserted successfully in table ' + each_csv_file[:-4] + '.')

    except (Exception, psycopg2.Error) as error:
        print("Error while inserting values of " + each_csv_file, error, sep="\n")