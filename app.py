# ================================================================
<<<<<<< HEAD
#  YKS RANK GRINDER — Production Ready
#  Local: SQLite  |  Web: PostgreSQL (otomatik seçim)
=======
#  YKS RANK GRINDER v5.0
#  Chat + 30 Tema + Banner GIF + Username Change + Split LB
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
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
<<<<<<< HEAD
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
=======
app.secret_key = os.environ.get('SECRET_KEY', 'local-dev-key-2024')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXT = {'png','jpg','jpeg','gif','webp'}

# ═══════════════ DB KATMANI ═══════════════
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
USE_POSTGRES = DATABASE_URL.startswith('postgresql')

if USE_POSTGRES:
    import psycopg2, psycopg2.extras
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
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

<<<<<<< HEAD

def q(query):
    """SQLite ? → PostgreSQL %s dönüştür."""
    if USE_POSTGRES:
        return query.replace('?', '%s')
    return query


def db_execute(query, params=None):
    """SQL çalıştır (SELECT dışı: INSERT, UPDATE, DELETE)."""
=======
def q(query):
    return query.replace('?','%s') if USE_POSTGRES else query

def db_execute(query, params=None):
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
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
<<<<<<< HEAD
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    return dict(row)

=======
    row = cur.fetchone(); cur.close()
    return dict(row) if row else None
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

def db_fetchall(query, params=None):
    """Tüm satırları getir."""
    cur = db_execute(query, params)
    rows = cur.fetchall(); cur.close()
    return [dict(r) for r in rows]


def db_commit():
<<<<<<< HEAD
    """Değişiklikleri kaydet."""
    db = get_db()
    db.commit()
=======
    get_db().commit()
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


@app.teardown_appcontext
<<<<<<< HEAD
def close_db(exception):
    """İstek bitince bağlantıyı kapat."""
=======
def close_db(exc):
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    db = g.pop('db', None)
    if db: db.close()


<<<<<<< HEAD
# ╔══════════════════════════════════════════╗
# ║     TABLOLARI OLUŞTUR                   ║
# ╚══════════════════════════════════════════╝

=======
# ═══════════════ TABLO OLUŞTURMA ═══════════════
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
def init_db():
    """Tüm tabloları oluştur (yoksa)."""
    db = get_db()
