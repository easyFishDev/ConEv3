#!/usr/bin/python3
import nltk
import numpy
import psycopg2
import time, sys
import re
import os
import sys
from ConEv_utils_v01 import log, log_start, log_end, do_morph, delete_tables, clear_data, update_progress, cz_stem, what_is_my_priority, is_more_prio_process_running, find_word_attrs

# http://ufal.mff.cuni.cz/~zabokrtsky/courses/npfl092/html/nlp-frameworks.html


# with open("genesis.txt", "r") as f:
#   genesis = f.read()

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

#todo put this into config file
db_connection = psycopg2.connect("dbname=ConEv user=postgres password=forward host=127.0.0.1")
db = db_connection.cursor()

import time, sys

msg = ""

def check_dictionary(word, stem, lemm):
    pos, gender, animate, singular, negation, plural, degree = find_word_attrs(word)

    db.execute("SELECT word, stem, lemm from public.dictionary WHERE word=%s and 1=%s", (word, 1))
    results = db.fetchall()
    if not results:
        db.execute("INSERT INTO dictionary (word, stem, lemm, pos, gender, animate, singular, negation, plural, degree ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (word, stem, lemm, pos, gender, animate, singular, negation, plural, degree))
        db_connection.commit()
    db.execute("SELECT ID from public.dictionary WHERE word=%s and 1=%s", (word, 1))
    results = db.fetchall()
    return results[0]



def check_word(word, date_inserted, stem, lemm):
    #print(cz_stem("Koronavirusy", aggressive))
    dict_ID = check_dictionary(word, stem, lemm)
    db.execute('SELECT word,count,date from public.words WHERE word=%s AND date=%s', (word, date_inserted))
    results = db.fetchall()
    if not results:
        db.execute('INSERT INTO words (word, date, stem, lemm, dictionary_id) VALUES (%s,%s,%s,%s,%s)', (word, date_inserted, stem, lemm, dict_ID))
        db_connection.commit()
    else:

        current_count = (results[0][1])
        msg = (word + " current count " + str(current_count))
        new_count = current_count + 1
        db.execute("UPDATE words SET count=%s, dictionary_id=%s WHERE word=%s AND date=%s ", (new_count, dict_ID, word, date_inserted))
        db_connection.commit()

    return dict_ID

def check_lemm(lemm, date_inserted, dict_ID):
    current_count=0
    db.execute('SELECT lemm,count,date from public.lemms WHERE lemm=%s AND date=%s', (lemm, date_inserted))
    results = db.fetchall()
    if not results:
        db.execute("INSERT INTO lemms (lemm, date, dictionary_id) VALUES (%s,%s,%s)", (lemm, date_inserted, dict_ID ))
        db_connection.commit()
    else:
        current_count = (results[0][1])
        msg = (lemm + " current count " + str(current_count))
        new_count = current_count + 1
        db.execute("UPDATE lemms SET count=%s, dictionary_id=%s WHERE lemm=%s AND date=%s and 1=%s ", (new_count, dict_ID, lemm, date_inserted,1))
        db_connection.commit()



def check_stem(stem, date_inserted):
    current_count=0
    db.execute('SELECT stem,count,date from public.stems WHERE stem=%s AND date=%s', (stem, date_inserted))
    results = db.fetchall()
    if not results:
        db.execute("INSERT INTO stems (stem, date) VALUES (%s,%s)", (stem, date_inserted, ))
        db_connection.commit()
    else:

        current_count = (results[0][1])
        msg = (stem + " current count " + str(current_count))
        new_count = current_count + 1
        db.execute("UPDATE stems SET count=%s WHERE stem=%s AND date=%s ", (new_count, stem, date_inserted))
        db_connection.commit()

def extract_words(text, date_inserted):
    sentences = nltk.sent_tokenize(text)
    for s in sentences:
        # print(s)
        # just the first sentence
        tokens_0 = nltk.word_tokenize(s)
        for word in tokens_0:
            if len(word) > 1:
                stem = cz_stem(word, "aggressive")
                lemm = do_morph(word)
                if lemm == "": lemm = stem
                dict_id=check_word(word, date_inserted, stem, lemm)

              #  check_stem(stem, date_inserted)
                check_lemm(lemm, date_inserted, dict_id)
    return len(tokens_0)
        # tagged_0 = nltk.pos_tag(tokens_0)

start = time.time()
log_start(os.path.basename(__file__))

my_prio=what_is_my_priority(os.path.basename(__file__))

canIrun = is_more_prio_process_running(os.path.basename(__file__),my_prio)

#print (canIrun)

#delete_tables()


clear_data()
#todo create stand/alone clearing script which will run daily/weekly

db.execute("SELECT title, description,date_inserted from magazine where status='new'")
results = db.fetchall()
recordNr = 0
log("stemming","word stemming started.",0, os.path.basename(__file__))
words_processed=0
for r in results:
    # print(len(results))
    # print(r)
    words_extracted = extract_words(r[0] + " " + str(r[1]), r[2].date())
    recordNr += 1
    stop=time.time()
    words_processed = words_extracted + words_processed
    update_progress(recordNr / len(results)," speed: "+str(round(words_processed/(stop-start),2))+" words/second")

log("stemming", "processed "+str(len(results))+" magazine records and "+str(words_processed)+" words.",3, os.path.basename(__file__))
stop = time.time()
log("stemming","word stemming finished - speed: "+str(words_processed/(stop-start))+" words/second",3, os.path.basename(__file__))
# change status
log("status","changing article status form new to lemm - START",2, os.path.basename(__file__))      #todo transfer it to universal function
db.execute("UPDATE magazine SET status='lemm' where status='new'")
db_connection.commit()
log("status","changing article status form new to lemm - END",2, os.path.basename(__file__))

log_end(os.path.basename(__file__),stop-start)
