import csv
import os
import sqlite3
import textwrap

import NLP

connection = sqlite3.connect('./Newspaper_Records.db')
cursor = connection.cursor()
# connection = sqlite3.connect('C:/Users/mike/Sources/Guyana_News/Newspaper_Records.db')
# cursor = connection.cursor()


def write_to_csv(quantity=None):
    # Store database records to csv
    if os.path.exists('./Summary_generated.csv'):
        os.remove('./Summary_generated.csv')

    with open('./Summary_generated.csv', 'w', newline='') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow([entry[0] for entry in cursor.execute("SELECT * FROM stabroek WHERE 1=2").description])

        limit = ""
        if quantity is not None:
            limit = " LIMIT " + str(quantity)

        for entries in cursor.execute("SELECT * FROM articles" + limit).fetchall():
            writer.writerow(entries)


def get_analysis():
    url, fulltext = cursor.execute("SELECT url, fulltext FROM stabroek ORDER BY RANDOM() LIMIT 1").fetchone()

    print()
    print(url)
    print('\n'.join(textwrap.wrap(fulltext, 80, break_long_words=False)))
    NLP.nltk_ner(fulltext)

get_analysis()
