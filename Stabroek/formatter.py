import sqlite3
import pandas

keyfile = pandas.read_excel('../Summary_key.xlsx')


connection = sqlite3.connect('../Newspaper_Records.db')
cursor = connection.cursor()

print("Started matching")
matches = 0

for url in keyfile['link_to_story']:

  if type(url) is float:
    print(url)

  archive_url = str(url).replace("/archives/", "/news/stories/").replace("http://", "https://")
  if cursor.execute("SELECT url FROM stabroek WHERE url=?", [archive_url]).fetchall():
    matches += 1
  if matches % 25 == 0: print(matches)

print(matches)

# Create stabroek table
# cursor.execute('CREATE TABLE IF NOT EXISTS stabroek_formatted (' +
#                'url TEXT, ' +
#                'fulltext TEXT, ' +
#                'title TEXT, ' +
#                'authors TEXT, ' +
#                'top_image TEXT, ' +
#                'images TEXT, ' +
#                'movies TEXT)')


# if __name__ == '__main__':
#     print(len(cursor.execute("SELECT * FROM stabroek").fetchall()))
