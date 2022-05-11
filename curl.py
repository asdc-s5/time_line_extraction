import requests

header = {'Content-Type' : 'application/json;charset=utf-8'}
#header={}
data_raw = {
"inputText": "—Todos ustedes, Zombies— en el año dos mil narra la crónica de un hombre joven.",
"inputDate": "",
"domain": "standard",
"lan": "es"}
url = 'https://annotador.oeg.fi.upm.es/annotate'

res = requests.post(url, headers=header ,data=data_raw)
print(res.json())



"""

"""