from flask import Flask,session,render_template,redirect,request,jsonify,make_response
import mysql.connector
import bcrypt
import sendEmail,googleGemini
import time
from datetime import datetime
from datetime import date
import json

with open('config.json') as f:
    config=json.load(f)
    
mydb=mysql.connector.connect(
    host=config["DB_HOST"],
    user=config["DB_USER"],
    password=config["DB_PASS"],
    database=config["DB_NAME"]
)

myCursor=mydb.cursor(dictionary=True)
create_query_users="CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255),last_name VARCHAR(255), email VARCHAR(255),password VARCHAR(255), token VARCHAR(255))"
myCursor.execute(create_query_users)
mydb.commit()

create_query_settings="CREATE TABLE IF NOT EXISTS users_settings (user_id INT, mobile_no INT NULL, currency VARCHAR(255), monthly_income INT, financial_goal VARCHAR(255), payday VARCHAR(255), budget_alert VARCHAR(255), unusual_spend_alert VARCHAR(255), investment_insights VARCHAR(255), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)"
myCursor.execute(create_query_settings)
mydb.commit()

create_query_budget="CREATE TABLE IF NOT EXISTS budgets(budget_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, budget_amount INT,allocated_budget INT, remaining_budget INT, start_date DATE, end_date DATE, description VARCHAR(255), status VARCHAR(255), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)"
myCursor.execute(create_query_budget)
mydb.commit()

create_query_addExpense="CREATE TABLE IF NOT EXISTS expenses (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT,budget_id INT, expense INT, description TEXT, category VARCHAR(255), date DATE, time TIME, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (budget_id) REFERENCES budgets(budget_id) ON DELETE CASCADE)"
myCursor.execute(create_query_addExpense)
mydb.commit()

create_query_category="CREATE TABLE IF NOT EXISTS category (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, budget_id INT,category VARCHAR(255), amount_allocated INT, spent INT, remaining INT, category_notes VARCHAR(255), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (budget_id) REFERENCES budgets(budget_id) ON DELETE CASCADE)"
myCursor.execute(create_query_category)
mydb.commit()

today=date.today()
delete_query="DELETE FROM budgets WHERE end_date < %s"
myCursor.execute(delete_query,(today,))
mydb.commit()

def getConnection():
    global mydb
    if not mydb.is_connected():
        mydb.connect()
    return mydb

app=Flask(__name__)
app.secret_key=config["SECRET_KEY"]

@app.route("/")
def home_page():
    logged_in=request.cookies.get("loggedin")
    if logged_in=="true":
        return redirect('/homePage')
    return render_template("index.html")

@app.route("/index", methods=['GET','POST'])
def create_account():
    if request.method=='POST':
        conn=getConnection()
        first_name=request.form['firstname']
        last_name=request.form['lastname']
        email=request.form['email']
        password=request.form['password']
        byte_pass=password.encode()
        hashed_password=bcrypt.hashpw(byte_pass,bcrypt.gensalt())
        select_query="SELECT * FROM users WHERE email= %s"
        myCursorPrivate=conn.cursor(dictionary=True)
        myCursorPrivate.execute(select_query,(email,))
        res=myCursorPrivate.fetchone()
        if res==None:
            insert_query="INSERT INTO users (first_name, last_name, email, password) VALUES (%s,%s, %s, %s)"
            values=(first_name,last_name,email,hashed_password)
            myCursorPrivate.execute(insert_query,values)
            mydb.commit()
            select_query="SELECT * FROM users WHERE email = %s"
            myCursorPrivate.execute(select_query,(email,))
            res=myCursorPrivate.fetchone()
            response=make_response(redirect('/homePage'))
            response.set_cookie("loggedin","true",max_age=60 * 60 * 24 * 365 * 10)
            response.set_cookie("user_email",email,max_age=60 * 60 * 24 * 365 * 10)
            response.set_cookie("first_name",first_name,max_age=60 * 60 * 24 * 365 * 10)
            response.set_cookie("last_name",last_name,max_age=60 * 60 * 24 * 365 * 10)
            response.set_cookie("user_id",str(res['id']),max_age=60 * 60 * 24 * 365 * 10)
            return response
        else:
            return render_template("login.html")
    return render_template("index.html")


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        email=request.form['email']
        password=request.form['password']
        byte_password=password.encode()
        select_query="SELECT * FROM users WHERE email = %s"
        myCursorPrivate.execute(select_query,(email,))
        res=myCursorPrivate.fetchone()
        mydb.commit()
        if res and bcrypt.checkpw(byte_password,res['password'].encode()):
            response=make_response(redirect('/homePage'))
            if not request.cookies.get('user_email'):
                response.set_cookie("loggedin","true",max_age=60 * 60 * 24 * 365 * 10)
                response.set_cookie("user_email",email,max_age=60 * 60 * 24 * 365 * 10)
                response.set_cookie("first_name",res['first_name'],max_age=60 * 60 * 24 * 365 * 10)
                response.set_cookie("last_name",res['last_name'],max_age=60 * 60 * 24 * 365 * 10)
                response.set_cookie("user_id",str(res['id']),max_age=60 * 60 * 24 * 365 * 10)
                return response
            else:
                return redirect('/homePage')
        else:
            print("False")
    return render_template('login.html')

