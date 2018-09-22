import numpy as np
import json
import csv
import collections
import MeCab
import unicodedata
from gensim.models import word2vec, KeyedVectors, doc2vec
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE


class DataFilterWord2Vec():
    def __init__(self):
        # self.model = word2vec.Word2Vec.load('../data/model_dep/wiki.model')
        self.model = KeyedVectors.load_word2vec_format(
            '../data/model/model.vec')

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
        mt = MeCab.Tagger()
        mt.parse('')
        topic_vec_list = []
        tid_list = []
        text_list = []
        for tid, info in tid_info.items():
            text = info['text']
            tid_list.append(tid)
            text_list.append(text)
            node = mt.parseToNode(text)
            sum_vec, word_count = np.zeros(200), 0
            while node:
                fields = node.feature.split(',')
                if fields[0] == '名詞' or fields[0] == '動詞' or\
                        fields[0] == '形容詞':
                    word = node.surface
                    try:
                        if is_japanese(word):
                            sum_vec += self.model[word]
                            word_count += 1
                    except:
                        pass
                node = node.next
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

    def classification(self):
        tid_list = []
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            tid_list.append(tid)
        with open('../data/current/filter/text_dists.json', 'r') as f:
            dists = json.load(f)['dists']
        dists = np.array(dists)
        db = DBSCAN(eps=0.5, min_samples=1, metric='precomputed').fit(dists)
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

    def classification(self):
        with open('../data/current/filter/text_dists.json', 'r') as f:
            dists = json.load(f)['dists']
        tid_list = []
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            tid_list.append(tid)
        db = DBSCAN(eps=0.67, min_samples=1, metric='precomputed').fit(dists)
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
        print(len(unrelated))
        print(len(tweet_filter['related']))
        # for tid, text in unrelated.items():
        #     print(text)


if __name__ == '__main__':
    # dfwv = DataFilterWord2Vec()
    # dfwv.word_dist()
    # dfwv.classification()
    # dfwv.sweep()
    # dfwv.test()
    dfdv = DataFilterDoc2Vec()
    # dfdv.text_dist()
    # dfdv.classification()
    # dfdv.sweep()
    dfdv.test()
