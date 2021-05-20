import os
import requests
import json
import mysql.connector
from flask import Flask, jsonify, flash, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# Configure application
app = Flask(__name__)
app.secret_key = "adfbnviaadfjbkn"


if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#load database
banco = mysql.connector.connect(
    host = "bfmvrld2rnvkgpvamfxo-mysql.services.clever-cloud.com",
    user = "u4khq0vqpwlgbpky",
    passwd = "C3qxBYQLaIuGDJUJFNew",
    database = "bfmvrld2rnvkgpvamfxo",
    port = "3306"
)
banco.autocommit = True
db = banco.cursor(dictionary=True)



#homepage
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():

    q = request.args.get("q")
    session["buildingID"] = request.args.get("q")
    if q:
        db.execute("SELECT name, image FROM buildings WHERE id = %s;"% q)
        building = db.fetchall()
        db.execute("SELECT endereço, cidade, estado FROM addresses WHERE building_id = %s;"% q)
        endereço = db.fetchall()
        db.execute("SELECT ano, arquiteto, estilo, construção, função FROM building_info WHERE building_id = %s;"% q)
        info = db.fetchall()
        db.execute("SELECT * FROM usage_code;")
        usageDict = db.fetchall()
        db.execute("SELECT description FROM descriptions WHERE building_id = %s;"% q)
        description = db.fetchall()
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
    banco2 = mysql.connector.connect(
    host = "bfmvrld2rnvkgpvamfxo-mysql.services.clever-cloud.com",
    user = "u4khq0vqpwlgbpky",
    passwd = "C3qxBYQLaIuGDJUJFNew",
    database = "bfmvrld2rnvkgpvamfxo",
    port = "3306"
)
    banco2.autocommit = True
    db2 = banco2.cursor(dictionary=True)
    q = request.args.get("q")
    if q:
        db2.execute("SELECT building_id, type, comment, time, commentID FROM comments WHERE building_id = %s ORDER BY commentID ASC, type DESC"% q)
        comments = db2.fetchall()
    banco2.close()
    return jsonify(comments)

@app.route("/postanswer", methods=['POST'] )
def postanswer():
    
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
    db.execute('SELECT MAX(commentID) FROM comments')
    ifdb = db.fetchall()
    if ifdb[0]["MAX(commentID)"]!= None:
        db.execute('SELECT MAX(commentID) FROM comments')
        commentID = db.fetchall()[0]["MAX(commentID)"] + 1
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
        db.execute("SELECT * FROM buildings WHERE id IN (%s)"% session["buildingID"])
        building = db.fetchall()[0]
        db.execute("SELECT * FROM addresses WHERE building_id IN (%s)"% session["buildingID"])
        endereço = db.fetchall()[0]
        db.execute("SELECT * FROM building_info WHERE building_id IN (%s)"% session["buildingID"])
        info = db.fetchall()[0]
        db.execute("SELECT DISTINCT construção FROM building_info WHERE construção IS NOT NULL ORDER BY construção")
        constructions = db.fetchall()
        fields = dict.keys(info)
        db.execute("SELECT * FROM usage_code")
        usageDict = db.fetchall()
        db.execute("SELECT description FROM descriptions WHERE building_id = (%s)"% session["buildingID"])
        description = db.fetchall()[0]
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
        db.execute('SELECT * FROM descriptions WHERE building_id = %s'% buildingID)
        ifdb2 = db.fetchall()
        if ifdb2:
            db.execute('UPDATE descriptions SET description = "%s" WHERE building_id = (%s)'% (description, buildingID))
        else:
            db.execute('INSERT INTO descriptions VALUES (%s, %s)'% (buildingID, description))
        return redirect("/")
