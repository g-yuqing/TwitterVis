import random
import collections
import json
import numpy as np
from sklearn import manifold
import datetime


def model_data(directory, layers=10, smooth=False, normalized=False):
    '''
    time span: 60
    pattern num: 4
    topic layer: 10/20
    normalized: true/false
    change rate: high/low
    '''
    def random_pattern_len():
        pattern_num = 4
        total_len = 60
        patterns = []
        minval, maxval = 10, 20
        while len(patterns) < pattern_num:
            if len(patterns) == pattern_num-1:
                length = total_len - sum(patterns)
            else:
                length = random.randint(minval, maxval)
            if length >= minval and length <= maxval:
                patterns.append(length)
            else:
                patterns = []
        return patterns

    topic_scores = collections.defaultdict(list)
    topic_desc = collections.defaultdict(list)
    # big_change = random.choice([True, False])
    vals = [[6, 8], [9, 11], [12, 14], [15, 17], [18, 20]]
    # vals = [[6, 8], [11, 13], [16, 18], [21, 23]]
    # # init
    # topic_val = {}
    # for tn in range(layers):
    #     topic = 'topic'+str(tn)
    #     topic_val[topic] = random.choice(range(len(vals)))
    patterns = random_pattern_len()
    print(patterns)
    # pattern 1  ========================
    start = 0
    end = start + patterns[0]
    for tn in range(layers):
        if smooth:
            [minval, maxval] = random.choice(vals)
        else:
            [minval, maxval] = random.choice(vals)
        topic = 'topic'+str(tn)
        topic_desc[topic].append([minval, maxval])
        for time in range(start, end):
            val = random.randint(minval, maxval)+random.uniform(-0.5, 0.5)
            topic_scores[topic].append(val)
    # pattern 2  ========================
    start = patterns[0]
    end = start + patterns[1]
    for tn in range(layers):
        topic = 'topic'+str(tn)
        if smooth:
            prevIdx = vals.index(topic_desc[topic][-1])
            if prevIdx == 0:
                idx = 1
            elif prevIdx == len(vals)-1:
                idx = prevIdx-1
            else:
                idx = prevIdx + random.choice([-1, 1])
            [minval, maxval] = vals[idx]
        else:
            [minval, maxval] = random.choice(vals)
        topic_desc[topic].append([minval, maxval])
        for time in range(start, end):
            val = random.randint(minval, maxval)+random.uniform(-0.5, 0.5)
            topic_scores[topic].append(val)
    # pattern 3  ========================
    start = sum(patterns[:2])
    end = start + patterns[2]
    for tn in range(layers):
        topic = 'topic'+str(tn)
        if smooth:
            prevIdx = vals.index(topic_desc[topic][-1])
            if prevIdx == 0:
                idx = 1
            elif prevIdx == len(vals)-1:
                idx = prevIdx-1
            else:
                idx = prevIdx + random.choice([-1, 1])
            [minval, maxval] = vals[idx]
        else:
            [minval, maxval] = random.choice(vals)
        topic_desc[topic].append([minval, maxval])
        for time in range(start, end):
            val = random.randint(minval, maxval)+random.uniform(-0.5, 0.5)
            topic_scores[topic].append(val)
    # pattern 4  ========================
    start = sum(patterns[:3])
    end = start + patterns[3]
    for tn in range(layers):
        topic = 'topic'+str(tn)
        if smooth:
            prevIdx = vals.index(topic_desc[topic][-1])
            if prevIdx == 0:
                idx = 1
            elif prevIdx == len(vals)-1:
                idx = prevIdx-1
            else:
                idx = prevIdx + random.choice([-1, 1])
            [minval, maxval] = vals[idx]
        else:
            [minval, maxval] = random.choice(vals)
        topic_desc[topic].append([minval, maxval])
        for time in range(start, end):
            val = random.randint(minval, maxval)+random.uniform(-0.5, 0.5)
            topic_scores[topic].append(val)
    # normalization
    if normalized:
        matrix = [[0]*sum(patterns) for _ in range(layers)]
        for row in range(len(matrix)):
            topic = 'topic'+str(row)
            scores = topic_scores[topic]
            for col in range(len(matrix[0])):
                matrix[row][col] = scores[col]
        matrix = np.array(matrix)
        matrixT = matrix.transpose()
        temp = []
        for scores in matrixT:
            ratio = np.linalg.norm(scores)
            norm = scores / ratio
            temp.append(norm)
        matrix = np.array(temp).transpose()
        for idx, row in enumerate(matrix):
            topic = 'topic'+str(idx)
            topic_scores[topic] = row.tolist()
    # save to json file
    dataset = {
        'descript': {'pattern': patterns, 'topic': topic_desc},
        'data': topic_scores}
    path = directory + 'data.json'
    with open(path, 'w') as f:
        json.dump(dataset, f)
    return dataset


def graph_data(directory, dataset):
    topic_scores = dataset['data']
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
    path1 = directory + 'top-topics.json'
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
    path2 = directory + 'state-graph.json'
    with open(path2, 'w') as f:
        json.dump(dict(nodes=nodes, links=links), f)


def main():
    for i in range(1, 6):
        directory = '../data/retweet-2011/model-data2/'+str(i)
        dataset = model_data(directory, 10, True, True)
        graph_data(directory, dataset)
    for i in range(6, 11):
        directory = '../data/retweet-2011/model-data2/'+str(i)
        dataset = model_data(directory, 20, True, True)
        graph_data(directory, dataset)


if __name__ == '__main__':
    main()
