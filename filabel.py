import click
import os
import configparser
import requests
import fnmatch
import sys
import flask
import hmac
import hashlib


# Format all OK,FAIL,PR,REPO words
# return string with click style
 

def format(text):
    text = text.lower()
    if text == "ok":
        return click.style('OK', fg='green', bold=True)
    elif text == "fail":
        return click.style('FAIL', fg='red', bold=True)
    elif text == "pr":
        return click.style('PR', bold=True)
    elif text == "repo":
        return click.style('REPO', bold=True)
    else:
        raise Exception("Unkown text")

# Match file with label rules
# return list


def getLabels(source, path):
    result = []
    for label, patterns in source.items():
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                result.append(label)
                break
    return result


class GitHub:

    BASE_URL = "https://api.github.com/"
    PER_PAGE = 100

    def __init__(self, token):
        self.token = token
        self.session = self.createSession()
        self.getUserName()

    # Get UserName From token
    def getUserName(self):
        response = self.session.get(self.BASE_URL+"user")
        if not response.ok:
            raise Exception("Cannot get username")
        self.username = response.json()['login'];
    
    # Create session with predefined github auth header
    # return session
    def createSession(self):
        session = requests.Session()

        def token_auth(req):
            req.headers['Authorization'] = F'token {self.token}'
            return req
        session.auth = token_auth
        return session

    # Process labels for selected repo
    def processRepo(self, user, repo, state, base, labels, delete):
        try:

            PRs = self.getPR(user, repo, state, base)

            click.echo("{} {} - {}".format(format("repo"),
                                           F"{user}/{repo}", format("ok")))

            for pr in PRs:
                self.processPR(pr, labels, delete)
        except:
            click.echo("{} {} - {}".format(format("repo"),
                                           F"{user}/{repo}", format("fail")))

    # Get pull request for repo
    # Return pull request object
    def getPR(self, user, repo, state, base):

        reqParams = {'per_page': 100}
        if state is not None:
            reqParams['state'] = state

        if base is not None:
            reqParams['base'] = base

        url = self.BASE_URL + F"repos/{user}/{repo}/pulls"
        PRs = []

        while True:
            response = self.session.get(url, params=reqParams)
            reqParams = {}

            if not response.ok:
                raise Exception("PR get failed")

            PRs.extend(response.json())

            if 'next' not in response.links:
                return PRs

            url = response.links["next"]["url"]

    # Process label for selected pull request
    def processPR(self, pr, labels, delete):
        try:
            files = self.getPRFiles(pr)
            calculatedLabels = set()
            for file in files:
                for label in getLabels(labels, file["filename"]):
                    calculatedLabels.add(label)

            prLabels = {label['name'] for label in pr['labels']}
            labelsAvailable = set(labels.keys())
            labelsAdd = calculatedLabels - prLabels
            labelsToRemove = (prLabels & labelsAvailable) - calculatedLabels
            labelsKnown = ((prLabels & labelsAvailable) -
                           labelsAdd) - labelsToRemove

            labelsFinal = set(prLabels | labelsAdd)

            if delete:
                labelsFinal = labelsFinal - labelsToRemove

            self.updateLabels(pr, labelsFinal)

            click.echo("  {} {} - {}".format(format("pr"),
                                             pr['html_url'], format("ok")))

            labels = []

            if delete:
                for label in labelsToRemove:
                    labels.append([label, '-', 'red'])

            for label in labelsAdd:
                labels.append([label, '+', 'green'])

            for label in labelsKnown:
                labels.append([label, '='])

            labels.sort(key=lambda x: x[0])

            for label in labels:
                if label[1] == '=':
                    click.echo("    {} {}".format(label[1], label[0]))
                else:
                    click.echo(click.style("    {} {}".format(
                        label[1], label[0]), fg=label[2]))

        except:
            click.echo("  {} {} - {}".format(format("pr"),
                                             pr['html_url'], format("fail")))

    # Replace old labels for pull request

    def updateLabels(self, pr, labels):
        data = list(labels)
        url = F"{pr['issue_url']}/labels"
        response = self.session.put(url, json=data)
        if not response.ok:
            raise Exception("Update labels failed")

    # Get files assosciated with pull requst
    # return file objects
    def getPRFiles(self, pr):
        url = F"{pr['url']}/files"
        files = []
        reqParams = {'per_page': 100}
        while True:
            response = self.session.get(url, params=reqParams)
            reqParams = {}
            if not response.ok:
                raise Exception("File get failed")

            files.extend(response.json())

            if 'next' not in response.links:
                return files

            url = response.links["next"]["url"]


