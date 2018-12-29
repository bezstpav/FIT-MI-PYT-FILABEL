import click
import os
import configparser
import requests
import fnmatch
import sys
import asyncio
import aiohttp
import re
from urllib import parse


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


def getPagesAddress(next, last):
    try:
        parsed = parse.urlparse(str(next))
        nextPage = int(parse.parse_qs(
            parse.urlparse(str(next)).query)["page"][0])
        lastPage = int(parse.parse_qs(
            parse.urlparse(str(last)).query)["page"][0])
        query = parse.parse_qs(parse.urlparse(str(next)).query)
        query = {key: query[key][0] for key in query}
        address = []
        for i in range(nextPage, lastPage+1):
            query["page"] = str(i)
            url = "{}://{}{}?{}".format(parsed.scheme, parsed.netloc,
                                        parsed.path, parse.urlencode(query))
            address.append(url)
        return address
    except Exception as err:
        print(err)

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
        self.getUserName()

    # Get UserName From token
    def getUserName(self):
        response = self.createSession().get(self.BASE_URL+"user")
        if not response.ok:
            raise Exception("Cannot get username")
        self.username = response.json()['login']

    # Create session with predefined github auth header
    # return session
    def createSession(self):
        session = requests.Session()

        def token_auth(req):
            req.headers['Authorization'] = F'token {self.token}'
            return req
        session.auth = token_auth
        return session

    def createAsyncSession(self):
        session = aiohttp.ClientSession(
            headers={"Authorization": F'token {self.token}'}, connector=aiohttp.TCPConnector(verify_ssl=False))
        return session

    # Process labels for selected repo
    async def processRepo(self, user, repo, state, base, labels, delete):
        stdout = ''
        try:
            PRs = await self.getPR(user, repo, state, base)
            stdout = "{} {} - {}".format(format("repo"),
                                         F"{user}/{repo}", format("ok"))+'\n'
            futures = []
            for pr in PRs:
                future = asyncio.ensure_future(
                    self.processPR(pr, labels, delete))
                futures.append(future)

            for item in futures:
                stdout = stdout + await item
        except:
            stdout = "{} {} - {}".format(format("repo"),
                                         F"{user}/{repo}", format("fail"))+'\n'

        return stdout.rstrip()

    # Get pull request for repo
    # Return pull request object
    async def getPR(self, user, repo, state, base):

        reqParams = {'per_page': 100}
        if state is not None:
            reqParams['state'] = state

        if base is not None:
            reqParams['base'] = base

        url = self.BASE_URL + F"repos/{user}/{repo}/pulls"
        PRs = []

        async with self.createAsyncSession() as session:
            async with session.get(url, params=reqParams) as response:
                reqParams = {}
                if response.status != 200:
                    raise Exception("PR get failed")
                obj = await response.json()
                PRs.extend(obj)
                if 'next' not in response.links:
                    return PRs
        futures = []
        addresses = getPagesAddress(
            response.links['next']['url'], response.links['last']['url'])
        for address in addresses:
            future = asyncio.ensure_future(self.getJson(address))
            futures.append(future)

        for future in futures:
            PRs.extend(await future)

        return PRs

    async def getJson(self, address):
        async with self.createAsyncSession() as session:
            async with session.get(address) as response:
                if response.status != 200:
                    raise Exception("Get failed")
                return await response.json()

    # Process label for selected pull request

    async def processPR(self, pr, labels, delete):
        stdout = ''
        try:
            files = await self.getPRFiles(pr)
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

            await self.updateLabels(pr, labelsFinal)

            stdout = "{} {} - {}".format(format("pr"),
                                         pr['html_url'], format("ok")) + '\n'

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
                    stdout = stdout + \
                        "  {} {}".format(label[1], label[0]) + '\n'
                else:
                    stdout = stdout + click.style("  {} {}".format(
                        label[1], label[0]), fg=label[2]) + '\n'

        except Exception as err:
            print(err)
            stdout = stdout + "{} {} - {}".format(format("pr"),
                                                  pr['html_url'], format("fail"))+'\n'
        return stdout

    # Replace old labels for pull request

    async def updateLabels(self, pr, labels):
        data = list(labels)
        url = F"{pr['issue_url']}/labels"

        async with self.createAsyncSession() as session:
            async with session.put(url, json=data) as response:
                obj = await response.text()
                if response.status != 200:
                    raise Exception("Update labels failed")

    # Get files assosciated with pull requst
    # return file objects
    async def getPRFiles(self, pr):
        url = F"{pr['url']}/files"
        files = []
        reqParams = {'per_page': 100}
        async with self.createAsyncSession() as session:
            async with session.get(url, params=reqParams) as response:
                obj = await response.json()
                if response.status != 200:
                    raise Exception("File get failed")
                files.extend(obj)
                if 'next' not in response.links:
                    return files

        futures = []
        addresses = getPagesAddress(
            response.links['next']['url'], response.links['last']['url'])
        for address in addresses:
            future = asyncio.ensure_future(self.getJson(address))
            futures.append(future)

        for future in futures:
            files.extend(await future)
        return files