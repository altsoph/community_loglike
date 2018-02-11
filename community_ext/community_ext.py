# -*- coding: utf-8 -*-
"""
This package implements several community detection.

Originally based on community aka python-louvain library from Thomas Aynaud
(https://github.com/taynaud/python-louvain)
"""
from __future__ import print_function

import array
import random
from math import exp, log, sqrt
from collections import defaultdict
from collections import Counter

import networkx as nx

from .community_status import Status

__author__ = """Aleksey Tikhonov (altsoph@gmail.com)"""
__author__ = """Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)"""
#    Copyright (C) 2018 by
#    Aleksey Tikhonov (altsoph@gmail.com>
#    Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)
#    All rights reserved.
#    BSD license.

__PASS_MAX = -1
__MIN = 0.0000001


def partition_at_level(dendrogram, level):
    """Return the partition of the nodes at the given level

    A dendrogram is a tree and each level is a partition of the graph nodes.
    Level 0 is the first partition, which contains the smallest communities,
    and the best is len(dendrogram) - 1.
    The higher the level is, the bigger are the communities

    Parameters
    ----------
    dendrogram : list of dict
       a list of partitions, ie dictionnaries where keys of the i+1 are the
       values of the i.
    level : int
       the level which belongs to [0..len(dendrogram)-1]

    Returns
    -------
    partition : dictionnary
       A dictionary where keys are the nodes and the values are the set it
       belongs to

    Raises
    ------
    KeyError
       If the dendrogram is not well formed or the level is too high

    See Also
    --------
    best_partition which directly combines partition_at_level and
    generate_dendrogram to obtain the partition of highest modularity

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> dendrogram = generate_dendrogram(G)
    >>> for level in range(len(dendrogram) - 1) :
    >>>     print("partition at level", level, "is", partition_at_level(dendrogram, level))  # NOQA
    """
    partition = dendrogram[0].copy()
    for index in range(1, level + 1):
        for node, community in partition.items():
            partition[node] = dendrogram[index][community]
    return partition


def modularity(partition, graph, weight='weight',gamma = 1.):
    """Compute the modularity of a partition of a graph

    Parameters
    ----------
    partition : dict
       the partition of the nodes, i.e a dictionary where keys are their nodes
       and values the communities
    graph : networkx.Graph
       the networkx graph which is decomposed
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'


    Returns
    -------
    modularity : float
       The modularity

    Raises
    ------
    KeyError
       If the partition is not a partition of all graph nodes
    ValueError
        If the graph has no link
    TypeError
        If graph is not a networkx.Graph

    References
    ----------
    .. 1. Newman, M.E.J. & Girvan, M. Finding and evaluating community
    structure in networks. Physical Review E 69, 26113(2004).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)
    >>> modularity(part, G)
    """
    if graph.is_directed():
        raise TypeError("Bad graph type, use only non directed graph")

    inc = dict([])
    deg = dict([])
    links = graph.size(weight=weight)
    if links == 0:
        raise ValueError("A graph without link has an undefined modularity")

    for node in graph:
        com = partition[node]
        deg[com] = deg.get(com, 0.) + graph.degree(node, weight=weight)
        for neighbor, datas in graph[node].items():
            edge_weight = datas.get(weight, 1)
            if partition[neighbor] == com:
                if neighbor == node:
                    inc[com] = inc.get(com, 0.) + float(edge_weight)
                else:
                    inc[com] = inc.get(com, 0.) + float(edge_weight) / 2.

    res = 0.
    for com in set(partition.values()):
        res += (inc.get(com, 0.) / links) - \
               gamma * (deg.get(com, 0.) / (2. * links)) ** 2
    return res


