import json
import collections
from itertools import combinations
import numpy as np
import networkx as nx
import datetime


def create_date_keyword():
    '''
    output {date: {keyword: score}}
    '''
    with open('../data/retweet-2011/sample.json', 'r') as f:
        tid_info = json.load(f)
    corpus_list, term_list = [], []
    date_tid_count = collections.defaultdict(
        lambda: collections.defaultdict(int))
    for tid, info in tid_info.items():
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
            words_list.append(tid_info[tid]['words'])
            retweet_count += count
        tweet_count = len(tid_count)  # all tweet counts in one day
        # retweet count in one day
        for tid, count in tid_count.items():  # each tweet
            words = tid_info[tid]['words']
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


def create_period_keyword(count=20, timestep=5, movestep=1):
    '''
    return period_kwscore, keyword_score (except big words)
    period_kwscore: {period: {keyword: score}} | keywords with high score
    keyword_score: [(keyword, score), ] | all the keywords in descending order
    '''
    bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
    with open('../data/retweet-2011/keywords.json', 'r') as f:
        date_keywords = json.load(f)
    keyword_score = collections.defaultdict(int)
    period_kwscore = {}
    start = datetime.date(2011, 3, 11)
    end = datetime.date(2011, 12, 31) - datetime.timedelta(days=timestep-1)
    current = start
    while current <= end:
        kw_weight = collections.Counter()
        for i in range(timestep):
            date = (current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            kw_weight += collections.Counter(date_keywords[date])
        # remove big words
        for bw in bigwords:
            if bw in kw_weight:
                del kw_weight[bw]
        kwscore = kw_weight.most_common(count)
        period_kwscore[current.strftime('%Y-%m-%d')] = kwscore
        for ks in kwscore:
            kw, score = ks[0], ks[1]
            keyword_score[kw] += score
        current += datetime.timedelta(days=movestep)
    # convert keyword_score dictionary to list
    keyword_score = sorted(keyword_score.items(), key=lambda kv: kv[1],
                           reverse=True)  # [(keyword, score), (), ()]
    with open('../data/retweet-2011/top_keywords.json', 'w') as f:
        json.dump(dict(period=period_kwscore, keywords=keyword_score), f)
    return period_kwscore, keyword_score


if __name__ == '__main__':
    create_date_keyword()
    # create_period_keyword()
