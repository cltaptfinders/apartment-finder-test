import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase if not already done
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # or use env var
    firebase_admin.initialize_app(cred)

# Email of the user to update
email = "arodriguez@cltapts.com"
new_password = "arodriguez"  # Replace with the new password you want to set

try:
    user = auth.get_user_by_email(email)
    auth.update_user(
        user.uid,
        password=new_password
    )
    print(f"✅ Password updated for user: {email}")
except auth.UserNotFoundError:
    print(f"❌ No user found with email: {email}")
except Exception as e:
    print(f"⚠️ Error updating password: {e}")