<<<<<<< HEAD

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
=======
    if USE_POSTGRES:
        cur = db.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, profile_photo TEXT DEFAULT 'default.png',
            profile_banner TEXT DEFAULT '', theme TEXT DEFAULT 'lol-classic',
            daily_goal_minutes INTEGER DEFAULT 360, target_university TEXT DEFAULT '',
            target_mat_net REAL DEFAULT 0, target_fiz_net REAL DEFAULT 0,
            target_kim_net REAL DEFAULT 0, target_bio_net REAL DEFAULT 0,
            total_lp INTEGER DEFAULT 0, goals_set INTEGER DEFAULT 0,
            pomodoro_work INTEGER DEFAULT 25, pomodoro_break INTEGER DEFAULT 5,
            username_changed_at TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS study_sessions (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            subject TEXT NOT NULL, topic TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL, lp_earned INTEGER NOT NULL,
            is_pomodoro INTEGER DEFAULT 0, pomodoro_cycles INTEGER DEFAULT 0,
            session_date DATE NOT NULL, created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS deneme_results (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            mat_net REAL DEFAULT 0, fiz_net REAL DEFAULT 0,
            kim_net REAL DEFAULT 0, bio_net REAL DEFAULT 0,
            total_net REAL DEFAULT 0, lp_earned INTEGER DEFAULT 0,
            deneme_date DATE NOT NULL, created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS daily_checks (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            check_date DATE NOT NULL, total_minutes INTEGER DEFAULT 0,
            goal_met INTEGER DEFAULT 0, lp_change INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0, UNIQUE(user_id, check_date)
        );
        CREATE TABLE IF NOT EXISTS friendships (
            id SERIAL PRIMARY KEY, sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL, status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW(), UNIQUE(sender_id, receiver_id)
        );
        CREATE TABLE IF NOT EXISTS user_achievements (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL, earned_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, achievement_id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            ntype TEXT NOT NULL, message TEXT NOT NULL,
            icon TEXT DEFAULT '🔔', is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS weekly_badges (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            badge_type TEXT NOT NULL, badge_name TEXT NOT NULL,
            badge_icon TEXT NOT NULL, week_start DATE NOT NULL,
            week_end DATE NOT NULL, stat_value TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY, sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL, content TEXT NOT NULL,
            is_read INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        # Upgrade
        for col, default in [('username_changed_at','NULL'),('profile_banner',"''")]:
            try: cur.execute(f"ALTER TABLE users ADD COLUMN {col} TIMESTAMP DEFAULT {default}")
            except: db.rollback()
        try: cur.execute("CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL, content TEXT NOT NULL, is_read INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT NOW())")
        except: db.rollback()
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
        cur.close()

    else:
<<<<<<< HEAD
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

=======
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, profile_photo TEXT DEFAULT 'default.png',
            profile_banner TEXT DEFAULT '', theme TEXT DEFAULT 'lol-classic',
            daily_goal_minutes INTEGER DEFAULT 360, target_university TEXT DEFAULT '',
            target_mat_net REAL DEFAULT 0, target_fiz_net REAL DEFAULT 0,
            target_kim_net REAL DEFAULT 0, target_bio_net REAL DEFAULT 0,
            total_lp INTEGER DEFAULT 0, goals_set INTEGER DEFAULT 0,
            pomodoro_work INTEGER DEFAULT 25, pomodoro_break INTEGER DEFAULT 5,
            username_changed_at TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            subject TEXT NOT NULL, topic TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL, lp_earned INTEGER NOT NULL,
            is_pomodoro INTEGER DEFAULT 0, pomodoro_cycles INTEGER DEFAULT 0,
            session_date DATE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS deneme_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            mat_net REAL DEFAULT 0, fiz_net REAL DEFAULT 0,
            kim_net REAL DEFAULT 0, bio_net REAL DEFAULT 0,
            total_net REAL DEFAULT 0, lp_earned INTEGER DEFAULT 0,
            deneme_date DATE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS daily_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            check_date DATE NOT NULL, total_minutes INTEGER DEFAULT 0,
            goal_met INTEGER DEFAULT 0, lp_change INTEGER DEFAULT 0,
            processed INTEGER DEFAULT 0, UNIQUE(user_id, check_date)
        );
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL, status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(sender_id, receiver_id)
        );
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL, earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, achievement_id)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            ntype TEXT NOT NULL, message TEXT NOT NULL,
            icon TEXT DEFAULT '🔔', is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weekly_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            badge_type TEXT NOT NULL, badge_name TEXT NOT NULL,
            badge_icon TEXT NOT NULL, week_start DATE NOT NULL,
            week_end DATE NOT NULL, stat_value TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL, content TEXT NOT NULL,
            is_read INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Upgrade existing tables
        for col in ['username_changed_at','profile_banner']:
            try: db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT DEFAULT ''")
            except: pass
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    db_commit()
    print("✅ Veritabanı tabloları hazır!")


<<<<<<< HEAD
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
=======
# ═══════════════ 30 TEMA ═══════════════
THEMES = [
    {'id':'lol-classic',  'name':'LoL Classic',     'icon':'🎮','preview':['#0a0e13','#c89b3c','#0ac8b9']},
    {'id':'arcade',       'name':'Arcade',          'icon':'🕹️','preview':['#0d0221','#ff00ff','#00ffff']},
    {'id':'ocean',        'name':'Okyanus',         'icon':'🌊','preview':['#0a1628','#00b4d8','#48cae4']},
    {'id':'forest',       'name':'Orman',           'icon':'🌲','preview':['#0a1a0a','#88cc44','#44bb88']},
    {'id':'sunset',       'name':'Gün Batımı',     'icon':'🌅','preview':['#1a0e08','#ff6b35','#f7c948']},
    {'id':'cyberpunk',    'name':'Cyberpunk',       'icon':'💜','preview':['#0a0a1a','#ff2a6d','#05d9e8']},
    {'id':'valorant',     'name':'Valorant',        'icon':'🔴','preview':['#0f1012','#ff4655','#bd3944']},
    {'id':'snowdown',     'name':'Kış',            'icon':'❄️','preview':['#0a1520','#88ccff','#44aadd']},
    {'id':'star-guardian','name':'Yıldız',         'icon':'⭐','preview':['#1a0e20','#ee77aa','#aa77ee']},
    {'id':'blood-moon',   'name':'Kan Ayı',        'icon':'🌑','preview':['#1a0808','#cc2222','#ff4444']},
    {'id':'neon',         'name':'Neon',            'icon':'💡','preview':['#0a0a0a','#39ff14','#ff073a']},
    {'id':'sakura',       'name':'Sakura',          'icon':'🌸','preview':['#1a0e14','#ff99cc','#ffccdd']},
    {'id':'void',         'name':'Void',            'icon':'🕳️','preview':['#0a0014','#8844cc','#cc77ff']},
    {'id':'project',      'name':'Project',         'icon':'🤖','preview':['#0a1014','#00ccff','#0088cc']},
    {'id':'infernal',     'name':'Cehennem',        'icon':'😈','preview':['#1a0a00','#ff6600','#ffaa00']},
    {'id':'galaxy',       'name':'Galaksi',         'icon':'🌌','preview':['#0a0a1e','#6644cc','#9966ff']},
    {'id':'spirit',       'name':'Ruh Çiçeği',     'icon':'🦊','preview':['#0e1420','#66bbcc','#aaddee']},
    {'id':'dark-star',    'name':'Karanlık Yıldız','icon':'⚫','preview':['#08080e','#6622aa','#9944dd']},
    {'id':'high-noon',    'name':'Kovboy',          'icon':'🤠','preview':['#1a1408','#cc8833','#eebb55']},
    {'id':'lunar',        'name':'Ay Festivali',    'icon':'🏮','preview':['#1a0a0a','#cc3333','#ffcc00']},
    {'id':'crystal',      'name':'Kristal',         'icon':'💎','preview':['#0e1418','#44cccc','#88eeff']},
    {'id':'volcanic',     'name':'Volkan',          'icon':'🌋','preview':['#1a0800','#ee4400','#ff8800']},
    {'id':'deep-sea',     'name':'Derin Deniz',     'icon':'🐙','preview':['#040e18','#004488','#0066bb']},
    {'id':'aurora',       'name':'Kutup Işığı',    'icon':'🌈','preview':['#0a1018','#00cc88','#44aaff']},
    {'id':'desert',       'name':'Çöl',            'icon':'🏜️','preview':['#1a1408','#ccaa44','#eedd88']},
    {'id':'steampunk',    'name':'Steampunk',       'icon':'⚙️','preview':['#141008','#aa7733','#cc9955']},
    {'id':'phantom',      'name':'Hayalet',         'icon':'👻','preview':['#0e0e14','#8888aa','#aaaacc']},
    {'id':'emerald-city', 'name':'Zümrüt Şehir',  'icon':'🏙️','preview':['#081a0e','#00cc66','#44ee88']},
    {'id':'ruby',         'name':'Yakut',           'icon':'❤️','preview':['#1a0808','#cc1144','#ee3366']},
    {'id':'sapphire',     'name':'Safir',           'icon':'💙','preview':['#08081a','#2244cc','#4466ee']},
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
]

RANKS = [
    {'name':'Demir','min_lp':0,'color':'#5c5c5c','glow':'#3a3a3a','img':'iron.png','icon':'⚔️'},
    {'name':'Bronz','min_lp':1000,'color':'#cd7f32','glow':'#8b5e20','img':'bronze.png','icon':'🛡️'},
    {'name':'Gümüş','min_lp':2500,'color':'#c0c0c0','glow':'#8a8a8a','img':'silver.png','icon':'⚡'},
    {'name':'Altın','min_lp':5000,'color':'#ffd700','glow':'#b8960f','img':'gold.png','icon':'👑'},
    {'name':'Platin','min_lp':8000,'color':'#00cec9','glow':'#00a8a3','img':'platinum.png','icon':'💎'},
    {'name':'Zümrüt','min_lp':12000,'color':'#00b894','glow':'#009a7b','img':'emerald.png','icon':'🔮'},
    {'name':'Elmas','min_lp':17000,'color':'#74b9ff','glow':'#4a90d9','img':'diamond.png','icon':'💠'},
    {'name':'Ustalık','min_lp':23000,'color':'#a29bfe','glow':'#7c74d4','img':'master.png','icon':'🏆'},
    {'name':'Üstatlık','min_lp':30000,'color':'#fd79a8','glow':'#d4507e','img':'grandmaster.png','icon':'🌟'},
    {'name':'Challenger','min_lp':40000,'color':'#fdcb6e','glow':'#e6b04a','img':'challenger.png','icon':'🔥'},
]

ACHIEVEMENTS = [
<<<<<<< HEAD
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
=======
    {'id':'first_session','name':'İlk Adım','desc':'İlk çalışma','icon':'🎯','lp':50,'category':'study'},
    {'id':'hour_1','name':'Isınma','desc':'1 saat çalış','icon':'⏰','lp':100,'category':'study'},
    {'id':'hour_10','name':'Çalışkan Arı','desc':'10 saat','icon':'🐝','lp':200,'category':'study'},
    {'id':'hour_50','name':'Savaşçı','desc':'50 saat','icon':'⚔️','lp':400,'category':'study'},
    {'id':'hour_100','name':'Efsane','desc':'100 saat','icon':'🏛️','lp':500,'category':'study'},
    {'id':'hour_200','name':'Tanrı','desc':'200 saat','icon':'👁️','lp':500,'category':'study'},
    {'id':'streak_3','name':'Üçleme','desc':'3 gün seri','icon':'🔥','lp':50,'category':'streak'},
    {'id':'streak_7','name':'Boss','desc':'7 gün seri','icon':'💪','lp':150,'category':'streak'},
    {'id':'streak_14','name':'Canavar','desc':'14 gün seri','icon':'🦁','lp':300,'category':'streak'},
    {'id':'streak_30','name':'Ay Tanrısı','desc':'30 gün seri','icon':'🌙','lp':500,'category':'streak'},
    {'id':'pomo_1','name':'İlk Pomo','desc':'1 pomodoro','icon':'🍅','lp':50,'category':'pomodoro'},
    {'id':'pomo_25','name':'Pomo Avcı','desc':'25 pomo','icon':'🍅','lp':150,'category':'pomodoro'},
    {'id':'pomo_100','name':'Pomo Usta','desc':'100 pomo','icon':'🍅','lp':300,'category':'pomodoro'},
    {'id':'deneme_1','name':'İlk Deneme','desc':'1 deneme','icon':'📝','lp':50,'category':'deneme'},
    {'id':'deneme_5','name':'Gazi','desc':'5 deneme','icon':'📊','lp':150,'category':'deneme'},
    {'id':'deneme_target','name':'Hedef!','desc':'Hedef nete ulaş','icon':'🎯','lp':300,'category':'deneme'},
    {'id':'first_friend','name':'Arkadaş','desc':'İlk arkadaş','icon':'🤝','lp':50,'category':'social'},
    {'id':'friends_5','name':'Ekip','desc':'5 arkadaş','icon':'👥','lp':100,'category':'social'},
    {'id':'first_message','name':'İlk Mesaj','desc':'İlk sohbet','icon':'💬','lp':30,'category':'social'},
    {'id':'weekly_champ','name':'Haftalık Şampiyon','desc':'Haftanın en iyisi','icon':'🏆','lp':200,'category':'weekly'},
    {'id':'rank_bronze','name':'Bronz','desc':'Bronz ol','icon':'🛡️','lp':0,'category':'rank'},
    {'id':'rank_silver','name':'Gümüş','desc':'Gümüş ol','icon':'⚡','lp':0,'category':'rank'},
    {'id':'rank_gold','name':'Altın','desc':'Altın ol','icon':'👑','lp':0,'category':'rank'},
    {'id':'rank_platinum','name':'Platin','desc':'Platin ol','icon':'💎','lp':0,'category':'rank'},
    {'id':'rank_emerald','name':'Zümrüt','desc':'Zümrüt ol','icon':'🔮','lp':0,'category':'rank'},
    {'id':'rank_diamond','name':'Elmas','desc':'Elmas ol','icon':'💠','lp':0,'category':'rank'},
    {'id':'rank_master','name':'Ustalık','desc':'Usta ol','icon':'🏆','lp':0,'category':'rank'},
    {'id':'rank_grandmaster','name':'Üstatlık','desc':'Üstat ol','icon':'🌟','lp':0,'category':'rank'},
    {'id':'rank_challenger','name':'Challenger','desc':'Challenger ol','icon':'🔥','lp':0,'category':'rank'},
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
]
ACHIEVEMENT_MAP = {a['id']:a for a in ACHIEVEMENTS}

AYT_TOPICS = {
<<<<<<< HEAD
    'Matematik':['Temel Kavramlar','Sayı Basamakları','Bölme ve Bölünebilme','EBOB-EKOK','Rasyonel Sayılar','Basit Eşitsizlikler','Mutlak Değer','Üslü Sayılar','Köklü Sayılar','Çarpanlara Ayırma','Oran Orantı','Denklem Çözme','Problemler (Sayı-Kesir-Yaş)','Problemler (İşçi-Havuz-Yüzde)','Problemler (Kar-Zarar-Hareket)','Kümeler','Fonksiyonlar','Polinomlar','2. Derece Denklemler','Permütasyon Kombinasyon','Binom','Olasılık','İstatistik','Logaritma','Diziler Seriler','Limit Süreklilik','Türev','İntegral','Trigonometri','Analitik Geometri','Karmaşık Sayılar'],
    'Fizik':['Vektörler','Kuvvet Denge','Tork','Düzgün Doğrusal Hareket','Düzgün İvmeli Hareket','Newton Yasaları','İş Güç Enerji','İtme Momentum','Elektrik Alan','Paralel Levhalar Sığa','Manyetizma','İndüksiyon','Alternatif Akım','Dalga Mekaniği','Atom Fiziği','Radyoaktivite','Basınç Kaldırma','Optik'],
    'Kimya':['Atom Periyodik Sistem','Kimyasal Etkileşimler','Maddenin Halleri','Mol Stokiyometri','Kimyasal Tepkimeler','Asit Baz','Karışımlar','Çözeltiler Derişim','Kimyasal Denge','Termokimya','Tepkime Hızları','Elektrokimya','Organik Kimya','Çekirdek Kimyası'],
    'Biyoloji':['Hücre Organeller','Hücre Bölünmeleri','Kalıtım','Ekosistem','Bitki Biyolojisi','Enerji Dönüşümleri','Sindirim','Dolaşım Bağışıklık','Solunum','Boşaltım','Sinir Sistemi','Endokrin','Duyu Organları','Destek Hareket','Üreme Gelişme','Komünite Popülasyon','Sınıflandırma'],
=======
    'Matematik':['Temel Kavramlar','Sayı Basamakları','Bölme-Bölünebilme','EBOB-EKOK','Rasyonel Sayılar','Eşitsizlikler','Mutlak Değer','Üslü Sayılar','Köklü Sayılar','Çarpanlara Ayırma','Oran Orantı','Denklem','Problemler (Sayı-Kesir-Yaş)','Problemler (İşçi-Havuz-Yüzde)','Problemler (Hareket-Karışım)','Kümeler','Fonksiyonlar','Polinomlar','2.Derece Denklemler','Permütasyon-Kombinasyon','Binom','Olasılık','İstatistik','Logaritma','Diziler','Limit','Türev','İntegral','Trigonometri','Analitik Geometri','Karmaşık Sayılar'],
    'Fizik':['Vektörler','Kuvvet-Denge','Tork','Doğrusal Hareket','İvmeli Hareket','Newton','İş-Güç-Enerji','Momentum','Elektrik Alan','Sığa','Manyetizma','İndüksiyon','AC','Dalga','Atom Fiziği','Radyoaktivite','Basınç','Optik'],
    'Kimya':['Atom-Periyodik','Etkileşimler','Madde Halleri','Mol-Stokiyometri','Tepkimeler','Asit-Baz','Karışımlar','Çözeltiler','Denge','Termokimya','Hız','Elektrokimya','Organik','Çekirdek'],
    'Biyoloji':['Hücre','Bölünmeler','Kalıtım','Ekosistem','Bitki','Enerji','Sindirim','Dolaşım','Solunum','Boşaltım','Sinir','Endokrin','Duyu','Hareket','Üreme','Popülasyon','Sınıflandırma'],
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
}
SUBJECT_ICONS = {'Matematik':'📐','Fizik':'⚡','Kimya':'🧪','Biyoloji':'🧬'}


# ╔══════════════════════════════════════════╗
# ║     YARDIMCI FONKSİYONLAR               ║
# ╚══════════════════════════════════════════╝

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

def get_rank(lp):
    cur=RANKS[0]
    for r in RANKS:
        if lp>=r['min_lp']:cur=r
        else:break
    return cur

def get_next_rank(lp):
    for r in RANKS:
        if lp<r['min_lp']:return r
    return None

def rank_progress(lp):
    c=get_rank(lp);n=get_next_rank(lp)
    if not n:return 100
    t=n['min_lp']-c['min_lp'];d=lp-c['min_lp']
    return int(d/t*100) if t else 100

def login_required(f):
    @wraps(f)
    def w(*a,**kw):
        if 'user_id' not in session:
            flash('Giriş yapın.','warning');return redirect(url_for('login'))
        return f(*a,**kw)
    return w

<<<<<<< HEAD
def get_photo_url(photo_value):
    if not photo_value or photo_value == 'default.png':
        return None
    if photo_value.startswith('http'):
        return photo_value
    return url_for('static', filename='uploads/' + photo_value)

def add_notification(user_id, ntype, message, icon='🔔'):
=======
def get_photo_url(v):
    if not v or v=='default.png':return None
    if v.startswith('http'):return v
    return url_for('static',filename='uploads/'+v)

def add_notification(uid,ntype,msg,icon='🔔'):
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    db_execute('INSERT INTO notifications(user_id,ntype,message,icon) VALUES(?,?,?,?)',
               (uid,ntype,msg,icon))

def get_streak(uid):
    u=db_fetchone('SELECT daily_goal_minutes FROM users WHERE id=?',(uid,))
    if not u:return 0
    goal=u['daily_goal_minutes'];streak=0;d=date.today()-timedelta(days=1)
    while True:
<<<<<<< HEAD
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
=======
        r=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND session_date=?',(uid,d.isoformat()))
        if r and r['t']>=goal:streak+=1;d-=timedelta(days=1)
        else:break
    return streak

def get_friend_count(uid):
    r=db_fetchone("SELECT COUNT(*) as c FROM friendships WHERE (sender_id=? OR receiver_id=?) AND status='accepted'",(uid,uid))
    return r['c'] if r else 0

def get_unread_messages(uid):
    r=db_fetchone('SELECT COUNT(*) as c FROM messages WHERE receiver_id=? AND is_read=0',(uid,))
    return r['c'] if r else 0


# ═══════════════ BAŞARIM + GÜNLÜK + HAFTALIK ═══════════════
def check_achievements(uid):
    earned={r['achievement_id'] for r in db_fetchall('SELECT achievement_id FROM user_achievements WHERE user_id=?',(uid,))}
    u=db_fetchone('SELECT * FROM users WHERE id=?',(uid,))
    if not u:return []
    new=[]
    ts=db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',(uid,))['c']
    tm=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(uid,))['t']
    th=tm/60
    tp=db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',(uid,))['t']
    td=db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',(uid,))['c']
    streak=get_streak(uid);friends=get_friend_count(uid);lp=u['total_lp']
    hw=db_fetchone('SELECT id FROM weekly_badges WHERE user_id=? LIMIT 1',(uid,))
    msg_count=db_fetchone('SELECT COUNT(*) as c FROM messages WHERE sender_id=?',(uid,))['c']

    checks={
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
        'first_session':ts>=1,'hour_1':th>=1,'hour_10':th>=10,'hour_50':th>=50,
        'hour_100':th>=100,'hour_200':th>=200,
        'streak_3':streak>=3,'streak_7':streak>=7,'streak_14':streak>=14,'streak_30':streak>=30,
        'pomo_1':tp>=1,'pomo_25':tp>=25,'pomo_100':tp>=100,
        'deneme_1':td>=1,'deneme_5':td>=5,
        'first_friend':friends>=1,'friends_5':friends>=5,
<<<<<<< HEAD
=======
        'first_message':msg_count>=1,
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
        'weekly_champ':bool(hw),
        'rank_bronze':lp>=1000,'rank_silver':lp>=2500,'rank_gold':lp>=5000,
        'rank_platinum':lp>=8000,'rank_emerald':lp>=12000,'rank_diamond':lp>=17000,
        'rank_master':lp>=23000,'rank_grandmaster':lp>=30000,'rank_challenger':lp>=40000,
    }
    if 'deneme_target' not in earned:
        tgt=u['target_mat_net']+u['target_fiz_net']+u['target_kim_net']+u['target_bio_net']
        if tgt>0:
            best=db_fetchone('SELECT MAX(total_net) as m FROM deneme_results WHERE user_id=?',(uid,))
            if best and best['m'] and best['m']>=tgt:checks['deneme_target']=True

    for aid,cond in checks.items():
        if aid not in earned and cond and aid in ACHIEVEMENT_MAP:
