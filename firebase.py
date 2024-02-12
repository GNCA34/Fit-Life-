
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("yazlab-d0f5a-firebase-adminsdk-hfmn1-8b0954369d.json")

firebase_admin.initialize_app(cred, {'databaseURL': "https://yazlab-d0f5a-default-rtdb.firebaseio.com"})

ref = db.reference("/Kullanicilar")
print(ref.get())

