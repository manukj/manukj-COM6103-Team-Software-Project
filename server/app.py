from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import text
from flask_cors import CORS
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345@localhost:3306/test_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:your_password@127.0.0.0:3306/test_db'
db = SQLAlchemy(app)
CORS(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(30), unique=False, nullable=False)
    last_name = db.Column(db.String(60), unique=False, nullable=False)
    phoneNumber = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    isStaff = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phoneNumber': self.phoneNumber,
            'isStaff': self.isStaff,
            'isAdmin': self.isAdmin
        }



class NewDevice(db.Model):
    __tablename__ = 'device'
    deviceID = db.Column(db.Integer, primary_key=True, unique=True)
    deviceType = db.Column(db.String(120), nullable=True)
    brand = db.Column(db.String(120), nullable=True)
    model = db.Column(db.String(120), unique=True, nullable=True)
    dateOfRelease = db.Column(db.Date, nullable=True)
    isVerified = db.Column(db.Boolean, default=False)

class NewUserDevice(db.Model):
    __tablename__ = 'userDevice'
    userDeviceID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, nullable=False)
    deviceID = db.Column(db.Integer, nullable=True)
    dateOfPurchase = db.Column(db.Date, nullable=True)
    imageUrl = db.Column(db.String(120), nullable=True)
    qrCodeUrl = db.Column(db.String(120), nullable=True)
    dateOfCreation = db.Column(db.Date, nullable=True)
    dataRetrievalID = db.Column(db.Integer, nullable=True)
    estimatedValue = db.Column(db.String(120), nullable=True)
    
# Create the tables when Flask starts up
with app.app_context():
    db.create_all()


@app.route("/")
def check_sql_connection():
    try:
        db.session.execute(text("SELECT 1"))
        return 'Connection to MySQL is successful!'
    except Exception as e:
        return f'Error: {str(e)}'


@app.route('/api/login', methods=['POST'])
def login():
    """
    Login implementation. Compares the user supplied credentials with the database entries for authentication.

    Returns:
        A JSON response depending on the correct or invalid credentials.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        return jsonify(user.serialize()), 200
    else:
        return jsonify({'message': 'Invalid Credentials'}), 401



@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email').lower()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phoneNumber = data.get('phoneNumber')
    password = data.get('password')
    acceptedTerms = data.get('terms')

    # check for blank rows
    if email == "" or first_name == "" or last_name == "" or phoneNumber == "" or password == "":
        return jsonify({'message': 'Blank Data!'}), 409

    # check for users who already exist
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User with this email already exists'}), 409

    # ensure user has accepted t&c's
    if not acceptedTerms:
        return jsonify({'message': 'You have not accepted Terms and Conditions'}), 409

    # create the new user
    newUser = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        phoneNumber=phoneNumber,
    )

    # source:
    # https://stackoverflow.com/a/16336401/11449502
    try:
        db.session.add(newUser)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        # code from https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        return jsonify({'message': 'Database Error'}), 500
    return jsonify({'message': 'Login Successful'}), 200


@app.route('/api/getAllUsers', methods=['GET']) 
def getAllUsers():
    """
    Retrieve all users from the database and return them as JSON.
    The role is determined based on the isAdmin and isStaff flags:
    - isAdmin: True -> 'admin'
    - isStaff: True -> 'employee'
    - Neither: -> 'endUser'
    """
    users = User.query.all()
    user_data = [
        {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phoneNumber,
            'role': 'admin' if user.isAdmin else ('employee' if user.isStaff else 'endUser')
        } for user in users
    ]
    return jsonify(user_data)


@app.route('/api/updateUserToStaff', methods=['POST'])
def updateUserToStaff():
    """
    Update a user's status to staff.

    Returns:
        A JSON response with a success message if the user is found and updated successfully.
        A JSON response with an error message and status code 404 if the user is not found.
    """
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.isStaff = True
    db.session.commit()
    return jsonify({'message': 'User updated to staff'}), 200

@app.route('/api/updateUserToAdmin', methods=['POST'])
def updateUserToAdmin():
    """
    Update a user's role to admin.
    Args:
        email (str): The email of the user to update.
    Returns:
        A JSON response with a success message if the user is successfully updated to admin.
        A JSON response with an error message if the user is not found in the database.
    """
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.isAdmin = True
    db.session.commit()
    return jsonify({'message': 'User updated to admin'}), 200
   
@app.route('/api/deleteUser', methods=['POST'])
def deleteUser():
    """
    Delete a user from the database.
    Args:
        email (str): The email of the user to delete.
    Returns:
        A JSON response with a success message if the user is successfully deleted.
        A JSON response with an error message if the user is not found in the database.
    """
    # TODO : Add a check to see if the user calling this api is an admin before deleting
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200
   
@app.route('/api/downgradeToUser', methods=['POST'])
def updateUserToEndUser():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.isAdmin = False
    user.isStaff = False
    db.session.commit()
    return jsonify({'message': 'User downgraded to end user'}), 200

@app.route('/api/createDevice/', methods=['POST'])
def createDevice():
    """
    Create device API
    If user wants to add a new device which is not already listed in the db, it will create a new device entry
    Associates the device with the user by userID
    Returns:
        A JSON response with a success message if the device is successfully created; A JSON response with an error message if the device model already exists in the database.
        A JSON response with a success message if the device is successfully associated with the user; A JSON response with an error message if any problems arrives.
    """
    data = request.json
    userID = data.get('userID')
    deviceType = data.get('deviceType')
    deviceID = data.get('deviceID')
    brand = data.get('brand')
    model = data.get('model')
    imageUrl = data.get('imageUrl')
    qrCodeUrl = data.get('qrCodeUrl')
    dateOfRelease = data.get('dateOfRelease')
    dateOfPurchase = data.get('dateOfPurchase')
    
    """Need to finalize if the isVerified is added in the device or userDevice table"""
    if not all([dateOfPurchase, imageUrl]):
        isVerified = False
    else:
        isVerified = True
    
    if(deviceID is None):
        try:
            newDeviceAdded = NewDevice(
                deviceType=deviceType,
                brand=brand,
                model=model,
                dateOfRelease=dateOfRelease,
                isVerified=False            
            )
            db.session.add(newDeviceAdded)
            db.session.commit()
            deviceID = newDeviceAdded.deviceID
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            return jsonify({'message': 'Device creation error'}), 500
    
    newUserDeviceAdded = NewUserDevice(
        userID = userID,
        deviceID = deviceID,
        dateOfPurchase = dateOfPurchase,
        imageUrl = imageUrl,
        qrCodeUrl = qrCodeUrl,
        dateOfCreation = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        dataRetrievalID = 0,
        estimatedValue = ""
    )
    
    try:
        db.session.add(newUserDeviceAdded)
        db.session.commit()
        return jsonify({'message': 'User Device creation successful'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        return jsonify({'message': 'User device creation error'}), 500