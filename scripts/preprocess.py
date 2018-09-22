import os.path
import json
import math
import logging
import collections
import datetime
import numpy as np
import pandas as pd
import unicodedata
import MeCab
import phate
from gensim.models import word2vec, KeyedVectors
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn import manifold
from sklearn.cluster import DBSCAN, KMeans
import networkx as nx
from operator import itemgetter


class NLProcessor():
    def __init__(self):
        pass
        # print('loading model')
        # self.model = KeyedVectors.load_word2vec_format(
        #     '../data/model/model.vec')
        # self.model = word2vec.Word2Vec.load('../data/model_dep/wiki.model')

    def word_to_vec_model(self):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=logging.INFO)
        sentences = word2vec.Text8Corpus('../data/model/wiki_wakati.txt')
        model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)
        model.save('../data/model/wiki.model')

    def doc_to_vec_model(self):
        def is_japanese(string):
            for ch in string:
                name = unicodedata.name(ch)
                if "CJK UNIFIED" in name \
                        or "HIRAGANA" in name or "KATAKANA" in name:
                    return True
            return False

        def collect_words(text):
            out_words = []
            tagger = MeCab.Tagger('')
            tagger.parse('')
            # remove 'RT ...:'
            if 'RT' in text:
                index = text.find(':')
                text = text[index+1:]
            node = tagger.parseToNode(text)
            while node:
                word_type = node.feature.split(",")[0]
                if word_type in ['名詞', '動詞', '形容詞']:
                    word = node.surface
                    if is_japanese(word):
                        out_words.append(word)
                node = node.next
            return out_words
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        training_docs, index = [], 0
        for tid, info in tid_info.items():
            training_docs.append(
                TaggedDocument(
                    words=collect_words(info['text']),
                    tags=[str(index)]))
            index += 1
        model = Doc2Vec(documents=training_docs, min_count=1, dm=0)
        model.save('../data/model/tweet.model')

    def process_csv(self):
        def is_japanese(string):
            for ch in string:
                name = unicodedata.name(ch)
                if "CJK UNIFIED" in name \
                        or "HIRAGANA" in name or "KATAKANA" in name:
                    return True
            return False
        mt = MeCab.Tagger()
        mt.parse('')
        filepath = '../data/current/retweet_info.csv'
        dataset = pd.read_csv(filepath).values  # tid,date,infl,user,text,count
        tid_info = collections.defaultdict(dict)
        print(len(dataset))
        for data in dataset:
            # for json dump
            tid, author, text, count = str(data[0]), int(data[2]),\
                 str(data[4]), int(data[5])
            if tid in tid_info:
                continue
            tid_info[tid]['author'] = author
            tid_info[tid]['count'] = count
            tid_info[tid]['rtd'] = collections.defaultdict(int)
            tid_info[tid]['text'] = text
            tid_info[tid]['words'] = []
            if text[:2] == 'RT':
                pos = text.find(':')
                text = text[pos+1:]
            node = mt.parseToNode(text)
            while node:
                fields = node.feature.split(',')
                if fields[0] == '名詞' and fields[2] == '一般' and\
                        fields[1] != '代名詞' and fields[1] != '連体化' and\
                        fields[1] != '非自立':
                    word = node.surface
                    if is_japanese(word):
                        tid_info[tid]['words'].append(word)
                else:
                    pass
                node = node.next
        for data in dataset:
            tid, date = str(data[0]), str(data[1])
            tid_info[tid]['rtd'][date] += 1
        print(len(tid_info))
        # return tweet_id
        with open('../data/current/tweet_info.json', 'w') as f:
            json.dump(tid_info, f)

    def text_process(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        unknown_list = collections.defaultdict(int)
        topic_vec_list = []
        topic_word_list = []
        tid_list = []
        for tid, info in tid_info.items():
            words = info['words']
            sum_vec, word_count = np.zeros(200), 0
            for word in words:
                try:
                    sum_vec += self.model[word]
                    word_count += 1
                except:
                    unknown_list[word] += 1
            if word_count == 0:
                topic_vec_list.append(sum_vec)
            else:
                topic_vec_list.append(sum_vec/word_count)
            topic_word_list.append(words)
            tid_list.append(tid)
        length = len(topic_vec_list)
        dists = [[0]*length for _ in range(length)]
        for i in range(length-1):
            for j in range(i+1, length):
                vec1, vec2 = topic_vec_list[i], topic_vec_list[j]
                if not np.any(vec1) and not np.any(vec2):
                    dists[i][j] = dists[j][i] = 0
                elif np.any(vec1) and not np.any(vec2) or\
                        (not np.any(vec1) and np.any(vec2)):
                    dists[i][j] = dists[j][i] = 1
                else:
                    dists[i][j] = dists[j][i] = 1 - cos_sim(vec1, vec2)
        dists = np.array(dists)
        db = DBSCAN(eps=0.3, min_samples=6, metric='precomputed').fit(dists)
        labels = db.labels_
        print(len(labels))
        # topic_vec_list = np.array(topic_vec_list)
        # tsne = manifold.TSNE(n_components=2, random_state=0)
        # positions = tsne.fit_transform(topic_vec_list)
        # topic_vec_list = np.array(topic_vec_list)
        # pl = phate.PHATE(n_components=2)
        # positions = pl.fit_transform(topic_vec_list)
        clustering_tid = collections.defaultdict(list)
        assert len(labels) == len(tid_list)
        for tid, cluster in zip(tid_list, labels):
            clustering_tid[str(cluster)].append(tid)
        with open('../data/current/clustering_tid.json', 'w') as f:
            json.dump(clustering_tid, f)

    def text_layout(self):
        with open('../data/current/clustering_tid.json', 'r') as f:
            clustering_tid = json.load(f)
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        tid_list = clustering_tid['0']+clustering_tid['-1']
        topic_vec_list = []
        for tid in tid_list:
            info = tid_info[str(tid)]
            words = info['words']
            sum_vec, word_count = np.zeros(200), 0
            for word in words:
                try:
                    sum_vec += self.model[word]
                    word_count += 1
                except:
                    pass
            if word_count == 0:
                topic_vec_list.append(sum_vec)
            else:
                topic_vec_list.append(sum_vec/word_count)
        topic_vec_list = np.array(topic_vec_list)
        pl = phate.PHATE(n_components=2)
        positions = pl.fit_transform(topic_vec_list)
        nodes = []
        for pos in positions:
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes.append(dict(x=x_pos, y=y_pos))
        with open('../data/current/text_layout.json', 'w') as f:
            json.dump(dict(nodes=nodes), f)

    def word_corpus(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/clustering_tid.json', 'r') as f:
            clustering_tid = json.load(f)
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        tid_list = clustering_tid['0']+clustering_tid['-1']
        word_id = {}
        word_list = []
        wid = 0
        for tid in tid_list:
            info = tid_info[str(tid)]
            words = info['words']
            for word in words:
                if word not in word_id:
                    word_id[word] = wid
                    word_list.append(word)
                    wid += 1
        # combine similiar words
        sim_thres = 0.6
        length = len(word_list)
        for i in range(length-1):
            for j in range(i+1, length):
                try:
                    w1, w2 = word_list[i], word_list[j]
                    vec1 = self.model[w1]
                    vec2 = self.model[w2]
                    if cos_sim(vec1, vec2) >= sim_thres:
                        wid = min(word_id[w1], word_id[w2])
                        word_id[w1] = word_id[w2] = wid
                except:
                    pass
        # pagerank
        G = nx.DiGraph()
        for tid in tid_list:
            info = tid_info[str(tid)]
            words = info['words']
            length = len(words)
            if length > 1:
                for i in range(length-1):
                    for j in range(i+1, length):
                        w1, w2 = words[i], words[j]
                        wid1, wid2 = word_id[w1], word_id[w2]
                        G.add_edge(wid1, wid2)
        word_score = {}
        pr = nx.pagerank(G)
        for i, score in pr.items():
            word = word_list[i]
            word_score[word] = score
        with open('../data/current/temp.json', 'w') as f:
            json.dump(word_score, f)

    def snapshot(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        unknown_list = collections.defaultdict(int)
        # topic = ['放射能', '環境', '避難', '政府', '学会', '経済', '食品']
        topic = ['危機管理', '関東地方', '風評被害', '放射性物質', '子どもたち',
                 'この国', '無量大数', '編集長', '基準値', 'ツイート',
                 '廃炉', '安倍首相', 'ミリシーベルト', 'メルトダウン']

        def func():
            temp = {}
            for key in topic:
                temp[key] = 0
            return temp
        tpc_vecs = [self.model[tpc] for tpc in topic]
        date_tpc = collections.defaultdict(func)
        sim_thres = 0.5
        for tid, info in tid_info.items():
            words = info['words']
            temp_topic = []
            for i, tpc in enumerate(topic):
                vec1 = tpc_vecs[i]
                for word in words:
                    try:
                        vec2 = self.model[word]
                        temp_sim = cos_sim(vec1, vec2)
                        if temp_sim > sim_thres:
                            temp_topic.append(tpc)
                            break
                    except:
                        unknown_list[word] += 1
            date_count = info['rtd']
            for date, count in date_count.items():
                for tt in temp_topic:
                    date_tpc[date][tt] += count
        # snapshot matrix
        graph = []
        date_list = []
        timestep, overlay = 31, 28
        movestep = timestep - overlay
        start_date = datetime.date(2011, 3, 1)
        end_date = datetime.date(2016, 12, 1)
        current_date = start_date
        while current_date < end_date:
            temp_vec = np.array([0]*len(topic))
            for i in range(timestep):
                temp_date = current_date + datetime.timedelta(days=i)
                temp_date_str = temp_date.strftime('%Y-%m-%d')
                try:
                    temp_vec += np.array(
                        list(date_tpc[temp_date_str].values()))
                except:
                    pass
            # normalize
            if np.any(temp_vec):
                norm1 = temp_vec / np.linalg.norm(temp_vec)
            else:
                norm1 = temp_vec
            graph.append(norm1)
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=movestep)
        # tsne layout
        graph = np.array(graph)
        tsne = manifold.TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(graph)
        # # phate layout
        # graph = np.array(graph)
        # pl = phate.PHATE(n_components=2)
        # positions = pl.fit_transform(graph)
        nodes = []
        for pos, g, d in zip(positions, graph, date_list):
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes.append(dict(x=x_pos, y=y_pos, d=d, c=g.tolist()))
        links = []
        nl = len(nodes)
        for i in range(nl-1):
            links.append(dict(src=nodes[i], dst=nodes[i+1]))
        with open('../data/current/nodes.json', 'w') as f:
            json.dump(dict(nodes=nodes, links=links), f)

    def snapshot_dep(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        topic = ['放射能', '環境', '避難', '政府', '学会', '安全', '反原発']
        tpc_vecs = [self.model.wv[tpc] for tpc in topic]
        date_tpc = collections.defaultdict(lambda: {'放射能': 0, '環境': 0,
                                                    '避難': 0, '政府': 0,
                                                    '学会': 0, '安全': 0,
                                                    '反原発': 0})
        # create snapshots
        sim_thres = 0.5
        for tid, info in tid_info.items():
            words = info['words']
            temp_topic = []
            for i, tpc in enumerate(topic):
                vec1 = tpc_vecs[i]
                for word in words:
                    try:
                        vec2 = self.model.wv[word]
                        temp_sim = cos_sim(vec1, vec2)
                        if temp_sim > sim_thres:
                            temp_topic.append(tpc)
                            break
                    except:
                        pass
            date_count = info['rtd']
            for date, count in date_count.items():
                for tt in temp_topic:
                    date_tpc[date][tt] += count
        # snapshot matrix
        graph, sizelist = [], []
        timestep, overlay = 31, 28
        movestep = timestep - overlay
        start_date = datetime.date(2011, 3, 1)
        end_date = datetime.date(2016, 12, 1)
        current_date = start_date
        while current_date < end_date:
            temp_vec = np.array([0]*len(topic))
            for i in range(timestep):
                temp_date = current_date + datetime.timedelta(days=i)
                temp_date_str = temp_date.strftime('%Y-%m-%d')
                try:
                    temp_vec += np.array(
                        list(date_tpc[temp_date_str].values()))
                except:
                    pass
            sizelist.append(np.sum(temp_vec))
            # normalize
            if np.any(temp_vec):
                norm1 = temp_vec / np.linalg.norm(temp_vec)
            else:
                norm1 = temp_vec
            graph.append(norm1)
            current_date += datetime.timedelta(days=movestep)
        # tsne layout
        sizelist = np.array(sizelist)
        sizelist = sizelist / np.linalg.norm(sizelist)
        graph = np.array(graph)
        tsne = manifold.TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(graph)
        assert len(positions) == len(sizelist)
        nodes = []
        for pos, size in zip(positions, sizelist):
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes.append(dict(x=x_pos, y=y_pos, s=size))
        links = []
        nl = len(nodes)
        for i in range(nl-1):
            links.append(dict(src=nodes[i], dst=nodes[i+1]))
        with open('../data/current/nodes.json', 'w') as f:
            json.dump(dict(nodes=nodes, links=links), f)

    def similarity_dist(self):
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

        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        # convert words to vector
        # load file
        with open('../data/current/tweet_info.json', 'r') as f:
            dataset = json.load(f)
        tid_list, vec_list = [], []
        for tid, info in dataset.items():
            words = info['words']
            tid_list.append(tid)
            vec_list.append(get_vector_words(words))
        assert len(tid_list) == len(vec_list)
        # calculate distances
        length = len(vec_list)
        print(length)
        dist_mat = [[0]*length for _ in range(length)]
        for i in range(length-1):
            for j in range(i+1, length):
                dist_mat[i][j] = dist_mat[j][i] = 1 - cos_sim(vec_list[i],
                                                              vec_list[j])
        with open('../data/current/similarity_dist.json', 'w') as f:
            json.dump(dict(dist=dist_mat, tid=tid_list), f)


class Graph():
    def __init__(self):
        pass

    def tsne_layout(self):
        '''
        output nodes poistion only based on tsne algorithm
        '''
        with open('../data/current/similarity_dist.json', 'r') as f:
            dataset = json.load(f)
            dist_mat = dataset['dist']
            tid_list = dataset['tid']
        assert len(dist_mat) == len(tid_list)
        tsne = manifold.TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(dist_mat)
        print(len(positions))
        print(positions[0])
        nodes_info = []
        for index, pos in enumerate(positions):
            tid = int(tid_list[index])
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes_info.append(dict(tid=tid, x=x_pos, y=y_pos))
        with open('../data/current/nodes_position.json', 'w') as f:
            json.dump(dict(nodes=nodes_info), f)

    def process_clustering(self):
        with open('../data/current/nodes_rtdate.json', 'r') as f:
            dataset = json.load(f)
        nodes = dataset['nodes']
        positions = []
        for node in nodes:
            positions.append([node['x'], node['y']])
        labels = DBSCAN(eps=8, min_samples=100).fit_predict(positions)
        assert len(labels) == len(nodes)
        for i, node in enumerate(nodes):
            node['cluster'] = int(labels[i])
        with open('../data/current/nodes_clustering.json', 'w') as f:
            json.dump(dict(nodes=nodes), f)

    def process_retweet_info(self):
        dataset = pd.read_csv('../data/current/retweet_info.csv')
        dataset = dataset.values
        # count monthly retweet info
        # 2011 2012 2013 | 2014 2015 2016 | 2017
        # (1 *) 12 * 3   | (3 *) 4 * 3    | (6 *) 1 = 36+12+1 = 49
        # each month     | each quarter   | half year
        tid_dateinfo = collections.defaultdict(lambda: [0]*49)
        for data in dataset:
            date, tid = data[0], data[1]
            ymd = date.split('-')
            year, month = ymd[0], ymd[1]
            if year in ['2011', '2012', '2013']:
                offset = (int(year) - 2011) * 12
                index = int(month) - 1 + offset
                tid_dateinfo[tid][index] += 1
            elif year in ['2014', '2015', '2016']:
                month = int(month)
                offset = 36 + (int(year)-2014) * 4
                index = math.floor((month-1)/3) + offset
                tid_dateinfo[tid][index] += 1
            else:
                tid_dateinfo[tid][48] += 1
        with open('../data/current/nodes_clustering.json', 'r') as f:
            nodes = json.load(f)['nodes']
        for node in nodes:
            tid = node['tid']
            node['rtdate'] = tid_dateinfo[tid]
        with open('../data/current/nodes_rtdate.json', 'w') as f:
            json.dump(dict(nodes=nodes), f)


class SysTest():
    def __init__(self):
        if not os.path.exists('../data/model/wiki.model'):
            print('training model')
            self.mode_training()
        else:
            print('loading model')
            self.model = word2vec.Word2Vec.load('../data/model/wiki.model')

    def mode_training(self):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=logging.INFO)
        sentences = word2vec.Text8Corpus('../data/model/wiki_wakati.txt')
        model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)
        model.save('../data/model/wiki.model')

    def generate_testData(self):
        '''
        use data in 2011 and 2012 as test data
        '''
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

        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))

        dataset = pd.read_csv('../data/current/retweet_info.csv').values
        tid_dateinfo = collections.defaultdict(lambda: [0]*24)
        for data in dataset:
            date, tid, = data[0], str(data[1])
            ymd = date.split('-')
            year, month = ymd[0], ymd[1]
            if year in ['2011', '2012']:
                offset = (int(year)-2011)*12
                index = int(month) - 1 + offset
                tid_dateinfo[tid][index] += 1
            else:
                pass
        # calculate similarity distances
        with open('../data/current/tweet_info.json', 'r') as f:
            dataset = json.load(f)
        tid_list, vec_list, word_list = [], [], []
        for tid, info in dataset.items():
            if tid in tid_dateinfo:
                words = info['words']
                word_list.append(words)
                tid_list.append(tid)
                vec_list.append(get_vector_words(words))
        print(len(tid_list), len(vec_list), len(tid_dateinfo))
        assert len(tid_list) == len(vec_list)
        assert len(tid_list) == len(tid_dateinfo)
        # length = len(tid_list)
        # dist_mat = [[0]*length for _ in range(length)]
        # for i in range(length-1):
        #     for j in range(i+1, length):
        #         dist_mat[i][j] = dist_mat[j][i] = 1 - cos_sim(vec_list[i],
        #                                                       vec_list[j])
        # tsne layout
        nodes_list = []
        tsne = manifold.TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(np.array(vec_list))
        for index, pos in enumerate(positions):
            tid = tid_list[index]
            word = word_list[index]
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes_list.append(dict(tid=tid, x=x_pos, y=y_pos,
                                   rtd=tid_dateinfo[tid],
                                   kw=word))
        with open('../data/current/test/nodes.json', 'w') as f:
            json.dump(dict(nodes=nodes_list), f)


if __name__ == '__main__':
    nlp = NLProcessor()
    # nlp.process_csv()
    nlp.doc_to_vec_model()
    # nlp.word_corpus()
    # nlp.text_process()
    # nlp.snapshot()
    # graph = Graph()
    # graph.tsne_layout()
    # graph.process_clustering()
    # graph.process_retweet_info()
    # st = SysTest()
    # st.generate_testData()
