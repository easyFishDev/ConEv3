import psycopg2
import os
import re
import sys
import majka
import json
import time

morph_cz = majka.Majka('/home/jhu/PycharmProjects/ConEv/nlp/majka.w-lt')
morph_en = majka.Majka('/home/jhu/PycharmProjects/ConEv/nlp/w-lt.en.fsa')
morph_de = majka.Majka('/home/jhu/PycharmProjects/ConEv/nlp/w-lt.ger.fsa')
# https://nlp.fi.muni.cz/czech-morphology-analyser/


db_connection = psycopg2.connect("dbname=ConEv user=postgres password=forward host=127.0.0.1")
db = db_connection.cursor()


def find_word_attrs(word, language):

#-----------------------------------------------------------------------------------------------CZ
    morph_cz.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
    morph_cz.flags |= majka.DISALLOW_LOWERCASE  # do not enable to find lowercase variants
    morph_cz.flags |= majka.IGNORE_CASE  # ignore the word case whatsoever
    morph_cz.flags = 0  # unset all flags

    morph_cz.tags = False  # return just the lemma, do not process the tags
    morph_cz.tags = True  # turn tag processing back on (default)

    morph_cz.compact_tag = True  # return tag in compact form (as returned by Majka)
    morph_cz.compact_tag = False  # do not return compact tag (default)

    morph_cz.first_only = True  # return only the first entry
    morph_cz.first_only = False  # return all entries (default)

#-----------------------------------------------------------------------------------------------EN
    morph_en.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
    morph_en.flags |= majka.DISALLOW_LOWERCASE  # do not enable to find lowercase variants
    morph_en.flags |= majka.IGNORE_CASE  # ignore the word case whatsoever
    morph_en.flags = 0  # unset all flags

    morph_en.tags = False  # return just the lemma, do not process the tags
    morph_en.tags = True  # turn tag processing back on (default)

    morph_en.compact_tag = True  # return tag in compact form (as returned by Majka)
    morph_cz.compact_tag = False  # do not return compact tag (default)

    morph_en.first_only = True  # return only the first entry
    morph_en.first_only = False  # return all entries (default)

#-----------------------------------------------------------------------------------------------DE
    morph_de.flags |= majka.ADD_DIACRITICS  # find word forms with diacritics
    morph_de.flags |= majka.DISALLOW_LOWERCASE  # do not enable to find lowercase variants
    morph_de.flags |= majka.IGNORE_CASE  # ignore the word case whatsoever
    morph_de.flags = 0  # unset all flags

    morph_de.tags = False  # return just the lemma, do not process the tags
    morph_de.tags = True  # turn tag processing back on (default)

    morph_de.compact_tag = True  # return tag in compact form (as returned by Majka)
    morph_cz.compact_tag = False  # do not return compact tag (default)

    morph_de.first_only = True  # return only the first entry
    morph_de.first_only = False  # return all entries (default)


    if language == 'CZ':
        a = morph_cz.find(word)
    if language == 'EN':
        a = morph_en.find(word)
    if language == 'DE':
        a = morph_de.find(word)


    pos=""
    gender=""
    animate=""
    singular=""
    negation=""
    plural=""
    degree=""

    try:
        if language=="CZ":
            pos = (a[0]['tags']['pos'])
        if language=="EN" or language=="DE":
            pos = (a[0]['tags']['other'])
    except:
        pass

    try:
        gender = (a[0]['tags']['gender'])
    except:
        pass

    try:
        animate = (a[0]['tags']['animate'])
    except:
        pass

    try:
        singular = (a[0]['tags']['singular'])
    except:
        pass
    try:
        negation = (a[0]['tags']['negation'])
    except:
        pass
    try:
        plural = (a[0]['tags']['plural'])
    except:
        pass
    try:
        degree = (a[0]['tags']['degree'])
    except:
        pass

    return pos, gender, animate, singular, negation, plural, degree

def build_digital_article(record_id, dictionary_ID):
    db.execute("INSERT INTO magazine_words (magazine_record_id, dictionary_id) VALUES (%s,%s)",
               (record_id, dictionary_ID))
    db_connection.commit()



def log(action, description, severity, filename):
    # to_do - zapamatovat si cas posledniho behu, dat now()-ta hodnota a vyjde jak dlouho trvala posledni operace
    db.execute("INSERT INTO log_table (action, description, severity, script) VALUES (%s,%s,%s,%s)",
               (action, description, severity, filename))
    db_connection.commit()
    print(action + "----" + description + "----severity " + str(severity) + "")

def log_start(filename):
    log("start", "instance " + filename + " started", 5, filename)
    update_semaphore(filename, "running")

