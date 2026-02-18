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
app.secret_key = os.environ.get('SECRET_KEY', 'local-dev-key-2024')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXT = {'png','jpg','jpeg','gif','webp'}

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
USE_POSTGRES = DATABASE_URL.startswith('postgresql')

if USE_POSTGRES:
    import psycopg2, psycopg2.extras
else:
    import sqlite3

def get_db():
    if 'db' not in g:
        if USE_POSTGRES:
            g.db = psycopg2.connect(DATABASE_URL)
            g.db.autocommit = False
        else:
            g.db = sqlite3.connect('yks_rank.db')
            g.db.row_factory = sqlite3.Row
    return g.db

def q(query):
    return query.replace('?','%s') if USE_POSTGRES else query

def db_execute(query, params=None):
    db = get_db(); query = q(query)
    if USE_POSTGRES:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = db.cursor()
    cur.execute(query, params or ())
    return cur

def make_serializable(d):
    if d is None: return None
    r = {}
    for k, v in d.items():
        if isinstance(v, datetime):
            r[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(v, date):
            r[k] = v.isoformat()
        else:
            r[k] = v
    return r

def db_fetchone(query, params=None):
    cur = db_execute(query, params)
    row = cur.fetchone(); cur.close()
    return make_serializable(dict(row)) if row else None

def db_fetchall(query, params=None):
    cur = db_execute(query, params)
    rows = cur.fetchall(); cur.close()
    return [make_serializable(dict(r)) for r in rows]

def db_commit():
    get_db().commit()

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = get_db()
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
        for col, typ, default in [
            ('username_changed_at','TIMESTAMP','NULL'),
            ('profile_banner','TEXT',"''")
        ]:
            try: cur.execute(f"ALTER TABLE users ADD COLUMN {col} {typ} DEFAULT {default}")
            except: db.rollback()
        cur.close()
    else:
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
            username_changed_at TEXT DEFAULT '',
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
        for col in ['username_changed_at','profile_banner']:
            try: db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT DEFAULT ''")
            except: pass
    db_commit()

THEMES = [
    {'id':'lol-classic','name':'LoL Classic','icon':'🎮','preview':['#0a0e13','#c89b3c','#0ac8b9']},
    {'id':'arcade','name':'Arcade','icon':'🕹️','preview':['#0d0221','#ff00ff','#00ffff']},
    {'id':'ocean','name':'Okyanus','icon':'🌊','preview':['#0a1628','#00b4d8','#48cae4']},
    {'id':'forest','name':'Orman','icon':'🌲','preview':['#0a1a0a','#88cc44','#44bb88']},
    {'id':'sunset','name':'Gün Batımı','icon':'🌅','preview':['#1a0e08','#ff6b35','#f7c948']},
    {'id':'cyberpunk','name':'Cyberpunk','icon':'💜','preview':['#0a0a1a','#ff2a6d','#05d9e8']},
    {'id':'valorant','name':'Valorant','icon':'🔴','preview':['#0f1012','#ff4655','#bd3944']},
    {'id':'snowdown','name':'Kış','icon':'❄️','preview':['#0a1520','#88ccff','#44aadd']},
    {'id':'star-guardian','name':'Yıldız','icon':'⭐','preview':['#1a0e20','#ee77aa','#aa77ee']},
    {'id':'blood-moon','name':'Kan Ayı','icon':'🌑','preview':['#1a0808','#cc2222','#ff4444']},
    {'id':'neon','name':'Neon','icon':'💡','preview':['#0a0a0a','#39ff14','#ff073a']},
    {'id':'sakura','name':'Sakura','icon':'🌸','preview':['#1a0e14','#ff99cc','#ffccdd']},
    {'id':'void','name':'Void','icon':'🕳️','preview':['#0a0014','#8844cc','#cc77ff']},
    {'id':'project','name':'Project','icon':'🤖','preview':['#0a1014','#00ccff','#0088cc']},
    {'id':'infernal','name':'Cehennem','icon':'😈','preview':['#1a0a00','#ff6600','#ffaa00']},
    {'id':'galaxy','name':'Galaksi','icon':'🌌','preview':['#0a0a1e','#6644cc','#9966ff']},
    {'id':'spirit','name':'Ruh','icon':'🦊','preview':['#0e1420','#66bbcc','#aaddee']},
    {'id':'dark-star','name':'Karanlık','icon':'⚫','preview':['#08080e','#6622aa','#9944dd']},
    {'id':'high-noon','name':'Kovboy','icon':'🤠','preview':['#1a1408','#cc8833','#eebb55']},
    {'id':'lunar','name':'Ay','icon':'🏮','preview':['#1a0a0a','#cc3333','#ffcc00']},
    {'id':'crystal','name':'Kristal','icon':'💎','preview':['#0e1418','#44cccc','#88eeff']},
    {'id':'volcanic','name':'Volkan','icon':'🌋','preview':['#1a0800','#ee4400','#ff8800']},
    {'id':'deep-sea','name':'Derin Deniz','icon':'🐙','preview':['#040e18','#004488','#0066bb']},
    {'id':'aurora','name':'Kutup Işığı','icon':'🌈','preview':['#0a1018','#00cc88','#44aaff']},
    {'id':'desert','name':'Çöl','icon':'🏜️','preview':['#1a1408','#ccaa44','#eedd88']},
    {'id':'steampunk','name':'Steampunk','icon':'⚙️','preview':['#141008','#aa7733','#cc9955']},
    {'id':'phantom','name':'Hayalet','icon':'👻','preview':['#0e0e14','#8888aa','#aaaacc']},
    {'id':'emerald-city','name':'Zümrüt Şehir','icon':'🏙️','preview':['#081a0e','#00cc66','#44ee88']},
    {'id':'ruby','name':'Yakut','icon':'❤️','preview':['#1a0808','#cc1144','#ee3366']},
    {'id':'sapphire','name':'Safir','icon':'💙','preview':['#08081a','#2244cc','#4466ee']},
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
    {'id':'first_session','name':'İlk Adım','desc':'İlk çalışma','icon':'🎯','lp':50,'category':'study'},
    {'id':'hour_1','name':'Isınma','desc':'1 saat','icon':'⏰','lp':100,'category':'study'},
    {'id':'hour_10','name':'Çalışkan','desc':'10 saat','icon':'🐝','lp':200,'category':'study'},
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
    {'id':'weekly_champ','name':'Şampiyon','desc':'Haftanın en iyisi','icon':'🏆','lp':200,'category':'weekly'},
    {'id':'rank_bronze','name':'Bronz','desc':'Bronz ol','icon':'🛡️','lp':0,'category':'rank'},
    {'id':'rank_silver','name':'Gümüş','desc':'Gümüş ol','icon':'⚡','lp':0,'category':'rank'},
    {'id':'rank_gold','name':'Altın','desc':'Altın ol','icon':'👑','lp':0,'category':'rank'},
    {'id':'rank_platinum','name':'Platin','desc':'Platin ol','icon':'💎','lp':0,'category':'rank'},
    {'id':'rank_emerald','name':'Zümrüt','desc':'Zümrüt ol','icon':'🔮','lp':0,'category':'rank'},
    {'id':'rank_diamond','name':'Elmas','desc':'Elmas ol','icon':'💠','lp':0,'category':'rank'},
    {'id':'rank_master','name':'Ustalık','desc':'Usta ol','icon':'🏆','lp':0,'category':'rank'},
    {'id':'rank_grandmaster','name':'Üstatlık','desc':'Üstat ol','icon':'🌟','lp':0,'category':'rank'},
    {'id':'rank_challenger','name':'Challenger','desc':'Challenger ol','icon':'🔥','lp':0,'category':'rank'},
]
ACHIEVEMENT_MAP = {a['id']:a for a in ACHIEVEMENTS}

AYT_TOPICS = {
    'Matematik':['Temel Kavramlar','Sayı Basamakları','Bölme-Bölünebilme','EBOB-EKOK','Rasyonel Sayılar','Eşitsizlikler','Mutlak Değer','Üslü Sayılar','Köklü Sayılar','Çarpanlara Ayırma','Oran Orantı','Denklem','Problemler (Sayı-Kesir-Yaş)','Problemler (İşçi-Havuz-Yüzde)','Problemler (Hareket-Karışım)','Kümeler','Fonksiyonlar','Polinomlar','2.Derece Denklemler','Permütasyon-Kombinasyon','Binom','Olasılık','İstatistik','Logaritma','Diziler','Limit','Türev','İntegral','Trigonometri','Analitik Geometri','Karmaşık Sayılar'],
    'Fizik':['Vektörler','Kuvvet-Denge','Tork','Doğrusal Hareket','İvmeli Hareket','Newton','İş-Güç-Enerji','Momentum','Elektrik Alan','Sığa','Manyetizma','İndüksiyon','AC','Dalga','Atom Fiziği','Radyoaktivite','Basınç','Optik'],
    'Kimya':['Atom-Periyodik','Etkileşimler','Madde Halleri','Mol-Stokiyometri','Tepkimeler','Asit-Baz','Karışımlar','Çözeltiler','Denge','Termokimya','Hız','Elektrokimya','Organik','Çekirdek'],
    'Biyoloji':['Hücre','Bölünmeler','Kalıtım','Ekosistem','Bitki','Enerji','Sindirim','Dolaşım','Solunum','Boşaltım','Sinir','Endokrin','Duyu','Hareket','Üreme','Popülasyon','Sınıflandırma'],
}
SUBJECT_ICONS = {'Matematik':'📐','Fizik':'⚡','Kimya':'🧪','Biyoloji':'🧬'}

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

def get_rank(lp):
    c=RANKS[0]
    for r in RANKS:
        if lp>=r['min_lp']:c=r
        else:break
    return c

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

def get_photo_url(v):
    if not v or v=='default.png':return None
    if v.startswith('http'):return v
    return url_for('static',filename='uploads/'+v)

def add_notification(uid,ntype,msg,icon='🔔'):
    db_execute('INSERT INTO notifications(user_id,ntype,message,icon) VALUES(?,?,?,?)',(uid,ntype,msg,icon))

def get_streak(uid):
    u=db_fetchone('SELECT daily_goal_minutes FROM users WHERE id=?',(uid,))
    if not u:return 0
    goal=u['daily_goal_minutes'];s=0;d=date.today()-timedelta(days=1)
    while True:
        r=db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? AND session_date=?',(uid,d.isoformat()))
        if r and r['t']>=goal:s+=1;d-=timedelta(days=1)
        else:break
    return s

def get_friend_count(uid):
    r=db_fetchone("SELECT COUNT(*) as c FROM friendships WHERE (sender_id=? OR receiver_id=?) AND status='accepted'",(uid,uid))
    return r['c'] if r else 0

def get_unread_messages(uid):
    r=db_fetchone('SELECT COUNT(*) as c FROM messages WHERE receiver_id=? AND is_read=0',(uid,))
    return r['c'] if r else 0

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
    mc=db_fetchone('SELECT COUNT(*) as c FROM messages WHERE sender_id=?',(uid,))['c']
    checks={
        'first_session':ts>=1,'hour_1':th>=1,'hour_10':th>=10,'hour_50':th>=50,
        'hour_100':th>=100,'hour_200':th>=200,
        'streak_3':streak>=3,'streak_7':streak>=7,'streak_14':streak>=14,'streak_30':streak>=30,
        'pomo_1':tp>=1,'pomo_25':tp>=25,'pomo_100':tp>=100,
        'deneme_1':td>=1,'deneme_5':td>=5,
        'first_friend':friends>=1,'friends_5':friends>=5,'first_message':mc>=1,
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
            a=ACHIEVEMENT_MAP[aid]
            db_execute('INSERT INTO user_achievements(user_id,achievement_id) VALUES(?,?)',(uid,aid))
            if a['lp']>0:db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(a['lp'],uid))
            add_notification(uid,'achievement',f"🏅 {a['name']}: {a['desc']} (+{a['lp']} LP)",a['icon'])
            new.append(a)
    db_commit()
    return new

def process_weekly_badges():
    today=date.today()
    if today.weekday()!=0:return
    we=today-timedelta(days=1);ws=we-timedelta(days=6)
    if db_fetchone('SELECT id FROM weekly_badges WHERE week_start=? LIMIT 1',(ws.isoformat(),)):return
    for qs,bt,bn,bi in [
        ('SELECT user_id,SUM(duration_minutes) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_study','👑 Çalışma Kralı','👑'),
        ('SELECT user_id,SUM(pomodoro_cycles) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? AND is_pomodoro=1 GROUP BY user_id ORDER BY total DESC LIMIT 1','top_pomo','🍅 Pomo Ustası','🍅'),
        ('SELECT user_id,MAX(total_net) as total FROM deneme_results WHERE deneme_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_deneme','📊 Deneme Şampiyonu','📊'),
        ('SELECT user_id,SUM(lp_earned) as total FROM study_sessions WHERE session_date BETWEEN ? AND ? GROUP BY user_id ORDER BY total DESC LIMIT 1','top_lp','⚡ LP Avcısı','⚡'),
    ]:
        w=db_fetchone(qs,(ws.isoformat(),we.isoformat()))
        if w and w.get('user_id'):
            db_execute('INSERT INTO weekly_badges(user_id,badge_type,badge_name,badge_icon,week_start,week_end,stat_value) VALUES(?,?,?,?,?,?,?)',
                       (w['user_id'],bt,bn,bi,ws.isoformat(),we.isoformat(),str(w.get('total',''))))
            add_notification(w['user_id'],'weekly_badge',f'{bi} {bn}! +200 LP',bi)
            db_execute('UPDATE users SET total_lp=total_lp+200 WHERE id=?',(w['user_id'],))
    db_commit()

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
        if mins>=goal:lc,met=200,1
        elif mins>0:lc=max(-int((goal-mins)/goal*30),-30);met=0
        else:lc,met=-20,0
        if ex:db_execute('UPDATE daily_checks SET total_minutes=?,goal_met=?,lp_change=?,processed=1 WHERE id=?',(mins,met,lc,ex['id']))
        else:db_execute('INSERT INTO daily_checks(user_id,check_date,total_minutes,goal_met,lp_change,processed) VALUES(?,?,?,?,?,1)',(uid,d.isoformat(),mins,met,lc))
        db_execute(f'UPDATE users SET total_lp={mx}(0,total_lp+?) WHERE id=?',(lc,uid))
    streak=get_streak(uid)
    for sd,sl in {3:50,7:150,14:300,30:500}.items():
        if streak==sd:
            db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(sl,uid))
            add_notification(uid,'streak',f'🔥 {sd} gün seri! +{sl} LP','🔥')
    check_achievements(uid);db_commit()

