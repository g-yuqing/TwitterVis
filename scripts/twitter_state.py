# import collections
import json
import numpy as np
# from sklearn.cluster import DBSCAN
from sklearn import manifold
from sklearn.decomposition import PCA
from twitter_keyword import create_period_keyword


def state_graph(count=20, timestep=5, movestep=1):
    def cos_sim(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                     np.linalg.norm(vec2))
    # calculate keywords
    period_kwscore, keyword_score =\
        create_period_keyword(count, timestep, movestep)
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
    pca = PCA(n_components=1)
    pcapos = pca.fit_transform(graph)
    print(pca.explained_variance_ratio_)
    print(pca.n_components_)
    for tpos, ppos, g, d, r in\
            zip(tsnepos, pcapos, graph, datelist, ratiolist):
        nodes.append(dict(x=float(tpos[0]), y=float(tpos[1]),
                          pca=float(ppos[0]), date=d, kw=g.tolist(), ratio=r))
    # links
    links = []
    for i in range(len(nodes)-1):
        srcn, dstn = nodes[i], nodes[i+1]
        src = dict(x=srcn['x'], y=srcn['y'])
        dst = dict(x=dstn['x'], y=dstn['y'])
        links.append(dict(src=src, dst=dst))
    # # state
    # # clustering
    # datelen = len(graph)
    # dists = [[0]*datelen for _ in range(datelen)]
    # for i in range(datelen-1):
    #     for j in range(i+1, datelen):
    #         dists[i][j] = dists[j][i] = 1 - cos_sim(graph[i], graph[j])
    # db = DBSCAN(eps=0.03, min_samples=1, metric='precomputed').fit(dists)
    # labels = db.labels_
    # cluster_index = collections.defaultdict(list)
    # for idx, clu in enumerate(labels):
    #     cluster_index[clu].append(idx)
    # # 0: recurrent, 1: worm, 2: leap
    # timespan = 5
    # cluster_state = collections.defaultdict(int)
    # for clu, idxs in cluster_index.items():
    #     if len(idxs) == 1:
    #         cluster_state[clu] = 1
    #     else:
    #         diffs = np.diff(idxs)
    #         if max(diffs) > timespan:
    #             cluster_state[clu] = 0
    #         else:
    #             cluster_state[clu] = 1
    # # cluster for convex hull
    # clusters = []
    # for clu, idxs in cluster_index.items():
    #     node_pos = list(map(
    #         lambda idx: [nodes[idx]['x'], nodes[idx]['y']], idxs))
    #     clusters.append(dict(state=int(cluster_state[clu]), npos=node_pos))
    # save to json file
    with open('../data/retweet-2011/state_graph.json', 'w') as f:
        json.dump(dict(nodes=nodes, links=links), f)


def clustering(matrix):
    def cos_sim(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                     np.linalg.norm(vec2))
    vecnum = len(matrix)
    sims = [[1]*vecnum for _ in range(vecnum)]
    for i in range(vecnum-1):
        for j in range(i+1, vecnum):
            sims[i][j] = sims[j][i] = cos_sim(matrix[i], matrix[j])


if __name__ == '__main__':
    state_graph()
