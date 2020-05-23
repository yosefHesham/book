from application import db
import requests


#api_key = "3ZdRtZuPYHNnTuIgTI7QHw"
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": "0060096187"})
#data = res.json()

#name = 'YOUSEF'
#print(name.swapcase())
row = db.execute("select id from books where isbn = :isbn ",{'isbn':"0380795272"}).fetchone()
print(row[0])


