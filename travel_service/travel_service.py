#travel_service.py
from decimal import Decimal
from flask import Flask, Response, request, jsonify
# import pymysql
import json, time, math
from datetime import date
import requests
import subprocess
import json

# 调用API的参数
ip = "10.77.110.222"
port = 8999
if_path = "oids/testOid"
user = "anyone"

app = Flask(__name__)

def str_to_json(json_str):    
    """
    用于解析 BPMN 任务返回的字符串，提取其中的 'body' 字段并转换为 dict。
    """

    data = json.loads(json_str)

    body_str = data.get('body')

    if body_str:
        body_dict = json.loads(body_str)
        return body_dict
    else:
        print("没有找到 'body' 字段。")
        return None

# datatime 转换为 json
class DateEncoder(json.JSONEncoder):
    """
    解决 datetime、Decimal 等无法被默认 JSONEncoder 序列化的问题。
    """
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

@app.route('/register', methods=['POST', 'GET'])
def register_original():
    """
    注册接口，与数据库交互的逻辑已封装到 BPMN + HTTP 的方式。
    这里通过 BPMN 流程查询用户是否存在 -> 存在则返回“用户已存在” -> 否则插入。
    """
    datajsonstr = request.get_data()
    input = json.loads(datajsonstr)
    
    # 获取传递的参数
    name = input["name"]
    password = input["password"]
    user_type = input["user_type"]

    # 根据 user_type 不同，调用不同的查询 / 插入服务
    if user_type == "普通用户":
        user_type = "user"
        service_name_select = "select_user_3934"
        service_url_select = "/api/select_user_3934"
        service_name_add = "insert_user_3934"
        service_url_add = "/api/insert_user_3934"
        body_select = {"user_name": name}
        body_add = {"user_name": name, "password": password, "user_role": user_type}
    elif user_type in ["航空公司", "酒店", "租车公司", "旅游景点"]:
        type_mapping = {
            "航空公司": "Flight",
            "酒店": "Hotel",
            "租车公司": "Rental",
            "旅游景点": "Attraction"
        }
        user_type = type_mapping[user_type]
        service_name_select = "select_company_3934"
        service_url_select = "/api/select_company_3934"
        service_name_add = "insert_company_3934"
        service_url_add = "/api/insert_company_3934"
        body_select = {"company_name": name}
        body_add = {"company_name": name, "password": password, "company_type": user_type}
    else:
        return "无效的用户类型", 400

    # 设计POST请求的参数并通过POST请求获取数据库数据,下面的同样如此不再阐述
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 传递的参数打包成 json
    payload_select = {
        "s-consumerName": "A",
        "headers": {},
        "body": body_select,
        "s-serviceName": service_name_select,
        "s-group": "Service2024",
        "s-url": service_url_select,
        "s-method": "POST"
    }
    
    try:
        # 首先查询是否已存在
        response = requests.post(api_url, headers=headers, json=payload_select, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        data = response_data.get("data", [])

        if not isinstance(data, list):
            print(f"Unexpected data format: {data}")
            return "注册服务返回数据格式错误", 500  # Internal Server Error for unexpected data format

        if response_data.get("success") and len(data) > 0:
            return "用户已存在", 409  # 冲突

        # 执行插入 BPMN
        # 这里是区分 user or company 传入 pd / bd
        if user_type == "user":
            pd = {"choose": 2}
            bd = {"user_name": name, "password": password, "user_role": user_type}
        else:
            pd = {"choose": 1}
            bd = {"company_name": name, "password": password, "company_type": user_type}
        
        # 调用bpmn
        complete_command = [
            "python3", "tool.py", "bpmn", "complete",
            "-ip", ip,
            "-p", str(port),
            "-if", if_path,
            "-n", "register",
            "-pd", json.dumps(pd, ensure_ascii=False),
            "-bd", json.dumps(bd, ensure_ascii=False),
            "-u", user
        ]
        output = execute_command(complete_command)

        if output is not None:
            print("主要命令输出结果:")
            print(output)
            return "注册成功", 201
        else:
            print("主要命令执行失败。")
            return "注册失败", 500

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return "注册服务不可用", 503  # Service Unavailable
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "注册时发生错误", 500  # Internal Server Error


@app.route('/login', methods=['POST', 'GET'])
def login_original():
    """
    登录接口，与数据库交互的逻辑通过 BPMN 进行。
    当 user_type 为 “user” 时走查询用户分支，否则走查询公司分支。
    """
    datajsonstr = request.get_data() # 获取调用参数
    input = json.loads(datajsonstr)

    # 获取传递的参数
    name = input["name"]
    password = input["password"]
    user_type = input["user_type"]

    if user_type == "普通用户": # 查询用户类型
        user_type = "user"
    elif user_type in ["航空公司", "酒店", "租车公司", "旅游景点"]:
        type_mapping = {
            "航空公司": "Flight",
            "酒店": "Hotel",
            "租车公司": "Rental",
            "旅游景点": "Attraction"
        }
        user_type = type_mapping[user_type]
    else:
        return "无效的用户类型", 400  # 对于无效的用户类型返回400 Bad Request

    try:
        if user_type == "user": # 根据用户类型更改bpmn调用参数
            pd = {"login": 1}
            bd = {"user_name": name}
        else:
            pd = {"login": 2}
            bd = {"company_name": name}
        
         # 第一次 BPMN complete，用于从数据库中查询此用户
        complete_command = [
            "python3", "tool.py", "bpmn", "complete",
            "-ip", ip,
            "-p", str(port),
            "-if", if_path,
            "-n", "login",
            "-pd", json.dumps(pd, ensure_ascii=False),
            "-bd", json.dumps(bd, ensure_ascii=False),
            "-u", user
        ]
        output = execute_command(complete_command)

        data = str_to_json(output) # 将bpmn的返回值转换为json格式

        # 第二次 BPMN complete，根据用户类型走不同分支
        if user_type == "user":
            pd = {"usera": 1}
        else:
            pd = {"usera": 2}
        bd = {}
        complete_command = [
            "python3", "tool.py", "bpmn", "complete",
            "-ip", ip,
            "-p", str(port),
            "-if", if_path,
            "-n", "responseusercheck",
            "-pd", json.dumps(pd, ensure_ascii=False),
            "-bd", json.dumps(bd, ensure_ascii=False),
            "-u", user
        ]
        output = execute_command(complete_command)

        db_password = data['data'][0]['password']
        if not db_password:
            return "用户不存在", 404 # 用户不存在

        if password == db_password:
            return "密码正确", 200
        else:
            return "密码错误", 401  # 密码错误，未授权

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return "登录服务不可用", 503  # 登录服务不可用
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "登录时发生错误", 500  # 内部服务器错误

# 提供给 travel_local.py 的内部接口：登录
@app.route('/internal_login', methods=['POST'])
def internal_login():
    data = request.get_json()
    response = requests.post("http://localhost:9527/login", json=data)
    return response.text

@app.route('/internal_register', methods=['POST'])
def internal_register():
    data = request.get_json()
    response = requests.post("http://localhost:9527/register", json=data)
    return response.text

# 获取 Admin Dashboard 所需的所有数据
@app.route('/internal_get_all_services', methods=['POST'])
def internal_get_all_services():
    """
    返回所有用户、企业、航班、酒店、租车、景点等信息，用于管理员后台管理。
    这里统一调用 10.77.110.222:8999 提供的 microservice 接口查询。
    """
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    services = {
        "users": {
            "s-serviceName": "query_All_Users_3934",
            "s-url": "/api/query_All_Users_3934"
        },
        "companies": {
            "s-serviceName": "query_All_Companies_3934",
            "s-url": "/api/query_All_Companies_3934"
        },
        "tickets": {
            "s-serviceName": "query_all_FlightInfo_3934",
            "s-url": "/api/query_all_FlightInfo_3934"
        },
        "hotels": {
            "s-serviceName": "query_all_Hotel_3934",
            "s-url": "/api/query_all_Hotel_3934"
        },
        "car_rentals": {
            "s-serviceName": "query_all_CarRental_3934",
            "s-url": "/api/query_all_CarRental_3934"
        },
        "attractions": {
            "s-serviceName": "query_all_Attraction_3934",
            "s-url": "/api/query_all_Attraction_3934"
        }
    }

    data = {}

    # 调用不同的POST请求获取数据库信息
    for key, service in services.items():
        payload = {
            "s-consumerName": "A",
            "headers": {},
            "body": {},
            "s-serviceName": service["s-serviceName"],
            "s-group": "Service2024",
            "s-url": service["s-url"],
            "s-method": "POST"
        }
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("success"):
                data[key] = response_data.get("data", [])
            else:
                data[key] = []
        except:
            data[key] = []

    return jsonify(data)

@app.route('/internal_query_all_Attraction_by_CompanyId', methods=['GET'])
def internal_query_all_Attraction_by_CompanyId():
    """
    按企业ID查询景点信息。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    
    # 传递的参数打包成 json
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_id": str(data["company_id"])
        },
        "s-serviceName": "query_all_Attractions_by_CompanyId_3934",
        "s-group": "Service2024",
        "s-url": "/api/query_all_Attractions_by_CompanyId_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"data": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_query_all_Rental_by_CompanyId', methods=['GET'])
def internal_query_all_Rental_by_CompanyId():
    """
    按企业ID查询租车信息。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_id": str(data["company_id"])
        },
        "s-serviceName": "query_all_Rental_by_CompanyId_3934",
        "s-group": "Service2024",
        "s-url": "/api/query_all_Rental_by_CompanyId_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"data": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_query_all_Hotel_by_CompanyId', methods=['GET'])
