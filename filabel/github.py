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

def getLabels(source, path):
    """Get all labels for given path
    
    :param source: Labels definition
    :type path: dict
    :param path: File full path
    :type path: string
    :return: Labels
    :rtype: list[string]
    """

    result = []
    for label, patterns in source.items():
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                result.append(label)
                break
    return result


def getPagesAddress(next, last):
    """Get GitHub all Page links from next and last link
    
    :param next: next link
    :type next: string
    :param last: last link
    :type last: string
    :return: links
    :rtype: string
    """

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

def format(text):
    """Format all OK,FAIL,PR,REPO words
    
    :param text: word
    :type text: string
    :raises Exception: Unknown text
    :return: formated click style text
    :rtype: string
    """

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


class GitHubAsync:
    """
    GitHub object for async PRs labeling 
    """

    BASE_URL = "https://api.github.com/"
    """
    GitHub API URL
    """


    def __init__(self, token):
        """GH constructor
        
        :param token: github api token
        :type token: string
        """

        self.token = token
        self.getUserName()

    def getUserName(self):
        """
        Get Username from token
        """
        response = self.createSession().get(self.BASE_URL+"user")
        if not response.ok:
            raise Exception("Cannot get username")
        self.username = response.json()['login']

    def createSession(self):
        """
        Create Session with predefined github auth header
        """
        session = requests.Session()

        def token_auth(req):
            req.headers['Authorization'] = F'token {self.token}'
            return req
        session.auth = token_auth
        return session

    def createAsyncSession(self):
        """
        Create Async Session with predefined github auth header
        """
        session = aiohttp.ClientSession(
            headers={"Authorization": F'token {self.token}'}, connector=aiohttp.TCPConnector(verify_ssl=False))
        return session

    async def processRepo(self, user, repo, state, base, labels, delete):
        """Async Label all PRs in given repo
        
        :param user: Repo's owner
        :type user: string
        :param repo: Repo name
        :type repo: string
        :param state: Filter PR state (open|close|all)
        :type state: string
        :param base: Filter by base name
        :type base: string or none
        :param labels: Labels
        :type labels: dict
        :param delete: Delete if additional label exist
        :type delete: bool
        :return: Text output
        :rtype: string
        """

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

    
    async def getPR(self, user, repo, state, base):
        """Async Get PRs for given repo
        
        :param user: Repo's owner
        :type user: string
        :param repo: Repo name
        :type repo: string
        :param state: Filter PR state (open|close|all)
        :type state: string
        :param base: Filter by base name
        :type base: string or none
        :raises Exception: PRs get failed
        :return: PRs
        :rtype: list of prs
        """

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
        """Download and parse JSON
        
        :param address: Address of endpoint
        :type address: string
        :raises Exception: Get failed
        :return: downloaded object
        :rtype: dict
        """

        async with self.createAsyncSession() as session:
            async with session.get(address) as response:
                if response.status != 200:
                    raise Exception("Get failed")
                return await response.json()


    async def processPR(self, pr, labels, delete):
        """Async Set correct labels for PR
        
        :param pr: PR
        :type pr: PR object
        :param labels: Labels
        :type labels: dict
        :param delete: Delete if additional label exist
        :type delete: bool
        :return: Text output
        :rtype: string
        """

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

        except Exception:
            stdout = stdout + "{} {} - {}".format(format("pr"),
                                                  pr['html_url'], format("fail"))+'\n'
        return stdout

    async def updateLabels(self, pr, labels):
        """Async Set labels for PR
        
        :param pr: PR
        :type pr: PR object
        :param labels: labels
        :type labels: list
        :raises Exception: Settings failed
        """

        data = list(labels)
        url = F"{pr['issue_url']}/labels"

        async with self.createAsyncSession() as session:
            async with session.put(url, json=data) as response:
                obj = await response.text()
                if response.status != 200:
                    raise Exception("Update labels failed")


    async def getPRFiles(self, pr):
        """Async Get All Files for PR
        
        :param pr: PR
        :type pr: PR object
        :raises Exception: Get Failed
        :return: Files objects
        :rtype: list
        """

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


class GitHub:
    """
    GitHub object for PRs labeling 
    """

    BASE_URL = "https://api.github.com/"
    """
    GitHub API URL
    """

    def __init__(self, token):
        """GH constructor
        
        :param token: github api token
        :type token: string
        """
        self.token = token
        self.session = self.createSession()
        self.getUserName()

    def getUserName(self):
        """
        Get Username from token
        """
        response = self.session.get(self.BASE_URL+"user")
        if not response.ok:
            raise Exception("Cannot get username")
        self.username = response.json()['login']

    def createSession(self):
        """
        Create Session with predefined github auth header
        """
        session = requests.Session()

        def token_auth(req):
            req.headers['Authorization'] = F'token {self.token}'
            return req
        session.auth = token_auth
        return session

    
    def processRepo(self, user, repo, state, base, labels, delete):
        """Label all PRs in given repo
        
        :param user: Repo's owner
        :type user: string
        :param repo: Repo name
        :type repo: string
        :param state: Filter PR state (open|close|all)
        :type state: string
        :param base: Filter by base name
        :type base: string or none
        :param labels: Labels
        :type labels: dict
        :param delete: Delete if additional label exist
        :type delete: bool
        """
        try:

            PRs = self.getPR(user, repo, state, base)

            click.echo("{} {} - {}".format(format("repo"),
                                           F"{user}/{repo}", format("ok")))

            for pr in PRs:
                self.processPR(pr, labels, delete)
        except:
            click.echo("{} {} - {}".format(format("repo"),
                                           F"{user}/{repo}", format("fail")))


    def getPR(self, user, repo, state, base):
        """Get PRs for given repo
        
        :param user: Repo's owner
        :type user: string
        :param repo: Repo name
        :type repo: string
        :param state: Filter PR state (open|close|all)
        :type state: string
        :param base: Filter by base name
        :type base: string or none
        :raises Exception: PRs get failed
        """

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

    def processPR(self, pr, labels, delete):
        """Set correct labels for PR
        
        :param pr: PR
        :type pr: PR object
        :param labels: Labels
        :type labels: dict
        :param delete: Delete if additional label exist
        :type delete: bool
        """
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

    
    def updateLabels(self, pr, labels):
        """Set labels for PR
        
        :param pr: PR
        :type pr: PR object
        :param labels: labels
        :type labels: list
        :raises Exception: Settings failed
        """
        data = list(labels)
        url = F"{pr['issue_url']}/labels"
        response = self.session.put(url, json=data)
        if not response.ok:
            raise Exception("Update labels failed")

    def getPRFiles(self, pr):
        """Async Get All Files for PR
        
        :param pr: PR
        :type pr: PR object
        :raises Exception: Get Failed
        :return: Files objects
        :rtype: list
        """
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