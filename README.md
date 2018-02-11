# community_loglike
This library provides several community detection algorithms based on the likelihood optimization. 

Louvain algorithm is used to optimize the likelihood for each model. 
The following models are implemented:
  * PPM: Planted Partition Model (particular case of Stochastic Block Model) having two parameters p_in and p_out;
  * DCPPM: Degree-Corrected Planted Partition Model having two parameters p_in and p_out;
  * ILFR: Independent LFR Model with parameter mu
  * ILFRs: simplified version of ILFR

Link to the paper describing all algorithms will be provided soon.

## Acknowledgements
Originally based on [community aka python-louvain library from Thomas Aynaud](https://github.com/taynaud/python-louvain).

## Requirements
This library uses networkx as a graph processing library.
It should work with Python 2.7 or python 3.

The provided example (example_run.py) works only under Python 2.7.

## Examples
### TBD