def internal_query_all_Hotel_by_CompanyId():
    """
    按企业ID查询酒店信息。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_id": str(data["company_id"])
        },
        "s-serviceName": "query_all_Hotel_by_CompanyId_3934",
        "s-group": "Service2024",
        "s-url": "/api/query_all_Hotel_by_CompanyId_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"data": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_query_all_FlightInfo_by_CompanyId', methods=['GET'])
def internal_query_all_FlightInfo_by_CompanyId():
    """
    按企业ID查询航班信息。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_id": str(data["company_id"])
        },
        "s-serviceName": "query_all_FlightInfo_by_CompanyId_3934",
        "s-group": "Service2024",
        "s-url": "/api/query_all_FlightInfo_by_CompanyId_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"data": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_delete_company', methods=['POST'])
def internal_delete_company():
    """
    删除企业的内部接口，供管理员调用。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_name": data["company_name"]
        },
        "s-serviceName": "delete_company_by_name_3934",
        "s-group": "Service2024",
        "s-url": "/api/delete_company_by_name_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 删除 User 的内部接口
@app.route('/internal_delete_user', methods=['POST'])
def internal_delete_user():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "user_name": str(data["user_name"])
        },
        "s-serviceName": "delete_user_3934",
        "s-group": "Service2024",
        "s-url": "/api/delete_user_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 添加 hotel 的内部接口
@app.route('/internal_add_hotel', methods=['POST', 'GET'])
def internal_add_hotel():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "city": data["city"],
            "company_name": data["hotel_name"],
            "company_id": str(data["company_id"]),
            "rating": str(data["rating"])
        },
        "s-serviceName": "insert_hotel_3934",
        "s-group": "Service2024",
        "s-url": "/api/insert_hotel_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 添加 flght 的内部接口
@app.route('/internal_add_flight', methods=['POST', 'GET'])
def internal_add_flight():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "departure_city": data["departure_city"],
            "arrival_city": data["arrival_city"],
            "departure_time": data["departure_time"],
            "price": str(data["price"]),
            "company_id": str(data["company_id"]),
            "rating": str(data["rating"])
        },
        "s-serviceName": "insert_flight_3934",
        "s-group": "Service2024",
        "s-url": "/api/insert_flight_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 删除 hotel 的内部接口
@app.route('/internal_delete_hotel', methods=['POST', 'GET'])
def internal_delete_hotel():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "hotel_id": data["hotel_id"]
        },
        "s-serviceName": "delete_hotel_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/delete_hotel_by_id_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})
        
# 删除 flght 的内部接口
@app.route('/internal_delete_flight', methods=['POST', 'GET'])
def internal_delete_flight():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "flight_id": data["flight_id"]
        },
        "s-serviceName": "delete_flight_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/delete_flight_by_id_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 添加 Ticket 的内部接口
@app.route('/internal_add_ticket', methods=['POST'])
def internal_add_ticket():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "flight_id": str(data["flight_id"]),
            "departure_city": data["departure_city"],
            "arrival_city": data["arrival_city"],
            "departure_time": data["departure_time"],
            "price": str(data["price"]),
            "company_id": str(data["company_id"]),
            "rating": str(data["rating"])
        },
        "s-serviceName": "add_ticket_3934",
        "s-group": "Service2024",
        "s-url": "/api/add_ticket_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 删除 Ticket 的内部接口
@app.route('/internal_delete_ticket', methods=['POST'])
def internal_delete_ticket():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "flight_id": str(data["flight_id"])
        },
        "s-serviceName": "delete_ticket_3934",
        "s-group": "Service2024",
        "s-url": "/api/delete_ticket_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 更新企业类型
@app.route('/internal_update_hotel', methods=['POST'])
def internal_update_hotel():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "hotel_id": data["hotel_id"],
            "company_id": data["company_id"],
            "hotel_name": data["hotel_name"],
            "city": data["city"],
            "rating": str(data["rating"])
        },
        "s-serviceName": "update_hotel_3934",
        "s-group": "Service2024",
        "s-url": "/api/update_hotel_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 更新企业类型
@app.route('/internal_update_company', methods=['POST'])
def internal_update_company():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_name": data["company_name"],
            "company_type": data["company_type"]
        },
        "s-serviceName": "update_company_type_3934",
        "s-group": "Service2024",
        "s-url": "/api/update_company_type_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})
    
# 更新用户权限
@app.route('/internal_update_user', methods=['POST'])
def internal_update_user():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "user_name": data["user_name"],
            "user_role": data["user_role"]
        },
        "s-serviceName": "update_user_role_3934",
        "s-group": "Service2024",
        "s-url": "/api/update_user_role_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

# 更新 Ticket 的内部接口
@app.route('/internal_update_ticket', methods=['POST'])
def internal_update_ticket():
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "flight_id": str(data["flight_id"]),
            "departure_city": data["departure_city"],
            "arrival_city": data["arrival_city"],
            "departure_time": data["departure_time"],
            "price": str(data["price"]),
            "company_id": str(data["company_id"]),
            "rating": str(data["rating"])
        },
        "s-serviceName": "update_ticket_3934",
        "s-group": "Service2024",
        "s-url": "/api/update_ticket_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_submit_order', methods=['GET', 'POST'])
def internal_submit_order():
    """
    最终下单接口：根据 user_id、flight_id、hotel_id、carrental_id、attraction_id 等信息，
    从数据库查询单价并计算总价，然后调用 BPMN 流程完成后续保存订单动作。
    """
    data = request.get_json()
    
    # 获取传递的参数
    user_id = data.get("user_id")
    flight_id = data.get("flight_id")
    hotel_id = data.get("hotel_id")
    carrental_id = data.get("carrental_id")
    attraction_id = data.get("attraction_id")

    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    
    # get flight price
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {"flight_id": str(flight_id)},
        "s-serviceName": "get_flight_price_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_flight_price_by_id_3934",
        "s-method": "POST"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=10)
    response_data = response.json()
    flight_price = 0
    if len(response_data['data']):
        flight_price = response_data['data'][0]['price']

    # get carrental_id price
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {"carrental_id": str(carrental_id)},
        "s-serviceName": "get_car_price_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_car_price_by_id_3934",
        "s-method": "POST"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=10)
    response_data = response.json()
    carrental_price = 0
    if len(response_data['data']):
        carrental_price = response_data['data'][0]['price']
    
    # get hotel price
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {"room_id": str(hotel_id)},
        "s-serviceName": "get_hotel_price_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_hotel_price_by_id_3934",
        "s-method": "POST"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=10)
    response_data = response.json()
    room_price = 0
    if len(response_data['data']):
        room_price = response_data['data'][0]['room_price']
    
    # get attraction price
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {"attraction_id": str(attraction_id)},
        "s-serviceName": "get_attraction_price_by_id_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_attraction_price_by_id_3934",
        "s-method": "POST"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=10)
    response_data = response.json()
    attraction_price = 0
    if len(response_data['data']):
        attraction_price = response_data['data'][0]['price']

    pd = {}
    bd = {"user_id": user_id,"flight_id": flight_id, "room_id": hotel_id,
    "carrental_id": carrental_id, "attraction_id": attraction_id, "hotel_id": hotel_id,
    "flightprice": flight_price, "room_price": room_price,
    "carprice": carrental_price, "attprice": attraction_price}
    # 11. 执行主要的 BPMN 完成命令
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "submitorder",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output = execute_command(complete_command)

    return jsonify({"success": True})

# internal_submit_travel_info 接口： 接收travel_local发来的信息，调用BPMN服务并返回结果
@app.route('/internal_submit_travel_info', methods=['POST'])
def internal_submit_travel_info():
    """
    接收来自前端(travel_local.py)的旅行偏好信息,
    分别查询航班/酒店/租车/景点，对数据进行整合和排序(可使用 BPMN 或直接写逻辑),并返回。
    """
    data = request.get_json()
    
    # 获取传递的参数
    departure_date = data.get("departure_date")
    departure_city = data.get("departure_city")
    arrival_city = data.get("arrival_city")
    need_car = data.get("need_car", "no")
    car_type = data.get("car_type")
    gear_type = data.get("gear_type")
    guide = data.get("guide")
    preference = data.get("preference", "rating")
    
    prefernce_flight = data.get("prefernce_flight")
    prefernce_hotel = data.get("prefernce_hotel")
    prefernce_carrental = data.get("prefernce_carrental")
    prefernce_attraction = data.get("prefernce_attraction")
    
    pd = {"preference": 0, "needcar": 0}
    if need_car == "yes":
        pd["needcar"] = 1
    else:
        pd["needcar"] = 0
    
    if preference == "rating":
        pd["preference"] = 0
    else:
        pd["preference"] = 1
        
    bd = {}

    # 执行 BPMN 完成命令
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "recommendbypreference",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output = execute_command(complete_command)

    # 统一的请求地址和请求头
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # -------- 1. Ticket Query --------
    ticket_body = {
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "departure_date": departure_date,
        "preference": preference
    }
    ticket_payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": ticket_body,
        "s-serviceName": "ticket_query_3934",
        "s-group": "Service2024",
        "s-url": "/api/ticket_query_3934",
        "s-method": "POST"
    }
    try:
        ticket_resp = requests.post(api_url, headers=headers, json=ticket_payload, timeout=10)
        ticket_resp.raise_for_status()
        ticket_data = ticket_resp.json().get("data", {})  # 返回格式类似 { "data": { "ticket0": {...}, "ticket1": {...}, ... } }
    except Exception as e:
        print("ticket_query_3934 failed:", e)
        ticket_data = {}

    # -------- 2. Car Rental Query --------
    # 只有在 need_car != "no" 时才查询
    car_data = {}
    if need_car==None or need_car.lower() != "no" :
        car_body = {
            "arrival_city": arrival_city,
            "car_type": car_type,
            "gear_type": gear_type,
            "preference": preference,
            "need_car": need_car
        }
        car_payload = {
            "s-consumerName": "A",
            "headers": {},
            "body": car_body,
            "s-serviceName": "car_rental_query_3934",
            "s-group": "Service2024",
            "s-url": "/api/car_rental_query_3934",
            "s-method": "POST"
        }
        try:
            car_resp = requests.post(api_url, headers=headers, json=car_payload, timeout=10)
            car_resp.raise_for_status()
            car_data = car_resp.json().get("data", {})  
        except Exception as e:
            print("car_rental_query_3934 failed:", e)
            car_data = {}

    # -------- 3. Hotel Query --------
    hotel_body = {
        "arrival_city": arrival_city,
        "preference": preference
    }
    hotel_payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": hotel_body,
        "s-serviceName": "hotel_query_3934",
        "s-group": "Service2024",
        "s-url": "/api/hotel_query_3934",
        "s-method": "POST"
    }
    try:
        hotel_resp = requests.post(api_url, headers=headers, json=hotel_payload, timeout=10)
        hotel_resp.raise_for_status()
        hotel_data = hotel_resp.json().get("data", {})
    except Exception as e:
        print("hotel_query_3934 failed:", e)
        hotel_data = {}

    # -------- 4. Attraction Query --------
    attraction_body = {
        "arrival_city": arrival_city,
        "preference": preference
    }
    attraction_payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": attraction_body,
        "s-serviceName": "attraction_query_3934",
        "s-group": "Service2024",
        "s-url": "/api/attraction_query_3934",
        "s-method": "POST"
    }
    try:
        attraction_resp = requests.post(api_url, headers=headers, json=attraction_payload, timeout=10)
        attraction_resp.raise_for_status()
        attraction_data = attraction_resp.json().get("data", {})
    except Exception as e:
        print("attraction_query_3934 failed:", e)
        attraction_data = {}

    # query attraction
    pd = {}
    bd = {"arrival_city": arrival_city, "attractionrating": prefernce_attraction}
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "attrating",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output_attraction = execute_command(complete_command)
    data_attraction = str_to_json(output_attraction)

    pd = {}
    bd = {"arrival_city": arrival_city,"departure_time": departure_date,
    "departure_city": departure_city, "flightrating": prefernce_flight}
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "flightrating",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output_flight = execute_command(complete_command)
    data_flight = str_to_json(output_flight)

    pd = {"needcar": 1}
    bd = {"arrival_city": arrival_city, "carrentalrating": prefernce_carrental,
    "transmission_type": gear_type, "car_type": car_type}
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "carrating",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output_car = execute_command(complete_command)
    data_car = str_to_json(output_car)

    pd = {}
    bd = {"arrival_city": arrival_city, "hotelrating": prefernce_hotel}
    complete_command = [
        "python3", "tool.py", "bpmn", "complete",
        "-ip", ip,
        "-p", str(port),
        "-if", if_path,
        "-n", "hotelrating",
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-u", user
    ]
    output_hotel = execute_command(complete_command)
    data_hotel= str_to_json(output_hotel)

    # 构建返回的列表
    tickets_list = []
    for item in ticket_data:
        tickets_list.append((
            item.get("flight_id", ""),
            item.get("departure_city", ""),
            item.get("arrival_city", ""),
            item.get("departure_time", ""),
            item.get("price", ""),
            item.get("rating", "")
        ))

    flights_list = []
    for item in data_flight['data']:
        flights_list.append((
            item["flight_id"],
            item["departure_city"],
            item["arrival_city"],
            item["departure_time"],
            item["price"],
            item["rating"]
        ))

    car_list = []
    for val in car_data:
        car_list.append((
            val.get("carrental_id", ""),
            val.get("car_type", ""),
            val.get("transmission_type", ""),
            val.get("rental_location", ""),
            val.get("return_location", ""),
            val.get("price", ""),
            val.get("rating", "")
        ))
    carrental_list = []
    for item in data_car['data']:
        carrental_list.append((
            item["carrental_id"],
            item["car_type"],
            item["transmission_type"],
            item["rental_location"],
            item["return_location"],
            item["price"],
            item["rating"]
        ))

    hotel_list = []
    for val in hotel_data:
        hotel_list.append((
            val.get("room_id", ""),
            val.get("room_number", ""),
            val.get("room_type", ""),
            val.get("room_price", ""),
            val.get("rating", ""),
            val.get("hotel_name", "")
        ))
    hotelroom_list = []
    for item in data_hotel['data']:
        hotelroom_list.append((
            item["room_id"],
            item["room_number"],
            item["room_type"],
            item["room_price"],
            item["rating"],
            item["hotel_name"]
        ))

    attraction_list = []
    for val in attraction_data:
        attraction_list.append((
            val.get("attraction_id", ""),
            val.get("attraction_name", ""),
            val.get("city", ""),
            val.get("price", ""),
            val.get("rating", "")
        ))
    attractions_list = []
    for item in data_attraction['data']:
        attractions_list.append((
            item["attraction_id"],
            item["attraction_name"],
            item["city"],
            item["price"],
            item["rating"]
        ))

    # 组装返回给 travel_local.py 的数据结构
    form_data = {
        "flights": flights_list,
        "hotels": hotelroom_list,
        "car_rentals": carrental_list,
        "attractions": attractions_list
    }

    return jsonify(form_data)

@app.route('/travel_recommend', methods = ['POST', 'GET'])
def travel_recommend():
    """
    演示：返回推荐结果的数据接口。
    """
    datajson = request.get_data()
    input = json.loads(datajson)
    
    # 获取传递的参数
    ticket_result = input["ticket_result"]
    hotel_result = input["hotel_result"]
    car_rental_result = input["car_rental_result"]
    attraction_result = input["attraction_result"]

    recommend_result = {
        "ticket_result": ticket_result,
        "hotel_result": hotel_result,
        "car_rental_result": car_rental_result,
        "attraction_result": attraction_result
    }
    return json.dumps(recommend_result, ensure_ascii=False)

@app.route('/get_id_by_name_company', methods = ['POST', 'GET'])
def get_id_by_name_company():
    """
    通过 company_name 获取公司ID。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_name": data["company_name"]
        },
        "s-serviceName": "get_id_by_name_company_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_id_by_name_company_3934",
        "s-method": "POST"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"id": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/get_id_by_name_user', methods = ['POST', 'GET'])
