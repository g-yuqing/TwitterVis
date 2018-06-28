import json
import numpy as np
import pandas as pd
import collections
import itertools
from operator import itemgetter
from scipy.spatial import ConvexHull
from sklearn.cluster import DBSCAN
from scipy.spatial import distance
from sklearn.metrics import jaccard_similarity_score


class Processor(object):

    def __init__(self):
        '''
        ignored = [717922257591357440, 723135095998021633, 723139415464235009,
                   729273865554137088, 459225831399624704, 465151176447520770,
                   467486287952220160, 469332281467736065, 840917328837591044,
                   841398081773948928, 470877507260923904, 472116952429633536,
                   291193150951804931, 848521527989460993, 572797359333093379,
                   580674454969176064, 580991509786333184, 865125847165947904,
                   587251589322182656, 588674041835163648, 589506230508466177,
                   318661603438497792, 321457685985894400, 332828892433887232,
                   333219205090516993, 333386802276745216, 333560962919575553,
                   335960245501296641, 338155963666268160, 338301663712522245]
        '''
        pass

    def tweet_count_sorteds(self):
        '''
        sort tweet by retweet count
        '''
        dataset = pd.read_csv('../data/quarter/quarter.csv')
        dataset = dataset.values
        year_info = collections.defaultdict(list)
        year_tweet_count = collections.defaultdict(
                lambda: collections.defaultdict(int))
        for data in dataset:
            ymd, user, influencer, rid = data[0], data[1], data[2], data[3]
            year = ymd.split('-')[0]
            year_tweet_count[year][rid] += 1
            year_info[year].append(dict(user=user, influencer=influencer,
                                        rid=rid))
        year_tweet_count_sorted = {}
        for year, info_dict in year_tweet_count.items():
            year_tweet_count_sorted[year] = collections.OrderedDict(
                sorted(info_dict.items(), key=itemgetter(1), reverse=True))
        with open('../data/quarter/tweet_count_sorted.json', 'w') as f:
            json.dump(year_tweet_count_sorted, f)

    def forcelayout(self):
        '''
        return forcelayout data
        '''
        # get tweet id
        tweet_limit = 80
        with open('../data/quarter/tweet_count_sorted.json', 'r') as f:
            dataset = json.load(f)
        year_tweet_count = collections.defaultdict(list)
        for year, info in dataset.items():
            tcount = 0
            for tweet, count in info.items():
                # if tcount >= tweet_limit:
                #     break
                if count < tweet_limit and tcount > 30:
                    break
                else:
                    year_tweet_count[year].append(dict(tid=tweet, count=count))
                    tcount += 1
        # remove meaningless tweet
        ignored = [717922257591357440, 723135095998021633, 723139415464235009,
                   729273865554137088, 459225831399624704, 465151176447520770,
                   467486287952220160, 469332281467736065, 840917328837591044,
                   841398081773948928, 470877507260923904, 472116952429633536,
                   291193150951804931, 848521527989460993, 572797359333093379,
                   580674454969176064, 580991509786333184, 865125847165947904,
                   587251589322182656, 588674041835163648, 589506230508466177,
                   318661603438497792, 321457685985894400, 332828892433887232,
                   333219205090516993, 333386802276745216, 333560962919575553,
                   335960245501296641, 338155963666268160, 338301663712522245]
        revised_year_tweet_count = collections.defaultdict(list)
        for year, tweet_info in year_tweet_count.items():
            for temp in tweet_info:
                if int(temp['tid']) in ignored:
                    print('meaningless tweet: ', temp['tid'])
                    continue
                else:
                    revised_year_tweet_count[year].append(temp)
        year_tweet_count = revised_year_tweet_count
        # generate forcelayout data {nodes:[], edges: []}
        filename = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        for fn in filename:
            nodes, edges = [], []
            node_count = 0
            edge_count = 0
            node_id = {}
            # tweet node
            for tweet_info in year_tweet_count[fn]:
                tid, count = tweet_info['tid'], tweet_info['count']
                if tid not in node_id:
                    node_id[tid] = node_count
                    node_count += 1
                    nodes.append(dict(
                        id=node_id[tid], name='T'+tid, degree=count))
            # user node, retweet edges
            dataset = pd.read_csv('../data/quarter/quarter.csv')
            dataset = dataset.values
            for data in dataset:
                ymd, user, rid = str(data[0]), str(data[1]), str(data[3])
                year = ymd.split('-')[0]
                if year == fn:
                    for tweet_info in year_tweet_count[year]:
                        tid, count = tweet_info['tid'], tweet_info['count']
                        if tid == rid:
                            if user not in node_id:
                                node_id[user] = node_count
                                node_count += 1
                                nodes.append(dict(
                                    id=node_id[user], name='U'+user))
                            edges.append(dict(
                                id=edge_count,
                                source=node_id[rid], target=node_id[user]))
                            edge_count += 1
            jsonfile = dict(nodes=nodes, edges=edges)
            with open('../data/quarter/node_edge/'+fn+'.json', 'w') as f:
                json.dump(jsonfile, f)

            def extract_id():
                with open('../data/quarter/tweet_count_sorted.json', 'r') as f:
                    dataset = json.load(f)
                result = []
                for year, info in dataset.items():
                    step = 0
                    for tid, count in info.items():
                        if count < 80 and step > 30:
                            break
                        else:
                            result.append(tid)
                        step += 1
                print(result)
                print(len(result))

    def tweet_info(self):
        dataset = pd.read_csv('../data/quarter/quarter_full.csv')
        dataset = dataset.values
        tweet_info = collections.defaultdict(dict)
        for data in dataset:
            tid, words, date, author, text = data[0], data[1], data[2],\
                data[3], data[4]
            year = date.split('-')[0]
            if pd.isnull(words):
                words = 'none'
            tweet_info[year]['T'+str(tid)] = dict(tid=tid, words=words,
                                                  date=date, author=author,
                                                  text=text)
        with open('../data/quarter/tweet_info.json', 'w') as f:
            json.dump(tweet_info, f)

    def user_count(self):
        year_user_count = {}
        filename = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        for fn in filename:
            with open('../data/quarter/node_edge/'+fn+'.json', 'r') as f:
                edges = json.load(f)['edges']
            user_count = collections.defaultdict(int)
            for edge in edges:
                target = edge['target']
                user_count[target] += 1
            year_user_count[fn] = collections.OrderedDict(
                sorted(user_count.items(), key=itemgetter(1), reverse=True))
        with open('../data/quarter/year_user_count.json', 'w') as f:
            json.dump(year_user_count, f)

    def cluster_tweet(self):
        filename = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        for fn in filename:
            with open('../data/quarter/node_edge/'+fn+'.json', 'r') as f:
                node_edge = json.load(f)
            # generate binary vector
            nodes = node_edge['nodes']
            for i, node in enumerate(nodes):
                if 'degree' not in node:
                    offset = i
                    break
            tweet_id = range(offset)
            user_id = range(offset, len(nodes))
            length = len(user_id)
            tweet_vector = {}
            for tid in tweet_id:
                tweet_vector[tid] = [0] * length
            edges = node_edge['edges']
            for edge in edges:
                tid, uid = edge['source'], edge['target']
                tweet_vector[tid][uid-offset] = 1
            # calculate similarity
            tweet_count = len(tweet_id)
            similarity = [[0]*tweet_count for _ in range(tweet_count)]
            for i in range(tweet_count):
                for j in range(i, tweet_count):
                    if i == j:
                        similarity[i][j] = 1
                    else:
                        similarity[i][j] = similarity[j][i] = \
                            distance.cosine(tweet_vector[i],
                                            tweet_vector[j])
            db = DBSCAN(eps=0.99, min_samples=3, metric='precomputed')
            clusters = db.fit_predict(similarity)
            with open('../static/graph/'+fn+'.json', 'r') as f:
                dataset = json.load(f)
            nodes = dataset['nodes']
            colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
                      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe',
                      '#008080', '#e6beff', '#aa6e28', '#fffac8', '#800000',
                      '#aaffc3', '#808000', '#ffd8b1', '#000080', '#808080']
                      # '#FFFFFF', '#000000']
            for i, cluster in enumerate(clusters):
                nodes[i]['cluster'] = int(cluster)
                nodes[i]['color'] = colors[cluster]
            with open('../data/quarter/cluster/'+fn+'.json', 'w') as f:
                jsonfile = dict(nodes=nodes, edges=dataset['edges'])
                json.dump(jsonfile, f)


if __name__ == '__main__':
    processor = Processor()
    # processor.tweet_count_sorteds()
    # processor.forcelayout()
    processor.user_count()
    # processor.tweet_info()
    # processor.cluster_tweet()
