import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Resume
from core.resume_parser import extract_text_from_pdf
from core.skill_matcher import analyze_resume_text

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'smart_resume_analyzer_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Max 5 MB size limit
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize DB
db.init_app(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables before first request
with app.app_context():
    db.create_all()

# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Please check your login details and try again.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.date_uploaded.desc()).all()
    return render_template('dashboard.html', name=current_user.name, resumes=user_resumes)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    if 'resume_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))
    
    file = request.files['resume_file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # ====== AI BRAIN INTEGRATION ======
        extracted_text = extract_text_from_pdf(file_path)
        score, detected_skills = analyze_resume_text(extracted_text)
        # ==================================
        
        # Naya resume entry asli score aur skills ke sath save karo
        new_resume = Resume(
            user_id=current_user.id, 
            score=score, 
            detected_skills=detected_skills
        )
        db.session.add(new_resume)
        db.session.commit()
        
        flash('Resume successfully uploaded and analyzed!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid file type. Only PDF is allowed.', 'danger')
        return redirect(url_for('dashboard'))
@app.route('/report/<int:id>')
@login_required
def view_report(id):
    # 1. Database se specific resume fetch karo
    resume = Resume.query.get_or_404(id)

    # Security Check: Koi dusra user kisi aur ka resume na dekh paye
    if resume.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    # 2. Database mein skills ek lamba text (comma separated) tha, usko list mein convert kar rahe hain
    detected_list = resume.detected_skills.split(', ') if resume.detected_skills else []

    # 3. Dummy "Missing Skills" calculation (Jisko Student 4 aage chal kar advance karega)
    master_skills = ["python", "java", "sql", "html", "css", "javascript", "machine learning", "git", "cybersecurity"]
    missing_list = [skill for skill in master_skills if skill not in detected_list]

    return render_template('results.html', resume=resume, detected_skills=detected_list, missing_skills=missing_list)

if __name__ == '__main__':
    app.run(debug=True)