def best_partition(graph, partition=None,
                   weight='weight', resolution=1., randomize=False, model='ppm', pars = None):
    assert model in ('dcppm','ppm','ilfr','ilfrs'), "Unknown model specified"
    """Compute the partition of the graph nodes which maximises the modularity
    (or try..) using the Louvain heuristices

    This is the partition of highest modularity, i.e. the highest partition
    of the dendrogram generated by the Louvain algorithm.

    Parameters
    ----------
    graph : networkx.Graph
       the networkx graph which is decomposed
    partition : dict, optional
       the algorithm will start using this partition of the nodes.
       It's a dictionary where keys are their nodes and values the communities
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'
    resolution :  double, optional
        Will change the size of the communities, default to 1.
        represents the time described in
        "Laplacian Dynamics and Multiscale Modular Structure in Networks",
        R. Lambiotte, J.-C. Delvenne, M. Barahona
    randomize :  boolean, optional
        Will randomize the node evaluation order and the community evaluation
        order to get different partitions at each call

    Returns
    -------
    partition : dictionnary
       The partition, with communities numbered from 0 to number of communities

    Raises
    ------
    NetworkXError
       If the graph is not Eulerian.

    See Also
    --------
    generate_dendrogram to obtain all the decompositions levels

    Notes
    -----
    Uses Louvain algorithm

    References
    ----------
    .. 1. Blondel, V.D. et al. Fast unfolding of communities in
    large networks. J. Stat. Mech 10008, 1-12(2008).

    Examples
    --------
    >>>  #Basic usage
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)

    >>> #other example to display a graph with its community :
    >>> #better with karate_graph() as defined in networkx examples
    >>> #erdos renyi don't have true community structure
    >>> G = nx.erdos_renyi_graph(30, 0.05)
    >>> #first compute the best partition
    >>> partition = community.best_partition(G)
    >>>  #drawing
    >>> size = float(len(set(partition.values())))
    >>> pos = nx.spring_layout(G)
    >>> count = 0.
    >>> for com in set(partition.values()) :
    >>>     count += 1.
    >>>     list_nodes = [nodes for nodes in partition.keys()
    >>>                                 if partition[nodes] == com]
    >>>     nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                    node_color = str(count / size))
    >>> nx.draw_networkx_edges(G, pos, alpha=0.5)
    >>> plt.show()
    """
    dendo = generate_dendrogram(graph,
                                partition,
                                weight,
                                resolution,
                                randomize,
                                model=model,
                                pars=pars)
    return partition_at_level(dendo, len(dendo) - 1)


def generate_dendrogram(graph,
                        part_init=None,
                        weight='weight',
                        resolution=1.,
                        randomize=False,
                        model='ppm',
                        pars = None):
    """Find communities in the graph and return the associated dendrogram

    A dendrogram is a tree and each level is a partition of the graph nodes.
    Level 0 is the first partition, which contains the smallest communities,
    and the best is len(dendrogram) - 1. The higher the level is, the bigger
    are the communities


    Parameters
    ----------
    graph : networkx.Graph
        the networkx graph which will be decomposed
    part_init : dict, optional
        the algorithm will start using this partition of the nodes. It's a
        dictionary where keys are their nodes and values the communities
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'
    resolution :  double, optional
        Will change the size of the communities, default to 1.
        represents the time described in
        "Laplacian Dynamics and Multiscale Modular Structure in Networks",
        R. Lambiotte, J.-C. Delvenne, M. Barahona

    Returns
    -------
    dendrogram : list of dictionaries
        a list of partitions, ie dictionnaries where keys of the i+1 are the
        values of the i. and where keys of the first are the nodes of graph

    Raises
    ------
    TypeError
        If the graph is not a networkx.Graph

    See Also
    --------
    best_partition

    Notes
    -----
    Uses Louvain algorithm

    References
    ----------
    .. 1. Blondel, V.D. et al. Fast unfolding of communities in large
    networks. J. Stat. Mech 10008, 1-12(2008).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> dendo = generate_dendrogram(G)
    >>> for level in range(len(dendo) - 1) :
    >>>     print("partition at level", level,
    >>>           "is", partition_at_level(dendo, level))
    :param weight:
    :type weight:
    """
    if graph.is_directed():
        raise TypeError("Bad graph type, use only non directed graph")

    # special case, when there is no link
    # the best partition is everyone in its community
    if graph.number_of_edges() == 0:
        part = dict([])
        for node in graph.nodes():
            part[node] = node
        return [part]

    current_graph = graph.copy()
    status = Status()
    status.init(current_graph, weight, part_init)
    status_list = list()
    __one_level(current_graph, status, weight, resolution, randomize, model=model, pars=pars)
    new_mod = __modularity(status,model=model,pars=pars)
    partition = __renumber(status.node2com)
    status_list.append(partition)
    mod = new_mod
    current_graph = induced_graph(partition, current_graph, weight)

    status.init(current_graph, weight, raw_partition = __transit(partition,status.rawnode2node), raw_graph=graph)

    while True:
        __one_level(current_graph, status, weight, resolution, randomize, model=model, pars=pars)
        new_mod = __modularity(status,model=model,pars=pars)
        if new_mod - mod < __MIN:
            break
        partition = __renumber(status.node2com)
        status_list.append(partition)
        mod = new_mod
        current_graph = induced_graph(partition, current_graph, weight)

        status.init(current_graph, weight, raw_partition = __transit(partition,status.rawnode2node), raw_graph=graph)
    return status_list[:]


