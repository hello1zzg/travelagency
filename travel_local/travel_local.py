from flask import Flask, redirect, url_for, request, render_template, session, jsonify
import pymysql, time, json
import requests
from urllib import request as rq
import re
import subprocess

app = Flask(__name__)
app.secret_key = 'development key'


'''
session用作全局变量:
name, userId,
'''

def parse_ticket_result(ticket_result_str):
    if not ticket_result_str:
        return []
    ticket_pattern = r'\{price=(.*?), company_name=(.*?), arrival_city=(.*?), departure_city=(.*?), departure_time=(.*?), flight_id=(.*?)\}'
    tickets = re.findall(ticket_pattern, ticket_result_str)
    return [{"flight_id": int(t[5]), "departure_city": t[3], "arrival_city": t[2], "departure_time": t[4], "price": f"￥{float(t[0]):.2f}", "airline": t[1]} for t in tickets]

def parse_hotel_result(hotel_result_str):
    if not hotel_result_str:
        return []
    hotel_pattern = r'\{room_id=(.*?), room_price=(.*?), rating=(.*?), room_number=(.*?), room_type=(.*?), hotel_name=(.*?)\}'
    hotels = re.findall(hotel_pattern, hotel_result_str)
    return [{"room_id": int(h[0]), "room_number": h[3], "room_type": h[4], "price": f"￥{float(h[1]):.2f}"} for h in hotels]

def parse_car_rental_result(car_rental_result_str):
    if not car_rental_result_str:
        return []
    
    car_rental_pattern = r'car\d+=\{return_location=(.*?), price=(.*?), company_name=(.*?), rating=(.*?), rental_location=(.*?), carrental_id=(\d+), transmission_type=(.*?), car_type=(.*?)\}'
    car_rentals = re.findall(car_rental_pattern, car_rental_result_str)
    return [
        {
            "carrental_id": int(c[5]),
            "car_type": c[7],
            "transmission_type": c[6],
            "rental_location": c[4],
            "return_location": c[0],
            "price": f"￥{float(c[1]):.2f}",
            "company_name": c[2],
            "rating": float(c[3])
        }
        for c in car_rentals
    ]

def parse_attraction_result(attraction_result_str):
    if not attraction_result_str:
        return []
    attraction_pattern = r'\{attraction_name=(.*?), city=(.*?), price=(.*?), attraction_id=(.*?), rating=(.*?)\}'
    attractions = re.findall(attraction_pattern, attraction_result_str)
    return [{"attraction_id": int(a[3]), "attraction_name": a[0], "city": a[1], "price": f"￥{float(a[2]):.2f}"} for a in attractions]


@app.route('/')
def index():
    return render_template("login.html")


@app.route('/login',methods = ['POST', 'GET'])
def login():
    name = request.form.get("nm")
    password = request.form.get("pd")
    print(name,password)
    headers = {'Content-Type': 'application/json'}
    map = {}
    map["name"] = name
    map["password"] = password
    datajson = json.dumps(map)
    r=rq.Request(url="http://10.43.124.131:2024/login",data=bytes(datajson, "utf-8"),headers=headers)
    result = rq.urlopen(r).read().decode('utf-8')
    print(result)
    if result == "用户不存在":
        return "用户不存在"
    elif result == "密码正确":
        session["name"] = name
        # 调用 instance.py 实例化流程
        if(name == "airadmin"): 
            return redirect(url_for('admin_dashboard'))  # 新增重定向到企业端
        try:
            subprocess.run([
                'python3', 
                '/home/torres/codes/travelAgency/workflow/instance.py',  # 绝对路径
                '--allocationTablePath=/home/torres/codes/travelAgency/workflow/table/0923_Submit.bpmn.table',  # 绝对路径
                '--deploymentName=0923TravelRecommend.bpmn', 
                '--processDataPath=/home/torres/codes/travelAgency/workflow/data/processData.txt',  # 绝对路径
                '--businessDataPath=/home/torres/codes/travelAgency/workflow/data/instanceData.txt'  # 绝对路径
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while executing instance script: {e}")
            return "Failed to instantiate BPMN process"

        return redirect(url_for('get_services'))
    elif result == "密码错误":
        return "密码错误"

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get("name") != "airadmin":
        return redirect(url_for('login'))  # 非管理员重定向到登录页面

    mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='ysm', password='yangshiming', db='ysm_tourism')

    # 查询 ticket, hotel, car rental 和 attraction 表的信息
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM FlightInfo")
            tickets = cursor.fetchall()

            cursor.execute("SELECT * FROM Hotel")
            hotels = cursor.fetchall()

            cursor.execute("SELECT * FROM CarRental")
            car_rentals = cursor.fetchall()

            cursor.execute("SELECT * FROM Attraction")
            attractions = cursor.fetchall()
            
            print("-------------------------------")
            print("Ticket Result:", tickets)
            print("Hotel Result:", hotels)
            print("Car Rental Result:", car_rentals)
            print("Attraction Result:", attractions)

    except Exception as e:
        print(f"Database query error: {e}")
        tickets, hotels, car_rentals, attractions = [], [], [], []
    finally:
        mysql_conn.close()

    return render_template('admin_dashboard.html', tickets=tickets, hotels=hotels, car_rentals=car_rentals, attractions=attractions)

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    flight_id = request.form.get('flight_id')  # 获取 'flight_id' 而不是 'ticket_id'
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_time = request.form.get('departure_time')
    price = request.form.get('price')
    rating = request.form.get('rating')
    company_id = 1  # 根据需要设定或获取 company_id

    try:
        mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='ysm', password='yangshiming', db='ysm_tourism')
        with mysql_conn.cursor() as cursor:
            sql = "INSERT INTO FlightInfo (flight_id, departure_city, arrival_city, departure_time, price, rating, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (flight_id, departure_city, arrival_city, departure_time, price, rating, company_id))
        mysql_conn.commit()
    except Exception as e:
        print(e)
        return "Error adding ticket"
    finally:
        mysql_conn.close()

    return redirect(url_for('admin_dashboard'))



