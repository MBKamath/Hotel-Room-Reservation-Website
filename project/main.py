
from enum import unique
from flask import Flask,redirect,render_template,request,flash
from flask.globals import request
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask import json,session
from flask_mail import Mail
import json
#localhost conn
local_server=True
app=Flask(__name__)
app.secret_key="kamath"

with open('config.json','r') as c:
    params=json.load(c)["params"]

#to establish the smtp connections to the mail servers 
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail=Mail(app)

#To get unique user access
login_manager = LoginManager(app)
login_manager.login_view='login'
#creating a database and connecting it...
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@127.0.0.1/HOTEL'
db=SQLAlchemy(app)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#relations
class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    U_Name=db.Column(db.String(30))
    email=db.Column(db.String(30))
    U_dob=db.Column(db.String(15))
    U_Pno=db.Column(db.Integer)
    U_password=db.Column(db.String(1000),unique=True)

class Hotel(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    H_name=db.Column(db.String(30))
    email=db.Column(db.String(100))
    H_password=db.Column(db.String(1000))

class Hotelrooms(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(30),unique=True)
    hname=db.Column(db.String(100))
    regularrooms=db.Column(db.Integer)
    semiluxuryrooms=db.Column(db.Integer)
    luxuryrooms=db.Column(db.Integer)
    luxurypoolrooms=db.Column(db.Integer)

class Booking(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uemail=db.Column(db.String(50))
    roomtype=db.Column(db.String(50))
    hcode=db.Column(db.String(1000))
    no_of_rooms=db.Column(db.Integer)
    uname=db.Column(db.String(50))
    uphone=db.Column(db.String(15))


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/addroomdetails',methods=['POST','GET'])
def addroomdetails():
    email=session['user1']
    posts=Hotel.query.filter_by(email=email).first()
    hcode=posts.H_name
    postsdata=Hotelrooms.query.filter_by(hcode=hcode).first()
    if request.method=="POST":               
        code=request.form.get('hcode')
        name=request.form.get('hname') 
        rrooms=request.form.get('regularrooms') 
        slrooms=request.form.get('semiluxuryrooms') 
        lrooms=request.form.get('luxuryrooms') 
        lprooms=request.form.get('luxurypoolrooms') 
        code=code.upper()
        huser=Hotel.query.filter_by(H_name=code).first()
        hruser=Hotelrooms.query.filter_by(hcode=code).first()
        if hruser:
           
            flash("Hotel data already present...You can update the data","info")
            return render_template("hotelrooms.html",postsdata=postsdata)
        if huser:
            db.engine.execute(f"INSERT INTO `Hotelrooms` (`hcode`,`hname`,`regularrooms`,`semiluxuryrooms`,`luxuryrooms`,`luxurypoolrooms`) VALUES ('{code}','{name}','{rrooms}','{slrooms}','{lrooms}','{lprooms}')")
            flash("Hotel rooms updated","info")
            return render_template("hotelrooms.html",postsdata=postsdata)
        else:
            flash("Hotel not found in Database","warning")
    return render_template("hotelrooms.html",postsdata=postsdata)

#to link the post request from signup page and get and  store the values in the database
@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST": 
        name=request.form.get('U_Name')
        email=request.form.get('U_email')
        dob=request.form.get('U_dob')
        phno=request.form.get('U_PNo')
        password=request.form.get('U_password')
        #we encrypt the password below
        encpwd=generate_password_hash(password)
        user1=User.query.filter_by(email=email).first()
        userpwd=User.query.filter_by(U_password=password).first()
        if user1 or userpwd :
            flash("User with same e-mail already exists or the password is taken","warning")
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO `User`(`U_Name`,`email`,`U_dob`,`U_PNo`,`U_password`) VALUES ('{name}','{email}','{dob}','{phno}','{encpwd}')")
        flash("Successfully Signed up...Please Login","success")
        return render_template("userlogin.html")
    return render_template("usersignup.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST": 
        email=request.form.get('U_email')
        password=request.form.get('U_password')
        user=User.query.filter_by(email=email).first()
    # to check if decrypted password from database matches the password of the user given in login form
        if user and check_password_hash(user.U_password,password):
            login_user(user)
            flash("Successfully Logged in","success")
            return render_template("index.html")
        else:
            #to display flash message by passing the fields into the variables in message.html file 
            flash("Wrong inputs","danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")


@app.route('/hotellogin',methods=['POST','GET'])
def hotellogin():
    if request.method=="POST": 
        email=request.form.get('email')
        password=request.form.get('H_password')
        user=Hotel.query.filter_by(email=email).first()
    # to check if decrypted password from database matches the password of the user given in login form
        if user and check_password_hash(user.H_password,password):
            session['user1']=email
            session['code']=user.H_name
            flash("Successfully Logged in","success")
            return render_template("index1.html")
        else:
            #to display flash message by passing the fields into the variables in message.html file 
            flash("Wrong Credentials","danger")
            return render_template("hotellogin.html")
    return render_template("hotellogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST": 
        username=request.form.get('username')
        password=request.form.get('password')
        #if given credentials matches then redirect to add hotel page
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("Admin Login Success","success")
            return render_template("addHotUser.html")
        else:
            flash("Invalid Credentials","danger")
    return render_template("admin.html")

@app.route('/logout')
#below method tells that user must be logged in to implement this route
@login_required
def logout():
    logout_user()
    flash("Logout successful","info")
    return redirect(url_for('login'))
    
@app.route('/addhoteluser',methods=['POST','GET'])
def addhoteluser():
    if('user' in session and session['user']==params['user']):
        if request.method=="POST": 
              
            hname=request.form.get('H_name')
            email=request.form.get('H_email')       
            password=request.form.get('H_password')
        #we encrypt the password below
            encpwd=generate_password_hash(password)
            hname=hname.upper()
            user=Hotel.query.filter_by(email=email).first()
            if user:
                flash("Hotel mail already exists in the Database","warning")
            else:
                db.engine.execute(f"INSERT INTO `Hotel` (`H_name`,`email`,`H_password`) VALUES ('{hname}','{email}','{encpwd}')")
                flash("Data sent to Hotel management and successfully added to the Travel-Inn Database","success")
            return render_template("addHotUser.html")

    else:
        flash("Login and try again","warning")
        return redirect('/admin')


@app.route("/hedit/<string:id>",methods=['POST','GET'])
def hedit(id):
    if('user1' in session):
        postsdata=Hotelrooms.query.filter_by(id=id).first()
        if request.method=="POST":               
            code=request.form.get('hcode')
            name=request.form.get('hname') 
            rrooms=request.form.get('regularrooms') 
            slrooms=request.form.get('semiluxuryrooms') 
            lrooms=request.form.get('luxuryrooms') 
            lprooms=request.form.get('luxurypoolrooms') 
            code=code.upper()
            db.engine.execute(f"UPDATE `Hotelrooms` SET `hcode`='{code}',`hname`='{name}',`regularrooms`='{rrooms}',`semiluxuryrooms`='{slrooms}',`luxuryrooms`='{lrooms}',`luxurypoolrooms`='{lprooms}' WHERE `Hotelrooms`.`id`={id}")
            flash("Availability of rooms updated","info")
            return redirect("/addroomdetails")            
        return render_template("hedit.html",postsdata=postsdata)

    

@app.route("/hdelete/<string:id>",methods=['POST','GET'])
def hdelete(id):
    if('user1' in session):
        db.engine.execute(f"DELETE FROM `Hotelrooms` WHERE `Hotelrooms`.`id`={id}")
        flash("Hotel details deleted","danger")
        return redirect("/addroomdetails")

@app.route("/details",methods=['GET'])
@login_required
def details():
    email=current_user.email
    data=db.engine.execute(f"SELECT * FROM `Booking` WHERE `Booking`.`uemail`='{email}'")
    return render_template("details.html",data=data)          
#To check DB connection
@app.route("/test")
def hotel():
    try:
        a=HOTEL.query.all()
        print(a)
        return "my database is connected"
    except Exception as e:
        print(e)
        return f"not connected {e}"

@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    flash("Admin logged out","info")
    return redirect('/admin')

@app.route('/logouthotel')
def logouthotel():
    session.pop('user1')
    flash("Hotel user logged out","info")
    return redirect('/hotellogin')

@app.route('/booking',methods=['POST','GET'])
@login_required
def booking():
    query=db.engine.execute(f"SELECT * FROM `Hotelrooms`")
    if request.method=="POST":
        uemail=request.form.get('uemail')
        roomtype=request.form.get('roomtype')
        hcode=request.form.get('hcode')
        nor=request.form.get('nor')
        uname=request.form.get('uname')
        uphone=request.form.get('uphone')
        check2=Hotelrooms.query.filter_by(hcode=hcode).first()
        if not check2:
            flash("Hotel code not found","danger")
        code=hcode
        dbb=db.engine.execute(f"SELECT * FROM `Hotelrooms` WHERE `Hotelrooms`.`hcode`='{code}'")
        roomtype=roomtype
        if roomtype=="Regular Room":
            for d in dbb:
                seat=d.regularrooms
                ar=Hotelrooms.query.filter_by(hcode=code).first()
                ar.regularrooms=seat-int(nor)
                seat=seat-int(nor)
                db.session.commit()
        elif roomtype=="Semi-Luxury Room":
            for d in dbb:
                seat=d.semiluxuryrooms
                ar=Hotelrooms.query.filter_by(hcode=code).first()
                ar.semiluxuryrooms=seat-int(nor)
                seat=seat-int(nor)
                db.session.commit()
        elif roomtype=="Luxury Room":
            for d in dbb:
                seat=d.luxuryrooms
                ar=Hotelrooms.query.filter_by(hcode=code).first()
                ar.luxuryrooms=seat-int(nor)
                seat=seat-int(nor)
                db.session.commit()
        elif roomtype=="Luxury Room with Pool":
            for d in dbb:
                seat=d.luxurypoolrooms
                ar=Hotelrooms.query.filter_by(hcode=code).first()
                ar.luxurypoolrooms=seat-int(nor)
                seat=seat-int(nor)
                db.session.commit()  
        else:
            pass   
        check=Hotelrooms.query.filter_by(hcode=code).first()
        if(seat>0 and check):
            res=Booking(uemail=uemail,roomtype=roomtype,hcode=hcode,no_of_rooms=nor,uname=uname,uphone=uphone)  
            db.session.add(res)
            db.session.commit()
            flash("Your Hotel Rooms have been reserved\n Visit the Hotel for booking and payment","success")
        else:  
            flash("Reservation could not be processed due to shortage of rooms","warning")
    return render_template("booking.html",query=query)

app.run(debug=True)