def induced_graph(partition, graph, weight="weight"):
    """Produce the graph where nodes are the communities

    there is a link of weight w between communities if the sum of the weights
    of the links between their elements is w

    Parameters
    ----------
    partition : dict
       a dictionary where keys are graph nodes and  values the part the node
       belongs to
    graph : networkx.Graph
        the initial graph
    weight : str, optional
        the key in graph to use as weight. Default to 'weight'


    Returns
    -------
    g : networkx.Graph
       a networkx graph where nodes are the parts

    Examples
    --------
    >>> n = 5
    >>> g = nx.complete_graph(2*n)
    >>> part = dict([])
    >>> for node in g.nodes() :
    >>>     part[node] = node % 2
    >>> ind = induced_graph(part, g)
    >>> goal = nx.Graph()
    >>> goal.add_weighted_edges_from([(0,1,n*n),(0,0,n*(n-1)/2), (1, 1, n*(n-1)/2)])  # NOQA
    >>> nx.is_isomorphic(int, goal)
    True
    """
    ret = nx.Graph()
    ret.add_nodes_from(partition.values())

    for node1, node2, datas in graph.edges_iter(data=True):
        edge_weight = datas.get(weight, 1)
        com1 = partition[node1]
        com2 = partition[node2]
        w_prec = ret.get_edge_data(com1, com2, {weight: 0}).get(weight, 1)
        ret.add_edge(com1, com2, attr_dict={weight: w_prec + edge_weight})

    return ret


def __renumber(dictionary):
    """Renumber the values of the dictionary from 0 to n
    """
    count = 0
    ret = dictionary.copy()
    new_values = dict([])

    for key in dictionary.keys():
        value = dictionary[key]
        new_value = new_values.get(value, -1)
        if new_value == -1:
            new_values[value] = count
            new_value = count
            count += 1
        ret[key] = new_value

    return ret

def __transit(partition,rawnodepart):
    res = dict()
    for n,mn in rawnodepart.items():
        res[n] = partition[mn]
    return res


def load_binary(data):
    """Load binary graph as used by the cpp implementation of this algorithm
    """
    data = open(data, "rb")

    reader = array.array("I")
    reader.fromfile(data, 1)
    num_nodes = reader.pop()
    reader = array.array("I")
    reader.fromfile(data, num_nodes)
    cum_deg = reader.tolist()
    num_links = reader.pop()
    reader = array.array("I")
    reader.fromfile(data, num_links)
    links = reader.tolist()
    graph = nx.Graph()
    graph.add_nodes_from(range(num_nodes))
    prec_deg = 0

    for index in range(num_nodes):
        last_deg = cum_deg[index]
        neighbors = links[prec_deg:last_deg]
        graph.add_edges_from([(index, int(neigh)) for neigh in neighbors])
        prec_deg = last_deg

    return graph


def __randomly(seq, randomize):
    """ Convert sequence or iterable to an iterable in random order if
    randomize """
    if randomize:
        shuffled = list(seq)
        random.shuffle(shuffled)
        return iter(shuffled)
    return seq


def __get_safe_par(model,pars=None):
    if not pars: 
        par = 1.-__MIN
    else:
        if model in ('ilfrs','ilfr'):
            try:
                par = pars.get('mu',1.)
            except:
                par = 1.
            par = max(par,__MIN)
            par = min(par,1.-__MIN)
        elif model in ('dcppm','ppm'):
            try:
                par = pars.get('gamma',1.)
            except:
                par = 1.
            par = max(par,__MIN)
    return par

