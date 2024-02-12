
import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, db
from firebase import db  
app = Flask(__name__)
import os
from werkzeug.security import check_password_hash  
import firebase_admin
from flask import render_template
from firebase import db as firebase_db 
from werkzeug.security import generate_password_hash
import base64
from datetime import datetime
current_time = datetime.now()

from werkzeug.utils import secure_filename
secret_key = os.urandom(24)
print(secret_key)

app = Flask(__name__, static_url_path='/static')

app.config['UPLOAD_FOLDER'] = 'your_upload_folder_path'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
  
    users_ref = db.reference("/Kullanicilar")
    users = users_ref.get()


    for user_id, user_data in users.items():
        if user_data.get("Email") == email and str(user_data.get("sifre")) == password:
      
            if user_data.get('active') is False:
                flash('Giriş başarısız: Hesabınız devre dışı bırakıldı. Lütfen iletişime geçin.')
                return redirect(url_for('index'))
            
          
            flash(f'Giriş başarılı: Hoş geldiniz, {user_data.get("Ad")}')
            if role == "user":
                return redirect(url_for('show_profile', email=email))
            elif role == "coach":
                return redirect(url_for('show_profilecoach',email=email))
            elif role == "admin":
                return redirect(url_for('admin_dashboard'))
          
            return redirect(url_for('show_profile', email=email))

  
    print("Kullanıcı bulunamadı")
    return redirect(url_for('index'))





@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
   
    users_ref = firebase_db.reference("/Kullanicilar")
    users = users_ref.get()
   
    return render_template('admin_dashboard.html',users=users)



