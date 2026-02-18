# ================================================================
#  YKS RANK GRINDER — Production Ready
#  Local: SQLite  |  Web: PostgreSQL (otomatik seçim)
# ================================================================

import os
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'local-test-gizli-anahtar-2024')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ╔══════════════════════════════════════════╗
# ║     VERİTABANI KATMANI                  ║
# ║  Local  → SQLite  (yks_rank.db dosyası) ║
# ║  Web    → PostgreSQL (Render.com)       ║
# ╚══════════════════════════════════════════╝

DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Render.com "postgres://" verir ama Python "postgresql://" ister
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_POSTGRES = DATABASE_URL.startswith('postgresql')

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    print("✅ PostgreSQL modunda çalışıyor (WEB)")
else:
    import sqlite3
    print("✅ SQLite modunda çalışıyor (LOCAL)")


def get_db():
    """Veritabanı bağlantısı al."""
    if 'db' not in g:
        if USE_POSTGRES:
            g.db = psycopg2.connect(DATABASE_URL)
            g.db.autocommit = False
        else:
            g.db = sqlite3.connect('yks_rank.db')
            g.db.row_factory = sqlite3.Row
    return g.db


def q(query):
    """SQLite ? → PostgreSQL %s dönüştür."""
    if USE_POSTGRES:
        return query.replace('?', '%s')
    return query


def db_execute(query, params=None):
    """SQL çalıştır (SELECT dışı: INSERT, UPDATE, DELETE)."""
    db = get_db()
    query = q(query)
    if USE_POSTGRES:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = db.cursor()
    cur.execute(query, params or ())
    return cur


def db_fetchone(query, params=None):
    """Tek satır getir."""
    cur = db_execute(query, params)
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    return dict(row)


def db_fetchall(query, params=None):
    """Tüm satırları getir."""
    cur = db_execute(query, params)
    rows = cur.fetchall()
    cur.close()
    return [dict(r) for r in rows]


def db_commit():
    """Değişiklikleri kaydet."""
    db = get_db()
    db.commit()


