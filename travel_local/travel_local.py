#travel_local.py
from flask import Flask, redirect, url_for, request, render_template, session, jsonify, flash
import pymysql
import requests
import json
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'development key'

@app.route('/')
def index():
    response = requests.post("http://10.46.199.36:9527/init", timeout=10)
    response.raise_for_status()

    return render_template("login.html") # 渲染登录界面 login.html

# 登录 (Login)
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")  # 渲染登录表单
    
    # 获取前端表单信息
    name = request.form.get("nm")
    password = request.form.get("pd")
    user_type = request.form.get("type")

    # 调用 travel_service.py 的 /internal_login 接口
    headers = {'Content-Type': 'application/json'}
    datajson = json.dumps({"name": name, "password": password, "user_type": user_type})
    try:
        # 向 service 端发出 post 请求，并将 pyload 传递出去
        response = requests.post( # 向service对应接口发起POST
            url="http://10.46.199.36:9527/internal_login", data=datajson, headers=headers, timeout=10
        )
        result = response.text
    except Exception as e:
        # 连接到service失败，返回错误信息
        print(f"Error connecting to service: {e}")
        flash('无法连接到认证服务，请稍后再试。', 'login_error')
        return redirect(url_for('login'))
    
    if result == "用户不存在": # 用户不存在
        flash('用户不存在！', 'login_error')
        return redirect(url_for('login'))
    elif result == "密码正确":
        # 密码正确，判断用户类型
        session["name"] = name
        if name == "admin":
            return redirect(url_for('admin_dashboard')) # 渲染管理员后台 admin_dashboard
        elif user_type == "航空公司":
            return redirect(url_for('submit_Flight')) # 渲染航线管理页面
        elif user_type == "酒店":
            return redirect(url_for('submit_Hotel')) # 渲染酒店公司服务管理页面
        elif user_type == "旅游景点":
            return redirect(url_for('submit_Attraction')) # 渲染景点服务管理页面
        elif user_type == "租车公司":
            return redirect(url_for('submit_Rental')) # 渲染租车公司服务管理页面
        else:
            return redirect(url_for('get_services')) # 渲染个人用户管理页面

    elif result == "密码错误": # 密码错误
        flash('密码错误！', 'login_error')
        return redirect(url_for('login'))
    else:
        # 未知错误报错
        flash('未知错误，请联系管理员。', 'login_error')
        return redirect(url_for('login'))

# 注册 (Register)
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("login.html")  # 渲染登录/注册表单
    
    # 获取前端表单信息
    name = request.form.get("nm_regiter")
    password = request.form.get("pd_regiter")
    user_type = request.form.get("type_regiter")

    headers = {'Content-Type': 'application/json'}
    datajson = json.dumps({"name": name, "password": password, "user_type": user_type})
    try:
        # 向 service 端发出 post 请求，并将 pyload 传递出去
        response = requests.post(
            url="http://10.46.199.36:9527/internal_register", data=datajson, headers=headers, timeout=10
        )
        result = response.text
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error connecting to register service: {e}")
        flash('无法连接到注册服务，请稍后再试。', 'register_error')
        return redirect(url_for('login'))
    
    if result == "用户已存在":
        flash('用户已存在！', 'register_error')
        return redirect(url_for('login'))
    else:
        # 注册成功，返回成功信息。
        flash('注册成功，请登录。', 'register_success')
        return redirect(url_for('login'))