def __one_level(graph, status, weight_key, resolution, randomize, model='ppm', pars = None):
    """Compute one level of communities
    """
    modified = True
    nb_pass_done = 0
    cur_mod = __modularity(status,model=model,pars=pars)
    new_mod = cur_mod
    par = __get_safe_par(model,pars)
    __E = float(status.total_weight)
    __2E = 2.*__E
    mpar = 1.-par
    __l2E = 0.
    __l2Epar = 0.
    __l2Epar2 = 0.
    if __E>0:
        __l2E = log(__2E)
        if mpar>0.:
            __l2Epar = log(__2E*mpar/par)
    if mpar>0.:
        __l2Epar2 = (log(par/mpar)-__l2E)
    __lpar = log(par)
    __l2Epar3 = (__lpar-__l2E)
    __par2E = par/__2E
    P2 = len(status.rawnode2node)
    P2 = P2*(P2-1)/2.
    while modified and nb_pass_done != __PASS_MAX:
        cur_mod = new_mod
        modified = False
        nb_pass_done += 1
        for node in __randomly(graph.nodes(), randomize):
            com_node = status.node2com[node]
            neigh_communities = __neighcom(node, graph, status, weight_key)
            v_in_degree = neigh_communities.get(com_node,0)

            if model=='dcppm':
                com_degree = status.degrees.get(com_node, 0.)
                v_degree = status.gdegrees.get(node, 0.)
                pre_calc1 = par * v_degree / __2E
                remove_cost = pre_calc1 * (com_degree - v_degree) - v_in_degree
            elif model == 'ilfrs':
                com_degree = status.degrees.get(com_node, 0.)
                v_degree = status.gdegrees.get(node, 0.)
                v_loops  = graph.get_edge_data(node, node, default={weight_key: 0}).get(weight_key, 1)
                com_in_degree = status.internals.get(com_node, 0.)
                remove_cost = v_in_degree*__l2Epar2
                remove_cost += com_in_degree * log(com_degree)
                if com_degree > v_degree: remove_cost -= (com_in_degree - v_loops - v_in_degree) * log(com_degree - v_degree)
            elif model == 'ilfr':
                com_degree = status.degrees.get(com_node, 0.)
                v_degree = status.gdegrees.get(node, 0.)
                v_loops  = graph.get_edge_data(node, node, default={weight_key: 0}).get(weight_key, 1)
                com_in_degree = status.internals.get(com_node, 0.)
                remove_cost = v_in_degree*__l2Epar3
                if com_degree >0: remove_cost -= com_in_degree*log((mpar/com_degree)+__par2E)
                if com_degree-v_degree>0: remove_cost += (com_in_degree-v_in_degree-v_loops)*log((mpar/(com_degree-v_degree))+__par2E)
            else:
                volume_node = status.node2size[node]
                volume_cluster = status.com2size[com_node] - volume_node
                pre_calc1 = par*volume_node/P2
                remove_cost = volume_cluster*pre_calc1 - v_in_degree/__E 
            __remove(node, com_node,
                     neigh_communities.get(com_node, 0.), status)

            best_com = com_node
            best_increase = 0.

            for com, dnc in __randomly(neigh_communities.items(),
                                       randomize):
                if model=='dcppm':
                    com_degree = status.degrees.get(com, 0.)
                    add_cost = dnc - pre_calc1 * com_degree
                elif model == 'ilfrs':
                    com_in_degree = status.internals.get(com, 0.)
                    com_degree = status.degrees.get(com, 0.)
                    add_cost = dnc*__l2Epar
                    add_cost += com_in_degree*log(com_degree)
                    add_cost -= (com_in_degree + v_loops + dnc) * log(com_degree + v_degree)
                elif model == 'ilfr':
                    com_in_degree = status.internals.get(com, 0.)
                    com_degree = status.degrees.get(com, 0.)
                    add_cost = dnc*(__l2E-__lpar)
                    if com_degree >0: add_cost -= com_in_degree*log((mpar/com_degree)+__par2E)
                    if com_degree+v_degree>0: add_cost += (com_in_degree+dnc+v_loops)*log((mpar/(com_degree+v_degree))+__par2E)
                else:
                    volume_cluster = status.com2size[com]
                    add_cost = dnc/__E - volume_cluster*pre_calc1

                incr = add_cost + remove_cost
                
                if incr > best_increase:
                    best_increase = incr
                    best_com = com

            __insert(node, best_com,
                     neigh_communities.get(best_com, 0.), status)

            if best_com != com_node:
                modified = True
        if modified:
            new_mod = __modularity(status,model=model,pars=pars)
            if new_mod - cur_mod < __MIN:
                break