def get_id_by_name_user():
    """
    通过 user_name 获取用户ID。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "user_name": data["user_name"]
        },
        "s-serviceName": "get_id_by_name_user_3934",
        "s-group": "Service2024",
        "s-url": "/api/get_id_by_name_user_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"id": response_data.get("data", []), "success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})


@app.route('/internal_add_company', methods=['POST'])
def internal_add_company():
    """
    添加企业的内部接口，供管理员或注册流程使用。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "company_name": data["company_name"],
            "password": data["password"],
            "company_type": data["company_type"]
        },
        "s-serviceName": "insert_company_3934",
        "s-group": "Service2024",
        "s-url": "/api/insert_company_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_add_user', methods=['POST'])
def internal_add_user():
    """
    添加用户的内部接口，供管理员或注册流程使用。
    """
    data = request.get_json()
    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json","Content-Type": "application/json"}
    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "user_name": data["user_name"],
            "password": data["pass_word"],
            "user_role": data["user_role"]
        },
        "s-serviceName": "insert_user_3934",
        "s-group": "Service2024",
        "s-url": "/api/insert_user_3934",
        "s-method": "POST"
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except:
        return jsonify({"success": False})

@app.route('/internal_add_user_rating', methods=['POST'])
def internal_add_user_rating():
    """
    添加用户对某实体（如航班、酒店）的评分的内部接口。
    接收：
    {
      "entity_type": "FlightInfo",  # Hotel / CarRental / Attraction / Guide
      "entity_id": "xxx",
      "rating": "xxx"
    }
    """
    data = request.get_json()
    entity_type = data["entity_type"]
    entity_id = data["entity_id"]
    rating = data["rating"]

    api_url = "http://10.77.110.222:8999/grafana/runNoCache?loadBalance=enabled"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "s-consumerName": "A",
        "headers": {},
        "body": {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "rating": rating
        },
        "s-serviceName": "add_rating_3934",  # 需在后端做插入 "INSERT INTO UserRating(...)"
        "s-group": "Service2024",
        "s-url": "/api/add_rating_3934",
        "s-method": "POST"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        return jsonify({"success": response_data.get("success", False)})
    except Exception as e:
        print("internal_add_user_rating error:", e)
        return jsonify({"success": False})


