import csv
import os
import sqlite3

from Record import Record

connection = sqlite3.connect('./Newspaper_Records.db')
cursor = connection.cursor()


def write_to_csv(quantity=None):
    # Store database records to csv
    if os.path.exists('./Summary_generated.csv'):
        os.remove('./Summary_generated.csv')

    with open('./Summary_generated.csv', 'w', newline='') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(Record.header_csv())

        limit = ""
        if quantity is not None:
            limit = " LIMIT " + str(quantity)

        for url in cursor.execute("SELECT Link_to_story FROM articles" + limit).fetchall():
            writer.writerow(Record(url[0]).get_csv_elements())
