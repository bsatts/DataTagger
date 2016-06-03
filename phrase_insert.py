import sqlite3
import sys, json
import codecs
from os import listdir
from os.path import isfile, join
import traceback
from textblob import TextBlob
from pattern.en import parse, parsetree


def main():
    db_file = sys.argv[1]
    # Connect to the sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    #Get all the lines and for each line fill the phrases
    line_list = c.execute("SELECT id, text FROM line order by id;").fetchall()
    print "Done with fetchall"
    phrase_id = 0
    for line in line_list:
        line_id, text = line
        #Parse the sentence and break it into phrases
        res = parsetree(text, relations = True)
        #Identify the phrases
        sentence = res.sentences[0]
        phrases = sentence.phrases
        for phrase in phrases:
            #Count the length of the words
            if len(phrase.words) >= 2:
                text = unicode(phrase)
                c.execute("INSERT INTO phrase (id, text, line_id) VALUES \
                    (?, ?, ?)", (phrase_id, text, line_id))
                phrase_id += 1
    print phrase_id
    conn.commit()
    conn.close()
    print "Finished"


if __name__ == "__main__":
    main()
