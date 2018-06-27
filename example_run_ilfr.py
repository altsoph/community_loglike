# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function
import community_ext
import networkx as nx
import scipy

def opt_mu(G,partition,mu):
    opt_fn = lambda x:-community_ext.ilfr_mu_loglikelihood(G,partition,current_mu=x[0],model='ilfr')
    return float(scipy.optimize.fmin_powell(opt_fn, mu,full_output = False,disp = False))


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

method = 'ilfr'
print('\nMethod', method)

# a starting parameter value depends on the method
work_par = 0.5

# now start the iterative process    
prev_par, it = -1, 0
prev_pars = set()
while abs(work_par-prev_par)>1e-5: # stop if the size of improvement too small
    it += 1
    if it>100: break # stop after 100th iteration

    # update the parameter value
    prev_par = work_par
    if prev_par in prev_pars: break # stop if we are in the cycle
    prev_pars.add(prev_par)

    # find the optimal partition with the current parameter value
    partition = community_ext.best_partition(G,model=method,pars={'mu':work_par})

    # calculate optimal parameter value for the current partition
    work_par = opt_mu(G,partition,community_ext.estimate_mu(G,partition))

    loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'gamma':work_par,'mu':work_par})
    print('current par',work_par,'loglike',loglike)

# calculate and print the scores of resulting partition
part_scores = community_ext.compare_partitions(groundtruth_partition,partition)
loglike =   community_ext.model_log_likelihood(G,partition,model=method,pars={'gamma':work_par,'mu':work_par})
print('best par',work_par)
print("rand\t% 0f\tjaccard\t% 0f\tnmi\t% 0f\tnmi_arithm\t% 0f\tsize\t%d\tloglike\t% 0f" %\
        (part_scores['rand'], part_scores['jaccard'], part_scores['nmi'], part_scores['nmi_arithm'], len(set(partition.values())), loglike))