@app.route('/forgetPassword', methods=['GET','POST'])
def forgetPassword():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        email=request.form['email']
        session['resetPasswordEmail']=email
        select_query="SELECT * FROM users WHERE email = %s"
        myCursorPrivate.execute(select_query,(email,))
        res=myCursorPrivate.fetchone()
        if res:
            sendEmail.send_reset_email(email)
    return render_template('forgetPassword.html')

@app.route("/homePage")
def homePage():
    logged_in=request.cookies.get("loggedin")
    if logged_in=="true":
        return render_template("homePage.html")
    else:   
        return render_template("index.html")

@app.route('/api/homePageAddExpense')
def homePageAddExpense():
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    id=request.cookies.get("user_id")
    select_query="SELECT budget_id FROM budgets WHERE user_id =%s"
    myCursorPrivate.execute(select_query,(id,))
    res=myCursorPrivate.fetchone()
    return jsonify({"result":res})

@app.route("/api/homePage")
def updateHomePage():
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    id=request.cookies.get("user_id")
    curr_time=time.localtime()
    current_year=curr_time.tm_year
    current_month=curr_time.tm_mon
    if curr_time.tm_mon>=1 or curr_time.tm_mon<=11:
        next_month=curr_time.tm_mon+1
        next_year=curr_time.tm_year
    else:
        next_month=1
        next_year=curr_time.tm_mon+1
    
    select_query="SELECT COUNT(*) FROM expenses WHERE date BETWEEN '%s-%s-01' AND '%s-%s-01' AND user_id =%s"
    values=(current_year,current_month,next_year,next_month,id)
    myCursorPrivate.execute(select_query,values)
    res=myCursorPrivate.fetchone()
    countTransactions=res['COUNT(*)']
    selet_query_spending="SELECT SUM(expense) FROM expenses WHERE date BETWEEN '%s-%s-01' AND '%s-%s-01' AND user_id = %s"
    myCursorPrivate.execute(selet_query_spending,values)
    res=myCursorPrivate.fetchone()
    totalTransactions=res["SUM(expense)"]
    currency=request.cookies.get("currency")
    data={
        "countTransactions":countTransactions,
        "totalTransactions":totalTransactions,
        "currency":currency
    }
    return jsonify(data)

@app.route('/api/resetPassword',methods=['POST'])
def resetPassword():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        data=request.get_json()
        password=data.get('password')
        email=data.get('email')
        hashedPassword=bcrypt.hashpw(password.encode(),bcrypt.gensalt())
        update_query="UPDATE users SET password= %s WHERE email = %s"
        myCursorPrivate.execute(update_query,(hashedPassword,email))
        mydb.commit()
    return render_template('resetPassword.html')

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = request.args.get('email')  
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    if not email:
        return "Email missing from reset link", 400
    mydb.commit()
    select_query = "SELECT token FROM users WHERE email = %s"
    myCursorPrivate.execute(select_query, (email,))
    thisToken = myCursorPrivate.fetchone()
    if thisToken['token'] == token:
        return render_template('resetPassword.html',email=email)
    else:
        return "Invalid or expired reset link", 400

