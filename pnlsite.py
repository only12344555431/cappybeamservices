from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(150), default='default.jpg')
    threads = db.relationship('Thread', backref='user', lazy=True)
    posts = db.relationship('Post', backref='user', lazy=True)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts = db.relationship('Post', backref='thread', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Reset database to ensure schema consistency
with app.app_context():
    db.drop_all()
    db.create_all()

# Common navigation bar HTML to include in all templates
NAVBAR = '''
<div class="navbar">
    <div class="nav-left">
        <a href="{{ url_for('forum') }}">C7KA Forum</a>
    </div>
    <div class="nav-right">
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('user_profile', username=current_user.username) }}">{{ current_user.username }}</a> |
            <a href="{{ url_for('profile') }}">Profil</a> |
            <a href="{{ url_for('logout') }}">Çıkış</a>
        {% else %}
            <a href="{{ url_for('login') }}">Giriş</a> |
            <a href="{{ url_for('register') }}">Kayıt</a>
        {% endif %}
    </div>
</div>
<style>
    .navbar { 
        background: #222; 
        padding: 10px 20px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        border-bottom: 1px solid #ff9500; 
        position: fixed; 
        top: 0; 
        width: 100%; 
        z-index: 1000; 
    }
    .nav-left a, .nav-right a { 
        color: #ff9500; 
        text-decoration: none; 
        margin: 0 10px; 
    }
    .nav-left a:hover, .nav-right a:hover { 
        text-shadow: 0 0 5px #ff9500; 
    }
    body { 
        padding-top: 60px; /* Space for fixed navbar */
    }
</style>
'''

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>C7KA Forum</title>
    <style>
        body { background: black; color: #ff5555; font-family: 'Courier New', monospace; margin: 0; }
        #intro { display: flex; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: black; z-index: 999; justify-content: center; align-items: center; }
        #intro-text { color: #00ff00; font-size: 32px; white-space: pre-wrap; text-align: center; text-shadow: 0 0 10px #00ff00; }
        .hidden { display: none; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div id="intro">
        <pre id="intro-text"></pre>
    </div>
    <script>
        const introText = `root@kali:~$ sudo systemctl start c7ka-forum
[OK] Initializing C7KA Forum Network...
[OK] System Root Login Successful
[OK] Accessing Cehennem Interface...`;
        const introElement = document.getElementById('intro-text');
        let i = 0;
        const typingSpeed = 30;
        function typeWriter() {
            if (i < introText.length) {
                introElement.textContent += introText.charAt(i);
                i++;
                setTimeout(typeWriter, typingSpeed);
            } else {
                const remainingTime = 4000 - (i * typingSpeed);
                setTimeout(() => {
                    window.location.href = "{{ url_for('forum') }}";
                }, remainingTime > 0 ? remainingTime : 0);
            }
        }
        typeWriter();
    </script>
</body>
</html>
''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, password_hash=password)
        db.session.add(user)
        db.session.commit()
        flash('Kayıt başarılı!')
        return redirect(url_for('login'))
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Kayıt - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        input { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>Kayıt Ol</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p style="color: #00ff00;">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <input type="text" name="username" placeholder="Kullanıcı Adı" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Kayıt Ol</button>
        </form>
    </div>
</body>
</html>
''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('forum'))
        flash('Giriş başarısız!')
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Giriş - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        input { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>Giriş Yap</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p style="color: #00ff00;">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <input type="text" name="username" placeholder="Kullanıcı Adı" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Giriş Yap</button>
        </form>
    </div>
</body>
</html>
''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('forum'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.bio = request.form['bio']
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_pic = filename
        db.session.commit()
        flash('Profil güncellendi!')
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Profil - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        img { max-width: 100px; border-radius: 50%; border: 2px solid #ff9500; }
        input, textarea { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>Profilini Düzenle</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p style="color: #00ff00;">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <img src="{{ url_for('static', filename='uploads/' + user.profile_pic) }}" alt="Profil Fotoğrafı">
        <form method="POST" enctype="multipart/form-data">
            <textarea name="bio" placeholder="Biyografi">{{ user.bio or '' }}</textarea>
            <input type="file" name="profile_pic">
            <button type="submit">Kaydet</button>
        </form>
    </div>
</body>
</html>
''', user=current_user)

@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>{{ user.username }} - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        img { max-width: 100px; border-radius: 50%; border: 2px solid #ff9500; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>{{ user.username }}</h1>
        <img src="{{ url_for('static', filename='uploads/' + user.profile_pic) }}" alt="Profil Fotoğrafı">
        <p>{{ user.bio or 'Biyografi yok.' }}</p>
        {% if current_user.is_authenticated and current_user.id != user.id %}
            <a href="{{ url_for('chat', user_id=user.id) }}">Mesaj Gönder</a>
        {% endif %}
    </div>
</body>
</html>
''', user=user)

@app.route('/forum')
def forum():
    threads = Thread.query.all()
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Forum - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 900px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        .thread { background: #222; padding: 15px; margin: 10px 0; border-left: 3px solid #ff9500; }
        .thread:hover { background: #333; box-shadow: 0 0 10px #ff9500; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
        .fireball { animation: fall 3s linear infinite; position: absolute; }
        @keyframes fall { 0% { top: -50px; } 100% { top: 100%; } }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>C7KA Forum</h1>
        {% if current_user.is_authenticated %}
            <p><a href="{{ url_for('create_thread') }}">Yeni Başlık Oluştur</a></p>
        {% endif %}
        {% for thread in threads %}
            <div class="thread">
                <a href="{{ url_for('thread', thread_id=thread.id) }}">{{ thread.title }}</a>
                <p>Başlatan: <a href="{{ url_for('user_profile', username=thread.user.username) }}">{{ thread.user.username }}</a></p>
            </div>
        {% endfor %}
    </div>
    <script>
        function createFireball() {
            const fireball = document.createElement('div');
            fireball.className = 'fireball';
            fireball.style.left = Math.random() * 100 + 'vw';
            fireball.style.width = '10px';
            fireball.style.height = '10px';
            fireball.style.background = '#ff9500';
            fireball.style.borderRadius = '50%';
            fireball.style.boxShadow = '0 0 10px #ff9500';
            document.body.appendChild(fireball);
            setTimeout(() => fireball.remove(), 3000);
        }
        setInterval(createFireball, 500);
    </script>
</body>
</html>
''', threads=threads)

@app.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    if request.method == 'POST':
        thread = Thread(title=request.form['title'], content=request.form['content'], user_id=current_user.id)
        db.session.add(thread)
        db.session.commit()
        flash('Başlık oluşturuldu!')
        return redirect(url_for('forum'))
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Başlık Oluştur - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        input, textarea { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>Yeni Başlık Oluştur</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p style="color: #00ff00;">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <input type="text" name="title" placeholder="Başlık" required>
            <textarea name="content" placeholder="İçerik" required></textarea>
            <button type="submit">Oluştur</button>
        </form>
    </div>
</body>
</html>
''')

@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    if request.method == 'POST' and current_user.is_authenticated:
        post = Post(content=request.form['content'], user_id=current_user.id, thread_id=thread_id)
        db.session.add(post)
        db.session.commit()
        flash('Yorum gönderildi!')
    posts = Post.query.filter_by(thread_id=thread_id).all()
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>{{ thread.title }} - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 900px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        .thread-content { background: #222; padding: 15px; margin: 10px 0; border-left: 3px solid #ff9500; }
        .post { background: #222; padding: 15px; margin: 10px 0; border-left: 3px solid #ff9500; }
        .post:hover { background: #333; box-shadow: 0 0 10px #ff9500; }
        textarea { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>{{ thread.title }}</h1>
        <div class="thread-content">
            <p><strong><a href="{{ url_for('user_profile', username=thread.user.username) }}">{{ thread.user.username }}</a></strong>: {{ thread.content }}</p>
        </div>
        <h2>Yorumlar</h2>
        {% for post in posts %}
            <div class="post">
                <p><strong><a href="{{ url_for('user_profile', username=post.user.username) }}">{{ post.user.username }}</a></strong>: {{ post.content }}</p>
            </div>
        {% endfor %}
        {% if current_user.is_authenticated %}
            <form method="POST">
                <textarea name="content" placeholder="Yorum yaz..." required></textarea>
                <button type="submit">Gönder</button>
            </form>
        {% else %}
            <p>Yorum yazmak için <a href="{{ url_for('login') }}">giriş yap</a>.</p>
        {% endif %}
    </div>
</body>
</html>
''', thread=thread, posts=posts)

@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    receiver = User.query.get_or_404(user_id)
    if request.method == 'POST':
        msg = Message(content=request.form['content'], sender_id=current_user.id, receiver_id=user_id)
        db.session.add(msg)
        db.session.commit()
        flash('Mesaj gönderildi!')
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).all()
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>{{ receiver.username }} ile Sohbet - C7KA Forum</title>
    <style>
        body { background: linear-gradient(180deg, #1a1a1a, #000); color: #ff5555; font-family: 'Courier New', monospace; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ff9500; border-radius: 5px; box-shadow: 0 0 15px #ff9500; }
        .message { padding: 10px; margin: 5px; border-radius: 5px; }
        .sent { background: #333; text-align: right; }
        .received { background: #222; }
        textarea { background: #222; color: #ff5555; border: 1px solid #ff9500; padding: 8px; width: 100%; margin: 10px 0; }
        button { background: #ff9500; color: black; padding: 10px; border: none; width: 100%; cursor: pointer; }
        button:hover { background: #ffaa33; }
        a { color: #ff9500; text-decoration: none; }
        a:hover { text-shadow: 0 0 5px #ff9500; }
    </style>
</head>
<body>
    ''' + NAVBAR + '''
    <div class="container">
        <h1>{{ receiver.username }} ile Sohbet</h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <p style="color: #00ff00;">{{ message }}</p>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% for message in messages %}
            <div class="message {% if message.sender_id == current_user.id %}sent{% else %}received{% endif %}">
                <p>{{ message.content }}</p>
            </div>
        {% endfor %}
        <form method="POST">
            <textarea name="content" placeholder="Mesaj yaz..." required></textarea>
            <button type="submit">Gönder</button>
        </form>
    </div>
</body>
</html>
''', receiver=receiver, messages=messages)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