<<<<<<< HEAD
            a = ACHIEVEMENT_MAP[aid]
            db_execute('INSERT INTO user_achievements(user_id,achievement_id) VALUES(?,?)',(user_id,aid))
            if a['lp'] > 0:
                db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(a['lp'],user_id))
            add_notification(user_id,'achievement',f"🏅 {a['name']}: {a['desc']} (+{a['lp']} LP)",a['icon'])
            new_achs.append(a)
=======
            a=ACHIEVEMENT_MAP[aid]
            db_execute('INSERT INTO user_achievements(user_id,achievement_id) VALUES(?,?)',(uid,aid))
            if a['lp']>0:db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(a['lp'],uid))
            add_notification(uid,'achievement',f"🏅 {a['name']}: {a['desc']} (+{a['lp']} LP)",a['icon'])
            new.append(a)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    db_commit()
    return new

def process_weekly_badges():
    today=date.today()
    if today.weekday()!=0:return
    we=today-timedelta(days=1);ws=we-timedelta(days=6)
    if db_fetchone('SELECT id FROM weekly_badges WHERE week_start=? LIMIT 1',(ws.isoformat(),)):return
    for q_str,btype,bname,bicon in [
        ('SELECT user_id,SUM(duration_minutes) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_study','👑 Çalışma Kralı','👑'),
        ('SELECT user_id,SUM(pomodoro_cycles) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? AND is_pomodoro=1 GROUP BY user_id ORDER BY total DESC LIMIT 1','top_pomo','🍅 Pomo Ustası','🍅'),
        ('SELECT user_id,MAX(total_net) as total FROM deneme_results WHERE deneme_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_deneme','📊 Deneme Şampiyonu','📊'),
        ('SELECT user_id,SUM(lp_earned) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_lp','⚡ LP Avcısı','⚡'),
    ]:
        w=db_fetchone(q_str,(ws.isoformat(),we.isoformat()))
        if w and w.get('user_id'):
            db_execute('INSERT INTO weekly_badges(user_id,badge_type,badge_name,badge_icon,week_start,week_end,stat_value) VALUES(?,?,?,?,?,?,?)',
                       (w['user_id'],btype,bname,bicon,ws.isoformat(),we.isoformat(),str(w.get('total',''))))
            add_notification(w['user_id'],'weekly_badge',f'{bicon} {bname}! +200 LP',bicon)
            db_execute('UPDATE users SET total_lp=total_lp+200 WHERE id=?',(w['user_id'],))
    db_commit()

