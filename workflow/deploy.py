import subprocess
import sys
import argparse

# python3 deploy.py --BpmnPath=./bpmn/diagram_v6.bpmn --deploymentName=0923TravelRecommend.bpmn

def deploy_bpmn(bpmn_path, deployment_name):
    try:
        # 构建 curl 命令
        curl_command = [
            'curl', '-X', 'POST',
            'http://10.77.110.222:8999/grafana/wfRequest/deploy',
            '-H', 'content-type: multipart/form-data',
            '--form', f'file=@{bpmn_path}',
            '--form', f'deploymentName={deployment_name}'
        ]

        # 执行 curl 命令
        result = subprocess.run(curl_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 输出结果
        print(result.stdout.decode())
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr.decode()}")

def main():
    parser = argparse.ArgumentParser(description="Deploy BPMN file to workflow service")
    parser.add_argument("--BpmnPath", type=str, required=True, help="Path to the BPMN file")
    parser.add_argument("--deploymentName", type=str, required=True, help="Deployment name for the BPMN file")

    args = parser.parse_args()

    deploy_bpmn(args.BpmnPath, args.deploymentName)

if __name__ == "__main__":
    main()