@app.route('/add_user', methods=['POST'])
def add_user():
    ad = request.form['ad']
    soyad = request.form['soyad']
    email = request.form['email']
    telefon = request.form['telefon']
    cinsiyet = request.form['cinsiyet']
    dogumtarihi = request.form['dogumtarihi']
    fotograf = request.form['fotografi']
    role = request.form['Rolü']

    
    if not firebase_db.reference("Kullanicilar").get():
        firebase_db.reference("Kullanicilar").set({})

    existing_uids = list(firebase_db.reference("Kullanicilar").get().keys())

    if not existing_uids:
        new_uid = "uid1"
    else:
        max_uid = max(existing_uids, key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
        last_index = int(max_uid[3:]) if max_uid[3:].isdigit() else 0
        new_uid = f"uid{last_index + 1}"

    firebase_db.reference("Kullanicilar").child(new_uid).set({
        'Ad': ad,
        'Soyad': soyad,
        'Email': email,
        'Telefon': telefon,
        'Cinsiyet': cinsiyet,
        'Dogum Tarihi': dogumtarihi,
        'Fotograf': fotograf,
        'role': role
    })

    
    return redirect(url_for('admin_dashboard'))


@app.route('/toggle_account', methods=['POST'])
def toggle_account():
    data = request.get_json()
    user_id = data.get('userId')
    action = data.get('action')

  
    users_ref = firebase_db.reference("/Kullanicilar")
    user_ref = users_ref.child(user_id)

    if action == 'enable':
        user_ref.update({'active': True})
    elif action == 'disable':
        user_ref.update({'active': False})

    return jsonify(success=True)



@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')



@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    ad = request.form['ad']
    soyad = request.form['soyad']
    dogum_tarihi = request.form['dogum_tarihi']
    cinsiyet = request.form['cinsiyet']
    email = request.form['email']
    telefon = request.form['telefon']
    sifre = request.form['sifre']
    fotograf = request.form['fotograf']
    role = request.form['role'] 
    
    if not firebase_db.reference("Kullanicilar").get():
        firebase_db.reference("Kullanicilar").set({})
  
    existing_uids = list(firebase_db.reference("Kullanicilar").get().keys())


 
    if not existing_uids:
        new_uid = "uid1"
    else:
   
        max_uid = max(existing_uids, key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
    
   
        last_index = int(max_uid[3:]) if max_uid[3:].isdigit() else 0
        new_uid = f"uid{last_index + 1}"

    firebase_db.reference("Kullanicilar").child(new_uid).set({
        'Ad': ad,
        'Soyad': soyad,
        'Dogum Tarihi': dogum_tarihi,
        'Cinsiyet': cinsiyet,
        'Email': email,
        'Telefon': telefon,
        'Fotograf':fotograf,
        'sifre': sifre ,
        'role': role
    })

    
    print(f'Kayıt işlemi:{ad} {soyad}')
    return redirect(url_for('index'))





@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset_password.html')

    elif request.method == 'POST':
        email = request.form['email']

        users_ref = firebase_db.reference("/Kullanicilar")
        users = users_ref.get()

        for user_id, user_data in users.items():
            if user_data.get("Email") == email:
               
                firebase_db.reference("Kullanicilar").child(user_id).child("sifre").set("")

                flash(f'{email} adresine şifre sıfırlama bağlantısı gönderildi.')
                return redirect(url_for('index'))

        
        return render_template('reset_password.html', error_message='Belirtilen e-posta adresine sahip bir kullanıcı bulunamadı.')




@app.route('/profile/<email>', methods=['GET'])
def show_profile(email):

    users_ref = firebase_db.reference("/Kullanicilar")
    users = users_ref.get()

    for user_id, user_data in users.items():
        if user_data.get("Email") == email:
            danisan_id = user_id  
            danisan_plans=get_danisan_nutrition_plans(danisan_id)

            danisan_programs = get_danisan_exercise_programs(danisan_id)
            
       
            antrenor_messages = get_messages_by_danisan_id(danisan_id)
            return render_template('profile.html', user_data=user_data, danisan_programs=danisan_programs, antrenor_messages=antrenor_messages, danisan_plans=danisan_plans, update_profile_url=url_for('update_profile', email=email))

   
    
    
    return redirect(url_for('index'))

def get_messages_by_danisan_id(danisan_id):
    messages_ref = firebase_db.reference("messages")
    messages = messages_ref.get()
    antrenor_messages = []

    if messages:
        for message_id, message_data in messages.items():
            if message_data.get("danisan_id") == danisan_id:
                antrenor_messages.append(message_data['antrenor_mesaj'])

    return antrenor_messages





@app.route('/add_message', methods=['POST'])
def add_message():
    danisan_id = request.form['danisan_id']
    antrenor_id = request.form['antrenor_id']
    danisan_mesaj = request.form['danisan_mesaj']

    if not firebase_db.reference("messages").get():
        firebase_db.reference("messages").set({})

    existing_mids = list(firebase_db.reference("messages").get().keys())

    if not existing_mids:
        new_mid = "mid1"
    else:
        max_mid = max(existing_mids, key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
        last_index = int(max_mid[3:]) if max_mid[3:].isdigit() else 0
        new_mid = f"mid{last_index + 1}"

    firebase_db.reference("messages").child(new_mid).set({
        'danisan_id': danisan_id,
        'antrenor_id': antrenor_id,
        'danisan_mesaj': danisan_mesaj,
        'antrenor_mesaj': "", 
    })

    return render_template('profile.html', danisan_id=danisan_id, antrenor_id=antrenor_id, danisan_mesaj=danisan_mesaj, antrenor_mesaj="", user_data={})


@app.route('/add_message2', methods=['POST'])
def add_message2():
    danisan_id = request.form['danisan_id']
    antrenor_id = request.form['antrenor_id']
    antrenor_mesaj = request.form['antrenor_mesaj']

    if not firebase_db.reference("messages").get():
        firebase_db.reference("messages").set({})

    existing_mids = list(firebase_db.reference("messages").get().keys())

    if not existing_mids:
        new_mid = "mid1"
    else:
        max_mid = max(existing_mids, key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
        last_index = int(max_mid[3:]) if max_mid[3:].isdigit() else 0
        new_mid = f"mid{last_index + 1}"

    firebase_db.reference("messages").child(new_mid).set({
        'danisan_id': danisan_id,
        'antrenor_id': antrenor_id,
        'danisan_mesaj': '',
        'antrenor_mesaj':antrenor_mesaj, 
    })

    return render_template('profilecoach.html', danisan_id=danisan_id, antrenor_id=antrenor_id, danisan_mesaj='', antrenor_mesaj=antrenor_mesaj, user_data={})
    




def get_danisan_exercise_programs(danisan_id):
    
    exercise_programs_ref = firebase_db.reference("/exercise_programs")
    exercise_programs = exercise_programs_ref.get()

    danisan_programs = []
    for program_id, program_data in exercise_programs.items():
        if program_data.get("danisan_id") == danisan_id:
            danisan_programs.append(program_data)

    return danisan_programs

def get_danisan_nutrition_plans(danisan_id):
    nutrition_plans_ref=firebase_db.reference("/nutrition_plans")
    nutrition_plans=nutrition_plans_ref.get()
    
    danisan_plans= []
    for plan_id, plan_data in nutrition_plans.items():
        if plan_data.get("danisan_id")==danisan_id:
            danisan_plans.append(plan_data)
    return danisan_plans


@app.route('/update_profile/<email>', methods=['POST'])
def update_profile(email):
    
    ad = request.form['ad']
    soyad = request.form['soyad']
    dogum_tarihi=request.form['dogum_tarihi']
    cinsiyet=request.form['cinsiyet']   
    email=request.form['email']
    telefon=request.form['telefon']
    sifre=request.form['sifre']
    
    fotograf = request.files['fotograf']
    if fotograf:
   
        secure_filename_fotograf = secure_filename(fotograf.filename)

       
        fotograf.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename_fotograf))
    else:
   
        users_ref = firebase_db.reference("/Kullanicilar")
        users = users_ref.get()

        for user_id, user_data in users.items():
            if user_data.get("Email") == email:
                secure_filename_fotograf = user_data.get("Fotograf")
                break

  
    users_ref = firebase_db.reference("/Kullanicilar")
    users = users_ref.get()

    for user_id, user_data in users.items():
        if user_data.get("Email") == email:
            users_ref.child(user_id).update({
                'Ad': ad,
                'Soyad': soyad,
                'Dogum Tarihi':dogum_tarihi,
                'Cinsiyet':cinsiyet,
                'Email':email,
                'Telefon':telefon,
                'Fotograf': secure_filename_fotograf,
                
                'sifre':sifre
                
        
            })
           
            return redirect(url_for('show_profile', email=email))

    return redirect(url_for('index'))



@app.route('/edit_user/<user_id>', methods=['GET'])
def edit_user(user_id):

    users_ref = firebase_db.reference("/Kullanicilar")
    users = users_ref.get()

    for user_id_, user_data in users.items():
        if user_id_ == user_id:
            return render_template('edit_user.html', user_data=user_data, user_id=user_id)

   
  
    return redirect(url_for('index'))





@app.route('/update_user/<user_id>', methods=['POST'])
def update_user(user_id):
    # Formdan gelen güncellenmiş bilgileri al
    ad = request.form['ad']
    soyad = request.form['soyad']
    email = request.form['email']
    telefon = request.form['telefon']
    cinsiyet = request.form['cinsiyet']
    dogumtarihi = request.form['dogumtarihi']
    fotograf = request.files['fotografi']
    role = request.form['Rolü']

    if fotograf:
       
        secure_filename_fotograf = secure_filename(fotograf.filename)

      
        fotograf.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename_fotograf))
    else:
  
        users_ref = firebase_db.reference("/Kullanicilar")
        users = users_ref.get()

        for user_id_, user_data in users.items():
            if user_id_ == user_id:
                secure_filename_fotograf = user_data.get("Fotograf")
                break

   
    users_ref = firebase_db.reference("/Kullanicilar")
    users = users_ref.get()

    for user_id_, user_data in users.items():
        if user_id_ == user_id:
            users_ref.child(user_id_).update({
                'Ad': ad,
                'Soyad': soyad,
                'Email': email,
                'Telefon': telefon,
                'Cinsiyet': cinsiyet,
                'Dogum Tarihi': dogumtarihi,
                'Fotograf': secure_filename_fotograf,
                'role': role
            })
            flash('Kullanıcı bilgileri güncellendi.')
            return redirect(url_for('admin_dashboard'))


    flash('Kullanıcı bulunamadı')
    return redirect(url_for('index'))