# 提交景点信息
@app.route('/submit_Attraction')
def submit_Attraction():
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "company_name": (session.get("name"))
    }
    # 根据 company_name 获取 company_id。
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']

    # 将传递的参数打包成一个json
    payload = {
        "company_id": company_id
    }

    try:
        # 向 service 端发出 get 请求，并将 pyload 传递出去
        response = requests.get("http://10.46.199.36:9527/internal_query_all_Attraction_by_CompanyId", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error fetching data from service: {e}")
        flash("无法连接到数据服务，请稍后再试。", "error")
        data = {"flights":[]}
    
    # attractions 用来存储景点信息
    attractions = []
    for a in data.get("data", []):
        # 原SQL查询Hotel表的列顺序: hotel_id, hotel_name, city, rating, company_id
        attractions.append((
            a.get("attraction_id", ""),
            a.get("attraction_name", ""),
            a.get("city", ""),
            a.get("price", ""),
            a.get("rating", ""),
            a.get("company_id", "")
        ))

    return render_template('service_submit_Attraction.html', users = users, attractions = attractions)

@app.route('/submit_Rental')
def submit_Rental():
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "company_name": (session.get("name"))
    }
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']
    payload = {
        "company_id": company_id
    }

    # 调用service接口，如果调用失败，则返回错误信息
    try:
        response = requests.get("http://10.46.199.36:9527/internal_query_all_Rental_by_CompanyId", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error fetching data from service: {e}")
        flash("无法连接到数据服务，请稍后再试。", "error")
        data = {"rentals":[]}

    # rentals 用来存储租车信息
    rentals = []
    for r in data.get("data", []):
        # 原SQL查询Hotel表的列顺序: hotel_id, hotel_name, city, rating, company_id
        rentals.append((
            r.get("car_type", ""),
            r.get("transmission_type", ""),
            r.get("rental_location", ""),
            r.get("return_location", ""),
            r.get("price", ""),
            r.get("rating", ""),
            r.get("company_id", "")
        ))

    return render_template('service_submit_Rental.html', users = users, rentals = rentals) # 渲染页面 service_submit_Rental

@app.route('/submit_Hotel')
def submit_Hotel():
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "company_name": (session.get("name"))
    }

    # 向 service 端发出 post 请求，并将 pyload 传递出去
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']

    # 将传递的参数打包成一个json
    payload = {
        "company_id": company_id
    }

    try:
        # 向 service 端发出 get 请求，并将 pyload 传递出去
        response = requests.get("http://10.46.199.36:9527/internal_query_all_Hotel_by_CompanyId", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error fetching data from service: {e}")
        flash("无法连接到数据服务，请稍后再试。", "error")
        data = {"flights":[]}

    # hotels 用来存储酒店信息
    hotels = []
    for h in data.get("data", []):
        # 原SQL查询Hotel表的列顺序: hotel_id, hotel_name, city, rating, company_id
        hotels.append((
            h.get("hotel_id", ""),
            h.get("hotel_name", ""),
            h.get("city", ""),
            h.get("rating", "")
        ))
    return render_template('service_submit_Hotel.html', users = users, hotels = hotels) # 渲染页面 service_submit_Hotel

# 更新酒店信息
@app.route('/update_hotel', methods=['POST', 'GET'])
def update_hotel():
    
    # 获取前端表单信息
    hotel_id = request.form.get('hotel_id')
    company_id = request.form.get('company_id')
    hotel_name = request.form.get('hotel_name')
    city = request.form.get('city')
    rating = request.form.get('rating')

    # 将传递的参数打包成一个 json
    payload = {
        "hotel_id": hotel_id,
        "company_id": company_id,
        "hotel_name": hotel_name,
        "city": city,
        "rating": rating
    }
    try:
        # 向 service 端发出 post 请求，并将 pyload 传递出去
        response = requests.post("http://10.46.199.36:9527/internal_update_hotel", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("更改成功！", "success")
        else:
            flash("更改失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("更改失败,请检查", "error")

    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 删除指定酒店
@app.route('/delete_hotel', methods=['POST', 'GET'])
def delete_hotel():
    # 获取前端表单信息
    hotel_id = request.form.get('hotel_id')

    # 将传递的参数打包成一个json
    payload = {
        "hotel_id": hotel_id
    }
    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_hotel", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("删除成功！", "success")
        else:
            flash("删除失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败,请检查", "error")

    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 删除制定酒店信息
@app.route('/delete_hotel_info', methods=['POST', 'GET'])
def delete_hotel_info():

    # 获取前端表单信息
    hotel_id = request.form.get('hotel_id')

    # 将传递的参数打包成一个json
    payload = {
        "hotel_id": hotel_id
    }
    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_hotel", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("删除成功！", "success")
        else:
            flash("删除失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败,请检查", "error")

    return redirect(url_for('submit_Hotel')) # 重定向到 submit_Hotel

# 添加酒店信息
@app.route("/add_hotel", methods=['POST', 'GET'])
def add_hotel():

    # 获取前端表单信息
    company_id = request.form.get('hotel_id')
    company_name = request.form.get('hotel_name')
    city = request.form.get('city')
    rating = request.form.get('rating')

    # 将传递的参数打包成一个json
    payload = {
        "company_id": company_id,
        "hotel_name": company_name,
        "city": city,
        "rating": rating
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_hotel", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            flash("添加失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败,请检查", "error")
    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 提交酒店信息
@app.route('/submit_Hotel_info', methods=['POST', 'GET'])
def submit_Hotel_info():

    # 获取前端表单信息
    hotel_name = request.form.get('hotel_name')
    city = request.form.get('city')
    rating = 0
    
    # 先根据 company_name 获取 company_id
    payload = {
        "company_name": (session.get("name"))
    }
    # 向service端发出post请求，并将pyload传递出去
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']
    
    # 将传递的参数打包成一个json
    payload = {
        "hotel_name": hotel_name,
        "city": city,
        "rating": rating,
        "company_id": company_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_hotel", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            flash("添加失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败,请检查", "error")
    
    return redirect(url_for('submit_Hotel')) # 重定向到 submit_Hotel

# 添加航班信息
@app.route('/submit_Flight')
def submit_Flight():
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "company_name": (session.get("name"))
    }

    # 向service端发出post请求，并将pyload传递出去
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']

    # 将传递的参数打包成一个json
    payload = {
        "company_id": company_id
    }
    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.get("http://10.46.199.36:9527/internal_query_all_FlightInfo_by_CompanyId", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error fetching data from service: {e}")
        flash("无法连接到数据服务，请稍后再试。", "error")
        data = {"flights":[]}
    
    # flights 用来存储航班信息
    flights = []
    for h in data.get("data", []):
        # 原SQL查询Hotel表的列顺序: hotel_id, hotel_name, city, rating, company_id
        flights.append((
            h.get("flight_id", ""),
            h.get("departure_city", ""),
            h.get("arrival_city", ""),
            h.get("departure_time", ""),
            h.get("price", "")
        ))

    return render_template('service_submit_Flight.html', users = users, flights = flights) # 渲染 service_submit_Flight 页面

# 添加航班信息
@app.route('/submit_flight_info', methods = ['POST', 'GET'])
def submit_flight_info():

    # 获取前端表单信息
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_time = request.form.get('departure_time')
    price = request.form.get('price')
    rating = 0
    company_id = 1

    # 将传递的参数打包成一个json
    payload = {
        "company_name": (session.get("name"))
    }

    # 向service端发出post请求，并将pyload传递出去
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_company", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    company_id = resp_data.get("id")[0]['company_id']

    # 将传播的参数打包成一个json
    payload = {
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_time": departure_time,
        "price": price,
        "rating": rating,
        "company_id": company_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_flight", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            flash("添加失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败,请检查", "error")

    return redirect(url_for('submit_Flight')) # 重定向到 submit_Flight

# 删除航班信息
@app.route('/delete_flight_info', methods=['POST', 'GET'])
def delete_flight_info():

    # 获取前端表单信息
    flight_id = request.form.get('flight_id')

    # 将传递的信息打包为 json
    payload = {
        "flight_id": flight_id
    }
    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_flight", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            # 删除失败，返回错误信息
            flash("删除成功！", "success")
        else:
            flash("删除失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败,请检查", "error")

    return redirect(url_for('submit_Flight')) # 重定向到 submit_Flight

# 跳转管理员后台
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get("name") != "admin":
        return redirect(url_for('login'))  # 非管理员用户重定向到登录页面

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_get_all_services", timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error fetching data from service: {e}")
        flash("无法连接到数据服务，请稍后再试。", "error")
        data = {"users":[], "tickets": [], "hotels": [], "car_rentals": [], "attractions": []}

    # 用户信息
    users = []

    # 遍历传回的数据并添加进入 users
    for u in data.get("users", []):
        users.append((
            u.get("user_id", ""),
            u.get("user_name", ""),
            u.get("password", ""),
            u.get("user_role", "")
        ))

    # 企业信息
    companies = []

    # 遍历传回的数据并添加进入 companies
    for cc in data.get("companies", []):
        companies.append((
            cc.get("company_id", ""),
            cc.get("company_name", ""),
            cc.get("company_type", ""),
            cc.get("password", "")
        ))

    # 将API返回的数据转换为与原SQL查询结果相同的结构（列表的元组）
    tickets = []

    # 遍历传回的数据并添加进入 tickets
    for t in data.get("tickets", []):
        # 原SQL查询FlightInfo表的列顺序: flight_id, departure_city, arrival_city, departure_time, price, rating
        tickets.append((
            t.get("flight_id", ""),
            t.get("departure_city", ""),
            t.get("arrival_city", ""),
            t.get("departure_time", ""),
            t.get("price", ""),
            t.get("rating", ""),
            t.get("company_id", "")
        ))

    # 酒店信息
    hotels = []

    # 遍历传回的数据并添加进入 hotels
    for h in data.get("hotels", []):
        hotels.append((
            h.get("hotel_id", ""),
            h.get("hotel_name", ""),
            h.get("city", ""),
            h.get("rating", ""),
            h.get("company_id", "")
        ))
    
    # 租车信息
    car_rentals = []

    # 遍历传回的数据并添加进入 car_rentals
    for c in data.get("car_rentals", []):
        car_rentals.append((
            c.get("carrental_id", ""),
            c.get("car_type", ""),
            c.get("transmission_type", ""),
            c.get("rental_location", ""),
            c.get("return_location", ""),
            c.get("price", ""),
            c.get("rating", ""),
            c.get("company_id", "")
        ))
    
    # 景点信息
    attractions = []

    # 遍历传回的数据并添加进入 attractions
    for a in data.get("attractions", []):
        attractions.append((
            a.get("attraction_id", ""),
            a.get("attraction_name", ""),
            a.get("city", ""),
            a.get("price", ""),
            a.get("rating", ""),
            a.get("company_id", "")
        ))

    orders = []

    return render_template('admin_dashboard.html', users = users, companies = companies, tickets = tickets, hotels = hotels, car_rentals = car_rentals, attractions = attractions, orders = orders) # 渲染 admin_dashboard 页面

# 更新公司信息
@app.route('/update_company',  methods = ['POST', 'GET'])
def update_company():

    # 获取前端表单信息
    company_name = request.form.get('company_name')
    company_type = request.form.get("company_type")

    # 根据公司类型更改 company_type
    if company_type == "航空公司":
        company_type = "Flight"
    elif company_type == "酒店":
        company_type = "Hotel"
    elif company_type == "租车公司":
        company_type = "Rental"
    else:
        company_type = "Attraction"
    
    # 将传递的参数打包成一个json
    payload = {
        "company_name": company_name,
        "company_type": company_type
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_update_company", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("更改成功！", "success")
        else:
            # 更改失败，返回错误信息
            flash("更改失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("更改失败，请检查", "error")

    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 修改 user 权限
@app.route('/update_user', methods=['POST', 'GET'])
def update_user():

    # 获取前端表单信息
    user_name = request.form.get('update_user_nm')
    user_role = request.form.get("user_role")

    if user_role == "管理员":
        user_role = "admin"
    else:
        user_role = "user"
    
    # 将传递的参数打包成一个json
    payload = {
        "user_name": user_name,
        "user_role": user_role
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_update_user", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("更改成功！", "success")
        else:
            # 更改失败，返回错误信息
            flash("更改失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("更改失败，请检查", "error")

    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 添加 企业
@app.route('/add_company', methods=['POST'])
def add_company():

    # 获取前端表单信息
    company_name = request.form.get('company_nm')
    password = request.form.get('company_pd')
    company_type = request.form.get('company_type')

    # 根据公司类型更改 company_type
    if company_type == "航空公司":
        company_type = "Flight"
    elif company_type == "酒店":
        company_type = "Hotel"
    elif company_type == "租车公司":
        company_type = "Rental"
    else:
        company_type = "Attraction"
    
    # 将传递的参数打包成一个json
    payload = {
        "company_name": company_name,
        "password": password,
        "company_type": company_type
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_company", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            # 添加失败，返回错误信息
            flash("添加失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败，请检查", "error")

    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 添加 User
@app.route('/add_user', methods=['POST'])
def add_user():

    # 获取前端表单信息
    user_name = request.form.get('nm')
    pass_word = request.form.get("pd")
    user_role = request.form.get("user_role")
    
    # 判断用户类型
    if user_role == "管理员":
        user_role = "admin"
    else:
        user_role = "user"
    
    # 将传递的参数打包成一个jason
    payload = {
        "user_name": user_name,
        "pass_word": pass_word,
        "user_role": user_role
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_user", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            # 添加失败，返回错误信息
            flash("添加失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败，请检查", "error")

    return redirect(url_for('admin_dashboard')) # 添加用户后，重定向到 admin_dashboard

#删除企业
@app.route('/delete_company', methods=['POST'])
def delete_company():

    # 获取前端表单信息
    user_name = request.form.get('company_delete_nm')

    # 将传递的参数打包成一个json
    payload = {"company_name": user_name}

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_company", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("删除成功！", "success")
        else:
            flash("删除失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败，请检查", "error")
    return redirect(url_for('admin_dashboard'))

# 删除用户
@app.route('/delete_user', methods=['POST'])
def delete_user():

    # 获取前端表单信息
    user_name = request.form.get('name_delete')

    # 将传递的参数打包成一个json
    payload = {"user_name": user_name}

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_user", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("删除成功！", "success")
        else:
            flash("删除失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败，请检查", "error")
    return redirect(url_for('admin_dashboard')) # 删除用户后，重定向到 admin_dashboard

# 添加 Ticket
@app.route('/add_ticket', methods=['POST'])
def add_ticket():

    # 获取前端表单信息
    flight_id = request.form.get('flight_id')
    departure_city = request.form.get('departure_city')
    arrival_city = request.form.get('arrival_city')
    departure_time = request.form.get('departure_time')
    price = request.form.get('price')
    rating = request.form.get('rating')
    company_id = 1

    # 将传递的参数打包成一个json
    payload = {
        "flight_id": flight_id,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_time": departure_time,
        "price": price,
        "rating": rating,
        "company_id": company_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_add_ticket", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("添加成功！", "success")
        else:
            # 添加失败，返回失败信息
            flash("添加失败，请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("添加失败，请检查", "error")
    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 删除 Ticket
@app.route('/delete_ticket', methods=['POST'])
def delete_ticket():
    
    # 获取前端表单信息
    flight_id = request.form.get('ticket_id')

    # 将传递的参数打包成一个json
    payload = {"flight_id": flight_id}
    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_delete_ticket", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            flash("删除成功！", "success")
        else:
            flash("删除失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("删除失败,请检查", "error")
    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 更新 Ticket
@app.route('/update_ticket', methods=['POST'])
def update_ticket():

    # 获取前端表单信息
    flight_id = request.form.get('flight_id')
    new_departure_city = request.form.get('departure_city')
    new_arrival_city = request.form.get('arrival_city')
    new_departure_time = request.form.get('departure_time')
    new_price = request.form.get('price')
    new_rating = request.form.get('rating')
    company_id = 1

    # 将传递的参数打包成一个json
    payload = {
        "flight_id": flight_id,
        "departure_city": new_departure_city,
        "arrival_city": new_arrival_city,
        "departure_time": new_departure_time,
        "price": new_price,
        "rating": new_rating,
        "company_id": company_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_update_ticket", json=payload, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        if resp_data.get("success"):
            # 更新成功，返回信息
            flash("更新成功！", "success")
        else:
            flash("更新失败,请检查", "error")
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Request error: {e}")
        flash("更新失败,请检查", "error")
    return redirect(url_for('admin_dashboard')) # 重定向到 admin_dashboard

# 获取服务 (Get Services)
@app.route('/get_services', methods=['POST', 'GET'])
def get_services():
    name = session.get("name")
    if not name:
        return redirect(url_for('login')) # 重定向到 login
    return render_template("service_submit.html", name=name) # 渲染 service_submit 界面

# 提交订单
@app.route('/submit_order2', methods=['POST', 'GET'])
def submit_order2():

    # 获取用户名称
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "user_name": (session.get("user_id"))
    }

    # 根据 user_name 获取 company_id。
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_user", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    user_id = resp_data.get("id")[0]['user_id']

    data = request.get_json()

    # 获取前端表单信息
    flight_id = request.form.get("flight_id")
    hotel_id = request.form.get("hotel_id")
    carrental_id = request.form.get("carrental_id")
    attraction_id = request.form.get("attraction_id")
    
    # 如果没有填写 id 则设置传递参数为 -1
    if flight_id == None:
        flight_id = -1
    if hotel_id == None:
        hotel_id = -1
    if carrental_id == None:
        carrental_id = -1
    if attraction_id == None:
        attraction_id = -1
    
    # 将传递的参数打包成一个json
    payload = {
        "user_id": user_id,
        "flight_id": flight_id,
        "hotel_id": hotel_id,
        "carrental_id": carrental_id,
        "attraction_id": attraction_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_submit_order", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        session['form_data'] = data
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error: {e}")
        return jsonify({"success": False})
    return jsonify({"success": True})

# 获取服务 (Get Services)
@app.route('/submit_order', methods=['POST', 'GET'])
def submit_order():
    users = []
    users.append((session.get("name")))

    # 将传递的参数打包成一个json
    payload = {
        "user_name": (session.get("name"))
    }

    # 根据 user_name 获取 user_id
    response = requests.post("http://10.46.199.36:9527/get_id_by_name_user", json=payload, timeout=10)
    response.raise_for_status()
    resp_data = response.json()
    user_id = resp_data.get("id")[0]['user_id']

    data = request.get_json()

    flight_id = data["flight_id"]
    hotel_id = data["hotel_id"]
    carrental_id = data["carrental_id"]
    attraction_id = data["attraction_id"]
    
    # 如果没有填写 id 则设置传递参数为 -1
    if flight_id == None:
        flight_id = -1
    if hotel_id == None:
        hotel_id = -1
    if carrental_id == None:
        carrental_id = -1
    if attraction_id == None:
        attraction_id = -1

    # 将传递的参数打包成一个json
    payload = {
        "user_id": user_id,
        "flight_id": flight_id,
        "hotel_id": hotel_id,
        "carrental_id": carrental_id,
        "attraction_id": attraction_id
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_submit_order", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        session['form_data'] = data
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error: {e}")
        return jsonify({"success": False})
    return jsonify({"success": True})

# 提交旅游信息 (Submit Travel Info)
@app.route('/submit_travel_info', methods=['POST'])
def submit_travel_info():
    
    # 获取前端表单信息
    departure_date = request.form.get("departure_date")
    departure_city = request.form.get("departure_city")
    arrival_city = request.form.get("arrival_city")
    need_car = request.form.get("need_car")
    
    # 车型和档位型号
    car_type = request.form.get("car_type") if need_car == "yes" else None
    gear_type = request.form.get("gear_type") if need_car == "yes" else None
    guide = request.form.get("guide")
    preference = request.form.get("preference")
    
    # 倾向限制
    prefernce_flight = request.form.get("prefernce_flight")
    prefernce_hotel = request.form.get("prefernce_hotel")
    prefernce_carrental = request.form.get("prefernce_carrental")
    prefernce_attraction = request.form.get("prefernce_attraction")
    
    # 将传递的参数打包成一个json
    payload = {
        "departure_date": departure_date,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "need_car": need_car,
        "car_type": car_type,
        "gear_type": gear_type,
        "guide": guide,
        "preference": preference,

        # 倾向限制
        "prefernce_flight": prefernce_flight,
        "prefernce_hotel": prefernce_hotel,
        "prefernce_carrental": prefernce_carrental,
        "prefernce_attraction": prefernce_attraction
    }

    try:
        # 向service端发出post请求，并将pyload传递出去
        response = requests.post("http://10.46.199.36:9527/internal_submit_travel_info", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        session['form_data'] = data
        return redirect(url_for('service_selection')) # 重定向到 service_selection
    except Exception as e:
        # 连接失败，返回错误信息
        print(f"Error: {e}")

    return jsonify({"error": "Failed to process request"}), 500

# 渲染 service_selection
@app.route('/service_selection')
def service_selection():
    form_data = session.get('form_data', {})
    return render_template('service_selection.html', form_data=form_data) # 渲染 service_selection 页面

# 提交航班信息
@app.route('/submit_travel_plan', methods=['POST'])
def submit_travel_plan():
    data = request.get_json()
    print("Received travel plan data:", data)
    return jsonify({"message": "Travel plan received successfully"}), 200

# 显示“评分页面”
@app.route('/rate_services', methods=['POST', 'GET'])
def rate_services():
    return render_template('rate_services.html') # 渲染rate_services页面

# 接收评分表单
@app.route('/rate_entity', methods=['POST'])
def rate_entity():
    body = request.get_json()

    # 获取前端元素值
    entity_type = body.get("entity_type")
    entity_id = body.get("entity_id")
    rating = body.get("rating")

    if not entity_type or not entity_id or not rating:
        # 返回错误信息 json
        return jsonify({"success": False, "message": "缺少必要字段"})

    # 这里再把 rating 转成浮点或整型
    try:
        rating_val = float(rating)
    except:
        # 返回错误信息 json
        return jsonify({"success": False, "message": "评分格式不正确"})

    # 将评分插入到 UserRating 表
    # 也可通过调用 service 后端 /internal_add_user_rating
    # 这里示例直接执行SQL:
    conn = pymysql.connect(host='10.47.79.97', port=3306, user='root', password='12345678', db='travelagency')
    try:
        # 连接数据库并执行 sql 语句
        with conn.cursor() as cursor:
            insert_sql = """INSERT INTO UserRating (entity_type, entity_id, rating)
                            VALUES (%s, %s, %s)"""
            cursor.execute(insert_sql, (entity_type, entity_id, rating_val))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        # 连接失败，返回错误信息
        print("rate_entity error:", e)
        return jsonify({"success": False, "message": str(e)})
    finally:
        # 断开数据库连接
        conn.close()

# 连接数据库
def get_db_conn():
    return pymysql.connect(host='10.47.79.97', port=3306, user='root', password='12345678', db='travelagency')

@app.route('/fetch_entities', methods=['GET'])
def fetch_entities():
    entity_type = request.args.get('entity_type', '')

    # 根据 entity_type 查询不同表的数据
    # 并返回前端可显示的 { id, name } 列表
    if entity_type == 'FlightInfo':
        # 查询航班
        sql = """SELECT flight_id AS id, 
                        CONCAT('航班ID:', flight_id, ' ', departure_city, '->', arrival_city) AS name
                 FROM FlightInfo"""
    elif entity_type == 'Hotel':
        # 查询酒店
        sql = """SELECT hotel_id AS id,
                        CONCAT('酒店ID:', hotel_id, ' ', hotel_name, ' (', city, ')') AS name
                 FROM Hotel"""
    elif entity_type == 'CarRental':
        # 查询租车
        sql = """SELECT carrental_id AS id,
                        CONCAT('租车ID:', carrental_id, ' ', car_type, ' [', transmission_type, ']') AS name
                 FROM CarRental"""
    elif entity_type == 'Attraction':
        # 查询景点
        sql = """SELECT attraction_id AS id,
                        CONCAT('景点ID:', attraction_id, ' ', attraction_name, ' (', city, ')') AS name
                 FROM Attraction"""
    elif entity_type == 'Guide':
        # 查询导游
        sql = """SELECT guide_id AS id,
                        CONCAT('导游ID:', guide_id, ' ', guide_name, ' [Phone:', guide_phone, ']') AS name
                 FROM Guide"""
    else:
        # 返回错误信息 json
        return jsonify({"success": False, "data": []})
    
    conn = get_db_conn()
    try:
        # 连接数据库并执行 sql 语句
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        result_list = []
        for row in rows:
            result_list.append({"id": row["id"], "name": row["name"]})
        return jsonify({"success": True, "data": result_list})
    except Exception as e:
        # 连接数据库失败，返回错误信息
        return jsonify({"success": False, "data": []})
    finally:
        # 关闭数据库连接
        conn.close()


# 启动 Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4396)