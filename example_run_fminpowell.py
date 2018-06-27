# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function
import community_ext
import networkx as nx
import scipy

# optimization routine
def opt_par(G,method,par):
    def opt_fn(work_par):
        work_par = work_par[0]
        if method in ('ilfrs','ilfr'):
            partition = community_ext.best_partition(G,model=method,pars={'mu':work_par})
            loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'mu':work_par})
        else:
            partition = community_ext.best_partition(G,model=method,pars={'gamma':work_par})
            loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'gamma':work_par})
        return -loglike

    # find the optimal parameter value
    best_par = float(scipy.optimize.fmin_powell(opt_fn, par, full_output = False,disp = False))

    # calculate the partition with the optimal parameter value
    if method in ('ilfrs','ilfr'):
        partition = community_ext.best_partition(G,model=method,pars={'mu':best_par})
        loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'mu':best_par})
    else:
        partition = community_ext.best_partition(G,model=method,pars={'gamma':best_par})
        loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'gamma':best_par})
    return partition, loglike, best_par


fn1 = "datasets/polblogs/polblogs.edges"
fn2 = fn1.replace(".edges",".clusters")
print("DATASET:",fn1)

# load graph
G = nx.Graph()
for line in open(fn1):
    from_node, to_node = map(int, line.rstrip().split("\t"))
    if from_node not in G or to_node not in G[from_node]:
        G.add_edge(from_node,to_node)

# load the ground-truth partition
groundtruth_partition = dict()
for line in open(fn2):
    node, cluster = map(int, line.rstrip().split("\t"))
    if node not in G.nodes(): continue 
    groundtruth_partition[node] = cluster

# print some general info
gt_mu = community_ext.estimate_mu(G,groundtruth_partition)
print("ground truth mu\t",gt_mu)
print("ground truth clusters\t",len(set(groundtruth_partition.values())))
print("ground truth modularity\t", community_ext.modularity(groundtruth_partition,G))

# now cycle thru the methods and optimize with each one
methods = ('ppm','dcppm','ilfrs','ilfr')

for method in methods:
    print('\nMethod', method)
    # a starting parameter value depends on the method
    if method in ('ilfrs','ilfr'):
        work_par = 0.5
    else:
        work_par = 1.

    partition, loglike, best_par = opt_par(G,method,work_par)
    # calculate and print the scores of resulting partition
    part_scores = community_ext.compare_partitions(groundtruth_partition,partition)
    print('best par',best_par)
    print("rand\t% 0f\tjaccard\t% 0f\tnmi\t% 0f\tnmi_arithm\t% 0f\tsize\t%d\tloglike\t% 0f" %\
            (part_scores['rand'], part_scores['jaccard'], part_scores['nmi'], part_scores['nmi_arithm'], len(set(partition.values())), loglike))
