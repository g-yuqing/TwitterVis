import collections
import json
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import manifold
from sklearn.decomposition import PCA
from twitter_keyword import create_period_keyword_whole


def state_graph(count=20, timestep=5, movestep=1):
    # calculate keywords
    period_kwscore, keyword_score =\
        create_period_keyword_whole(count, timestep, movestep, True)
    print([d[0] for d in keyword_score])
    # vectorize
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
    with open('../data/retweet-2011/state_graph.json', 'w') as f:
        json.dump(dict(nodes=nodes, links=links), f)


def clustering(count=20):
    '''
    cluster based on the positon of tsne result
    '''
    with open('../data/retweet-2011/state_graph.json', 'r') as f:
        dataset = json.load(f)
    links = dataset['links']
    nodes = dataset['nodes']
    positions = [[node['x'], node['y']] for node in nodes]
    clusters = DBSCAN(eps=3, min_samples=1).fit(positions)
    labels = clusters.labels_
    for label, node in zip(labels, nodes):
        node['g'] = int(label)
    # reset topic pattern according to groups
    groupnum = max(labels) - min(labels) + 1
    group_node = collections.defaultdict(list)
    group_idx = collections.defaultdict(list)
    for idx, group in enumerate(labels):
        group_idx[group].append(idx)
        group_node[group].append(nodes[idx])
    group_ptn = [[] for _ in range(groupnum)]
    for group, nodelist in group_node.items():
        ptn = np.zeros(len(nodelist[0]['kw']))
        for node in nodelist:
            ptn += (np.array(node['kw'])*node['ratio'])
        # normalize
        group_ptn[group] = ptn / np.linalg.norm(ptn)
    pca = PCA(n_components=1)
    pcapos = pca.fit_transform(group_ptn)
    print(pca.explained_variance_ratio_)
    print(pca.n_components_)
    for idx, node in enumerate(nodes):
        group = labels[idx]
        ppos = pcapos[group]
        node['pca'] = float(ppos)
    # set state {0: worm} {1: recurring}
    thres = 5
    for group, idxlist in group_idx.items():
        if len(idxlist) < 2:
            idx = idxlist[0]
            nodes[idx]['state'] = 0
        else:
            if max([y-x for x, y in zip(idxlist, idxlist[1:])]) >= thres:
                for idx in idxlist:
                    nodes[idx]['state'] = 1
            else:
                for idx in idxlist:
                    nodes[idx]['state'] = 0
    with open('../data/retweet-2011/state_graph.json', 'w') as f:
        json.dump(dict(nodes=nodes, links=links), f)


if __name__ == '__main__':
    state_graph(count=20, timestep=5, movestep=1)
    clustering()
