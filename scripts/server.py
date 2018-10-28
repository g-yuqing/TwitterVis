import collections
import json
import datetime
from itertools import combinations
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import manifold
# import rpack


def init_layout(count=20, timestep=5, movestep=1):
    def cos_sim(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                     np.linalg.norm(vec2))
    with open('../data/retweet-2011/keywords.json', 'r') as f:
        date_keywords = json.load(f)
    # rearrange date
    keyword_score = collections.defaultdict(int)
    keyword_idx, index = {}, 0
    date_kwscore = {}
    start = datetime.date(2011, 3, 11)
    end = datetime.date(2011, 12, 31) - datetime.timedelta(days=timestep-1)
    current = start
    while current <= end:
        kw_weight = collections.Counter()
        for i in range(timestep):
            date = (current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            kw_weight += collections.Counter(date_keywords[date])
        kwscore = kw_weight.most_common(count)
        date_kwscore[current.strftime('%Y-%m-%d')] = kwscore
        for ks in kwscore:
            kw, score = ks[0], ks[1]
            if kw not in keyword_idx:
                keyword_idx[kw] = index
                index += 1
            keyword_score[kw] += score
        current += datetime.timedelta(days=movestep)
    # vectorize
    ratiolist = []
    datelist = []
    veclist = []  # dately vector
    veclen = len(keyword_score)
    assert veclen == index
    for date, kw_scores in date_kwscore.items():
        vec = np.zeros(veclen)
        for kw_s in kw_scores:
            idx = keyword_idx[kw_s[0]]
            vec[idx] = kw_s[1]
        # normalize
        ratio = np.linalg.norm(vec)
        vec = vec / ratio
        ratiolist.append(ratio)
        datelist.append(date)
        veclist.append(vec)
    # clustering
    graph = np.array(veclist)
    datelen = len(graph)
    dists = [[0]*datelen for _ in range(datelen)]
    for i in range(datelen-1):
        for j in range(i+1, datelen):
            dists[i][j] = dists[j][i] = 1 - cos_sim(graph[i], graph[j])
    db = DBSCAN(eps=0.03, min_samples=1, metric='precomputed').fit(dists)
    labels = db.labels_
    # # nodes
    # nodes = []
    # # nodes: center vector of each cluster
    # cluster_index = collections.defaultdict(list)
    # for idx, clu in enumerate(labels):
    #     cluster_index[clu].append(idx)
    # center_cluster = []
    # center_vector = []
    # for clu, idxs in cluster_index.items():
    #     if len(idxs) == 1:
    #         idx = idxs[0]
    #         vec = veclist[idx]*ratiolist[idx]
    #     else:
    #         vec = np.zeros(veclen)
    #         for idx in idxs:
    #             vec += (veclist[idx]*ratiolist[idx])
    #     # normalize
    #     vec = vec / np.linalg.norm(vec)
    #     center_cluster.append(clu)
    #     center_vector.append(vec)
    # # nodes: center position - tsne
    # tsne = manifold.TSNE(n_components=2, perplexity=5,
    #                      early_exaggeration=12, random_state=0)
    # cenpos = tsne.fit_transform(center_vector)  # calculate center positions
    # # nodes: determine center area
    # areas = compute_boundary(np.array(cenpos))
    # # nodes: calculate nodes position in each cluster
    # node_positions = {}
    # for clu, cv, cp, area in zip(center_cluster, center_vector, cenpos, areas):
    #     idxs = cluster_index[clu]
    #     if len(idxs) == 1:
    #         node_positions[idxs[0]] = cp
    #     else:
    #         sub_vecs = [veclist[idx] for idx in idxs]
    #         sub_vecs.append(cv)
    #         subpos = tsne.fit_transform(sub_vecs)
    #         ocpx, ocpy = cp[0], cp[1]
    #         ncpx, ncpy = subpos[-1][0], subpos[-1][1]
    #         xlist = list(map(lambda x: x[0], subpos))
    #         ylist = list(map(lambda x: x[1], subpos))
    #         # project subnodes into area
    #         xk = (area['right']-area['left'])/(max(xlist)-min(xlist))
    #         yk = (area['top']-area['bottom'])/(max(ylist)-min(ylist))
    #         xb = ocpx - ncpx * xk
    #         yb = ocpy - ncpy * yk
    #         for idx, subp in zip(idxs, subpos[:-1]):
    #             x, y = float(subp[0]*xk+xb), float(subp[1]*yk+yb)
    #             node_positions[idx] = [x, y]
    # assert len(node_positions) == datelen
    # idx = 0
    # for g, d, r in zip(graph, datelist, ratiolist):
    #     x_pos, y_pos = node_positions[idx][0], node_positions[idx][1]
    #     nodes.append(dict(x=float(x_pos), y=float(y_pos), date=d,
    #                       kw=g.tolist(), ratio=r))
    #     idx += 1
    # nodes
    nodes = []
    cluster_index = collections.defaultdict(list)
    for idx, clu in enumerate(labels):
        cluster_index[clu].append(idx)
    tsne = manifold.TSNE(n_components=2, perplexity=5,
                         early_exaggeration=12, random_state=0)
    positions = tsne.fit_transform(graph)
    for pos, g, d, r in zip(positions, graph, datelist, ratiolist):
        x_pos, y_pos = pos[0], pos[1]
        nodes.append(dict(x=float(x_pos), y=float(y_pos), date=d,
                          kw=g.tolist(), ratio=r))
    # links
    links = []
    for i in range(len(nodes)-1):
        srcn, dstn = nodes[i], nodes[i+1]
        src = dict(x=srcn['x'], y=srcn['y'])
        dst = dict(x=dstn['x'], y=dstn['y'])
        links.append(dict(src=src, dst=dst))
    # state
    # 0: recurrent, 1: worm, 2: leap
    timespan = 5
    cluster_state = collections.defaultdict(int)
    for clu, idxs in cluster_index.items():
        if len(idxs) == 1:
            cluster_state[clu] = 1
        else:
            diffs = np.diff(idxs)
            if max(diffs) > timespan:
                cluster_state[clu] = 0
            else:
                cluster_state[clu] = 1
    # cluster for convex hull
    clusters = []
    for clu, idxs in cluster_index.items():
        node_pos = list(map(
            lambda idx: [nodes[idx]['x'], nodes[idx]['y']], idxs))
        clusters.append(dict(state=int(cluster_state[clu]), npos=node_pos))
    # save to json file
    kwlist = ['']*veclen
    for k, v in keyword_idx.items():
        kwlist[v] = k
    with open('../data/retweet-2011/state_graph.json', 'w') as f:
        json.dump(dict(nodes=nodes, links=links, clusters=clusters,
                       kwidx=kwlist, kwscr=keyword_score), f)


def compute_boundary(nodelist):
    nodelist = nodelist.tolist()
    xlist = list(map(lambda x: x[0], nodelist))
    ylist = list(map(lambda x: x[1], nodelist))
    xrg = [min(xlist), max(xlist)]
    yrg = [min(ylist), max(ylist)]
    # extend border
    left = xrg[0]-(xrg[1]-xrg[0])/5
    right = xrg[1]+(xrg[1]-xrg[0])/5
    top = yrg[1]+(yrg[1]-yrg[0])/5
    bottom = yrg[0]-(yrg[1]-yrg[0])/5
    length = len(nodelist)
    result = []
    for i in range(length):  # each node
        nx, ny = nodelist[i][0], nodelist[i][1]
        otherlist = nodelist[:i]+nodelist[i+1:] +\
            [[left, bottom], [left, top],
             [right, bottom], [right, top]]
        lval, rval, tval, bval = 999, 999, 999, 999
        xlist = list(map(lambda x: x[0], otherlist))
        ylist = list(map(lambda x: x[1], otherlist))
        # left & right
        for x in xlist:
            if x-nx > 0 and x-nx < rval:  # right
                rval = x - nx
            if nx-x > 0 and nx-x < lval:  # left
                lval = nx - x
        for y in ylist:
            if y-ny > 0 and y-ny < tval:  # top
                tval = y - ny
            if ny-y > 0 and ny-y < bval:  # bot
                bval = ny - y
        rval = rval / 2
        lval = lval / 2
        tval = tval / 2
        bval = bval / 2
        result.append(dict(pos=[nx, ny], left=nx-lval,
                           right=nx+rval, top=ny+tval, bottom=ny-bval,
                           lb=[nx-lval, ny-bval],
                           rb=[nx+rval, ny-bval],
                           lt=[nx-lval, ny+tval],
                           rt=[nx+rval, ny+tval]))
    return result


if __name__ == '__main__':
    # extract_topic()
    init_layout()
