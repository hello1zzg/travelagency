from flask import Flask, redirect, url_for, request, render_template, session
import pymysql, time, json, subprocess
from urllib import request as rq
from forms import LoanForm
from loan_calculator import loan_calculator

app = Flask(__name__)
app.secret_key = 'development key'


'''
session用作全局变量:
name, userId,
'''


@app.route('/')
def index():
    return render_template("login.html")


@app.route('/login',methods = ['POST', 'GET'])
def login():
    name = request.form.get("nm")
    password = request.form.get("pd")
    # print(name, password)
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= '12138', db= 'loan')

    sql1 = "SELECT id, password FROM User WHERE name = '%s'"%(name)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql1)
            User_data = cursor.fetchone()
            # print(User_data)
    except Exception as e:
        print(e)

    mysql_conn.close()

    if User_data == None:
        return "用户不存在"
    elif password == User_data[1]:
        if name == 'bankadmin1' or name == 'bankadmin2' or name == 'bankadmin3':
            session["bankadmin"] = name
            return redirect(url_for('bank_manual_judge'))
        elif name == 'fundadmin':
            return redirect(url_for('fund_manual_judge'))
        session["userId"] = User_data[0]
        session['name'] = name
        return redirect(url_for('get_services'))
    else:
        return "密码错误"


@app.route('/get_services',methods = ['POST', 'GET'])
def get_services():
    name = session["name"]
    if not name:
        return redirect(url_for('login'))  # 如果未登录，重定向到登录页面
    return render_template("service_selection.html", name = name)

@app.route('/ticket_purchase')
def ticket_purchase():
    # 这里处理机票购买逻辑
    return render_template("ticket_purchase.html")

@app.route('/hotel_booking')
def hotel_booking():
    return render_template("hotel_booking.html")

@app.route('/car_rental')
def car_rental():
    return render_template("car_rental.html")

@app.route('/attraction_selection')
def attraction_selection():
    return render_template("attraction_selection.html")

@app.route('/submit_loanEXP',methods = ['POST', 'GET'])
def submit_loanEXP():
    loanEXP = int(request.form.get("loanEXP"))
    session["loanEXP"] = loanEXP
    name = session["name"]
    userId = session["userId"]

    # '''
    # 把b图实例化
    # '''
    # staticAllocationTable = open("/Users/xuwei/Documents/课程/微服务与区块链/大作业/workflow/table/2022104167loan.bpmn.table", 'r').read()
    # deploymentName = "2022104167loan.bpmn"
    # processData = open("/Users/xuwei/Documents/课程/微服务与区块链/大作业/workflow/data/processData.txt", 'r').read()
    # businessData = open("/Users/xuwei/Documents/课程/微服务与区块链/大作业/workflow/data/instanceData.txt", 'r').read()
    # processData=processData.replace("\n","")
    # businessData=businessData.replace("\n","")
    # staticAllocationTable=staticAllocationTable.replace("\n","")

    # map1={}
    # map1["deploymentName"]=deploymentName
    # map1["processData"]=processData
    # map1["businessData"]=businessData
    # map1["staticAllocationTable"]=staticAllocationTable
    # map1["fcn"]="instance"
    # datajsonstr1=json.dumps(map1)
    # preStr="curl -X POST http://10.77.70.173:8999/grafana/wfRequest -H \"Accept: application/json\" -H \"Content-Type: application/json\" -d "
    # curlString=preStr+json.dumps(datajsonstr1)
    # print(curlString)
    # result1 = subprocess.Popen(curlString, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8').communicate()[0]
    # print(result1)
    # resultMap1=json.loads(result1)

    # if resultMap1["模拟执行结果"]:
    #     f=open("workflow/data/oid.txt","w")
    #     f.truncate(0)
    #     f.write(resultMap1["Oid"])
    #     f.close()

    # time.sleep(3)

    '''
    从complete借鉴的代码, 用于usertask向bpmn中连接的servicetask传数据, 传的业务数据放在businessData
    '''
    headers = {'Content-Type': 'application/json'}
    # 如果程序运行过了，需要重新实例化一次bpmn，每次实例化返回新的oid
    Oid=open("/Users/xuwei/Documents/课程/微服务与区块链/大作业/workflow/data/oid.txt",'r').read()
    # Oid = resultMap1["Oid"]
    # print(Oid)
    user = "anyone"
    taskName = "submit"
    processData= "{}"
    businessData=json.dumps({"userId":userId, "loanEXP":loanEXP})
    map={}
    map["taskName"]=taskName
    map["processData"]=processData
    map["businessData"]=businessData
    map["user"]=user
    map["fcn"]="complete"
    map["Oid"]=Oid
    datajsonstr=json.dumps(map)
    r=rq.Request(url="http://10.77.70.173:8999/grafana/wfRequest",data=bytes(datajsonstr,"utf-8"),headers=headers)
    result = rq.urlopen(r).read().decode('utf-8')
    print(result.encode('utf-8'))
    resultMap=json.loads(result)
    # return resultMap

    '''
    获取执行的结果需要执行query.sh,下面的代码相当于实现了query.sh, 获取到servicetask自动流转的最终结果
    '''
    responseMap = {}
    if resultMap["code"]==500:
        responseMap["code"]=500
        responseMap["body"]=resultMap["body"]
        responseMap["state"]="Failed"
        return responseMap
    oid1=resultMap["Oid"]
    # print(oid1)
    getResponseUrl="http://10.77.70.173:8999/grafana/getResByOid/"+oid1
    for i in range(50):
        time.sleep(0.2)
        r=rq.Request(url=getResponseUrl)
        res = rq.urlopen(r).read().decode('utf-8')
        print(res)
        if res!="none":
            resMap=json.loads(res)
            if "isEnd" in resMap:
                responseMap["code"]=200
                responseMap["body"]=resMap["businessData"]
                responseMap["state"]="Success"
                # return responseMap
                res_body = responseMap["body"]
                session["loan_rec"] = res_body
                return redirect(url_for('choose_loan_plan'))
    responseMap["code"]=500
    responseMap["body"]="time out,It may be that the write to blockchain failed"
    responseMap["state"]="Failed"
    return responseMap


