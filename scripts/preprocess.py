import json
import csv
import numpy as np
import collections
import networkx as nx
import itertools
from scipy.spatial import ConvexHull


class Processor(object):

    def __init__(self):
        pass

    def loadCSV(self):
        '''
        load csv data, save as json file
        '''
        with open('../data/march/retweet_state_march.csv', newline='') as f:
            # reader = csv.reader(f, delimiter=' ', quotechar='|')
            dataset = collections.defaultdict(list)
            reader = csv.DictReader(f)
            count = 1
            for row in reader:
                date = row['date']
                year = date.split('-')[0]
                user = row['user']
                influencer = row['influencer']
                dataset[year].append(
                    dict(user=user, influencer=influencer))
                count += 1
            print(count)
        with open('../data/march/march.json', 'w') as f:
            json.dump(dataset, f)

    def forcelayoutJSON(self):
        '''
        read data processed by loadCSV function,
        convert into forcelayout format
        '''
        with open('../data/march/march.json', 'r') as f:
            dataset = json.load(f)
        years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        for year in years:
            year_data = dataset[year]
            nodes = []
            edges = []
            node_degree = collections.defaultdict(int)
            for data in year_data:
                target = data['user']
                source = data['influencer']
                node_degree[target] += 1
                node_degree[source] += 1
            src_thres, trg_thres = 0, 30
            uid = 0
            node_id = {}
            for data in year_data:
                target = data['user']
                source = data['influencer']
                if node_degree[target] > trg_thres and\
                        node_degree[source] > src_thres:
                    if target not in node_id:
                        node_id[target] = uid
                        nodes.append(
                            dict(name=uid, degree=node_degree[target],
                                 tid='T'+str(target)))
                        uid += 1
                    if source not in node_id:
                        node_id[source] = uid
                        nodes.append(
                            dict(name=uid, degree=node_degree[source],
                                 tid='S'+str(source)))
                        uid += 1
                    edges.append(
                        dict(source=node_id[source], target=node_id[target]))
            print(year, len(nodes), len(edges))
            res = dict(nodes=nodes, edges=edges)
            with open('../static/march/' + year + '.json', 'w') as f:
                json.dump(res, f)

    def cluster_overview(self):
        years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        clusters_info = {}
        for year in years:
            with open('../data/clustered/'+year+'.json') as f:
                graph = json.load(f)
            nodes = graph['nodes']
            year_info = collections.defaultdict(list)
            for node in nodes:
                year_info[node['cluster']].append(node)
            cluster_count = len(year_info)
            user_count_in_cluster = []
            most_active_users = []
            for key, val in year_info.items():
                user_count_in_cluster.append(len(val))
                val.sort(key=lambda x: x['degree'], reverse=True)
                active_count = int(max(1, min(len(val)/100, 20)))
                val_count = 0
                while len(most_active_users) <= active_count:
                    if 'S' in val[val_count]['tid']:
                        most_active_users.append(val[val_count])
                    val_count += 1
                # most_active_users.append(val[:active_count])
            clusters_info[year] = dict(cluster_count=cluster_count,
                                       user_per_count=user_count_in_cluster,
                                       most_active_users=most_active_users)
        with open('../data/clustered/cluster_overview.json', 'w') as f:
            json.dump(clusters_info, f)

    def node_contour(self):
        years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        result = {}
        for year in years:
            with open('../data/clustered/'+year+'.json') as f:
                data = json.load(f)
            nodes = data['nodes']
            colors = {}
            cluster_nodes = collections.defaultdict(list)
            for node in nodes:
                colors[node['cluster']] = node['color']
                cluster_nodes[node['cluster']].append([node['x'], node['y']])
            counter_nodes = {}
            for key, val in cluster_nodes.items():
                indexs = ConvexHull(np.array(val)).vertices
                boundary_nodes = [dict(x=val[i][0], y=val[i][1])
                                  for i in indexs]
                counter_nodes[key] = dict(color=colors[key],
                                          boundary=boundary_nodes)
            result[year] = counter_nodes
        with open('../data/clustered/cluster_counter.json', 'w') as f:
            json.dump(result, f)

    def graphSimilarity(self):
        '''
        compare similarity between two graphs
        3,4,5 vertices 29 cases
        '''
        patterns = [
            [(0, 1), (0, 2)],  # 3-1
            [(0, 1), (0, 2), (1, 2)],  # 3-2
            [(0, 1), (1, 2), (2, 3)],  # 4-1
            [(0, 1), (0, 2), (0, 3)],  # 4-2
            [(0, 1), (1, 2), (2, 3), (0, 3)],  # 4-3
            [(0, 1), (1, 2), (1, 3), (2, 3)],  # 4-4
            [(0, 1), (0, 2), (1, 2), (2, 3), (0, 3)],  # 4-5
            [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (1, 3)],  # 4-6
            [(0, 1), (1, 2), (2, 3), (3, 4)],  # 5-1
            [(0, 1), (0, 2), (0, 3), (3, 4)],  # 5-2
            [(0, 1), (0, 2), (0, 3), (0, 4)],  # 5-3
            [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)],  # 5-4
            [(0, 1), (0, 2), (1, 2), (0, 3), (3, 4)],  # 5-5
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2)],  # 5-6
            [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)],  # 5-7
            [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4)],  # 5-8
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4)],  # 5-9
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (3, 4)],  # 5-10
            [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 4)],  # 5-11
            [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-12
            [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)],  # 5-13
            [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-14
            [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)],  # 5-15
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 4), (3, 4)],  # 5-16
            [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-17
            [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
             (2, 3), (1, 4), (2, 4)],  # 5-18
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
             (2, 3), (3, 4), (0, 4)],  # 5-19
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
             (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-20
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3),
             (1, 4), (2, 3), (2, 4), (3, 4)],  # 5-21
        ]
        pattern_graphs = []
        # init pattern graphs | target graphs
        for pattern in patterns:
            temp = nx.Graph()
            for edge in pattern:
                s, t = edge[0], edge[1]
                temp.add_edge(s, t)
            pattern_graphs.append(temp)
        print('init pattern graphs done')
        graphlets = {}
        for _, mon in self.month.items():
            print('in month:', mon)
            with open(self.path + 'target/' + mon + '.json', 'r') as f:
                graph = json.load(f)
                nodes = graph['nodes']
                edges = graph['edges']
                reserved = []
                distrib = [0] * len(patterns)
                for cc, node in enumerate(nodes):  # check each node
                    print('===========node: ', cc, node[
                          'degree'], '===========')
                    # init source graph
                    source = nx.Graph()
                    uid = node['name']
                    degree = node['degree']
                    if degree < 2:
                        print('no match pattern')
                        continue
                    elif degree > 100:
                        print('reserved node')
                        reserved.append(uid)
                        continue
                    else:
                        source_nodes = [uid]
                        for edge in edges:
                            if len(source_nodes) == degree + 1:
                                break
                            s, t = edge['source'], edge['target']
                            if s == uid:
                                source.add_edge(s, t)
                                source_nodes.append(t)
                            if t == uid:
                                source.add_edge(s, t)
                                source_nodes.append(s)
                        for edge in edges:
                            s, t = edge['source'], edge['target']
                            if s in source_nodes[1:] and t in source_nodes[1:]:
                                source.add_edge(s, t)
                        print('source graph complete')
                        # check each pattern (geanerate target graph)
                        for i, pg in enumerate(pattern_graphs):
                            print('pattern: ', i)
                            if i < 2:  # 3 nodes
                                for sub_nodes in itertools.combinations(
                                        source_nodes[1:], 2):
                                    subg = source.subgraph(sub_nodes + (uid,))
                                    if nx.is_connected(subg) and \
                                            nx.is_isomorphic(subg, pg):
                                        distrib[i] += 1
                                        break
                            elif i >= 2 and i < 8:  # 4 nodes
                                for sub_nodes in itertools.combinations(
                                        source_nodes[1:], 3):
                                    subg = source.subgraph(sub_nodes + (uid,))
                                    if nx.is_connected(subg) and \
                                            nx.is_isomorphic(subg, pg):
                                        distrib[i] += 1
                                        break
                            else:  # 5 nodes
                                for sub_nodes in itertools.combinations(
                                        source_nodes[1:], 4):
                                    subg = source.subgraph(sub_nodes + (uid,))
                                    if nx.is_connected(subg) and \
                                            nx.is_isomorphic(subg, pg):
                                        distrib[i] += 1
                                        break
                        print(distrib)
            graphlets[mon] = dict(distrib=distrib, reserved=reserved)
        with open(self.path + 'graphlets.json', 'w') as f:
            json.dump(graphlets, f)


def most_active_users():
    with open('../data/clustered/cluster_overview.json', 'r') as f:
        dataset = json.load(f)
    jsonfile = {}
    for key, val in dataset.items():
        most_active_users = val['most_active_users']
        temp_user = []
        for cluster_user in most_active_users:
            for user in cluster_user:
                uid = user['tid']
                temp_user.append(uid[1:])
        jsonfile[key] = temp_user
    with open('../data/clustered/temp.json', 'w') as f:
        json.dump(jsonfile, f)


if __name__ == '__main__':
    processor = Processor()
    # processor.forcelayoutJSON()
    # processor.graphSimilarity()
    processor.cluster_overview()
    # processor.node_contour()
    # most_active_users()
