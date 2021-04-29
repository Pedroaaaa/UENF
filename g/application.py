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
app.config["SECRET_KEY"] = "123456789"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#load database
#db = SQL("sqlite:///UENF.db")
db = SQL("mysql://root:pmm@2406@localhost:3306/uenf")

#homepage
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        building = db.execute("SELECT name, image FROM buildings WHERE id = %s"% q)
        endereço = db.execute("SELECT endereço, cidade, estado FROM addresses WHERE building_id = %s"% q)
        info = db.execute("SELECT ano, arquiteto, estilo, construção, função FROM building_info WHERE building_id = %s"% q)
        usageDict = db.execute("SELECT * FROM usage_code")
        description = db.execute("SELECT description FROM descriptions WHERE building_id = %s"% q)
        building[0].update(endereço[0])
        building[0].update(info[0])
        building[0].update(description[0])
        for usage in usageDict:
            if usage["code"] == building[0]["função"]:
                building[0]["função"] = usage["description"]
        session["buildingID"] = q
    else:
        building = []
    return jsonify(building)

@app.route("/comment")
def comment():
    q = request.args.get("q")
    if q:
        comments = db.execute("SELECT building_id, type, comment, time, commentID FROM comments WHERE building_id = %s ORDER BY commentID ASC, type DESC", q)
    return jsonify(comments)

@app.route("/postanswer", methods=['POST'] )
def postanswer():
    #check if answer is received by checking the id
    if request.form.get('qid'):
        answer = request.form.get('answer')
        commentID = request.form.get('qid')
    commentType = request.form.get('type')
    #write into sql database
    db.execute("INSERT INTO comments (building_id, type, comment, time, commentID) VALUES ('%s', '%s', '%s', CURRENT_TIMESTAMP , (%s))"% (session["buildingID"], commentType, answer, commentID))
    return redirect("/")

@app.route("/addimage", methods=['POST'] )
def addimage():
    if request.form.get('cover_url'):
        image = request.form.get('cover_url')
        #write into sql database
        if image != "None":
            db.execute('UPDATE buildings SET image = "%s" WHERE id = (%s)'% (image, session["buildingID"]))
        
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
    print (commentType)
    print (comment)
    #write into sql database
    db.execute("INSERT INTO comments (building_id, type, comment, time, commentID) VALUES ('%s', '%s', '%s', CURRENT_TIMESTAMP , (%s))"% (session["buildingID"], commentType, comment, commentID))
    return redirect("/")

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    #load database info to page for editing
    if request.method == 'GET':
        building = db.execute("SELECT * FROM buildings WHERE id IN (%s)"% session["buildingID"])[0]
        endereço = db.execute("SELECT * FROM addresses WHERE building_id IN (%s)"% session["buildingID"])[0]
        info = db.execute("SELECT * FROM building_info WHERE building_id IN (%s)"% session["buildingID"])[0]
        constructions = db.execute("SELECT DISTINCT construção FROM building_info WHERE construção IS NOT NULL ORDER BY construção")
        fields = dict.keys(info)
        usageDict = db.execute("SELECT * FROM usage_code")
        description = db.execute("SELECT description FROM descriptions WHERE building_id = (%s)"% session["buildingID"])[0]
        return render_template("edit.html", building=building, endereço=endereço, info = info, fields = fields, usage = usageDict, constructions = constructions, description = description )
    #update edited info in database
    if request.method == 'POST':
        buildingID = session["buildingID"]
        ano = request.form.get('ano')
        arquiteto = request.form.get('arquiteto')
        estilo = request.form.get('estilo')
        if request.form.get('construção') == 'other':
            construção = request.form.get('construção_other')
        else:
            construção = request.form.get('construção')
        função = request.form.get('função')
        description = request.form.get('cap')
        image = request.form.get('image')
        if image != "None" and image != "none":
            db.execute('UPDATE buildings SET image = "%s" WHERE id = (%s)'% (image, buildingID))
        db.execute('UPDATE building_info SET ano = "%s", arquiteto = "%s", estilo = "%s", construção = "%s", função = "%s" WHERE building_id = (%s)'% (ano, arquiteto, estilo, construção, função, buildingID))
        if db.execute('SELECT * FROM descriptions WHERE building_id = %s'% buildingID):
            db.execute('UPDATE descriptions SET description = "%s" WHERE building_id = (%s)'% (description, buildingID))
        else:
            db.execute('INSERT INTO descriptions VALUES (%s, %s)'% (buildingID, description))
        return redirect("/")