<<<<<<< HEAD
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

=======
def check_daily_goals(uid):
    u=db_fetchone('SELECT * FROM users WHERE id=?',(uid,))
    if not u or not u['goals_set']:return
    today=date.today();process_weekly_badges()
    try:created=datetime.strptime(str(u['created_at'])[:10],'%Y-%m-%d').date()
    except:created=today-timedelta(days=60)
    mx='GREATEST' if USE_POSTGRES else 'MAX'
    for i in range(1,8):
        d=today-timedelta(days=i)
        if d<created:continue
        ex=db_fetchone('SELECT * FROM daily_checks WHERE user_id=? AND check_date=?',(uid,d.isoformat()))
        if ex and ex['processed']:continue
        mins=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND session_date=?',(uid,d.isoformat()))['t']
        goal=u['daily_goal_minutes']
        if mins>=goal:lp_ch,met=200,1
        elif mins>0:lp_ch=max(-int((goal-mins)/goal*30),-30);met=0
        else:lp_ch,met=-20,0
        if ex:db_execute('UPDATE daily_checks SET total_minutes=?,goal_met=?,lp_change=?,processed=1 WHERE id=?',(mins,met,lp_ch,ex['id']))
        else:db_execute('INSERT INTO daily_checks(user_id,check_date,total_minutes,goal_met,lp_change,processed) VALUES(?,?,?,?,?,1)',(uid,d.isoformat(),mins,met,lp_ch))
        db_execute(f'UPDATE users SET total_lp={mx}(0,total_lp+?) WHERE id=?',(lp_ch,uid))
    streak=get_streak(uid)
    for sd,sl in {3:50,7:150,14:300,30:500}.items():
        if streak==sd:
            db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(sl,uid))
            add_notification(uid,'streak',f'🔥 {sd} gün seri! +{sl} LP','🔥')
    check_achievements(uid);db_commit()


# ═══════════════ CONTEXT ═══════════════
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
@app.context_processor
def inject_globals():
    unread=0;unread_msgs=0
    if 'user_id' in session:
