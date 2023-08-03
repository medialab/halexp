import requests

url = 'http://10.17.0.14:5000/json-example'
myobj = {
    "language" : "Python",
    "framework" : "Flask",
    "website" : "Scotch",
    "version_info" : {
        "python" : "3.9.0",
        "flask" : "1.1.2"
    },
    "examples" : ["query", "form", "json"],
    "boolean_test" : True
}

x = requests.post(url, json = myobj)

print(x.text)
