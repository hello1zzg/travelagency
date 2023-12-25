from decimal import Decimal
from flask import Flask, Response, redirect, url_for, request, render_template,jsonify
import pymysql
from urllib import request as rq
import json ,time, math
import pandas as pd
from datetime import date
    
app = Flask(__name__)

# login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    datajsonstr = request.get_data()
    input = json.loads(datajsonstr)
    name = input["name"]
    password = input["password"]
    # print(name, password)

    print(datajsonstr)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    sql1 = "SELECT user_id, password FROM User WHERE user_name = '%s'"%(name)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql1)
            User_data = cursor.fetchone()
            print(User_data)
    except Exception as e:
        print(e)

    mysql_conn.close()

    if User_data == None:
        return "用户不存在"
    elif password == User_data[1]:
        # if name == 'bankadmin1' or name == 'bankadmin2' or name == 'bankadmin3':
        #     # session["bankadmin"] = name
        #     return redirect(url_for('bank_manual_judge'))
        # elif name == 'fundadmin':
        #     return redirect(url_for('fund_manual_judge'))
        # session["userId"] = User_data[0]
        # session['name'] = name
        return "密码正确"
    else:
        return "密码错误"


# datatime转换为json
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# ticket query
@app.route('/ticket_query', methods = ['POST', 'GET'])
def ticket_query():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)

    departure_city = input["departure_city"]
    arrival_city = input["arrival_city"]
    departure_time = input["departure_date"]
    preference = input["preference"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')
    if preference == "price" :
        sql = "select flight_id, departure_city, arrival_city, departure_time, price, company_name from FlightInfo, Company where FlightInfo.company_id = Company.company_id and departure_city = '%s' and arrival_city = '%s' and departure_time = '%s' order by price"%(departure_city, arrival_city, departure_time)
    else:
        sql = "select flight_id, departure_city, arrival_city, departure_time, price, company_name from FlightInfo, Company where FlightInfo.company_id = Company.company_id and departure_city = '%s' and arrival_city = '%s' and departure_time = '%s' order by rating desc"%(departure_city, arrival_city, departure_time)

    print(sql)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            User_data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = {}
            print(columns)
            i = 0
            for row in User_data:
                label = "ticket" + str(i)
                i = i + 1
                result[label] = dict(zip(columns, row)) 
            # return json.dumps(result, cls=DateEncoder, ensure_ascii=False)
            # 使用 json.dumps 和 Response 来禁用 ASCII 转义
            json_data = json.dumps({"data": result}, cls=DateEncoder, ensure_ascii=False)
            # print(json_string)
            # json_data = json.dumps({"data": json_string}, cls=DateEncoder, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')
    except Exception as e:
        print(e)
    mysql_conn.close()
        

# hotel query
@app.route('/hotel_query', methods = ['POST', 'GET'])
def hotel_query():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    arrival_city = input["arrival_city"]
    preference = input["preference"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')
    if preference == "price" :
        sql = "select room_id, room_number, room_type, room_price, rating, hotel_name from Hotel, RoomInfo where Hotel.hotel_id = RoomInfo.hotel_id and city = '%s' order by price"%(arrival_city)
    else:
        sql = "select room_id, room_number, room_type, room_price, rating, hotel_name from Hotel, RoomInfo where Hotel.hotel_id = RoomInfo.hotel_id and city = '%s' order by rating desc"%(arrival_city)

    # print(sql)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            User_data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = {}
            print(columns)
            i = 0
            for row in User_data:
                label = "room" + str(i)
                i = i + 1
                result[label] = dict(zip(columns, row))
                # result.append(dict(zip(columns, row)))
                # 使用 json.dumps 和 Response 来禁用 ASCII 转义
            json_data = json.dumps({"data": result}, cls=DateEncoder, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')
            # return json.dumps(result, cls=DateEncoder, ensure_ascii=False)
    except Exception as e:
        print(e)
    mysql_conn.close()

# car_rental query
@app.route('/car_rental_query', methods = ['POST', 'GET'])
def car_rental_query():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    need_car = input["need_car"]
    car_type = input["car_type"]
    gear_type = input["gear_type"]
    arrival_city = input["arrival_city"]
    preference = input["preference"]
    if need_car != "no":
        mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')
        if preference == "price" :
            sql = "select carrental_id, car_type, transmission_type, rental_location, return_location, price, rating, company_name from CarRental, Company where CarRental.company_id = Company.company_id and car_type = '%s' and transmission_type = '%s' and rental_location = '%s' and return_location = '%s' order by price"%(car_type, gear_type, arrival_city, arrival_city)
        else:
            sql = "select carrental_id, car_type, transmission_type, rental_location, return_location, price, rating, company_name from CarRental, Company where CarRental.company_id = Company.company_id and car_type = '%s' and transmission_type = '%s' and rental_location = '%s' and return_location = '%s' order by rating desc"%(car_type, gear_type, arrival_city, arrival_city)
        print(sql)
        try:
            with mysql_conn.cursor() as cursor:
                cursor.execute(sql)
                User_data = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                result = {}
                print(columns)
                i = 0
                for row in User_data:
                    label = "car" + str(i)
                    i = i + 1
                    result[label] = dict(zip(columns, row))
                    # result.append(dict(zip(columns, row)))
                # return json.dumps(result, cls=DateEncoder, ensure_ascii=False)
                json_data = json.dumps({"data": result}, cls=DateEncoder, ensure_ascii=False)
                return Response(json_data, mimetype='application/json')
        except Exception as e:
            print(e)
        mysql_conn.close()
    else:
        return []

# car_rental query
@app.route('/attraction_query', methods = ['POST', 'GET'])
def attraction_query():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    arrival_city = input["arrival_city"]
    preference = input["preference"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')
    if preference == "price" :
        sql = "select attraction_id, attraction_name, city, price, rating from Attraction where city = '%s' order by price"%(arrival_city)
    else:
        sql = "select attraction_id, attraction_name, city, price, rating from Attraction where city = '%s' order by rating desc"%(arrival_city)
    print(sql)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            User_data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = {}
            print(columns)
            i = 0
            for row in User_data:
                label = "attraction" + str(i)
                i = i + 1
                result[label] = dict(zip(columns, row))
                # result.append(dict(zip(columns, row)))
            json_data = json.dumps({"data": result}, cls=DateEncoder, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')
            # return json.dumps(result, cls=DateEncoder, ensure_ascii=False)
    except Exception as e:
        print(e)
    mysql_conn.close()

@app.route('/guide_query', methods = ['POST', 'GET'])
def guide_query():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    arrival_city = input["arrival_city"]
    preference = input["preference"]
    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')
    if preference == "price" :
        sql = "select attraction_id, attraction_name, city, price, rating from Attraction where city = '%s' order by price"%(arrival_city)
    else:
        sql = "select attraction_id, attraction_name, city, price, rating from Attraction where city = '%s' order by rating desc"%(arrival_city)
    print(sql)
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            User_data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = []
            print(columns)
            for row in User_data:
                result.append(dict(zip(columns, row)))
            json_data = json.dumps({"data": result}, cls=DateEncoder, ensure_ascii=False)
            return Response(json_data, mimetype='application/json')
            # return json.dumps(result, cls=DateEncoder, ensure_ascii=False)
    except Exception as e:
        print(e)
    mysql_conn.close()

@app.route('/travel_recommend', methods = ['POST', 'GET'])
def travel_recommend():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    ticket_result = input["ticket_result"]
    hotel_result = input["hotel_result"]
    car_rental_result = input["car_rental_result"]
    attraction_result = input["attraction_result"]

    recommend_result = {}
    recommend_result["ticket_result"] = ticket_result
    recommend_result["hotel_result"] = hotel_result
    recommend_result["car_rental_result"] = car_rental_result
    recommend_result["attraction_result"] = attraction_result
    # recommend_result["hotel_result"] = hotel_result

    return json.dumps(recommend_result, ensure_ascii=False)


# 买飞机票
@app.route('/ticket_purchase', methods = ['POST', 'GET'])
def ticket_purchase():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    user_id = input["user_id"]
    flight_id = input["flight_id"]

    sql = "insert into ticket_purchase values (%s, %s)"%(user_id, flight_id)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    print(sql)
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql)
        mysql_conn.commit()
        # result = cursor.fetchone()
        # print(result)
    return jsonify({"message": "Travel plan received successfully"})

# 酒店预定
@app.route('/hotel_preserve', methods = ['POST', 'GET'])
def hotel_preserve():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    print(input)

    user_id = input["user_id"]
    hotel_id = input["hotel_id"]
    room_id = input["room_id"]

    sql = "insert into hotel_preserve values (%s, %s, %s)"%(user_id, hotel_id, room_id)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    print(sql)
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql)
        mysql_conn.commit()
        # result = cursor.fetchone()
        # print(result)
    return jsonify({"message": "Travel plan received successfully"})


# 车子预定
@app.route('/car_preserve', methods = ['POST', 'GET'])
def car_preserve():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    print(input)
    user_id = input["user_id"]
    carrental_id = input["carrental_id"]

    sql = "insert into car_preserve values (%s, %s)"%(user_id, carrental_id)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    print(sql)
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql)
        mysql_conn.commit()
        # result = cursor.fetchone()
        # print(result)
    return jsonify({"message": "Travel plan received successfully"})


# 景点预定
@app.route('/attraction_preserve', methods = ['POST', 'GET'])
def attraction_preserve():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    user_id = input["user_id"]
    attraction_id = input["attraction_id"]

    sql = "insert into attraction_preserve values (%s, %s)"%(user_id, attraction_id)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    print(sql)
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql)
        mysql_conn.commit()
        # result = cursor.fetchone()
        # print(result)
    return jsonify({"message": "Travel plan received successfully"})

# 导游预定
@app.route('/guide_preserve', methods = ['POST', 'GET'])
def guide_preserve():
    datajson = request.get_data()
    # print(datajson)
    input = json.loads(datajson)
    
    user_id = input["user_id"]
    guide_id = input["guide_id"]

    sql = "insert into guide_preserve values (%s, %s)"%(user_id, guide_id)

    mysql_conn = pymysql.connect(host= '127.0.0.1', port= 3306, user= 'ysm', password= 'yangshiming', db= 'ysm_tourism')

    print(sql)
    with mysql_conn.cursor() as cursor:
        cursor.execute(sql)
        mysql_conn.commit()
        # result = cursor.fetchone()
        # print(result)
    return jsonify({"message": "Travel plan received successfully"})