from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nskk_school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

db = SQLAlchemy(app)

# ==================== Database Models ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, staff, admin, parent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    class_grade = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    parent_phone = db.Column(db.String(15), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    bus_route = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id, 'roll_number': self.roll_number, 'class_grade': self.class_grade,
            'section': self.section, 'phone': self.phone, 'address': self.address,
            'parent_name': self.parent_name, 'parent_phone': self.parent_phone,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None
        }

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    qualification = db.Column(db.String(200), nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    class_grade = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    parent_phone = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    documents = db.Column(db.Text)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 'full_name': self.full_name, 'email': self.email,
            'phone': self.phone, 'class_grade': self.class_grade, 'status': self.status,
            'applied_on': self.applied_on.strftime('%Y-%m-%d %H:%M:%S')
        }

class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # tuition, transport, books
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 'student_id': self.student_id, 'amount': self.amount,
            'fee_type': self.fee_type, 'due_date': self.due_date.strftime('%Y-%m-%d'),
            'status': self.status
        }

class BusRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), unique=True, nullable=False)
    bus_number = db.Column(db.String(20), unique=True, nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(15), nullable=False)
    capacity = db.Column(db.Integer, default=50)
    current_location = db.Column(db.String(200), default='School')
    stops = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id, 'route_name': self.route_name, 'bus_number': self.bus_number,
            'driver_name': self.driver_name, 'current_location': self.current_location
        }

class LibraryBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'author': self.author,
            'category': self.category, 'available': self.available
        }

class BookIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('library_book.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')  # issued, returned
    fine = db.Column(db.Float, default=0)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # sports, cultural, academic
    organized_by = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'event_date': self.event_date.strftime('%Y-%m-%d %H:%M'),
            'location': self.location, 'category': self.category
        }

class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    class_grade = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    current_organization = db.Column(db.String(200))
    designation = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_photo = db.Column(db.String(500))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 'full_name': self.full_name, 'graduation_year': self.graduation_year,
            'current_organization': self.current_organization, 'designation': self.designation
        }

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # general, academic, event
    posted_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'content': self.content,
            'category': self.category, 'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# ==================== Routes ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

# ==================== Admission Routes ====================