@app.route('/show_profilecoach/<email>', methods=['GET'])
def show_profilecoach(email):

    users_ref = firebase_db.reference("/coaches")
    users = users_ref.get()

    for user_id, user_data in users.items():
        if user_data.get("Email") == email:

            danisan_ids = user_data.get("danisanlar", "").split(',')
            danisanlar = []

            for danisan_id in danisan_ids:
                danisan = firebase_db.reference("/Kullanicilar").child(danisan_id).get()
                if danisan:
                    danisanlar.append(danisan)

            exercise_programs_ref = firebase_db.reference("/exercise_programs")
            exercise_programs = exercise_programs_ref.get()

            antrenor_specific_programs = {
                program_id: program for program_id, program in exercise_programs.items() if program.get("antrenor_id") == user_id
            }

            antrenor_messages = get_messages_by_antrenor_id(user_id)

            return render_template(
                'profilecoach.html',
                user_data=user_data,
                danisanlar=danisanlar,
                exercise_programs=antrenor_specific_programs,
                antrenor_messages=antrenor_messages,
                update_profile_url=url_for('update_profilecoach', email=email),
                add_message2_url=url_for('add_message2')
            )

    flash('Profil bulunamadı')
    return redirect(url_for('index'))




def get_messages_by_antrenor_id(antrenor_id):
    messages_ref = firebase_db.reference("messages")
    messages = messages_ref.get()
    danisan_messages = []

    if messages:
        for message_id, message_data in messages.items():
            if message_data.get("antrenor_id") == antrenor_id:
                danisan_messages.append(message_data['danisan_mesaj'])

    return danisan_messages
