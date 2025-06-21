# -*- coding: utf-8 -*-


from flask import Flask,redirect, url_for,render_template,request

import cgi
import cgitb
import mysql.connector
from decimal import Decimal

# Enable debug output
cgitb.enable()

# Get the form data
form = cgi.FieldStorage()
mydb = mysql.connector.connect(host="localhost",user="Tejaswi",password="Venkat@1202",database="Tejaswi")
mycursor = mydb.cursor()
app=Flask(__name__)
@app.route("/",methods=['POST','GET'])
def login():
    if(request.method=="POST"): 
        username=request.form["username"]
        password=request.form['password']
        print(username,password)
        mycursor.execute("SELECT type FROM users WHERE email=%s && password=%s", (username, password))
        # print("<h1>hi</h1>")
        result = mycursor.fetchone()
        if result==('perspective_renter',):
            return redirect(url_for("renter",email=username))
        elif result== ('agent',):
            return redirect(url_for("agent",email=username))
        else:
            return '<h1>Wrong Username or Password</h1>'
    else:
        return render_template("index.html")
@app.route("/register",methods=['POST','GET'])
def register():
    if(request.method=="POST"): 
        # mydb = mysql.connector.connect(host="localhost",user="root",password="manu",database="manohar")
        # mycursor = mydb.cursor()
        name=request.form["name"]
        email=request.form["email"]
        phone=request.form["phone"]
        password=request.form['password']
        type=request.form['type']
        if(type=='renter'):
            location=request.form['location']
            budget=request.form['budget']
            # movein=request.form['movein']
            movein=str('2025-10-02')
            query_users='insert into users values(%s,%s,%s,%s)'
            query_renters='insert into perspective_renters(emailID,name,move_in_date,location,budget) values(%s,%s,%s,%s,%s)'
            mycursor.execute(query_users,(name,email,password,'perspective_renter'))
            mycursor.execute(query_renters, (email, name,movein,location,budget))
            mydb.commit()
            return redirect(url_for('login'))
        else:
            agency=request.form['agency']
            query_users='insert into users values(%s,%s,%s,%s)'
            query_agents='insert into agents values(%s,%s,%s,%s,%s)'
            mycursor.execute(query_users,(name,email,password,'agent'))
            mycursor.execute(query_agents,(email,name,'emp',agency,phone))
            mydb.commit()
            return redirect(url_for('login'))
    else:
        return render_template("register.html")


@app.route('/<email>')
def renter(email):
    query_property='select * from property where available=1'
    mycursor.execute(query_property)
    data = mycursor.fetchall()
    query_bookings='select * from bookingrecords where emailID=%s'
    mycursor.execute(query_bookings,[email])
    bookings=[' ']
    bookings=mycursor.fetchall()
    print(bookings)
    return render_template("homepage_renters.html",data=data,email=email)

@app.route('/agent<email>')
def agent(email):

    return render_template('homepage_agent.html',email=email)
    print(email)

@app.route('/bookings<data>')
def bookings(data):

    # data=eval(data)
    query_bookings='select bookingrecords.emailID,BookingID,property_type, location, city,address,price,description,availability,crimerate,nearby_schools from bookingrecords inner join property on property.propertyID=bookingrecords.propertyID having emailID=%s'
    mycursor.execute(query_bookings,(data,))
    data=mycursor.fetchall()
    if(data):

        return render_template("bookings.html",data=data)
    else:
        return f'<h1>None</h1>'


@app.route('/ads<email>')
def ads(email):
    query_ads='select * from property where emailID=%s'
    mycursor.execute(query_ads,[email])
    ads=mycursor.fetchall()
    return render_template("ads.html",ads=ads)

@app.route('/success<email>')
def success(email):

    return '<center><h1>Success!</h1></center>'