@app.route('/delete_ticket', methods=['POST'])
def delete_ticket():

    ticket_id = request.form.get('ticket_id')

    try:
        mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='ysm', password='yangshiming', db='ysm_tourism')
        with mysql_conn.cursor() as cursor:
            sql = "DELETE FROM FlightInfo WHERE flight_id = %s"
            cursor.execute(sql, (ticket_id,))
        mysql_conn.commit()
    except Exception as e:
        print(e)
        return "Error deleting ticket"
    finally:
        mysql_conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/update_ticket', methods=['POST'])
def update_ticket():
    ticket_id = request.form.get('flight_id')  # 从表单获取 'flight_id'
    new_departure_city = request.form.get('departure_city')
    new_arrival_city = request.form.get('arrival_city')
    new_departure_time = request.form.get('departure_time')  # 使用 'departure_time' 而不是 'departure_date'
    new_price = request.form.get('price')
    new_rating = request.form.get('rating')
    try:
        mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='ysm', password='yangshiming', db='ysm_tourism')
        with mysql_conn.cursor() as cursor:
            # 更新 SQL 语句中的字段名称也要对应修改
            sql = "UPDATE FlightInfo SET departure_city = %s, arrival_city = %s, departure_time = %s, price = %s, rating = %s WHERE flight_id = %s"
            cursor.execute(sql, (new_departure_city, new_arrival_city, new_departure_time, new_price, new_rating, ticket_id))
        mysql_conn.commit()
    except Exception as e:
        print(e)
        return "Error updating ticket"
    finally:
        mysql_conn.close()

    return redirect(url_for('admin_dashboard'))




@app.route('/get_services',methods = ['POST', 'GET'])
def get_services():
    name = session["name"]
    if not name:
        return redirect(url_for('login'))  # 如果未登录，重定向到登录页面
    return render_template("service_submit.html", name = name)

@app.route('/submit_travel_info', methods=['POST', 'GET'])
def submit_travel_info():

    # 获取表单数据
    departure_date = request.form.get("departure_date")
    departure_city = request.form.get("departure_city")
    arrival_city = request.form.get("arrival_city")
    need_car = request.form.get("need_car")
    car_type = request.form.get("car_type") if need_car == "yes" else None

    gear_type = request.form.get("gear_type") if need_car == "yes" else None
    guide = request.form.get("guide")
    preference = request.form.get("preference")

    # 构造业务数据的 Python 字典
    business_data_dict = {
        "departure_date": departure_date,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "need_car": need_car,
        "car_type": car_type,
        "gear_type": gear_type,
        # "guide": guide,
        "preference": preference
    }
    # 将业务数据字典序列化为 JSON 字符串
    business_data_json = json.dumps(business_data_dict,ensure_ascii=False)

    # 准备发送请求的数据
    Oid = open("/home/torres/codes/travelAgency/workflow/data/oid.txt", 'r').read().strip()
    request_data = {
        "Oid": Oid,
        "taskName": "Submit",
        "processData": "{}",
        "businessData": business_data_json,
        "user": "anyone"
    }
    print(json.dumps(business_data_json, ensure_ascii=False))
    # 发送请求到 BPMN 服务
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url="http://10.77.110.222:8999/grafana/wfRequest/complete", 
                             data=json.dumps(request_data), 
                             headers=headers)
    if response.status_code != 200:
        # 处理失败情况
        print("Error in BPMN request:", response.text)
        return jsonify({"error": "Failed to process BPMN request"})
    # 处理成功情况
    print("BPMN request successful:", response.text)

    url = "http://10.77.110.222:8999/grafana/getResponseByOid/"+Oid
    payload = {}
    headers = {}
    time.sleep(1)
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    response_text=response.text
    # 解析 JSON 字符串
    response_data = json.loads(response_text)

    # 提取 businessData 字段
    business_data_str = response_data["businessData"]

    # 解析 businessData 的 JSON 字符串
    business_data = json.loads(business_data_str)

    # 提取各个结果
    ticket_result = business_data.get("ticket_result")
    hotel_result = business_data.get("hotel_result")
    car_rental_result = business_data.get("car_rental_result")
    attraction_result = business_data.get("attraction_result")

    # 打印结果
    print("-------------------------------")
    print("Ticket Result:", ticket_result)
    print("Hotel Result:", hotel_result)
    print("Car Rental Result:", car_rental_result)
    print("Attraction Result:", attraction_result)

    form_data = {
        "flights": parse_ticket_result(ticket_result),
        "hotels": parse_hotel_result(hotel_result),
        "car_rentals": parse_car_rental_result(car_rental_result),
        "attractions": parse_attraction_result(attraction_result)
    }
    print(form_data)
    session['form_data'] = form_data
    return redirect(url_for('service_selection'))

@app.route('/service_selection')
def service_selection():
    # form_data = request.args.get('form_data')
    form_data = session.get('form_data', {})
    print("--------------------------form_data--------------------------")
    print(form_data)
    return render_template('service_selection.html', form_data=form_data)

@app.route('/submit_travel_plan', methods=['POST'])
def submit_travel_plan():
    data = request.get_json()
    print("Received travel plan data:", data)
    # 失败码: 500：服务器错误 501：请求还没有被实现 502：网关错误 503：服务暂时不可用 505：请求的 HTTP 版本不支持。
    return jsonify({"message": "Travel plan received successfully"}), 200

if __name__ == '__main__':
    # app.run(port=2023)
    app.run(debug = True, host='0.0.0.0', port=2023)
