import json
import collections
import datetime
import numpy as np
from sklearn import manifold


class SampleEval(object):
    def create_test_data(self, length=20, timestep=5, movestep=1, save=False):
        testdata = {}
        tweet_thres = 3
        general_rt_thres = 5
        leap_rt_thres = 20
        general_kw = '汚染'
        leap_kw1 = '子供'  # 4/12
        leap_kw2 = 'ベクレル'  # 3/20
        with open('../data/retweet-2011/sample.json', 'r') as f:
            tid_info = json.load(f)
        date_tid_count = collections.defaultdict(
            lambda: collections.defaultdict(int))
        for tid, info in tid_info.items():
            for d, r in info['rtd'].items():
                date_tid_count[d][tid] = r
        start = datetime.date(2011, 3, 11)
        end = datetime.date(2011, 3, 31)
        current = start
        # general keyword
        while current <= end:
            temp = {}
            datestr = current.strftime('%Y-%m-%d')
            tid_count = date_tid_count[datestr]
            for tid, count in tid_count.items():
                words = tid_info[tid]['words']
                if general_kw in words and count < general_rt_thres:
                    temp[tid] = count
                if len(temp) >= tweet_thres:
                    # testdata[datestr] = temp
                    break
            testdata[datestr] = temp
            current += datetime.timedelta(days=movestep)
        # leap keyword1
        current = start
        done = False
        while current <= end:
            datestr = current.strftime('%Y-%m-%d')
            tid_count = date_tid_count[datestr]
            for tid, count in tid_count.items():
                words = tid_info[tid]['words']
                if leap_kw1 in words and count > leap_rt_thres:
                    testdata[datestr][tid] = count
                    print('keyword1 is done: ', datestr)
                    done = True
                    break
            if done:
                break
            current += datetime.timedelta(days=movestep)
        # leap keyword2
        current = start
        done = False
        while current <= end:
            datestr = current.strftime('%Y-%m-%d')
            tid_count = date_tid_count[datestr]
            for tid, count in tid_count.items():
                words = tid_info[tid]['words']
                if leap_kw2 in words and count > leap_rt_thres:
                    testdata[datestr][tid] = count
                    print('keyword2 is done: ', datestr)
                    done = True
                    break
            if done:
                break
            current += datetime.timedelta(days=movestep)
        if save:
            savepath = '../data/retweet-2011/state-evaluation/testdata.json'
            json.dump(testdata, open(savepath, 'w'))
        return tid_info, testdata  # {date: {tid: count}}

    def evaluation(self, length=2, timestep=2, movestep=1):
        bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線',
                    '東京電力']
        tid_info, date_tid_count = self.create_test_data(length, timestep,
                                                         movestep, False)
        # calculate score============================================
        date_period = {}  # {date1: [date1, date2, ]}
        start = datetime.date(2011, 3, 11)
        end = datetime.date(2011, 3, 31) - datetime.timedelta(days=timestep-1)
        current = start
        while current <= end:
            datelist = []
            for i in range(timestep):
                date = (
                    current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                datelist.append(date)
            date = datelist[0]
            date_period[date] = datelist
            current += datetime.timedelta(days=movestep)
        period_tid_count = {}
        for ps, period in date_period.items():
            temp = collections.Counter()
            for date in period:
                if date not in date_tid_count:
                    continue
                tid_count = date_tid_count[date]
                temp += collections.Counter(tid_count)
            period_tid_count[ps] = temp
        # score
        period_kwscore = {}
        keyword_score = collections.defaultdict(int)
        for period, tid_count in period_tid_count.items():  # each day
            # print(period)
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
                words = tid_info[tid]['words']
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
            # print('daily frequency calculation done')
            # remove unrelated terms
            for key, val in term_score.items():
                if len(key) <= 1 or key == 'たち' or key == 'さん' or\
                        key == 'そう' or key == '今日' or key == '日本':
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
            period_kwscore[period] = temp_res
            print(period, temp_res)
            for ks in temp_res:
                kw, score = ks[0], ks[1]
                keyword_score[kw] += score
        savepath = '../data/retweet-2011/state-evaluation/top_keywords.json'
        json.dump(dict(period=period_kwscore, keywords=keyword_score),
                  open(savepath, 'w'))
        # return period_kwscore, keyword_score
        # generate state view===========================================
        # vectorize
        keyword_score = sorted(keyword_score.items(), key=lambda kv: kv[1],
                               reverse=True)
        allkeywords = list(map(lambda d: d[0], keyword_score))
        ratiolist = []
        datelist = []
        veclist = []  # dately vector
        veclen = len(keyword_score)
        for period, kw_scores in period_kwscore.items():
            vec = np.zeros(veclen)
            for kw_s in kw_scores:
                idx = allkeywords.index(kw_s[0])
                vec[idx] = kw_s[1]
            # normalize
            ratio = np.linalg.norm(vec)
            vec = vec / ratio
            ratiolist.append(ratio)
            datelist.append(period)
            veclist.append(vec)
        graph = np.array(veclist)
        # nodes
        nodes = []
        tsne = manifold.TSNE(n_components=2, perplexity=5,
                             early_exaggeration=12, random_state=0)
        tsnepos = tsne.fit_transform(graph)
        for tpos, g, d, r in\
                zip(tsnepos, graph, datelist, ratiolist):
            nodes.append(dict(x=float(tpos[0]), y=float(tpos[1]),
                              date=d, kw=g.tolist(), ratio=r))
        # links
        links = []
        for i in range(len(nodes)-1):
            srcn, dstn = nodes[i], nodes[i+1]
            src = dict(x=srcn['x'], y=srcn['y'])
            dst = dict(x=dstn['x'], y=dstn['y'])
            links.append(dict(src=src, dst=dst))
        # save to json file
        savepath = '../data/retweet-2011/state-evaluation/state_graph.json'
        json.dump(dict(nodes=nodes, links=links), open(savepath, 'w'))


class StatisticEval(object):
    def evaluation():
        '''
        analyze:
        3/17,3/18, leaping, 3/19,3/20
        params:
        timestep=5, movestep=1, length=20
        '''
        bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線',
                    '東京電力']
        with open('../data/retweet-2011/sample.json', 'r') as f:
            tid_info = json.load(f)
        date_tid_count = collections.defaultdict(
            lambda: collections.defaultdict(int))
        for tid, info in tid_info.items():
            for d, r in info['rtd'].items():
                date_tid_count[d][tid] = r
        period1 = ['2011-03-17', '2011-03-18', '2011-03-19',
                   '2011-03-20', '2011-03-21']
        period2 = ['2011-03-18', '2011-03-19', '2011-03-20',
                   '2011-03-21', '2011-03-22']
        period3 = ['2011-03-19', '2011-03-20', '2011-03-21',
                   '2011-03-22', '2011-03-23']
        period4 = ['2011-03-20', '2011-03-21', '2011-03-22',
                   '2011-03-23', '2011-03-24']
        result = {}
        for period in [period1, period2, period3, period4]:
            print('================================')
            tcount = 0  # tweet counts
            rtcount = 0  # retweet counts
            kwcount = collections.defaultdict(int)  # keywords in tweet
            kwcountall = collections.defaultdict(int)  # keywords in all
            for date in period:
                tid_count = date_tid_count[date]
                tcount += len(tid_count)
                for tid, count in tid_count.items():
                    rtcount += count
                    for word in tid_info[tid]['words']:
                        kwcount[word] += 1
                        kwcountall[word] += count
            # filter:
            for key in kwcount:
                if key in bigwords or\
                        len(key) <= 1 or key == 'たち' or key == 'さん' or\
                        key == 'そう' or key == '今日' or key == '日本':
                    kwcount[key] = 0
            for key in kwcountall:
                if key in bigwords or\
                        len(key) <= 1 or key == 'たち' or key == 'さん' or\
                        key == 'そう' or key == '今日' or key == '日本':
                    kwcountall[key] = 0

            kwsum = sum(list(kwcount.values()))
            kwrtsum = sum(list(kwcountall.values()))
            kwcount = sorted(kwcount.items(), key=lambda kv: kv[1],
                             reverse=True)  # [(keyword, count), (), ()]
            kwcountall = sorted(kwcountall.items(), key=lambda kv: kv[1],
                                reverse=True)  # [(keyword, count), (), ()]
            temp1, temp2 = 0, 0
            tempres = []
            for kwc in kwcount:
                kw, count = kwc[0], kwc[1]
            for kwc in kwcountall:
                kw, count = kwc[0], kwc[1]
                temp2 += count
                if temp2/kwrtsum < 0.5:
                    tempres.append((kw, count))
            res = dict(tc=tcount, rtc=rtcount, kwc=kwcount[:20],
                       kwcall=kwcountall[:20],
                       kwsum=kwsum, kwrtsum=kwrtsum, tp=tempres)
            for d in kwcount[:20]:
                print(d[0], ': ', d[1], ' -- ', d[1]/tcount)
            print('--->')
            for d in kwcountall[:20]:
                print(d[0], ': ', d[1], ' -- ', d[1]/rtcount)
            print('---------------')


if __name__ == '__main__':
    se = StatisticEval
    se.evaluation()
