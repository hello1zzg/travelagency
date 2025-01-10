import subprocess
import json


    #    bd = {
    #     "user_id": "1",
    #     "flight_id": "1",
    #     "room_id": "1",
    #     "carrental_id": "1",
    #     "attraction_id": "1",
    #     "hotel_id": "1"
    # }

def execute_command(command):
    """
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
            text=True,               # 以字符串形式返回输出
            encoding='utf-8'         # 明确指定编码为UTF-8
        )
        print(f"命令执行成功: {' '.join(command)}")
        print("输出:", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {' '.join(command)}")
        print("错误信息:", e.stderr)
        return None

def execute_tool_commands(bd,ip = "10.77.110.222", port = 8999, if_path = "oids/testOid", name = "Submit", pd = {}, user = "anyone",
                         bpmn_file="bpmns/test.bpmn", signature_file = "test.bpmn_sigs", deploy_bpmn_name = "test.bpmn", instance_oid = "testOid",
                         signer_keys = ["P-3934", "P-3913"], signer_output = "signatures/test.bpmn_sigs", deploy_signature_file = "signatures/test.bpmn_sigs"):
    """
    按顺序执行签名、部署、实例化和主要的 BPMN 完成命令。

    :param ip: 服务器 IP 地址
    :param port: 端口号
    :param if_path: 接口路径
    :param name: 操作名称
    :param pd: 参数数据
    :param bd: 业务数据
    :param user: 用户名
    :param bpmn_file: BPMN 文件路径
    :param signature_file: 签名输出文件路径
    :param deploy_bpmn_name: 部署时使用的 BPMN 名称
    :param instance_oid: 实例化时使用的 OID
    :param signer_keys: 签名时使用的密钥列表
    :param signer_output: 签名输出文件路径
    :param deploy_signature_file: 部署时使用的签名文件路径
    """
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
        return

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
        return

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
        return

    pd = {"login":1}
    bd = {"user_name":"123123"}

    # 4. 执行主要的 BPMN 完成命令
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

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")

    pd = {"usera":1}
    bd = {}

    # 5. 执行主要的 BPMN 完成命令
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

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")


    pd = {"preference": 0, "needcar": 1}
    bd = {}

    # 6. 执行主要的 BPMN 完成命令
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

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")


    pd = {}
    bd = {"arrival_city":"北京","attractionrating":"4.0"}
    # 7. 执行主要的 BPMN 完成命令
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
    output = execute_command(complete_command)

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")


    pd = {}
    bd = {"arrival_city":"北京","departure_time":"2024-12-01","departure_city":"上海","flightrating":"4.0"}
    # 8. 执行主要的 BPMN 完成命令
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
    output = execute_command(complete_command)

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")


    pd = {"needcar":1}
    bd = {"arrival_city":"北京","carrentalrating":"4.0","transmission_type":"自动挡","car_type":"电动车"}
    # 9. 执行主要的 BPMN 完成命令
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
    output = execute_command(complete_command)

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")


    pd = {}
    bd = {"arrival_city":"北京","hotelrating":"4.0"}
    # 10. 执行主要的 BPMN 完成命令
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
    output = execute_command(complete_command)

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")

    pd = {}
    bd = {"user_id":"1","flight_id":"1","room_id":"1","carrental_id":"1","attraction_id":"1","hotel_id":"1","flightprice":"100","room_price":"100","carprice":"100","attprice":"100"}
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

    if output is not None:
        print("主要命令输出结果:")
        print(output)
    else:
        print("主要命令执行失败。")

if __name__ == "__main__":
    # 定义主要命令的参数
    ip = "10.77.110.222"
    port = 8999
    if_path = "oids/testOid"
    name = "Submit"
    pd = {}  # 这里是一个空的 JSON 对象，按需修改

    bd = {
        "user_id": "1",
        "flight_id": "1",
        "room_id": "1",
        "carrental_id": "1",
        "attraction_id": "1",
        "hotel_id": "1"
    }
    user = "anyone"

    # 定义签名、部署和实例化命令的参数
    bpmn_file = "bpmns/test.bpmn"
    signature_file = "test.bpmn_sigs"
    deploy_bpmn_name = "test.bpmn"
    instance_oid = "testOid"
    signer_keys = ["P-3934", "P-3913"]
    signer_output = "signatures/test.bpmn_sigs"
    deploy_signature_file = "signatures/test.bpmn_sigs"

    # 执行所有命令
    execute_tool_commands(
        ip=ip,
        port=port,
        if_path=if_path,
        name=name,
        pd=pd,
        bd=bd,
        user=user,
        bpmn_file=bpmn_file,
        signature_file=signature_file,
        deploy_bpmn_name=deploy_bpmn_name,
        instance_oid=instance_oid,
        signer_keys=signer_keys,
        signer_output=signer_output,
        deploy_signature_file=deploy_signature_file
    )