import json
import collections
import datetime
import math
import numpy as np
from sklearn.cluster import DBSCAN
# from gensim.models import word2vec, KeyedVectors
from sklearn import manifold


class Snapshot():
    def __init__(self):
        self.timestep = 31
        self.overlay = 24
        self.movestep = self.timestep - self.overlay
        # self.model = word2vec.Word2Vec.load('../data/model2/wiki.model')
        # self.model = KeyedVectors.load_word2vec_format(
        #     '../data/model/model.vec')
        # self.topic = [('稼働', '福島'),
        #               ('反原発'),
        #               ('子供', '影響'),
        #               ('被曝', '検査', '内部'),
        #               ('風評被害', '福島'),
        #               ('放射線', '汚染', '影響'),
        #               ('避難', '福島'),
        #               ('東電', '福島'),
        #               ('モニタリング', '政府')]
        self.topic = [('原発', '稼働'), ('原発', '東電'), ('原発', '福島'),
                      ('放射能', '福島'), ('福島', '避難'), ('原発', '報道'),
                      ('報道', '福島'), ('安全', '福島'), ('福島', '被曝'),
                      ('事故', '原発'), ('原発', '安全'), ('原発', '電力'),
                      ('復興', '福島'), ('国民', '東電'), ('東電', '福島'),
                      ('子供', '福島'), ('政府', '東電'), ('東電', '社員'),
                      ('原発', '反対'), ('影響', '福島')]
        pass

    def snapshot(self):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/topic/tweet_info.json', 'r') as f:
            tid_info = json.load(f)

        def func():
            temp = {}
            for key in self.topic:
                temp[key] = 0
            return temp
        date_tpc_count = collections.defaultdict(func)
        # date_tpc_info = collections.defaultdict(
        #     lambda: collections.defaultdict(
        #         lambda: dict(tid=[], text=[], rtcount=0)))
        for tid, info in tid_info.items():  # each tweet
            words = info['words']
            temp_topic = []
            for i, tpcs in enumerate(self.topic):  # each topic
                if tpcs[0] in words and tpcs[1] in words:
                    temp_topic.append(tpcs)
            for date, count in info['rtd'].items():  # date: RTcount
                for tt in temp_topic:
                    date_tpc_count[date][tt] += count
                    # date_tpc_info[date]['_'.join(tt)]['tid'].append(tid)
                    # date_tpc_info[date]['_'.join(tt)]['text'].append(
                    #     info['text'])
                    # date_tpc_info[date]['_'.join(tt)]['rtcount'] +=\
                    #     info['rtd'][date]
        # snapshot matrix
        graph, ratio_list = [], []  # ratio: revocery normalization
        date_list = []
        start_date = datetime.date(2011, 3, 11)
        end_date = datetime.date(2016, 12, 1)
        current_date = start_date
        while current_date < end_date:
            temp_vec = np.array([0.00000000001]*len(self.topic))
            for i in range(self.timestep):
                temp_date = current_date + datetime.timedelta(days=i)
                temp_date_str = temp_date.strftime('%Y-%m-%d')
                try:
                    temp_vec += np.array(
                        list(date_tpc_count[temp_date_str].values()))
                except:
                    pass
            # normalize
            if np.any(temp_vec):
                ratio = np.linalg.norm(temp_vec)
                norm1 = temp_vec / ratio
            else:
                ratio = 0
                norm1 = temp_vec
            ratio_list.append(ratio)
            graph.append(norm1)
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=self.movestep)
        # clustering
        graph = np.array(graph)
        length = len(graph)
        dists = [[0]*length for _ in range(length)]
        for i in range(length-1):
            for j in range(i+1, length):
                dists[i][j] = dists[j][i] = 1 - cos_sim(graph[i], graph[j])
        db = DBSCAN(eps=0.1, min_samples=1, metric='precomputed').fit(dists)
        labels = db.labels_
        # tsne
        tsne = manifold.TSNE(n_components=2, perplexity=5,
                             early_exaggeration=12, random_state=0)
        positions = tsne.fit_transform(graph)
        nodes = []
        for pos, g, d, r in zip(positions, graph, date_list, ratio_list):
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes.append(dict(x=x_pos, y=y_pos, date=d,
                              rtptn=g.tolist(), rate=r))
        links = []
        for i in range(len(nodes)-1):
            srcn, dstn = nodes[i], nodes[i+1]
            src = dict(x=srcn['x'], y=srcn['y'])
            dst = dict(x=dstn['x'], y=dstn['y'])
            links.append(dict(src=src, dst=dst))
        with open('../data/current/snapshot/nodes.json', 'w') as f:
            json.dump(dict(nodes=nodes, links=links), f)
        return nodes, links, labels, graph

    # def clustering(self, save_file=True):
    #     def compute_dist(vec1, vec2):
    #         return ((vec1[0]-vec2[0])**2+(vec1[1]-vec2[1])**2)**0.5
    #     with open('../data/current/snapshot/nodes.json', 'r') as f:
    #         dataset = json.load(f)
    #     nodes = dataset['nodes']
    #     links = dataset['links']
    #     nodes_pos = []
    #     for node in nodes:
    #         nodes_pos.append([node['x'], node['y']])
    #     length = len(nodes_pos)
    #     dists = [[0]*length for _ in range(length)]
    #     for i in range(length-1):
    #         for j in range(i+1, length):
    #             vec1, vec2 = nodes_pos[i], nodes_pos[j]
    #             dists[i][j] = dists[j][i] = compute_dist(vec1, vec2)
    #     db = DBSCAN(eps=2, min_samples=1, metric='precomputed').fit(dists)
    #     labels = db.labels_
    #     if not save_file:
    #         return labels, nodes
    #     else:
    #         for node, clu in zip(nodes, labels):
    #             node['clu'] = int(clu)
    #         with open('../data/current/snapshot/nodes_clustered.json', 'w')\
    #                 as f:
    #             json.dump(dict(nodes=nodes, links=links), f)

    def check_state(self):
        '''
        0: recurrent, 1: worm, 2: leap
        '''
        def compute_boundary(nodelist):
            # min(myList, key=lambda x:abs(x-myNumber))
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

        def nodeIdxToDate(idx):
            start_date = datetime.date(2011, 3, 11)
            cur_date = start_date + datetime.timedelta(days=idx*self.movestep)
            return cur_date.strftime('%Y-%m-%d')

        nodes, links, labels, graph = self.snapshot()
        cluster_index = collections.defaultdict(list)
        timespan_thres = 5
        for i, clu in enumerate(labels):
            cluster_index[clu].append(i)
        cluster_state = collections.defaultdict(int)
        for clu, idx_list in cluster_index.items():
            if len(idx_list) == 1:
                cluster_state[clu] = 1
            else:
                diff_list = np.diff(idx_list)
                if max(diff_list) > timespan_thres:
                    cluster_state[clu] = 0
                else:
                    cluster_state[clu] = 1
        # nodes
        # determine node positions
        tsne = manifold.TSNE(n_components=2, random_state=0)
        assert len(labels) == len(graph)
        # compute the center of each cluster
        center_graph = []
        for clu, idxs in cluster_index.items():
            center = sum([graph[idx] for idx in idxs])/len(idxs)
            center = center / np.linalg.norm(center)
            center_graph.append(center)
        # compute center positions
        # center_pos = tsne.fit_transform(np.array(center_graph))
        center_pos = []
        center_num = len(center_graph)
        col = row = round(center_num ** 0.5)
        for idx, cg in enumerate(center_graph):
            ri = math.floor(idx/row)+1
            ci = idx % col + 1
            center_pos.append([ri, ci])
        # computer center boundary
        center_boundary = compute_boundary(np.array(center_pos))
        # summarize each cluster
        cluster_center = {}
        for clu, pos, bdy in zip(list(cluster_index.keys()), center_pos,
                                 center_boundary):
            cluster_center[str(clu)] = dict(
                center=[float(pos[0]), float(pos[1])],
                boundary=bdy)
        idx_pos = {}  # node index: node position
        for clu, idxs in cluster_index.items():
            if len(idxs) > 1:  # cluster consists of more than one node
                # compute all graphs in cluster
                cluster_graph = [graph[idx] for idx in idxs]
                # compute center
                center = sum(cluster_graph)/len(idxs)
                center = center / np.linalg.norm(center)
                cluster_graph.append(center)
                # project to 2D
                all_pos = tsne.fit_transform(np.array(cluster_graph))
                # center x, y in current coordinates system
                ncx, ncy = all_pos[-1][0], all_pos[-1][1]
                # center x, y in original coordinates system
                ocx, ocy = cluster_center[str(clu)]['center'][0],\
                    cluster_center[str(clu)]['center'][1]
                obdy = cluster_center[str(clu)]['boundary']
                # map all nodes in current coordinates system
                # into center node original area
                xlist = list(map(lambda x: x[0], all_pos))
                ylist = list(map(lambda x: x[1], all_pos))
                # x-axis, y-axis relationship, zoom (origin/current)
                xk = (obdy['right']-obdy['left'])/(max(xlist)-min(xlist))
                yk = (obdy['top']-obdy['bottom'])/(max(ylist)-min(ylist))
                # translate
                xb = ocx - ncx * xk
                yb = ocy - ncy * yk
                for idx, pos in zip(idxs, all_pos[:-1]):
                    ox, oy = float(pos[0]*xk+xb), float(pos[1]*yk+yb)
                    idx_pos[str(idx)] = [ox, oy]
            else:  # cluster consists of only one node
                idx_pos[str(idxs[0])] = cluster_center[str(clu)]['center']
        # reset node position
        for idx, node in enumerate(nodes):
            node['x'] = idx_pos[str(idx)][0]
            node['y'] = idx_pos[str(idx)][1]
        # links
        links = []
        for i in range(len(nodes)-1):
            srcn, dstn = nodes[i], nodes[i+1]
            src_tpc = [int(d*srcn['rate']) for d in srcn['rtptn']]
            dst_tpc = [int(d*dstn['rate']) for d in dstn['rtptn']]
            # src_tpc = np.array(srcn['rtptn'])*srcn['rate']
            # dst_tpc = np.array(dstn['rtptn'])*dstn['rate']
            src = dict(x=srcn['x'], y=srcn['y'], date=srcn['date'],
                       tpc=src_tpc)
            dst = dict(x=dstn['x'], y=dstn['y'], date=dstn['date'],
                       tpc=dst_tpc)
            state = -1
            if labels[i] != labels[i+1]:
                state = 2
            links.append(dict(src=src, dst=dst, state=state))
        # clusters
        clusters = []
        for clu, idxs in cluster_index.items():  # each cluster
            # date_info = []
            date_list = []
            node_pos = []
            for idx in idxs:
                date = nodeIdxToDate(idx)  # recover index to date
                date_list.append(date)
                # tpc_info = date_tpc_info[date]
                # date_info.append({date: tpc_info})
                node_pos.append([nodes[idx]['x'], nodes[idx]['y']])
            temp = dict(clu=int(clu), state=int(cluster_state[clu]),
                        ndate=date_list, npos=node_pos)
            clusters.append(temp)
        with open('../data/current/snapshot/nodes_state.json', 'w') as f:
            json.dump(dict(nodes=nodes, links=links, clusters=clusters), f)


