#!/usr/bin/python
import webbrowser
from time import time
import pickle
import click
import subprocess

from fsnavigator_map import FsNavigatorMap
from route_finder import RouteFinder

def get_map():
    try:
        with open('.map', 'rb') as file:
            return pickle.load(file)
    except TypeError:
        return FsNavigatorMap()

@click.group()
def cli():
    pass

@cli.command()
def build():
    stats = time()
    map = FsNavigatorMap()
    stats = time() - stats
    click.echo(f'Route map built in {stats:.1f}s.')
    with open('.map', 'wb') as file:
        pickle.dump(map, file)

@cli.command()
@click.argument('name')
def node(name):
    map = get_map()
    node = map.nodes[name]
    click.echo(f'{node.name} {node.x},{node.y}')

@cli.command()
@click.argument('name')
def neighbours(name):
    map = get_map()
    node = map.nodes[name]
    click.echo(node)
    for _, neighbour in map.neighbours[node]:
        click.echo(f'{neighbour.name} {neighbour.x},{neighbour.y} {neighbour.via}')

@cli.command()
@click.argument('start')
@click.argument('end')
@click.option('--open/--no-open', '-o/-no', default=False)
def route(start, end, open):
    map = get_map()

    start = map.nodes[start]
    end = map.nodes[end]
    route = RouteFinder(map=map, start=start, end=end)

    stats = time()
    route.find()
    stats = time() - stats
    click.echo(f'Found route in {stats:.1f}s.')
    click.echo(f'ROUTE: {route.atc_route}')
    webbrowser.open(f'https://skyvector.com/?fpl={route.atc_route}')

@cli.command()
@click.option('--host', '-h', default='0.0.0.0', help='The address the web app will listen in.')
@click.option('--port', '-p', default=5000, help='The TCP port to listen to')
@click.option('--debug', '-d', default=False, is_flag=True, help='Set enviroment mode')
def run(host, port, debug):
    """Runs a development web server."""
    if debug:
        from flask_web import app
        app.run(host=host, port=port, debug=debug)
    else:
        bind = '%s:%s' % (host, port)
        subprocess.call(['gunicorn', 'flask_web:app', '--bind', bind, '--log-file=-'])

        
if __name__ == '__main__':
    cli()
