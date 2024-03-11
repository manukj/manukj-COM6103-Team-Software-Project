from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import text
from flask_cors import CORS



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


# Create the tables when Flask starts up
with app.app_context():
    db.create_all()

class Device(db.Model):
    deviceID = db.Column(db.Integer, primary_key=True)
    deviceType = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    dateOfRelease = db.Column(db.Date)
    isVerified = db.Column(db.Boolean, default=False)
    classification = db.Column(db.String(50))  # Added classification column

class CustomerDevice(db.Model):
    __tablename__ = 'customer_device'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.deviceID'), nullable=False)
    classification = db.Column(db.String(50))
    device_type = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)

# Establish relationship with the User model
    user = db.relationship('User', backref=db.backref('customer_devices', lazy=True))
# Establish relationship with the Device model
    device = db.relationship('Device', backref=db.backref('customer_devices', lazy=True))

# Access customer_devices for a user
# user_instance.customer_devices(Returns a list of associated CustomerDevice instances)
# Access the user for a customer_device
# customer_device_instance.user (Returns the associated User instance)

# the serialize method is used for the CustomerDevice model to convert instances of the model into a serializable format
# When you need to return a JSON response for a CustomerDevice instance, you can use this method:
# Assuming `customer_device` is an instance of CustomerDevice --> serialized_data = customer_device.serialize()
    def serialize(self):
        return {
            'user_id': self.user_id,
            'deviceID': self.deviceID,
            'deviceType': self.deviceType,
            'brand': self.brand,
            'model': self.model,
            'dateOfRelease': self.dateOfRelease,
            'isVerified': self.isVerified,
            'classification': self.classification,
        }


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
        return jsonify({'message': 'Login Successful'}), 200
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


@app.route('/api/moveDeviceClassification', methods=['POST'])
def move_device_classification():
    """
    Move device classification for a user by staff.

    Returns:
        A JSON response with a success message if the classification is moved successfully.
        A JSON response with an error message if the user, device, or new classification is not found.
    """
    data = request.json

    # Input Validation
    email = data.get('email')
    new_classification = data.get('new_classification')
    if not email or not new_classification:
        return jsonify({'error': 'Invalid request data'}), 400

    # Check if the staff user is authenticated
    staff_user = User.query.filter_by(email='staff@example.com').first()  # Adjust the email as per your staff user

    if not staff_user or not staff_user.isStaff:
        return jsonify({'message': 'Unauthorized access'}), 403

    user = User.query.filter_by(email=email).first()

    if user:
        customer_device = CustomerDevice.query.filter_by(user_id=user.id).first()

        if customer_device:
            customer_device.classification = new_classification
            db.session.commit()
            return jsonify({'message': 'Classification moved successfully'}), 200
        else:
            return jsonify({'message': 'Device information not found for the user'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404