@app.route("/addExpense",methods=['GET','POST'])
def addExpense():
    return render_template("addExpense.html")

@app.route('/api/addExpense',methods=['GET','POST'])
def addExpenseDB():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        id=request.cookies.get('user_id')
        budget_id=request.cookies.get('budget_id')
        select_query="SELECT * FROM category WHERE budget_id = %s AND category = %s"
        data=request.get_json()
        expense=data.get('expense')
        description=data.get('description')
        category=data.get('category')
        date=data.get('date')
        time=data.get('time')
        myCursorPrivate.execute(select_query,(budget_id, category))
        res=myCursorPrivate.fetchone()
        if res==None:
            return jsonify({"result":"Failed"})
        elif int(expense)>int(res['remaining']):
            return jsonify({"result":"highExpense"})
        else:
            select_query="SELECT * FROM budgets WHERE budget_id = %s"
            myCursorPrivate.execute(select_query,(budget_id,))
            resDate=myCursorPrivate.fetchone()
            input_date=datetime.strptime(date,"%Y-%m-%d").date()

            if resDate['start_date']<=input_date and resDate['end_date']>=input_date:
                insert_query="INSERT INTO expenses (user_id,budget_id,expense,description,category,date,time) VALUES (%s, %s, %s, %s, %s, %s,%s)"
                values=(id,budget_id,expense,description,category,date,time)
                myCursorPrivate.execute(insert_query,values)
                mydb.commit()
                spent=int(res['spent'])+int(expense)
                remaining=int(res['remaining'])-int(expense)
                update_query="UPDATE category SET spent = %s, remaining = %s WHERE budget_id =%s AND category = %s"
                myCursorPrivate.execute(update_query,(spent,remaining,budget_id,category))
                mydb.commit()
                return jsonify({"result":"success","redirectURL":"/homePage"}),200
            else:
                return jsonify({"error":"dateTimeError"})
            
    return jsonify({"result":"error"})

@app.route("/chat",methods=['POST','GET'])
def chat():
    if request.method=='POST':
        data = request.get_json()
        user_input=data.get("input")
        response=googleGemini.geminiInuput(user_input)
        return jsonify({'replay': response})
    return render_template("chat.html")

@app.route('/settings',methods=['GET','POST'])
def settings():
    return render_template("settings.html")

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    respone=make_response(redirect('/'))
    respone.set_cookie("loggedin",'',expires=0)
    respone.set_cookie("user_id",expires=0)
    respone.set_cookie("user_email",'',expires=0)
    respone.set_cookie("first_name",'',expires=0)
    respone.set_cookie("last_name",'',expires=0)
    respone.set_cookie("currency",'',expires=0)
    respone.set_cookie("phone_no",'',expires=0)
    respone.set_cookie("monthly_income",'',expires=0)
    respone.set_cookie("financial_goal",'',expires=0)
    respone.set_cookie("payday",'',expires=0)
    respone.set_cookie("budget_alert",'',expires=0)
    respone.set_cookie("unusual_spend_alert",'',expires=0)
    respone.set_cookie("investment_insights",'',expires=0)
    respone.set_cookie("budget_id","",expires=0)
    return respone

