import click
import os
import configparser
import requests
import fnmatch
import sys

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