@app.route('/choose_loan_plan', methods = ['GET', 'POST'])
def choose_loan_plan():
    loanEXP = session["loanEXP"]
    loan_rec = session["loan_rec"]
    # print(loan_rec)
    loan_rec_dict = json.loads(loan_rec)

    form = LoanForm()
    if form.validate_on_submit():
        loan_type = form.loan_type.data
        repay_type = form.repay_type.data
        term = form.term.data
        f_amount = form.f_amount.data
        bankId = form.bankId.data
        b_amount = form.b_amount.data
        session['loan_type'] = loan_type
        session['repay_type'] = repay_type
        session['term'] = term
        session['f_amount'] = f_amount
        session['bankId'] = bankId
        session['b_amount'] = b_amount
        return redirect(url_for('confirm_loan_plan'))
    else:
        return render_template('choose_loan_plan.html', loan_rec_dict = loan_rec_dict, loanEXP = loanEXP, form = form)


@app.route('/confirm_loan_plan', methods = ['GET', 'POST'])
def confirm_loan_plan():
    userId = session["userId"]
    loan_type = session.get("loan_type")
    repay_type = session.get("repay_type")
    term = session.get("term")
    f_amount = session.get("f_amount")
    bankId = session.get("bankId")
    b_amount = session.get("b_amount")

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql1 = "SELECT rate FROM Bank WHERE id = %s"%(bankId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql1)
            Bank_data = cursor.fetchone()
            # print(Bank_data)
    except Exception as e:
        print(e)

    sql2 = "SELECT discount FROM BankUser WHERE bankId = %s AND UserId = %s"%(bankId, userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql2)
            BankUser_data = cursor.fetchone()
            # print(BankUser_data)
    except Exception as e:
        print(e)

    sql3 = "SELECT rate FROM FundUser WHERE userId = %s"%(userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql3)
            FundUser_data = cursor.fetchone()
            # print(FundUser_data)
    except Exception as e:
        print(e)
    
    mysql_conn.close()

    d_rate = round(Bank_data[0] * BankUser_data[0],4)
    f_rate = FundUser_data[0]
    session["d_rate"] = d_rate
    session["f_rate"] = f_rate

    loan_cal_dict = {}
    if loan_type == 1:               # 公积金贷款
        loan_cal_dict = loan_calculator(f_amount, f_rate * 100, term, repay_type)
        session["f_total_pay"] = loan_cal_dict["total_pay"]
        session["f_monthly_pay"] = loan_cal_dict["monthly_pay"]
        session["f_monthly_decrement"] = loan_cal_dict["monthly_decrement"]
        session["b_total_pay"] = 0
        session["b_monthly_pay"] = 0
        session["b_monthly_decrement"] = 0
    elif loan_type == 2:             # 混合贷款
        b_loan_cal_dict = loan_calculator(b_amount, d_rate * 100, term, repay_type)
        session["b_total_pay"] = b_loan_cal_dict["total_pay"]
        session["b_monthly_pay"] = b_loan_cal_dict["monthly_pay"]
        session["b_monthly_decrement"] = b_loan_cal_dict["monthly_decrement"]
        f_loan_cal_dict = loan_calculator(f_amount, f_rate * 100, term, repay_type)
        session["f_total_pay"] = f_loan_cal_dict["total_pay"]
        session["f_monthly_pay"] = f_loan_cal_dict["monthly_pay"]
        session["f_monthly_decrement"] = f_loan_cal_dict["monthly_decrement"]
        loan_cal_dict["total_pay"] = b_loan_cal_dict["total_pay"] + f_loan_cal_dict["total_pay"]
        loan_cal_dict["monthly_pay"] = b_loan_cal_dict["monthly_pay"] + f_loan_cal_dict["monthly_pay"]
        loan_cal_dict["monthly_decrement"] = b_loan_cal_dict["monthly_decrement"] + f_loan_cal_dict["monthly_decrement"]
    elif loan_type == 3:             # 商业贷款
        loan_cal_dict = loan_calculator(b_amount, d_rate * 100, term, repay_type)
        session["b_total_pay"] = loan_cal_dict["total_pay"]
        session["b_monthly_pay"] = loan_cal_dict["monthly_pay"]
        session["b_monthly_decrement"] = loan_cal_dict["monthly_decrement"]
        session["f_total_pay"] = 0
        session["f_monthly_pay"] = 0
        session["f_monthly_decrement"] = 0
    total_pay = loan_cal_dict["total_pay"]
    monthly_pay = loan_cal_dict["monthly_pay"]
    monthly_decrement = loan_cal_dict["monthly_decrement"]
    session["total_pay"] = total_pay
    session["monthly_pay"] = monthly_pay
    session["monthly_decrement"] = monthly_decrement
    # print(f_amount, f_rate, term, repay_type)                            # debug
    # print(type(f_amount), type(f_rate), type(term), type(repay_type))    # debug
    # print(loan_cal_dict)                                                 # debug

    return render_template("confirm_loan_plan.html", loan_type = loan_type, total_amount = f_amount + b_amount, repay_type = repay_type,
                            total_pay = total_pay, term = term, monthly_pay = monthly_pay, monthly_decrement = monthly_decrement)