<<<<<<< HEAD
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
=======
        r=db_fetchone('SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND is_read=0',(session['user_id'],))
        unread=r['c'] if r else 0
        unread_msgs=get_unread_messages(session['user_id'])
    return {'current_theme':session.get('theme','lol-classic'),'all_themes':THEMES,
            'all_ranks':RANKS,'unread_notifs':unread,'unread_msgs':unread_msgs,
            'get_photo_url':get_photo_url,'get_rank':get_rank}


# ════════════════════════════════════════
#  ANA ROTALAR
# ════════════════════════════════════════
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

# ── KAYIT ──
@app.route('/register', methods=['GET','POST'])
def register():
<<<<<<< HEAD
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

=======
    if request.method=='POST':
        un=request.form.get('username','').strip();pw=request.form.get('password','');pw2=request.form.get('password_confirm','')
        if not un or not pw:flash('Gerekli.','error');return redirect(url_for('register'))
        if len(un)<3:flash('En az 3 karakter.','error');return redirect(url_for('register'))
        if len(pw)<6:flash('Şifre en az 6.','error');return redirect(url_for('register'))
        if pw!=pw2:flash('Eşleşmiyor.','error');return redirect(url_for('register'))
        if db_fetchone('SELECT 1 FROM users WHERE username=?',(un,)):
            flash('Alınmış.','error');return redirect(url_for('register'))
        db_execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(un,generate_password_hash(pw)))
        db_commit()
        u=db_fetchone('SELECT id FROM users WHERE username=?',(un,))
        session['user_id']=u['id'];session['username']=un;session['theme']='lol-classic'
        flash('Kayıt başarılı!','success');return redirect(url_for('setup_goals'))
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return render_template('register.html')

# ── GİRİŞ ──
@app.route('/login', methods=['GET','POST'])
def login():
<<<<<<< HEAD
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
=======
    if request.method=='POST':
        un=request.form.get('username','').strip();pw=request.form.get('password','')
        u=db_fetchone('SELECT * FROM users WHERE username=?',(un,))
        if u and check_password_hash(u['password_hash'],pw):
            session['user_id']=u['id'];session['username']=u['username'];session['theme']=u.get('theme','lol-classic')
            check_daily_goals(u['id'])
            if not u['goals_set']:return redirect(url_for('setup_goals'))
            flash(f'Hoş geldin, {un}! 🎮','success');return redirect(url_for('dashboard'))
        flash('Hatalı.','error')
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return render_template('login.html')

@app.route('/logout')
def logout():
<<<<<<< HEAD
    session.clear()
    flash('Çıkış yapıldı.','info')
    return redirect(url_for('login'))
=======
    session.clear();flash('Çıkış.','info');return redirect(url_for('login'))
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

# ── HEDEFLER ──
@app.route('/setup-goals', methods=['GET','POST'])
@login_required
def setup_goals():
<<<<<<< HEAD
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
=======
    if request.method=='POST':
        db_execute('UPDATE users SET daily_goal_minutes=?,target_university=?,target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,goals_set=1 WHERE id=?',
                   (int(float(request.form.get('daily_hours',6))*60),request.form.get('target_university',''),
                    float(request.form.get('target_mat_net',0)),float(request.form.get('target_fiz_net',0)),
                    float(request.form.get('target_kim_net',0)),float(request.form.get('target_bio_net',0)),session['user_id']))
        db_commit();flash('Hedefler kaydedildi! 🚀','success');return redirect(url_for('dashboard'))
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return render_template('setup_goals.html')

@app.route('/api/set-theme', methods=['POST'])
@login_required
def set_theme():
<<<<<<< HEAD
    tid = request.get_json().get('theme','lol-classic')
    if tid not in [t['id'] for t in THEMES]:
        return jsonify(success=False)
    db_execute('UPDATE users SET theme=? WHERE id=?',(tid,session['user_id']))
    db_commit()
    session['theme'] = tid
=======
    tid=request.get_json().get('theme','lol-classic')
    if tid not in [t['id'] for t in THEMES]:return jsonify(success=False)
    db_execute('UPDATE users SET theme=? WHERE id=?',(tid,session['user_id']));db_commit();session['theme']=tid
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return jsonify(success=True)

@app.route('/api/notifications')
@login_required
def get_notifications():
<<<<<<< HEAD
    notifs = db_fetchall(
        'SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20',
        (session['user_id'],))
    db_execute('UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0',
               (session['user_id'],))
    db_commit()
    return jsonify(notifs)
=======
    n=db_fetchall('SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20',(session['user_id'],))
    db_execute('UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0',(session['user_id'],));db_commit()
    return jsonify(n)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


# ═══════ KULLANICI ADI DEĞİŞTİRME ═══════
@app.route('/api/change-username', methods=['POST'])
@login_required
def change_username():
    new_name = request.get_json().get('new_username','').strip()
    if not new_name or len(new_name)<3:
        return jsonify(success=False, message='En az 3 karakter.')
    if len(new_name)>20:
        return jsonify(success=False, message='En fazla 20 karakter.')

    user = db_fetchone('SELECT username, username_changed_at FROM users WHERE id=?',(session['user_id'],))
    if user['username'] == new_name:
        return jsonify(success=False, message='Zaten bu isimdesin.')

    # 7 gün cooldown kontrolü
    if user.get('username_changed_at') and user['username_changed_at']:
        try:
            last_change = datetime.strptime(str(user['username_changed_at'])[:19], '%Y-%m-%d %H:%M:%S')
            diff = datetime.now() - last_change
            if diff.days < 7:
                remaining = 7 - diff.days
                return jsonify(success=False,
                    message=f'İsim değiştirmek için {remaining} gün daha beklemelisin.')
        except:
            pass

    # İsim müsait mi?
    if db_fetchone('SELECT 1 FROM users WHERE username=?',(new_name,)):
        return jsonify(success=False, message='Bu isim alınmış.')

    db_execute('UPDATE users SET username=?, username_changed_at=? WHERE id=?',
               (new_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session['user_id']))
    db_commit()
    session['username'] = new_name
    return jsonify(success=True, message=f'İsmin "{new_name}" olarak değiştirildi! 🎉')


# ═══════ DASHBOARD ═══════
@app.route('/dashboard')
@login_required
def dashboard():
    check_daily_goals(session['user_id'])
<<<<<<< HEAD
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
=======
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    ti=date.today().isoformat()
    today_mins=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND session_date=?',(session['user_id'],ti))['t']
    total_mins=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(session['user_id'],))['t']
    today_pomos=db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND session_date=? AND is_pomodoro=1',(session['user_id'],ti))['t']
    last_deneme=db_fetchone('SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 1',(session['user_id'],))
    weekly=[]
    for i in range(6,-1,-1):
        d=date.today()-timedelta(days=i)
        m=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND session_date=?',(session['user_id'],d.isoformat()))['t']
        weekly.append({'label':['Pzt','Sal','Çar','Per','Cum','Cmt','Paz'][d.weekday()],'mins':m})
    subj_stats=db_fetchall('SELECT subject,COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? GROUP BY subject ORDER BY t DESC',(session['user_id'],))
    streak=get_streak(session['user_id'])
    ra_raw=db_fetchall('SELECT achievement_id,earned_at FROM user_achievements WHERE user_id=? ORDER BY earned_at DESC LIMIT 5',(session['user_id'],))
    ra=[dict(ACHIEVEMENT_MAP.get(r['achievement_id'],{}),earned_at=r['earned_at']) for r in ra_raw if r['achievement_id'] in ACHIEVEMENT_MAP]
    lb_pos=db_fetchone('SELECT COUNT(*)+1 as pos FROM users WHERE total_lp>(SELECT total_lp FROM users WHERE id=?)',(session['user_id'],))['pos']
    tu=db_fetchone('SELECT COUNT(*) as c FROM users')['c']
    pr=db_fetchall("SELECT f.id,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON u.id=f.sender_id WHERE f.receiver_id=? AND f.status='pending'",(session['user_id'],))
    mb=db_fetchall('SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC LIMIT 10',(session['user_id'],))
    r=get_rank(u['total_lp']);nr=get_next_rank(u['total_lp']);prog=rank_progress(u['total_lp'])
    return render_template('dashboard.html',user=u,rank=r,next_rank=nr,rank_progress=prog,
        today_mins=today_mins,total_mins=total_mins,today_pomodoros=today_pomos,
        last_deneme=last_deneme,weekly=weekly,subj_stats=subj_stats,streak=streak,
        subject_icons=SUBJECT_ICONS,recent_achievements=ra,lb_position=lb_pos,
        total_users=tu,pending_requests=pr,my_badges=mb)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


