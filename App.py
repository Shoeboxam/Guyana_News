from Record import Record
from stabroek import write_to_database
import NLP

import csv
import os
import sqlite3

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

        for url in cursor.execute("SELECT url FROM articles" + limit).fetchall():
            writer.writerow(Record(url[0]).get_csv_elements())


def update_records(func, quantity=None):
    """Pass each record in the database through a function and store it"""
    limit = ""
    if quantity is not None:
        limit = " LIMIT " + str(quantity)

    for url in cursor.execute("SELECT url FROM articles" + limit).fetchall():
        func(Record(url[0])).store_to_database()

# Write ten days worth of articles to the database
# write_to_database(10)

update_records(NLP.nltk_ner)

