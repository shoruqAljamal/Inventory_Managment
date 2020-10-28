import os

from flask import Flask ,render_template,request,redirect,flash
from flask_mysqldb import MySQL
from werkzeug.exceptions import abort

import yaml
app = Flask(__name__, instance_relative_config=True)

app.config.from_mapping(
    SECRET_KEY='dev',

)

db = yaml.load(open('db.yaml'))

# Configuration db
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

def get_db():
    return mysql



# a simple page that says hello
@app.route('/')
def index():
 return render_template('base.html')

@app.route('/getProducts')
def getProducts():
    cur = mysql.connection.cursor()
    resultValue = cur.execute('SELECT product_id , product_name ,location_name FROM location l right JOIN product p ON l.location_id = p.location_id ')
    if resultValue > 0 :
     products = cur.fetchall()
    else:
        products =[]

    return render_template('product/getProduct.html',products =products)


@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    cur = mysql.connection.cursor()
    resultValue = cur.execute(
        'SELECT * FROM location')
    if resultValue > 0:
        locations = cur.fetchall()
    if request.method == 'POST':
        # Fetch form data
        productDetails = request.form
        nameProduct = productDetails['name']
        locationId = productDetails['locationId']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (product_name,location_id) VALUES(%s,%s)",(nameProduct,locationId,))
        mysql.connection.commit()
        cur.close()
        return redirect('/getProducts')
    return render_template('product/addProduct.html',locations=locations)

def get_product(id):

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM PRODUCT "
                              "WHERE product_id = (%s)", (id,))
    if resultValue > 0:
        product = cur.fetchone()
    else:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return product


@app.route('/<int:id>/updateProduct', methods=('GET', 'POST'))
def updateProduct(id):
    product = get_product(id)
    locationId = product[2]
    cur = mysql.connection.cursor()
    resultValue = cur.execute(
        'SELECT * FROM location WHERE NOT location_id = (%s)',(locationId,))
    if resultValue > 0:
        locations = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name']


        if not name:
            error = 'Name is required.'
            flash(error)
        else:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE product SET product_name = (%s)"
                        "WHERE product_id = (%s)", (name,id,))
            mysql.connection.commit()
            cur.close()


            return redirect('/getProducts')

    return render_template('product/editProduct.html', product=product, locations=locations)

######### Location views

@app.route('/getLocations')
def getLocations():
    cur =mysql.connection.cursor()
    resultValue = cur.execute('SELECT * FROM location  WHERE NOT location_id = (%s)',('7',))
    if resultValue>0:
        locations = cur.fetchall()

    return render_template('location/getLocation.html', locations =locations)


@app.route('/addLocation', methods=['GET', 'POST'])
def addLocation():
    if request.method == 'POST':
        locationDetails = request.form
        nameLocation = locationDetails['name']
        cur= mysql.connection.cursor()
        cur.execute("INSERT INTO location (location_name) VALUES(%s)", (nameLocation,))
        mysql.connection.commit()
        cur.close()
        return redirect('/getLocations')
    return render_template('location/addLocation.html')

def get_location(id):

    cur = mysql.connection.cursor()

    resultValue = cur.execute("SELECT * FROM LOCATION " 
                              "WHERE location_id = (%s)",(id,))
    if resultValue > 0:
     location = cur.fetchone()
    return location






@app.route('/<int:id>/updateLocation', methods=('GET', 'POST'))
def updateLocation(id):
    location = get_location(id)

    if request.method == 'POST':
        name = request.form['name']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE location SET location_name = (%s) WHERE location_id = (%s)', (name,id,))
        mysql.connection.commit()
        cur.close()


        return redirect('/getLocations')

    return render_template('location/editLocation.html', location=location)


###############3 Movements

@app.route('/getMovements')
def getMovements():
    cur =mysql.connection.cursor()
    resultValue = cur.execute(
                            'SELECT m.movement_id , m.timestamp,m.qty, p.product_name,lf.location_name,lt.location_name '
                            'FROM productmovement m left join product p '
                            'on m.product_id = p.product_id '
                            'left join location lf on m.from_location_id = lf.location_id '
                            'left join location lt on m.to_location_id = lt.location_id')
    if resultValue > 0:
        movements = cur.fetchall()
    else:
        movements=[]

    return render_template('productMovement/getMovement.html', movements = movements)

