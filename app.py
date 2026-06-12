from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "cs50_final_projesi_hemen_usta"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def db_baglan():
    conn = sqlite3.connect("hemenusta.db")
    conn.row_factory = sqlite3.Row
    return conn

def veritabani_kur():
    conn = db_baglan()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            sifre_hash TEXT NOT NULL,
            telefon TEXT,
            mail TEXT,
            ilce TEXT,
            rol TEXT NOT NULL,
            meslek TEXT,
            hakkinda TEXT,
            vip_mi INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usta_isleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usta_id INTEGER,
            foto_yolu TEXT NOT NULL,
            is_tanimi TEXT NOT NULL,
            fiyat INTEGER NOT NULL,
            FOREIGN KEY(usta_id) REFERENCES kullanicilar(id)
        )
    """)
    conn.commit()
    conn.close()

veritabani_kur()

@app.route("/", methods=["GET", "POST"])
def ana_sayfa():
    db = db_baglan()
    search_query = request.args.get("search", "").strip()
    city_query = request.args.get("city", "").strip()

    # Temel sorgu: Ustaları ve eğer yükledilerse son iş fotoğraflarını getirir
    query = """
        SELECT kullanicilar.*, usta_isleri.foto_yolu, usta_isleri.is_tanimi, usta_isleri.fiyat
        FROM kullanicilar
        LEFT JOIN usta_isleri ON kullanicilar.id = usta_isleri.usta_id
        WHERE kullanicilar.rol = 'usta'
    """
    params = []

    # Kelime araması (İsim veya Meslek/Kategori)
    if search_query:
        query += " AND (kullanicilar.isim LIKE ? OR kullanicilar.meslek LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Şehir / İlçe araması
    if city_query:
        query += " AND kullanicilar.ilce LIKE ?"
        params.append(f"%{city_query}%")

    # POST araması (Eski form yapısının bozulmaması için uyumluluk)
    if request.method == "POST":
        ilce = request.form.get("ilce", "").strip()
        meslek = request.form.get("meslek", "")
        if ilce:
            query += " AND kullanicilar.ilce LIKE ?"
            params.append(f"%{ilce}%")
        if meslek:
            query += " AND kullanicilar.meslek = ?"
            params.append(meslek)

    query += " GROUP BY kullanicilar.id" # Her ustayı bir kez listelemek için
    ustalar = db.execute(query, params).fetchall()
    db.close()
    
    return render_template("anasayfa.html", ustalar=ustalar, search_query=search_query, city_query=city_query)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        isim = request.form.get("isim")
        sifre = request.form.get("sifre")
        rol = request.form.get("rol") or "usta"
        telefon = request.form.get("telefon")
        mail = request.form.get("mail")
        ilce = request.form.get("ilce", "").strip()
        meslek = request.form.get("meslek")
        hakkinda = request.form.get("hakkinda")

        sifre_hash = generate_password_hash(sifre)

        db = db_baglan()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO kullanicilar (isim, sifre_hash, telefon, mail, ilce, rol, meslek, hakkinda)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (isim, sifre_hash, telefon, mail, ilce, rol, meslek, hakkinda))
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
            return redirect("/")
        else:
            return "Hatalı kullanıcı adı veya şifre!"

    return render_template("login.html")

@app.route("/panel", methods=["GET", "POST"])
def panel():
    if not session.get("kullanici_id"):
        return redirect("/login")

    usta_id = session["kullanici_id"]

    if request.method == "POST":
        is_tanimi = request.form.get("is_tanimi")
        fiyat = request.form.get("fiyat")
        file = request.files.get("foto")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            db = db_baglan()
            db.execute("""
                INSERT INTO usta_isleri (usta_id, foto_yolu, is_tanimi, fiyat)
                VALUES (?, ?, ?, ?)
            """, (usta_id, filename, is_tanimi, fiyat))
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