@app.teardown_appcontext
def close_db(exception):
    """İstek bitince bağlantıyı kapat."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ╔══════════════════════════════════════════╗
# ║     TABLOLARI OLUŞTUR                   ║
# ╚══════════════════════════════════════════╝

def init_db():
    """Tüm tabloları oluştur (yoksa)."""
    db = get_db()

    if USE_POSTGRES:
        # PostgreSQL syntax
        tables_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id                 SERIAL PRIMARY KEY,
            username           TEXT UNIQUE NOT NULL,
            password_hash      TEXT NOT NULL,
            profile_photo      TEXT DEFAULT 'default.png',
            profile_banner     TEXT DEFAULT '',
            theme              TEXT DEFAULT 'lol-classic',
            daily_goal_minutes INTEGER DEFAULT 360,
            target_university  TEXT DEFAULT '',
            target_mat_net     REAL DEFAULT 0,
            target_fiz_net     REAL DEFAULT 0,
            target_kim_net     REAL DEFAULT 0,
            target_bio_net     REAL DEFAULT 0,
            total_lp           INTEGER DEFAULT 0,
            goals_set          INTEGER DEFAULT 0,
            pomodoro_work      INTEGER DEFAULT 25,
            pomodoro_break     INTEGER DEFAULT 5,
            created_at         TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id                SERIAL PRIMARY KEY,
            user_id           INTEGER NOT NULL,
            subject           TEXT NOT NULL,
            topic             TEXT NOT NULL,
            duration_minutes  INTEGER NOT NULL,
            lp_earned         INTEGER NOT NULL,
            is_pomodoro       INTEGER DEFAULT 0,
            pomodoro_cycles   INTEGER DEFAULT 0,
            session_date      DATE NOT NULL,
            created_at        TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS deneme_results (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            mat_net     REAL DEFAULT 0,
            fiz_net     REAL DEFAULT 0,
            kim_net     REAL DEFAULT 0,
            bio_net     REAL DEFAULT 0,
            total_net   REAL DEFAULT 0,
            lp_earned   INTEGER DEFAULT 0,
            deneme_date DATE NOT NULL,
            created_at  TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS daily_checks (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER NOT NULL,
            check_date    DATE NOT NULL,
            total_minutes INTEGER DEFAULT 0,
            goal_met      INTEGER DEFAULT 0,
            lp_change     INTEGER DEFAULT 0,
            processed     INTEGER DEFAULT 0,
            UNIQUE(user_id, check_date)
        );

        CREATE TABLE IF NOT EXISTS friendships (
            id          SERIAL PRIMARY KEY,
            sender_id   INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status      TEXT DEFAULT 'pending',
            created_at  TIMESTAMP DEFAULT NOW(),
            UNIQUE(sender_id, receiver_id)
        );

        CREATE TABLE IF NOT EXISTS user_achievements (
            id             SERIAL PRIMARY KEY,
            user_id        INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            earned_at      TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            ntype      TEXT NOT NULL,
            message    TEXT NOT NULL,
            icon       TEXT DEFAULT '🔔',
            is_read    INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS weekly_badges (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            badge_type  TEXT NOT NULL,
            badge_name  TEXT NOT NULL,
            badge_icon  TEXT NOT NULL,
            week_start  DATE NOT NULL,
            week_end    DATE NOT NULL,
            stat_value  TEXT DEFAULT '',
            created_at  TIMESTAMP DEFAULT NOW()
        );
        """
        cur = db.cursor()
        cur.execute(tables_sql)
        cur.close()

    else:
        # SQLite syntax
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            username           TEXT UNIQUE NOT NULL,
            password_hash      TEXT NOT NULL,
            profile_photo      TEXT DEFAULT 'default.png',
            profile_banner     TEXT DEFAULT '',
            theme              TEXT DEFAULT 'lol-classic',
            daily_goal_minutes INTEGER DEFAULT 360,
            target_university  TEXT DEFAULT '',
            target_mat_net     REAL DEFAULT 0,
            target_fiz_net     REAL DEFAULT 0,
            target_kim_net     REAL DEFAULT 0,
            target_bio_net     REAL DEFAULT 0,
            total_lp           INTEGER DEFAULT 0,
            goals_set          INTEGER DEFAULT 0,
            pomodoro_work      INTEGER DEFAULT 25,
            pomodoro_break     INTEGER DEFAULT 5,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            subject           TEXT NOT NULL,
            topic             TEXT NOT NULL,
            duration_minutes  INTEGER NOT NULL,
            lp_earned         INTEGER NOT NULL,
            is_pomodoro       INTEGER DEFAULT 0,
            pomodoro_cycles   INTEGER DEFAULT 0,
            session_date      DATE NOT NULL,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS deneme_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            mat_net     REAL DEFAULT 0,
            fiz_net     REAL DEFAULT 0,
            kim_net     REAL DEFAULT 0,
            bio_net     REAL DEFAULT 0,
            total_net   REAL DEFAULT 0,
            lp_earned   INTEGER DEFAULT 0,
            deneme_date DATE NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_checks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            check_date    DATE NOT NULL,
            total_minutes INTEGER DEFAULT 0,
            goal_met      INTEGER DEFAULT 0,
            lp_change     INTEGER DEFAULT 0,
            processed     INTEGER DEFAULT 0,
            UNIQUE(user_id, check_date)
        );

        CREATE TABLE IF NOT EXISTS friendships (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status      TEXT DEFAULT 'pending',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sender_id, receiver_id)
        );

        CREATE TABLE IF NOT EXISTS user_achievements (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            earned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            ntype      TEXT NOT NULL,
            message    TEXT NOT NULL,
            icon       TEXT DEFAULT '🔔',
            is_read    INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS weekly_badges (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            badge_type  TEXT NOT NULL,
            badge_name  TEXT NOT NULL,
            badge_icon  TEXT NOT NULL,
            week_start  DATE NOT NULL,
            week_end    DATE NOT NULL,
            stat_value  TEXT DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    db_commit()
    print("✅ Veritabanı tabloları hazır!")


# ╔══════════════════════════════════════════╗
# ║     SABİTLER                            ║
# ╚══════════════════════════════════════════╝

RANKS = [
    {'name':'Demir',      'min_lp':0,     'color':'#5c5c5c','glow':'#3a3a3a','img':'iron.png',       'icon':'⚔️'},
    {'name':'Bronz',      'min_lp':1000,  'color':'#cd7f32','glow':'#8b5e20','img':'bronze.png',     'icon':'🛡️'},
    {'name':'Gümüş',     'min_lp':2500,  'color':'#c0c0c0','glow':'#8a8a8a','img':'silver.png',     'icon':'⚡'},
    {'name':'Altın',     'min_lp':5000,  'color':'#ffd700','glow':'#b8960f','img':'gold.png',       'icon':'👑'},
    {'name':'Platin',     'min_lp':8000,  'color':'#00cec9','glow':'#00a8a3','img':'platinum.png',   'icon':'💎'},
    {'name':'Zümrüt',    'min_lp':12000, 'color':'#00b894','glow':'#009a7b','img':'emerald.png',    'icon':'🔮'},
    {'name':'Elmas',      'min_lp':17000, 'color':'#74b9ff','glow':'#4a90d9','img':'diamond.png',    'icon':'💠'},
    {'name':'Ustalık',   'min_lp':23000, 'color':'#a29bfe','glow':'#7c74d4','img':'master.png',     'icon':'🏆'},
    {'name':'Üstatlık',  'min_lp':30000, 'color':'#fd79a8','glow':'#d4507e','img':'grandmaster.png','icon':'🌟'},
    {'name':'Challenger', 'min_lp':40000, 'color':'#fdcb6e','glow':'#e6b04a','img':'challenger.png', 'icon':'🔥'},
]

THEMES = [
    {'id':'lol-classic',  'name':'LoL Classic',  'icon':'🎮','preview':['#0a0e13','#c89b3c','#0ac8b9']},
    {'id':'arcade',       'name':'Arcade',       'icon':'🕹️','preview':['#0d0221','#ff00ff','#00ffff']},
    {'id':'ocean',        'name':'Okyanus',      'icon':'🌊','preview':['#0a1628','#00b4d8','#48cae4']},
    {'id':'forest',       'name':'Orman',        'icon':'🌲','preview':['#0a1a0a','#88cc44','#44bb88']},
    {'id':'sunset',       'name':'Gün Batımı',  'icon':'🌅','preview':['#1a0e08','#ff6b35','#f7c948']},
    {'id':'cyberpunk',    'name':'Cyberpunk',    'icon':'💜','preview':['#0a0a1a','#ff2a6d','#05d9e8']},
    {'id':'valorant',     'name':'Valorant',     'icon':'🔴','preview':['#0f1012','#ff4655','#bd3944']},
    {'id':'snowdown',     'name':'Kış',         'icon':'❄️','preview':['#0a1520','#88ccff','#44aadd']},
    {'id':'star-guardian','name':'Yıldız',      'icon':'⭐','preview':['#1a0e20','#ee77aa','#aa77ee']},
]

ACHIEVEMENTS = [
    {'id':'first_session','name':'İlk Adım','desc':'İlk çalışma oturumu','icon':'🎯','lp':50,'category':'study'},
    {'id':'hour_1','name':'Isınma Turu','desc':'1 saat çalış','icon':'⏰','lp':100,'category':'study'},
    {'id':'hour_10','name':'Çalışkan Arı','desc':'10 saat çalış','icon':'🐝','lp':200,'category':'study'},
    {'id':'hour_50','name':'Azimli Savaşçı','desc':'50 saat çalış','icon':'⚔️','lp':400,'category':'study'},
    {'id':'hour_100','name':'Efsane','desc':'100 saat çalış','icon':'🏛️','lp':500,'category':'study'},
    {'id':'hour_200','name':'Tanrı Seviyesi','desc':'200 saat çalış','icon':'👁️','lp':500,'category':'study'},
    {'id':'streak_3','name':'Üçleme','desc':'3 gün seri','icon':'🔥','lp':50,'category':'streak'},
    {'id':'streak_7','name':'Haftalık Boss','desc':'7 gün seri','icon':'💪','lp':150,'category':'streak'},
    {'id':'streak_14','name':'İki Hafta Canavarı','desc':'14 gün seri','icon':'🦁','lp':300,'category':'streak'},
    {'id':'streak_30','name':'Ay Tanrısı','desc':'30 gün seri','icon':'🌙','lp':500,'category':'streak'},
    {'id':'pomo_1','name':'İlk Pomodoro','desc':'İlk pomodoro','icon':'🍅','lp':50,'category':'pomodoro'},
    {'id':'pomo_25','name':'Pomodoro Avcısı','desc':'25 pomodoro','icon':'🍅','lp':150,'category':'pomodoro'},
    {'id':'pomo_100','name':'Pomodoro Ustası','desc':'100 pomodoro','icon':'🍅','lp':300,'category':'pomodoro'},
    {'id':'deneme_1','name':'İlk Deneme','desc':'İlk deneme girişi','icon':'📝','lp':50,'category':'deneme'},
    {'id':'deneme_5','name':'Deneme Gazisi','desc':'5 deneme','icon':'📊','lp':150,'category':'deneme'},
    {'id':'deneme_target','name':'Hedef Vuruldu!','desc':'Hedef netine ulaş','icon':'🎯','lp':300,'category':'deneme'},
    {'id':'first_friend','name':'Yol Arkadaşı','desc':'İlk arkadaş','icon':'🤝','lp':50,'category':'social'},
    {'id':'friends_5','name':'Ekip Kuruldu','desc':'5 arkadaş','icon':'👥','lp':100,'category':'social'},
    {'id':'weekly_champ','name':'Haftalık Şampiyon','desc':'Haftanın en iyisi ol','icon':'🏆','lp':200,'category':'weekly'},
    {'id':'rank_bronze','name':'Bronz','desc':'Bronz rütbesi','icon':'🛡️','lp':0,'category':'rank'},
    {'id':'rank_silver','name':'Gümüş','desc':'Gümüş rütbesi','icon':'⚡','lp':0,'category':'rank'},
    {'id':'rank_gold','name':'Altın','desc':'Altın rütbesi','icon':'👑','lp':0,'category':'rank'},
    {'id':'rank_platinum','name':'Platin','desc':'Platin rütbesi','icon':'💎','lp':0,'category':'rank'},
    {'id':'rank_emerald','name':'Zümrüt','desc':'Zümrüt rütbesi','icon':'🔮','lp':0,'category':'rank'},
    {'id':'rank_diamond','name':'Elmas','desc':'Elmas rütbesi','icon':'💠','lp':0,'category':'rank'},
    {'id':'rank_master','name':'Ustalık','desc':'Ustalık rütbesi','icon':'🏆','lp':0,'category':'rank'},
    {'id':'rank_grandmaster','name':'Üstatlık','desc':'Üstatlık rütbesi','icon':'🌟','lp':0,'category':'rank'},
    {'id':'rank_challenger','name':'Challenger!','desc':'Challenger ol!','icon':'🔥','lp':0,'category':'rank'},
]
ACHIEVEMENT_MAP = {a['id']:a for a in ACHIEVEMENTS}

AYT_TOPICS = {
    'Matematik':['Temel Kavramlar','Sayı Basamakları','Bölme ve Bölünebilme','EBOB-EKOK','Rasyonel Sayılar','Basit Eşitsizlikler','Mutlak Değer','Üslü Sayılar','Köklü Sayılar','Çarpanlara Ayırma','Oran Orantı','Denklem Çözme','Problemler (Sayı-Kesir-Yaş)','Problemler (İşçi-Havuz-Yüzde)','Problemler (Kar-Zarar-Hareket)','Kümeler','Fonksiyonlar','Polinomlar','2. Derece Denklemler','Permütasyon Kombinasyon','Binom','Olasılık','İstatistik','Logaritma','Diziler Seriler','Limit Süreklilik','Türev','İntegral','Trigonometri','Analitik Geometri','Karmaşık Sayılar'],
    'Fizik':['Vektörler','Kuvvet Denge','Tork','Düzgün Doğrusal Hareket','Düzgün İvmeli Hareket','Newton Yasaları','İş Güç Enerji','İtme Momentum','Elektrik Alan','Paralel Levhalar Sığa','Manyetizma','İndüksiyon','Alternatif Akım','Dalga Mekaniği','Atom Fiziği','Radyoaktivite','Basınç Kaldırma','Optik'],
    'Kimya':['Atom Periyodik Sistem','Kimyasal Etkileşimler','Maddenin Halleri','Mol Stokiyometri','Kimyasal Tepkimeler','Asit Baz','Karışımlar','Çözeltiler Derişim','Kimyasal Denge','Termokimya','Tepkime Hızları','Elektrokimya','Organik Kimya','Çekirdek Kimyası'],
    'Biyoloji':['Hücre Organeller','Hücre Bölünmeleri','Kalıtım','Ekosistem','Bitki Biyolojisi','Enerji Dönüşümleri','Sindirim','Dolaşım Bağışıklık','Solunum','Boşaltım','Sinir Sistemi','Endokrin','Duyu Organları','Destek Hareket','Üreme Gelişme','Komünite Popülasyon','Sınıflandırma'],
}
SUBJECT_ICONS = {'Matematik':'📐','Fizik':'⚡','Kimya':'🧪','Biyoloji':'🧬'}


# ╔══════════════════════════════════════════╗
# ║     YARDIMCI FONKSİYONLAR               ║
# ╚══════════════════════════════════════════╝

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

def get_rank(lp):
    cur = RANKS[0]
    for r in RANKS:
        if lp >= r['min_lp']: cur = r
        else: break
    return cur

def get_next_rank(lp):
    for r in RANKS:
        if lp < r['min_lp']: return r
    return None

def rank_progress(lp):
    cur=get_rank(lp); nxt=get_next_rank(lp)
    if not nxt: return 100
    t=nxt['min_lp']-cur['min_lp']; d=lp-cur['min_lp']
    return int(d/t*100) if t else 100

def login_required(f):
    @wraps(f)
    def wrapper(*a,**kw):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.','warning')
            return redirect(url_for('login'))
        return f(*a,**kw)
    return wrapper

def get_photo_url(photo_value):
    if not photo_value or photo_value == 'default.png':
        return None
    if photo_value.startswith('http'):
        return photo_value
    return url_for('static', filename='uploads/' + photo_value)

def add_notification(user_id, ntype, message, icon='🔔'):
    db_execute('INSERT INTO notifications(user_id,ntype,message,icon) VALUES(?,?,?,?)',
               (user_id, ntype, message, icon))

def get_streak(user_id):
    user = db_fetchone('SELECT daily_goal_minutes FROM users WHERE id=?',(user_id,))
    if not user: return 0
    goal = user['daily_goal_minutes']
    streak = 0
    d = date.today() - timedelta(days=1)
    while True:
        r = db_fetchone(
            'SELECT COALESCE(SUM(duration_minutes),0) as t '
            'FROM study_sessions WHERE user_id=? AND session_date=?',
            (user_id, d.isoformat()))
        if r and r['t'] >= goal:
            streak += 1; d -= timedelta(days=1)
        else:
            break
    return streak

def get_friend_count(user_id):
    r = db_fetchone(
        "SELECT COUNT(*) as c FROM friendships "
        "WHERE (sender_id=? OR receiver_id=?) AND status='accepted'",
        (user_id, user_id))
    return r['c'] if r else 0


# ╔══════════════════════════════════════════╗
# ║     HAFTALIK ROZET SİSTEMİ              ║
# ╚══════════════════════════════════════════╝

def process_weekly_badges():
    today = date.today()
    if today.weekday() != 0:  # Sadece Pazartesi
        return
    week_end   = today - timedelta(days=1)
    week_start = week_end - timedelta(days=6)

    existing = db_fetchone('SELECT id FROM weekly_badges WHERE week_start=? LIMIT 1',
                           (week_start.isoformat(),))
    if existing:
        return

    top_study = db_fetchone(
        'SELECT user_id, SUM(duration_minutes) as total '
        'FROM study_sessions WHERE session_date BETWEEN ? AND ? '
        'GROUP BY user_id ORDER BY total DESC LIMIT 1',
        (week_start.isoformat(), week_end.isoformat()))

    top_pomo = db_fetchone(
        'SELECT user_id, SUM(pomodoro_cycles) as total '
        'FROM study_sessions WHERE session_date BETWEEN ? AND ? AND is_pomodoro=1 '
        'GROUP BY user_id ORDER BY total DESC LIMIT 1',
        (week_start.isoformat(), week_end.isoformat()))

    top_deneme = db_fetchone(
        'SELECT user_id, MAX(total_net) as total '
        'FROM deneme_results WHERE deneme_date BETWEEN ? AND ? '
        'GROUP BY user_id ORDER BY total DESC LIMIT 1',
        (week_start.isoformat(), week_end.isoformat()))

    top_lp = db_fetchone(
        'SELECT user_id, SUM(lp_earned) as total '
        'FROM study_sessions WHERE session_date BETWEEN ? AND ? '
        'GROUP BY user_id ORDER BY total DESC LIMIT 1',
        (week_start.isoformat(), week_end.isoformat()))

    badge_data = [
        (top_study,  'top_study',  '👑 Çalışma Kralı',    '👑'),
        (top_pomo,   'top_pomo',   '🍅 Pomodoro Ustası',  '🍅'),
        (top_deneme, 'top_deneme', '📊 Deneme Şampiyonu', '📊'),
        (top_lp,     'top_lp',     '⚡ LP Avcısı',        '⚡'),
    ]

    for winner, btype, bname, bicon in badge_data:
        if winner and winner.get('user_id'):
            stat = str(winner.get('total', ''))
            db_execute(
                'INSERT INTO weekly_badges(user_id,badge_type,badge_name,badge_icon,week_start,week_end,stat_value) '
                'VALUES(?,?,?,?,?,?,?)',
                (winner['user_id'], btype, bname, bicon,
                 week_start.isoformat(), week_end.isoformat(), stat))
            add_notification(winner['user_id'], 'weekly_badge',
                f'{bicon} Haftalık rozet: {bname}! +200 LP', bicon)
            db_execute('UPDATE users SET total_lp=total_lp+200 WHERE id=?',
                       (winner['user_id'],))
    db_commit()


# ╔══════════════════════════════════════════╗
# ║     BAŞARIM KONTROLÜ                    ║
# ╚══════════════════════════════════════════╝

def check_achievements(user_id):
    earned = {r['achievement_id'] for r in db_fetchall(
        'SELECT achievement_id FROM user_achievements WHERE user_id=?',(user_id,))}
    user = db_fetchone('SELECT * FROM users WHERE id=?',(user_id,))
    if not user: return []
    new_achs = []

    ts = db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',(user_id,))['c']
    tm = db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(user_id,))['t']
    th = tm / 60
    tp = db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',(user_id,))['t']
    td = db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',(user_id,))['c']
    streak = get_streak(user_id)
    friends = get_friend_count(user_id)
    lp = user['total_lp']
    hw = db_fetchone('SELECT id FROM weekly_badges WHERE user_id=? LIMIT 1',(user_id,))

    checks = {
        'first_session':ts>=1,'hour_1':th>=1,'hour_10':th>=10,'hour_50':th>=50,
        'hour_100':th>=100,'hour_200':th>=200,
        'streak_3':streak>=3,'streak_7':streak>=7,'streak_14':streak>=14,'streak_30':streak>=30,
        'pomo_1':tp>=1,'pomo_25':tp>=25,'pomo_100':tp>=100,
        'deneme_1':td>=1,'deneme_5':td>=5,
        'first_friend':friends>=1,'friends_5':friends>=5,
        'weekly_champ':bool(hw),
        'rank_bronze':lp>=1000,'rank_silver':lp>=2500,'rank_gold':lp>=5000,
        'rank_platinum':lp>=8000,'rank_emerald':lp>=12000,'rank_diamond':lp>=17000,
        'rank_master':lp>=23000,'rank_grandmaster':lp>=30000,'rank_challenger':lp>=40000,
    }

    if 'deneme_target' not in earned:
        tgt = user['target_mat_net']+user['target_fiz_net']+user['target_kim_net']+user['target_bio_net']
        if tgt > 0:
            best = db_fetchone('SELECT MAX(total_net) as m FROM deneme_results WHERE user_id=?',(user_id,))
            if best and best['m'] and best['m'] >= tgt:
                checks['deneme_target'] = True

    for aid, cond in checks.items():
        if aid not in earned and cond and aid in ACHIEVEMENT_MAP:
            a = ACHIEVEMENT_MAP[aid]
            db_execute('INSERT INTO user_achievements(user_id,achievement_id) VALUES(?,?)',(user_id,aid))
            if a['lp'] > 0:
                db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(a['lp'],user_id))
            add_notification(user_id,'achievement',f"🏅 {a['name']}: {a['desc']} (+{a['lp']} LP)",a['icon'])
            new_achs.append(a)
    db_commit()
    return new_achs