@app.route('/addMovement', methods=['GET', 'POST'])
def addMovement():
    cur = mysql.connection.cursor()
   #Locations
    resultValue = cur.execute(
        'SELECT * FROM location')
    if resultValue > 0:
        locations = cur.fetchall()
    #Products
    resultValue = cur.execute(
        'SELECT p.product_id , p.product_name, l.location_name , l.location_id FROM product p left join  location l on p.location_id = l.location_id')
    if resultValue > 0:
        products = cur.fetchall()

    if request.method == 'POST':
        # Fetch form data
        movementDetails = request.form
        #productObj = movementDetails['productObj']
        productObj = movementDetails.get('productObj')
        tolocationId = movementDetails['tolocationId']
        stampdate = movementDetails['stampdate']
        qty = movementDetails['qty']
        productObj = productObj.replace("(","")
        productObj = productObj.replace(")", "")
        values =  productObj.split(",")
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO productmovement (product_id , from_location_id , to_location_id , timestamp , qty) VALUES(%s,%s,%s,%s,%s)",
            (values[0], values[3], tolocationId, stampdate, qty,))
        mysql.connection.commit()
        cur.close()
        cur = mysql.connection.cursor()
        cur.execute("UPDATE product SET location_id =(%s) where product_id =(%s)",
                    (tolocationId, values[0],))
        mysql.connection.commit()
        cur.close()

        return redirect("/getMovements")
    return render_template('productMovement/addMovement.html',locations=locations,products=products)


def get_movement(id):

    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM productmovement "
                              "WHERE movement_id = (%s)", (id,))
    if resultValue > 0:
        movement = cur.fetchone()
    else:
        abort(404, "Movement id {0} doesn't exist.".format(id))

    return movement




@app.route('/<int:id>/updateMovement', methods=('GET', 'POST'))
def updateMovement(id):
    movement = get_movement(id)
    tolocationId = movement[3]

    cur = mysql.connection.cursor()
    resultValue = cur.execute(
        'SELECT * FROM location WHERE NOT location_id = (%s)',(tolocationId,))
    if resultValue > 0:
        locations = cur.fetchall()

     # Products
    resultValue = cur.execute(
        'SELECT p.product_id , p.product_name, l.location_name , l.location_id FROM product p left join  location l on p.location_id = l.location_id')
    if resultValue > 0:
        products = cur.fetchall()


    if request.method == 'POST':
        # Fetch form data
        movementDetails = request.form
        # productObj = movementDetails['productObj']
        productObj = movementDetails.get('productObj')
        tolocationId = movementDetails['tolocationId']
        stampdate = movementDetails['stampdate']
        qty = movementDetails['qty']
        productObj = productObj.replace("(", "")
        productObj = productObj.replace(")", "")
        values = productObj.split(",")


        cur = mysql.connection.cursor()
        cur.execute("UPDATE productmovement SET timestamp = (%s) , from_location_id = (%s), to_location_id = (%s) , product_id = (%s) , qty = (%s) "
                        "WHERE movement_id = (%s)", (stampdate,  values[3],tolocationId, values[0],qty,id,))
        mysql.connection.commit()
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("UPDATE product SET location_id =(%s) where product_id =(%s)",
                    (tolocationId, values[0],))
        mysql.connection.commit()
        cur.close()


        return redirect('/getMovements')

    return render_template('productMovement/editMovement.html', movement=movement, locations=locations, products=products)

@app.route('/Report')
def Report():
    cur =mysql.connection.cursor()
    resultValue = cur.execute(
                            'SELECT  p.product_name , l.location_name , p.product_id, l.location_id , p.location_id '
                            'FROM location l '
                            'join  product p '
                            'on l.location_id = p.location_id order by l.location_name ')
    if resultValue > 0:
         productwithloc= cur.fetchall()
    else:
         productwithloc=[]

    class report:
        def __init__(self, product_name, location_name,qty):
            self.product_name = product_name
            self.location_name = location_name
            self.qty = qty


    list = []

    for row in productwithloc:
        cur = mysql.connection.cursor()
        result = cur.execute(
            'SELECT m.qty from productmovement m '
            'where ( m.to_location_id = (%s) and m.product_id = (%s) ) '
            'order by  m.movement_id desc ', (row[3], row[2],))
        if result > 0:
            resultval = cur.fetchone()
            strresultvleu = str(resultval)
            strresultvleu = strresultvleu.replace("("," ")
            strresultvleu = strresultvleu.split(",")[0]
            list.append(report(row[0],row[1], strresultvleu))
        else :
            list.append(report(row[0], row[1], '0'))


    return render_template('report/Report.html', reports = list)



if __name__ == '__main__':
  app.run(debug=True)

