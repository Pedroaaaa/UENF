from cs50 import SQL


db = SQL("mysql://root:pmm@2406@localhost:3306/uenf")

buildingID = 74
image = "kkk"
db.execute('UPDATE buildings SET image = "%s" WHERE id = (%s)'% (image, buildingID))
