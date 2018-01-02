from time import sleep
from requests import get
from os.path import dirname
from networkx import Graph
import sys

HOST = 'https://api.vk.com/method/'
VERSION = '5.69'


def get_friends_dict(user_id=1):
    return get(HOST + 'friends.get', params={'user_id': user_id, 'fields': 'first_name', 'v': VERSION}).json()


def add_account_to_graph(graph, account_id, fr_only=False):
    friends = get_friends_dict(account_id).get('response', {}).get('items', [])
    if fr_only:
        for friend in friends:
            if friend['id'] in graph.nodes():
                graph.add_edge(account_id, friend['id'])
    else:
        for friend in friends:
            graph.add_edge(account_id, friend['id'])


def graph_builder(graph, account_id, depth=1, delay=0.0, fr_only=False, inscription='', enrich_inscription=True):
    sleep(delay)
    if depth != 1:
        add_account_to_graph(graph, account_id)
        if enrich_inscription:
            inscription = str(len(graph.nodes()) - 1)
        for iter_num, friend_id in enumerate(list(graph.nodes())[1:], 1):
            iteration = str(iter_num) + '/' + inscription
            print('Iteration:', iteration)
            graph_builder(graph, friend_id, depth - 1, delay, fr_only, iteration, False)
    else:
        add_account_to_graph(graph, account_id, fr_only)
    return graph


def edge_intersection(graph1, graph2):
    graph = Graph()
    graph.add_edges_from([edge for edge in min(graph1, graph2, key=lambda graph: graph.number_of_edges()).edges
                          if edge in max(graph1, graph2, key=lambda graph: graph.number_of_edges()).edges])
    return graph


def module_path():
    if hasattr(sys, 'frozen'):
        return dirname(sys.executable)
    return dirname(__file__)