@app.route('/submit_ad<email>',methods=['POST','GET'])
def submit_ad(email):
    if(request.method=="POST"):
        # mydb = mysql.connector.connect(host="localhost",user="root",password="manu",database="manohar")
        # mycursor = mydb.cursor()
        property_type=request.form["type"]
        location=request.form["location"]
        address=request.form["address"]
        city=request.form['city']
        price=request.form['price']
        description=request.form['description']
        school=request.form['school']
        crimerate=request.form['crimerate']
        # date=request.form['date']
        query_house_apartment='insert into property(emailID,property_type,location,city,address,price,description,availability,available,crimerate,nearby_schools) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        mycursor.execute(query_house_apartment,(email,property_type,location,city,address,price,description,'2025-05-10',1,crimerate,school))
        if(property_type=='house' or property_type=='apartment'):

            if(property_type=='house'):
                rooms_no=request.form["rooms"]
                sft=request.form["sft"]
                houseID=mycursor.lastrowid
                query_house2='insert into houses values(%s,%s,%s)'
                mycursor.execute(query_house2,(houseID,rooms_no,sft))
                mydb.commit()
                return redirect(url_for('success',email=email))
            else:
                rooms_no=request.form["rooms_apt"]
                sft=request.form["sft_apt"]
                apartmentID=mycursor.lastrowid
                query_apartment='insert into apartments(apartmentID,rooms,sft) values(%s,%s,%s)'
                mycursor.execute(query_apartment,(apartmentID,rooms_no,sft))
                mydb.commit()
                return redirect(url_for('success',email=email))
        elif(property_type=='commercial_building'):
            build_type=request.form["build_type"]
            sft=request.form["sft_build"]
            buildingID=mycursor.lastrowid
            query_building='insert into commercial_building values(%s,%s,%s)'
            mycursor.execute(query_building,(buildingID,sft,build_type))
            mydb.commit()
            return redirect(url_for('success',email=email))
        else:
            return redirect(url_for('agent',email=email))
    else:
        return redirect(url_for('agent',email=email))
    
@app.route('/book_now/<id>/<email>')
def book_now(id,email):
    query_retrieve_book='select propertyID,property_type,location,city,address,price,description,availability,crimerate,nearby_schools from property where propertyID=%s'
    mycursor.execute(query_retrieve_book,(id,))
    data=mycursor.fetchone()
    type=data[1]
    query_address='select * from address where emailID=%s'
    mycursor.execute(query_address,(email,))
    address=mycursor.fetchall()
    if(type=='house'):
        query_ind='select rooms,sft from houses where houseID=%s'
        mycursor.execute(query_ind,(id,))
        house_data=mycursor.fetchone()
        # return f'<h1>{data,house_data}</h1>'
        return render_template('book_now.html', data=data,ind=house_data,address=address,email=email)
    elif(type=='apartment'):
        query_ind='select rooms,sft from apartments where apartmentID=%s'
        mycursor.execute(query_ind,(id,))
        apartment_data=mycursor.fetchone()
        return render_template('book_now.html', data=data,ind=apartment_data,address=address,email=email)
    else:
        query_ind='select sft,type from commercial_building where buildingID=%s'
        mycursor.execute(query_ind,(id,))
        building_data=mycursor.fetchone()
        return render_template('book_now.html', data=data,email=email,ind=building_data,address=address)

@app.route('/payment<id>/<email>/<type>',methods=['POST','GET'])
def payment(id,email,type):
    if(request.method=="POST"):
        
        name=request.form["name"]
        address=request.form["address-select"]
        card=request.form['credit_card']
        expiry=request.form['expiration']
        cvv=request.form['cvv']

        query_card='select * from creditcard_information where Card_Number=%s'
        mycursor.execute(query_card,(card,))
        result = mycursor.fetchone()
        if (not result):
            query_card_insert='insert into creditcard_information values(%s,%s,%s,%s,%s)'
            mycursor.execute(query_card_insert,(email,card,'2025-05-10',name,cvv))
        if(address=='new-address'):
            line1=request.form['new-address-line-1']
            line2=request.form['new-address-line-2']
            postal_code=request.form['new-address-postal-code']
            city=request.form['new-address-city']
            state=request.form['new-address-state']
            country=request.form['new-address-country']
            query_address_insert='insert into address(emailID,line1,line2,postal_code,city,state,country)values(%s,%s,%s,%s,%s,%s,%s)'
            mycursor.execute(query_address_insert,(email,line1,line2,postal_code,city,state,country))        
            mydb.commit()
        
        query_booking_insert='insert into bookingrecords(emailID,propertyID,creditCard) values(%s,%s,%s)'
        mycursor.execute(query_booking_insert,(email,id,card))

        query_update_property='UPDATE property SET available = 0 where propertyID=%s'
        mycursor.execute(query_update_property,(id,))
        mydb.commit()


    else:
        return redirect(url_for('agent',email=email))

    return f'<h1>Success</h1>'


@app.route('/rewards<email>')
def rewards(email):
    query_rewards='select bookingrecords.emailID, sum(price) as rewards from bookingrecords inner join property on bookingrecords.propertyID = property.propertyID group by emailID having emailID=%s'
    mycursor.execute(query_rewards,(email,))
    rewards=mycursor.fetchone()
    if(rewards):
        return f'<h1>Currently You have "{rewards[1]}" points</h1>'
    else:
        return f'<h1>None</h1>'

if __name__=="__main__":
    app.run(debug=True)