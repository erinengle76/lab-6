### Lab 3 ###
'''
Class: INFO 253B SPRING 2023
Author: ERIN JONES
Date of Late Edit: 02/16/2023

The following server works with a local JSON file (quotes.json) containing key:value pairs which specify a day of the week and a
a quote associated with that day. 

Lines 14 - 40 contain imports and helper functions that help to simplify the view function for each route. Functions are as follows:
    - getDataFromFile() - collects data from the local JSON and puts it into dictionary format
    - updateFile() - updates the JSON file, where an updated dictionary is passed as an argument. This is used when quotes are
    modified, added, or deleted.
    - validDay() - checks to see if the day passed either in the request body or in the URL represents a valid day of the week against a list
    - updateCase() - ensures all input is changed to all lower case prior to being used for searching the dictionary or being added as a key

Lines 49 - 79 handle GET and POST requests associated with the "/" route.

    - POST (lines 70 - 90)
        - user-provided data is accessed from the request body
        - if any of the user data is empty or missing, a KeyError will be thrown, caught and handled, returning a 400 status code w/empty body
        - the user-provided day is tested using validDay(); if the day is not valid, a 400 status code w/empty body is returned
        - the user-provided day is checked against the dictionary; if the day exists already, a 400 status code w/empty body is returned
        - if the day does not exist in the dictionary, the dictionary is updated to add the day:quote pair, the file is updated and
         the function returns a 201 status code w/the key-value pair in the body in JSON format

Lines 81 - 123 handle GET, DELETE and PUT requests associated with the "/<day>" route

    - For all requests, the view function first checks to see that the day provided is a valid day. If the day is not valid, an error
    message and a 400 status code is passed
    - If no day is provided, a 405 error will be thrown and handled by lines 145-147 - returning a blank body and a 405 error
    - If the day provided is a valid day of the week, the various methods are handled as follows:
    - GET (lines 101-107)
        - If the day exists in the file, the quote is returned in JSON format with a 200 status code
        - If the day does not exist in the file, a blank body and 204 status code are returned

Lines 159-161 provide an error handler function for 405 errors returning 405 status code and blank body 
'''

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/quotes_db"
db = SQLAlchemy(app)

class Quotes(db.Model):
    day = db.Column(db.String(80), primary_key=True)
    quote = db.Column(db.String(1000))

    def to_dict(self):
        return {
            'day' : self.day,
            'quotes' : self.quote
        }

def getDataFromFile():
    file = open("quotes.json")
    quotesDict = json.load(file)
    file.close()
    return quotesDict

def updateFile(allQuotes):
    with open("quotes.json", "w") as f:
        json.dump(allQuotes, f)
        f.close()
    return True

def validDay(day):
    validDays = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    if validDays.count(day) > 0:
        return True
    else:
        return False

def updateCase(day):
    newDay = day.lower()
    return newDay

@app.route("/", methods = ["POST"])
def addDay():
    if request.method == "POST":
        data = request.get_json()
        try:
            rDay = data["day"]
            requestDay = updateCase(rDay)
            requestQuote = data["quote"]
            if len(requestQuote) == 0:
                return "", 400
            else:
                if validDay(requestDay):
                    new_quote = Quotes(day=requestDay, quote=requestQuote)
                    db.session.add(new_quote)
                    try:
                        db.session.commit()
                        return jsonify(new_quote.to_dict()), 201
                    except IntegrityError:
                        db.session.rollback()
                        quote_update = Quotes.query.filter_by(day=requestDay).first()
                        # if quote_update:
                        quote_update.day = requestDay
                        quote_update.quote = requestQuote
                        db.session.commit()
                        return jsonify(Quotes.to_dict), 200  
                    # try:
                    #     exists = allQuotes[requestDay]
                    #     return "", 400
                    # except KeyError:
                    #     allQuotes[requestDay] = requestQuote
                    #     updateFile(allQuotes)
                    #     return jsonify({
                    #         requestDay:requestQuote
                    #     }), 201
                else:
                    return "Please enter a valid day of the week.", 400
        except KeyError:
            return "Appropriate data was not provided in your request", 400
   
@app.route("/<day>", methods = ["GET"])
def getByID(day):
    day = updateCase(day)
    if validDay(day):
        if request.method == "GET":
            quote = Quotes.query.filter_by(day=day).first()
            if quote:
                return jsonify(quote.to_dict)
            else:
                return jsonify({'Error': 'A quote for this day does not exist in the database'}), 204
            # try:
            #     return jsonify({
            #         day:allQuotes[day]
            #     }), 200
            # except KeyError: 
            #     return "", 204
    else:
        return "Please enter a valid day of the week.", 400   

@app.errorhandler(405)
def handleMethodError(e):
    return "Method Not Allowed", 405


        


