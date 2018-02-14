#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This package implements several community detection.

Originally based on community aka python-louvain library from Thomas Aynaud
(https://github.com/taynaud/python-louvain)
"""

from .community_ext import (
    partition_at_level,
    modularity,
    best_partition,
    generate_dendrogram,
    induced_graph,
    load_binary,
    estimate_gamma,
    estimate_mu,
    ilfr_mu_loglikelihood,
    compare_partitions,
    model_log_likelihood
)


__author__ = """Aleksey Tikhonov (altsoph@gmail.com)"""
__author__ = """Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)"""

#    Copyright (C) 2018 by
#    Aleksey Tikhonov (altsoph@gmail.com>
#    Liudmila Ostroumova Prokhorenkova (ostroumova-la@yandex-team.ru)
#    All rights reserved.
#    BSD license.
