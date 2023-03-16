from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/quotes_db"
db = SQLAlchemy(app)

class Quote(db.Model):
    day = db.Column(db.String(80), primary_key=True)
    quote = db.Column(db.String(1000))

    def to_dict(self):
        return {
            'day' : self.day,
            'quote' : self.quote
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

@app.route('/quotes')
def get_quotes():
    quotes = Quote.query.all()
    return jsonify([quote.to_dict() for quote in quotes])

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
                    new_quote = Quote(day=requestDay, quote=requestQuote)
                    db.session.add(new_quote)
                    try:
                        db.session.commit()
                        return jsonify(new_quote.to_dict()), 201
                    except IntegrityError:
                        db.session.rollback()
                        quote_update = Quote.query.filter_by(day=requestDay).first()
                        # if quote_update:
                        quote_update.day = requestDay
                        quote_update.quote = requestQuote
                        db.session.commit()
                        return jsonify(Quote.to_dict), 200  
                else:
                    return "Please enter a valid day of the week.", 400
        except KeyError:
            return "Appropriate data was not provided in your request", 400
   
@app.route("/<day>", methods = ["GET"])
def getByID(day):
    day = updateCase(day)
    if validDay(day):
        if request.method == "GET":
            quote = Quote.query.filter_by(day=day).first()
            if quote:
                return jsonify(quote.to_dict)
            else:
                return jsonify({'Error': 'A quote for this day does not exist in the database'}), 204

    else:
        return "Please enter a valid day of the week.", 400  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

 

# @app.errorhandler(405)
# def handleMethodError(e):
#     return "Method Not Allowed", 405



        