@app.route('/submit_loan_plan', methods = ['GET', 'POST'])
def submit_loan_plan():
    userId = session["userId"]
    name = session["name"]
    loan_type = session.get("loan_type")
    repay_type = session.get("repay_type")
    term = session.get("term")
    f_rate = session["f_rate"]
    f_amount = session.get("f_amount")
    f_interest = session["f_total_pay"] - f_amount
    f_total_pay = session["f_total_pay"]
    f_monthly_pay = session["f_monthly_pay"]
    f_monthly_decrement = session["f_monthly_decrement"]
    bankId = session.get("bankId")
    d_rate = session["d_rate"]
    b_amount = session.get("b_amount")
    b_interest = session["b_total_pay"] - b_amount
    b_total_pay = session["b_total_pay"]
    b_monthly_pay = session["b_monthly_pay"]
    b_monthly_decrement = session["b_monthly_decrement"]

    '''
    从complete借鉴的代码, 用于usertask向bpmn中连接的servicetask传数据, 传的业务数据放在businessData
    '''
    headers = {'Content-Type': 'application/json'}
    # 如果程序运行过了，需要重新实例化一次bpmn，每次实例化返回新的oid
    Oid=open("/Users/xuwei/Documents/课程/微服务与区块链/大作业/workflow/data/oid.txt",'r').read()
    user = "anyone"
    taskName = "submit_loan_plan"
    processData= "{}"
    businessData=json.dumps({
        "userId":userId,
        "name":name,
        "loan_type":loan_type,
        "repay_type":repay_type,
        "term":term,
        "f_rate":f_rate,
        "f_amount":f_amount,
        "f_interest":f_interest,
        "f_total_pay":f_total_pay,
        "f_monthly_pay":f_monthly_pay,
        "f_monthly_decrement":f_monthly_decrement,
        "bankId":bankId,
        "d_rate":d_rate,
        "b_amount":b_amount,
        "b_interest":b_interest,
        "b_total_pay":b_total_pay,
        "b_monthly_pay":b_monthly_pay,
        "b_monthly_decrement":b_monthly_decrement
    })
    map={}
    map["taskName"]=taskName
    map["processData"]=processData
    map["businessData"]=businessData
    map["user"]=user
    map["fcn"]="complete"
    map["Oid"]=Oid
    datajsonstr=json.dumps(map)
    r=rq.Request(url="http://10.77.70.173:8999/grafana/wfRequest",data=bytes(datajsonstr,"utf-8"),headers=headers)
    result = rq.urlopen(r).read().decode('utf-8')
    print(result.encode('utf-8'))
    resultMap=json.loads(result)
    print(resultMap)

    '''
    获取执行的结果需要执行query.sh, 下面的代码相当于实现了query.sh, 获取到servicetask自动流转的最终结果
    '''
    responseMap = {}
    if resultMap["code"]==500:
        responseMap["code"]=500
        responseMap["body"]=resultMap["body"]
        responseMap["state"]="Failed"
        return responseMap
    oid2=resultMap["Oid"]
    getResponseUrl="http://10.77.70.173:8999/grafana/getResByOid/"+oid2
    for i in range(50):
        time.sleep(0.2)
        r=rq.Request(url=getResponseUrl)
        res = rq.urlopen(r).read().decode('utf-8')
        if res!="none":
            resMap=json.loads(res)
            if "isEnd" in resMap:
                responseMap["code"]=200
                responseMap["body"]=resMap["businessData"]
                responseMap["state"]="Success"
                # return responseMap
                resData = json.loads(responseMap["body"])
                loan_time = resData["loan_time"]
                session["loan_time"] = loan_time
                return redirect(url_for('wait_judge'))
    responseMap["code"]=500
    responseMap["body"]="time out,It may be that the write to blockchain failed"
    responseMap["state"]="Failed"
    return responseMap


