from Record import Record
from websites.stabroek import get_article_urls, get_day_urls

import csv
import os
import sqlite3

num_records = 10

connection = sqlite3.connect('Newspaper_Records.db')
cursor = connection.cursor()

# Create articles table
labels = []
for label in Record.header_db():
    labels.append(label + ' TEXT')
cursor.execute('CREATE TABLE IF NOT EXISTS articles ' + str(tuple(Record.header_db())))

# Create article list
for idx, day_url in enumerate(get_day_urls()):
    print("Processing: " + day_url)
    for article_url in get_article_urls(day_url):
        Record(article_url).store_to_database()

    # Prevent re-processing the day on reload
    cursor.execute("INSERT INTO stabroek_days (day) VALUES (?)", (day_url,))
    if idx is 10:
        break
#
# # Store database records to csv
# if os.path.exists('./test_scraped_data.csv'):
#     os.remove('./test_scraped_data.csv')
#
# with open('./test_scraped_data.csv', 'w', newline='') as outputfile:
#     writer = csv.writer(outputfile)
#     writer.writerow(Record.header_csv())
#
#     for record in cursor.execute('SELECT * FROM articles'):
#         writer.writerow(record.get_csv_elements())

connection.commit()
