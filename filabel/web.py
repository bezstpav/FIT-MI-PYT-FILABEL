import os
import configparser
import sys
import flask
import hmac
import hashlib

from .github import GitHub

app = flask.Flask(__name__)

def parseConfigsFromEnv():
    """
    Load config from ENV variable
    """

    token=None
    secret=None
    labels={}
    
    if 'FILABEL_CONFIG' not in os.environ:
        raise Exception('Missing env FILABEL_CONFIG') 

    files = os.environ['FILABEL_CONFIG'].split(':')
    for file in files:
        try:
            config = configparser.ConfigParser()
            config.read(file)
            if 'github' in config:
                token = config['github']['token']
                secret = config['github']['secret']
            elif 'labels' in config:
                for key in config['labels'].keys():
                    labels[key] = config['labels'][key].strip().split('\n')
        except:
            raise Exception(F'Configuration {file} not usable!')
        
    if token == None:
        raise Exception("Missing token")

    app.github = GitHub(token)
    app.labels = labels
    app.webhookSecret = secret

class HTTPException(Exception):
    """
    Custom HTTP Exception wrapper
    """

    def __init__(self,message,code=400):
        Exception.__init__(self,message)
        self.code = code
        self.message = message

@app.before_first_request
def webhool_load():
    """
    Parse config on before first request
    """

    parseConfigsFromEnv()


@app.route('/',methods=['GET'])
def index():
    """
    Show Help on intro page
    """

    return flask.render_template('index.html', name=app.github.username,labels = app.labels)

def checkSignature(signature,data):
    """Check signature data signature
    
    :return: success
    :rtype: bool
    """

    github_secret = bytes(app.webhookSecret, 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)


def label(reposlug):
    """
    Parse reposlug to user,repo pair
    """

    tmp = reposlug.split('/')
    if len(tmp) != 2:
        raise HTTPException(F"Reposlug {reposlug} not valid!")
    try:
        app.github.processRepo(tmp[0], tmp[1], None, None, app.labels, False)
    except Exception as err:
        raise HTTPException(str(err))

@app.route('/',methods=['POST'])
@app.route('/webhook',methods=['POST'])
def webhook():
    """
    Web github webhook endpoint
    """

    if not flask.request.is_json:
        raise HTTPException(F"Content is not json")
    
    headers = flask.request.headers
    
    event = headers['X-GitHub-Event']
    if event is None:
        raise HTTPException(F"X-GitHub-Event is missing")
   

    signature = headers['X-Hub-Signature']
    if signature is None:
        raise HTTPException(F"X-Hub-Signature is missing")
 
    if not checkSignature(signature,flask.request.data):
        raise HTTPException(F"Signature is wrong")

    content = flask.request.get_json()
    print(content)
    if event == 'ping':
        zen = content['zen']
        print(F'Received Ping - {zen}')
        return F'Pong - {zen}'
    elif event == 'pull_request':
        reposlug = content['pull_request']['head']['repo']['full_name']
        print(F'Pull request Event - {reposlug}')
        label(reposlug)
        return F"Labeled - {reposlug}"
    else:
        raise HTTPException("Unknown event")



@app.errorhandler(HTTPException)
def handle_invalid_usage(error):
    return error.message,error.code