def __neighcom(node, graph, status, weight_key):
    """
    Compute the communities in the neighborhood of node in the graph given
    with the decomposition node2com
    """
    weights = {}
    for neighbor, datas in graph[node].items():
        if neighbor != node:
            edge_weight = datas.get(weight_key, 1)
            neighborcom = status.node2com[neighbor]
            weights[neighborcom] = weights.get(neighborcom, 0) + edge_weight

    return weights


def __remove(node, com, weight, status):
    """ Remove node from community com and modify status"""
    status.degrees[com] = (status.degrees.get(com, 0.)
                           - status.gdegrees.get(node, 0.))
    status.degrees[-1] = status.degrees.get(-1, 0.)+status.gdegrees.get(node, 0.)

    status.internals[com] = float(status.internals.get(com, 0.) -
                                  weight - status.loops.get(node, 0.))
    status.node2com[node] = -1
    status.internals[-1] = status.loops.get(node, 0.)
    status.com2size[com] -= status.node2size[node]

def __insert(node, com, weight, status):
    """ Insert node into community and modify status"""
    status.node2com[node] = com
    status.degrees[-1] = status.degrees.get(-1, 0.)-status.gdegrees.get(node, 0.)
    status.degrees[com] = (status.degrees.get(com, 0.) +
                           status.gdegrees.get(node, 0.))
    status.internals[com] = float(status.internals.get(com, 0.) +
                                  weight + status.loops.get(node, 0.))
    status.com2size[com] += status.node2size[node]


def __get_DLD(status):
    return sum(map(lambda x:x*log(x),filter(lambda x:x>0,status.rawnode2degree.values())))

def __get_es(status):
    E = float(status.total_weight)
    Ein = 0
    degrees_squared = 0.
    for community in set(status.node2com.values()):
        Ein += status.internals.get(community, 0.)
        tmp = status.degrees.get(community, 0.)
        degrees_squared += tmp*tmp #status.degrees.get(community, 0.)**2
    Eout = E - Ein
    return E,Ein,Eout,degrees_squared

def __get_SUMDC2_P2in(status):
    DC = defaultdict(int)
    VC = defaultdict(int)
    for n,mn in status.rawnode2node.items():
        DC[status.node2com[mn]] += status.rawnode2degree[n]
        VC[status.node2com[mn]] += 1
    SUMDC2 = 0
    P2in = 0
    for c,d in DC.items():
        SUMDC2 += d*d
        P2in += VC[c]*(VC[c]-1)/2.
    return SUMDC2,P2in

def __modularity(status,model='ppm',pars = None):
    """
    Fast compute the modularity of the partition of the graph using
    status precomputed
    """
    par = __get_safe_par(model,pars)
    if not pars: pars = {}
    if model=='dcppm':
        # print(model,"!")
        # par = pars.get('gamma',1.)
        links = float(status.total_weight)
        result = 0.
        for community in set(status.node2com.values()):
            in_degree = status.internals.get(community, 0.)
            degree = status.degrees.get(community, 0.)
            if links > 0:
                result += in_degree / links - par *   ((degree / (2. * links)) ** 2)
        return result
    elif model == 'ilfrs':
        # par = pars.get('mu',1.)
        E,Ein,Eout,_ = __get_es(status)
        result = 0.
        par = max(par,__MIN)
        par = min(par,1.-__MIN)
        result += Eout * log( par )
        result += Ein * log( 1 - par )
        result += - Eout * log( 2*E )
        for community in set(status.node2com.values()):
            degree = status.degrees.get(community, 0.)
            if degree>0:
                result -= status.internals.get(community, 0.)*log(degree)
        result -= E
        result += __get_DLD(status)
        return result
    elif model == 'ilfr':
        # par = pars.get('mu',1.)
        E,_,Eout,_ = __get_es(status)
        DLD = __get_DLD(status)
        par = max(par,__MIN)
        logl = Eout*log(par)-Eout*log(2*E)+DLD-E
        for community in set(status.node2com.values()):
            degree = status.degrees.get(community, 0.)
            if degree>0:
                logl += status.internals.get(community, 0.)*log(((1.-par)/degree)+float(par)/(2.*E))
        return logl
    else:
        # par = pars.get('gamma',1.)
        E,Ein,Eout,_ = __get_es(status)
        _,P2in = __get_SUMDC2_P2in(status)        
        P2 = len(status.rawnode2node)
        P2 = P2*(P2-1)/2.
        P2out = P2 - P2in
        P2in = max(P2in,__MIN)
        P2out = max(P2out,__MIN)
        return (Ein - par*P2in*E/P2)/E

