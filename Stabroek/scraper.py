import requests
import sys
import time

from multiprocessing import Queue, Process, cpu_count

import bs4
from newspaper import Article
from newspaper.article import ArticleException

import sqlite3
connection = sqlite3.connect('../Newspaper_Records.db')
cursor = connection.cursor()

# Create Stabroek days table
cursor.execute('CREATE TABLE IF NOT EXISTS stabroek_days (day TEXT)')

# Create stabroek table
cursor.execute('CREATE TABLE IF NOT EXISTS stabroek (' +
               'url TEXT, ' +
               'fulltext TEXT, ' +
               'title TEXT, ' +
               'authors TEXT, ' +
               'top_image TEXT, ' +
               'images TEXT, ' +
               'movies TEXT)')

cursor.execute('CREATE TABLE IF NOT EXISTS stabroek_nlp (' +
               'url TEXT, ' +
               'summary TEXT, ' +
               'keywords TEXT)')

archive_url = 'http://stabroeknews.com/archive/'


# Returns the urls of every day in the archive
def get_day_urls(memoize=True):
    soup = bs4.BeautifulSoup(requests.get(archive_url).content, "lxml")

    day_urls = []

    # Loop through the elements of the dropdown to build a list of article pages
    for date_option in soup.find("select", {"name": '\\"archive-dropdown\\"'}):
        # Filter out the placeholder option

        if type(date_option) is bs4.element.NavigableString:
            continue

        day_url = date_option['value']

        if day_url == '\\"\\"':
            continue

        # Filter out days that have already been processed
        if memoize and len(cursor.execute('SELECT * FROM stabroek_days WHERE day = ? LIMIT 1', (day_url,)).fetchall()):
            continue

        day_urls.append(day_url)

    return day_urls


# Returns the urls of every article in a day
def get_article_urls(url, page=1, memoize=True):
    soup = bs4.BeautifulSoup(requests.get(url + '/page/' + str(page)).content, "lxml")
    article_urls = []

    # Retrieve list of all articles
    article_list = soup.findAll("li", {"class": "post"})

    # Loop through each article element and grab the url
    for article in article_list:
        article_url = article.h3.a['href']

        if not memoize or not len(cursor.execute('SELECT * FROM stabroek WHERE url = ? LIMIT 1', (article_url,)).fetchall()):
            article_urls.append(article_url)

    if article_list:
        article_urls.extend(get_article_urls(url, page=page+1, memoize=True))

    return article_urls


def scrape(limit=None):

    # Store results from downloading threads via a single transaction thread
    # This fixes issues with concurrent database writes / timeouts
    write_queue = Queue()
    write_process = Process(target=transaction_process, args=(write_queue,), name="transaction_manager")
    write_process.start()

    # Create article list
    for day_idx, day_url in enumerate(get_day_urls()):

        article_queue = Queue()
        article_urls = get_article_urls(day_url)

        for url in article_urls:
            article_queue.put(url)

        pool = [Process(target=download_process, args=(write_queue, article_queue,), name=str(proc))
                for proc in range(cpu_count())]

        for proc in pool:
            proc.start()

        print()
        force_quit = False
        while any([proc.is_alive() for proc in pool]) and not force_quit:
            # Increment status
            sys.stdout.write("\r\x1b[KCollecting: " + day_url + " " +
                             str(len(article_urls) - article_queue.qsize()) + '/' + str(len(article_urls)))
            sys.stdout.flush()

            time.sleep(0.5)

            # Sometimes threads get hung on an eternal process, IE waiting on a download
            if article_queue.empty():
                time.sleep(3)
                # Increment status
                sys.stdout.write("\r\x1b[KCollecting: " + day_url + " " +
                                 str(len(article_urls) - article_queue.qsize()) + '/' + str(len(article_urls)))
                sys.stdout.flush()

                if any([proc.is_alive() for proc in pool]):
                    time.sleep(5)
                    print(" (killed hung thread)", end="")
                    force_quit = True

        for proc in pool:
            proc.terminate()

        # Prevent re-processing the day on reload
        write_queue.put(("INSERT INTO stabroek_days (day) VALUES (?)", (day_url,)))

        # Limit number of days to download
        if limit is not None and day_idx + 1 is limit:
            break

    while not write_queue.empty():
        print("Waiting for database writes to finish")
        time.sleep(1)

    write_process.terminate()


def download_process(write_queue, item_queue):
    while not item_queue.empty():
        article_url = item_queue.get()

        success = False
        while not success:
            try:
                parse_article(write_queue, article_url)
                success = True
            except (ArticleException, sqlite3.OperationalError):
                print("Redownloading article: " + article_url)

            # Be nice to their servers
            time.sleep(1)


def transaction_process(write_queue):
    while True:
        success = False

        while not success:
            try:
                cursor.execute(*write_queue.get())
                success = True
            except sqlite3.OperationalError:
                print("\nDatabase locked, re-executing.")
            except Exception as error:
                print("\nCaught faulty database write: " + str(error))

        connection.commit()


def parse_article(write_queue, article_url):
    article = Article(article_url)
    article.download()
    article.parse()
    article.nlp()

    record = (article_url,
              article.text,
              article.title,
              ', '.join(article.authors),
              article.top_image,
              ', '.join(article.images),
              ', '.join(article.movies))

    record_nlp = (article_url,
                  article.summary,
                  ', '.join(article.keywords))

    # IF exists: update, ELSE: insert
    if cursor.execute('SELECT * FROM stabroek WHERE url = ? LIMIT 1', (article_url,)).fetchall():
        sql = "UPDATE stabroek SET " \
              "url=?, " \
              "fulltext=?, " \
              "title=?, " \
              "authors=?, " \
              "top_image=?, " \
              "images=?, " \
              "movies=?, WHERE url = ?"

        sql_nlp = "UPDATE stabroek_nlp SET " \
                  "url=?, " \
                  "summary=?, " \
                  "keywords=?, WHERE url = ?"
    else:
        sql = "INSERT INTO stabroek VALUES (" + "?, " * 6 + "?)"
        sql_nlp = "INSERT INTO stabroek_nlp VALUES (?, ?, ?)"

    write_queue.put((sql, record))
    write_queue.put((sql_nlp, record_nlp))


if __name__ == '__main__':
    scrape()
    print(len(cursor.execute("SELECT * FROM stabroek").fetchall()))