# ╔══════════════════════════════════════════╗
# ║     GÜNLÜK KONTROL                      ║
# ╚══════════════════════════════════════════╝

def check_daily_goals(user_id):
    user = db_fetchone('SELECT * FROM users WHERE id=?',(user_id,))
    if not user or not user['goals_set']: return

    today = date.today()
    process_weekly_badges()

    try: created = datetime.strptime(str(user['created_at'])[:10],'%Y-%m-%d').date()
    except: created = today - timedelta(days=60)

    max_fn = 'GREATEST' if USE_POSTGRES else 'MAX'

    for i in range(1, 8):
        d = today - timedelta(days=i)
        if d < created: continue
        exists = db_fetchone('SELECT * FROM daily_checks WHERE user_id=? AND check_date=?',
                             (user_id, d.isoformat()))
        if exists and exists['processed']: continue

        mins = db_fetchone(
            'SELECT COALESCE(SUM(duration_minutes),0) as t '
            'FROM study_sessions WHERE user_id=? AND session_date=?',
            (user_id, d.isoformat()))['t']
        goal = user['daily_goal_minutes']

        if mins >= goal:
            lp_ch, met = 200, 1
        elif mins > 0:
            lp_ch = max(-int((goal-mins)/goal*30), -30)
            met = 0
        else:
            lp_ch, met = -20, 0

        if exists:
            db_execute(
                'UPDATE daily_checks SET total_minutes=?,goal_met=?,lp_change=?,processed=1 WHERE id=?',
                (mins, met, lp_ch, exists['id']))
        else:
            db_execute(
                'INSERT INTO daily_checks(user_id,check_date,total_minutes,goal_met,lp_change,processed) '
                'VALUES(?,?,?,?,?,1)',
                (user_id, d.isoformat(), mins, met, lp_ch))

        db_execute(
            f'UPDATE users SET total_lp={max_fn}(0,total_lp+?) WHERE id=?',
            (lp_ch, user_id))

    streak = get_streak(user_id)
    for s_days, s_lp in {3:50, 7:150, 14:300, 30:500}.items():
        if streak == s_days:
            db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(s_lp,user_id))
            add_notification(user_id,'streak',f'🔥 {s_days} gün seri! +{s_lp} LP!','🔥')

    check_achievements(user_id)
    db_commit()