def __get_pin_pout(status):
    E,Ein,Eout,degrees_squared = __get_es(status)
    SUMDC2,P2in = __get_SUMDC2_P2in(status)
    Pin = 4.*Ein*E/SUMDC2
    if Eout == 0:
        Pout = __MIN
    else:
        Pout = 4.*Eout*E/(4.*E*E-SUMDC2)
    return Pin,Pout,E,Ein,Eout,degrees_squared,SUMDC2,P2in

def model_log_likelihood(graph,part_init,model,weight='weight',pars=None): #,fixedPin=None,fixedPout=None):
    current_graph = graph.copy()
    status = Status()
    status.init(current_graph, weight, part_init)
    assert model in ('dcppm','ppm','ilfr','ilfrs'), "Unknown model specified"
    par = __get_safe_par(model,pars)    
    if not pars: pars = {}
    if model == 'dcppm':
        # par = pars.get('gamma',1.)        
        pin,pout,E,Ein,Eout,degrees_squared,_,_ = __get_pin_pout(status)
        DLD = __get_DLD(status)
        result = 0.
        pin = max(pin,__MIN)
        pout = max(pout,__MIN)
        result += Ein*(log(pin)-log(pout))
        result -= (pin-pout)*degrees_squared/(4.*E)
        result += DLD # = __GRAPH_DEGREES_PREC
        result += E*log(pout)
        result -= E*pout
        result -= E*log(2.*E)
        return result
    elif model in ('ilfr', 'ilfrs'):
        if not pars.get('mu',None): # is None:
            return __modularity(status,model=model,pars={'mu':estimate_mu(graph,part_init)})
        else:
            return __modularity(status,model=model,pars=pars)
    elif model == 'ppm':
        # par = pars.get('gamma',1.)        
        E,Ein,Eout,_ = __get_es(status)
        _,P2in = __get_SUMDC2_P2in(status)
        P2 = len(status.rawnode2node)
        P2 = P2*(P2-1)/2.
        P2out = P2 - P2in
        P2in = max(P2in,__MIN)
        P2out = max(P2out,__MIN)
        Pin = Ein/P2in
        Pout = Eout/P2out
        ext_mod = -Eout - Ein
        if 'fixedPin' in pars: #is not None: 
            Pin = pars['fixedPin']
            ext_mod += Ein - P2in*pars['fixedPin']
        if 'fixedPout' in pars: #is not None: 
            Pout = pars['fixedPout']
            ext_mod += Eout - P2out*pars['fixedPout']
        if Ein > 0.:
            ext_mod += Ein*log(Pin)
        if Eout > 0.:
            ext_mod += Eout*log(Pout)
        return ext_mod

def estimate_gamma(graph,part_init,weight='weight',model='ppm',pars=None): #fixedPin=None,fixedPout=None):
    current_graph = graph.copy()
    status = Status()
    status.init(current_graph, weight, part_init)
    if not pars: pars = {}    

    if model == 'dcppm':
        Pin,Pout,_,_,_,_,_,_ = __get_pin_pout(status)
        Pin = max(Pin,__MIN)
        Pout = max(Pout,__MIN)
        return (Pin-Pout)/(log(Pin)-log(Pout))
    else:
        E,Ein,Eout,_ = __get_es(status)
        _,P2in = __get_SUMDC2_P2in(status)
        P2 = len(status.rawnode2node)
        P2 = P2*(P2-1)/2.
        P2out = P2 - P2in
        P2in = max(P2in,__MIN)
        P2out = max(P2out,__MIN)
        Pin = Ein/P2in
        Pout = Eout/P2out
        # if fixedPin is not None: Pin = fixedPin
        # if fixedPout is not None: Pout = fixedPout
        if 'fixedPin' in pars: #is not None: 
            Pin = pars['fixedPin']
        if 'fixedPout' in pars: #is not None: 
            Pout = pars['fixedPout']
        if Pin == 0.: Pin = __MIN
        if Pout == 0.: Pout = __MIN
        return P2 * (Pin - Pout) / (E * (log(Pin) - log(Pout)))

