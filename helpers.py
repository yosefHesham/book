from flask import redirect,session,render_template
from functools import wraps
from models.reviews import Review
import requests



def login_required(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def get_reviews(isbn):
            api_key = "3ZdRtZuPYHNnTuIgTI7QHw"
            try:
                
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": "0060096187"})
            except:
                return render_template("error.html", error= "error occuered", direction="/result")    
            data = res.json()
            print(data)
            review = Review(
            data['books'][0]['average_rating'],
            data['books'][0]['work_reviews_count']
            )
            return review
        
        