# ╔══════════════════════════════════════════╗
# ║     CONTEXT PROCESSOR                   ║
# ╚══════════════════════════════════════════╝

@app.context_processor
def inject_globals():
    unread = 0
    if 'user_id' in session:
        r = db_fetchone('SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND is_read=0',
                        (session['user_id'],))
        unread = r['c'] if r else 0
    return {
        'current_theme': session.get('theme','lol-classic'),
        'all_themes': THEMES,
        'all_ranks': RANKS,
        'unread_notifs': unread,
        'get_photo_url': get_photo_url,
        'get_rank': get_rank,
    }


# ╔══════════════════════════════════════════════════════╗
# ║     TÜM ROTALAR                                    ║
# ╚══════════════════════════════════════════════════════╝

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

# ── KAYIT ──
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        uname = request.form.get('username','').strip()
        pw    = request.form.get('password','')
        pw2   = request.form.get('password_confirm','')

        if not uname or not pw:
            flash('Kullanıcı adı ve şifre gerekli.','error')
            return redirect(url_for('register'))
        if len(uname) < 3:
            flash('En az 3 karakter.','error')
            return redirect(url_for('register'))
        if len(pw) < 6:
            flash('Şifre en az 6 karakter.','error')
            return redirect(url_for('register'))
        if pw != pw2:
            flash('Şifreler eşleşmiyor.','error')
            return redirect(url_for('register'))
        if db_fetchone('SELECT 1 FROM users WHERE username=?',(uname,)):
            flash('Bu isim alınmış.','error')
            return redirect(url_for('register'))

        db_execute(
            'INSERT INTO users(username,password_hash) VALUES(?,?)',
            (uname, generate_password_hash(pw)))
        db_commit()
        user = db_fetchone('SELECT id FROM users WHERE username=?',(uname,))
        session['user_id'] = user['id']
        session['username'] = uname
        session['theme'] = 'lol-classic'
        flash('Kayıt başarılı!','success')
        return redirect(url_for('setup_goals'))

    return render_template('register.html')