def log_end(filename, time_elapsed):
    log('end', "instance " + filename + " finished in "+str(time_elapsed)+" seconds.", 5, filename)
    update_semaphore(filename, "idle")

def do_morph(word, language):

    if language == 'CZ':
        morph_cz.tags = False
        morph_cz.first_only = True
        morph_cz.negative = "ne"
        lemm = morph_cz.find(word)

    if language == 'EN':
        morph_en.tags = False
        morph_en.first_only = True
        morph_en.negative = "no"
        lemm = morph_en.find(word)

    if language == 'DE':
        morph_en.tags = False
        morph_en.first_only = True
        morph_en.negative = "nein"
        lemm = morph_de.find(word)



    if len(lemm)==0:
        return("")
    else:
        return(lemm[0]['lemma'])

def delete_tables():
    log("delete", "table deletions started", 0, "tbd")
    db.execute("DELETE from words")
    db.execute("DELETE from stems")
    db.execute("DELETE from lemms")
    db.execute("DELETE from magazine_words")
    db.execute("DELETE from dictionary")

    db_connection.commit()
    log("delete", "table deletions finished", 0, "tbd")

def clear_data():
    log("clearing", "table clearing started", 0, "tbd")
    db.execute("UPDATE magazine SET status='new' where status='lemm'")
    db.execute("UPDATE words SET count=0")
    db.execute("UPDATE lemms SET count=0")
    db.execute("UPDATE stems SET count=0")
    db_connection.commit()
    log("clearing", "table clearing finished", 0, "tbd")

def what_is_my_priority(script_name):
    db.execute("SELECT priority from semaphore WHERE script_name = '"+script_name+"'")
    results = db.fetchall()
#todo osetrit pripad, kdy se nic nenalezne
    return results[0][0]

def update_semaphore(script_name, status):
    db.execute("UPDATE semaphore SET status=%s where script_name=%s", (status, script_name))
    db_connection.commit()


def is_more_prio_process_running_private(priority, script_name):

    db.execute("SELECT * from semaphore WHERE priority <= "+str(priority)+" AND status = 'running'")
    results = db.fetchall()
    print (results)
    if len(results)>1: #since current proces is always included, because of SQL Where condition <=, we are evaluating more than one
        log("sleep", "going to sleep, another process is running", 5, script_name)
        time.sleep(5)
        log("sleep", "woken up, continue with work", 5, script_name)
        return True
    else:
        return False


def is_more_prio_process_running(script_name, priority):
    finish = True
    i=0
    while (finish==True):
        finish=is_more_prio_process_running_private(priority, script_name)
        i=i+1
        if i==10:
            log("exit", "another process with higher prio is running for long time", 9, script_name)
            log_end(script_name,0)
            #update_semaphore(script_name, "idle")
            exit()
        print(i)





def update_progress(progress, message):
    # update_progress() : Displays or updates a console progress bar
    ## Accepts a float between 0 and 1. Any int will be converted to a float.
    ## A value under 0 represents a 'halt'.
    ## A value at 1 or bigger represents 100%

    barLength = 60  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength * progress))
    # format("{:.2%}".progress*100
    progr = ("{:.2f}".format(progress * 100))
    text = "\rPercent: [{0}] {1}% {2}".format("#" * block + "-" * (barLength - block), progr, status)
    sys.stdout.write(text+message)
    sys.stdout.flush()

def cz_stem(word, aggressive=False):
    #https: // github.com / UFAL - DSG / alex / blob / master / alex / utils / czech_stemmer.py
    if not re.match("^\\w+$", word):
        return word
    if not word.islower() and not word.istitle() and not word.isupper():
        #print("warning: skipping word with mixed case: {}".format(word),file=sys.stderr)
        return word
    s = word.lower() # all our pattern matching is done in lowercase
    s = _remove_case(s)
    s = _remove_possessives(s)
    if aggressive:
        s = _remove_comparative(s)
        s = _remove_diminutive(s)
        s = _remove_augmentative(s)
        s = _remove_derivational(s)
    if word.isupper():
        return s.upper()
    if word.istitle():
        return s.title()
    return s

