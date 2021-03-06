from matplotlib.pyplot import axis, savefig, show
from networkx import draw_networkx_nodes, draw_networkx_labels, draw_networkx_edges, circular_layout, spring_layout, \
    spectral_layout, random_layout, shell_layout, write_edgelist
from os import listdir, mkdir
from random import randint
from argparse import ArgumentParser
from functions import *


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
    parser.add_argument('-i', '--int', action='store_true',
                        help='If true, program calculates edge intersection between graphs of the first and the second '
                             'persons.')
    parser.add_argument('-n', '--id2', type=int, action='store', nargs='?',
                        help='VK Id of the second person of interest.')
    parser.add_argument('-m', '--mod', type=int, action='store', nargs='?', default=1,
                        help='Operating mode: 1 - At the last step of the recursion program adds edges to the graph '
                             'only between already included vertexes; any other - At the last step of the recursion '
                             'program adds all incoming edges to the graph.')

    args = parser.parse_args()
    mod = True if args.mod == 1 else False

    if args.int:
        if args.id2 is None:
            print('Error: ID2 field was not defined, while INT was declared. Use -h to help.')
            raise AssertionError
        my_graph = edge_intersection(graph_builder(Graph(), args.user_id[0], args.dep, args.slp, mod),
                                     graph_builder(Graph(), args.id2, args.dep, args.slp, mod))
    else:
        my_graph = graph_builder(Graph(), args.user_id[0], args.dep, args.slp, mod)

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

    path = module_path() + '/images/'

    try:
        mkdir(path)
    except OSError:
        pass

    fig_name, dir_files = '', set(listdir(path))
    while not fig_name:
        variant = '_img' + str(randint(1000000, 9999999))
        for file_name in dir_files:
            if variant in file_name:
                break
        else:
            fig_name = 'id' + str(args.user_id[0]) + ('intersect' + str(args.id2) if args.int else '') \
                       + '_dep' + str(args.dep) + '_mod' + str(args.mod) + variant
    axis('off')
    savefig(path + fig_name + '.pdf', format='pdf')

    with open(path + fig_name + '.data', 'wb') as out:
        write_edgelist(my_graph, out, encoding='ascii', data=False)

    print('The image was saved as', fig_name)
    show()


if __name__ == '__main__':
    main()