def wait_bank_judge(loan_time):
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql = "SELECT manual_judge FROM BankLoan WHERE loan_time = '%s'"%(loan_time)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            manual_judge = cursor.fetchone()[0]
            # print(manual_judge)
    except Exception as e:
        print(e)

    mysql_conn.close()

    if manual_judge == 1:
        return 1
    elif manual_judge == 0:
        return 0
    return -1


def wait_fund_judge(loan_time):
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql = "SELECT manual_judge FROM FundLoan WHERE loan_time = '%s'"%(loan_time)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            manual_judge = cursor.fetchone()[0]
            # print(manual_judge)
    except Exception as e:
        print(e)

    mysql_conn.close()

    if manual_judge == 1:
        return 1
    elif manual_judge == 0:
        return 0
    return -1


@app.route('/wait_judge', methods = ['GET', 'POST'])
def wait_judge():
    loan_type = session["loan_type"]
    loan_time = session["loan_time"]
    f_amount = session["f_amount"]
    b_amount = session["b_amount"]
    repay_type = session["repay_type"]
    total_pay = session["total_pay"]
    term = session["term"]
    monthly_pay = session["monthly_pay"]
    monthly_decrement = session["monthly_decrement"]
    # f_manual_judge = -1
    # b_manual_judge = -1
    if loan_type == 1:
        f_manual_judge = wait_fund_judge(loan_time)
        if f_manual_judge == 0 or f_manual_judge == 1:
            # time.sleep(2)
            return render_template("loan_result.html", loan_type = loan_type, f_amount = f_amount, b_amount = b_amount, 
                                repay_type = repay_type, total_pay = total_pay, term = term, monthly_pay = monthly_pay, 
                                monthly_decrement = monthly_decrement, loan_result = f_manual_judge)
        return render_template("wait_judge.html")
        
    elif loan_type == 2:
        b_manual_judge = wait_bank_judge(loan_time)
        f_manual_judge = wait_fund_judge(loan_time)
        if b_manual_judge != 0 and b_manual_judge != 1:
            # time.sleep(2)
            return render_template("wait_judge.html")
        if f_manual_judge != 0 and f_manual_judge != 1:
            # time.sleep(2)
            return render_template("wait_judge.html")
        print(b_manual_judge, f_manual_judge)
        if b_manual_judge == 1 and f_manual_judge == 1:
            manual_judge = 1
        else:
            manual_judge = 0
        return render_template("loan_result.html", loan_type = loan_type, f_amount = f_amount, b_amount = b_amount, 
                                repay_type = repay_type, total_pay = total_pay, term = term, monthly_pay = monthly_pay, 
                                monthly_decrement = monthly_decrement, b_loan_result = b_manual_judge, 
                                f_loan_result = f_manual_judge, loan_result = manual_judge)
    elif loan_type == 3:
        b_manual_judge = wait_bank_judge(loan_time)
        if b_manual_judge != 0 and b_manual_judge != 1:
            # time.sleep(2)
            return render_template("wait_judge.html")
        return render_template("loan_result.html", loan_type = loan_type, f_amount = f_amount, b_amount = b_amount, 
                                repay_type = repay_type, total_pay = total_pay, term = term, monthly_pay = monthly_pay, 
                                monthly_decrement = monthly_decrement, loan_result = b_manual_judge)


