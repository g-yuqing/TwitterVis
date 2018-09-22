import json
import collections
import datetime
import numpy as np
from sklearn import manifold


class Snapshot():
    def __init__(self):
        pass

    def snapshot(self, topic_list):
        def cos_sim(vec1, vec2):
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) *
                                         np.linalg.norm(vec2))
        with open('../data/current/tweet_info.json', 'r') as f:
            tid_info = json.load(f)
        unknown_list = collections.defaultdict(int)
        # topic = ['放射能', '環境', '避難', '政府', '学会', '経済', '食品']
        topic = ['危機管理', '関東地方', '風評被害', '放射性物質', '子どもたち',
                 'この国', '無量大数', '編集長', '基準値', 'ツイート',
                 '廃炉', '安倍首相', 'ミリシーベルト', 'メルトダウン']

        def func():
            temp = {}
            for key in topic:
                temp[key] = 0
            return temp
        tpc_vecs = [self.model[tpc] for tpc in topic]
        date_tpc = collections.defaultdict(func)
        sim_thres = 0.5
        for tid, info in tid_info.items():
            words = info['words']
            temp_topic = []
            for i, tpc in enumerate(topic):
                vec1 = tpc_vecs[i]
                for word in words:
                    try:
                        vec2 = self.model[word]
                        temp_sim = cos_sim(vec1, vec2)
                        if temp_sim > sim_thres:
                            temp_topic.append(tpc)
                            break
                    except:
                        unknown_list[word] += 1
            date_count = info['rtd']
            for date, count in date_count.items():
                for tt in temp_topic:
                    date_tpc[date][tt] += count
        # snapshot matrix
        graph = []
        date_list = []
        timestep, overlay = 31, 28
        movestep = timestep - overlay
        start_date = datetime.date(2011, 3, 1)
        end_date = datetime.date(2016, 12, 1)
        current_date = start_date
        while current_date < end_date:
            temp_vec = np.array([0]*len(topic))
            for i in range(timestep):
                temp_date = current_date + datetime.timedelta(days=i)
                temp_date_str = temp_date.strftime('%Y-%m-%d')
                try:
                    temp_vec += np.array(
                        list(date_tpc[temp_date_str].values()))
                except:
                    pass
            # normalize
            if np.any(temp_vec):
                norm1 = temp_vec / np.linalg.norm(temp_vec)
            else:
                norm1 = temp_vec
            graph.append(norm1)
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=movestep)
        # tsne layout
        graph = np.array(graph)
        tsne = manifold.TSNE(n_components=2, random_state=0)
        positions = tsne.fit_transform(graph)
        # # phate layout
        # graph = np.array(graph)
        # pl = phate.PHATE(n_components=2)
        # positions = pl.fit_transform(graph)
        nodes = []
        for pos, g, d in zip(positions, graph, date_list):
            x_pos, y_pos = float(pos[0]), float(pos[1])
            nodes.append(dict(x=x_pos, y=y_pos, d=d, c=g.tolist()))
        links = []
        nl = len(nodes)
        for i in range(nl-1):
            links.append(dict(src=nodes[i], dst=nodes[i+1]))
        with open('../data/current/nodes.json', 'w') as f:
            json.dump(dict(nodes=nodes, links=links), f)