# ── GİRİŞ ──
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username','').strip()
        pw    = request.form.get('password','')
        user  = db_fetchone('SELECT * FROM users WHERE username=?',(uname,))

        if user and check_password_hash(user['password_hash'], pw):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['theme']    = user.get('theme','lol-classic')
            check_daily_goals(user['id'])
            if not user['goals_set']:
                return redirect(url_for('setup_goals'))
            flash(f'Hoş geldin, {uname}! 🎮','success')
            return redirect(url_for('dashboard'))

        flash('Hatalı bilgiler.','error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.','info')
    return redirect(url_for('login'))

# ── HEDEFLER ──
@app.route('/setup-goals', methods=['GET','POST'])
@login_required
def setup_goals():
    if request.method == 'POST':
        hrs  = float(request.form.get('daily_hours',6))
        uni  = request.form.get('target_university','')
        mn   = float(request.form.get('target_mat_net',0))
        fn   = float(request.form.get('target_fiz_net',0))
        kn   = float(request.form.get('target_kim_net',0))
        bn   = float(request.form.get('target_bio_net',0))
        db_execute(
            'UPDATE users SET daily_goal_minutes=?,target_university=?,'
            'target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,'
            'goals_set=1 WHERE id=?',
            (int(hrs*60),uni,mn,fn,kn,bn,session['user_id']))
        db_commit()
        flash('Hedefler kaydedildi! 🚀','success')
        return redirect(url_for('dashboard'))
    return render_template('setup_goals.html')

# ── TEMA ──
@app.route('/api/set-theme', methods=['POST'])
@login_required
def set_theme():
    tid = request.get_json().get('theme','lol-classic')
    if tid not in [t['id'] for t in THEMES]:
        return jsonify(success=False)
    db_execute('UPDATE users SET theme=? WHERE id=?',(tid,session['user_id']))
    db_commit()
    session['theme'] = tid
    return jsonify(success=True)

# ── BİLDİRİMLER ──
@app.route('/api/notifications')
@login_required
def get_notifications():
    notifs = db_fetchall(
        'SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20',
        (session['user_id'],))
    db_execute('UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0',
               (session['user_id'],))
    db_commit()
    return jsonify(notifs)

