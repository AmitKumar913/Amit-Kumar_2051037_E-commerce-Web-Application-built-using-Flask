from flask import Flask, request, render_template, session, redirect, url_for,flash,jsonify
import requests
import os
import json
import pandas as pd
from middleware import guest,auth
from captcha.image import ImageCaptcha
import random
from flask_mail import *
from datetime import *
import pytz
from twilio.rest import Client

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestHeaderFieldsTooLarge
import uuid
# import logging
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Your API key
API_KEY = '579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b'

# # Enable logging
# logging.basicConfig(level=logging.DEBUG)


# setting the confi for sending the sms 
#----------------------sms Configuration-----------------
account_sid = 'AC8dec5083868b5269717df425561d97a9'
auth_token = 'e8aa8658fad0f66798276e94da1cef7a'
client = Client(account_sid, auth_token)

# setting the confi for sending the mail 
#----------------------mail Configuration-----------------
app.config["MAIL_SERVER"]='smtp.office365.com'
app.config["MAIL_PORT"]="587"
app.config["MAIL_USERNAME"]="ankiyaTech@outlook.com"  # PUT your outlook email.id
app.config["MAIL_PASSWORD"]="Amit@12345"  # PUT   your ouutlook password
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USE_SSL"]=False
mail=Mail(app)   #creating the obj of Mail clas through we send the mail 
#----------------------------------------------------------


#configurer the upload directory and imag
#________________________________________
app.config["UPLOAD_DIRECTORY"]="static/profile_img/"
app.config["MAX_CONTENT_LENGTH"]= 16 * 1024 *1024 #16MB
app.config["ALLOWED_EXTENSIONS"]= [".jpg",'.jpeg','.png','.gif']




data_file = "static/one.json"
login_data_file = "static/username.json"
user_cart_data="static/info.json"
user_address_file="static/user_address.json"


# [How to prevent browser back button after logout?]  OR
# [How do we control web page caching, across all browsers?] - https://stackoverflow.com/questions/49547/how-do-we-control-web-page-caching-across-all-browsers
# Add no-cache headers to all responses
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

## _______File System_________


# Ensure data files exist
if not os.path.exists(data_file):
    with open(data_file, 'w') as file:
        file.write('[]')  # Initialize with an empty list

if not os.path.exists(login_data_file):
    with open(login_data_file, 'w') as file:
        file.write('[]')  # Initialize with an empty list

if not os.path.exists(user_cart_data):
    with open(user_cart_data, 'w') as file:
        file.write('[]')  # Initialize with an empty list

if not os.path.exists(user_address_file):
    with open(user_address_file, 'w') as file:
        file.write('[]')  # Initialize with an empty list


