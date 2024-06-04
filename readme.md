# This is my Login Credentials 
# For Admin 
"email\":\"akgupta3507@gmail.com\", \"password\": \"Amit@1234\" 
# For User
\"email\": \"amit.kumar.cse24@heritageit.edu.in\", \"password\":
\"Amit@12345\",

Project Overview This backend code is built using Flask, a Python web
framework. It includes various features such as session management, SMS
configuration, email configuration, file upload handling, and more.

# Key Components Flask Setup: 
The Flask app is initialized with a secret
key for session management. API Key: You've defined an API key (API_KEY)
for your application. SMS Configuration: Twilio is used for sending SMS
messages. 
You've set up the account SID and authentication token. Email
Configuration: You're using Office 365 SMTP server for sending emails.
Configure the MAIL_USERNAME and MAIL_PASSWORD with your Outlook
credentials. 
# File Upload Handling: 
The UPLOAD_DIRECTORY specifies where
uploaded files (e.g., profile images) are stored. The MAX_CONTENT_LENGTH
limits the size of uploaded files. The allowed file extensions are
defined in ALLOWED_EXTENSIONS. 
# Data Files: 
You have several JSON data
files (one.json, username.json, info.json, and user_address.json). These
files likely store user-related data, cart information, and addresses.
No-Cache Headers: 
You've added no-cache headers to prevent browser
caching after logout. Next Steps Endpoints: Describe the available
endpoints (routes) in your Flask app. Installation and Setup: Provide
instructions on how to set up and run your backend locally.
# Dependencies: 
List any additional Python packages or libraries required.
Environment Variables: Mention any environment variables needed (e.g.,
API keys, database connection strings).

Address Management Your backend code includes functionality related to
managing user addresses. Here's a brief overview:

# Adding an Address: 
When a user submits an address form, the code
generates a unique ID for the address. The address details (country,
pincode, address lines, landmark, city, and state) are collected from
the form. The address is associated with the user's email. If the user
is editing an existing address, the previous address with the same ID is
removed. Otherwise, a new address entry is created. The updated address
data is stored in the user_address.json file. Editing an Address: Users
can edit their existing addresses. 
The route /edit_add/\<id\> allows
users to modify address details. The address ID is extracted from the
URL parameter. The corresponding address is retrieved from the
user_address.json file. Users can update any field (e.g., address lines,
city, state). 
The updated address data is saved back to the file.
Deleting an Address: Users can delete an address. The route
/delete_add/\<id\> removes the address with the specified ID. The
updated address data is saved to the user_address.json file. Postal Code
Lookup: The route /get_location/\<pincode\> performs a lookup using the
Data.gov.in API. 
It retrieves city and state information based on the
provided pincode. The response is returned as JSON data.

# SMS OTP Verification In this section:
you've implemented SMS-based OTP
verification for user login. Here's how it works:

# Requesting OTP: 
When a user enters their registered email, the system
checks if the email exists in the login data. If found, the associated
mobile number is stored in the session. The system generates a random
OTP and sends it via SMS to the user's mobile number. The OTP is valid
for 1 minute. Verifying OTP: The user enters the received OTP in the
verification form. The system compares the entered OTP with the stored
OTP. If the OTP matches and is within the valid time window, the user is
logged in. Otherwise, an error message is displayed. Password Check
Function: You've implemented a password_check function to validate
password strength. It checks for minimum length, uppercase letters,
lowercase letters, and special characters.

# Email Verification and Password Reset In this section:
you've implemented email verification and password reset functionality. Here's
how it works:

# User Registration: 
When a user registers, a random OTP is generated. The
OTP is sent via email to the user's registered email address. The OTP is
valid for 1 minute. The user must enter the OTP to complete the
registration process. Forget Password: If a user forgets their password,
they can request a password reset. The system checks if the provided
email exists in the login data. If found, an OTP is generated and sent
via email. The user must enter the OTP to reset their password. Password
Strength Check: You've implemented a password_check function to ensure
password strength. It checks for minimum length, uppercase letters,
lowercase letters, and special characters.

Admin Routes You're all set! Let's dive into the admin routes of your
application:

Adding New Data (/add_data): Admins can add new product data to the JSON
file. The form collects details such as product name, number, color,
size, and price. A unique ID is generated for the new entry. The data is
appended to the existing JSON file. Deleting Existing Data
(/delete_data): Admins can delete product data based on the provided ID.
The specified entry is removed from the JSON file. Updating Existing
Data (/update_data): Admins can update product data. The route allows
editing details such as product name, number, color, size, and price.
The updated data replaces the existing entry in the JSON file. Common
Routes: The paginate_data function helps with pagination by splitting
data into pages. This function is useful for displaying paginated data
in your application.
election based
on user role (admin or user) Detail View Route: /detail/\<int:id\>
Authentication required Displays details of a specific contact Retrieves
data from the database Search Bar Route: /search_bar Authentication
required Handles search queries Filters contact data based on search
input Paginates search results
