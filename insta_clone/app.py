from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insta_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120))
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(256), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    stories = db.relationship('Story', backref='author', lazy=True, cascade='all, delete-orphan')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)
    caption = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        return unique_filename
    return None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template('feed.html', posts=posts)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if not username or not email or not password:
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    
    # Get active stories (not expired)
    now = datetime.utcnow()
    stories = Story.query.filter(
        Story.user_id == user.id,
        Story.expires_at > now
    ).order_by(Story.created_at.desc()).all()
    
    return render_template('profile.html', user=user, posts=posts, stories=stories)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        
        current_user.full_name = full_name
        current_user.bio = bio
        
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                filename = save_uploaded_file(file)
                if filename:
                    # Delete old profile pic if not default
                    if current_user.profile_pic != 'default.jpg':
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_pic))
                        except:
                            pass
                    current_user.profile_pic = filename
        
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('edit_profile.html')

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        caption = request.form.get('caption')
        
        if 'image' not in request.files:
            flash('Нет файла изображения', 'error')
            return redirect(url_for('new_post'))
        
        file = request.files['image']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(url_for('new_post'))
        
        filename = save_uploaded_file(file)
        if not filename:
            flash('Недопустимый тип файла', 'error')
            return redirect(url_for('new_post'))
        
        post = Post(image=filename, caption=caption, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        
        flash('Пост опубликован!', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_post.html')

@app.route('/story/new', methods=['GET', 'POST'])
@login_required
def new_story():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Нет файла изображения', 'error')
            return redirect(url_for('new_story'))
        
        file = request.files['image']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(url_for('new_story'))
        
        filename = save_uploaded_file(file)
        if not filename:
            flash('Недопустимый тип файла', 'error')
            return redirect(url_for('new_story'))
        
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=24)
        
        story = Story(
            image=filename,
            expires_at=expires_at,
            user_id=current_user.id
        )
        db.session.add(story)
        db.session.commit()
        
        flash('История опубликована! (исчезнет через 24 часа)', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('new_story.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default profile picture placeholder if needed
    default_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default.jpg')
    if not os.path.exists(default_pic_path):
        # Create a simple 1x1 pixel placeholder
        from PIL import Image
        img = Image.new('RGB', (1, 1), color='gray')
        img.save(default_pic_path)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
