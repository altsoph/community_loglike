# community_loglike
This library provides several community detection algorithms based on the likelihood optimization. 
It's a complimentary code for our article [Community detection through likelihood optimization: in search of a sound model](https://arxiv.org/abs/1802.04472).

## Acknowledgements
Originally based on the code of [community aka python-louvain library from Thomas Aynaud](https://github.com/taynaud/python-louvain).

## Methods
We provide several different models, so the likelihood of a graph partition under the given model could be used as a target quality function to optimize.
The optimization process itself is a standard greedy Louvain algorithm. The 

The following models are implemented:
  * PPM: Planted Partition Model (particular case of Stochastic Block Model) having two parameters p_in and p_out;
  * DCPPM: Degree-Corrected Planted Partition Model having two parameters p_in and p_out;
  * ILFR: Independent LFR Model with parameter mu
  * ILFRs: simplified version of ILFR

## Requirements
This library uses networkx as a graph processing library.
It should work with Python 2.7 or Python 3.

The provided example scripts probably work only under Python 2.7 but could be easily adapted for Python 3.

## Examples
We included 3 different examples with two reasons in mids:
  * to illustrate the possibilities and functions of our library
  * to demonstrate several possible optimal parameter search strategies

### 1. example_run.py
This example uses 3 different models (PPM/DCPPM/ILFRs) and the iterative parameter optimization strategy.
On each iteration such strategy first constructs the best partition given the parameter value, then calculates the most probable parameter value for the current partition. It appears (according to Newman's work?) such iteration fast converges to the (local?) optimum solution.
Finally, this example gives the rand/jaccard/NMI scores against the ground truth partition for each of the resulting partitions.

### 2. example_run_ilfr.py
This second example does exactly the same as a previous one, but especially for the ILFR method.
The difference is in the way we calculate the best parameter value for given partition: there is no good analytical solution for this case, so we use **scipy.optimize.fmin_powell** to optimize it on each iteration.

### 3. example_run_fminpowell.py
The third example uses the direct optimization of the log likelihood of the model parameter for each model using **scipy.optimize.fmin_powell**.


## Main library functions
Here is the list of the most important functions with brief comments on them:
  * **best_partition** -- this is the main function to build the partition given the *graph* (NetworkX object), *method* (should be "dcppm"/"ppm"/"ilfr"/"ilfrs"), *pars* as a dict of model's parameters (basically, one should use 'mu' from (0,1) for "ilfr" and "ilfrs", and 'gamma' from (0,inf) for "ppm"/"dcppm") and some optional parameters same as in the python-louvain package,
  * **model_log_likelihood** -- calculates the log likelihood of the given partition of the graph considering the given method and method's parameter value,
  * **estimate_mu** -- returns the estimation for the best mu value given the graph and its partition, should be used for the "ilfrs" model,
  * **estimate_gamma** -- returns the estimation for the best gamma value given the model ("ppm"/"dcppm"), the graph and its partition; also the fixed Pin, Pout parameters could be provided (see the model description for some details?),
  * **ilfr_mu_loglikelihood** -- returns the log likelihood for the given mu value considering the graph and the partition,
  * **compare_partitions** -- calculates Rand index, Jaccard index and NMI between two different partitions of the same graph.

## Datasets 
We also included several real world datasets with the known ground truth partitions, namely:
  * datasets/**karate** (Wayne W Zachary. 1977. An information flow model for conflict and fission in
small groups),
  * datasets/**doplhins** (David Lusseau, Karsten Schneider, Oliver J Boisseau, Patti Haase, Elisabeth
Slooten, and Steve M Dawson. 2003. The bottlenose dolphin community of
Doubtful Sound features a large proportion of long-lasting associations. Behavioral
Ecology and Sociobiology 54, 4 (2003), 396–405.),
  * datasets/**football** (Mark EJ Newman and Michelle Girvan. 2004. Finding and evaluating community
structure in networks. Physical review E 69, 2 (2004), 026113),
  * datasets/**polbooks** (Mark EJ Newman. 2006. Modularity and community structure in networks.
Proceedings of the national academy of sciences 103, 23 (2006), 8577–8582),
  * datasets/**polblogs** (Lada A Adamic and Natalie Glance. 2005. The political blogosphere and the 2004
US election: divided they blog. In Proceedings of the 3rd international workshop
on Link discovery. ACM, 36–43),
  * datasets/**eu-core** (Jure Leskovec, Jon Kleinberg, and Christos Faloutsos. 2007. Graph evolution:
Densification and shrinking diameters. ACM Transactions on Knowledge Discovery
from Data (TKDD) 1, 1 (2007), 2),
  * datasets/**cora_full** (Lovro Šubelj and Marko Bajec. 2013. Model of complex networks based on
citation dynamics. In Proceedings of the 22nd international conference on World
Wide Web. ACM, 527–530),
  * datasets/**as** (Marián Boguná, Fragkiskos Papadopoulos, and Dmitri Krioukov. 2010. Sustaining
the internet with hyperbolic mapping. Nature communications 1 (2010), 62).
