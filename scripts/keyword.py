import json
import collections
from itertools import combinations
import numpy as np
import networkx as nx


class Keyword():
    def __init__(self):
        with open('../data/retweet-2011/sample.json', 'r') as f:
            self.tid_info = json.load(f)

    def keyword_weight(self):
        corpus_list, term_list = [], []
        date_tid_count = collections.defaultdict(
            lambda: collections.defaultdict(int))
        for tid, info in self.tid_info.items():
            corpus_list.append(info['text'])
            term_list.append(info['words'])
            for d, r in info['rtd'].items():
                date_tid_count[d][tid] = r
        print('prepare done')
        # every day => tf + exp + rtc
        date_term_score = {}
        for date, tid_count in date_tid_count.items():  # each day
            print(date)
            term_score = collections.defaultdict(float)
            term_count = collections.defaultdict(int)  # count of tweets
            words_list = []
            retweet_count = 0  # all retweet counts in one day
            for tid, count in tid_count.items():  # each tweet
                words_list.append(self.tid_info[tid]['words'])
                retweet_count += count
            tweet_count = len(tid_count)  # all tweet counts in one day
            # retweet count in one day
            for tid, count in tid_count.items():  # each tweet
                words = self.tid_info[tid]['words']
                words_len = len(words)  # word count in one tweet
                # remove repeated element
                nr_words = list(set(words))
                for nr_word in nr_words:  # each word
                    tf = words.count(nr_word) / words_len
                    rtc = count / retweet_count
                    term_score[nr_word] += tf * rtc
                    term_count[nr_word] += 1
            for term, score in term_score.items():
                twc = term_count[term]  # count of tweets include nr_word
                exp = np.exp(twc/tweet_count)
                term_score[term] *= exp
            print('daily frequency calculation done')
            # PageRank
            graph = nx.DiGraph()
            for words in words_list:
                combs = combinations(words, 2)
                for comb in combs:
                    graph.add_edge(comb[0], comb[1],
                                   weight=term_score[comb[0]])
                    graph.add_edge(comb[1], comb[0],
                                   weight=term_score[comb[1]])
            pr = nx.pagerank(graph)
            print('daily PageRank calculation done')
            for term, score in pr.items():
                term_score[term] = score
            # remove unrelated terms
            for key, val in term_score.items():
                if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                        key == 'そう' or key == '今日':
                    term_score[key] = 0.0
            scores = list(term_score.values())
            average = sum(scores) / len(scores)
            thres = average * 2
            res_mine = {}
            for key, val in term_score.items():
                if val > thres:
                    res_mine[key] = val
            date_term_score[date] = res_mine
        # save to file
        with open('../data/retweet-2011/keywords.json', 'w') as f:
            json.dump(date_term_score, f)


if __name__ == '__main__':
    kw = Keyword()
    kw.keyword_weight()
