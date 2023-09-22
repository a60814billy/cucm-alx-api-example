import os
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

urllib3.disable_warnings()

from flask import Flask

base_dir = os.path.dirname(__file__)

app = Flask(__name__, static_folder=os.path.join(base_dir, "static"))

cucm_api_server = os.environ["CUCM_API_SRV"]
cucm_version = os.environ['CUCM_VER'] or '14.0'
axl_credential = {
    'username': os.environ["CUCM_API_USER"],
    'password': os.environ["CUCM_API_PASS"]
}

@app.get('/')
def index():
    return app.send_static_file("index.html")

@app.get('/appUser')
def getApplicationUser():

    soapEnvelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/14.0">
        <soapenv:Header/>
        <soapenv:Body>
        <ns:listAppUser>
            <searchCriteria>
                <userid>%</userid>
            </searchCriteria>
        </ns:listAppUser>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    headers = {
        "Content-Type": "text/xml",
        "Accept": "text/xml",
        "SOAPAction": f'"CUCM:DB ver={cucm_version} listAppUser"'
    }

    resp = requests.post(cucm_api_server,
                        verify=False,
                        auth=HTTPBasicAuth(axl_credential["username"], axl_credential['password']), 
                        headers=headers, 
                        data=soapEnvelope)
    
    print(resp.content)

    ns = {
        "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
        "axl":"http://www.cisco.com/AXL/API/14.0"
    }

    tree = ET.fromstring(resp.content)
    users = tree.find("./soapenv:Body/axl:listAppUserResponse/return", namespaces=ns)

    result = []
    

    for user in users:
        app_user = {}
        for attr in user.iter():
            if attr is user:
                continue
            app_user[attr.tag] = attr.findtext('.')
        result.append(app_user)

    return result

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)

