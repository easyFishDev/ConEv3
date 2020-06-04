import psycopg2
import ConEv_utils_v01
import os, time
import functools


#todo put this into config file
db_connection = psycopg2.connect("dbname=ConEv user=postgres password=forward host=127.0.0.1")
db = db_connection.cursor()



start = time.time()
ConEv_utils_v01.log_start(os.path.basename(__file__))

#select * from names, "dictionary" d2 where names.firstname = d2.lemm

db.execute("select dictionary.id, names.firstname, names.* from names, dictionary where names.firstname = dictionary.lemm ")
results = db.fetchall()

for r in results:
	db.execute("select id from magazine_words where dictionary_id='%s'", (r[0],))   #todo don't forget to create index!!!
	mg=db.fetchall()

	con = functools.reduce(lambda sub, ele: sub * 10 + ele, mg[0])
	con=con+1
	db.execute("select dictionary_id from magazine_words where id=%s", (str(con),))
	mgplus=db.fetchall()


	for p in mgplus:
		#print("magazine_id-----"+str(p[0]))
		db.execute("select word, lemm from dictionary where id='%s'", (p[0],))
		dict_surname=db.fetchall()
		for d in dict_surname:
			if (d[1]!=''):
				if (d[1][0].upper()==d[1][0]):
					#print(d[1][0].upper()+"  "+d[1][0])
					print(r[1] + " " + d[0] + " " + d[1])


print("-----------------")

stop = time.time()
ConEv_utils_v01.log_end(os.path.basename(__file__), stop - start)
