import os
import requests
import json
from cs50 import SQL
from flask import Flask, jsonify, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#load database
db = SQL("sqlite:///Harvard.db")

#homepage
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    q = request.args.get("q", "")
    if q:
        building = db.execute("SELECT name, image FROM buildings WHERE id = ?", q)
        address = db.execute("SELECT address, city, state FROM addresses WHERE building_id = ?", q)
        info = db.execute("SELECT year, architect, style, construction, usage FROM building_info WHERE building_id = (?)", q)
        usageDict = db.execute("SELECT * FROM usage_code")
        description = db.execute("SELECT description FROM descriptions WHERE building_id = ?", q)
        building[0].update(address[0])
        building[0].update(info[0])
        building[0].update(description[0])
        for usage in usageDict:
            if usage["code"] == building[0]["usage"]:
                building[0]["usage"] = usage["description"]
        session["buildingID"] = q
    else:
        building = []
    return jsonify(building)

@app.route("/comment")
def comment():
    q = request.args.get("q", "")
    if q:
        comments = db.execute("SELECT building_id, type, comment, time, commentID FROM comments WHERE building_id = ? ORDER BY commentID ASC, type DESC", q)
    return jsonify(comments)

@app.route("/postanswer", methods=['POST'] )
def postanswer():
    #check if answer is received by checking the id
    if request.form.get('qid'):
        answer = request.form.get('answer')
        commentID = request.form.get('qid')
    commentType = request.form.get('type')
    #write into sql database
    db.execute("INSERT INTO comments (building_id, type, comment, time, commentID) VALUES (?, ?, ?, CURRENT_TIMESTAMP , ?)", session["buildingID"], commentType, answer, commentID)
    return redirect("/")

@app.route("/addimage", methods=['POST'] )
def addimage():
    if request.form.get('cover_url'):
        image = request.form.get('cover_url')
        #write into sql database
        db.execute('UPDATE buildings SET image = (?) WHERE id = (?)', image, session["buildingID"])
        return redirect("/")
    else:
        return redirect("/")

@app.route("/postcomment", methods=['POST'] )
def postcomment():
    comment = request.form.get('comment')
    #set commentID so that answer and question can be grouped togehter
    if db.execute('SELECT MAX(commentID) FROM comments')[0]["MAX(commentID)"]!= None:
        commentID = db.execute('SELECT MAX(commentID) FROM comments')[0]["MAX(commentID)"] + 1
    else:
        commentID = 0
    commentType = request.form.get('type')
    #write into sql database
    db.execute("INSERT INTO comments (building_id, type, comment, time, commentID) VALUES (?, ?, ?, CURRENT_TIMESTAMP , ?)", session["buildingID"], commentType, comment, commentID)
    return redirect("/")

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    #load database info to page for editing
    if request.method == 'GET':
        building = db.execute("SELECT * FROM buildings WHERE id IN (?)", session["buildingID"])[0]
        address = db.execute("SELECT * FROM addresses WHERE building_id IN (?)", session["buildingID"])[0]
        info = db.execute("SELECT * FROM building_info WHERE building_id IN (?)", session["buildingID"])[0]
        constructions = db.execute("SELECT DISTINCT construction FROM building_info WHERE construction IS NOT NULL ORDER BY construction")
        fields = dict.keys(info)
        usageDict = db.execute("SELECT * FROM usage_code")
        description = db.execute("SELECT description FROM descriptions WHERE building_id = ?", session["buildingID"])[0]
        return render_template("edit.html", building=building, address=address, info = info, fields = fields, usage = usageDict, constructions = constructions, description = description )
    #update edited info in database
    if request.method == 'POST':
        buildingID = session["buildingID"]
        year = request.form.get('year')
        architect = request.form.get('architect')
        style = request.form.get('style')
        if request.form.get('construction') == 'other':
            construction = request.form.get('construction_other')
        else:
            construction = request.form.get('construction')
        usage = request.form.get('usage')
        description = request.form.get('cap')
        image = request.form.get('image')
        db.execute('UPDATE buildings SET image = (?) WHERE id = (?)', image, buildingID)
        db.execute('UPDATE building_info SET year = (?), architect = (?), style = (?), construction = (?), usage = (?) WHERE building_id = (?)', year, architect, style, construction, usage, buildingID)
        if db.execute('SELECT * FROM descriptions WHERE building_id = (?)', buildingID):
            db.execute('UPDATE descriptions SET description = (?) WHERE building_id = (?)', description, buildingID)
        else:
            db.execute('INSERT INTO descriptions VALUES (?, ?)', buildingID, description)
        return redirect("/")
