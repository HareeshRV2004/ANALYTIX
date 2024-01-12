from flask import Flask,redirect,url_for,render_template,request,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import matplotlib.pyplot as plt 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory
from werkzeug.exceptions import HTTPException
import traceback



app=Flask(__name__)
app.secret_key="45"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.permanent_session_lifetime=timedelta(minutes=1)
db=SQLAlchemy(app)
reviews_data = []
login_manager = LoginManager(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(200), nullable=False)

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(200), nullable=False)


class csign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    feedback = db.Column(db.Text, nullable=False)

class usign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ucompany_name = db.Column(db.String(100), nullable=False)
    uemail = db.Column(db.String(100), unique=True, nullable=False)
    upassword = db.Column(db.String(100), nullable=False)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(100))
class Reviews(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    xname = db.Column(db.String(100), nullable=False)
    cname = db.Column(db.String(100), nullable=False)
    nps = db.Column(db.Integer, nullable=False)
    rsponse_time = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    ratings = db.Column(db.Integer, nullable=False)
    advantages = db.Column(db.Text, nullable=False)
    disadvantages = db.Column(db.Text, nullable=False)
    improvements = db.Column(db.Text, nullable=False)
    proof = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return Reviews.query.get(int(user_id))    



@app.route("/")
def home():
	return redirect(url_for("home1"))

@app.route("/home",methods=["POST","GET"])
def home1():
	return render_template("home1.html")

@app.route('/feedback', methods=['GET', 'POST'])
def feedback1():
    if request.method == 'POST':
        
        feedback_text = request.form['feedback']  
        fname = request.form['fname']
        new_feedback = Feedback(fname=fname, feedback=feedback_text)  
        db.session.add(new_feedback)
        db.session.commit()

        return redirect('/')



    return render_template('feedback.html')  
@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory('uploads', filename)

@app.route("/logout")
def logout():
	session.pop("user",None)
	flash("YOu have been logged out!!","info")
	return redirect(url_for("login"))

@app.route("/base")
def base():
    ucompany_name = session.get('ucompany_name', '')
    companies = Company.query.all()
    return render_template('review.html',ucompany_name=ucompany_name, companies=companies)

@app.route('/submit_review', methods=['POST','GET'])
def submit_review():
    if request.method == 'POST':
        xname = request.form['xname']
        cname = request.form['cname']
        age = int(request.form['age'])
        ratings = request.form['ratings']
        nps=request.form['nps']
        rsponse_time=request.form['rsponse_time']
        advantages = request.form['advantages']
        disadvantages = request.form['disadvantages']
        improvements = request.form['improvements']

        uploaded_file = request.files['proof']
        filename = None
        if uploaded_file:
            ext = uploaded_file.filename.split('.')[-1].lower()  
            if ext == 'png':
                filename = f"{cname}_{xname}.jpg"  
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            
                img = Image.open(uploaded_file)
                img = img.convert("RGB")
                img.save(file_path, "JPEG")
            else:
                filename = f"{cname}_{xname}.{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)


        
        review = Reviews(
            xname=xname,
            cname=cname,
            nps=nps,
            age=age,
            ratings=ratings,
            advantages=advantages,
            rsponse_time=rsponse_time,
            disadvantages=disadvantages,
            improvements=improvements,
            proof=filename
        )


        db.session.add(review)
        db.session.commit()

        return redirect(url_for("udashboard",xname=xname))

@app.route("/company_detail",methods=["POST","GET"])
def index():
    company_name = request.args.get('company_name')
    if request.method == 'POST':
        cname = request.form['cname']
        category = request.form['category']
        description = request.form['description']
        website = request.form['website']
        
        new_company = Company(cname=cname, category=category, description=description, website=website)
        db.session.add(new_company)
        db.session.commit()
        return redirect(url_for("dashboard",company_name=cname))
    return render_template('company_details.html',company_name=company_name)


@app.route("/cdata",methods=["POST","GET"])
def cdata():
	return render_template("cdata.html",values=Reviews.query.all())


@app.route("/comp")
def comp():
    companies = Company.query.all()
    return render_template('comp.html', companies=companies)
@app.route('/dashboard/<company_name>')
def dashboard(company_name):
    reviews = Reviews.query.filter_by(cname=company_name).all()
    rating_counts = (db.session.query(Reviews.ratings, db.func.count(Reviews.ratings)).filter(Reviews.cname == company_name).group_by(Reviews.ratings).all())
    ratings = [count[0] for count in rating_counts]
    counts = [count[1] for count in rating_counts]
    plt.bar(ratings, counts)
    plt.xlabel('Rating')
    plt.ylabel('Number of People')
    plt.title('Number of People Rated in Each overall Rating ')
    plt.xticks(ratings)
    plt.tight_layout()
    graph_filename = 'static/ratings.png'  # Make sure 'static' folder exists
    plt.savefig(graph_filename)
    plt.close()
    reviews = Reviews.query.filter_by(cname=company_name).all()
    rating_counts = (db.session.query(Reviews.rsponse_time, db.func.count(Reviews.rsponse_time)).filter(Reviews.cname == company_name).group_by(Reviews.rsponse_time).all())
    ratings = [count[0] for count in rating_counts]
    counts = [count[1] for count in rating_counts]
    plt.bar(ratings, counts)
    plt.xlabel('response time rating')
    plt.ylabel('Number of People')
    plt.title('Number of People Rated in Each response time  Rating ')
    plt.xticks(ratings)
    plt.tight_layout()
    graph_filename = 'static/response.png'  
    plt.savefig(graph_filename)
    plt.close()

    reviews = Reviews.query.filter_by(cname=company_name).all()
    rating_counts = (db.session.query(Reviews.nps, db.func.count(Reviews.nps)).filter(Reviews.cname == company_name).group_by(Reviews.nps).all())
    ratings = [count[0] for count in rating_counts]
    counts = [count[1] for count in rating_counts]
    plt.bar(ratings, counts)
    plt.xlabel('nps rating')
    plt.ylabel('Number of People')
    plt.title('Number of People Rated in Each nps Rating ')
    plt.xticks(ratings)
    plt.tight_layout()

    graph_filename = 'static/nps.png'  # Make sure 'static' folder exists
    plt.savefig(graph_filename)
    plt.close()

    return render_template('dashboard.html', graph_filename=graph_filename, cname=company_name, reviews=reviews)	
@app.route('/csign', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        company_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_company = csign(company_name=company_name, email=email, password=hashed_password)
        db.session.add(new_company)
        db.session.commit()

        return redirect(url_for('index',company_name=company_name))

    return render_template('signup.html')

@app.route('/clogin', methods=['GET', 'POST'])
def clogin():
    if request.method == 'POST':
        company_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']

        company = csign.query.filter_by(email=email).first()

        if company and check_password_hash(company.password, password):
    
            return redirect(url_for("dashboard",company_name=company_name))
        else:
            return render_template('clogin.html', message="Invalid email or password")

    return render_template('clogin.html', message="succesful")
@app.route('/usign', methods=['GET', 'POST'])
def usign_up():
    if request.method == 'POST':
        ucompany_name = request.form['ucompany_name']
        uemail = request.form['uemail']
        upassword = request.form['upassword']
        hashed_password = generate_password_hash(upassword, method='sha256')

        new_company = usign(ucompany_name=ucompany_name, uemail=uemail, upassword=hashed_password)
        db.session.add(new_company)
        db.session.commit()
        session['ucompany_name'] = ucompany_name

        return redirect(url_for('comp'))

    return render_template('usign.html')

@app.route('/ulogin', methods=['GET', 'POST'])
def ulogin():
    if request.method == 'POST':
        ucompany_name = request.form['ucompany_name']
        uemail = request.form['uemail']
        upassword = request.form['upassword']

        company = usign.query.filter_by(uemail=uemail).first()

        if company and check_password_hash(company.upassword, upassword):
        
            session['ucompany_name'] = ucompany_name
            return redirect(url_for("comp"))
        else:
            return render_template('ulogin.html', message="Invalid email or password")

    return render_template('ulogin.html', message="succesful")
@app.route('/privacy')
def privacy():
     return render_template('privacy.html')
@app.route('/udashboard/<xname>', methods=['GET', 'POST'])
def udashboard(xname):
    reviews = Reviews.query.filter_by(xname=xname).all()
    num_reviews = len(reviews)
    return render_template('udashboard.html', xname=xname, num_reviews=num_reviews, reviews=reviews)
    
@app.route('/submit_question', methods=['POST'])
def submit_question():
    if request.method == 'POST':
        company_name = request.form['company_name']
        question = request.form['question']

        new_question = Question(company_name=company_name, question=question)
        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for('comp'))

@app.route('/submit_answer/<xname>', methods=['POST'])
def submit_answer(xname):
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('answer_'):
                question_id = int(key.split('_')[1])
                user_answer = UserAnswer(user_name=xname, question_id=question_id, answer=value)
                db.session.add(user_answer)
                db.session.commit()

        return redirect(url_for('udashboard', xname=xname))
    
"""@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return redirect(url_for("home1"))
    


@app.errorhandler(Exception)
def handle_exception(e):
    return redirect(url_for("home1"))"""""

if __name__=="__main__":
	with app.app_context():
		db.create_all()
		app.run(debug=True)


