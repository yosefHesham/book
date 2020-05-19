from application import db
import requests
name = "rousef"
apiKey ='AIzaSyA9yMVvxWwADV57ZPAS7vuiCcTvR0LKV1Y'
covers = dict()
count = 0
row = db.execute("select isbn from books where lower(title)  like :title", {'title':  name[0] + "%" }).fetchall()
res = requests.Session
print(len(row))
for i in range (len(row)):
    api_endpoint = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key={}".format(row[i]['isbn'],apiKey)
    res = requests.get(api_endpoint)
    result = res.json()
    print(res.url)
    count = count + 1
    print("## {} ##".format(count))
    #entry = result['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    #print(entry)
    #covers[row[i]['isbn']] = entry