@app.route('/update_profilecoach/<email>', methods=['POST'])
def update_profilecoach(email):

    Ad = request.form['Ad']
    Soyad = request.form['Soyad']
      
    Email=request.form['Email']
    iletisim_bilgileri=request.form['iletisim_bilgileri']
    danisanlar=request.form['danisanlar']
    
    
    deneyimler=request.form['deneyimler']
    uzmanlik_alanlari=request.form['uzmanlik_alanlari']

    users_ref = firebase_db.reference("/coaches")
    users = users_ref.get()

    for user_id, user_data in users.items():
        if user_data.get("Email") == email:
            users_ref.child(user_id).update({
                'Ad': Ad,
                'Soyad': Soyad,
           
                'Email':email,
                'iletisim_bilgileri':iletisim_bilgileri,
                'danisanlar':danisanlar,
                'deneyimler':deneyimler,
                'uzmanlik_alanlari':uzmanlik_alanlari,
                
                
          
            })
            flash('Profil bilgileriniz güncellendi.')
            return redirect(url_for('show_profilecoach', email=email))

    flash('Kullanici bulunamadi')
    return redirect(url_for('index'))



def get_program_by_id(program_id):

    program_ref = firebase_db.reference(f"/exercise_programs/{program_id}")
    program = program_ref.get()
    return program

@app.route('/update_program/<program_id>', methods=['GET', 'POST'])
def update_program(program_id):
   
    program = get_program_by_id(program_id)

    if request.method == 'POST':
  
        updated_program_data = {
            'danisan_id':request.form['danisan_id'],
            'antrenor_id':request.form['antrenor_id'],
            'danisan_adi':request.form['danisan_adi'],
            'danisan_soyadi':request.form['danisan_soyadi'],
            'egzersiz_adi': request.form['egzersiz_adi'],
            'hedefler': request.form['hedefler'],
            'program_suresi': request.form['program_suresi'],
            'set_sayisi': request.form['set_sayisi'],
          
        }

        update_program(program_id, updated_program_data)
        
        flash('Program başarıyla güncellendi!')
        return redirect(url_for('show_profilecoach', email=session['antrenor_email']))

    return render_template('update_program.html', program=program)









app.secret_key = secret_key

if __name__ == '__main__':
    app.run(debug=True)
    

