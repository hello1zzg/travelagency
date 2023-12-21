import requests

url = "http://10.77.110.222:8999/grafana/getResponseByOid/0923TravelRecommend.bpmn@58b9bfb9-c185-4c43-86ae-cad5b8480fc0"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
