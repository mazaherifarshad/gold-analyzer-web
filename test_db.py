import sqlite3 
print("Testing SQLite...") 
conn = sqlite3.connect(':memory:') 
cursor = conn.cursor() 
cursor.execute("CREATE TABLE test (id int)") 
cursor.execute("INSERT INTO test VALUES (1)") 
conn.commit() 
print("? Success! SQLite works!") 
conn.close() 