# Read the JSON data from file
def read(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data

# Write the JSON data to file
def write(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

# Add id with increasing values to each item
def adding_ixd():
    existing_data = read(data_file)
    for idx, item in enumerate(existing_data, start=1):
        item['id'] = idx
    write(data_file, existing_data)

# Generate OTP
def generate_otp():
    return random.randrange(100000, 999999)


# Verify OTP
def verify_otp(entered_otp):
    stored_otp = session.get('otp')
    expiry_time = session.get('otp_expiry')
    if stored_otp is None or stored_otp != int(entered_otp) or datetime.now(pytz.utc) > expiry_time:
        return False
    return True


@app.route("/edit_profile")
def edit_profile():
    user_address=read(user_address_file)
    for user_add in user_address:
        if session["user"]["email"] in user_add:
            user_address=user_add[session["user"]["email"]]
            break
    else:
        user_address={}
    return render_template("edit_profile.html",user=session["user"],addresses=user_address) # pass the whole data of the login user 



@app.route("/upload_img",methods=["POST"])
def upload_img():
    if request.method=='POST':
        try:
            file=request.files['file']
            extension= os.path.splitext(file.filename)[1].lower()
            if extension in app.config["ALLOWED_EXTENSIONS"]:
                # Generate a new filename using UUID
                new_filename = str(uuid.uuid4()) + extension
                # Save the file with the new filename
                file.save(os.path.join(app.config["UPLOAD_DIRECTORY"], secure_filename(new_filename)))
                user_datas=read(login_data_file)
                session["user"]["profile_image"]=os.path.join(app.config["UPLOAD_DIRECTORY"], secure_filename(new_filename))
                for user_data in user_datas:
                    if session['user']["email"]== user_data["email"]:
                        if user_data["profile_image"]!="static/profile_img/default.png":
                            # Delete the file
                            os.remove(user_data["profile_image"])
                        user_data["profile_image"]=session["user"]["profile_image"]
                        write(login_data_file,user_datas)
                flash("Image upload Successfully")
            else:
                flash("File is not an image")
        except RequestHeaderFieldsTooLarge:
            flash("File is larger than 16MB")
            return redirect(url_for("edit_profile"))
    return redirect(url_for("edit_profile"))

@app.route("/add_address",methods=["POST","GET"])
def add_address():
    if request.method=="POST":
        address2=request.form["address2"] if request.form["address2"] else " "
        landmark= request.form["landmark"] if request.form["landmark"] else " "
        # Generate a unique ID for the address
        address_id = str(uuid.uuid4())
        address={
                "id": address_id,
                "country":request.form["country"],
                "pincode":request.form["pincode"],
                "address1":request.form["address1"],
                "address2":address2,
                "landmark":landmark,
                "city":request.form["city"].title (),
                "state":request.form["state"].title ()
        }
        user_address=read(user_address_file)
        if "add" in session:
            for user_add in user_address:
                if session["user"]["email"] in user_add:
                    for add in user_add[session["user"]["email"]]:
                        if add['id']==session["add"]:
                            user_add[session["user"]["email"]].remove(add)
                            del session["add"]
                            break
        for user_add in user_address:
            if session["user"]["email"] in user_add:
                user_add[session["user"]["email"]].append(address)
                break    
        else:
            new_address={session["user"]["email"]:[address]}
            user_address.append(new_address)
        write(user_address_file,user_address)
        user_address=read(user_address_file)
        for user_add in user_address:
            if session["user"]["email"] in user_add:
                user_address=user_add[session["user"]["email"]]
                break
            else:
                user_address={}
        flash("Address add successfully !")
        return render_template("edit_profile.html",user=session["user"],addresses=user_address)
    return render_template("add_address.html",user=session["user"],address={})



@app.route("/edit_add/<id>",methods=["GET"])
def edit_add(id):
    user_address=read(user_address_file)
    if request.method== "GET":
        # id=request.args.get("id")
        for user_add in user_address:
            if session["user"]["email"] in user_add:
                for add in user_add[session["user"]["email"]]:
                    if add['id']==id:
                        session["add"]=id
                        return render_template("add_address.html",address=add)
        
            
    return redirect(url_for("edit_profile"))


@app.route("/delete_add/<id>",methods=["GET"])
def delete_add(id):
    user_address=read(user_address_file)
    if request.method== "GET":
        # id=request.args.get("id")
        for user_add in user_address:
            if session["user"]["email"] in user_add:
                for add in user_add[session["user"]["email"]]:
                    if add['id']==id:
                        user_add[session["user"]["email"]].remove(add)
                        write(user_address_file,user_address)
                        flash("Address delete Successfully! ")
                        return redirect(url_for("edit_profile"))
        
            
    return render_template("edit_profile.html")
#___________postal & address___________

@app.route('/get_location/<pincode>', methods=['GET'])
def get_location(pincode):
    url = 'https://api.data.gov.in/resource/709e9d78-bf11-487d-93fd-d547d24cc0ef'
    params = {
        'api-key': API_KEY,
        'format': 'json',
        'filters[pincode]': pincode
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200 and 'records' in data and len(data['records']) > 0:
            post_office = data['records'][0]
            location_data = {
                'city': post_office.get('district', ''),
                'state': post_office.get('statename', '')
                
            }
            return jsonify(location_data)
        else:
            
            return jsonify({'error': 'Invalid Pincode or No data found'}), 400
    except Exception as e:
        
        return jsonify({'error': str(e)}), 500









@app.route("/sms_otp",methods=["POST","GET"])
def sms_otp():
    if request.method=="POST":
        login_data = read(login_data_file)
        # number=request.form["number"]
        email=request.form["email"]
        for element in login_data:
            if email==element["email"]:
                session["number"]=element['number']
                session["element"]=element
                return redirect(url_for("sms_generator"))
            # else:
            #     return render_template("login_sms_otp.html",myMsg="This Mobile no. is not registered, Please Register ! ")
                
        else:
            return render_template("login_sms_otp.html",myMsg="This Mobile no. is not registered, Please Register ! ")
    else:
        return render_template("login_sms_otp.html")


@app.route("/sms_generator")    
def sms_generator():
    otp=generate_otp()
    session['otp'] = otp
    session['otp_expiry'] = datetime.now(pytz.utc) + timedelta(minutes=1)
    # print(otp)
    message = client.messages.create(
        body="This is your otp for login "+str(otp)+"\nValid for 1 min",
        from_='+14013299388',
        to="+91"+session["number"]
    )
    return render_template("sms_otp_verification.html")

@app.route("/sms_verify",methods=["POST"])
def sms_verify():
    if request.method == 'POST':
        entered_otp = request.form["otp"]
        if verify_otp(entered_otp):
            session['email'] = session["element"]["email"]  # Store the username in the session
            session['tag']=session["element"]['tag']
            # del session["number"]
            # del session["element"]
            return redirect(url_for("home"))
    return render_template("user_opt_verification.html", msg="Invalid OTP. Please try again.")

# password_check 
def passwrod_check(password):
    if len(password)<8:
        msg="Password length must be greater than or equal to 8 characters  !"
        return False,msg
    cap_char=False
    small_char=False
    special_char=False
    for char in password:
        if ord(char) in range(97,123):
            small_char=True
        elif ord(char) in range(65,91):
            cap_char=True
        elif ord(char) in range(33,48) or ord(char) in range(58,65) or ord(char) in range(123,127):
            special_char=True
    if cap_char==False:
        msg="Password must contain aleast one uppercase char !"
        return False,msg
        # return render_template("register.html", myMsg="Password must contain aleast one uppercase char ")
    if small_char==False:
        msg="Password must contain aleast one lowercase char  !"
        return False,msg
        # return render_template("register.html", myMsg="Password must contain aleast one lowercase char ")
    if special_char==False:
        msg="Password must contain aleast one special char  !"
        return False,msg
        # return render_template("register.html", myMsg="Password must contain aleast one special char ")
    return True,""

## _________Routes_____________
@app.route("/")
@guest
def home():
    if 'email' in session:
        return redirect(url_for('show_data'))
    return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
@guest
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        login_data = read(login_data_file)
        for user_data in login_data:
            if user_data['email'] == email:
                if user_data['password'] == password:
                    session['email'] = email  # Store the username in the session
                    session['tag']=user_data['tag']
                    session['name']=user_data["name"]
                    session["user"]=user_data
                    if user_data['tag']==1:
                        return render_template("admin_dashboard.html",name=session['name'])
                    else:
                        return redirect(url_for('show_data'))
                else:
                    return render_template("login.html", myMsg="Invalid password")
        else:
            return render_template("login.html", myMsg="User is not registered, Please Register ! ")      
    return render_template("login.html")


@app.route("/register")
def register():
    # creating random number for cpatcha image
    num= random.randrange(100000,999999)
    # create an image instance of the given size
    img=ImageCaptcha(width=280,height=90)
    # immage cpatcha text
    global captcha_text
    captcha_text=str(num)
    # write the image on the given file and save it 
    img.write(captcha_text,"static/captcha/user_captcha.png")
    return render_template("register.html")


@app.route("/register_insert", methods=["POST", "GET"])
# @guest
def register_insert():
    
    if request.method == 'POST':
        captcha=request.form['captcha']
        # print(captcha_text)
        # print(captcha)
        if captcha!=captcha_text:
            flash("Invalid Captcha !")
            return redirect(url_for("register"))
        login_data = read(login_data_file)
        name=request.form["name"]
        email=request.form['email'].lower()
        # this is checking user is already register or not 
        for entry in login_data:
             if email in entry['email']:
                flash("User is already registered  !")
                return redirect(url_for("register"))
                #   return render_template("register.html", myMsg="User is already registered ")  
               
        password=request.form['password']

        valid, message = passwrod_check(password)
        if valid==False:
            flash(message)
            return redirect(url_for("register"))
        re_password=request.form['re_password']

        # this is checking password and re_password is eaual or not
        if password!=re_password:
            flash("Password is not Matched  !")
            return redirect(url_for("register"))
            #  return render_template("register.html", myMsg="Passwrod is not Matched")
        else:
            global new_entry
            new_entry={
                "tag" : 0,
                "name": name,
                "email" : email,
                "password" : password,
                "number" :request.form["number"],
                "profile_image" : "static/profile_img/default.png"
            }
            # session.clear()
            session["new_entry"]=new_entry
            return redirect(url_for("otp_generator"))
            # email_verification()
           
            
            # return  render_template("login.html")    
    return redirect(url_for("register"))

@app.route("/otp_generator")
def otp_generator():
    otp = generate_otp()
    session['otp'] = otp
    session['otp_expiry'] = datetime.now(pytz.utc) + timedelta(minutes=1)
    new_entry = session.get("new_entry")
    existing_entry = session.get("existing_entry")
    if new_entry:
        msg = Message("ankiyaTech Email Verification", sender="ankiyaTech@outlook.com", recipients=[new_entry["email"]])
        msg.body = "Hi "+new_entry["name"]+ "!\n\nYour email OTP is " + str(otp)
    

    elif existing_entry:
        
        msg = Message("ankiyaTech Email Verification", sender="ankiyaTech@outlook.com", recipients=[existing_entry["email"]])
        msg.body = "Hi "+existing_entry["name"]+ " !\n\nYour email OTP is for reset password " + str(otp)
        
    mail.send(msg)
    return render_template("user_opt_verification.html")
    


#________________Forget_Password ___________

@app.route("/forget_password",methods=["POST","GET"])
def forget_password():
    if request.method=='POST':
        login_data = read(login_data_file)
        email=request.form["email"]
        for element in login_data:
            if email==element["email"]:
                global existing_entry
                existing_entry=element
                session["existing_entry"]=element
                if "new_entry" in session:
                    del session["new_entry"]
                return redirect(url_for("otp_generator"))
        else:
            return render_template("forget_password.html",myMsg="User is not registered, Please Register ! ")
    else:
        return render_template("forget_password.html")



#___________email verification__________
@app.route("/email_verify",methods=["POST"])
def email_verify():
 
    if request.method == 'POST':
        entered_otp = request.form["otp"]
        if verify_otp(entered_otp):
            login_data = read(login_data_file)
            if "new_entry" in session:
                del session["new_entry"]
                # here new_entry is the global variable 
                login_data.append(new_entry)
                write(login_data_file, login_data)
                return  render_template("login.html")
            else:
                return render_template("reset_password.html") 
    return render_template("user_opt_verification.html", msg="Invalid OTP. Please try again.")

#_______________reset_password______
@app.route("/reset_password",methods=["GET","POST"])
def reset_passwrod():
    if request.method=="POST":
        password=request.form["password"]
        valid, message = passwrod_check(password)
        if valid==False:
            flash(message)
            return render_template("reset_password.html")
        re_password=request.form['re_password']

        # this is checking password and re_password is eaual or not
        if password!=re_password:
            flash("Password is not Matched  !")
            return render_template("reset_password.html")

        login_data = read(login_data_file)
        if "existing_entry" in session:
            del session["existing_entry"]
            for element in login_data:
                if existing_entry["email"]==element["email"]:
                    element["password"]=password
            write(login_data_file, login_data)
        return  render_template("login.html")
    return render_template("reset_password.html")

#____________logout__________

@app.route("/logout")
# @auth
def logout():
    session.pop('email', None)  # Remove the username from the session
    session.pop('tag',None)
    session.clear()
    return redirect(url_for('login'))

##__________Admin Routes_______________

#Adding new data into the JSON file

@app.route("/add_data", methods=["POST", "GET"])
@auth
def adding_new():
    existing_data = read(data_file)
    if request.method == 'POST':
        ixd = len(existing_data) + 1
        new_entry = {
            "product_name": request.form['product_name'],
            "product_number": int(request.form["product_number"]),
            "color": request.form["color"],
            "size": request.form['size'],
            "image": None,
            "price": "$"+str(request.form['price']),
            "id": ixd
        }
        existing_data.append(new_entry)
        write(data_file, existing_data)
        return render_template("crud_show.html", new_entry=[new_entry], myMsg="This is the new data added to our file ")
    else:
        return render_template('add_data.html')

#deleting the existing data from the JSON file
@app.route("/delete_data", methods=['GET'])
@auth
def delete_data():
    existing_data = read(data_file)
    if request.method== "GET":
        index=int( request.args.get("id"))
        if index>0 and index<=len(existing_data):
            del_data = existing_data.pop(index - 1)
            write(data_file, existing_data)
            adding_ixd()
            return render_template("crud_show.html", myMsg="Your data is successfully deleted")
        else:
            return render_template("crud_show.html", myMsg="This id is not in our file 'SORRY' ")
        

# Update the existing data from the JSON file
@app.route("/update_data", methods=["POST", 'GET'])
@auth
def update_data():
    existing_data = read(data_file)
    if request.method== "GET":
        index=int( request.args.get("id"))
        if index>0 and index<=len(existing_data):
            existing_data_updat = existing_data[index - 1]
            return render_template("update.html", new_entry=existing_data_updat)
        else:
            return render_template("crud_show.html", myMsg="This id is not in our file 'SORRY' ")
    elif request.method == 'POST':
        new_entry = {
            "product_name": request.form['product_name'],
            "product_number": int(request.form["product_number"]),
            "color": request.form["color"],
            "size": request.form['size'],
            "image": None,
            "price": request.form['price'],
            "id": int(request.form['id'])
        }
        existing_data[int(request.form['id']) - 1] = new_entry
        write(data_file, existing_data)
        return render_template("crud_show.html", new_entry=[new_entry], myMsg="This is the updated data to our file ")



## ___________Common Routes______________



def paginate_data(data, page, per_page):
    """
    Paginate the data.

    :param data: List of data to paginate.
    :param page: Current page number.
    :param per_page: Number of items per page.
    :return: A tuple (paginated_data, total_pages).
    """
    total_items = len(data)
    total_pages = (total_items + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data[start:end]
    return paginated_data, total_pages


@app.route("/show_data")
@auth
def show_data():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    adding_ixd()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    # Read data from file
    existing_data = read(data_file)
    
    # Paginate the data
    paginated_data, total_pages = paginate_data(existing_data, page, per_page)
    
    # User-specific data for the cart
    user = session['email']
    existing_users = read(user_cart_data)
    total_cart_items = next((user_data["total"] for user_data in existing_users if user_data["email"] == user), 0)
    
    template = "admin_show_data.html" if session['tag'] == 1 else "user_show_data.html"
    return render_template(template, 
                           existing_data=paginated_data, 
                           total_items=total_cart_items, 
                           user=session["user"], 
                           page=page, 
                           total_pages=total_pages)


#_________filter___________________
# I have to implement

@app.route("/detail/<int:id>")
@auth
def detail(id):
    existing_data = read(data_file)
    particular_row=existing_data[id-1]
    return render_template('detail.html',existing_data=particular_row)


## _____________User Routes____________



@app.route("/search_bar", methods=["POST"])
@auth
def search_bar():
    existing_data = read(data_file)
    if request.method == "POST":
        search_data = request.form["search"].lower()
        required_data = [data for data in existing_data if search_data in data["product_name"].lower()]

        if not required_data:
            return render_template("user_show_data.html", msg="There is no product related to this word! 🥱", user=session["user"],total_pages=0, 
                               page=0)

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page

        # Paginate the search results
        paginated_data, total_pages = paginate_data(required_data, page, per_page)

        return render_template("user_show_data.html", 
                               existing_data=paginated_data, 
                               total_pages=total_pages, 
                               page=page, 
                               user=session["user"])
    return redirect(url_for("show_data"))


@app.route('/add_cart/<int:id>')
@auth
def add_cart(id):
    user=session['email']  # here we get the user email from the session
    existing_users=read(user_cart_data)
    existing_data = read(data_file)
    for existing_user in existing_users:
        if user in existing_user['email']:
            id=str(id)
            if id in existing_user["items"]:
                existing_user["items"][id]+=1
            else:
                existing_user["items"][id]=1
            existing_user["total"]+=1
            break
    else:
        new_user={
            "email":user,
            # id : frequency
            "items":{id:1},
            "total" : 1
        }
        existing_users.append(new_user)
    write(user_cart_data, existing_users)
    return redirect(url_for("show_data"))

@app.route("/view_cart")
@auth
def view_cart():
    user=session['email']  # here we get the user email from the session
    existing_cart_users=read(user_cart_data)
    existing_data = read(data_file)

    for existing_cart_user in existing_cart_users:
        if user in existing_cart_user['email']:
            product_lists=[]
            total=0
            for index, frequency in existing_cart_user["items"].items():
                product_name = existing_data[int(index)-1]["product_name"]
                product_price=float(existing_data[int(index)-1]["price"][1:])
                total_price=round(product_price * frequency, 2)
                total+=total_price
                product_lists.append({product_name: [frequency, int(index),total_price]}) # productname : [freq,its id,product_price(total_cost)]
                # print(product_lists)
            if product_lists==[]:
                return  render_template("cart.html",msg="Your cart is Empty, Please add !",total=0,user=session["user"])
            else:
                return render_template("cart.html",items=product_lists,total=round(total,2),user=session["user"])
    return render_template("cart.html",msg="Your cart is Empty, Please add !",total=0,user=session["user"])
 
@app.route("/increase_count/<int:id>")
@auth
def increase_count(id):
    user=session['email']  # here we get the user email from the session
    existing_users=read(user_cart_data)
    existing_data = read(data_file)
    for existing_user in existing_users:
        if user in existing_user['email']:
            id=str(id)
            existing_user["items"][id]+=1
            existing_user["total"]+=1
            break
    write(user_cart_data, existing_users)
    return redirect(url_for("view_cart"))

@app.route("/decrease_count/<int:id>")
@auth
def decrease_count(id):
    user=session['email']  # here we get the user email from the session
    existing_users=read(user_cart_data)
    existing_data = read(data_file)
    for existing_user in existing_users:
        if user in existing_user['email']:
            id=str(id)
            existing_user["items"][id]-=1
            existing_user["total"]-=1
            if existing_user["items"][id]==0:
                del existing_user["items"][id]
            break
    write(user_cart_data, existing_users)
    return redirect(url_for("view_cart"))

#___________Checkout__________
@app.route("/checkout")
def checkout():
    shipping_address = "358, Pushpanjali apartment, Patuli Palki Bar, 24 Paraganas North, West Bengal, 700109"
    card_name = "Diya Gupta"
    card_number = "9383 3847 3494 8763"
    order_items = [
        {"name": "Mushroom - Porcini, Dry", "price": 877.78},
        {"name": "Hog / Sausage Casing - Pork", "price": 764.71},
        {"name": "Oil - Sunflower", "price": 744.86}
    ]
    delivery = 16.99
    discount = 0.00
    total_exc_tax = 557.99
    tax = 12.99
    order_total = total_exc_tax + tax + delivery
    savings = 34.99

    return render_template('checkout.html', 
                           shipping_address=shipping_address,
                           card_name=card_name,
                           card_number=card_number,
                           order_items=order_items,
                           delivery=delivery,
                           discount=discount,
                           total_exc_tax=total_exc_tax,
                           tax=tax,
                           order_total=order_total,
                           savings=savings,user=session["user"])





if __name__ == "__main__":
    app.run(debug=True, port=8080)