# ═══════ ÇALIŞMA ═══════
@app.route('/study')
@login_required
def study():
    return render_template('study.html', subjects=AYT_TOPICS, icons=SUBJECT_ICONS)

@app.route('/study/<subject>')
@login_required
def study_subject(subject):
<<<<<<< HEAD
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
=======
    if subject not in AYT_TOPICS:flash('Geçersiz.','error');return redirect(url_for('study'))
    return render_template('study_topics.html',subject=subject,topics=AYT_TOPICS[subject],icon=SUBJECT_ICONS.get(subject,'📚'))

@app.route('/study/<subject>/<int:tidx>')
@login_required
def study_timer(subject,tidx):
    if subject not in AYT_TOPICS or tidx>=len(AYT_TOPICS[subject]):flash('Geçersiz.','error');return redirect(url_for('study'))
    u=db_fetchone('SELECT pomodoro_work,pomodoro_break FROM users WHERE id=?',(session['user_id'],))
    return render_template('timer.html',subject=subject,topic=AYT_TOPICS[subject][tidx],icon=SUBJECT_ICONS.get(subject,'📚'),pomo_work=u['pomodoro_work'] or 25,pomo_break=u['pomodoro_break'] or 5)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

# ── ÇALIŞMA KAYDET ──
@app.route('/api/save-session', methods=['POST'])
@login_required
def save_session():
<<<<<<< HEAD
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
=======
    d=request.get_json();subj=d.get('subject','');topic=d.get('topic','')
    mins=int(d.get('duration_minutes',0));is_p=int(d.get('is_pomodoro',0));pc=int(d.get('pomodoro_cycles',0))
    if mins<1:return jsonify(success=False,message='En az 1 dk!')
    lp=(mins*2)+(pc*15 if is_p else 0)
    old_lp=db_fetchone('SELECT total_lp FROM users WHERE id=?',(session['user_id'],))['total_lp']
    old_r=get_rank(old_lp)
    db_execute('INSERT INTO study_sessions(user_id,subject,topic,duration_minutes,lp_earned,is_pomodoro,pomodoro_cycles,session_date) VALUES(?,?,?,?,?,?,?,?)',
               (session['user_id'],subj,topic,mins,lp,is_p,pc,date.today().isoformat()))
    db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(lp,session['user_id']))
    u=db_fetchone('SELECT total_lp FROM users WHERE id=?',(session['user_id'],))
    new_r=get_rank(u['total_lp']);ru=old_r['name']!=new_r['name']
    if ru:add_notification(session['user_id'],'rankup',f"🎉 {new_r['name']}!",new_r['icon'])
    na=check_achievements(session['user_id']);db_commit()
    return jsonify(success=True,lp_earned=lp,total_lp=u['total_lp'],rank=new_r['name'],rank_img=new_r['img'],
        rank_color=new_r['color'],rank_up=ru,new_rank_name=new_r['name'] if ru else None,
        new_achievements=[{'name':a['name'],'icon':a['icon'],'lp':a['lp']} for a in na],message=f'+{lp} LP! 🎉')
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


# ═══════ DENEME ═══════
@app.route('/deneme', methods=['GET','POST'])
@login_required
def deneme():
<<<<<<< HEAD
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
=======
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    if request.method=='POST':
        mn=float(request.form.get('mat_net',0));fn=float(request.form.get('fiz_net',0))
        kn=float(request.form.get('kim_net',0));bn=float(request.form.get('bio_net',0))
        dd=request.form.get('deneme_date',date.today().isoformat());tn=mn+fn+kn+bn
        tgt=u['target_mat_net']+u['target_fiz_net']+u['target_kim_net']+u['target_bio_net']
        lp=int((tn/tgt)*400) if tgt>0 else int(tn*4);lp=max(0,min(lp,800))
        db_execute('INSERT INTO deneme_results(user_id,mat_net,fiz_net,kim_net,bio_net,total_net,lp_earned,deneme_date) VALUES(?,?,?,?,?,?,?,?)',
                   (session['user_id'],mn,fn,kn,bn,tn,lp,dd))
        db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(lp,session['user_id']))
        check_achievements(session['user_id']);db_commit();flash(f'+{lp} LP','success');return redirect(url_for('deneme'))
    hist=db_fetchall('SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 20',(session['user_id'],))
    return render_template('deneme.html',user=u,history=hist)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


# ═══════ PROFİL ═══════
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
<<<<<<< HEAD
    if request.method == 'POST':
        # Profil fotoğrafı (GIF dahil)
=======
    if request.method=='POST':
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
        if 'profile_photo' in request.files:
            f = request.files['profile_photo']
            if f and f.filename and allowed_file(f.filename):
<<<<<<< HEAD
                fn = secure_filename(
                    f"u{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db_execute('UPDATE users SET profile_photo=? WHERE id=?',
                           (fn, session['user_id']))
                db_commit()
                flash('Fotoğraf güncellendi! 📸','success')

        # Banner (GIF dahil)
