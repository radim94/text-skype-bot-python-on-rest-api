import requests

#response=requests.post('localhost:9092')
#response = requests.post("http://127.0.0.1:9090/api/calling/call", verify=False)
response = requests.post("http://127.0.0.1:9092/getSpeechReconnition",verify=False)