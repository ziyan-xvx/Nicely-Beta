from app import app, db
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from sqlalchemy import create_engine
import os
import pandas as pd
from werkzeug.utils import secure_filename
from app.scrapper import getClient, twitter_verify
from app.visualization import process, processtext, graphplot
from app.SAModle import analysis

from app.models import Users, Nicely_post, infos, user_tweets, Counselor
db.create_all()
engine = create_engine('sqlite:///app/userdata.sqlite3', echo=False)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}

class StatusDenied(Exception):
    pass

@app.errorhandler(StatusDenied)
def redirect_on_status_denied(error):
    return redirect(url_for('login'))

def currently_logged_in():
    user = session.get("user_logged_in")
    if user:
        return
    else:
        flash('You are currently logged out')
        raise StatusDenied

@app.route('/admin')
def admin():
    return render_template('data.html', users = Users.query.all(), infos = infos.query.all() )

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    user_logged_in = session.get("user_logged_in")
    user_active = Users.query.filter_by(username = user_logged_in).first()
    if user_active:
        return redirect("/dashboard", code = 302)

    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            username = request.form['username']
            password = request.form['password']
            user = Users(username, password)
            session['user_logged_in'] = username

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('personalinfo', data = username))
    return render_template("signup.html")

@app.route('/personal-info', methods = ['GET', 'POST'])
def personalinfo():
    user_logged_in = session.get("user_logged_in")
    if request.method == 'POST':
        if not request.form['gender'] or not request.form['phone'] or not request.form['email'] or not request.form['twitter']:
            flash('Please enter all the required fields')
            return redirect('/personal-info')
        if twitter_verify(request.form['twitter']) == False:
            print("second verify false")
            flash('Please enter a corrent twitter username without "@" under your profile')
            redirect('/personal-info')
        else: 
            print("second verify true")
            info = infos(user_name = user_logged_in, demographic = request.form['demographic'], twitter = request.form['twitter'], language = request.form['language'],
                         workstatus = request.form['workstatus'], gender = request.form['gender'], phone = request.form['phone'], email = request.form['email'])
            db.session.add(info)
            print(f"added to the queue, Now fetching social data")
            twitter_name = request.form['twitter']
            resultReturned = getClient(twitter_name, user_logged_in)
            graphplot(resultReturned)
            db.session.commit()
            flash('Records were successfully added')
    return render_template("personalinfo.html")

@app.route('/')
def main():
    return redirect("/login")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    user_logged_in = session.get("user_logged_in")
    user_active = Users.query.filter_by(username = user_logged_in).first()
    if user_active:
        return redirect("/dashboard", code = 302)

    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            user = Users.query.filter_by(username = request.form['username']).first()
            if user and user.password == request.form['password']:
                session['user_logged_in'] = request.form['username']
                return redirect(url_for('dashboard'))
            else:
                flash('invalid password or username')
    return render_template("login.html")

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop("user_logged_in", None)
    flash('you are now logged out')
    return redirect(url_for('login'))

def snapshot(data):
    if len(data) > 0:
        result = []
        a = range(1,5)
        for num in a:
            lst = [float(e[num]) for e in data]
            value = round(100 * sum(lst)/len(lst), 2)
            result.append(value)
        return result
    else:     
        return "not available yet, make your first entries to start!"

def process_pie(list):
    if len(list) > 0:
        result = []
        a = range(0,6)
        for num in a:
            lst = list[num]
            result.append(lst)
        return result

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    currently_logged_in()
    user_logged_in = session.get("user_logged_in")
    verify = user_tweets.query.filter_by(user_name = user_logged_in).first()

    if verify:
        raw = pd.read_sql ('SELECT user_name, Anger, Joy, Optimism, Sadness, AveDailyScore, Tweet_time FROM user_tweets', engine)
        new = raw.loc[raw["user_name"] == user_logged_in]
        data = new.values.tolist()
        numbers = list(range(0, 6))
        pie = process_pie(data)
        radar = snapshot(data)
        lables = [row[6] for row in data]
        values = [float(row[5]) for row in data]
        values_pie = [[row[1], row[2], row[3], row[4]] for row in pie]
        if len(data) > 0:
            EmotionScore = round(sum(values)/len(data), 2)
        else:
            EmotionScore = "not available yet, make your first entries to start!"
        return render_template("dashboard.html", usr = user_logged_in, EmotionScore = EmotionScore, lables = lables, values = values, radar = radar, values_pie = values_pie, numbers = numbers)
    else:
        session.pop("user_logged_in", None)
        flash("Please associate your account with valid twitter account")
        return redirect("/login")

    