=======
                fn=secure_filename(f"u{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],fn))
                db_execute('UPDATE users SET profile_photo=? WHERE id=?',(fn,session['user_id']));db_commit()
                flash('PP güncellendi! 📸','success')
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
        if 'profile_banner' in request.files:
            f = request.files['profile_banner']
            if f and f.filename and allowed_file(f.filename):
<<<<<<< HEAD
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
=======
                fn=secure_filename(f"b{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],fn))
                db_execute('UPDATE users SET profile_banner=? WHERE id=?',(fn,session['user_id']));db_commit()
                flash('Banner güncellendi! 🖼️','success')
        if 'daily_hours' in request.form:
            db_execute('UPDATE users SET daily_goal_minutes=?,target_university=?,target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,pomodoro_work=?,pomodoro_break=? WHERE id=?',
                       (int(float(request.form.get('daily_hours',6))*60),request.form.get('target_university',''),
                        float(request.form.get('target_mat_net',0)),float(request.form.get('target_fiz_net',0)),
                        float(request.form.get('target_kim_net',0)),float(request.form.get('target_bio_net',0)),
                        int(request.form.get('pomodoro_work',25)),int(request.form.get('pomodoro_break',5)),session['user_id']))
            db_commit();flash('Güncellendi!','success')
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    stats={'sessions':db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',(session['user_id'],))['c'],
           'total_mins':db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(session['user_id'],))['t'],
           'denemes':db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',(session['user_id'],))['c'],
           'active_days':db_fetchone('SELECT COUNT(DISTINCT session_date) as d FROM study_sessions WHERE user_id=?',(session['user_id'],))['d'],
           'pomodoros':db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',(session['user_id'],))['t']}
    earned_ids={a['achievement_id'] for a in db_fetchall('SELECT achievement_id FROM user_achievements WHERE user_id=?',(session['user_id'],))}
    wb=db_fetchall('SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC',(session['user_id'],))
    # Cooldown hesapla
    can_change_name=True;name_cooldown_days=0
    if u.get('username_changed_at') and u['username_changed_at']:
        try:
            lc=datetime.strptime(str(u['username_changed_at'])[:19],'%Y-%m-%d %H:%M:%S')
            diff=(datetime.now()-lc).days
            if diff<7:can_change_name=False;name_cooldown_days=7-diff
        except:pass
    return render_template('profile.html',user=u,rank=get_rank(u['total_lp']),stats=stats,
        achievements=ACHIEVEMENTS,earned_ids=earned_ids,weekly_badges=wb,
        can_change_name=can_change_name,name_cooldown_days=name_cooldown_days)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)


# ═══════ ARKADAŞLAR ═══════
@app.route('/friends')
@login_required
def friends():
<<<<<<< HEAD
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
=======
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    fr=db_fetchall("SELECT u.id,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON (CASE WHEN f.sender_id=? THEN f.receiver_id ELSE f.sender_id END)=u.id WHERE (f.sender_id=? OR f.receiver_id=?) AND f.status='accepted' ORDER BY u.total_lp DESC",
                   (session['user_id'],session['user_id'],session['user_id']))
    inc=db_fetchall("SELECT f.id as fid,u.id as uid,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON u.id=f.sender_id WHERE f.receiver_id=? AND f.status='pending'",(session['user_id'],))
    out=db_fetchall("SELECT f.id as fid,u.id as uid,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON u.id=f.receiver_id WHERE f.sender_id=? AND f.status='pending'",(session['user_id'],))
    return render_template('friends.html',user=u,rank=get_rank(u['total_lp']),friends=fr,incoming=inc,outgoing=out)
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

@app.route('/api/add-friend', methods=['POST'])
@login_required
def add_friend():
<<<<<<< HEAD
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
=======
    un=request.get_json().get('username','').strip()
    if not un:return jsonify(success=False,message='İsim gir.')
    t=db_fetchone('SELECT id FROM users WHERE username=?',(un,))
    if not t:return jsonify(success=False,message='Bulunamadı.')
    if t['id']==session['user_id']:return jsonify(success=False,message='Kendini ekleyemezsin 😄')
    ex=db_fetchone('SELECT * FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
                   (session['user_id'],t['id'],t['id'],session['user_id']))
    if ex:
        if ex['status']=='accepted':return jsonify(success=False,message='Zaten arkadaşsınız!')
        return jsonify(success=False,message='İstek mevcut.')
    db_execute("INSERT INTO friendships(sender_id,receiver_id,status) VALUES(?,?,'pending')",(session['user_id'],t['id']))
    add_notification(t['id'],'friend_request',f'📩 {session["username"]} arkadaşlık isteği!','🤝');db_commit()
    return jsonify(success=True,message=f'{un} kullanıcısına istek gönderildi! 🤝')

# Leaderboard üzerinden ID ile arkadaş ekleme
@app.route('/api/add-friend-by-id', methods=['POST'])
@login_required
def add_friend_by_id():
    tid=request.get_json().get('user_id')
    if not tid:return jsonify(success=False,message='Geçersiz.')
    if int(tid)==session['user_id']:return jsonify(success=False,message='Kendini ekleyemezsin 😄')
    t=db_fetchone('SELECT id,username FROM users WHERE id=?',(tid,))
    if not t:return jsonify(success=False,message='Bulunamadı.')
    ex=db_fetchone('SELECT * FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
                   (session['user_id'],tid,tid,session['user_id']))
    if ex:
        if ex['status']=='accepted':return jsonify(success=False,message='Zaten arkadaşsınız!')
        return jsonify(success=False,message='İstek mevcut.')
    db_execute("INSERT INTO friendships(sender_id,receiver_id,status) VALUES(?,?,'pending')",(session['user_id'],tid))
    add_notification(tid,'friend_request',f'📩 {session["username"]} arkadaşlık isteği!','🤝');db_commit()
    return jsonify(success=True,message=f'{t["username"]} kullanıcısına istek gönderildi! 🤝')
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

@app.route('/api/accept-friend', methods=['POST'])
@login_required
def accept_friend():
<<<<<<< HEAD
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
=======
    fid=request.get_json().get('friendship_id')
    f=db_fetchone("SELECT * FROM friendships WHERE id=? AND receiver_id=? AND status='pending'",(fid,session['user_id']))
    if not f:return jsonify(success=False)
    db_execute("UPDATE friendships SET status='accepted' WHERE id=?",(fid,))
    add_notification(f['sender_id'],'friend_accepted',f'✅ {session["username"]} kabul etti!','🎉')
    check_achievements(session['user_id']);check_achievements(f['sender_id']);db_commit()
    return jsonify(success=True,message='Kabul! 🎉')
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)

@app.route('/api/reject-friend', methods=['POST'])
@login_required
def reject_friend():
<<<<<<< HEAD
    fid = request.get_json().get('friendship_id')
    db_execute('DELETE FROM friendships WHERE id=? AND receiver_id=?',
               (fid, session['user_id']))
    db_commit()
=======
    fid=request.get_json().get('friendship_id')
    db_execute('DELETE FROM friendships WHERE id=? AND receiver_id=?',(fid,session['user_id']));db_commit()
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return jsonify(success=True)

@app.route('/api/remove-friend', methods=['POST'])
@login_required
def remove_friend():
<<<<<<< HEAD
    uid = request.get_json().get('user_id')
    db_execute(
        'DELETE FROM friendships WHERE '
        '(sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
        (session['user_id'],uid,uid,session['user_id']))
    db_commit()
=======
    uid=request.get_json().get('user_id')
    db_execute('DELETE FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',
               (session['user_id'],uid,uid,session['user_id']));db_commit()
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
    return jsonify(success=True)


# ═══════ LEADERBOARD (İKİLİ) ═══════
@app.route('/leaderboard')
@login_required
def leaderboard():
<<<<<<< HEAD
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
=======
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))

    # Global LP sıralaması
    global_lb=db_fetchall('SELECT id,username,profile_photo,total_lp,(SELECT COALESCE(SUM(duration_minutes),0) FROM study_sessions WHERE user_id=users.id) as total_study FROM users ORDER BY total_lp DESC LIMIT 50')

    # Haftalık çalışma sıralaması
    ws=(date.today()-timedelta(days=date.today().weekday())).isoformat()
    weekly_study_lb=db_fetchall('SELECT u.id,u.username,u.profile_photo,u.total_lp,COALESCE(SUM(s.duration_minutes),0) as week_mins FROM users u JOIN study_sessions s ON s.user_id=u.id AND s.session_date>=? GROUP BY u.id,u.username,u.profile_photo,u.total_lp ORDER BY week_mins DESC LIMIT 50',(ws,))

    # Deneme net sıralaması (son deneme bazında)
    deneme_lb=db_fetchall('''
        SELECT u.id,u.username,u.profile_photo,u.total_lp,d.total_net,d.mat_net,d.fiz_net,d.kim_net,d.bio_net,d.deneme_date
        FROM users u JOIN deneme_results d ON d.user_id=u.id
        WHERE d.id=(SELECT id FROM deneme_results WHERE user_id=u.id ORDER BY deneme_date DESC LIMIT 1)
        ORDER BY d.total_net DESC LIMIT 50
    ''')

    # Arkadaş LB
    fids_rows=db_fetchall("SELECT CASE WHEN sender_id=? THEN receiver_id ELSE sender_id END as fid FROM friendships WHERE (sender_id=? OR receiver_id=?) AND status='accepted'",
                          (session['user_id'],session['user_id'],session['user_id']))
    fids=[f['fid'] for f in fids_rows]+[session['user_id']]
    if len(fids)>1:
        ph=','.join(['%s' if USE_POSTGRES else '?']*len(fids))
        friends_lb=db_fetchall(f'SELECT id,username,profile_photo,total_lp,(SELECT COALESCE(SUM(duration_minutes),0) FROM study_sessions WHERE user_id=users.id) as total_study FROM users WHERE id IN ({ph}) ORDER BY total_lp DESC',fids)
    else:friends_lb=[]

    # Bugün
    today_lb=db_fetchall('SELECT u.id,u.username,u.profile_photo,u.total_lp,COALESCE(SUM(s.duration_minutes),0) as today_mins FROM users u JOIN study_sessions s ON s.user_id=u.id AND s.session_date=? GROUP BY u.id,u.username,u.profile_photo,u.total_lp ORDER BY today_mins DESC LIMIT 20',(date.today().isoformat(),))

    # Rozetler
    recent_badges=db_fetchall('SELECT wb.*,u.username,u.profile_photo FROM weekly_badges wb JOIN users u ON u.id=wb.user_id ORDER BY wb.week_start DESC LIMIT 20')

    my_pos=1
    for i,x in enumerate(global_lb):
        if x['id']==session['user_id']:my_pos=i+1;break

    return render_template('leaderboard.html',user=u,rank=get_rank(u['total_lp']),
        global_lb=global_lb,friends_lb=friends_lb,today_lb=today_lb,
        weekly_study_lb=weekly_study_lb,deneme_lb=deneme_lb,
        recent_badges=recent_badges,my_position=my_pos)


