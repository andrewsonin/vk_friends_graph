import requests
import matplotlib.pyplot as plt
import networkx as nx
from time import sleep
print('This program is designed to build a graph of the friendship relations between users of social network VK.\n')


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
    if depth == 1:
        return
    if enrich_inscription:
        inscription = str(len(graph.nodes()))
    iterator = 1
    for friend_id in graph.nodes()[1:]:
        iteration = str(iterator) + '/' + inscription
        print('Iteration:', iteration)
        graph_builder(graph, friend_id, depth - 1, delay, iteration, False)
        iterator += 1

HOST = 'https://api.vk.com/method/'
VERSION = '5.62'

print('Please, input ID of some VK user:')
my_id = int(input())

print('\nPlease, input a depth of search.\nATTENTION!!! If you choose a depth of search greater than 1, be ready '
      'to face a lack of RAM.')
my_depth = int(input())
if my_depth < 1:
    my_depth = 1
    print('Invalid value. The depth was changed to 1.')

print('\nPlease, input a time delay in seconds.\nIf you have a very fast computer, please, input nonzero delay. '
      'Otherwise antiDoS system may reject you.')
my_delay = float(input())

drawing_ways = ['circular', 'spring', 'spectral', 'random', 'shell']
string = [str(i) + ' - ' + str(drawing_ways[i]) for i in range(len(drawing_ways))]
print('\nChoose one of the drawing algorithms:')
print(*string, sep=', ')
drawing_way = int(input())
if not drawing_way in range(len(drawing_ways)):
    drawing_way = 0
    print('Invalid value. The algorithm was changed to 0.')

my_graph = nx.Graph()
graph_builder(my_graph, my_id, my_depth, my_delay)

print('\nCalculating space configuration of vertexes…')
positions = eval('nx.' + drawing_ways[drawing_way] + '_layout(my_graph)')
edges = [element for element in my_graph.edges(data=True)]

print('Full number of accounts involved:', len(my_graph.nodes()))
print('Drawing a graph…')
nx.draw_networkx_nodes(my_graph, positions, node_shape='s', node_size=500, node_color='y')
nx.draw_networkx_labels(my_graph, positions, font_size=4, font_family='sans-serif', font_color='r')
nx.draw_networkx_edges(my_graph, positions, edgelist=edges, width=1)

plt.axis('off')
plt.savefig('friends_graph.png')
print('The image was saved as friends_graph.png')
plt.show()
