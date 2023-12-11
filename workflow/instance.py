import subprocess
import sys,getopt,json
 
opts,args = getopt.getopt(sys.argv[1:],"h", ["allocationTablePath=", "deploymentName=","processDataPath=","businessDataPath="])
deploymentName = ""
staticAllocationTable = ""
processData=""
businessData=""
for op,value in opts:
    if op == "-h":
        #usage()
        print("allocationTablePath:静态分配表文件的路径\ndeploymentName:部署的deployment的Name\nprocessDataPath:processData文件的路径\nbusinessData:businessData文件的路径")
        print("注1:allocationTable,processData,businessData,均需要为json格式")
        print("注2:参数中存在空格记得使用双引号，如\"** *\"")
        print("python instance.py --allocationTablePath= --deploymentName= --processDataPath= --businessDataPath=")
        sys.exit()
    elif op=="--allocationTablePath":
        f = open(value, 'r')
        f_str = f.read()
        staticAllocationTable=f_str
    elif op=="--deploymentName":
        deploymentName=value
    elif op=="--processDataPath":
        f = open(value, 'r')
        f_str = f.read()
        processData=f_str
    elif op=="--businessDataPath":
        f = open(value, 'r')
        f_str = f.read()
        businessData=f_str
map={}
processData=processData.replace("\n","")
businessData=businessData.replace("\n","")
staticAllocationTable=staticAllocationTable.replace("\n","")



map["deploymentName"]=deploymentName
map["processData"]=processData
map["businessData"]=businessData
map["staticAllocationTable"]=staticAllocationTable
map["fcn"]="instance"
datajsonstr=json.dumps(map)
preStr="curl -X POST http://10.77.70.173:8999/grafana/wfRequest -H \"Accept: application/json\" -H \"Content-Type: application/json\" -d "
curlString=preStr+json.dumps(datajsonstr)
print(curlString)
result = subprocess.Popen(curlString, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8').communicate()[0]
#proxies = {'http': 'socks5://127.0.0.1:7891','https':'socks5://127.0.0.1:7891'}
print(result)
resultMap=json.loads(result)

if resultMap["模拟执行结果"]:
    f=open("workflow/data/oid.txt","w")
    f.truncate(0)
    f.write(resultMap["Oid"])
