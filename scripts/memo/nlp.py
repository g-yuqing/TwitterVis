import os.path
import collections
import json
import logging
import numpy as np
import pandas as pd
from gensim.models import word2vec
from sklearn.cluster import DBSCAN


class Nlp():
    def __init__(self):
        if not os.path.exists('../data/model/wiki.model'):
            self.mode_training()
        else:
            self.model = word2vec.Word2Vec.load('../data/model/wiki.model')

    def mode_training(self):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=logging.INFO)
        sentences = word2vec.Text8Corpus('../data/model/wiki_wakati.txt')
        model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)
        model.save('../data/model/wiki.model')

    def similarity(self):
        def get_vector(words):
            sum_vec = np.zeros(200)
            word_count = 0
            for word in words:
                try:
                    sum_vec += self.model.wv[word]
                    word_count += 1
                except:
                    pass
            return sum_vec / word_count

        def cos_sim(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        with open('../data/quarter/tweet_info.json', 'r') as f:
            dataset = json.load(f)
        node_name = []
        year_info = collections.defaultdict(list)
        for year, info in dataset.items():
            for tid, details in info.items():
                year_info[year].append(details['words'])
                node_name.append(tid)
        # calculate similarity
        year_dist = {}
        for year, info in year_info.items():
            cos_dist = [[0]*len(info) for _ in range(len(info))]
            for i1, d1 in enumerate(info):
                for i2, d2 in enumerate(info):
                    if i1 <= i2:
                        continue
                    else:
                        temp1 = [d for d in d1.split()]
                        temp2 = [d for d in d2.split()]
                        v1, v2 = get_vector(temp1), get_vector(temp2)
                        simi = cos_sim(v1, v2)
                        cos_dist[i1][i2] = cos_dist[i2][i1] = 1 - simi
            year_dist[year] = cos_dist
        with open('../data/quarter/cosine_distance.json', 'w') as f:
            json.dump(year_dist, f)
        # clustering
        filename = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
                  '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe',
                  '#008080', '#e6beff', '#aa6e28', '#fffac8', '#800000',
                  '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080']
        # with open('../data/quarter/cosine_distance.json', 'r') as f:
        #     year_dist = json.dump(f)
        for fn in filename:
            with open('../data/quarter/node_edge/'+fn+'.json', 'r') as f:
                node_edge = json.load(f)
            nodes = node_edge['nodes']
            cos_dist = year_dist[fn]
            db = DBSCAN(eps=0.5, min_sample=2, metric='precomputed')
            clusters = db.fit_predict(cos_dist)
            for i in range(len(node_name)):
                name = nodes[i]['name']
                nid = node_name.index(name)
                nodes[i]['cluster'] = int(clusters[nid])
                nodes[i] = colors[clusters[nid]]
            with open('../data/quarter/cluster'+fn+'.json', 'w') as f:
                jsonfile = dict(nodes=nodes, )


if __name__ == '__main__':
    nlp = Nlp()
    nlp.similarity()
