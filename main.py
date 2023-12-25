from time import sleep as timeSleep
from pyngrok import ngrok

from os import environ
from socket import socket, AF_INET, SOCK_STREAM
from requests import get as requests_get
from secrets import token_urlsafe
from random import shuffle

import concurrent.futures, yaml, logging, os
from base64 import b64decode
from datetime import datetime
from threading import Thread
from itertools import cycle
from flask import Flask; app = Flask(
    __name__
)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

ngrokTcpURL: str = ''
ngrokConfig: ngrok.PyngrokConfig = ngrok.PyngrokConfig(auth_token = environ.get('NGROK_AUTH_TOKEN'))
proxyList: list[str] = list()

if (os.path.isfile((backupFileName := 'proxyBackup.txt'))):
    proxyList = list(set([line.strip() for line in open(backupFileName, 'r').readlines()]))


config = yaml.safe_load( open('config.yaml', 'r'))

MAX_WORKER: int = config['max_worker']
SHUFFLE_PROXY: bool = config['proxy']['shuffle']
PROXY_TIMEOUT: int = config['proxy']['timeout_in_second']
VERBOSE: bool = config['verbose']

proxyID: dict = {}
checkStatus: dict = {}
checkBeforeDelete: int = 2

# ============================================================================================

proxyProvider: str = b'aHR0cHM6Ly9wcm94eXNwYWNlLnByby9odHRwLnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vbW1weDEyL3Byb3h5LWxpc3QvbWFzdGVyL2h0dHAudHh0Cmh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9CbGFja1Nub3dEb3QvcHJveHlsaXN0LXVwZGF0ZS1ldmVyeS1taW51dGUvbWFpbi9odHRwcy50eHQKaHR0cDovL3dvcm0ucmlwL2h0dHAudHh0Cmh0dHA6Ly9wcm94eXNlYXJjaGVyLnNvdXJjZWZvcmdlLm5ldC9Qcm94eSUyMExpc3QucGhwP3R5cGU9aHR0cApodHRwczovL2FwaS5wcm94eXNjcmFwZS5jb20vdjIvP3JlcXVlc3Q9Z2V0cHJveGllcyZhbXA7cHJvdG9jb2w9aHR0cCZhbXA7dGltZW91dD01ODUwJmFtcDtjb3VudHJ5PWFsbCZhbXA7c3NsPWFsbCZhbXA7YW5vbnltaXR5PWFsbCZhbXA7c2ltcGxpZmllZD10cnVlCmh0dHBzOi8vcHJveHlzcGFjZS5wcm8vaHR0cHMudHh0Cmh0dHBzOi8vbXVsdGlwcm94eS5vcmcvdHh0X2FsbC9wcm94eS50eHQKaHR0cHM6Ly9hcGkub3BlbnByb3h5bGlzdC54eXovaHR0cC50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1RoZVNwZWVkWC9QUk9YWS1MaXN0L21hc3Rlci9odHRwLnR4dGh0dHBzOi8vYXBpLm9wZW5wcm94eWxpc3QueHl6L2h0dHAudHh0Cmh0dHA6Ly9yb290amF6ei5jb20vcHJveGllcy9wcm94aWVzLnR4dApodHRwczovL2FwaS5wcm94eXNjcmFwZS5jb20vP3JlcXVlc3Q9ZGlzcGxheXByb3hpZXMmcHJveHl0eXBlPWh0dHAKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2NsYXJrZXRtL3Byb3h5LWxpc3QvbWFzdGVyL3Byb3h5LWxpc3QtcmF3LnR4dApodHRwczovL3Byb3h5LXNwaWRlci5jb20vYXBpL3Byb3hpZXMuZXhhbXBsZS50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1RoZVNwZWVkWC9QUk9YWS1MaXN0L21hc3Rlci9odHRwLnR4dApodHRwOi8vYWxleGEubHIyYi5jb20vcHJveHlsaXN0LnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vQjRSQzBERS1UTS9wcm94eS1saXN0L21haW4vSFRUUC50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3Jvb3N0ZXJraWQvb3BlbnByb3h5bGlzdC9tYWluL0hUVFBTX1JBVy50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3N1bm55OTU3Ny9wcm94eS1zY3JhcGVyL21hc3Rlci9wcm94aWVzLnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vc2hpZnR5dHIvcHJveHktbGlzdC9tYXN0ZXIvcHJveHkudHh0Cmh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Vc2VyUjNYL3Byb3h5LWxpc3QvbWFpbi9vbmxpbmUvaHR0cC50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1NoaWZ0eVRSL1Byb3h5LUxpc3QvbWFzdGVyL2h0dHAudHh0Cmh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9vcHN4Y3EvcHJveHktbGlzdC9tYXN0ZXIvbGlzdC50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL21vbm9zYW5zL3Byb3h5LWxpc3QvbWFpbi9wcm94aWVzL2h0dHAudHh0Cmh0dHBzOi8vc2hlZXNoLnJpcC9odHRwLnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vcHJveHk0cGFyc2luZy9wcm94eS1saXN0L21haW4vaHR0cC50eHQKaHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1RoZVNwZWVkWC9TT0NLUy1MaXN0L21hc3Rlci9odHRwLnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vamV0a2FpL3Byb3h5LWxpc3QvbWFpbi9vbmxpbmUtcHJveGllcy90eHQvcHJveGllcy1odHRwLnR4dApodHRwczovL3Jhdy5naXRodWJ1c2VyY29udGVudC5jb20vbW9ub3NhbnMvcHJveHktbGlzdC9tYWluL3Byb3hpZXNfYW5vbnltb3VzL2h0dHAudHh0Cmh0dHBzOi8vcmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbS9CbGFja1Nub3dEb3QvcHJveHlsaXN0LXVwZGF0ZS1ldmVyeS1taW51dGUvbWFpbi9odHRwLnR4dApodHRwczovL3d3dy5wcm94eS1saXN0LmRvd25sb2FkL2FwaS92MS9nZXQ/dHlwZT1odHRw'
proxyProvider: list[str] = b64decode(proxyProvider).decode('UTF-8').split('\n')