def estimate_mu(graph,partition,current_mu=None,model=None,weight='weight'):
    if model == 'ilfr':
        current_graph = graph.copy()
        status = Status()
        status.init(current_graph, weight, partition)
        E,_,Eout,_ = __get_es(status)
        if current_mu is None: current_mu = Eout/float(E)
        current_mu = max(current_mu,__MIN)
        current_mu = min(current_mu,1.-__MIN)
        res_mu = Eout*log(current_mu)
        for community in set(status.node2com.values()):
            degree = status.degrees.get(community, 0.)
            in_degree = 2*status.internals.get(community, 0.)
            if degree>0:
                res_mu += in_degree*log(((1.-current_mu)/degree)+current_mu/(2.*E))/2.
        return res_mu
    Eout = 0
    Gsize = graph.size()
    for n1,n2 in graph.edges_iter(): #links:
        if partition[n1] != partition[n2]: 
            Eout += 1
    return float(Eout)/Gsize

def _eta(data):
    if len(data) <= 1: return 0
    _exp = exp(1)
    counts = Counter()
    for d in data:
        counts[d] += 1
    probs = [float(c) / len(data) for c in counts.values()]
    probs = [p for p in probs if p > 0.]
    ent = 0
    for p in probs:
        if p > 0.:
            ent -= p * log(p, _exp)
    return ent

def _nmi(x, y):
    sum_mi = 0.0
    x_value_list = list(set(x))
    y_value_list = list(set(y))
    Px = []
    for xval in x_value_list:
        Px.append( len(filter(lambda q:q==xval,x))/float(len(x)) )
    Py = []
    for yval in y_value_list:
        Py.append( len(filter(lambda q:q==yval,y))/float(len(y)) )

    for i in xrange(len(x_value_list)):
        if Px[i] ==0.:
            continue
        sy = []
        for j,yj in enumerate(y):
            if x[j] == x_value_list[i]:
                sy.append( yj )
        if len(sy)== 0:
            continue
        pxy = []
        for yval in y_value_list:
            pxy.append( len(filter(lambda q:q==yval,sy))/float(len(y)) )

        t = []
        for j,q in enumerate(Py):
            if q>0:
                t.append( pxy[j]/Py[j] / Px[i])
            else:
                t.append( -1 )
            if t[-1]>0:
                sum_mi += (pxy[j]*log( t[-1]) )
    eta_xy = _eta(x)*_eta(y)
    if eta_xy == 0.: return -1
    return sum_mi/sqrt(_eta(x)*_eta(y))

def compare_partitions(p1,p2):
    p1_sets = defaultdict(set)
    p2_sets = defaultdict(set)
    [p1_sets[item[1]].add(item[0]) for item in p1.items()]
    [p2_sets[item[1]].add(item[0]) for item in p2.items()]
    p1_sets = p1_sets.values()
    p2_sets = p2_sets.values()
    cross_tab = [[0, 0], [0, 0]]
    for a1, s1 in enumerate(p1_sets):
        for a2, s2 in enumerate(p2_sets):
            common = len(s1 & s2)
            l1 = len(s1) - common
            l2 = len(s2) - common
            cross_tab[0][0] += common * common
            cross_tab[1][0] += common * l2
            cross_tab[0][1] += l1 * common
            cross_tab[1][1] += l1 * l2
    [[a00, a01], [a10, a11]] = cross_tab

    p1_vec = map(lambda x:x[1],sorted(p1.items(),key=lambda x:x[0]))
    p2_vec = map(lambda x:x[1],sorted(p2.items(),key=lambda x:x[0]))

    return {
        'nmi': _nmi(p1_vec,p2_vec),
        'rand': float(a00 + a11) / (a00 + a01 + a10 + a11),
        'jaccard' : float(a00) / (a01 + a10 + a00)
    }

