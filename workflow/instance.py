import subprocess
import sys
import getopt
import json
 
# python3 instance.py --allocationTablePath=./table/0923_Submit.bpmn.table --deploymentName=0923TravelRecommend.bpmn --processDataPath=./data/processData.txt --businessDataPath=./data/instanceData.txt

def main():
    opts, args = getopt.getopt(sys.argv[1:], "h", ["allocationTablePath=", "deploymentName=", "processDataPath=", "businessDataPath="])
    deploymentName = ""
    staticAllocationTable = ""
    processData = ""
    businessData = ""

    for op, value in opts:
        if op == "-h":
            #usage()
            print("allocationTablePath:静态分配表文件的路径\ndeploymentName:部署的deployment的Name\nprocessDataPath:processData文件的路径\nbusinessData:businessData文件的路径")
            print("注1:allocationTable,processData,businessData,均需要为json格式")
            print("注2:参数中存在空格记得使用双引号，如\"** *\"")
            print("python instance.py --allocationTablePath= --deploymentName= --processDataPath= --businessDataPath=")
            sys.exit()
        elif op == "--allocationTablePath":
            with open(value, 'r') as f:
                staticAllocationTable = f.read()
        elif op == "--deploymentName":
            deploymentName = value
        elif op == "--processDataPath":
            with open(value, 'r') as f:
                processData = f.read()
        elif op == "--businessDataPath":
            with open(value, 'r') as f:
                businessData = f.read()

    map = {
        "deploymentName": deploymentName,
        "processData": processData.replace("\n", ""),
        "businessData": businessData.replace("\n", ""),
        "staticAllocationTable": staticAllocationTable.replace("\n", ""),
        "fcn": "instance"
    }

    data_json_str = json.dumps(map)
    curl_command = f"curl -X POST http://10.77.110.222:8999/grafana/wfRequest/instance  -H \"Accept: application/json\" -H \"Content-Type: application/json\" -d '{data_json_str}'"

    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        resultMap = json.loads(result.stdout)
        if resultMap.get("模拟执行结果"):
            with open("/home/torres/codes/travelAgency/workflow/data/oid.txt", "w") as f:
                f.write(resultMap["Oid"])
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
