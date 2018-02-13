import csv
import os
import sqlite3
import textwrap
import json

import NLP

connection = sqlite3.connect('./Newspaper_Records.db')
cursor = connection.cursor()
# connection = sqlite3.connect('C:/Users/mike/Sources/Guyana_News/Newspaper_Records.db')
# cursor = connection.cursor()

with open('./locations.json', 'r') as infile:
    locations = json.load(infile)

dictionaries = {}
for file in os.listdir('./dictionaries'):
    with open('./dictionaries/' + file, 'r') as infile:
        dictionaries[file[:-4]] = infile.read().splitlines()


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
    # url, fulltext, publish_date = cursor.execute("SELECT url, fulltext, publish_date FROM stabroek ORDER BY RANDOM() LIMIT 1").fetchone()
    results = cursor.execute("SELECT url, fulltext, publish_date FROM stabroek "
                             "WHERE publish_date='2016-08-11' "
                             "AND url NOT LIKE '%sports%'"
                             "AND url NOT LIKE '%world%'").fetchall()

    print(len(results))
    for url, fulltext, publish_date in results:
        print()
        print(url)
        # print(publish_date)
        # print('\n'.join(textwrap.wrap(fulltext, 80, break_long_words=False)))
        # print(NLP.nltk_ner(fulltext))

        locations = []
        crime_classes = []
        for token in fulltext.lower().split(" "):
            if token in locations:
                locations.append(token)

            for key in dictionaries:
                if token in dictionaries[key]:
                    crime_classes.append(key)

        print("LOCATIONS: " + str(locations))
        print("CRIME_CLASSES: " + str(crime_classes))

get_analysis()