# ═══════════════ SOHBET SİSTEMİ ═══════════════

@app.route('/chat')
@login_required
def chat():
    """Sohbet listesi — arkadaşlarla son mesajlar."""
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    # Arkadaş listesi + her biriyle son mesaj
    fr=db_fetchall("""
        SELECT u.id,u.username,u.profile_photo,u.total_lp
        FROM friendships f
        JOIN users u ON (CASE WHEN f.sender_id=? THEN f.receiver_id ELSE f.sender_id END)=u.id
        WHERE (f.sender_id=? OR f.receiver_id=?) AND f.status='accepted'
        ORDER BY u.username
    """, (session['user_id'],session['user_id'],session['user_id']))

    # Her arkadaş için son mesaj ve okunmamış sayı
    chats = []
    for f in fr:
        last_msg = db_fetchone("""
            SELECT content, created_at, sender_id FROM messages
            WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
            ORDER BY created_at DESC LIMIT 1
        """, (session['user_id'],f['id'],f['id'],session['user_id']))
        unread = db_fetchone(
            'SELECT COUNT(*) as c FROM messages WHERE sender_id=? AND receiver_id=? AND is_read=0',
            (f['id'], session['user_id']))['c']
        chats.append({
            **f,
            'last_message': last_msg,
            'unread': unread
        })

    # Okunmamış mesajı olanları üste al
    chats.sort(key=lambda x: (x['unread'] > 0, x['last_message']['created_at'] if x['last_message'] else ''), reverse=True)

    return render_template('chat.html', user=u, rank=get_rank(u['total_lp']), chats=chats)

@app.route('/chat/<int:friend_id>')
@login_required
def chat_with(friend_id):
    """Belirli arkadaşla sohbet."""
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    friend=db_fetchone('SELECT id,username,profile_photo,total_lp FROM users WHERE id=?',(friend_id,))
    if not friend:flash('Kullanıcı bulunamadı.','error');return redirect(url_for('chat'))

    # Arkadaş mı kontrol et
    is_friend=db_fetchone(
        "SELECT 1 FROM friendships WHERE ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)) AND status='accepted'",
        (session['user_id'],friend_id,friend_id,session['user_id']))
    if not is_friend:flash('Bu kişiyle arkadaş değilsin.','error');return redirect(url_for('chat'))

    # Mesajları okundu işaretle
    db_execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',
               (friend_id, session['user_id']))
    db_commit()

    # Son 100 mesaj
    messages=db_fetchall("""
        SELECT m.*, u.username as sender_name, u.profile_photo as sender_photo
        FROM messages m JOIN users u ON u.id=m.sender_id
        WHERE (m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?)
        ORDER BY m.created_at ASC LIMIT 100
    """, (session['user_id'],friend_id,friend_id,session['user_id']))

    return render_template('chat_room.html', user=u, rank=get_rank(u['total_lp']),
        friend=friend, friend_rank=get_rank(friend['total_lp']), messages=messages)

@app.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    data=request.get_json()
    rid=data.get('receiver_id')
    content=data.get('content','').strip()
    if not content:return jsonify(success=False,message='Boş mesaj gönderilemez.')
    if len(content)>500:return jsonify(success=False,message='Mesaj çok uzun (max 500).')
    if not rid:return jsonify(success=False,message='Geçersiz alıcı.')

    # Arkadaş mı?
    is_friend=db_fetchone(
        "SELECT 1 FROM friendships WHERE ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)) AND status='accepted'",
        (session['user_id'],rid,rid,session['user_id']))
    if not is_friend:return jsonify(success=False,message='Arkadaş değilsiniz.')

    db_execute('INSERT INTO messages(sender_id,receiver_id,content) VALUES(?,?,?)',
               (session['user_id'],rid,content))
    check_achievements(session['user_id'])
    db_commit()

    return jsonify(success=True,message='Gönderildi.')

@app.route('/api/get-messages/<int:friend_id>')
@login_required
def get_messages(friend_id):
    """Polling ile yeni mesajları al."""
    after=request.args.get('after','0')  # Son mesaj ID'si

    # Okunmamışları okundu yap
    db_execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',
               (friend_id, session['user_id']))

    msgs=db_fetchall("""
        SELECT m.id, m.sender_id, m.content, m.created_at,
               u.username as sender_name
        FROM messages m JOIN users u ON u.id=m.sender_id
        WHERE ((m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?))
              AND m.id > ?
        ORDER BY m.created_at ASC
    """, (session['user_id'],friend_id,friend_id,session['user_id'],int(after)))
    db_commit()

    return jsonify(msgs)


# ═══════ STATS ═══════
@app.route('/stats')
@login_required
def stats():
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    sd={}
    for s in AYT_TOPICS:
        rows=db_fetchall('SELECT topic,SUM(duration_minutes) as t,COUNT(*) as c FROM study_sessions WHERE user_id=? AND subject=? GROUP BY topic ORDER BY t DESC',(session['user_id'],s))
        tot=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND subject=?',(session['user_id'],s))['t']
        sd[s]={'topics':rows,'total':tot}
    dt=db_fetchall('SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date ASC LIMIT 30',(session['user_id'],))
    ch=db_fetchall('SELECT * FROM daily_checks WHERE user_id=? AND processed=1 ORDER BY check_date DESC LIMIT 30',(session['user_id'],))
    met=sum(1 for c in ch if c['goal_met']);gpct=int(met/len(ch)*100) if ch else 0
    return render_template('stats.html',user=u,rank=get_rank(u['total_lp']),next_rank=get_next_rank(u['total_lp']),
        rank_progress=rank_progress(u['total_lp']),subj_detail=sd,deneme_trend=dt,daily_checks=ch,goal_pct=gpct,subject_icons=SUBJECT_ICONS)


# ════════════════════════════════════════
if __name__=='__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    os.makedirs('static/img/ranks',exist_ok=True)
    with app.app_context():init_db()
    app.run(debug=True,port=5000)
else:
    with app.app_context():init_db()
>>>>>>> b8452b7 (v5: chat, 30 tema, banner, isim degistirme, ikili lb)
