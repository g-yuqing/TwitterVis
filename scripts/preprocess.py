import os.path
import json
import logging
import collections
# from operator import itemgetter
import datetime
import numpy as np
import pandas as pd
import MeCab
from gensim.models import word2vec
from sklearn import manifold
import networkx as nx


class Nlp():
    def __init__(self):
        if not os.path.exists('../data/model/wiki.model'):
            self.mode_training()
        else:
            print('load model')
            self.model = word2vec.Word2Vec.load('../data/model/wiki.model')

    def mode_training(self):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=logging.INFO)
        sentences = word2vec.Text8Corpus('../data/model/wiki_wakati.txt')
        model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)
        model.save('../data/model/wiki.model')

    def year_retweet(self):
        print('preprocess data')
        tid_text = {}  # tid: content
        year_tweet = collections.defaultdict(list)  # classify tweet by year
        year_tid = collections.defaultdict(list)
        # query tweet_text file, retreive tid and text
        dataset = pd.read_csv('../data/tweet_text.csv')
        dataset = dataset.values
        for data in dataset:
            tid_text[str(data[0])] = dict(words=data[1], text=data[2])
        # # query retweet file, get retweeted time
        dataset = pd.read_csv('../data/retweet.csv')
        dataset = dataset.values
        for data in dataset:
            date, tid = data[0], str(data[1])
            if tid in tid_text:
                year = date.split('-')[0]
                if tid not in year_tid[year]:
                    year_tid[year].append(tid)
                    words, text = tid_text[tid]['words'], tid_text[tid]['text']
                    year_tweet[year].append(dict(tid=tid, words=words,
                                                 text=text))
        return year_tweet

    def similarity_dist(self):
        print('calculate similarity dist')
        mt = MeCab.Tagger('')
        mt.parse('')

        def get_vector_words(words):
            sum_vec = np.zeros(200)
            word_count = 0
            for word in words:
                try:
                    sum_vec += self.model.wv[word]
                    word_count += 1
                except:
                    pass
            return sum_vec / word_count

        def get_vector(text):
            sum_vec = np.zeros(200)
            word_count = 0
            node = mt.parseToNode(text)
            while node:
                fields = node.feature.split(',')
                if fields[0] == '名詞' or fields[0] == '動詞' or\
                        fields[0] == '形容詞':
                    try:
                        sum_vec += self.model.wv[node.surface]
                        word_count += 1
                    except:
                        pass
                node = node.next
            return sum_vec / word_count

        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))

        year_tweet = self.year_retweet()
        year_cosdist = {}
        for year, tweet_list in year_tweet.items():
            tid_list = [t['tid'] for t in tweet_list]
            length = len(tweet_list)
            dist_mat = [[0] * length for _ in range(length)]
            for i in range(length-1):
                for j in range(i+1, length):
                    tweet1, tweet2 = tweet_list[i], tweet_list[j]
                    text1, text2 = tweet1['text'], tweet2['text']
                    vec1, vec2 = get_vector(text1), get_vector(text2)
                    dist_mat[i][j] = dist_mat[j][i] = 1 - cos_sim(vec1, vec2)
            year_cosdist[year] = dict(dist=dist_mat, tids=tid_list)
        with open('../data/text_dist.json', 'w') as f:
            json.dump(year_cosdist, f)

    def word_cloud(self):
        word_count = collections.defaultdict(int)
        dataset = pd.read_csv('../data/words_noun.csv')
        dataset = dataset.values
        for data in dataset:
            words = data[1]
            for word in words.split():
                word_count[word] += 1
        with open('../data/word_cloud.json', 'w') as f:
            json.dump(word_count, f)

    def tweet_pagerank(self):
        # # words
        # word_count = collections.defaultdict(int)
        # dataset = pd.read_csv('../data/words_noun.csv')
        # dataset = dataset.values
        # for data in dataset:
        #     words = data[1]
        #     for word in words.split():
        #         word_count[word] += 1
        # key_words = ['原発', '事故', '避難', '放射能']
        # # influencers
        # influencer_count = collections.defaultdict(int)
        # dataset = pd.read_csv('../data/influencers.csv')
        # dataset = dataset.values
        # # tweets similarity
        with open('../data/text_dist.json', 'r') as f:
            dataset = json.load(f)
        for year, info in dataset.items():
            dist, tids = info['dist'], info['tids']
            length = len(tids)
            graph = nx.DiGraph()
            for i in range(length-1):
                for j in range(i+1, length):
                    graph.add_edge(i, j, weight=1 - dist[i][j])
                    graph.add_edge(j, i, weight=1 - dist[i][j])
            pr = nx.pagerank(graph)
            print(year)
            for key, val in pr.items():
                print(key, val)
        # calculate


