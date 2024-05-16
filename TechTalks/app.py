import flask
from flask import request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask import render_template,session,jsonify
import json
from sqlalchemy import func
from heapq import nlargest



app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/forum'
db = SQLAlchemy(app)
app.config['SECRET_KEY']= "afhbrjbnjbc"  
class users(db.Model):
    sno =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
class questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    answers = db.Column(db.String, nullable=False)
class feedback(db.Model):
    name =db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, primary_key=True)
    feedback = db.Column(db.String, nullable=False)

@app.route('/', methods=[ "GET", "POST"])
def login():
     if request.method == 'POST':
         print("here reaches")
         print(request.form)
         if "signUp" in request.form:
             
             print("if condition true")
             name = request.form['name']
             email = request.form['email']
             password = request.form['pass']
             userRecord = users.query.filter(
               
                     users.email.like(email)
                 
             ).all()
             userFound=len(userRecord)
             if userFound<=0:
                 print(name+email+password)
                 entry=users(name=name, email=email,password=password)
                 db.session.add(entry)
                 db.session.commit()
                 return render_template("index.html",msg='')
             else:
                return render_template("index.html",msg="Username already exist pls try again!!!")

         else:
             print("else condition true")
             userName = request.form['userName']
             pas = request.form['pas']
             print("record")
             userRecord = users.query.filter(
               
                     users.name.like(userName),
                     users.password.like(pas)
                 
             ).all()
             userFound=len(userRecord)
            

             if userFound>0 and userRecord[0].name==userName:
                 session['nameSession']=userRecord[0].name
                 return render_template('final dashboard-1.html',msg='')

             else:
                  return render_template("index.html", msg="Invalid username and password!!!")

             #print(userRecord[0].name)
     elif session.get('nameSession') is not None:
       
         print(session['nameSession'])
         return render_template('final dashboard-1.html',msg='')
     else:
         return render_template("index.html",msg='')
   
 
@app.route('/feedback',methods=[ "GET", "POST"])
def feedbackForm():
    if request.method == 'POST':
        name=request.form["name"]
        email=request.form["email"]
        feedbackFromForm=request.form["feedback"]

        feedbacktostore = feedback(name=name, email=email,feedback=feedbackFromForm)
        db.session.add(feedbacktostore)
        db.session.commit()
        flash("Your feedback is submitted.")
        return redirect('/')









@app.route('/home')
def home_page():
    return render_template('final dashboard-1.html')

@app.route('/signout')
def signout():
    session.pop('nameSession')
    return redirect("/")


@app.route('/f1')
def forum1():
    return render_template('f1.html')



@app.route('/f2')
def forum():
    return render_template('f2.html')

@app.route('/articles')
def articles():
    return render_template('articles.html')


@app.route('/interest')
def interest():
    return render_template('interest.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/questions')
def allquestions():
    result = questions.query.all()
    return render_template('questions.html',questions=result)

@app.route('/askaquestion', methods=[ "GET", "POST"])
def askaquestion():
    if request.method == "POST":
        questionByUser = request.form["question"]
        print(bool(questions.query.filter_by(question=questionByUser).first()))
        if(not bool(questions.query.filter_by(question=questionByUser).first())):
            row = questions(question=questionByUser, answers="[]")
            db.session.add(row)
            db.session.commit()
            success = "true"

        answers = questions.query.filter(
            questions.question.like(questionByUser)
        ).one()
        answersList = json.loads(answers.answers)
        return render_template('f1.html', answersList=answersList, result=answers) 
    else:
        return render_template('askaquestion.html')      

@app.route('/search', methods=[ "GET", "POST"])
def search():
    if request.method == "POST":
        searchQuery = request.form['search']

        result = questions.query.filter(
            questions.question.like('%' + searchQuery + '%')
        ).all()

        searchQueryResult = []
        categories = []
        success = ""

        if(len(result) == 0):
            success = "false"
        else:
            for i in result:
                dict = {}
                dictCategory = {}
                dict["question"] = i.question
                dict["category"] = i.category
                if not any(d['category'] == i.category for d in categories):
                    dictCategory["category"] = i.category
                    categories.append(dictCategory)
                searchQueryResult.append(dict)
                success = "true"

    return render_template('questions.html', questions=searchQueryResult, categories=categories, success=success)

@app.route('/answer/<string:question>', methods=[ "GET", "POST"])
def answer(question):
    answers = questions.query.filter(
            questions.question.like(question)
        ).first()
    answersList = json.loads(answers.answers)

    print(answersList)

    return render_template('f1.html', answersList=answersList, result=answers)