# ── DASHBOARD ──
@app.route('/dashboard')
@login_required
def dashboard():
    check_daily_goals(session['user_id'])
    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    today_iso = date.today().isoformat()

    today_mins = db_fetchone(
        'SELECT COALESCE(SUM(duration_minutes),0) as t '
        'FROM study_sessions WHERE user_id=? AND session_date=?',
        (session['user_id'], today_iso))['t']
    total_mins = db_fetchone(
        'SELECT COALESCE(SUM(duration_minutes),0) as t '
        'FROM study_sessions WHERE user_id=?',
        (session['user_id'],))['t']
    today_pomos = db_fetchone(
        'SELECT COALESCE(SUM(pomodoro_cycles),0) as t '
        'FROM study_sessions WHERE user_id=? AND session_date=? AND is_pomodoro=1',
        (session['user_id'], today_iso))['t']
    last_deneme = db_fetchone(
        'SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 1',
        (session['user_id'],))

    weekly = []
    for i in range(6,-1,-1):
        d = date.today()-timedelta(days=i)
        m = db_fetchone(
            'SELECT COALESCE(SUM(duration_minutes),0) as t '
            'FROM study_sessions WHERE user_id=? AND session_date=?',
            (session['user_id'], d.isoformat()))['t']
        weekly.append({
            'label':['Pzt','Sal','Çar','Per','Cum','Cmt','Paz'][d.weekday()],
            'mins':m})

    subj_stats = db_fetchall(
        'SELECT subject, COALESCE(SUM(duration_minutes),0) as t '
        'FROM study_sessions WHERE user_id=? GROUP BY subject ORDER BY t DESC',
        (session['user_id'],))

    streak = get_streak(session['user_id'])

    recent_achs_raw = db_fetchall(
        'SELECT achievement_id, earned_at FROM user_achievements '
        'WHERE user_id=? ORDER BY earned_at DESC LIMIT 5',
        (session['user_id'],))
    recent_achs = [
        dict(ACHIEVEMENT_MAP.get(r['achievement_id'],{}), earned_at=r['earned_at'])
        for r in recent_achs_raw
        if r['achievement_id'] in ACHIEVEMENT_MAP]

    lb_pos = db_fetchone(
        'SELECT COUNT(*)+1 as pos FROM users '
        'WHERE total_lp > (SELECT total_lp FROM users WHERE id=?)',
        (session['user_id'],))['pos']
    total_users = db_fetchone('SELECT COUNT(*) as c FROM users')['c']

    pending_requests = db_fetchall(
        'SELECT f.id, u.username, u.profile_photo, u.total_lp '
        'FROM friendships f JOIN users u ON u.id=f.sender_id '
        "WHERE f.receiver_id=? AND f.status='pending'",
        (session['user_id'],))

    my_badges = db_fetchall(
        'SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC LIMIT 10',
        (session['user_id'],))

    r    = get_rank(user['total_lp'])
    nr   = get_next_rank(user['total_lp'])
    prog = rank_progress(user['total_lp'])

    return render_template('dashboard.html',
        user=user, rank=r, next_rank=nr, rank_progress=prog,
        today_mins=today_mins, total_mins=total_mins,
        today_pomodoros=today_pomos, last_deneme=last_deneme,
        weekly=weekly, subj_stats=subj_stats, streak=streak,
        subject_icons=SUBJECT_ICONS, recent_achievements=recent_achs,
        lb_position=lb_pos, total_users=total_users,
        pending_requests=pending_requests, my_badges=my_badges)

# ── ÇALIŞMA ──
@app.route('/study')
@login_required
def study():
    return render_template('study.html', subjects=AYT_TOPICS, icons=SUBJECT_ICONS)

@app.route('/study/<subject>')
@login_required
def study_subject(subject):
    if subject not in AYT_TOPICS:
        flash('Geçersiz.','error'); return redirect(url_for('study'))
    return render_template('study_topics.html',
        subject=subject, topics=AYT_TOPICS[subject],
        icon=SUBJECT_ICONS.get(subject,'📚'))

@app.route('/study/<subject>/<int:tidx>')
@login_required
def study_timer(subject, tidx):
    if subject not in AYT_TOPICS or tidx >= len(AYT_TOPICS[subject]):
        flash('Geçersiz.','error'); return redirect(url_for('study'))
    user = db_fetchone('SELECT pomodoro_work, pomodoro_break FROM users WHERE id=?',
                       (session['user_id'],))
    return render_template('timer.html',
        subject=subject, topic=AYT_TOPICS[subject][tidx],
        icon=SUBJECT_ICONS.get(subject,'📚'),
        pomo_work=user['pomodoro_work'] or 25,
        pomo_break=user['pomodoro_break'] or 5)

# ── ÇALIŞMA KAYDET ──
@app.route('/api/save-session', methods=['POST'])
@login_required
def save_session():
    data = request.get_json()
    subj = data.get('subject','')
    topic = data.get('topic','')
    mins = int(data.get('duration_minutes',0))
    is_pomo = int(data.get('is_pomodoro',0))
    pomo_cycles = int(data.get('pomodoro_cycles',0))

    if mins < 1:
        return jsonify(success=False, message='En az 1 dakika!')

    lp = (mins * 2) + (pomo_cycles * 15 if is_pomo else 0)

    old_lp = db_fetchone('SELECT total_lp FROM users WHERE id=?',
                         (session['user_id'],))['total_lp']
    old_rank = get_rank(old_lp)

    db_execute(
        'INSERT INTO study_sessions'
        '(user_id,subject,topic,duration_minutes,lp_earned,is_pomodoro,pomodoro_cycles,session_date) '
        'VALUES(?,?,?,?,?,?,?,?)',
        (session['user_id'], subj, topic, mins, lp, is_pomo, pomo_cycles,
         date.today().isoformat()))
    db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',
               (lp, session['user_id']))

    user = db_fetchone('SELECT total_lp FROM users WHERE id=?',
                       (session['user_id'],))
    new_rank = get_rank(user['total_lp'])
    rank_up = old_rank['name'] != new_rank['name']

    if rank_up:
        add_notification(session['user_id'], 'rankup',
            f"🎉 {new_rank['name']} rütbesine yükseldin!", new_rank['icon'])

    new_achs = check_achievements(session['user_id'])
    db_commit()

    return jsonify(
        success=True, lp_earned=lp, total_lp=user['total_lp'],
        rank=new_rank['name'], rank_img=new_rank['img'],
        rank_color=new_rank['color'], rank_up=rank_up,
        new_rank_name=new_rank['name'] if rank_up else None,
        new_achievements=[{'name':a['name'],'icon':a['icon'],'lp':a['lp']}
                          for a in new_achs],
        message=f'+{lp} LP! 🎉')

