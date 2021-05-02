import mysql.connector
banco = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "pmm@2406",
    database = "uenf"
)
banco.autocommit = True
db = banco.cursor(dictionary=True)
buildingID = 74
image = "333333333333"
db.execute('UPDATE buildings SET image = "%s" WHERE id = (%s)'% (image, buildingID))