@app.route('/submit-answer', methods=[ "GET", "POST"])
def submitAnswer():
    if request.method == "POST":

        result = questions.query.filter(
            questions.id.like(request.form['questionId'])
        ).one()

        resultdict = list(eval(result.answers)) 
        resultdictnew = {}
        resultdictnew['name'] = session['nameSession']
        resultdictnew['answer'] = request.form['answer']
        
        resultdict.append(resultdictnew)

        resultdictToString = json.dumps(resultdict)

        print(resultdictToString)

        result.answers = resultdictToString
        db.session.commit()

        
    return jsonify(result=resultdict[-1]) 


@app.route('/cyberSecPage', methods=[ "GET", "POST"])
def cyberSecPage():
    if request.method == "POST":
        question = request.form['question']
        category = request.form['questioncategory']
        if(not bool(questions.query.filter_by(question=question).first())):
            questionToStore = questions(question=question, category=category,answers="[]")
            db.session.add(questionToStore)
            db.session.commit()

    result = questions.query.filter(
            questions.category.like("Cyber Security")
        ).all()

    searchQueryResult = []
    success = ""

    if(len(result) == 0):
        success = "false"
    else:
        for i in result:
            dict = {}
            dict["question"] = i.question
            searchQueryResult.append(dict)
            success = "true"

    return render_template('cybersecurity.html', questions=searchQueryResult, success=success)

@app.route('/OOPPage', methods=[ "GET", "POST"])
def OOPPage():
    if request.method == "POST":
        question = request.form['question']
        category = request.form['questioncategory']
        if(not bool(questions.query.filter_by(question=question).first())):
            questionToStore = questions(question=question, category=category,answers="[]")
            db.session.add(questionToStore)
            db.session.commit()

    result = questions.query.filter(
            questions.category.like("Object Oriented Programming")
        ).all()

    searchQueryResult = []
    success = ""

    if(len(result) == 0):
        success = "false"
    else:
        for i in result:
            dict = {}
            dict["question"] = i.question
            searchQueryResult.append(dict)
            success = "true"
    print('THis is priting ',result)
    return render_template('ObjectOrientedProg.html', questions=searchQueryResult, success=success)



@app.route('/HardwaretechPage', methods=[ "GET", "POST"])
def HardwaretechPage():
    if request.method == "POST":
        question = request.form['question']
        category = request.form['questioncategory']
        if(not bool(questions.query.filter_by(question=question).first())):
            questionToStore = questions(question=question, category=category,answers="[]")
            db.session.add(questionToStore)
            db.session.commit()

    result = questions.query.filter(
            questions.category.like("HardwareTech")
        ).all()

    searchQueryResult = []
    success = ""

    if(len(result) == 0):
        success = "false"
    else:
        for i in result:
            dict = {}
            dict["question"] = i.question
            searchQueryResult.append(dict)
            success = "true"

    return render_template('HardwareTech.html', questions=searchQueryResult, success=success)


@app.route('/webdevelopmentPage', methods=[ "GET", "POST"])
def webdevelopmentPage():
    if request.method == "POST":
        question = request.form['question']
        category = request.form['questioncategory']
        if(not bool(questions.query.filter_by(question=question).first())):
            questionToStore = questions(question=question, category=category,answers="[]")
            db.session.add(questionToStore)
            db.session.commit()

    result = questions.query.filter(
            questions.category.like("webdevelopment")
        ).all()

    searchQueryResult = []
    success = ""

    if(len(result) == 0):
        success = "false"
    else:
        for i in result:
            dict = {}
            dict["question"] = i.question
            searchQueryResult.append(dict)
            success = "true"

    return render_template('webdevelopment.html', questions=searchQueryResult, success=success)

@app.route('/PythonPage', methods=[ "GET", "POST"])
def PythonPage():
    if request.method == "POST":
        question = request.form['question']
        category = request.form['questioncategory']
        if(not bool(questions.query.filter_by(question=question).first())):
            questionToStore = questions(question=question, category=category,answers="[]")
            db.session.add(questionToStore)
            db.session.commit()

    result = questions.query.filter(
            questions.category.like("Python")
        ).all()

    searchQueryResult = []
    success = ""

    if(len(result) == 0):
        success = "false"
    else:
        for i in result:
            dict = {}
            dict["question"] = i.question
            searchQueryResult.append(dict)
            success = "true"

    return render_template('python.html', questions=searchQueryResult, success=success)


@app.route('/topCategories')
def topCategories():
    result = questions.query.with_entities(questions.category, func.count(questions.category)).group_by(questions.category).all()
    
    resultListOfDicts = [{"category":a[0], "count":a[1]} for a in result]
    
    top3categories = nlargest(3, resultListOfDicts, key=lambda item: item["count"])
    print(top3categories)
    return render_template('topCategories.html', top3categories=top3categories)



if __name__=="__main__":
     app.run(port=5000, debug=True)
    
