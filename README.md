# Project 1

Web Programming with Python and JavaScript

the project containts 8 templates:

and most of them does not need explaining

but "bookpage.html" is just a page to display some random books for the user
and "result.html" it will display the books the user is searching for 

## helpers.py module

i created that module to handle required loggin function , to prevent user from accessing any data before logging in
also in this module i created a function to call the api to retrieve the data


# models folder
in this folder i created some classes to handle the data
"books.py" this class has all info about the book and it`s used in bookdetails page
"defaultbooks" to avoid loading unused data from the db i created that class which has only info about the book and it`s used in the bookpage and result page

"review.py" and "user_review.py"
the first one is to parse the received data from good reads api
the second is to parse the info about the reviews made by the user




