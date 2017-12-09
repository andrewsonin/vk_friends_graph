from requests import get
from matplotlib.pyplot import axis, savefig, show
from networkx import *
from time import sleep
from os import listdir
from random import randint
HOST = 'https://api.vk.com/method/'
VERSION = '5.62'


def get_friends_dict(user_id=1):
    return get(HOST + 'friends.get', params={'user_id': user_id, 'fields': 'first_name', 'v': VERSION}).json()


def add_account_to_graph(graph, account_id, fr_only=False):
    try:
        if fr_only:
            for friend in get_friends_dict(account_id)['response']['items']:
                if friend['id'] in graph.nodes():
                    graph.add_edge(account_id, friend['id'])
        else:
            for friend in get_friends_dict(account_id)['response']['items']:
                graph.add_edge(account_id, friend['id'])
    except KeyError:
        pass


def graph_builder(graph, account_id, depth=1, delay=float(0), fr_only=False, inscription='', enrich_inscription=True):
    sleep(delay)
    if depth == 1:
        add_account_to_graph(graph, account_id, fr_only)
        return None
    else:
        add_account_to_graph(graph, account_id)
    if enrich_inscription:
        inscription = str(len(graph.nodes()) - 1)
    iterator = 1
    for friend_id in list(graph.nodes())[1:]:
        iteration = str(iterator) + '/' + inscription
        print('Iteration:', iteration)
        graph_builder(graph, friend_id, depth - 1, delay, fr_only, iteration, False)
        iterator += 1

print('This program is designed to build a graph of the friendship relations between users of social network VK.\n'
      'Please, input ID of some VK user:')
my_id = int(input())

print('\nPlease, input a depth of search.\nATTENTION!!! If you choose a depth of search greater than 1, be ready '
      'to face a lack of RAM.')
my_depth = int(input())
if my_depth < 1:
    my_depth = 1
    print('Invalid value. The depth was changed to 1.')

print('\nPlease, input a time delay in seconds in range from 0 to 10.\nIf you have a very fast computer, please, input '
      'nonzero delay. Otherwise antiDoS system may reject you.')
my_delay = float(input())
if not 0 <= my_delay <= 10:
    my_delay = 0.3
    print('Invalid value. Time delay was changed to 0.3 second.')

drawing_ways = ['circular', 'spring', 'spectral', 'random', 'shell']
string = [str(i) + ' - ' + str(drawing_ways[i]) for i in range(len(drawing_ways))]
print('\nChoose one of the drawing algorithms:')
print(*string, sep=', ')
drawing_way = int(input())
if drawing_way not in range(len(drawing_ways)):
    drawing_way = 0
    print('Invalid value. The algorithm was changed to 0.')

print('\nPlease, choose operating mode:')
print('1 - At the last step of the recursion program will add edges to graph only between already included vertexes;'
      '\nany other - At the last step of the recursion program will add to graph all incoming edges.')
friends_only = (lambda x: True if x == '1' else False)(input())

my_graph = Graph()
graph_builder(my_graph, my_id, my_depth, my_delay, friends_only)

print('\nCalculating space configuration of vertexes…')
positions = eval(drawing_ways[drawing_way] + '_layout(my_graph)')

print('Full number of accounts involved:', len(my_graph.nodes()))
print('Drawing a graph…')
draw_networkx_nodes(my_graph, positions, node_shape='s', node_size=500, node_color='y')
draw_networkx_labels(my_graph, positions, font_size=4, font_family='sans-serif', font_color='r')
draw_networkx_edges(my_graph, positions, edgelist=my_graph.edges(), width=1)

axis('off')
fig_name, dir_files = '', set(listdir('.'))
while not fig_name:
    variant = str(randint(1000000, 9999999)) + '.png'
    if variant not in dir_files:
        fig_name = variant
savefig(fig_name)
print('The image was saved as', fig_name)
show()
