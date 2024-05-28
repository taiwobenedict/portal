import requests, json

def call_external_api(url, data, headers):
  try:
    info, raw, is_get = "", "raw" in str(headers) or "raw" in str(data), "IS_GET" in str(headers) or "IS_GET" in str(data)
    if not raw:
      r = requests.post(url, data=data, headers=headers) if not is_get else requests.get(url, headers=headers)
      info = (r.content).decode("utf-8").encode('ascii', 'ignore')
    else:
      r = requests.post(url, data=json.dumps(data), headers=headers) if not is_get else requests.get(url, headers=headers)
      info = (r.content).decode("utf-8").encode('ascii', 'ignore')
    return info
  except Exception as e:
    raise e
