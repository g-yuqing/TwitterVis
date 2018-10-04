import numpy as np
import pandas as pd
import json
import csv
import collections
import MeCab
import unicodedata
# from gensim.models import word2vec
from random import shuffle
from gensim.models import KeyedVectors, doc2vec
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
import matplotlib
import matplotlib.pyplot as plt


class DataFilterWord2Vec():
    def __init__(self):
        # self.model = word2vec.Word2Vec.load('../data/model_dep/wiki.model')
        # self.model = KeyedVectors.load_word2vec_format(
        #     '../data/model/model.vec')
        pass

    def process(self):
        def is_japanese(string):
            for ch in string:
                name = unicodedata.name(ch)
                if "CJK UNIFIED" in name \
                        or "HIRAGANA" in name or "KATAKANA" in name:
                    return True
            return False
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        # mt = MeCab.Tagger()
        # mt.parse('')
        topic_vec_list = []
        tid_list = []
        text_list = []
        for tid, info in tid_info.items():
            text = info['text']
            words = info['words']
            tid_list.append(tid)
            text_list.append(text)
            sum_vec, word_count = np.zeros(200), 0
            for word in words:
                try:
                    sum_vec += self.model[word]
                    word_count += 1
                except:
                    pass
            # node = mt.parseToNode(text)
            # sum_vec, word_count = np.zeros(200), 0
            # while node:
            #     fields = node.feature.split(',')
            #     if fields[0] == '名詞' or fields[0] == '動詞' or\
            #             fields[0] == '形容詞':
            #         word = node.surface
            #         try:
            #             if is_japanese(word):
            #                 sum_vec += self.model[word]
            #                 word_count += 1
            #         except:
            #             pass
            #     node = node.next
            if word_count == 0:
                topic_vec_list.append(sum_vec)
            else:
                topic_vec_list.append(sum_vec/word_count)
        return topic_vec_list, tid_list, text_list

    def word_dist(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        topic_vec_list, tid_list, text_list = self.process()
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
        with open('../data/current/filter/dists.json', 'w') as f:
            json.dump(dict(dists=dists), f)

    def classification(self, eps=0.21):
        tid_list = []
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            tid_list.append(tid)
        with open('../data/current/filter/dists.json', 'r') as f:
            dists = json.load(f)['dists']
        dists = np.array(dists)
        db = DBSCAN(eps=eps, min_samples=1, metric='precomputed').fit(dists)
        labels = db.labels_
        clustering_tid = collections.defaultdict(list)
        assert len(labels) == len(tid_list)
        for tid, cluster in zip(tid_list, labels):
            clustering_tid[str(cluster)].append(tid)
        with open('../data/current/filter/clustering_tid.json', 'w') as f:
            json.dump(clustering_tid, f)

    def sweep(self):
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        tid_text = {}
        for tid, info in tid_info.items():
            tid_text[tid] = info['text']
        # filter unconcerned tweets
        related, unrelated = {}, {}
        with open('../data/current/filter/clustering_tid.json', 'r') as f:
            clu_tidlist = json.load(f)
        for clu, tidlist in clu_tidlist.items():
            if clu == '0':
                for tid in tidlist:
                    related[tid] = tid_text[tid]
            else:
                for tid in tidlist:
                    unrelated[tid] = tid_text[tid]
        with open('../data/current/filter/tweet_filter.json', 'w') as f:
            json.dump(dict(related=related, unrelated=unrelated), f)

    def post_visualize(self):
        with open('../data/current/filter/clustering_tid.json', 'r') as f:
            dataset = json.load(f)
        tid_clus = {}
        for clu, tidlist in dataset.items():
            for tid in tidlist:
                tid_clus[tid] = clu
        topic_vec_list, tid_list, text_list = self.process()
        tsne = TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(topic_vec_list)
        # save to text
        nodes = []
        for tid, text, pos in zip(tid_list, text_list, positions):
            xp, yp = float(pos[0]), float(pos[1])
            clu = tid_clus[tid]
            nodes.append(dict(tid=tid, x=xp, y=yp, text=text, c=clu))
        with open('../data/current/filter/text_post_visualize.json', 'w') as f:
            json.dump(dict(nodes=nodes), f)

    def test(self):
        with open('../data/current/filter/tweet_filter.json', 'r') as f:
            tweet_filter = json.load(f)
        unrelated = tweet_filter['unrelated']
        for tid, text in unrelated.items():
            print(text)


class DataFilterDoc2Vec():
    def __init__(self):
        self.model = doc2vec.Doc2Vec.load('../data/model/tweet.model')

    def text_dist(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        tid_list = []
        length = len(tid_info)
        dists = [[0]*length for _ in range(length)]
        row = 0
        for tid, info in tid_info.items():
            tid_list.append(tid)
            vec1 = self.model.docvecs[str(row)]
            for i in range(row+1, length):
                vec2 = self.model.docvecs[str(i)]
                dists[row][i] = dists[i][row] = 1 - cos_sim(vec1, vec2)
            row += 1
        with open('../data/current/filter/text_dists.json', 'w') as f:
            json.dump(dict(dists=dists), f)

    def classification(self, eps=0.69):
        with open('../data/current/filter/text_dists.json', 'r') as f:
            dists = json.load(f)['dists']
        tid_list = []
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            tid_list.append(tid)
        db = DBSCAN(eps=eps, min_samples=1, metric='precomputed').fit(dists)
        labels = db.labels_
        clustering_tid = collections.defaultdict(list)
        assert len(labels) == len(tid_list)
        for tid, cluster in zip(tid_list, labels):
            clustering_tid[str(cluster)].append(tid)
        with open('../data/current/filter/text_clustering_tid.json', 'w') as f:
            json.dump(clustering_tid, f)

    def sweep(self):
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        tid_text = {}
        for tid, info in tid_info.items():
            tid_text[tid] = info['text']
        # filter unconcerned tweets
        related, unrelated = {}, {}
        with open('../data/current/filter/text_clustering_tid.json', 'r') as f:
            clu_tidlist = json.load(f)
        for clu, tidlist in clu_tidlist.items():
            if clu == '0':
                for tid in tidlist:
                    related[tid] = tid_text[tid]
            else:
                for tid in tidlist:
                    unrelated[tid] = tid_text[tid]
        with open('../data/current/filter/text_tweet_filter.json', 'w') as f:
            json.dump(dict(related=related, unrelated=unrelated), f)

    def test(self):
        '''
        check unrelated tweet content
        '''
        with open('../data/current/filter/text_tweet_filter.json', 'r') as f:
            tweet_filter = json.load(f)
        unrelated = tweet_filter['unrelated']
        for tid, text in unrelated.items():
            print(text)


class Evaluation():
    def generate_sample_data(self):
        '''
        add tag column manually
        '''
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        sample_tid = list(tid_info.keys())
        shuffle(sample_tid)
        sample_tid = sample_tid[:1000]
        sample_data = []
        for tid in sample_tid:
            sample_data.append(dict(tid=tid, text=tid_info[tid]['text']))
        with open('../data/current/filter/sample_tid_text.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['tid', 'text'])
            writer.writeheader()
            writer.writerows(sample_data)

    def evaluate(self):
        dataset = pd.read_csv('../data/current/filter/sample_tid_text_tag.csv')
        dataset = dataset.values
        tid_tag = {}
        for data in dataset:
            tid, tag = str(data[0]), int(data[1])
            tid_tag[tid] = tag
        # word2vec model
        with open('../data/current/filter/tweet_filter.json', 'r') as f:
            tweet_filter = json.load(f)
        unrelated = tweet_filter['unrelated']
        related = tweet_filter['related']
        res1 = dict(snbi=0, snan=0, siai=0, sibn=0)
        for tid, tag in tid_tag.items():
            if tag == 0:  # unrelated
                if tid in unrelated:
                    res1['snan'] += 1  # +2
                else:
                    assert tid in related
                    res1['snbi'] += 1  # -2
            else:  # related
                if tid in unrelated:
                    res1['sibn'] += 1  # -3
                else:
                    assert tid in related
                    res1['siai'] += 1  # +3
        # doc2vec model
        with open('../data/current/filter/text_tweet_filter.json', 'r') as f:
            text_tweet_filter = json.load(f)
        text_unrelated = text_tweet_filter['unrelated']
        text_related = text_tweet_filter['related']
        res2 = dict(snbi=0, snan=0, siai=0, sibn=0)
        for tid, tag in tid_tag.items():
            if tag == 0:  # unrelated
                if tid in text_unrelated:
                    res2['snan'] += 1
                else:
                    assert tid in text_related
                    res2['snbi'] += 1
            else:  # related
                if tid in text_unrelated:
                    res2['sibn'] += 1
                else:
                    assert tid in text_related
                    res2['siai'] += 1
        # print(res1)
        # print('=================')
        # print(res2)
        return res1, res2


def test():
    dfwv = DataFilterWord2Vec()
    dfdv = DataFilterDoc2Vec()
    eva = Evaluation()
    jsonfile = {}
    for eps in np.arange(0.1, 1, 0.01):
        dfwv.classification(eps)
        dfwv.sweep()
        dfdv.classification(eps)
        dfdv.sweep()
        res1, res2 = eva.evaluate()
        jsonfile[str(eps)] = dict(word=res1, doc=res2)
    with open('../data/current/filter/eps.json', 'w') as f:
        json.dump(jsonfile, f)


def visualize():
    def score(res):
        score = \
            res['snan']*0.02-res['snbi']*0.01-res['sibn']*0.02+res['siai']*0.01
        return score
    with open('../data/current/filter/eps.json', 'r') as f:
        dataset = json.load(f)
    xs = np.arange(0.1, 1, 0.01)
    keys = sorted([float(k) for k in dataset.keys()])
    keys = [str(k) for k in keys]
    ys1, ys2 = [], []
    for key in keys:
        word = dataset[key]['word']
        doc = dataset[key]['doc']
        ys1.append(score(word))
        ys2.append(score(doc))
    fig = plt.figure(figsize=(11, 8))
    ax1 = fig.add_subplot(111)
    ax1.plot(xs, ys1, label='word2vec')
    ax1.plot(xs, ys2, label='doc2vec')
    ax1.legend(loc=4)
    plt.xlabel('eps', fontsize=17)
    plt.ylabel('score', fontsize=17)
    # plt.show()
    fig.savefig('result.pdf', bbox_inches='tight')


if __name__ == '__main__':
    # def score(res):
    #     score = res['snan']*2-res['snbi']*2-res['sibn']*3+res['siai']*3
    #     return score
    # dfwv = DataFilterWord2Vec()
    # # dfwv.word_dist()
    # dfwv.classification()
    # dfwv.sweep()
    # # dfwv.test()
    # dfdv = DataFilterDoc2Vec()
    # # # dfdv.text_dist()
    # dfdv.classification()
    # dfdv.sweep()
    # # # dfdv.test()
    # eva = Evaluation()
    # res1, res2 = eva.evaluate()
    # print(score(res1), score(res2))
    # test()
    visualize()