def _remove_case(word):
    if len(word) > 7 and word.endswith("atech"):
        return word[:-5]
    if len(word) > 6:
        if word.endswith("ětem"):
            return _palatalise(word[:-3])
        if word.endswith("atům"):
            return word[:-4]
    if len(word) > 5:
        if word[-3:] in {"ech", "ich", "ích", "ého", "ěmi", "emi", "ému",
                         "ete", "eti", "iho", "ího", "ími", "imu"}:
            return _palatalise(word[:-2])
        if word[-3:] in {"ách", "ata", "aty", "ých", "ama", "ami",
                         "ové", "ovi", "ými"}:
            return word[:-3]
    if len(word) > 4:
        if word.endswith("em"):
            return _palatalise(word[:-1])
        if word[-2:] in {"es", "ém", "ím"}:
            return _palatalise(word[:-2])
        if word[-2:] in {"ům", "at", "ám", "os", "us", "ým", "mi", "ou"}:
            return word[:-2]
    if len(word) > 3:
        if word[-1] in "eiíě":
            return _palatalise(word)
        if word[-1] in "uyůaoáéý":
            return word[:-1]
    return word

def _remove_possessives(word):
    if len(word) > 5:
        if word[-2:] in {"ov", "ův"}:
            return word[:-2]
        if word.endswith("in"):
            return _palatalise(word[:-1])
    return word

def _remove_comparative(word):
    if len(word) > 5:
        if word[-3:] in {"ejš", "ějš"}:
            return _palatalise(word[:-2])
    return word

def _remove_diminutive(word):
    if len(word) > 7 and word.endswith("oušek"):
        return word[:-5]
    if len(word) > 6:
        if word[-4:] in {"eček", "éček", "iček", "íček", "enek", "ének",
                         "inek", "ínek"}:
            return _palatalise(word[:-3])
        if word[-4:] in {"áček", "aček", "oček", "uček", "anek", "onek",
                         "unek", "ánek"}:
            return _palatalise(word[:-4])
    if len(word) > 5:
        if word[-3:] in {"ečk", "éčk", "ičk", "íčk", "enk", "énk",
                         "ink", "ínk"}:
            return _palatalise(word[:-3])
        if word[-3:] in {"áčk", "ačk", "očk", "učk", "ank", "onk",
                         "unk", "átk", "ánk", "ušk"}:
            return word[:-3]
    if len(word) > 4:
        if word[-2:] in {"ek", "ék", "ík", "ik"}:
            return _palatalise(word[:-1])
        if word[-2:] in {"ák", "ak", "ok", "uk"}:
            return word[:-1]
    if len(word) > 3 and word[-1] == "k":
        return word[:-1]
    return word

def _remove_augmentative(word):
    if len(word) > 6 and word.endswith("ajzn"):
        return word[:-4]
    if len(word) > 5 and word[-3:] in {"izn", "isk"}:
        return _palatalise(word[:-2])
    if len(word) > 4 and word.endswith("ák"):
        return word[:-2]
    return word

def _remove_derivational(word):
    if len(word) > 8 and word.endswith("obinec"):
        return word[:-6]
    if len(word) > 7:
        if word.endswith("ionář"):
            return _palatalise(word[:-4])
        if word[-5:] in {"ovisk", "ovstv", "ovišt", "ovník"}:
            return word[:-5]
    if len(word) > 6:
        if word[-4:] in {"ásek", "loun", "nost", "teln", "ovec", "ovík",
                         "ovtv", "ovin", "štin"}:
            return word[:-4]
        if word[-4:] in {"enic", "inec", "itel"}:
            return _palatalise(word[:-3])
    if len(word) > 5:
        if word.endswith("árn"):
            return word[:-3]
        if word[-3:] in {"ěnk", "ián", "ist", "isk", "išt", "itb", "írn"}:
            return _palatalise(word[:-2])
        if word[-3:] in {"och", "ost", "ovn", "oun", "out", "ouš",
                         "ušk", "kyn", "čan", "kář", "néř", "ník",
                         "ctv", "stv"}:
            return word[:-3]
    if len(word) > 4:
        if word[-2:] in {"áč", "ač", "án", "an", "ář", "as"}:
            return word[:-2]
        if word[-2:] in {"ec", "en", "ěn", "éř", "íř", "ic", "in", "ín",
                         "it", "iv"}:
            return _palatalise(word[:-1])
        if word[-2:] in {"ob", "ot", "ov", "oň", "ul", "yn", "čk", "čn",
                         "dl", "nk", "tv", "tk", "vk"}:
            return word[:-2]
    if len(word) > 3 and word[-1] in "cčklnt":
        return word[:-1]
    return word

def _palatalise(word):
    if word[-2:] in {"ci", "ce", "či", "če"}:
        return word[:-2] + "k"

    if word[-2:] in {"zi", "ze", "ži", "že"}:
        return word[:-2] + "h"

    if word[-3:] in {"čtě", "čti", "čtí"}:
        return word[:-3] + "ck"

    if word[-3:] in {"ště", "šti", "ští"}:
        return word[:-3] + "sk"
    return word[:-1]