@app.route('/scoredetail', methods = ['GET', 'POST'])
def scoredetail():
    currently_logged_in()
    user_logged_in = session.get("user_logged_in")
    resultsback = user_tweets.query.filter_by(user_name = user_logged_in).all()
    return render_template("scoredetail.html", usr = user_logged_in, data = resultsback)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/view', methods = ['GET', 'POST'])
def view():
    currently_logged_in()
    if request.method == 'POST':
        posttext = request.form.get('content')
        checkStatus = request.form.get('checkbox')
        databack = analysis(posttext)
        scoredetail = process(databack)
        Avescore = processtext(scoredetail)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_logged_in = session.get("user_logged_in")
            filename_secure = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(filename_secure)
            file.filename = str(time) + filename + file_extension
            user_directory = "/post_videos/"
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+ user_directory, file.filename))
            media_path = "/static/upload" + user_directory + file.filename

            if checkStatus == "True":
                post = Nicely_post("Anonymous", filename, posttext, media_path, time)
                db.session.add(post)
            else:
                post = Nicely_post(user_logged_in, filename, posttext, media_path, time)
                db.session.add(post)
            
            entry = user_tweets(user_logged_in, "post_id", posttext, scoredetail[0], scoredetail[1], scoredetail[2], scoredetail[3], Avescore, time)
            
            db.session.add(entry)
            db.session.commit()

    user_logged_in = session.get("user_logged_in")
    pastposts = engine.execute('SELECT * FROM Nicely_post ORDER BY user_post_id DESC;')
    if pastposts :
        return render_template("view.html", posts = pastposts, usr = user_logged_in, filled = True)
    return render_template("view.html", usr = user_logged_in)

@app.route('/explained')
def explained():
    user_logged_in = session.get('user_logged_in')
    return render_template("explained.html", usr = user_logged_in)

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    user_logged_in = session.get('user_logged_in')
    emojilist = ["😁","😄","😐","🙁","😔","😡", "😬", "😍", "😎", "😴", "🤒", "🤯"]
    emoji_data = pd.read_csv("app/static/csv/emoji_Score.csv")

    if request.method == 'POST':
        emoji = request.form.get('emoji')
        entry = request.form.get('entry')

        position = emojilist.index(emoji)
        emoji_results = emoji_data.iloc[position]
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text_score = analysis(entry)
        scoredetail = process(text_score)
        Avescore = processtext(scoredetail)


        emoji_input = user_tweets(user_logged_in, "emoji", emoji, emoji_results[1], emoji_results[2], emoji_results[3], emoji_results[4], emoji_results[5], time)
        db.session.add(emoji_input)
        text_input = user_tweets(user_logged_in, "quiz", entry, scoredetail[0], scoredetail[1], scoredetail[2], scoredetail[3], Avescore, time)
        db.session.add(text_input)
        db.session.commit()

    return render_template("quiz.html", usr = user_logged_in, emojis = emojilist)

@app.route('/chat_signup', methods = ['GET', 'POST'])
def chat_signup():
    currently_logged_in()
    if request.method == 'POST':
        username = session.get("user_logged_in")
        name = request.form.get('name')
        description = request.form.get('description')
        fee = request.form.get('fee')
        language = request.form.get('language')
        number = request.form.get('number')
        gender = request.form.get('gender')
        email = request.form.get('email')
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename_secure = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(filename_secure)
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.filename = str(time) + filename + file_extension
            user_directory = "/post_videos/"
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+ user_directory, file.filename))

            media_path = "/static/upload" + user_directory + file.filename
            people = Counselor(username, name, gender, language, description, email, number, media_path, fee)

            db.session.add(people)
            db.session.commit()
            return redirect(url_for('chat'))
    return render_template("chat_signup.html")

@app.route('/chat')
def chat():
    user_logged_in = session.get('user_logged_in')
    data = Counselor.query.all()
    if data :
        return render_template("chat.html", people = data, usr = user_logged_in)
    return render_template("chat.html", usr = user_logged_in)

@app.route('/info')
def info():
    return render_template("info.html")