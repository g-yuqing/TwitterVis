import json
import collections
import numpy as np
import unicodedata
from sklearn.cluster import DBSCAN
from gensim.models import KeyedVectors


class DataFilter():
    def __init__(self):
        self.model = KeyedVectors.load_word2vec_format(
            '../data/model/model.vec')
        self.filepath = '../data/retweet-2011/sample.json'

    def process(self):
        def is_japanese(string):
            for ch in string:
                name = unicodedata.name(ch)
                if "CJK UNIFIED" in name \
                        or "HIRAGANA" in name or "KATAKANA" in name:
                    return True
            return False
        with open(self.filepath, 'r') as f:
            tid_info = json.load(f)
        topic_vec_list = []
        tid_list = []
        text_list = []
        # vectorize
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
        with open('../data/retweet-2011/filter/dists.json', 'w') as f:
            json.dump(dict(dists=dists), f)

    def classification(self, eps=0.21):
        tid_list = []
        with open(self.filepath, 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            tid_list.append(tid)
        with open('../data/retweet-2011/filter/dists.json', 'r') as f:
            dists = json.load(f)['dists']
        dists = np.array(dists)
        db = DBSCAN(eps=eps, min_samples=1, metric='precomputed').fit(dists)
        labels = db.labels_
        clustering_tid = collections.defaultdict(list)
        assert len(labels) == len(tid_list)
        for tid, cluster in zip(tid_list, labels):
            clustering_tid[str(cluster)].append(tid)
        with open('../data/retweet-2011/filter/clustering_tid.json', 'w') as f:
            json.dump(clustering_tid, f)

    def sweep(self):
        with open(self.filepath, 'r') as f:
            tid_info = json.load(f)
        tid_text = {}
        for tid, info in tid_info.items():
            tid_text[tid] = info['text']
        # filter unconcerned tweets
        related, unrelated = {}, {}
        with open('../data/retweet-2011/filter/clustering_tid.json', 'r') as f:
            clu_tidlist = json.load(f)
        for clu, tidlist in clu_tidlist.items():
            if clu == '0':
                for tid in tidlist:
                    related[tid] = tid_text[tid]
            else:
                for tid in tidlist:
                    unrelated[tid] = tid_text[tid]
        with open('../data/retweet-2011/filter/tweet_filter.json', 'w') as f:
            json.dump(dict(related=related, unrelated=unrelated), f)


if __name__ == '__main__':
    df = DataFilter()
    df.word_dist()
