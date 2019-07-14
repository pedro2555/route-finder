from time import time
import pickle
from flask import Flask, redirect, render_template, request

from fsnavigator_map import FsNavigatorMap
from route_finder import RouteFinder

def get_map():
    try:
        with open('.map', 'rb') as file:
            return pickle.load(file)
    except TypeError:
        return FsNavigatorMap()

def build():
    stats = time()
    map = FsNavigatorMap()
    stats = time() - stats
    return f'Route map built in {stats:.1f}s.'
    with open('.map', 'wb') as file:
        pickle.dump(map, file)

def route(start, end, open):
    map = get_map()

    start = map.nodes[start]
    end = map.nodes[end]
    route = RouteFinder(map=map, start=start, end=end)

    stats = time()
    route.find()
    stats = time() - stats
    output = [f'Found route in {stats:.1f}s.', f'ROUTE: {route.atc_route}']
    return "\n".join(output)

app = Flask(__name__, template_folder='flask_web')
build()


@app.route("/", methods=['GET'])
def home():
        return redirect("get_route_infos")

@app.route("/get_route_infos", methods=['GET'])
def get_route_infos():
        return render_template("get_route_infos.html")

@app.route("/generate_route", methods=['GET'])
def generate_route():
        start = request.args.get('Departure').upper()
        end =  request.args.get('Arrival').upper()
        get_map()
        return route(start, end, False)