def execute_command(command):
    """
    调用外部命令行执行 BPMN 流程或其他业务逻辑的封装。

    执行一个外部命令并返回其输出。

    :param command: 命令参数列表，例如 ["python3", "tool.py", "sign", ...]
    :return: 命令的标准输出，如果执行失败则返回 None
    """
    try:
        result = subprocess.run(
            command,
            check=True,              # 如果命令返回非零退出状态，会引发异常
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE,  # 捕获标准错误
            text=True                # 以字符串形式返回输出
        )
        print(f"命令执行成功: {' '.join(command)}")
        print("输出:", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {' '.join(command)}")
        print("错误信息:", e.stderr)
        return None

# 执行初始化BPMN
@app.route('/init', methods=['POST'])
def init():

    name = "Submit"
    pd = {}
    bd = {}
    user = "anyone"
    bpmn_file="bpmns/test.bpmn"
    signature_file = "test.bpmn_sigs"
    deploy_bpmn_name = "test.bpmn"
    instance_oid = "testOid"
    signer_keys = ["P-3934", "P-3913"]
    signer_output = "signatures/test.bpmn_sigs"
    deploy_signature_file = "signatures/test.bpmn_sigs"

    # 1. 执行签名命令
    sign_command = [
        "python3", "tool.py", "sign", "mutil",
        "-t", "file",
        "-c", bpmn_file,
        "-pk"] + signer_keys + [
        "-o", signer_output
    ]
    if execute_command(sign_command) is None:
        print("签名命令失败，终止执行。")
        return jsonify({"success": False})

    # 2. 执行部署命令
    deploy_command = [
        "python3", "tool.py", "bpmn", "deploy",
        "-ip", ip,
        "-p", str(port),
        "-f", bpmn_file,
        "-n", deploy_bpmn_name,
        "-s", deploy_signature_file
    ]
    if execute_command(deploy_command) is None:
        print("部署命令失败，终止执行。")
        return jsonify({"success": False})

    # 3. 执行实例化命令
    instance_command = [
        "python3", "tool.py", "bpmn", "instance",
        "-ip", ip,
        "-p", str(port),
        "-n", deploy_bpmn_name,
        "-pd", json.dumps(pd, ensure_ascii=False),
        "-bd", json.dumps(bd, ensure_ascii=False),
        "-t", json.dumps({"register": user}),
        "-o", instance_oid
    ]
    if execute_command(instance_command) is None:
        print("实例化命令失败，终止执行。")
        return jsonify({"success": False})
    
    return jsonify({"success": True})

# 启动 Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9527)