import json
import collections
# from itertools import combinations
import random
import csv
import numpy as np
# import networkx as nx
from gensim.summarization import keywords


def tutorial_data():
    '''
    each group (5 groups)
    30 tweets
    3,4 | 5,6 | 7,8 | 9,10 | 11,12
    create file: all data and sample (30) data
    '''
    with open('../data/retweet-2011/sample.json', 'r') as f:
        tid_info = json.load(f)
    group_date = {
        'A': ['2011-03', '2011-04'],
        'B': ['2011-05', '2011-06'],
        'C': ['2011-07', '2011-08'],
        'D': ['2011-09', '2011-10'],
        'E': ['2011-11', '2011-12']
    }
    # {date1: {tid1: info, tid2: info}, date2: {}}
    ym_tid_info = collections.defaultdict(dict)
    for tid, info in tid_info.items():
        date = list(info['rtd'].keys())[0]
        count = info['count']
        author = info['author']
        text = info['text']
        if text[:2] == 'RT':
            idx = text.find(':') + 2
            text = text[idx:]
        words = info['words']
        ym = date[:7]
        if tid not in ym_tid_info[ym]:
            ym_tid_info[ym][tid] = dict(date=date, count=count, author=author,
                                        text=text, words=words)
    # all data
    for group, datelist in group_date.items():
        filepath = '../data/retweet-2011/test/'+group
        datadict = {}
        for date in datelist:
            datadict.update(ym_tid_info[date])
        # extract 30 tweets
        samplekeys = random.sample(list(datadict), 30)
        sampledict = {}
        for key in samplekeys:
            sampledict[key] = datadict[key]
        with open(filepath+'/data.json', 'w') as f:
            json.dump(datadict, f)
        with open(filepath+'/sample.json', 'w') as f:
            json.dump(sampledict, f)
        # write to csv
        samplelist = []
        for tid, info in sampledict.items():
            info['tid'] = tid
            samplelist.append(info)
        with open(filepath+'/sample.csv', 'w') as f:
            csvwriter = csv.writer(f)
            ishead = True
            for data in samplelist:
                if ishead:
                    header = data.keys()
                    csvwriter.writerow(header)
                    ishead = False
                csvwriter.writerow(data.values())


def extract_keywords():
    # kw_weight = collections.Counter()
    for group in ['A', 'B', 'C', 'D', 'E']:
        print(group)
        filepath = '../data/retweet-2011/test/'+group
        with open(filepath+'/sample.json', 'r') as f:
            dataset = json.load(f)
        term_score = collections.defaultdict(float)
        # count of tweets contain word
        term_int_count = collections.defaultdict(int)
        # retweet count of word
        term_rt_count = collections.defaultdict(int)
        wordlist = []
        retweet_count = 0
        tweet_count = 0
        for _, info in dataset.items():
            retweet_count += info['count']
            tweet_count += 1
        for tid, info in dataset.items():
            if tid == '143362328841306112':
                print('wrong data')
                continue
            words = info['words']
            count = info['count']
            for _ in range(count):
                wordlist.append(words)
            wordlen = len(words)
            nr_words = list(set(words))
            for nr_word in nr_words:
                tf = words.count(nr_word)/wordlen
                term_score[nr_word] += tf
                term_rt_count[nr_word] += count
                term_int_count[nr_word] += 1
        for term, score in term_score.items():
            tic = term_int_count[term]  # count of tweets include nr_word
            trc = term_rt_count[term]  # retweet count of word
            exp = np.exp(tic/tweet_count)
            term_score[term] *= (exp*trc/retweet_count)
        for key, val in term_score.items():
            if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                    key == 'そう' or key == '今日' or key == '日本':
                term_score[key] = 0.0
        # kw_weight += collections.Counter(term_score)
        with open(filepath+'/keywords.json', 'w') as f:
            json.dump(term_score, f)
        # d = sorted(term_score.items(), key=lambda kv: kv[1])[-20:]
        # for i in d[::-1]:
        #     print(i[0])
        # test textrank
        print('============================')
        wholetext = ''
        for word in wordlist:
            temp = ' '.join(word)
            wholetext += (temp+' ')
        res = keywords(wholetext).split('\n')
        for r in res:
            print(r)


def evaluate():
    infolist = []
    for group in ['A', 'B', 'C', 'D', 'E']:
        filepath = '../data/retweet-2011/test/'+group
        with open(filepath+'/sample.json', 'r') as f:
            dataset = json.load(f)
        for _, info in dataset.items():
            infolist.append(dict(count=info['count'], words=info['words']))
    term_score = collections.defaultdict(float)
    # count of tweets contain word
    term_int_count = collections.defaultdict(int)
    # retweet count of word
    term_rt_count = collections.defaultdict(int)

    wordlist = []
    retweet_count = 0
    tweet_count = 0
    for info in infolist:
        retweet_count += info['count']
        tweet_count += 1
    for info in infolist:
        words = info['words']
        count = info['count']
        wordlist.append(words)
        wordlen = len(words)
        nr_words = list(set(words))
        for nr_word in nr_words:
            tf = words.count(nr_word)/wordlen
            term_score[nr_word] += tf
            term_rt_count[nr_word] += count
            term_int_count[nr_word] += 1
    for term, score in term_score.items():
        tic = term_int_count[term]  # count of tweets include nr_word
        trc = term_rt_count[term]  # retweet count of word
        exp = np.exp(tic/tweet_count+trc/retweet_count)
        term_score[term] *= exp
    for key, val in term_score.items():
        if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                key == 'そう' or key == '今日' or key == '日本':
            term_score[key] = 0.0
    with open(filepath+'/keywords.json', 'w') as f:
        json.dump(term_score, f)
    print('mine')
    d = sorted(term_score.items(), key=lambda kv: kv[1])[-20:]
    for i in d[::-1]:
        print(i[0])
    # test textrank
    print('pagerank')
    wholetext = ''
    for word in wordlist:
        temp = ' '.join(word)
        wholetext += (temp+' ')
    res = keywords(wholetext).split('\n')
    for r in res:
        print(r)


if __name__ == '__main__':
    # tutorial_data()
    extract_keywords()
    # evaluate()