# ── DENEME ──
@app.route('/deneme', methods=['GET','POST'])
@login_required
def deneme():
    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    if request.method == 'POST':
        mn = float(request.form.get('mat_net',0))
        fn = float(request.form.get('fiz_net',0))
        kn = float(request.form.get('kim_net',0))
        bn = float(request.form.get('bio_net',0))
        dd = request.form.get('deneme_date', date.today().isoformat())
        tn = mn+fn+kn+bn
        tgt = user['target_mat_net']+user['target_fiz_net']+user['target_kim_net']+user['target_bio_net']
        lp = int((tn/tgt)*400) if tgt > 0 else int(tn*4)
        lp = max(0, min(lp, 800))

        db_execute(
            'INSERT INTO deneme_results'
            '(user_id,mat_net,fiz_net,kim_net,bio_net,total_net,lp_earned,deneme_date) '
            'VALUES(?,?,?,?,?,?,?,?)',
            (session['user_id'],mn,fn,kn,bn,tn,lp,dd))
        db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',
                   (lp, session['user_id']))
        check_achievements(session['user_id'])
        db_commit()
        flash(f'Deneme kaydedildi! +{lp} LP','success')
        return redirect(url_for('deneme'))

    hist = db_fetchall(
        'SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 20',
        (session['user_id'],))
    return render_template('deneme.html', user=user, history=hist)

# ── PROFİL ──
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Profil fotoğrafı (GIF dahil)
        if 'profile_photo' in request.files:
            f = request.files['profile_photo']
            if f and f.filename and allowed_file(f.filename):
                fn = secure_filename(
                    f"u{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db_execute('UPDATE users SET profile_photo=? WHERE id=?',
                           (fn, session['user_id']))
                db_commit()
                flash('Fotoğraf güncellendi! 📸','success')

        # Banner (GIF dahil)
        if 'profile_banner' in request.files:
            f = request.files['profile_banner']
            if f and f.filename and allowed_file(f.filename):
                fn = secure_filename(
                    f"banner_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db_execute('UPDATE users SET profile_banner=? WHERE id=?',
                           (fn, session['user_id']))
                db_commit()
                flash('Banner güncellendi! 🖼️','success')

        # Ayarlar
        if 'daily_hours' in request.form:
            hrs = float(request.form.get('daily_hours',6))
            uni = request.form.get('target_university','')
            mn  = float(request.form.get('target_mat_net',0))
            fn  = float(request.form.get('target_fiz_net',0))
            kn  = float(request.form.get('target_kim_net',0))
            bn  = float(request.form.get('target_bio_net',0))
            pw  = int(request.form.get('pomodoro_work',25))
            pb  = int(request.form.get('pomodoro_break',5))
            db_execute(
                'UPDATE users SET daily_goal_minutes=?,target_university=?,'
                'target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,'
                'pomodoro_work=?,pomodoro_break=? WHERE id=?',
                (int(hrs*60),uni,mn,fn,kn,bn,pw,pb,session['user_id']))
            db_commit()
            flash('Ayarlar güncellendi!','success')

    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    stats = {
        'sessions': db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',
                                (session['user_id'],))['c'],
        'total_mins': db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',
                                  (session['user_id'],))['t'],
        'denemes': db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',
                               (session['user_id'],))['c'],
        'active_days': db_fetchone('SELECT COUNT(DISTINCT session_date) as d FROM study_sessions WHERE user_id=?',
                                   (session['user_id'],))['d'],
        'pomodoros': db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',
                                 (session['user_id'],))['t'],
    }
    earned_ids = {a['achievement_id'] for a in db_fetchall(
        'SELECT achievement_id FROM user_achievements WHERE user_id=?',
        (session['user_id'],))}
    weekly_badges = db_fetchall(
        'SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC',
        (session['user_id'],))

    return render_template('profile.html',
        user=user, rank=get_rank(user['total_lp']), stats=stats,
        achievements=ACHIEVEMENTS, earned_ids=earned_ids,
        weekly_badges=weekly_badges)

# ── ARKADAŞLAR ──
@app.route('/friends')
@login_required
def friends():
    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    friend_rows = db_fetchall(
        'SELECT u.id,u.username,u.profile_photo,u.total_lp '
        'FROM friendships f '
        'JOIN users u ON (CASE WHEN f.sender_id=? THEN f.receiver_id ELSE f.sender_id END)=u.id '
        "WHERE (f.sender_id=? OR f.receiver_id=?) AND f.status='accepted' "
        'ORDER BY u.total_lp DESC',
        (session['user_id'], session['user_id'], session['user_id']))
    incoming = db_fetchall(
        'SELECT f.id as fid, u.id as uid, u.username, u.profile_photo, u.total_lp '
        'FROM friendships f JOIN users u ON u.id=f.sender_id '
        "WHERE f.receiver_id=? AND f.status='pending'",
        (session['user_id'],))
    outgoing = db_fetchall(
        'SELECT f.id as fid, u.id as uid, u.username, u.profile_photo, u.total_lp '
        'FROM friendships f JOIN users u ON u.id=f.receiver_id '
        "WHERE f.sender_id=? AND f.status='pending'",
        (session['user_id'],))

    return render_template('friends.html',
        user=user, rank=get_rank(user['total_lp']),
        friends=friend_rows, incoming=incoming, outgoing=outgoing)

@app.route('/api/add-friend', methods=['POST'])
@login_required
def add_friend():
    uname = request.get_json().get('username','').strip()
    if not uname:
        return jsonify(success=False, message='Kullanıcı adı gir.')
    target = db_fetchone('SELECT id FROM users WHERE username=?',(uname,))
    if not target:
        return jsonify(success=False, message='Kullanıcı bulunamadı.')
    if target['id'] == session['user_id']:
        return jsonify(success=False, message='Kendini ekleyemezsin 😄')
    existing = db_fetchone(
        'SELECT * FROM friendships WHERE '
        '(sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
        (session['user_id'],target['id'],target['id'],session['user_id']))
    if existing:
        if existing['status'] == 'accepted':
            return jsonify(success=False, message='Zaten arkadaşsınız!')
        return jsonify(success=False, message='İstek zaten gönderilmiş.')

    db_execute(
        "INSERT INTO friendships(sender_id,receiver_id,status) VALUES(?,?,'pending')",
        (session['user_id'], target['id']))
    add_notification(target['id'], 'friend_request',
        f'📩 {session["username"]} arkadaşlık isteği gönderdi!', '🤝')
    db_commit()
    return jsonify(success=True, message=f'{uname} kullanıcısına istek gönderildi! 🤝')