class Graph():
    def __init__(self):
        pass

    def ego_network(self):
        with open('../data/coretweet_pattern.json', 'r') as f:
            dataset = json.load(f)
        results = {}
        for src_name, dst_info in dataset.items():
            src_name = int(src_name)
            name_nid = {}
            name_size = {}
            edge_weight = {}
            name_list = [d[0] for d in dst_info]
            for i, dst in enumerate(dst_info):
                if i == 0:
                    name, size = dst[0], dst[1]
                    name_size[name] = size
                    name_nid[name] = i
                else:
                    dst_name, weight = dst[0], dst[1]
                    edge_weight[tuple([src_name, dst_name])] = weight
                    name_nid[dst_name] = i
            # other nodes (except ego node)
            for dst in dst_info[1:]:
                name = dst[0]
                for i, temp_dst in enumerate(dataset[str(name)]):
                    if i == 0:
                        temp_name, size = temp_dst[0], temp_dst[1]
                        assert name == temp_name
                        name_size[temp_name] = size
                    else:
                        dst_name, weight = temp_dst[0], temp_dst[1]
                        if dst_name in name_nid:
                            if tuple([name, dst_name]) not in edge_weight or\
                                    tuple([dst_name, name]) not in edge_weight:
                                edge_weight[tuple([name, dst_name])] = weight
            graph = nx.Graph()
            res_nodes, temp_edges = [], []
            for edge, weight in edge_weight.items():
                src, dst = name_nid[edge[0]], name_nid[edge[1]]
                temp_edges.append(dict(source=src, target=dst, value=weight))
                graph.add_edge(src, dst, weight=weight)
            positions = nx.spring_layout(graph)
            for i, pos in positions.items():
                name = name_list[i]
                assert i == name_nid[name]
                size = name_size[name]
                res_nodes.append(dict(id=i, x=pos[0], y=pos[1], size=size,
                                      degree=len(dst_info)-1))
            res_edges = []
            for edge in temp_edges:
                si, ti, val = edge['source'], edge['target'], edge['value']
                x1, y1 = positions[si][0], positions[si][1]
                src = dict(x=x1, y=y1)
                x2, y2 = positions[ti][0], positions[ti][1]
                dst = dict(x=x2, y=y2)
                res_edges.append(dict(src=src, dst=dst, value=val))
            results[src_name] = dict(nodes=res_nodes, edges=res_edges)
        with open('../data/ego_network.json', 'w') as f:
            json.dump(results, f)

    def force_layout(self):
        with open('../data/coretweet_pattern.json', 'r') as f:
            dataset = json.load(f)
        print(len(dataset))
        nodes, edges = [], []
        name_nid = {}
        name_eid = {}
        node_count, edge_count = 0, 0
        for src_name, dst_info in dataset.items():
            src_name = int(src_name)
            if src_name not in name_nid:
                name_nid[src_name] = node_count
                nodes.append(dict(id=node_count, name=src_name,
                                  size=dst_info[0][1]))
                node_count += 1
            for dst in dst_info:
                dst_name = dst[0]
                if dst_name not in name_nid:
                    name_nid[dst_name] = node_count
                    nodes.append(dict(id=node_count, name=dst_name,
                                      size=dataset[str(dst_name)][0][1]))
                    node_count += 1
                edge_name1 = tuple([name_nid[src_name], name_nid[dst_name]])
                edge_name2 = tuple([name_nid[dst_name], name_nid[src_name]])
                if edge_name1 not in name_eid and edge_name2 not in name_eid\
                        and src_name != dst_name:
                    name_eid[edge_name1] = edge_count
                    edges.append(dict(id=edge_count, source=name_nid[src_name],
                                      target=name_nid[dst_name]))
                    edge_count += 1
        print(len(nodes), len(edges))
        with open('../data/force_layout.json', 'w') as f:
            json.dump(dict(nodes=nodes, edges=edges), f)

    def timeline(self):
        dataset = pd.read_csv('../data/retweet.csv')
        dataset = dataset.values
        tid_times = collections.defaultdict(list)
        for data in dataset:
            tid_times[data[1]].append(data[0])
        # sort tid_times
        temp_sorted = {}
        for tid, time_list in tid_times.items():
            temp_sorted[tid] = sorted(time_list, key=lambda x:
                                      datetime.datetime.strptime(x,
                                                                 '%Y-%m-%d'))
        # count
        results = collections.defaultdict(list)
        for tid, time_list in temp_sorted.items():
            # date_count = collections.defaultdict(int)
            date_count = {}
            min_date = datetime.datetime.strptime(time_list[0], '%Y-%m-%d')
            max_date = datetime.datetime.strptime(time_list[-1], '%Y-%m-%d')
            cur_date = min_date
            step = datetime.timedelta(days=1)
            while cur_date <= max_date:
                date_count[cur_date.strftime('%Y-%m-%d')] = 0
                cur_date += step
            for time in time_list:
                date_count[time] += 1
            for time, count in date_count.items():
                results[tid].append(dict(date=time, count=count))
        with open('../data/timeline.json', 'w') as f:
            json.dump(results, f)

    def coretweet_pattern(self):
        '''
        return
        tid: [{tid:count}]
        '''
        user_tid = collections.defaultdict(list)
        tid_user = collections.defaultdict(list)
        tid_tid = {}
        dataset = pd.read_csv('../data/retweet.csv')
        dataset = dataset.values
        for data in dataset:
            tid, dst = data[1], data[2]
            user_tid[dst].append(tid)
            tid_user[tid].append(dst)
        for tid, user_list in tid_user.items():
            tid_count = collections.defaultdict(int)
            for user in user_list:
                for ttid in user_tid[user]:
                    tid_count[ttid] += 1
            tid_tid[tid] = tid_count
        # sort
        result = {}
        # for tid, tid_dict in tid_tid.items():
        #     result[tid] = collections.OrderedDict(sorted(tid_dict.items(),
        #                                                  key=itemgetter(1),
        #                                                  reverse=True))
        for tid, tid_dict in tid_tid.items():
            result[tid] = sorted(tid_dict.items(), key=lambda x: x[1],
                                 reverse=True)
        with open('../data/coretweet_pattern.json', 'w') as f:
            json.dump(result, f)

    def mds_layout(self):
        seed = np.random.RandomState(seed=3)
        dataset = pd.read_csv('../data/tweet_text.csv')
        dataset = dataset.values
        tid_words = {}
        for data in dataset:
            tid_words[str(data[0])] = dict(noun=data[1], text=data[2])
        with open('../data/text_dist.json', 'r') as f:
            dataset = json.load(f)
        with open('../data/coretweet_pattern.json', 'r') as f:
            tid_tids = json.load(f)
        year_nodes = {}
        for year, dist_info in dataset.items():
            dist, tid_list = dist_info['dist'], dist_info['tids']
            mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-12,
                               dissimilarity='precomputed', random_state=seed)
            positions = mds.fit_transform(dist)
            nodes = []
            for i, p in enumerate(positions):
                # get neighbours
                temp_dists = dist[i]
                threshold = 0.3
                neigh = []
                for index in range(len(temp_dists)):
                    if temp_dists[index] <= threshold:
                        neigh.append(tid_list[index])
                tid = tid_list[i]
                noun = tid_words[tid]['noun'].split()
                text = tid_words[tid]['text']
                cotids = [[str(tweet[0]), tweet[1]]
                          for tweet in tid_tids[tid]]
                nodes.append(dict(x=p[0], y=p[1], tid=tid,
                                  noun=noun, text=text, neigh=neigh,
                                  cotids=cotids))
            year_nodes[year] = nodes
        all_nodes = []
        for year, nodelist in year_nodes.items():
            for nodedict in nodelist:
                nodedict['year'] = year
                all_nodes.append(nodedict)
        tid_text = {}
        for tid, worddict in tid_words.items():
            tid_text[str(tid)] = worddict['text']
        # add timeline information
        with open('../data/timeline.json', 'r') as f:
            tid_time = json.load(f)
        jsonfile = {'data': all_nodes, 'tidtext': tid_text,
                    'tidtime': tid_time}
        with open('../data/mds_layout.json', 'w') as f:
            json.dump(jsonfile, f)


if __name__ == '__main__':
    graph = Graph()
    graph.ego_network()
    # graph.force_layout()
    # graph.mds_layout()
    # graph.timeline()
    # graph.coretweet_pattern()
    # nlp = Nlp()
    # nlp.tweet_pagerank()
    # nlp.similarity_dist()
