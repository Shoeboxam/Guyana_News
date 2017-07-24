import csv
import os

from Record import Record

num_records = 100

records = []
with open('./data/article_urls.txt', 'r') as urlfile:
    for idx in range(num_records):
        print("Downloading article " + str(idx))
        records.append(Record(urlfile.readline(), nlp=True))

os.remove('./test_scraped_data.csv')

with open('./test_scraped_data.csv', 'w', newline='') as outputfile:
    writer = csv.writer(outputfile)
    writer.writerow(Record.header())

    for record in records:
        writer.writerow(record.elements())
