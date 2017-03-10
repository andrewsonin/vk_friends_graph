import requests
import matplotlib.pyplot as plt
import networkx as nx
from time import sleep
print('This program is designed to build a graph of the friendship relations between users of social network VK.\n'
      'ATTENTION!!! If you choose a depth of search greater than 1, be ready to face a lack of RAM.\n'
      'If you have a very fast computer, please, input nonzero delay. Otherwise antiDoS system may reject you.\n')


def get_friends_dict(user_id=1):
    return requests.get(HOST + 'friends.get', params={'user_id': user_id, 'fields': 'first_name', 'v': VERSION}).json()


def add_account_to_graph(graph, id):
    try:
        for friend in get_friends_dict(id)['response']['items']:
            graph.add_edge(id, friend['id'])
    except KeyError:
        pass


def graph_builder(graph, id, depth=1, delay=float(0), inscription='', enrich_inscription=True):
    add_account_to_graph(graph, id)
    sleep(delay)
    if enrich_inscription:
        inscription = str(len(graph.nodes()))
    if depth == 1:
        return
    iterator = 1
    for friend_id in graph.nodes():
        iteration = str(iterator) + '/' + inscription
        print('Iteration:', iteration)
        graph_builder(graph, friend_id, depth - 1, delay, iteration, False)
        iterator += 1


HOST = 'https://api.vk.com/method/'
VERSION = '5.62'

print('Please, input ID of some VK user:')
my_id = int(input())
print('Please, input a depth of search:')
my_depth = int(input())
if my_depth < 1:
    my_depth = 1
    print('Invalid value. The depth was changed to 1.')
print('Please, input a time delay in seconds:')
my_delay = float(input())

my_graph = nx.Graph()
graph_builder(my_graph, my_id, my_depth, my_delay)

print('Calculating space configuration of vertexes…')
positions = nx.spring_layout(my_graph)
edges = [element for element in my_graph.edges(data=True)]

print('Drawing a graph…')
nx.draw_networkx_nodes(my_graph, positions, node_shape='s', node_size=500, node_color='y')
nx.draw_networkx_labels(my_graph, positions, font_size=4, font_family='sans-serif', font_color='r')
nx.draw_networkx_edges(my_graph, positions, edgelist=edges, width=1)

plt.axis('off')
plt.savefig('friends_graph.png')
plt.show()