@app.route('/deleteAccount')
def deleteAccount():
    id=request.cookies.get("user_id")
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    respone=make_response(redirect('/'))
    delete_query_users="DELETE FROM users WHERE id = %s"
    myCursorPrivate.execute(delete_query_users,(id,))
    respone.set_cookie("loggedin",'',expires=0)
    respone.set_cookie("user_id",expires=0)
    respone.set_cookie("user_email",'',expires=0)
    respone.set_cookie("first_name",'',expires=0)
    respone.set_cookie("last_name",'',expires=0)
    respone.set_cookie("currency",'',expires=0)
    respone.set_cookie("phone_no",'',expires=0)
    respone.set_cookie("monthly_income",'',expires=0)
    respone.set_cookie("financial_goal",'',expires=0)
    respone.set_cookie("payday",'',expires=0)
    respone.set_cookie("budget_alert",'',expires=0)
    respone.set_cookie("unusual_spend_alert",'',expires=0)
    respone.set_cookie("investment_insights",'',expires=0)
    respone.set_cookie("budget_id","",expires=0)
    mydb.commit()
    return respone
@app.route('/budget',methods=['GET','POST'])
def budget():
    return render_template('budget.html')

@app.route("/api/setBudget",methods=['POST','GET'])
def setBudget():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        id=request.cookies.get("user_id")
        select_query="SELECT * FROM budgets WHERE user_id=%s"
        myCursorPrivate.execute(select_query,(id,))
        res=myCursorPrivate.fetchone()
        if res:
            return jsonify({"result":"Failed"})
        else:
            data=request.get_json()
            total_budget=data.get("total_budget")
            end_date=data.get('budget_end_date')
            start_date=data.get('budget_start_date')
            description=data.get('budget_description')
            insert_query="INSERT INTO budgets (user_id,budget_amount,start_date,end_date,allocated_budget,remaining_budget, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values=(id,total_budget,start_date,end_date,0,total_budget,description)
            myCursorPrivate.execute(insert_query,values)
            mydb.commit()
            select_query="SELECT * FROM budgets WHERE user_id=%s"
            myCursorPrivate.execute(select_query,(id,))
            res=myCursorPrivate.fetchone()
            response=make_response(jsonify({"result":"success"}))
            response.set_cookie("budget_id",str(res['budget_id']),max_age=60 * 60 * 24 * 365 * 10)
            return response
    return redirect('/budget')    

@app.route('/api/setCategory',methods=['POST','GET'])
def setCategory():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        id=request.cookies.get('user_id')
        budget_id=request.cookies.get('budget_id')
        data=request.get_json()
        category=data.get('category')
        amount_allocated=data.get('amount_allocated')
        category_notes=data.get('category_notes')
        select_query="SELECT * FROM category WHERE category = %s AND budget_id = %s"
        myCursorPrivate.execute(select_query,(category,budget_id))
        res=myCursorPrivate.fetchone()
        if res:
            return jsonify({"result":"Failed"})
        else:
            select_query="SELECT remaining_budget FROM budgets WHERE budget_id= %s"
            myCursorPrivate.execute(select_query,(budget_id,))
            res=myCursorPrivate.fetchone()
            if res==None:
                return jsonify({"error":"noBudget"})
            if int(amount_allocated)>int(res['remaining_budget']):
                return jsonify({"error":"highamount"})
            else:
                insert_query="INSERT INTO category (user_id, budget_id, category, amount_allocated, spent, remaining, category_notes) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                values=(id,budget_id,category,amount_allocated,0,amount_allocated,category_notes)
                myCursorPrivate.execute(insert_query,values)
                mydb.commit()
                select_query="SELECT * FROM budgets WHERE budget_id= %s"
                myCursorPrivate.execute(select_query,(budget_id,))
                res=myCursorPrivate.fetchone()
                new_allocated_budget=int(res['allocated_budget'])+int(amount_allocated)
                new_remaining_budget=int(res['remaining_budget'])-int(amount_allocated)
                update_query = "UPDATE budgets SET allocated_budget = %s, remaining_budget = %s WHERE budget_id = %s"
                myCursorPrivate.execute(update_query,(new_allocated_budget,new_remaining_budget,budget_id))
                mydb.commit()
                return jsonify({"success":"success","redirectURL":"/budget"})
    return redirect("/homePage")