@app.route('/bank_manual_judge', methods = ['GET', 'POST'])
def bank_manual_judge():
    bankadmin = session["bankadmin"]
    # userId = session["userId"]
    # name = session["name"]
    # loan_type = session["loan_type"]
    # repay_type = session["repay_type"]
    # term = session["term"]
    # d_rate = session["d_rate"]
    # b_amount = session["b_amount"]
    # b_interest = session["b_total_pay"] - b_amount
    # b_total_pay = session["b_total_pay"]
    # b_monthly_pay = session["b_monthly_pay"]
    # b_monthly_decrement = session["b_monthly_decrement"]
    # loan_time = session["loan_time"]
    # bankId = session["bankId"]

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql1 = "SELECT * FROM BankLoan WHERE bankId = '%s' AND manual_judge IS NULL"%(bankadmin[-1])
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql1)
            BankLoan_data = cursor.fetchone()
            # print(BankLoan_data)
    except Exception as e:
        print(e)

    if BankLoan_data == None:
        return "暂时没有贷款需要审批"

    userId = BankLoan_data[2]
    loan_type = BankLoan_data[3]
    repay_type = BankLoan_data[4]
    term = BankLoan_data[5]
    d_rate = BankLoan_data[6]
    b_amount = BankLoan_data[7]
    b_interest = BankLoan_data[8]
    b_total_pay = BankLoan_data[9]
    b_monthly_pay = BankLoan_data[10]
    b_monthly_decrement = BankLoan_data[11]
    loan_time = BankLoan_data[12]
    auto_judge = BankLoan_data[13]

    session["loan_time"] = loan_time

    if loan_type == 1:
        return "暂时没有贷款需要审批"

    sql2 = "SELECT name, credit, salary FROM User WHERE id = '%s'"%(userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql2)
            User_data = cursor.fetchone()
            # print(User_data)
    except Exception as e:
        print(e)

    username = User_data[0]
    credit = User_data[1]
    salary = User_data[2]

    sql3 = "SELECT deposit, quota FROM BankUser WHERE userId = '%s'"%(userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql3)
            # print(BankUser_data)
    except Exception as e:
        print(e)

    BankUser_data = cursor.fetchone()
    deposit = BankUser_data[0]
    quota = BankUser_data[1]

    mysql_conn.close()

    return render_template("bank_manual_judge.html", userId = userId, username = username, credit = credit, salary = salary,
                            deposit = deposit, quota = quota, loan_type = loan_type, repay_type = repay_type,
                            term = term, d_rate = d_rate, b_amount = b_amount, b_interest = b_interest, b_total_pay = b_total_pay, 
                            b_monthly_pay = b_monthly_pay, b_monthly_decrement = b_monthly_decrement, auto_judge = auto_judge)


