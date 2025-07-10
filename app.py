from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YourNewPassword123!@localhost/quiz_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200))
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    option_d = db.Column(db.String(100))
    correct_option = db.Column(db.String(1))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

# Home - list quizzes
@app.route('/')
def index():
    quizzes = Quiz.query.all()
    return render_template('index.html', quizzes=quizzes)

# Create new quiz
@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']
        new_quiz = Quiz(title=title)
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_quiz.html')

# Add question to quiz
@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        q = Question(
            question_text=request.form['question_text'],
            option_a=request.form['option_a'],
            option_b=request.form['option_b'],
            option_c=request.form['option_c'],
            option_d=request.form['option_d'],
            correct_option=request.form['correct_option'],
            quiz_id=quiz.id
        )
        db.session.add(q)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_question.html', quiz=quiz)

# Take quiz
@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        score = 0
        for q in quiz.questions:
            selected = request.form.get(str(q.id))
            if selected == q.correct_option:
                score += 1
        return render_template('result.html', score=score, total=len(quiz.questions))
    return render_template('take_quiz.html', quiz=quiz)

if __name__ == '__main__':
    # Create tables in MySQL if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)