@app.route('/api/getCateogry')
def get_category():
    try:
        budgetId=request.cookies.get("budget_id")
        select_query="SELECT * FROM category WHERE budget_id = %s"
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        myCursorPrivate.execute(select_query,(budgetId,))
        res=myCursorPrivate.fetchall()
        currency=request.cookies.get("currency")
        return jsonify({"result":res,"currency":currency})
    except Exception as e:
        print(e)
    

@app.route("/api/budget")
def budget_api():
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    id=request.cookies.get("user_id")
    budget_id=request.cookies.get("budget_id")
    currency=request.cookies.get("currency")
    monthly_income=request.cookies.get("monthly_income")
    select_query="SELECT * FROM budgets WHERE user_id = %s"
    myCursorPrivate.execute(select_query,(id,))
    res=myCursorPrivate.fetchone()
    if res==None:
        total_budget=0
        start_date=0
        end_date=""
        spend=0
        remaining=0
    else:
        total_budget=res['budget_amount']
        start_date=res["start_date"]
        end_date=res['end_date']
        select_query="SELECT sum(amount_allocated) FROM category WHERE budget_id = %s"
        myCursorPrivate.execute(select_query,(budget_id,))
        res=myCursorPrivate.fetchall()
        if res[0]['sum(amount_allocated)']== None:
            spend=0
            remaining=total_budget
        else:   
            spend=res[0]['sum(amount_allocated)']
            remaining=int(total_budget)-int(spend)
    data={
        "currency":currency,
        "monthly_income":monthly_income,
        "total_budget":total_budget,
        "start_date":start_date,
        "end_date":end_date,
        "spend":spend,
        "remaining":remaining
    }
    return jsonify(data)

@app.route('/api/settingDetails', methods=['GET'])
def settings_details():
    info = {
        "first_name": request.cookies.get("first_name",""),
        "last_name": request.cookies.get("last_name", ""),
        "email": request.cookies.get("user_email", ""),
        "currency": request.cookies.get("currency", ""),
        "phone_no": request.cookies.get("phone_no", ""),
        "monthly_income": request.cookies.get("monthly_income", ""),
        "financial_goal": request.cookies.get("financial_goal", ""),
        "payday": request.cookies.get("payday", ""),
        "budget_alert": request.cookies.get("budget_alert", "False"),
        "unusual_spend_alert": request.cookies.get("unusual_spend_alert", "False"),
        "investment_insights": request.cookies.get("investment_insights", "False")
    }
    return jsonify(info)