'''
proxyProvider: list[str] = [
    # Add your proxy sources here, each URL pointing to a plain text list of proxy addresses.
    # Ensure URLs are in their base64-encoded format to prevent Replit restrictions.
    # Example: 'https://api.example.com/proxylist.txt\n'

    # Add more proxy sources as needed
]
'''

# ============================================================================================


class pprint:
    def __init__(self, loc: str, text: str, *args, **kwargs) -> None:
        self.nowDate: datetime.now = datetime.now()

        if not (VERBOSE):
            print(
                self.nowDate.strftime("%Y-%m-%dT%H:%M:%S.")
                + str(self.nowDate.microsecond)
                + f" server[{loc}]: {text}",
                *args,
                **kwargs,
            )

# ============================================================================================

@app.route('/')
def a11_n3bap() -> str:
    if (not proxyList):
        return 'No proxy have been tested yet, come back again in 30 seconds'

    return '<br>'.join(proxyList)

def deleter() -> None: # This prevents the script using too much cpu
    global proxyID

    while True:

        if (len(proxyID) > 200):
            for key in list(proxyID.keys())[:200 - MAX_WORKER]:
                del proxyID[key]

def refresh_proxy() -> None:
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers = (1 if (_worker := int(MAX_WORKER / 9)) < 0 else _worker)) as executor:
            futures: list = [executor.submit(checkProxy, proxy, True) for proxy in proxyList]
            concurrent.futures.wait(futures)
            timeSleep(240)

def checkProxy(proxyAddress: str, isChecking: bool = False) -> None:

    if (isChecking and proxyAddress not in checkStatus):
        checkStatus[proxyAddress] = 0

    globals()['proxyID'][packetID := token_urlsafe(24).replace('_', '')] = proxyAddress
    split_proxyAddress: list = proxyAddress.split(':')

    try:
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.settimeout(PROXY_TIMEOUT); sock.connect((split_proxyAddress[0], int(split_proxyAddress[1])))

            sock.send(str.encode(
                f'GET /{packetID} HTTP/1.1\r\n'
                'Host: ' + ngrokTcpURL + '\r\n'
                '\r\n'

            ))

    except Exception:
        # open('blacklistProxy.txt', 'a').write(proxyID[packetID] + '\n')

        if (checkStatus[proxyAddress] >= checkBeforeDelete):
            proxyList.remove(proxyAddress)
            del checkStatus[proxyAddress]

        else:
            checkStatus[proxyAddress] += 1

        del globals()['proxyID'][packetID]

Thread(target = deleter).start()

# ========================================================================================================================================== #

def packetHandler(connection: socket, connectionAddress: tuple[str, int]) -> None:
    try:
        connectionBuffer: str = connection.recv(128).decode('UTF-8')

        if ( (packetIDs := connectionBuffer.split()[1][1:]) in proxyID.keys()):
            pprint('packetHandler', f'New proxy has been captured => {proxyID[packetIDs]} || {connectionAddress}')

            if (proxyID[packetIDs] not in proxyList):
              proxyList.append(proxyID[packetIDs])

            with open('proxyBackup.txt', 'w') as file: file.write( # Replit sometimes unexpectedly crashed and restart the scripts
                '\n'.join(proxyList)
            )

            del globals()['proxyID'][packetIDs]

            if ((_proxy := proxyID[packetIDs]) in checkStatus):
                del checkStatus[_proxy]

    except Exception as r:
        print(str(r))

def proxyGetter() -> None:

    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers = MAX_WORKER) as executor:
            availableProxy: list[str] = [
                address
                    for url in proxyProvider

                    for address in requests_get(url).text.splitlines()
                        if ':' in address and address.replace('.', '').replace(':', '').isdigit()

            ]

            if (SHUFFLE_PROXY): shuffle(
                availableProxy
            )

            futures: list = [executor.submit(checkProxy, proxyAddress) for proxyAddress in availableProxy]; 
            concurrent.futures.wait(futures)

ngrok.connect(9000, 'tcp', pyngrok_config = ngrokConfig)
ngrokTcpURL: str = str(ngrok.get_tunnels()[0])[20:].split('"')[0]

pprint('Server', f'Ngrok server is running => {(_url := ngrokTcpURL.split(":"))[0]}:{_url[1]}')

with socket(AF_INET, SOCK_STREAM) as socketServer:
    socketServer.bind(('0.0.0.0', 9000)); socketServer.listen()

    Thread(target = lambda: app.run(host = '0.0.0.0', port = 5000)).start()
    Thread(target = refresh_proxy).start()
    Thread(target = proxyGetter).start()

    while True:
        connection, _ = socketServer.accept()
        Thread(target = packetHandler, args = (connection, _)).start()