@app.route('/fund_manual_judge', methods = ['GET', 'POST'])
def fund_manual_judge():
    # userId = session["userId"]
    # name = session["name"]
    # loan_type = session["loan_type"]
    # repay_type = session["repay_type"]
    # term = session["term"]
    # f_rate = session["f_rate"]
    # f_amount = session["f_amount"]
    # f_interest = session["f_total_pay"] - f_amount
    # f_total_pay = session["f_total_pay"]
    # f_monthly_pay = session["f_monthly_pay"]
    # f_monthly_decrement = session["f_monthly_decrement"]
    # loan_time = session["loan_time"]

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql1 = "SELECT * FROM FundLoan WHERE manual_judge IS NULL"
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql1)
            FundLoan_data = cursor.fetchone()
            # print(FundLoan_data)
    except Exception as e:
        print(e)

    if FundLoan_data == None:
        return "暂时没有贷款需要审批"

    userId = FundLoan_data[1]
    loan_type = FundLoan_data[2]
    repay_type = FundLoan_data[3]
    term = FundLoan_data[4]
    f_rate = FundLoan_data[5]
    f_amount = FundLoan_data[6]
    f_interest = FundLoan_data[7]
    f_total_pay = FundLoan_data[8]
    f_monthly_pay = FundLoan_data[9]
    f_monthly_decrement = FundLoan_data[10]
    loan_time = FundLoan_data[11]
    auto_judge = FundLoan_data[12]

    session["loan_time"] = loan_time

    if loan_type == 3:
        return "暂时没有贷款需要审批"

    sql2 = "SELECT name, credit, salary FROM User WHERE id = '%s'"%(userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql2)
            User_data = cursor.fetchone()
            # print(User_data)
    except Exception as e:
        print(e)
    
    username = User_data[0]
    credit = User_data[1]
    salary = User_data[2]

    sql3 = "SELECT deposit, quota, f_month FROM FundUser WHERE userId = '%s'"%(userId)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql3)
            FundUser_data = cursor.fetchone()
            # print(FundUser_data)
    except Exception as e:
        print(e)

    deposit = FundUser_data[0]
    quota = FundUser_data[1]
    f_month = FundUser_data[2]

    mysql_conn.close()


    return render_template("fund_manual_judge.html", userId = userId, username = username, credit = credit, salary = salary,
                            deposit = deposit, quota = quota, f_month = f_month, loan_type = loan_type, repay_type = repay_type,
                            term = term, f_rate = f_rate, f_amount = f_amount, f_interest = f_interest, f_total_pay = f_total_pay, 
                            f_monthly_pay = f_monthly_pay, f_monthly_decrement = f_monthly_decrement, auto_judge = auto_judge)


@app.route('/store_bank_judge/<manual_judge>', methods = ['GET', 'POST'])
def store_bank_judge(manual_judge):
    loan_time = session["loan_time"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql = "UPDATE BankLoan SET manual_judge = %s WHERE loan_time = %s" % (manual_judge, loan_time)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
    except Exception as e:
        print(e)
    mysql_conn.commit()
    mysql_conn.close()

    return "审批完成"


@app.route('/store_fund_judge/<manual_judge>', methods = ['GET', 'POST'])
def store_fund_judge(manual_judge):
    loan_time = session["loan_time"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'root', password= 'rootroot', db= 'loan')

    sql = "UPDATE FundLoan SET manual_judge = %s WHERE loan_time = %s" % (manual_judge, loan_time)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
    except Exception as e:
        print(e)
    mysql_conn.commit()
    mysql_conn.close()

    return "审批完成"


if __name__ == '__main__':
    # app.run(port=2023)
    app.run(debug = True, port=2023)