@app.route('/api/settingsUpdate',methods=['GET','POST'])
def settings_update():
    if request.method=='POST':
        conn=getConnection()
        myCursorPrivate=conn.cursor(dictionary=True)
        id=request.cookies.get("user_id")
        data=request.get_json()
        currency = data.get('currency')
        phone_no=data.get('phone_no')
        monthly_income = data.get('income')
        financial_goal = data.get('financial_goals')
        payday = data.get('payday')
        budget_alert = data.get('budget_alerts')
        unusual_spend_alert = data.get('unusual_spending')
        investment_insights = data.get('investment_insights')
        if phone_no=='':
            phone_no=None
        select_query="SELECT * FROM users_settings WHERE user_id =%s"
        myCursorPrivate.execute(select_query,(id,))
        res=myCursorPrivate.fetchone()
        if res:
            update_query="UPDATE users_settings SET mobile_no = %s,currency = %s, monthly_income = %s, financial_goal = %s, payday = %s, budget_alert = %s, unusual_spend_alert = %s, investment_insights = %s WHERE user_id = %s"
            values=(phone_no,currency,monthly_income,financial_goal,payday,budget_alert,unusual_spend_alert,investment_insights,id)
            myCursorPrivate.execute(update_query,values)
            mydb.commit()
        else:
            insert_query="INSERT INTO users_settings (user_id, mobile_no, currency, monthly_income, financial_goal, payday, budget_alert, unusual_spend_alert, investment_insights) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values=(id,phone_no,currency,monthly_income,financial_goal,payday,budget_alert,unusual_spend_alert,investment_insights)
            myCursorPrivate.execute(insert_query,values)
            mydb.commit()

        response=make_response(redirect('/api/settingDetails'))
        response.set_cookie("currency",currency,max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("phone_no",str(phone_no or ""),max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("monthly_income",monthly_income,max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("financial_goal",financial_goal,max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("payday",payday,max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("budget_alert",str(budget_alert),max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("unusual_spend_alert",str(unusual_spend_alert),max_age=60 * 60 * 24 * 365 * 10)
        response.set_cookie("investment_insights",str(investment_insights),max_age=60 * 60 * 24 * 365 * 10)
        return response
    return redirect('/settings')

@app.route('/viewPastTransaction')
def viewPastTransaction():
    return render_template("viewPastTransaction.html")

@app.route('/api/getEditPageData',methods=['POST','GET'])
def getEditPageData():
    conn=getConnection()
    budget_id=request.cookies.get('budget_id')
    myCursorPrivate=conn.cursor(dictionary=True)
    data=request.get_json()
    category=data.get('category')
    select_query="SELECT amount_allocated FROM category WHERE budget_id = %s AND category = %s"
    value=(budget_id,category)
    myCursorPrivate.execute(select_query,value)
    res=myCursorPrivate.fetchone()
    amount_allocated=res['amount_allocated']
    return jsonify({"amount_allocated":amount_allocated})

@app.route('/api/setEditAmount',methods=['POST','GET'])
def setEditAmount():
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    budget_id=request.cookies.get('budget_id')
    data=request.get_json()
    category=data.get('category')
    newAmount=data.get('newAmount')
    select_query="SELECT remaining_budget,budget_amount FROM budgets WHERE budget_id = %s"
    myCursorPrivate.execute(select_query,(budget_id,))
    res=myCursorPrivate.fetchone()
    budget_amount=res['budget_amount']
    if int(newAmount)>int(res['remaining_budget']):
        return jsonify({"result":"failed"})
    else:
        select_query="SELECT spent FROM category WHERE budget_id = %s AND category = %s"
        myCursorPrivate.execute(select_query,(budget_id,category))
        res=myCursorPrivate.fetchone()
        update_query="UPDATE category SET amount_allocated = %s, remaining =%s WHERE category = %s AND budget_id = %s"
        remaining=int(newAmount)-int(res['spent'])
        value=(newAmount,remaining,category,budget_id)
        myCursorPrivate.execute(update_query,value)
        mydb.commit()
        select_query="SELECT sum(amount_allocated) FROM category WHERE budget_id = %s"
        myCursorPrivate.execute(select_query,(budget_id,))
        res=myCursorPrivate.fetchall()
        allocated_budget=res[0]['sum(amount_allocated)']
        remaining_budget=budget_amount-res[0]['sum(amount_allocated)']
        update_query="UPDATE budgets SET allocated_budget = %s, remaining_budget = %s WHERE budget_id = %s"
        value=(allocated_budget,remaining_budget,budget_id)
        myCursorPrivate.execute(update_query,value)
        mydb.commit()
        return jsonify({"result":"success"})

@app.route('/api/deleteCategory',methods=['POST','GET'])
def deleteCategory():
    conn=getConnection()
    myCursorPrivate=conn.cursor(dictionary=True)
    data=request.get_json()
    category_id=data.get('category_id')
    delete_query="DELETE FROM category WHERE id = %s"
    myCursorPrivate.execute(delete_query,(category_id,))
    mydb.commit()
    return jsonify({"result":"success"})

@app.route('/api/getExpense')
def getPastTransaction():
    conn=getConnection() 
    budget_id=request.cookies.get('budget_id')
    currency=request.cookies.get('currency')
    select_query="SELECT expense,description,date FROM expenses WHERE budget_id = %s"
    myCursorPrivate=conn.cursor(dictionary=True)
    myCursorPrivate.execute(select_query,(budget_id,))
    res=myCursorPrivate.fetchall()
    return jsonify({"result":"success","values":res,"currency":currency})

@app.route('/editPage')
def editPage():
    return render_template('editPage.html')
if __name__=='__main__':
    app.run(debug=True)