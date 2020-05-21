from application import db
import requests


api_key = "3ZdRtZuPYHNnTuIgTI7QHw"
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": "0060096187"})
data = res.json()
print(data['books'][0]['average_rating'] + " ss" + data['books'][0]['work_reviews_count'])



