import json
import collections
import numpy as np
import datetime


def unify_word(word):
    word_dictionary = {
        '被ばく': '被曝',
        'セシウムさん': 'セシウム',
        '放射性セシウム': 'セシウム',
        '甲状腺': '甲状線',
        '保物': '保健物理',
        'がん': '癌',
        'ガン': '癌',
        '子ども': '子供',
        'こども': '子供',
        '児': '子供',
        'ふくしま': '福島',
        'フクシマ': '福島',
        '東電': '東京電力'
    }
    if word in word_dictionary:
        return word_dictionary[word]
    else:
        return word


def create_period_keyword_whole(length=20, timestep=5, movestep=1, save=False):
    '''
    consider a period of time one time unit
    return period_kwscore, keyword_score (except big words)
    period_kwscore: {period: {keyword: score}} | keywords with high score
    keyword_score: [(keyword, score), ] | all the keywords in descending order
    output {period: {keyword: score}}
    '''
    # bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線',
    #             '東京電力']
    bigwords = ['福島', '福島県', '原発', '福島原発', '東京電力', '放射能', '汚染']
    date_period = {}  # {date1: [date1, date2, ]}
    start = datetime.date(2011, 3, 11)
    end = datetime.date(2011, 12, 31) - datetime.timedelta(days=timestep-1)
    current = start
    while current <= end:
        datelist = []
        for i in range(timestep):
            date = (current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            datelist.append(date)
        date = datelist[0]
        date_period[date] = datelist
        current += datetime.timedelta(days=movestep)
    with open('../data/retweet-2011/sample.json', 'r') as f:
        tid_info = json.load(f)
    date_tid_count = collections.defaultdict(
        lambda: collections.defaultdict(int))
    for tid, info in tid_info.items():
        for d, r in info['rtd'].items():
            date_tid_count[d][tid] = r
    period_tid_count = {}
    for ps, period in date_period.items():
        temp = collections.Counter()
        for date in period:
            tid_count = date_tid_count[date]
            temp += collections.Counter(tid_count)
        period_tid_count[ps] = temp
    print('prepare done')
    # every period => tf + exp + rtc
    period_term_score = {}
    keyword_score = collections.defaultdict(int)
    for period, tid_count in period_tid_count.items():  # each day
        print(period)
        term_score = collections.defaultdict(float)
        # count of tweets contain word
        term_int_count = collections.defaultdict(int)
        # retweet count of word
        term_rt_count = collections.defaultdict(int)
        words_list = []
        retweet_count = 0  # all retweet counts in one day
        tweet_count = len(tid_count)  # all tweet counts in one day
        for tid, count in tid_count.items():  # each tweet
            words_list.append(tid_info[tid]['words'])
            retweet_count += count
        # retweet count in one day
        for tid, count in tid_count.items():  # each tweet
            # words = tid_info[tid]['words']
            words = [unify_word(d) for d in tid_info[tid]['words']]
            words_len = len(words)  # word count in one tweet
            # remove repeated element
            nr_words = list(set(words))
            for nr_word in nr_words:  # each word
                tf = words.count(nr_word) / words_len
                # rtc = count / retweet_count
                # term_score[nr_word] += tf * rtc
                term_score[nr_word] += tf
                term_rt_count[nr_word] += count
                term_int_count[nr_word] += 1
        for term, score in term_score.items():
            tic = term_int_count[term]  # count of tweets include nr_word
            trc = term_rt_count[term]  # retweet count of word
            exp = np.exp(tic/tweet_count)
            term_score[term] *= (exp*(trc/retweet_count))
        print('daily frequency calculation done')
        # remove unrelated terms
        for key, val in term_score.items():
            if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                    key == 'そう' or key == '今日' or key == '日本' or\
                    key == '第一' or key == '現在':
                term_score[key] = 0.0
            # remove bigwords
            if key in bigwords:
                term_score[key] = 0.0
        scores = list(term_score.values())
        average = sum(scores) / len(scores)
        thres = average * 3
        result = {}
        for key, val in term_score.items():
            if val > thres:
                result[key] = val
        result = collections.Counter(result)
        if length == 'all':
            temp_res = result.most_common()
        else:
            temp_res = result.most_common(length)
        period_term_score[period] = temp_res
        for ks in temp_res:
            kw, score = ks[0], ks[1]
            keyword_score[kw] += score
    if save:
        with open('../data/retweet-2011/top_keywords.json', 'w') as f:
            json.dump(dict(period=period_term_score,
                           keywords=keyword_score), f)
    keyword_score = sorted(keyword_score.items(), key=lambda kv: kv[1],
                           reverse=True)  # [(keyword, score), (), ()]
    return period_term_score, keyword_score


if __name__ == '__main__':
    create_period_keyword_whole()
