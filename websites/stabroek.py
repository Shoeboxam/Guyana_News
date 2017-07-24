from lxml import html
import requests

import sqlite3

connection = sqlite3.connect('Newspaper_Records.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS stabroek_days (day TEXT)')

archive_url = 'https://www.stabroeknews.com/archive/'


# Returns the urls of every day in the archive
def get_day_urls(url, memoize=True):
    page_archive = requests.get(url)
    tree = html.fromstring(page_archive.content)

    day_urls = []

    # Select the dropdown element
    archive_dropdown_options = tree.xpath('//select[@name=\'\\"archive-dropdown\\"\']/option')

    # Loop through the elements of the dropdown to build a list of article pages
    for day_option in archive_dropdown_options:
        url = day_option.get('value')

        # Filter out the placeholder option
        if url == '\\"\\"':
            continue

        record = cursor.execute('SELECT 1 FROM stabroek_days WHERE key = ' + url)
        if cursor.execute('SELECT 1 FROM stabroek_days WHERE key = ' + url):
            record.

        day_urls.append(url)

    return day_urls


# Returns the urls of every article in a day
def get_article_urls(url, memoize=True):
    page_articles = requests.get(url)
    tree = html.fromstring(page_articles.content)

    # Select all article elements
    day_articles = tree.xpath('//article/div/h1/a')
    article_urls = []

    # Loop through each article element and grab the url
    for article in day_articles:
        article_urls.append(article.get('href'))

    return article_urls

# Create the day list
day_urls = get_day_urls(archive_url)
# Save the list to a file

urlfile = open('./data/day_urls.txt', 'rw')
for day_url in day_urls:
    urlfile.write("%s\n" % day_url)

# Create the article list
article_urls = []
for idx, day_url in enumerate(day_urls):
    print('(' + str(idx) + '/' + str(len(day_urls)) + ')')
    article_urls.extend(get_article_urls(day_url))

# Save the list to a file
urlfile = open('./data/article_urls.txt', 'w')
for article_url in article_urls:
    urlfile.write("%s\n" % article_url)

urlfile.close()
