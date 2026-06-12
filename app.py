from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "cs50_final_projesi_hemen_usta"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def db_baglan():
    conn = sqlite3.connect("hemenusta.db")
    conn.row_factory = sqlite3.Row
    return conn

# Sinsi hatayı çözen güvenli mimari: Veri tabanı siteye ilk istek atıldığında kurulur
@app.before_request
def veritabani_kur():
    # Bu kontrol sayesinde her tıklandığında boşuna tekrar tekrar çalışmaz
    if not os.path.exists("hemenusta.db"):
        conn = db_baglan()
        conn.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT NOT NULL, sifre_hash TEXT NOT NULL, telefon TEXT, mail TEXT, ilce TEXT, rol TEXT NOT NULL, meslek TEXT, hakkinda TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS usta_isleri (id INTEGER PRIMARY KEY AUTOINCREMENT, usta_id INTEGER, foto_yolu TEXT NOT NULL, is_tanimi TEXT NOT NULL, fiyat INTEGER NOT NULL)")
        
        # Hazır Numan Usta (Şifre: 373737)
        sifre_numan = generate_password_hash('373737')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO kullanicilar (isim, sifre_hash, telefon, mail, ilce, rol, meslek, hakkinda) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ('Numan Küçük', sifre_numan, '05551234567', 'numan@usta.com', 'çekmeköy', 'usta', 'Su Tesisatçısı', '15 yıllık tecrübe.'))
        uid = cursor.lastrowid
        conn.execute("INSERT INTO usta_isleri (usta_id, foto_yolu, is_tanimi, fiyat) VALUES (?, ?, ?, ?)", (uid, 'tesisat1.jpg', 'Mutfak Bataryası Değişimi', 750))
        conn.execute("INSERT INTO usta_isleri (usta_id, foto_yolu, is_tanimi, fiyat) VALUES (?, ?, ?, ?)", (uid, 'tesisat2.jpg', 'Kombi Petek Temizliği', 1200))
        
        conn.commit()
        conn.close()

@app.route("/", methods=["GET", "POST"])
def ana_sayfa():
    db = db_baglan()
    if request.method == "POST":
        ilce = request.form.get("ilce", "").strip().lower().replace('İ', 'i').replace('I', 'ı')
        meslek = request.form.get("meslek", "")
        ustalar = db.execute("""
            SELECT kullanicilar.*, usta_isleri.foto_yolu, usta_isleri.is_tanimi, usta_isleri.fiyat 
            FROM kullanicilar 
            LEFT JOIN usta_isleri ON kullanicilar.id = usta_isleri.usta_id 
            WHERE kullanicilar.rol = 'usta' 
            AND (kullanicilar.ilce = ? OR kullanicilar.ilce LIKE ?)
            AND kullanicilar.meslek = ?
        """, (ilce, f"%{ilce}%", meslek)).fetchall()
        db.close()
        return render_template("anasayfa.html", ustalar=ustalar, aranan_ilce=ilce, aranan_meslek=meslek)
    db.close()
    return render_template("anasayfa.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        rol = request.form.get("rol")
        db = db_baglan()
        db.execute("""
            INSERT INTO kullanicilar (isim, sifre_hash, telefon, mail, ilce, rol, meslek, hakkinda) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (request.form.get("isim"), generate_password_hash(request.form.get("sifre")), request.form.get("telefon"), request.form.get("mail"), request.form.get("ilce", "").strip().lower(), rol, request.form.get("meslek"), request.form.get("hakkinda")))
        db.commit()
        db.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        isim = request.form.get("isim")
        sifre = request.form.get("sifre")
        db = db_baglan()
        kullanici = db.execute("SELECT * FROM kullanicilar WHERE isim = ?", (isim,)).fetchone()
        db.close()
        
        if kullanici and check_password_hash(kullanici["sifre_hash"], sifre):
            session["kullanici_id"] = kullanici["id"]
            session["kullanici_adi"] = kullanici["isim"]
            session["rol"] = kullanici["rol"]
            
            if kullanici["rol"] == "usta":
                return redirect("/panel")
            else:
                return redirect("/")
        else:
            return "Hatalı kullanıcı adı veya şifre!"
    return render_template("login.html")

@app.route("/panel", methods=["GET", "POST"])
def panel():
    if not session.get("kullanici_id") or session.get("rol") != "usta": 
        return redirect("/")
        
    usta_id = session["kullanici_id"]
    if request.method == "POST":
        is_tanimi = request.form.get("is_tanimi")
        fiyat = request.form.get("fiyat")
        file = request.files.get("foto")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db = db_baglan()
            db.execute("INSERT INTO usta_isleri (usta_id, foto_yolu, is_tanimi, fiyat) VALUES (?, ?, ?, ?)", (usta_id, filename, is_tanimi, fiyat))
            db.commit()
            db.close()
            return redirect("/panel")
            
    db = db_baglan()
    isler = db.execute("SELECT * FROM usta_isleri WHERE usta_id = ?", (usta_id,)).fetchall()
    db.close()
    return render_template("panel.html", isler=isler)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
