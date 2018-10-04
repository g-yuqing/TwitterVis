import json
import collections
import math
import datetime
import MeCab
import numpy as np
import networkx as nx
# from gensim.models import KeyedVectors
from gensim.summarization import keywords


class TopicExtractor():
    def __init__(self):
        # self.model = KeyedVectors.load_word2vec_format(
        #     '../data/model/model.vec')
        pass

    def preprocess(self):
        '''
        remove unrelated tweet
        '''
        with open('../data/current/filter/tweet_filter.json', 'r') as f:
            tid_text = json.load(f)['related']
        with open('../data/current/tweet_info.json', 'r') as f:
            all_tid_info = json.load(f)
        tid_info = {}
        for tid, info in all_tid_info.items():
            if tid in tid_text:
                tid_info[tid] = info
        with open('../data/current/topic/tweet_info.json', 'w') as f:
            json.dump(tid_info, f)

    def keyword_extract(self, evaluation=False):
        corpus, term_list = [], []
        date_tid_count = collections.defaultdict(
            lambda: collections.defaultdict(int))
        with open('../data/current/topic/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            corpus.append(info['text'])
            term_list.append(info['words'])
            for d, r in info['rtd'].items():
                date_tid_count[d][tid] = r
        # each day data
        # tf + exp + rtc
        date_term_score = {}
        for date, tid_count in date_tid_count.items():  # each day
            term_score = collections.defaultdict(float)
            content_list, retweet_count = [], []
            for tid, count in tid_count.items():  # each tweet
                content_list.append(tid_info[tid]['words'])
                retweet_count.append(tid_info[tid]['count'])
            retweet_count = sum(retweet_count)  # all retweet count in one day
            tweet_count = len(tid_count)  # all tweet count in one day
            # retweet count in one day
            for tid, count in tid_count.items():  # each tweet
                words = tid_info[tid]['words']
                word_count = len(words)  # word count in one tweet
                # remove repeated element
                nr_words = list(set(words))
                for nr_word in nr_words:  # each word
                    tf = words.count(nr_word) / word_count
                    rtc = tid_info[tid]['count'] / retweet_count
                    term_score[nr_word] += tf * rtc
            for term, score in term_score.items():
                twc = 0  # count of tweets include nr_word
                for content in content_list:  # each tweet
                    if term in content:
                        twc += 1
                        break
                exp = np.exp(twc/tweet_count)
                term_score[term] *= exp
            date_term_score[date] = term_score
        term_scoreall = collections.defaultdict(float)
        for date, term_score in date_term_score.items():
            for term, score in term_score.items():
                term_scoreall[term] += score
        graph = nx.DiGraph()
        for terms in term_list:
            for i in range(len(terms)):
                term = terms[i]
                for rest_term in (terms[:i] + terms[i+1:]):
                    weight = term_scoreall[term]
                    graph.add_edge(term, rest_term, weight=weight)
        pr = nx.pagerank(graph)
        term_score = {}
        for term, score in pr.items():
            term_score[term] = score
        # remove unrelated terms
        for key, val in term_score.items():
            if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                    key == 'そう' or key == '今日' or key == '日本':
                term_score[key] = 0.0
        # extract keywords
        # mine
        scores = list(term_score.values())
        average = sum(scores) / len(scores)
        thres = average * 1.5
        res_mine = {}
        for key, val in term_score.items():
            if val > thres:
                res_mine[key] = val
        # textrank
        tr_corpus = ''
        for terms in term_list:
            tr_corpus += (' '.join(terms)+' ')
        res_textrank = keywords(tr_corpus).split('\n')
        with open('../data/current/topic/keywords.json', 'w') as f:
            json.dump(dict(textrank=res_textrank, minedict=res_mine), f)

    def topic_extract(self, grams='bi'):
        topics = collections.defaultdict(int)
        with open('../data/current/topic/keywords.json', 'r') as f:
            dataset = json.load(f)
        textrank, mine = dataset['textrank'], dataset['minedict']
        with open('../data/current/topic/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            words, count, day = info['words'], info['count'], len(info['rtd'])
            length = len(words)
            if length == 1:
                continue
            for i in range(length-1):
                for j in range(i+1, length):
                    kw1, kw2 = words[i], words[j]
                    if kw1 != kw2 and (kw1 not in kw2) and (kw2 not in kw1):
                        sc1, sc2 = mine.get(kw1), mine.get(kw2)
                        if sc1 and sc2:
                            sc = (sc1+sc2)
                            topics[tuple(sorted([kw1, kw2]))] += sc
        # sort
        res = sorted(topics.items(), key=lambda kv: kv[1], reverse=True)
        top20 = res[:20]
        print([kv[0] for kv in top20])

    def evaluation(self):
        term_list, corpus = [], []
        with open('../data/current/topic/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        for tid, info in tid_info.items():
            term_list.append(info['words'])
            corpus.append(info['text'])
        with open('../data/current/topic/keywords.json', 'r') as f:
            dataset = json.load(f)
        textrank, mine = dataset['textrank'], dataset['minedict']
        res = sorted(mine.items(), key=lambda kv: kv[1], reverse=True)
        print(res[:100])
        # for terms, cor in zip(term_list[100:130], corpus[100:130]):
        #     print('corpus: ', cor)
        #     temp_textrank, temp_mine = [], []
        #     for term in textrank:
        #         if term in terms:
        #             temp_textrank.append(term)
        #     for term in mine:
        #         if term in terms:
        #             temp_mine.append(term)
        #     print('textrank: ', temp_textrank)
        #     print('mine: ', temp_mine)


if __name__ == '__main__':
    te = TopicExtractor()
    # te.preprocess()
    # te.keyword_extract()
    # te.evaluation()
    te.topic_extract()
