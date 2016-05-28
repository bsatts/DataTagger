import sqlite3
import sys, json
import codecs
from os import listdir
from os.path import isfile, join
import traceback
from textblob import TextBlob

def main():
    input_folder = sys.argv[1]
    db_file = sys.argv[2]
    # Connect to the sqlite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    #Iterate through the folder and identify all the files
    onlyfiles = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]
    onlyfiles = filter(lambda x: x.endswith(".json"), onlyfiles)
    onlyfiles.sort()

    #Parse each file, scrape reddit contents and add to db
    post_id = 0
    chunk_id = 0
    line_id = 0
    for r_post in onlyfiles:
        try:
            with codecs.open(join(input_folder, r_post), encoding="utf-8") as f:
                post = json.loads(f.read())
        except:
            #Skip file that cannot be decoded
            continue
        #Parse the json file
        try:
            sub = post[0] #Get the link submission
            comments = post[1] #This is the comment body

            #Parse the submission
            sub_data = sub['data']['children'][0]['data']
            sub_name = sub_data['name']
            sub_text = sub_data['selftext']
            sub_title = sub_data['title']
            sub_author = sub_data['author']

            #Add the title to the text
            sub_text = sub_author + u":- " + sub_title + u"\n" + sub_text

            #sub_url = sub_data['url']
            comment_list = []
            #Parse all the comments
            #Define the recursive functions for parsing
            def parse_comment(comment_data):
                #Check if body exists (For cases where link to continue thread exists)
                if u'body' in comment_data:
                    comment_name = comment_data['name']
                    comment_parent = comment_data['parent_id']
                    comment_text = comment_data['body']
                    comment_author = comment_data['author']
                    comment_text = comment_author + u":- " + comment_text
                    comment_replies = comment_data['replies']
                    return {'name': comment_name, 'parent': comment_parent,
                            'text': comment_text, 'replies': comment_replies}
                else:
                    return {}

            def parse_listing(comment_listing):
                children = comment_listing['data']['children']
                for child in children:
                    comment = parse_comment(child['data'])
                    if comment:
                        com_name = comment['name']
                        com_text = comment['text']
                        com_parent = comment['parent']
                        comment_list.append((com_name, com_text, com_parent))
                        if comment['replies'] != u'':
                            parse_listing(comment['replies'])

            parse_listing(comments)

            #Insert all of it into the database
            c.execute("INSERT OR IGNORE INTO post (id, name, text) VALUES \
                (?, ?, ?)", (post_id, sub_name, sub_text))

            #Split into lines and insert
            blob = TextBlob(sub_text)
            lines = blob.sentences
            for line in lines:
                c.execute("INSERT OR IGNORE INTO line (id, text, post_id) VALUES \
                (?, ?, ?)", (line_id, unicode(line), post_id))
                #Chunk the line and insert into db
                line_blob = TextBlob(unicode(line))
                phrases = line_blob.noun_phrases
                for np in phrases:
                    c.execute("INSERT OR IGNORE INTO chunk (id, text, line_id) VALUES \
                    (?, ?, ?)", (chunk_id, unicode(np), line_id))
                    chunk_id += 1
                line_id += 1
            post_id += 1

            for com_tup in comment_list:
                c_name, c_text, c_parent = com_tup
                c.execute("INSERT OR IGNORE INTO post (id, name, text, parent_id) VALUES \
                (?, ?, ?, ?)", (post_id, c_name, c_text, c_parent))

                #Now split into lines and insert
                blob = TextBlob(c_text)
                lines = blob.sentences
                for line in lines:
                    c.execute("INSERT OR IGNORE INTO line (id, text, post_id) VALUES \
                    (?, ?, ?)", (line_id, unicode(line), post_id))
                    #Now chunk each comment and insert
                    line_blob = TextBlob(unicode(line))
                    phrases = line_blob.noun_phrases
                    for np in phrases:
                        c.execute("INSERT OR IGNORE INTO chunk (id, text, line_id) VALUES \
                        (?, ?, ?)", (chunk_id, unicode(np), line_id))
                        chunk_id += 1
                    line_id += 1
                post_id += 1
        except Exception as e:
            print r_post
            print traceback.format_exc()
            sys.exit(1)

    conn.commit()
    conn.close()
    print "Finished"

if __name__ == "__main__":
    main()
