import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # or use os.getenv if you use env var
    firebase_admin.initialize_app(cred)

# Function to look up user
def lookup_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        print(f"✅ Found user: {user.email}")
        print(f"UID: {user.uid}")
        print(f"Display Name: {user.display_name}")
        print(f"Custom Claims: {user.custom_claims}")
        print(f"Email Verified: {user.email_verified}")
    except auth.UserNotFoundError:
        print(f"❌ No user found with email: {email}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

# Example usage
lookup_user_by_email("brandon@cltapts.com")