def temp():
    '''
    generate date info file
    '''
    topic = [('原発', '稼働'), ('原発', '東電'), ('原発', '福島'),
             ('放射能', '福島'), ('福島', '避難'), ('原発', '報道'),
             ('報道', '福島'), ('安全', '福島'), ('福島', '被曝'),
             ('事故', '原発'), ('原発', '安全'), ('原発', '電力'),
             ('復興', '福島'), ('国民', '東電'), ('東電', '福島'),
             ('子供', '福島'), ('政府', '東電'), ('東電', '社員'),
             ('原発', '反対'), ('影響', '福島')]
    with open('../data/current/topic/tweet_info.json', 'r') as f:
        tid_info = json.load(f)
    # {date: [{tid, text, keywords, count}]}
    date_info = collections.defaultdict(list)
    for tid, info in tid_info.items():  # each tweet
        words = info['words']
        tpc_list = []
        for i, tpcs in enumerate(topic):  # each topic
            if tpcs[0] in words and tpcs[1] in words:
                tpc_list.append('_'.join(tpcs))
        for date, count in info['rtd'].items():  # date: RTcount
            date_info[date].append(dict(tid=tid, text=info['text'],
                                        count=count, tpc=tpc_list))
    with open('../data/current/snapshot/date_info.json', 'w') as f:
        json.dump(date_info, f)


if __name__ == '__main__':
    ss = Snapshot()
    # ss.snapshot()
    ss.check_state()
    # temp()
