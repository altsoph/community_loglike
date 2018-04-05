# coding=utf-8
# -*- coding: utf-8 -*-
"""
This package implements several community detection.

Originally based on community aka python-louvain library from Thomas Aynaud
(https://github.com/taynaud/python-louvain)
"""

__author__ = """Aleksey Tikhonov (altsoph@gmail.com)"""
__author__ = """Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)"""
#    Copyright (C) 2018 by
#    Aleksey Tikhonov (altsoph@gmail.com>
#    Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)
#    All rights reserved.
#    BSD license.


class Status(object):
    """
    To handle several data in one struct.

    Could be replaced by named tuple, but don't want to depend on python 2.6
    """
    node2com = {}
    total_weight = 0
    internals = {}
    degrees = {}
    gdegrees = {}
    rawnode2node = {}
    rawnode2degree = {}
    com2size = {}
    node2size = {}

    def __init__(self):
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.loops = dict([])
        self.rawnode2node = dict([])
        self.rawnode2degree = dict([])
        self.com2size = dict([])
        self.node2size = dict([])

    def __str__(self):
        return ("node2com : " + str(self.node2com) + " degrees : "
                + str(self.degrees) + " internals : " + str(self.internals)
                + " total_weight : " + str(self.total_weight)
                + " rawnode2node : " + str(self.rawnode2node) 
                + " com2size : " + str(self.com2size) 
                + " node2size : " + str(self.node2size) 
                )
    def copy(self):
        """Perform a deep copy of status"""
        new_status = Status()
        new_status.node2com = self.node2com.copy()
        new_status.rawnode2node = self.rawnode2node.copy()
        new_status.com2size = self.com2size.copy()
        new_status.internals = self.internals.copy()
        new_status.degrees = self.degrees.copy()
        new_status.gdegrees = self.gdegrees.copy()
        new_status.total_weight = self.total_weight
        new_status.rawnode2degree = self.rawnode2degree.copy()

    def init(self, graph, weight, part=None, raw_partition=None, raw_graph=None):
        """Initialize the status of a graph with every node in one community"""
        self.rawnode2node = dict([])
        self.rawnode2degree = dict([])
        self.com2size = dict([])
        self.node2size = dict([])
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.total_weight = graph.size(weight=weight)
        count = 0
        if part is None:
            for node in sorted(graph.nodes()):
                if raw_partition is None:
                    self.rawnode2node[node] = node
                self.node2com[node] = count
                deg = float(graph.degree(node, weight=weight))
                if deg < 0:
                    error = "Bad graph type ({})".format(type(graph))
                    raise ValueError(error)
                self.degrees[count] = deg
                self.gdegrees[node] = deg
                edge_data = graph.get_edge_data(node, node, default={weight: 0})
                self.loops[node] = float(edge_data.get(weight, 1))
                self.internals[count] = self.loops[node]
                count += 1
        else:
            for node in graph.nodes():
                if raw_partition is None:
                    self.rawnode2node[node] = node
                com = part[node]
                # self.rawnode2node[node] = com
                self.node2com[node] = com
                deg = float(graph.degree(node, weight=weight))
                self.degrees[com] = self.degrees.get(com, 0) + deg
                self.gdegrees[node] = deg
                inc = 0.
                for neighbor, datas in graph[node].items():
                    edge_weight = datas.get(weight, 1)
                    if edge_weight <= 0:
                        error = "Bad graph type ({})".format(type(graph))
                        raise ValueError(error)
                    if part[neighbor] == com:
                        if neighbor == node:
                            inc += float(edge_weight)
                        else:
                            inc += float(edge_weight) / 2.
                self.internals[com] = self.internals.get(com, 0) + inc
        if raw_partition:
            for node,metanode in raw_partition.items():
                self.rawnode2node[node] = metanode
        for com in set(self.node2com.values()):
            self.com2size[com] = 0
        for rawnode,node in self.rawnode2node.items():
            self.com2size[ self.node2com[node] ] += 1
            if node not in self.node2size:
                self.node2size[ node ] = 0
            self.node2size[ node ] += 1
        if raw_graph is None:
            raw_graph = graph
        for edge in raw_graph.edges():
            self.rawnode2degree[edge[0]] = self.rawnode2degree.get(edge[0],0)+1
            self.rawnode2degree[edge[1]] = self.rawnode2degree.get(edge[1],0)+1
