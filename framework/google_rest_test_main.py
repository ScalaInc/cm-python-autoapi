import requests
import json
import sys


def send_message(search_term_list):
    payload = {'key': 'AIzaSyBIPjime0eBh-gOmO0pcSeOsc_r5GRbqvk', 'cx': '012322969516488428657:pzodp6cbjk8'}
    payload['q']=" ".join(search_term_list)
    r = requests.get("https://www.googleapis.com/customsearch/v1",params=payload)
    print(json.dumps(json.loads(r.text), sort_keys = True, indent = 4, separators = (',',': ')))
    with open('jsonreturn.txt','w') as f:
        f.writelines(json.dumps(json.loads(r.text), sort_keys= True, indent = 4, separators = (',',': ')))
    jresponse =json.loads(r.text)
    items = jresponse['items']
    url_list = []
    for result in items:
           url_list.append(result['link'])
    print(url_list)

    
    
if __name__=="__main__":
    arguments = sys.argv
    print (arguments)
    print (arguments[1:])
    send_message(arguments[1:])