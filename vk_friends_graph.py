from requests import get
from matplotlib.pyplot import axis, savefig, show
from networkx import Graph, draw_networkx_nodes, draw_networkx_labels, draw_networkx_edges, circular_layout, \
    spring_layout, spectral_layout, random_layout, shell_layout, write_edgelist
from time import sleep
from os import listdir, mkdir
from random import randint
from argparse import ArgumentParser

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


def graph_builder(graph, account_id, depth=1, delay=float(0), fr_only=False, inscription='', enrich_inscription=True):
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


def main():
    parser = ArgumentParser(description='VK Friend Graph Builder')

    parser.add_argument('user_id',
                        metavar='USER_ID',
                        type=int,
                        nargs=1,
                        help='VK Id of the person of interest')

    parser.add_argument('-d', '--dep', type=int, action='store', nargs='?', default=2,
                        help='Depth of search. ATTENTION!!! If you choose a depth of search greater than 1, '
                             'be ready to face a lack of RAM.')
    parser.add_argument('-s', '--slp', type=float, action='store', nargs='?', default=0.0,
                        help='Time delay in seconds in range from 0 to 10 (if larger, it is interpreted as 10). '
                             'Default is 0. If you have a very fast Internet connection, '
                             'please, input nonzero delay. Otherwise antiDoS system may reject you.')
    parser.add_argument('-a', '--alg', type=int, action='store', nargs='?', default=1,
                        help='Drawing algorithms: 0 - circular, 1 - spring, 2 - spectral, 3 - random, 4 - shell. Other '
                             'and default is spring.')
    parser.add_argument('-m', '--mod', type=int, action='store', nargs='?', default=1,
                        help='Operating mode: 1 - At the last step of the recursion program adds edges to the graph '
                             'only between already included vertexes; any other - At the last step of the recursion '
                             'program adds all incoming edges to the graph.')

    args = parser.parse_args()

    my_graph = Graph()
    graph_builder(my_graph, args.user_id[0], args.dep, args.slp, True if args.mod == 1 else False)

    print('\nPlease, wait. Calculating space configuration of vertexes…')
    if args.alg == 1:
        positions = spring_layout(my_graph)
    elif args.alg == 0:
        positions = circular_layout(my_graph)
    elif args.alg == 2:
        positions = spectral_layout(my_graph)
    elif args.alg == 3:
        positions = random_layout(my_graph)
    elif args.alg == 4:
        positions = shell_layout(my_graph)
    else:
        positions = spring_layout(my_graph)

    print('Full number of accounts involved:', my_graph.number_of_nodes())
    print('Drawing a graph…')
    draw_networkx_nodes(my_graph, positions, node_shape='s', node_size=40, node_color='y')
    draw_networkx_labels(my_graph, positions, font_size=1, font_family='sans-serif', font_color='r')
    draw_networkx_edges(my_graph, positions, edgelist=my_graph.edges(), width=0.1)

    try:
        mkdir('images')
    except OSError:
        pass

    fig_name, dir_files = '', set(listdir('images'))
    while not fig_name:
        variant = str(randint(1000000, 9999999))
        if variant not in dir_files:
            fig_name = 'id' + str(args.user_id[0]) + '_dep' + str(args.dep) + '_mod' + str(args.mod) + '_img' + variant
    axis('off')
    savefig('images/' + fig_name + '.pdf', format='pdf')

    with open('images/' + fig_name + '.data', 'wb') as out:
        write_edgelist(my_graph, out, encoding='ascii', data=False)

    print('The image was saved as', fig_name)
    show()


if __name__ == '__main__':
    main()
