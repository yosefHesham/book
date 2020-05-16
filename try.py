from application import db

row = db.execute("Select id, username, hash from users where username = :username", {'username':'yosef'}).fetchone()
name = "h"

if  not name.strip():
    print("stripped")