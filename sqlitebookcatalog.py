import sqlite3 as lite


if __name__ == "__main__":
    
    con = lite.connect('bookcatalog.db')
    
    
    with con:
    
        cur = con.cursor()
        
        cur.execute("DROP TABLE IF EXISTS books")
        
        cur.execute("""CREATE TABLE books (bookid INTEGER PRIMARY KEY, title TEXT, author TEXT, pgcount INT, avg_rating REAL, isbn TEXT, image TEXT)""")
        