@app.route('/api/admission/apply', methods=['POST'])
def apply_admission():
    data = request.json
    admission = Admission(
        full_name=data.get('full_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        class_grade=data.get('class_grade'),
        dob=datetime.strptime(data.get('dob'), '%Y-%m-%d').date(),
        parent_name=data.get('parent_name'),
        parent_phone=data.get('parent_phone')
    )
    db.session.add(admission)
    db.session.commit()
    return jsonify({'success': True, 'id': admission.id}), 201

@app.route('/api/admission/applications', methods=['GET'])
def get_admissions():
    admissions = Admission.query.all()
    return jsonify([a.to_dict() for a in admissions])

@app.route('/api/admission/<int:app_id>/approve', methods=['PUT'])
def approve_admission(app_id):
    admission = Admission.query.get_or_404(app_id)
    admission.status = 'approved'
    db.session.commit()
    return jsonify({'success': True})

# ==================== Fee Routes ====================

@app.route('/api/fees/<int:student_id>', methods=['GET'])
def get_student_fees(student_id):
    fees = Fee.query.filter_by(student_id=student_id).all()
    return jsonify([f.to_dict() for f in fees])

@app.route('/api/fees', methods=['POST'])
def create_fee():
    data = request.json
    fee = Fee(
        student_id=data.get('student_id'),
        amount=data.get('amount'),
        fee_type=data.get('fee_type'),
        due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
    )
    db.session.add(fee)
    db.session.commit()
    return jsonify(fee.to_dict()), 201

@app.route('/api/fees/<int:fee_id>/pay', methods=['PUT'])
def pay_fee(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    fee.status = 'paid'
    fee.paid_date = datetime.now().date()
    db.session.commit()
    return jsonify({'success': True})

# ==================== Bus Routes ====================

@app.route('/api/bus/routes', methods=['GET'])
def get_bus_routes():
    routes = BusRoute.query.all()
    return jsonify([r.to_dict() for r in routes])

@app.route('/api/bus/tracking/<route_id>', methods=['GET'])
def track_bus(route_id):
    route = BusRoute.query.get_or_404(route_id)
    return jsonify(route.to_dict())

@app.route('/api/bus/<int:route_id>/location', methods=['PUT'])
def update_bus_location(route_id):
    route = BusRoute.query.get_or_404(route_id)
    data = request.json
    route.current_location = data.get('location')
    db.session.commit()
    return jsonify({'success': True})

# ==================== Library Routes ====================

@app.route('/api/library/books', methods=['GET'])
def get_library_books():
    category = request.args.get('category', None)
    query = LibraryBook.query
    if category:
        query = query.filter_by(category=category)
    books = query.all()
    return jsonify([b.to_dict() for b in books])

@app.route('/api/library/issue', methods=['POST'])
def issue_book():
    data = request.json
    book = LibraryBook.query.get(data.get('book_id'))
    if book and book.available > 0:
        book.available -= 1
        issue = BookIssue(
            student_id=data.get('student_id'),
            book_id=data.get('book_id')
        )
        db.session.add(issue)
        db.session.commit()
        return jsonify({'success': True}), 201
    return jsonify({'success': False, 'message': 'Book not available'}), 400

@app.route('/api/library/return/<int:issue_id>', methods=['PUT'])
def return_book(issue_id):
    issue = BookIssue.query.get_or_404(issue_id)
    book = LibraryBook.query.get(issue.book_id)
    book.available += 1
    issue.status = 'returned'
    issue.return_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

# ==================== Events Routes ====================

@app.route('/api/events', methods=['GET'])
def get_events():
    category = request.args.get('category', None)
    query = Event.query.order_by(Event.event_date.desc())
    if category:
        query = query.filter_by(category=category)
    events = query.all()
    return jsonify([e.to_dict() for e in events])

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    event = Event(
        title=data.get('title'),
        description=data.get('description'),
        event_date=datetime.strptime(data.get('event_date'), '%Y-%m-%d %H:%M'),
        location=data.get('location'),
        category=data.get('category'),
        organized_by=data.get('organized_by')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201

# ==================== Alumni Routes ====================

@app.route('/api/alumni', methods=['GET'])
def get_alumni():
    alumni = Alumni.query.order_by(Alumni.graduation_year.desc()).all()
    return jsonify([a.to_dict() for a in alumni])

@app.route('/api/alumni', methods=['POST'])
def add_alumni():
    data = request.json
    alumni = Alumni(
        full_name=data.get('full_name'),
        graduation_year=data.get('graduation_year'),
        class_grade=data.get('class_grade'),
        email=data.get('email'),
        phone=data.get('phone'),
        current_organization=data.get('current_organization'),
        designation=data.get('designation')
    )
    db.session.add(alumni)
    db.session.commit()
    return jsonify(alumni.to_dict()), 201

# ==================== Notice Routes ====================

@app.route('/api/notices', methods=['GET'])
def get_notices():
    category = request.args.get('category', None)
    query = Notice.query.order_by(Notice.created_at.desc())
    if category:
        query = query.filter_by(category=category)
    notices = query.all()
    return jsonify([n.to_dict() for n in notices])

@app.route('/api/notices', methods=['POST'])
def create_notice():
    data = request.json
    notice = Notice(
        title=data.get('title'),
        content=data.get('content'),
        category=data.get('category'),
        posted_by=data.get('posted_by')
    )
    db.session.add(notice)
    db.session.commit()
    return jsonify(notice.to_dict()), 201

# ==================== Stats Routes ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_students': Student.query.count(),
        'total_staff': Staff.query.count(),
        'total_events': Event.query.count(),
        'pending_admissions': Admission.query.filter_by(status='pending').count(),
        'total_alumni': Alumni.query.count(),
        'active_routes': BusRoute.query.count()
    })

# ==================== Initialize DB ====================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
