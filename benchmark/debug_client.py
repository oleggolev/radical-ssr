import json
import requests

target = "https://ssr-bench.radical-serverless.com"
# target = "http://0.0.0.0:8787"
fs_json = open('./benchmark/post.json')
post = json.load(fs_json)
post["id"] = 0

session = requests.Session()
resp = session.post(target + "/post", json=post)
# resp = requests.post(target + "/clear_kv")
# resp = requests.post(target + "/test_kv")
print(resp.content)
assert resp.status_code == 200

resp = session.get(target + "/posts")
print(resp.content)

fs_json.close()