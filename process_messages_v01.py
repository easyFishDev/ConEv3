#!/usr/bin/python3
from typing import Any, Union

import feedparser
import psycopg2
import mysql.connector
import configparser
from ConEv_utils_v01 import log, log_start, log_end, what_is_my_priority, is_more_prio_process_running
import get_content_v01
import time
import os

#todo make configuration working!!!
config = configparser.ConfigParser()
config.read('config.ini')

# https://fedoramagazine.org/never-miss-magazines-article-build-rss-notification-system/


# db_connection = sqlite3.connect('/var/tmp/magazine_rss.sqlite')
# print(config['postgreSQL']['db'])
# print(config['postgreSQL']['user'])
# print(config['postgreSQL']['pass'])
# print(config['postgreSQL']['host'])

# db_connection = psycopg2.connect("dbname=config['postgreSQL']['db'] user=config['postgreSQL']['user'] password=config['postgreSQL']['pass'] host='127.0.0.1'")
db_connection = psycopg2.connect("dbname=ConEv user=postgres password=forward host=127.0.0.1")
#db_connection = mysql.connector.connect(user='root', password='global99-News',
#                              host='127.0.0.1',
#                              database='ConEv')
# host=config['postgreSQL']['host']")

db = db_connection.cursor()
#db.execute('CREATE TABLE IF NOT EXISTS magazine (title TEXT, date TEXT, url TEXT)')


def article_is_not_db(article_title, article_date):
    """ Check if a given pair of article title and date
    is in the database.
    Args:
        article_title (str): The title of an article
        article_date  (str): The publication date of an article
    Return:
        True if the article is not in the database
        False if the article is already present in the database
    """
    db.execute("SELECT * from magazine WHERE title=%s AND date=%s", (article_title, article_date))

    if not db.fetchall():
        return True
    else:
        return False


def add_article_to_db(article_title, article_date, article_url, source_name, article_text, article_description, language):
    """ Add a new article title and date to the database
    Args:
        article_title (str): The title of an article
        article_date (str): The publication date of an article
        :param article_text:
    """
    db.execute("INSERT INTO magazine (title, date, url, source, article, description, language) VALUES (%s,%s,%s,%s,%s,%s,%s)",
               (article_title, article_date, article_url, source_name, article_text, article_description, language))

    db_connection.commit()


def read_article_feed(source, source_name, language):
    """ Get articles from RSS feed """
    try:
        feed = feedparser.parse(source)

        cnt = 0
        for article in feed['entries']:
            if article_is_not_db(article['title'], article['published']):
                # article_text = get_content_v01.fetch_article(article['link'])
                article_text = ""
                # print(article_text)
                #print(article["title"]+" "+source_name)
                #todo include language into article
                add_article_to_db(article['title'], article['published'], article['link'], source_name, article_text,
                              article['description'], language)
                cnt += 1

        # log('saving', source_name + ' has ' + str(cnt) + ' records inserted', 0)

        if len(feed['entries'])==cnt:
            sev=7
        else:
            if cnt>0:sev=1
            else: sev=0

        log('entries', source_name + ' has ' + str(len(feed['entries'])) + ' found, ' + str(cnt) + ' inserted', sev, os.path.basename(__file__))
        cnt = 0

    except Exception as e:
        log('error'+" "+repr(e), source, 9, os.path.basename(__file__))
        #print(repr(e))
        #print(str(e))


def process_RSS():
    db.execute("SELECT * from sources WHERE source_type = 'RSS' ")

    results = db.fetchall()
    for r in results:
        # log("reading", r[1] + " " + r[3], 0)
        read_article_feed(r[3], r[1], r[4])


if __name__ == '__main__':
    log_start(os.path.basename(__file__))
    #log("start", "instance "+os.path.basename(__file__)+" started", 0)
    start = time.time()

    my_prio = what_is_my_priority(os.path.basename(__file__))
    canIrun = is_more_prio_process_running(os.path.basename(__file__), my_prio)

    process_RSS()

    stop = time.time()
    elapsed = (stop - start)
    log("progress", "processed " +  ", inserted " + ", in " + str(elapsed) + " seconds",0, os.path.basename(__file__))
    log_end(os.path.basename(__file__),elapsed)
    db_connection.close()
