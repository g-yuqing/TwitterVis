import json
import numpy as np
import random
import collections
from sklearn import manifold
import datetime


def generate_data_task2_easy(topic_num, time_len):
    '''
    10 topics/20 topics
    '''
    topic_scores = collections.defaultdict(list)
    for time in range(time_len):
        if time < 12:  # pattern1
            # 1
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 15, 17
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time < 24:  # pattern2
            # 4
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 6:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 8:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 9, 11
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time < 36:  # pattern2
            # 3
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 15, 17
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 9, 11
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        else:  # pattern2
            # 2
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 14, 16
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
    return topic_scores


def generate_data_task2_hard(topic_num, time_len):
    '''
    10 topics/20 topics
    '''
    topic_scores = collections.defaultdict(list)
    for time in range(time_len):
        if time < 12:  # pattern1
            # 1
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 13:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time < 24:  # pattern2
            # 4
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 7:
                    minVal, maxVal = 12, 14
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 14:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time < 36:  # pattern2
            # 3
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 6:
                    minVal, maxVal = 15, 17
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 8:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 16:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        else:  # pattern2
            # 2
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 5:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 12:
                    minVal, maxVal = 9, 11
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 17:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
    return topic_scores


def generate_data_task1_easy(topic_num, time_len):
    '''
    10 topics/20 topics
    '''
    topic_scores = collections.defaultdict(list)
    for time in range(time_len):
        if time <= 14:  # pattern1
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 15, 17
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 18, 20
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 3, 5
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time <= 34:  # pattern2
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 2:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 8:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        else:  # pattern3
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 4:
                    minVal, maxVal = 9, 11
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 7:
                    minVal, maxVal = 12, 14
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 14, 16
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
    return topic_scores


def generate_data_task1_hard(topic_num, time_len):
    '''
    10 topics/20 topics
    '''
    topic_scores = collections.defaultdict(list)
    for time in range(time_len):
        if time <= 12:  # pattern1
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 7:
                    minVal, maxVal = 6, 8
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 12:
                    minVal, maxVal = 5, 7
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 16:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time <= 31:  # pattern2
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 4:
                    minVal, maxVal = 16, 18
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 7:
                    minVal, maxVal = 4, 6
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 12:
                    minVal, maxVal = 12, 14
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 5, 7
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        else:  # pattern3
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 2:
                    minVal, maxVal = 14, 16
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 8:
                    minVal, maxVal = 4, 6
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 12:
                    minVal, maxVal = 10, 12
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 11, 13
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
    return topic_scores


def generate_data_task3(topic_num, time_len):
    '''
    10 topics/20 topics
    '''
    topic_scores = collections.defaultdict(list)
    # for i in range(topic_num):
    #     topic = 'topic'+str(i+1)
    #     scores = []
    #     for j in range(time_len):
    #         if j == 1 or j == 10 or j == 20:
    #             scores.append(random.randint(5, 10))
    #         else:
    #             scores.append(random.randint(25, 30))
    #     # noise = np.random.normal(0, 1, time_len)
    #     # topic_score[topic] = (np.array(scores)+noise).tolist()
    #     topic_score[topic] = scores
    # path = '../data/retweet-2011/model-data/task1-raw.json'
    # with open(path, 'w') as f:
    #     json.dump(topic_score, f)
    # return topic_score
    for time in range(time_len):
        if time <= 5:  # pattern1
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 3:
                    minVal, maxVal = 3, 5
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 6:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 6, 8
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time <= 15:  # pattern2
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 2:
                    minVal, maxVal = 8, 10
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 8:
                    minVal, maxVal = 5, 7
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 16, 18
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        elif time <= 45:  # pattern3
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 4:
                    minVal, maxVal = 14, 16
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 7:
                    minVal, maxVal = 7, 9
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 2, 4
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
        else:  # pattern4
            for tp in range(topic_num):
                topic = 'topic'+str(tp)
                # determine pattern
                if tp < 5:
                    minVal, maxVal = 5, 7
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                elif tp < 7:
                    minVal, maxVal = 13, 15
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
                else:
                    minVal, maxVal = 5, 7
                    val = random.randint(minVal, maxVal)
                    topic_scores[topic].append(val)
    return topic_scores


def graph_data_task2(topic_scores):
    time_len = len(topic_scores['topic1'])
    date_topic_score = {}
    topic_sums = collections.defaultdict(float)
    basedate = datetime.date(2019, 1, 1)
    for t in range(time_len):
        date = basedate + datetime.timedelta(days=t)
        datestr = date.strftime('%Y-%m-%d')
        temp = []
        for topic, scores in topic_scores.items():
            temp.append((topic, scores[t]))
            topic_sums[topic] += scores[t]
        date_topic_score[datestr] = temp
    path1 = '../data/retweet-2011/model-data/task2/top-topics.json'
    with open(path1, 'w') as f:
        json.dump(dict(period=date_topic_score,
                       keywords=topic_sums), f)
    topic_sums = sorted(topic_sums.items(), key=lambda kv: kv[1],
                        reverse=True)  # [(topic1, scoresum), (), ()]
    # graph
    alltopics = list(map(lambda d: d[0], topic_sums))
    veclen = len(topic_sums)
    veclist = []
    datelist = []
    ratiolist = []
    for datestr, tp_scores in date_topic_score.items():
        vec = np.zeros(veclen)
        for tps in tp_scores:
            idx = alltopics.index(tps[0])
            vec[idx] = tps[1]
        ratio = np.linalg.norm(vec)
        vec = vec / ratio
        ratiolist.append(ratio)
        datelist.append(datestr)
        veclist.append(vec)
    graph = np.array(veclist)
    nodes = []
    tsne = manifold.TSNE(n_components=2, perplexity=30,
                         early_exaggeration=12)
    tsnepos = tsne.fit_transform(graph)
    for tpos, date, ratio in zip(tsnepos, datelist, ratiolist):
        nodes.append(dict(x=float(tpos[0]), y=float(tpos[1]), date=date,
                          ratio=ratio))
    links = []
    for i in range(len(nodes)-1):
        srcn, dstn = nodes[i], nodes[i+1]
        src = dict(x=srcn['x'], y=srcn['y'])
        dst = dict(x=dstn['x'], y=dstn['y'])
        links.append(dict(src=src, dst=dst))
    # save to json file
    path2 = '../data/retweet-2011/model-data/task2/state-graph.json'
    with open(path2, 'w') as f:
        json.dump(dict(nodes=nodes, links=links), f)


if __name__ == '__main__':
    topic_num = 20
    time_len = 50
    # graph_data_task2(generate_data_task2_hard(topic_num, time_len))
    graph_data_task2(generate_data_task2_hard(topic_num, time_len))
