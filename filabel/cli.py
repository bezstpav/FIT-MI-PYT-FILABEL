import click
import os
import configparser
import sys
import asyncio
from .github import GitHub

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
@click.option('-x', '--async', 'asyncFlag',  is_flag=True, help='Use asynchronnous (faster) logic.')
@click.argument('reposlugs', nargs=-1)
def main(state, delete, branch, auth, label, asyncFlag, reposlugs):
    """CLI tool for filename-pattern-based labeling of GitHub PRs"""
    reposlug = parseReposlugs(reposlugs)

    token = loadAuth(auth.name)
    labels = loadLabels(label.name)
    
    async def task():
        github = GitHub(token)
        futures=[]
        for item in reposlug:
            future = asyncio.ensure_future(github.processRepo(item[0], item[1], state, branch, labels, delete))
            futures.append(future)

        for item in futures:
            click.echo(await item)

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(task())
    loop.close()
