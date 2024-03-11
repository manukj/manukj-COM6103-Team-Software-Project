from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import text
from flask_cors import CORS
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


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

class Device(db.Model):
    __tablename__ = 'device'
    deviceID = db.Column(db.Integer, primary_key=True)
    deviceType = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    dateOfRelease = db.Column(db.Date, nullable=True)
    isVerified = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'deviceID': self.deviceID,
            'deviceType': self.deviceType,
            'brand': self.brand,
            'model': self.model,
            'dateOfRelease': str(self.dateOfRelease) if self.dateOfRelease else None,
            'isVerified': self.isVerified
        }


class UserDeviceTable(db.Model):
    __tablename__ = 'user_device_table'
    userDeviceID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, ForeignKey('user.id'),nullable=False)
    deviceID = db.Column(db.Integer, ForeignKey('device.deviceID'), nullable=False)
    dateOfPurchase = db.Column(db.Date)
    imageUrl = db.Column(db.String(255))
    qrCodeUrl = db.Column(db.String(255))
    dateOfCreation = db.Column(db.Date)
    dataRetrievalID = db.Column(db.Integer, nullable=True)
    estimatedValue = db.Column(db.String(255))

    # Define foreign key relationships
    user = relationship('User', backref='user_device_table', foreign_keys=[userID])
    device = relationship('Device', backref='user_device_table', foreign_keys=[deviceID])

    def serialize(self):
        return {
            'userDeviceID': self.userDeviceID,
            'deviceID': self.deviceID,
            'dateOfPurchase': str(self.dateOfPurchase),
            'imageUrl': self.imageUrl,
            'qrCodeUrl': self.qrCodeUrl,
            'dateOfCreation': str(self.dateOfCreation),
            'dataRetrievalID': self.dataRetrievalID,
            'estimatedValue': self.estimatedValue
        }




# Create the tables when Flask starts up
with app.app_context():
    db.create_all()


@app.route("/")
def hello_world():
    try:
        db.session.execute(text("SELECT 1"))
        return 'Connection to MySQL is successful!'
    except Exception as e:
        return f'Error: {str(e)}'


@app.route('/api/login', methods=['POST'])
def login():
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


@app.route('/api/getAllUsers', methods=['POST'])
def getAllUsers():
    """
    Retrieve all users from the database and return them as JSON.

    Returns:
        A JSON response containing the serialized data of all users.
    """
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


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


@app.route('/api/updateDeviceVisibility', methods=['POST'])
def update_device_visibility():
    """
    Update device visibility for a user by staff.

    Returns:
        A JSON response with a success message if the visibility is updated successfully.
        A JSON response with an error message if the user or device is not found.
    """
    data = request.json

    # Input Validation
    email = data.get('email')
    device_id = data.get('device_id')
    is_visible = data.get('is_visible')

    if not email or not device_id or is_visible is None:
        return jsonify({'error': 'Invalid request data'}), 400

    # Check if the staff user is authenticated
    staff_user = User.query.filter_by(email='staff@example.com',
                                      isStaff=True).first()  # Adjust the email as per your staff user

    if not staff_user:
        return jsonify({'message': 'Unauthorized access'}), 403

    user = User.query.filter_by(email=email).first()

    if user:
        user_device = UserDeviceTable.query.filter_by(user_id=user.id, device_id=device_id).first()

        if user_device:
            # Update the device visibility
            user_device.visible = is_visible
            db.session.commit()
            return jsonify({'message': 'Device visibility updated successfully'}), 200
        else:
            return jsonify({'message': 'Device not found for the user'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404

