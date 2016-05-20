import sqlite3
import os, sys
import codecs

def main():
    input_file = sys.argv[1]
    db_file = sys.argv[2]
    # Connect to the sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    id_var = 0
    with codecs.open(input_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            #Insert line into database
            c.execute("INSERT OR IGNORE INTO post (id, text) VALUES \
                     (?, ?)", (id_var, line))
            id_var += 1
    #Close the connection
    conn.commit()
    conn.close()
    print "Finished"




if __name__ == "__main__":
    main()