# Parse auth config
def loadAuth(path):
    try:
        config = configparser.ConfigParser()
        config.read(path)
        return config['github']['token']
    except:
        print("Auth configuration not usable!", file=sys.stderr)
        sys.exit(1)


# Parse labels config
def loadLabels(path):
    try:
        config = configparser.ConfigParser()
        config.read(path)

        return {key: config['labels'][key].strip().split(
            '\n') for key in config['labels'].keys()}

    except:
        print('Labels configuration not usable!', file=sys.stderr)
        sys.exit(1)


# Parse reposlugs
def parseReposlugs(reposlugs):
    result = []
    for reposlug in reposlugs:
        tmp = reposlug.split('/')
        if len(tmp) != 2:
            print(F"Reposlug {reposlug} not valid!", file=sys.stderr)
            sys.exit(1)
        result.append(tmp)
    return result


@click.command()
@click.option('-s', '--state', type=click.Choice(['open', 'closed', 'all']), show_default=True, default='open', help='Filter pulls by state.')
@click.option('-d/-D', '--delete-old/--no-delete-old', 'delete', show_default=True, default=True, help='Delete labels that do not match anymore.')
@click.option('-b', '--base', 'branch', default=None, metavar="BRANCH", help='Filter pulls by base (PR target) branch name.')
@click.option('-a', '--config-auth', 'auth', type=click.File('rb'), required=True, help='File with authorization configuration.')
@click.option('-l', '--config-labels', 'label', type=click.File('rb'), required=True, help=' File with labels configuration.')
@click.argument('reposlugs', nargs=-1)
def main(state, delete, branch, auth, label, reposlugs):
    """CLI tool for filename-pattern-based labeling of GitHub PRs"""
    reposlug = parseReposlugs(reposlugs)

    token = loadAuth(auth.name)
    labels = loadLabels(label.name)
    github = GitHub(token)

    for item in reposlug:
        github.processRepo(item[0], item[1], state, branch, labels, delete)


if __name__ == '__main__':
    main()


app = flask.Flask(__name__)

def parseConfigsFromEnv():
    token=None
    labels={}
    webhookSecret = os.environ['WEBHOOK_SECRET']

    if webhookSecret is None:
        raise Exception('Missing env WEBHOOK_SECRET') 


    if 'FILABEL_CONFIG' not in os.environ:
        raise Exception('Missing env FILABEL_CONFIG') 

    files = os.environ['FILABEL_CONFIG'].split(':')
    for file in files:
        try:
            config = configparser.ConfigParser()
            config.read(file)
            if 'github' in config:
                token = config['github']['token']
            elif 'labels' in config:
                for key in config['labels'].keys():
                    labels[key] = config['labels'][key].strip().split('\n')
        except:
            raise Exception(F'Configuration {file} not usable!')
        
    if token == None:
        raise Exception("Missing token")

    app.github = GitHub(token)
    app.labels = labels
    app.webhookSecret = webhookSecret

class HTTPException(Exception):
    def __init__(self,message,code=400):
        Exception.__init__(self,message)
        self.code = code
        self.message = message

@app.before_first_request
def webhool_load():
    parseConfigsFromEnv()


@app.route('/')
def index():
    return flask.render_template('index.html', name=app.github.username,labels = app.labels)

def checkSignature(signature,data):
    github_secret = bytes(app.webhookSecret, 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)


def label(reposlug):
    tmp = reposlug.split('/')
    if len(tmp) != 2:
        raise HTTPException(F"Reposlug {reposlug} not valid!")
    try:
        app.github.processRepo(tmp[0], tmp[1], None, None, app.labels, False)
    except Exception as err:
        raise HTTPException(err.message)

@app.route('/webhook',methods=['POST','GET'])
def webhook():
    
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