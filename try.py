from application import db

row = db.execute("Select id, username, hash from users where username = :username", {'username':'yosef'}).fetchone()
print(row)