@app.route('/api/accept-friend', methods=['POST'])
@login_required
def accept_friend():
    fid = request.get_json().get('friendship_id')
    f = db_fetchone(
        "SELECT * FROM friendships WHERE id=? AND receiver_id=? AND status='pending'",
        (fid, session['user_id']))
    if not f:
        return jsonify(success=False, message='İstek bulunamadı.')
    db_execute("UPDATE friendships SET status='accepted' WHERE id=?",(fid,))
    add_notification(f['sender_id'], 'friend_accepted',
        f'✅ {session["username"]} isteğini kabul etti!', '🎉')
    check_achievements(session['user_id'])
    check_achievements(f['sender_id'])
    db_commit()
    return jsonify(success=True, message='Kabul edildi! 🎉')

@app.route('/api/reject-friend', methods=['POST'])
@login_required
def reject_friend():
    fid = request.get_json().get('friendship_id')
    db_execute('DELETE FROM friendships WHERE id=? AND receiver_id=?',
               (fid, session['user_id']))
    db_commit()
    return jsonify(success=True)

@app.route('/api/remove-friend', methods=['POST'])
@login_required
def remove_friend():
    uid = request.get_json().get('user_id')
    db_execute(
        'DELETE FROM friendships WHERE '
        '(sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
        (session['user_id'],uid,uid,session['user_id']))
    db_commit()
    return jsonify(success=True)

# ── LEADERBOARD ──
@app.route('/leaderboard')
@login_required
def leaderboard():
    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))

    global_lb = db_fetchall(
        'SELECT id,username,profile_photo,total_lp,'
        '(SELECT COALESCE(SUM(duration_minutes),0) FROM study_sessions WHERE user_id=users.id) as total_study '
        'FROM users ORDER BY total_lp DESC LIMIT 50')

    friend_ids_rows = db_fetchall(
        'SELECT CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END as fid '
        "FROM friendships WHERE (sender_id=? OR receiver_id=?) AND status='accepted'",
        (session['user_id'], session['user_id'], session['user_id']))
    fids = [f['fid'] for f in friend_ids_rows] + [session['user_id']]

    if len(fids) > 1:
        if USE_POSTGRES:
            ph = ','.join(['%s']*len(fids))
        else:
            ph = ','.join(['?']*len(fids))
        friends_lb = db_fetchall(
            f'SELECT id,username,profile_photo,total_lp,'
            f'(SELECT COALESCE(SUM(duration_minutes),0) FROM study_sessions WHERE user_id=users.id) as total_study '
            f'FROM users WHERE id IN ({ph}) ORDER BY total_lp DESC',
            fids)
    else:
        friends_lb = []

    today_iso = date.today().isoformat()
    today_lb = db_fetchall(
        'SELECT u.id,u.username,u.profile_photo,u.total_lp,'
        'COALESCE(SUM(s.duration_minutes),0) as today_mins '
        'FROM users u JOIN study_sessions s ON s.user_id=u.id AND s.session_date=? '
        'GROUP BY u.id,u.username,u.profile_photo,u.total_lp '
        'ORDER BY today_mins DESC LIMIT 20',
        (today_iso,))

    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    weekly_lb = db_fetchall(
        'SELECT u.id,u.username,u.profile_photo,u.total_lp,'
        'COALESCE(SUM(s.duration_minutes),0) as week_mins '
        'FROM users u JOIN study_sessions s ON s.user_id=u.id AND s.session_date>=? '
        'GROUP BY u.id,u.username,u.profile_photo,u.total_lp '
        'ORDER BY week_mins DESC LIMIT 20',
        (week_start,))

    recent_badges = db_fetchall(
        'SELECT wb.*,u.username,u.profile_photo '
        'FROM weekly_badges wb JOIN users u ON u.id=wb.user_id '
        'ORDER BY wb.week_start DESC LIMIT 20')

    my_pos = 1
    for i, u in enumerate(global_lb):
        if u['id'] == session['user_id']:
            my_pos = i + 1
            break

    return render_template('leaderboard.html',
        user=user, rank=get_rank(user['total_lp']),
        global_lb=global_lb, friends_lb=friends_lb,
        today_lb=today_lb, weekly_lb=weekly_lb,
        recent_badges=recent_badges, my_position=my_pos)

# ── İSTATİSTİK ──
@app.route('/stats')
@login_required
def stats():
    user = db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    subj_detail = {}
    for s in AYT_TOPICS:
        rows = db_fetchall(
            'SELECT topic, SUM(duration_minutes) as t, COUNT(*) as c '
            'FROM study_sessions WHERE user_id=? AND subject=? '
            'GROUP BY topic ORDER BY t DESC',
            (session['user_id'], s))
        tot = db_fetchone(
            'SELECT COALESCE(SUM(duration_minutes),0) as t '
            'FROM study_sessions WHERE user_id=? AND subject=?',
            (session['user_id'], s))['t']
        subj_detail[s] = {'topics': rows, 'total': tot}

    deneme_trend = db_fetchall(
        'SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date ASC LIMIT 30',
        (session['user_id'],))
    checks = db_fetchall(
        'SELECT * FROM daily_checks WHERE user_id=? AND processed=1 '
        'ORDER BY check_date DESC LIMIT 30',
        (session['user_id'],))
    met = sum(1 for c in checks if c['goal_met'])
    gpct = int(met/len(checks)*100) if checks else 0

    return render_template('stats.html',
        user=user, rank=get_rank(user['total_lp']),
        next_rank=get_next_rank(user['total_lp']),
        rank_progress=rank_progress(user['total_lp']),
        subj_detail=subj_detail, deneme_trend=deneme_trend,
        daily_checks=checks, goal_pct=gpct,
        subject_icons=SUBJECT_ICONS)


# ╔══════════════════════════════════════════╗
# ║     BAŞLAT                              ║
# ╚══════════════════════════════════════════╝

if __name__ == '__main__':
    # LOCAL çalıştırma
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/img/ranks', exist_ok=True)
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
else:
    # PRODUCTION (gunicorn ile)
    with app.app_context():
        init_db()