@app.context_processor
def inject_globals():
    unread=0;unread_msgs=0
    if 'user_id' in session:
        r=db_fetchone('SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND is_read=0',(session['user_id'],))
        unread=r['c'] if r else 0
        unread_msgs=get_unread_messages(session['user_id'])
    return {'current_theme':session.get('theme','lol-classic'),'all_themes':THEMES,
            'all_ranks':RANKS,'unread_notifs':unread,'unread_msgs':unread_msgs,
            'get_photo_url':get_photo_url,'get_rank':get_rank}

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        un=request.form.get('username','').strip();pw=request.form.get('password','');pw2=request.form.get('password_confirm','')
        if not un or not pw:flash('Gerekli.','error');return redirect(url_for('register'))
        if len(un)<3:flash('En az 3 karakter.','error');return redirect(url_for('register'))
        if len(pw)<6:flash('Şifre en az 6.','error');return redirect(url_for('register'))
        if pw!=pw2:flash('Eşleşmiyor.','error');return redirect(url_for('register'))
        if db_fetchone('SELECT 1 FROM users WHERE username=?',(un,)):flash('Alınmış.','error');return redirect(url_for('register'))
        db_execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(un,generate_password_hash(pw)));db_commit()
        u=db_fetchone('SELECT id FROM users WHERE username=?',(un,))
        session['user_id']=u['id'];session['username']=un;session['theme']='lol-classic'
        flash('Kayıt başarılı!','success');return redirect(url_for('setup_goals'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        un=request.form.get('username','').strip();pw=request.form.get('password','')
        u=db_fetchone('SELECT * FROM users WHERE username=?',(un,))
        if u and check_password_hash(u['password_hash'],pw):
            session['user_id']=u['id'];session['username']=u['username'];session['theme']=u.get('theme','lol-classic')
            check_daily_goals(u['id'])
            if not u['goals_set']:return redirect(url_for('setup_goals'))
            flash(f'Hoş geldin, {un}! 🎮','success');return redirect(url_for('dashboard'))
        flash('Hatalı.','error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear();flash('Çıkış.','info');return redirect(url_for('login'))

@app.route('/setup-goals', methods=['GET','POST'])
@login_required
def setup_goals():
    if request.method=='POST':
        db_execute('UPDATE users SET daily_goal_minutes=?,target_university=?,target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,goals_set=1 WHERE id=?',
                   (int(float(request.form.get('daily_hours',6))*60),request.form.get('target_university',''),
                    float(request.form.get('target_mat_net',0)),float(request.form.get('target_fiz_net',0)),
                    float(request.form.get('target_kim_net',0)),float(request.form.get('target_bio_net',0)),session['user_id']))
        db_commit();flash('Hedefler kaydedildi! 🚀','success');return redirect(url_for('dashboard'))
    return render_template('setup_goals.html')

@app.route('/api/set-theme', methods=['POST'])
@login_required
def set_theme():
    tid=request.get_json().get('theme','lol-classic')
    if tid not in [t['id'] for t in THEMES]:return jsonify(success=False)
    db_execute('UPDATE users SET theme=? WHERE id=?',(tid,session['user_id']));db_commit();session['theme']=tid
    return jsonify(success=True)

@app.route('/api/notifications')
@login_required
def get_notifications():
    n=db_fetchall('SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 20',(session['user_id'],))
    db_execute('UPDATE notifications SET is_read=1 WHERE user_id=? AND is_read=0',(session['user_id'],));db_commit()
    return jsonify(n)

@app.route('/api/change-username', methods=['POST'])
@login_required
def change_username():
    nn=request.get_json().get('new_username','').strip()
    if not nn or len(nn)<3:return jsonify(success=False,message='En az 3 karakter.')
    if len(nn)>20:return jsonify(success=False,message='En fazla 20.')
    u=db_fetchone('SELECT username,username_changed_at FROM users WHERE id=?',(session['user_id'],))
    if u['username']==nn:return jsonify(success=False,message='Zaten bu isimdesin.')
    if u.get('username_changed_at') and u['username_changed_at']:
        try:
            lc=datetime.strptime(str(u['username_changed_at'])[:19],'%Y-%m-%d %H:%M:%S')
            d=(datetime.now()-lc).days
            if d<7:return jsonify(success=False,message=f'{7-d} gün bekle.')
        except:pass
    if db_fetchone('SELECT 1 FROM users WHERE username=?',(nn,)):return jsonify(success=False,message='Bu isim alınmış.')
    db_execute('UPDATE users SET username=?,username_changed_at=? WHERE id=?',(nn,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),session['user_id']))
    db_commit();session['username']=nn
    return jsonify(success=True,message=f'İsmin "{nn}" oldu! 🎉')

@app.route('/dashboard')
@login_required
def dashboard():
    check_daily_goals(session['user_id'])
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
    return render_template('dashboard.html',user=u,rank=r,next_rank=nr,rank_progress=prog,today_mins=today_mins,total_mins=total_mins,today_pomodoros=today_pomos,last_deneme=last_deneme,weekly=weekly,subj_stats=subj_stats,streak=streak,subject_icons=SUBJECT_ICONS,recent_achievements=ra,lb_position=lb_pos,total_users=tu,pending_requests=pr,my_badges=mb)

@app.route('/study')
@login_required
def study():
    return render_template('study.html',subjects=AYT_TOPICS,icons=SUBJECT_ICONS)

@app.route('/study/<subject>')
@login_required
def study_subject(subject):
    if subject not in AYT_TOPICS:flash('Geçersiz.','error');return redirect(url_for('study'))
    return render_template('study_topics.html',subject=subject,topics=AYT_TOPICS[subject],icon=SUBJECT_ICONS.get(subject,'📚'))

@app.route('/study/<subject>/<int:tidx>')
@login_required
def study_timer(subject,tidx):
    if subject not in AYT_TOPICS or tidx>=len(AYT_TOPICS[subject]):flash('Geçersiz.','error');return redirect(url_for('study'))
    u=db_fetchone('SELECT pomodoro_work,pomodoro_break FROM users WHERE id=?',(session['user_id'],))
    return render_template('timer.html',subject=subject,topic=AYT_TOPICS[subject][tidx],icon=SUBJECT_ICONS.get(subject,'📚'),pomo_work=u['pomodoro_work'] or 25,pomo_break=u['pomodoro_break'] or 5)

@app.route('/api/save-session', methods=['POST'])
@login_required
def save_session():
    d=request.get_json();subj=d.get('subject','');topic=d.get('topic','')
    mins=int(d.get('duration_minutes',0));is_p=int(d.get('is_pomodoro',0));pc=int(d.get('pomodoro_cycles',0))
    if mins<1:return jsonify(success=False,message='En az 1 dk!')
    lp=(mins*2)+(pc*15 if is_p else 0)
    old_lp=db_fetchone('SELECT total_lp FROM users WHERE id=?',(session['user_id'],))['total_lp']
    old_r=get_rank(old_lp)
    db_execute('INSERT INTO study_sessions(user_id,subject,topic,duration_minutes,lp_earned,is_pomodoro,pomodoro_cycles,session_date) VALUES(?,?,?,?,?,?,?,?)',(session['user_id'],subj,topic,mins,lp,is_p,pc,date.today().isoformat()))
    db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(lp,session['user_id']))
    u=db_fetchone('SELECT total_lp FROM users WHERE id=?',(session['user_id'],))
    new_r=get_rank(u['total_lp']);ru=old_r['name']!=new_r['name']
    if ru:add_notification(session['user_id'],'rankup',f"🎉 {new_r['name']}!",new_r['icon'])
    na=check_achievements(session['user_id']);db_commit()
    return jsonify(success=True,lp_earned=lp,total_lp=u['total_lp'],rank=new_r['name'],rank_img=new_r['img'],rank_color=new_r['color'],rank_up=ru,new_rank_name=new_r['name'] if ru else None,new_achievements=[{'name':a['name'],'icon':a['icon'],'lp':a['lp']} for a in na],message=f'+{lp} LP! 🎉')

@app.route('/deneme', methods=['GET','POST'])
@login_required
def deneme():
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    if request.method=='POST':
        mn=float(request.form.get('mat_net',0));fn=float(request.form.get('fiz_net',0))
        kn=float(request.form.get('kim_net',0));bn=float(request.form.get('bio_net',0))
        dd=request.form.get('deneme_date',date.today().isoformat());tn=mn+fn+kn+bn
        tgt=u['target_mat_net']+u['target_fiz_net']+u['target_kim_net']+u['target_bio_net']
        lp=int((tn/tgt)*400) if tgt>0 else int(tn*4);lp=max(0,min(lp,800))
        db_execute('INSERT INTO deneme_results(user_id,mat_net,fiz_net,kim_net,bio_net,total_net,lp_earned,deneme_date) VALUES(?,?,?,?,?,?,?,?)',(session['user_id'],mn,fn,kn,bn,tn,lp,dd))
        db_execute('UPDATE users SET total_lp=total_lp+? WHERE id=?',(lp,session['user_id']))
        check_achievements(session['user_id']);db_commit();flash(f'+{lp} LP','success');return redirect(url_for('deneme'))
    hist=db_fetchall('SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 20',(session['user_id'],))
    return render_template('deneme.html',user=u,history=hist)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        if 'profile_photo' in request.files:
            f=request.files['profile_photo']
            if f and f.filename and allowed_file(f.filename):
                fn=secure_filename(f"u{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],fn))
                db_execute('UPDATE users SET profile_photo=? WHERE id=?',(fn,session['user_id']));db_commit();flash('PP güncellendi!','success')
        if 'profile_banner' in request.files:
            f=request.files['profile_banner']
            if f and f.filename and allowed_file(f.filename):
                fn=secure_filename(f"b{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],fn))
                db_execute('UPDATE users SET profile_banner=? WHERE id=?',(fn,session['user_id']));db_commit();flash('Banner güncellendi!','success')
        if 'daily_hours' in request.form:
            db_execute('UPDATE users SET daily_goal_minutes=?,target_university=?,target_mat_net=?,target_fiz_net=?,target_kim_net=?,target_bio_net=?,pomodoro_work=?,pomodoro_break=? WHERE id=?',
                       (int(float(request.form.get('daily_hours',6))*60),request.form.get('target_university',''),float(request.form.get('target_mat_net',0)),float(request.form.get('target_fiz_net',0)),float(request.form.get('target_kim_net',0)),float(request.form.get('target_bio_net',0)),int(request.form.get('pomodoro_work',25)),int(request.form.get('pomodoro_break',5)),session['user_id']))
            db_commit();flash('Güncellendi!','success')
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    stats={'sessions':db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',(session['user_id'],))['c'],'total_mins':db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(session['user_id'],))['t'],'denemes':db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',(session['user_id'],))['c'],'active_days':db_fetchone('SELECT COUNT(DISTINCT session_date) as d FROM study_sessions WHERE user_id=?',(session['user_id'],))['d'],'pomodoros':db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',(session['user_id'],))['t']}
    earned_ids={a['achievement_id'] for a in db_fetchall('SELECT achievement_id FROM user_achievements WHERE user_id=?',(session['user_id'],))}
    wb=db_fetchall('SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC',(session['user_id'],))
    can_change=True;cooldown=0
    if u.get('username_changed_at') and u['username_changed_at']:
        try:
            lc=datetime.strptime(str(u['username_changed_at'])[:19],'%Y-%m-%d %H:%M:%S');d=(datetime.now()-lc).days
            if d<7:can_change=False;cooldown=7-d
        except:pass
    return render_template('profile.html',user=u,rank=get_rank(u['total_lp']),stats=stats,achievements=ACHIEVEMENTS,earned_ids=earned_ids,weekly_badges=wb,can_change_name=can_change,name_cooldown_days=cooldown)

@app.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    if user_id==session['user_id']:return redirect(url_for('profile'))
    t=db_fetchone('SELECT * FROM users WHERE id=?',(user_id,))
    if not t:flash('Bulunamadı.','error');return redirect(url_for('leaderboard'))
    tr=get_rank(t['total_lp'])
    stats={'sessions':db_fetchone('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=?',(user_id,))['c'],'total_mins':db_fetchone('SELECT COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=?',(user_id,))['t'],'denemes':db_fetchone('SELECT COUNT(*) as c FROM deneme_results WHERE user_id=?',(user_id,))['c'],'active_days':db_fetchone('SELECT COUNT(DISTINCT session_date) as d FROM study_sessions WHERE user_id=?',(user_id,))['d'],'pomodoros':db_fetchone('SELECT COALESCE(SUM(pomodoro_cycles),0) as t FROM study_sessions WHERE user_id=? AND is_pomodoro=1',(user_id,))['t']}
    subj_stats=db_fetchall('SELECT subject,COALESCE(SUM(duration_minutes),0) as t FROM study_sessions WHERE user_id=? GROUP BY subject ORDER BY t DESC',(user_id,))
    last_deneme=db_fetchone('SELECT * FROM deneme_results WHERE user_id=? ORDER BY deneme_date DESC LIMIT 1',(user_id,))
    earned_ids={a['achievement_id'] for a in db_fetchall('SELECT achievement_id FROM user_achievements WHERE user_id=?',(user_id,))}
    wb=db_fetchall('SELECT * FROM weekly_badges WHERE user_id=? ORDER BY week_start DESC LIMIT 10',(user_id,))
    fs=db_fetchone("SELECT * FROM friendships WHERE ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?))",(session['user_id'],user_id,user_id,session['user_id']))
    is_friend=fs and fs['status']=='accepted';is_pending=fs and fs['status']=='pending'
    lb_pos=db_fetchone('SELECT COUNT(*)+1 as pos FROM users WHERE total_lp>?',(t['total_lp'],))['pos']
    return render_template('user_profile.html',target=t,target_rank=tr,stats=stats,subj_stats=subj_stats,last_deneme=last_deneme,earned_ids=earned_ids,weekly_badges=wb,achievements=ACHIEVEMENTS,subject_icons=SUBJECT_ICONS,is_friend=is_friend,is_pending=is_pending,lb_position=lb_pos)

@app.route('/friends')
@login_required
def friends():
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    fr=db_fetchall("SELECT u.id,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON (CASE WHEN f.sender_id=? THEN f.receiver_id ELSE f.sender_id END)=u.id WHERE (f.sender_id=? OR f.receiver_id=?) AND f.status='accepted' ORDER BY u.total_lp DESC",(session['user_id'],session['user_id'],session['user_id']))
    inc=db_fetchall("SELECT f.id as fid,u.id as uid,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON u.id=f.sender_id WHERE f.receiver_id=? AND f.status='pending'",(session['user_id'],))
    out=db_fetchall("SELECT f.id as fid,u.id as uid,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON u.id=f.receiver_id WHERE f.sender_id=? AND f.status='pending'",(session['user_id'],))
    return render_template('friends.html',user=u,rank=get_rank(u['total_lp']),friends=fr,incoming=inc,outgoing=out)

@app.route('/api/add-friend', methods=['POST'])
@login_required
def add_friend():
    un=request.get_json().get('username','').strip()
    if not un:return jsonify(success=False,message='İsim gir.')
    t=db_fetchone('SELECT id FROM users WHERE username=?',(un,))
    if not t:return jsonify(success=False,message='Bulunamadı.')
    if t['id']==session['user_id']:return jsonify(success=False,message='Kendini ekleyemezsin 😄')
    ex=db_fetchone('SELECT * FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',(session['user_id'],t['id'],t['id'],session['user_id']))
    if ex:
        if ex['status']=='accepted':return jsonify(success=False,message='Zaten arkadaşsınız!')
        return jsonify(success=False,message='İstek mevcut.')
    db_execute("INSERT INTO friendships(sender_id,receiver_id,status) VALUES(?,?,'pending')",(session['user_id'],t['id']))
    add_notification(t['id'],'friend_request',f'📩 {session["username"]} arkadaşlık isteği!','🤝');db_commit()
    return jsonify(success=True,message=f'{un} kullanıcısına istek gönderildi! 🤝')

@app.route('/api/add-friend-by-id', methods=['POST'])
@login_required
def add_friend_by_id():
    tid=request.get_json().get('user_id')
    if not tid:return jsonify(success=False,message='Geçersiz.')
    if int(tid)==session['user_id']:return jsonify(success=False,message='Kendini ekleyemezsin 😄')
    t=db_fetchone('SELECT id,username FROM users WHERE id=?',(tid,))
    if not t:return jsonify(success=False,message='Bulunamadı.')
    ex=db_fetchone('SELECT * FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',(session['user_id'],tid,tid,session['user_id']))
    if ex:
        if ex['status']=='accepted':return jsonify(success=False,message='Zaten arkadaşsınız!')
        return jsonify(success=False,message='İstek mevcut.')
    db_execute("INSERT INTO friendships(sender_id,receiver_id,status) VALUES(?,?,'pending')",(session['user_id'],tid))
    add_notification(tid,'friend_request',f'📩 {session["username"]} arkadaşlık isteği!','🤝');db_commit()
    return jsonify(success=True,message=f'{t["username"]} kullanıcısına istek gönderildi! 🤝')

@app.route('/api/accept-friend', methods=['POST'])
@login_required
def accept_friend():
    fid=request.get_json().get('friendship_id')
    f=db_fetchone("SELECT * FROM friendships WHERE id=? AND receiver_id=? AND status='pending'",(fid,session['user_id']))
    if not f:return jsonify(success=False)
    db_execute("UPDATE friendships SET status='accepted' WHERE id=?",(fid,))
    add_notification(f['sender_id'],'friend_accepted',f'✅ {session["username"]} kabul etti!','🎉')
    check_achievements(session['user_id']);check_achievements(f['sender_id']);db_commit()
    return jsonify(success=True,message='Kabul! 🎉')

@app.route('/api/reject-friend', methods=['POST'])
@login_required
def reject_friend():
    fid=request.get_json().get('friendship_id')
    db_execute('DELETE FROM friendships WHERE id=? AND receiver_id=?',(fid,session['user_id']));db_commit()
    return jsonify(success=True)

@app.route('/api/remove-friend', methods=['POST'])
@login_required
def remove_friend():
    uid=request.get_json().get('user_id')
    db_execute('DELETE FROM friendships WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)',(session['user_id'],uid,uid,session['user_id']));db_commit()
    return jsonify(success=True)

@app.route('/leaderboard')
@login_required
def leaderboard():
    # Giriş yapan kullanıcıyı al
    u = db_fetchone('SELECT * FROM users WHERE id=?', (session['user_id'],))
    
    # Liderlik tabloları verileri
    global_lb = db_fetchall('SELECT username, total_lp, profile_photo FROM users ORDER BY total_lp DESC LIMIT 100')
    
    friends_lb = db_fetchall('''
        SELECT u.username, u.total_lp, u.profile_photo FROM users u 
        JOIN friendships f ON (f.user_id=? AND f.friend_id=u.id) OR (f.friend_id=? AND f.user_id=u.id)
        WHERE f.status='accepted'
        UNION
        SELECT username, total_lp, profile_photo FROM users WHERE id=?
        ORDER BY total_lp DESC
    ''', (session['user_id'], session['user_id'], session['user_id']))
    
    today_str = date.today().isoformat()
    today_lb = db_fetchall('''
        SELECT u.username, SUM(s.duration_minutes) as daily_total, u.profile_photo 
        FROM study_sessions s JOIN users u ON s.user_id=u.id 
        WHERE s.start_time LIKE ? GROUP BY u.id ORDER BY daily_total DESC LIMIT 50
    ''', (today_str + '%',))
    
    one_week_ago = (date.today() - timedelta(days=7)).isoformat()
    weekly_study_lb = db_fetchall('''
        SELECT u.username, SUM(s.duration_minutes) as weekly_total, u.profile_photo 
        FROM study_sessions s JOIN users u ON s.user_id=u.id 
        WHERE s.start_time >= ? GROUP BY u.id ORDER BY weekly_total DESC LIMIT 50
    ''', (one_week_ago,))
    
    deneme_lb = db_fetchall('''
        SELECT u.username, MAX(d.net_total) as best_net, u.profile_photo 
        FROM deneme_results d JOIN users u ON d.user_id=u.id 
        GROUP BY u.id ORDER BY best_net DESC LIMIT 50
    ''')

    recent_badges = db_fetchall('''
        SELECT u.username, a.badge_name, a.earned_at 
        FROM user_achievements a JOIN users u ON a.user_id=u.id 
        ORDER BY a.earned_at DESC LIMIT 15
    ''')

    all_users = db_fetchall('SELECT id FROM users ORDER BY total_lp DESC')
    my_pos = next((i + 1 for i, usr in enumerate(all_users) if usr['id'] == session['user_id']), 0)

    # HTML'in beklediği profil verilerini 'u' (mevcut kullanıcı) üzerinden ata
    target_rank = get_rank(u['total_lp'])
    earned_achievements = db_fetchall('SELECT achievement_id FROM user_achievements WHERE user_id=?', (u['id'],))
    earned_ids = [row['achievement_id'] for row in earned_achievements]

    return render_template('leaderboard.html', 
                           user=u, 
                           target=u, 
                           target_rank=target_rank,
                           earned_ids=earned_ids,
                           achievements=ACHIEVEMENT_LIST,
                           all_ranks=RANKS,
                           rank=target_rank, 
                           global_lb=global_lb, 
                           friends_lb=friends_lb, 
                           today_lb=today_lb, 
                           weekly_study_lb=weekly_study_lb, 
                           deneme_lb=deneme_lb, 
                           recent_badges=recent_badges, 
                           my_position=my_pos)

@app.route('/chat')
@login_required
def chat():
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    fr=db_fetchall("SELECT u.id,u.username,u.profile_photo,u.total_lp FROM friendships f JOIN users u ON (CASE WHEN f.sender_id=? THEN f.receiver_id ELSE f.sender_id END)=u.id WHERE (f.sender_id=? OR f.receiver_id=?) AND f.status='accepted' ORDER BY u.username",(session['user_id'],session['user_id'],session['user_id']))
    chats=[]
    for f in fr:
        lm=db_fetchone("SELECT content,created_at,sender_id FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY created_at DESC LIMIT 1",(session['user_id'],f['id'],f['id'],session['user_id']))
        ur=db_fetchone('SELECT COUNT(*) as c FROM messages WHERE sender_id=? AND receiver_id=? AND is_read=0',(f['id'],session['user_id']))['c']
        chats.append({'id':f['id'],'username':f['username'],'profile_photo':f.get('profile_photo','default.png'),'total_lp':f['total_lp'],'last_message':lm,'unread':ur})
    def sk(x):
        h=1 if x['unread']>0 else 0
        lt=str(x['last_message']['created_at']) if x['last_message'] and x['last_message'].get('created_at') else ''
        return(h,lt)
    chats.sort(key=sk,reverse=True)
    return render_template('chat.html',user=u,rank=get_rank(u['total_lp']),chats=chats)

@app.route('/chat/<int:friend_id>')
@login_required
def chat_with(friend_id):
    u=db_fetchone('SELECT * FROM users WHERE id=?',(session['user_id'],))
    friend=db_fetchone('SELECT id,username,profile_photo,total_lp FROM users WHERE id=?',(friend_id,))
    if not friend:flash('Bulunamadı.','error');return redirect(url_for('chat'))
    is_f=db_fetchone("SELECT 1 FROM friendships WHERE ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)) AND status='accepted'",(session['user_id'],friend_id,friend_id,session['user_id']))
    if not is_f:flash('Arkadaş değilsiniz.','error');return redirect(url_for('chat'))
    db_execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',(friend_id,session['user_id']));db_commit()
    msgs=db_fetchall("SELECT m.id,m.sender_id,m.receiver_id,m.content,m.created_at,u.username as sender_name FROM messages m JOIN users u ON u.id=m.sender_id WHERE (m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?) ORDER BY m.created_at ASC LIMIT 100",(session['user_id'],friend_id,friend_id,session['user_id']))
    return render_template('chat_room.html',user=u,rank=get_rank(u['total_lp']),friend=friend,friend_rank=get_rank(friend['total_lp']),messages=msgs)

@app.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    d=request.get_json();rid=d.get('receiver_id');content=d.get('content','').strip()
    if not content:return jsonify(success=False,message='Boş mesaj.')
    if len(content)>500:return jsonify(success=False,message='Çok uzun.')
    if not rid:return jsonify(success=False,message='Geçersiz.')
    is_f=db_fetchone("SELECT 1 FROM friendships WHERE ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)) AND status='accepted'",(session['user_id'],rid,rid,session['user_id']))
    if not is_f:return jsonify(success=False,message='Arkadaş değilsiniz.')
    db_execute('INSERT INTO messages(sender_id,receiver_id,content) VALUES(?,?,?)',(session['user_id'],rid,content))
    check_achievements(session['user_id']);db_commit()
    return jsonify(success=True)

@app.route('/api/get-messages/<int:friend_id>')
@login_required
def get_messages_api(friend_id):
    after=request.args.get('after','0')
    try:after_id=int(after)
    except:after_id=0
    db_execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',(friend_id,session['user_id']))
    msgs=db_fetchall("SELECT m.id,m.sender_id,m.content,m.created_at,u.username as sender_name FROM messages m JOIN users u ON u.id=m.sender_id WHERE ((m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?)) AND m.id>? ORDER BY m.created_at ASC",(session['user_id'],friend_id,friend_id,session['user_id'],after_id))
    db_commit()
    return jsonify(msgs)

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
    return render_template('stats.html',user=u,rank=get_rank(u['total_lp']),next_rank=get_next_rank(u['total_lp']),rank_progress=rank_progress(u['total_lp']),subj_detail=sd,deneme_trend=dt,daily_checks=ch,goal_pct=gpct,subject_icons=SUBJECT_ICONS)

if __name__=='__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    os.makedirs('static/img/ranks',exist_ok=True)
    with app.app_context():init_db()
    app.run(debug=True,port=5000)
else:
    with app.app_context():init_db()