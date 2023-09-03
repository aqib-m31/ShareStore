import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv
from os import getenv


# Initialize Firebase Admin SDK for Firebase Storage
# Load environment variables from a .env file
load_dotenv()

# Retrieve the path to the Google Cloud service account key file from environment variables
cred_path = getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize the Firebase Admin SDK using the service account credentials
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {"storageBucket": "share-store-0.appspot.com"})

# Create Reference to Firebase Storage bucket
bucket = storage.bucket()
