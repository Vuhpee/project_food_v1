#this program gets the food data from openfoodfacts DB using their API and records it to SQLite DB
import sqlite3
from requests import get
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

conn = sqlite3.connect("food.sqlite")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Brand(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT UNIQUE)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Product(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT UNIQUE,
            barcode TEXT UNIQUE, brand_id INTEGER, kcal REAL,
            protein REAL, carb REAL, fat REAL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Consumed 
            (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            product_id INTEGER UNIQUE, amount REAL)""")

#base url with no auth using only READ mode url
baseurl = "https://off:off@world.openfoodfacts.net/api/v2/product/"

#end url consists of the needed attributes about product
endurl = "?fields=product_name,nutriscore_data,nutriments,nutrition_grades,quantity,brands"

while True:
    conn.commit()

    barcode = input("Enter the barcode number of the product:")
    if (len(barcode) < 1): break 

    eat = input("Weight of the eaten portion in grams (if whole package leave blank and press enter): ")
    if (len(eat) > 0):
        eat = int(eat)

    url = baseurl + barcode + endurl 
    response = get(url, verify=False)
    js = response.json()

    if js["status"] == 0:
        print("PRODUCT NOT FOUND!")
        continue

    elif js["status"] == 1:
        #get data from JSON
        brand = js["product"]["brands"]
        name = js["product"]["product_name"]
        barcode = js["code"]
        kcal100 = js["product"]["nutriments"]["energy-kcal_100g"]
        carb100 = js["product"]["nutriments"]["carbohydrates_100g"]
        prot100 = js["product"]["nutriments"]["proteins_100g"]
        fat100 = js["product"]["nutriments"]["fat_100g"]

        print("PRODUCT FOUND.")
        print("Product name:",name)
        print("Barcode Number:",barcode)
        print("Calories 100gr:",kcal100)
        print("Carbonhydrates 100gr:",carb100)
        print("Proteins 100gr:",prot100)
        print("Fat 100gr:",fat100)
        try:
            #weight of package using RE because return value has "g" at the end
            pack_w = int(re.findall("[0-9]+",js["product"]["quantity"])[0])

            if (len(eat) < 1):
                eat = pack_w
            print("Calories taken:",kcal100 * eat / 100)
            print("Carbonhydrates taken:",carb100 * eat / 100)
            print("Proteins taken:",prot100 * eat / 100)
            print("Fat taken:",fat100* eat / 100)
            print("Weight of package:\n", pack_w, "grams")

        #if weight of packet data can not be found
        except:
            print("Calories taken:",kcal100 * eat / 100)
            print("Carbonhydrates taken:",carb100 * eat / 100)
            print("Proteins taken:",prot100 * eat / 100)
            print("Fat taken:\n",fat100 * eat / 100)
        


    #print(json.dumps(js, indent=2))

    #write data to SQLite
    cur.execute("INSERT OR IGNORE INTO Brand (name) VALUES (?)", (brand,))
    cur.execute("SELECT id FROM Brand WHERE name = ?", (brand,))
    brand_id = cur.fetchone()[0]

    cur.execute("""INSERT OR IGNORE INTO Product 
                (name, brand_id, barcode, kcal, protein, carb, fat) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (name, brand_id, barcode, kcal100, prot100, carb100, fat100))
    cur.execute("SELECT id FROM Product WHERE barcode = ?", (barcode,))
    product_id = cur.fetchone()[0]
    
    cur.execute("SELECT product_id FROM Consumed WHERE product_id = ?", (product_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO Consumed (product_id, amount) VALUES (?,?)", (product_id, eat))
    else:
        cur.execute("UPDATE Consumed SET amount = amount + ? WHERE product_id = ?", (eat, product_id))

    conn.commit()

sqlstr = """SELECT Product.name, Brand.name, Product.kcal, Product.protein, Product.carb, Product.fat, Consumed.amount     
            FROM Consumed JOIN product JOIN Brand
            ON Consumed.product_id = Product.id AND Product.brand_id = Brand.id
            ORDER BY Consumed.amount DESC"""
total_kcal = 0
total_prot = 0
total_carb = 0
total_fat = 0
print("\n\nTaken macros for the recording period for each product:")
for name, brand, kcal, protein, carb, fat, amount in cur.execute(sqlstr):
    #ratio to calculate taken macros. Because macro values are recorded for 100 grams of product
    ratio = amount / 100
    total_kcal += kcal * ratio
    total_prot += protein * ratio
    total_carb += carb * ratio
    total_fat += fat * ratio
    print(kcal * ratio,"kcal,",protein * ratio,"g proteins,",carb * ratio,"g carbonhydrates,",fat * ratio,"g fat taken from",brand,name)

print("\n\n------------------IN TOTAL------------------")
print(total_kcal,"kcal,", total_prot,"g proteins,", total_carb,"g cabonhydrates,",total_fat,"g fat taken for the recording period")


#create a .js file to viasualize the data total consumed macros and write html code to it
fhand = open("food.js","w")
fhand.write("foodData = [\n")

output = "["+str(total_kcal)+","+str(total_prot)+","+str(total_carb)+","+str(total_fat)+"]"
fhand.write(output)
fhand.write("\n];\n")
fhand.close()

print("Data written to food.js")
print("Open food.html to visualize the data")

conn.close()
