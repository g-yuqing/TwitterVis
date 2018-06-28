import json
import csv
import numpy as np
import pandas as pd
import collections
import networkx as nx
import itertools
from scipy.spatial import ConvexHull
import math
from scipy.spatial import distance
# import graph_tool.all as gt
#  /usr/local/Cellar/python/3.6.2/Frameworks/Python.framework/Versions/3.6/bin/python3


class Processor(object):

    def __init__(self):
        pass

    def loadCSV(self):
        '''
        load csv data, save as json file
        '''
        with open('../data/march/march.csv', newline='') as f:
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
            node_out_degree = collections.defaultdict(int)
            node_in_degree = collections.defaultdict(int)
            for data in year_data:
                target = data['user']
                source = data['influencer']
                node_in_degree[target] += 1
                node_out_degree[source] += 1
            out_thres, in_thres = 10, 0
            uid = 0
            edge_id = 0
            node_id = {}
            for data in year_data:
                target = data['user']
                source = data['influencer']
                if node_out_degree[target] > out_thres and\
                        node_in_degree[source] > in_thres:
                    if target not in node_id:
                        node_id[target] = uid
                        indeg = node_in_degree[target]
                        outdeg = node_out_degree[source]
                        nodes.append(
                            dict(id=uid, indeg=indeg, outdeg=outdeg,
                                 name=target))
                        uid += 1
                    if source not in node_id:
                        node_id[source] = uid
                        indeg = node_in_degree[target]
                        outdeg = node_out_degree[source]
                        nodes.append(
                            dict(id=uid, indeg=indeg, outdeg=outdeg,
                                 name=source))
                        uid += 1
                    edges.append(dict(id=edge_id,
                                      source=node_id[source],
                                      target=node_id[target]))
                    edge_id += 1
            print(year, len(nodes), len(edges))
            res = dict(nodes=nodes, edges=edges)
            with open('../data/march/' + year + '.json', 'w') as f:
                json.dump(res, f)

    def cluster_similarity(self):
        '''
        yearly data is clustered by Javascript
        '''
        years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
        # year_cluster_distrib = {}
        # for year in years:
        #     with open('../data/march/clustering/'+year+'.json', 'r') as f:
        #         dataset = json.load(f)
        #     # create cluster graph
        #     nodes, edges = dataset['nodes'], dataset['edges']
        #     cluster_nodes = collections.defaultdict(list)
        #     cluster_edges = collections.defaultdict(list)
        #     nid_cluster = {}
        #     cluster_count = 0
        #     for node in nodes:
        #         cluster, nid = node['cluster'], node['id']
        #         cluster_nodes[cluster].append(node)
        #         nid_cluster[nid] = cluster
        #         if cluster > cluster_count:
        #             cluster_count = cluster
        #     cluster_count += 1
        #     for edge in edges:
        #         src, dst = edge['source'], edge['target']
        #         if nid_cluster[src] == nid_cluster[dst]:
        #             cluster = nid_cluster[src]
        #             cluster_edges[cluster].append(edge)
        #     # calculate similarity of cluster
        #     print('year: ', year, '   cluster count', cluster_count)
        #     print()
        #     cluster_distrib = {}
        #     for cluster in range(cluster_count):
        #         nodes, edges = cluster_nodes[cluster], cluster_edges[cluster]
        #         print('nodes count', len(nodes))
        #         graph = dict(nodes=nodes, edges=edges)
        #         # distrib = self.graphlet_distrib(graph)
        #         distrib = self.graphlet_count(graph)
        #         print('distrib', distrib)
        #         print()
        #         cluster_distrib[cluster] = {distrib}
        #     year_cluster_distrib[year] = cluster_distrib
        # with open('../data/march/clustering/year_cluster_distrib.json',
        #           'w') as f:
        #     json.dump(year_cluster_distrib, f)

        def log_scale(vector):
            wb = 0.001
            vec_sum = sum(vector)+wb*len(vector)
            result = [math.log((vec + wb)/vec_sum) for vec in vector]
            return result

        def laplacian_kernel(vec1, vec2):
            temp = -distance.cityblock(vec1, vec2)
            return np.exp(temp)

        with open('../data/march/clustering/year_cluster_distrib.json',
                  'r') as f:
            year_distrib = json.load(f)
        year_vector = {}
        for year in years:
            cluster_distrib = year_distrib[year]
            cluster_vector = {}
            for cluster, distrib in cluster_distrib.items():
                cluster_vector[cluster] = log_scale(distrib)
            year_vector[year] = cluster_vector
        results = {}
        for year1, vectors1 in year_vector.items():
            if str(year1) == '2017':
                break
            else:
                year2 = str(int(year1) + 1)
                vectors2 = year_vector[year2]
                key = str(year1)+':'+str(year2)
                if year1 == year2:
                    continue
                else:
                    temp_res = {}
                    for clst1, val1 in vectors1.items():
                        for clst2, val2 in vectors2.items():
                            temp_key = str(clst1)+':'+str(clst2)
                            temp = laplacian_kernel(val1, val2)
                            if temp < 0.0001 or temp == 1.0:
                                continue
                            temp_res[temp_key] = temp
                results[key] = temp_res
        with open('../data/march/clustering/year_similarity.json',
                  'w') as f:
            json.dump(results, f)


    def graphlet_count(self, dataset):
        patterns3 = [
            [(0, 1), (0, 2)],  # 3-1
            [(0, 1), (0, 2), (1, 2)],  # 3-2
        ]
        patterns4 = [
            [(0, 1), (1, 2), (2, 3)],  # 4-1
            [(0, 1), (0, 2), (0, 3)],  # 4-2
            [(0, 1), (1, 2), (2, 3), (0, 3)],  # 4-3
            [(0, 1), (1, 2), (1, 3), (2, 3)],  # 4-4
            [(0, 1), (0, 2), (1, 2), (2, 3), (0, 3)],  # 4-5
            [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (1, 3)],  # 4-6
        ]
        patterns5 = [
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
        # temp_dict = {3: patterns3, 4: patterns4, 5: patterns5}
        temp_dict = {3: patterns3, 4: patterns4}
        graphlet = []
        for node_num, patterns in temp_dict.items():
            for pattern in patterns:
                graph = gt.Graph(directed=False)
                nodes, edges = [], []
                for i in range(node_num):
                    node = graph.add_vertex()
                    nodes.append(node)
                for edge in pattern:
                    i, j = edge[0], edge[1]
                    edge = graph.add_edge(nodes[i], nodes[j])
                    edges.append(edge)
                print('add graphlet')
                graphlet.append(graph)
        # main graph
        main_graph = gt.Graph(directed=False)
        nodes, edges = dataset['nodes'], dataset['edges']
        m_nodes, m_edges = [], []
        id_revise = {}
        for i, node in enumerate(nodes):
            nid = node['id']
            id_revise[nid] = i
            m_node = main_graph.add_vertex()
            m_nodes.append(m_node)
        for edge in edges:
            src, dst = edge['source'], edge['target']
            src_i, dst_i = id_revise[src], id_revise[dst]
            m_edge = main_graph.add_edge(m_nodes[src_i], m_nodes[dst_i])
            m_edges.append(m_edge)
        distrib = [0] * len(graphlet)
        for i in range(len(graphlet)):
            vm = gt.subgraph_isomorphism(graphlet[i], main_graph)
            distrib[i] = len(vm)
            print('result', len(vm))
        return distrib

    def graphlet_distrib(self, graph):
        '''
        compare similarity between two graphs
        3,4,5 vertices 29 cases
        '''
        nodes, edges = graph['nodes'], graph['edges']
        if len(nodes) == 1:
            print('1 nodes')
            return [0]
        if len(nodes) == 2:
            print('2 nodes')
            return [1]
        patterns = [
            [(0, 1), (0, 2)],  # 3-1
            [(0, 1), (0, 2), (1, 2)],  # 3-2
            # [(0, 1), (1, 2), (2, 3)],  # 4-1
            [(0, 1), (0, 2), (0, 3)],  # 4-2
            # [(0, 1), (1, 2), (2, 3), (0, 3)],  # 4-3
            [(0, 1), (1, 2), (1, 3), (2, 3)],  # 4-4
            # [(0, 1), (0, 2), (1, 2), (2, 3), (0, 3)],  # 4-5
            [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (1, 3)],  # 4-6
            # [(0, 1), (1, 2), (2, 3), (3, 4)],  # 5-1
            # [(0, 1), (0, 2), (0, 3), (3, 4)],  # 5-2
            [(0, 1), (0, 2), (0, 3), (0, 4)],  # 5-3
            # [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)],  # 5-4
            # [(0, 1), (0, 2), (1, 2), (0, 3), (3, 4)],  # 5-5
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2)],  # 5-6
            # [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)],  # 5-7
            # [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4)],  # 5-8
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4)],  # 5-9
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (3, 4)],  # 5-10
            # [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 4)],  # 5-11
            # [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-12
            # [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)],  # 5-13
            # [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-14
            # [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)],  # 5-15
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 4), (3, 4)],  # 5-16
            # [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-17
            # [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
            #  (2, 3), (1, 4), (2, 4)],  # 5-18
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
             (2, 3), (3, 4), (0, 4)],  # 5-19
            # [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
            #  (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-20
            # [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3),
            #  (1, 4), (2, 3), (2, 4), (3, 4)],  # 5-21
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
        distrib = [0] * len(patterns)
        for cc, node in enumerate(nodes):
            print('===========node: ', cc, node['name'], '===========')
            source_graph = nx.Graph()
            nid = node['id']
            source_nodes = [nid]
            for edge in edges:
                s, t = edge['source'], edge['target']
                if s == nid:
                    source_graph.add_edge(s, t)
                    source_nodes.append(t)
                if t == nid:
                    source_graph.add_edge(s, t)
                    source_nodes.append(s)
            for edge in edges:
                s, t = edge['source'], edge['target']
                if s in source_nodes[1:] and t in source_nodes[1:]:
                    source_graph.add_edge(s, t)
            print('source graph complete')
            print(len(source_nodes))
            # check each pattern
            for i, pg in enumerate(pattern_graphs):
                print('pattern: ', i)
                if i < 2:  # 3 nodes
                    for sub_nodes in itertools.combinations(
                            source_nodes[1:], 2):
                        subg = source_graph.subgraph(sub_nodes + (nid,))
                        if nx.is_connected(subg) and \
                                nx.is_isomorphic(subg, pg):
                            distrib[i] += 1
                            break
                elif i >= 2 and i < 5:  # 4 nodes
                    for sub_nodes in itertools.combinations(
                            source_nodes[1:], 3):
                        subg = source_graph.subgraph(sub_nodes + (nid,))
                        if nx.is_connected(subg) and \
                                nx.is_isomorphic(subg, pg):
                            distrib[i] += 1
                            break
                else:  # 5 nodes
                    for sub_nodes in itertools.combinations(
                            source_nodes[1:], 4):
                        subg = source_graph.subgraph(sub_nodes + (nid,))
                        if nx.is_connected(subg) and \
                                nx.is_isomorphic(subg, pg):
                            distrib[i] += 1
                            break
            print(distrib)
        return distrib

    # def popular_tweets(self):
    #     dataset = pd.read_csv('../data/march/march.csv')
    #     dataset = dataset.values
    #     retweet_count = collections.defaultdict(int)
    #     for data in dataset:
    #         ymd, tid = data[0], data[3]
    #         year = ymd.split('-')[0]
    #         retweet_count[tid] += 1
    #
    #     def year_count():
    #         return {'2011': 0, '2012': 0, '2013': 0, '2014': 0,
    #                 '2015': 0, '2016': 0, '2017': 0}
    #     retweet_count_details = collections.defaultdict(year_count)
    #     threshold = 50
    #     tweet_id = []
    #     for data in dataset:
    #         ymd, tid = data[0], data[3]
    #         year = ymd.split('-')[0]
    #         if retweet_count[tid] > threshold:
    #             if tid not in tweet_id:
    #                 tweet_id.append(tid)
    #             retweet_count_details[tid][year] += 1
    #     jsonfile = dict(tid=tweet_id, details=retweet_count_details)
    #     with open('../data/march/popular_tweet.json', 'w') as f:
    #         json.dump(jsonfile, f)
    #
    # def cluster_overview(self):
    #     years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
    #     clusters_info = {}
    #     for year in years:
    #         with open('../data/clustered/'+year+'.json') as f:
    #             graph = json.load(f)
    #         nodes = graph['nodes']
    #         year_info = collections.defaultdict(list)
    #         for node in nodes:
    #             year_info[node['cluster']].append(node)
    #         cluster_count = len(year_info)
    #         user_count_in_cluster = []
    #         active_users_dict = {}
    #         for key, val in year_info.items():
    #             if key == -1:
    #                 continue
    #             active_users = []
    #             user_count_in_cluster.append(len(val))
    #             val.sort(key=lambda x: x['degree'], reverse=True)
    #             active_count = int(max(1, min(len(val)/100, 7)))
    #             val_count = 0
    #             while len(active_users) <= active_count:
    #                 if 'S' in val[val_count]['uid']:
    #                     active_users.append(val[val_count])
    #                 val_count += 1
    #                 if val_count >= len(val):
    #                     break
    #             active_users_dict[key] = active_users
    #             # most_active_users.append(val[:active_count])
    #         clusters_info[year] = dict(cluster_count=cluster_count,
    #                                    user_per_count=user_count_in_cluster,
    #                                    most_active_users=active_users_dict)
    #     with open('../data/clustered/cluster_overview.json', 'w') as f:
    #         json.dump(clusters_info, f)
    #
    # def active_users(self):
    #     '''
    #     return most active users from cluster_overview file
    #     '''
    #     with open('../data/clustered/cluster_overview.json', 'r') as f:
    #         dataset = json.load(f)
    #     jsonfile = {}
    #     for key, val in dataset.items():
    #         most_active_users = val['most_active_users']
    #         temp_users = []
    #         for clst, userlist in most_active_users.items():
    #             for user in userlist:
    #                 uid = user['uid']
    #                 temp_users.append(uid[1:])
    #         jsonfile[key] = temp_users
    #     with open('../data/clustered/temp.json', 'w') as f:
    #         json.dump(jsonfile, f)
    #
    # def cluster_contour(self):
    #     '''
    #     return contours of forcelayout graph each year
    #     '''
    #     years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
    #     result = {}
    #     for year in years:
    #         with open('../data/clustered/'+year+'.json') as f:
    #             data = json.load(f)
    #         nodes = data['nodes']
    #         colors = {}
    #         cluster_nodes = collections.defaultdict(list)
    #         for node in nodes:
    #             colors[node['cluster']] = node['color']
    #             cluster_nodes[node['cluster']].append([node['x'], node['y']])
    #         counter_nodes = {}
    #         for key, val in cluster_nodes.items():
    #             indexs = ConvexHull(np.array(val)).vertices
    #             boundary_nodes = [dict(x=val[i][0], y=val[i][1])
    #                               for i in indexs]
    #             counter_nodes[key] = dict(color=colors[key],
    #                                       boundary=boundary_nodes)
    #         result[year] = counter_nodes
    #     with open('../data/clustered/cluster_counter.json', 'w') as f:
    #         json.dump(result, f)
    #
    # def word_process(self):
    #     '''
    #     return word noun in each cluster yearly
    #     '''
    #     # return year_info => year: [{id: words},]
    #     dataset = pd.read_csv('../data/clustered/active_users_words.csv')
    #     dataset = dataset.values
    #     year_info = collections.defaultdict(
    #         lambda: collections.defaultdict(list))
    #     for data in dataset:
    #         ymd, influencer, words = data[0], 'S'+str(data[1]), data[4]
    #         year = ymd.split('-')[0]
    #         year_info[year][influencer].append(words)  # {2011:{id:[words]}}
    #     # return year: {cluster1: [[],[]], cluster2: [[]]}
    #     with open('../data/clustered/cluster_overview.json', 'r') as f:
    #         overview = json.load(f)  # {2011:{most_active_users:[{},{}]}}
    #     jsonfile = {}  # {2011: {0:[[],[]], 1:[[],[]}
    #     for year, information in overview.items():
    #         uid_words = year_info[year]
    #         cluster_words = collections.defaultdict(list)
    #         for clst, nodelist in information['most_active_users'].items():
    #             for node in nodelist:
    #                 user = node['uid']
    #                 words = uid_words[user]
    #                 cluster_words[clst].append(words)
    #         jsonfile[year] = cluster_words
    #     with open('../static/clustered/cluster_words.json', 'w') as f:
    #         json.dump(jsonfile, f)
    #
    # def word_clouds(self):
    #     '''
    #     return word cloud
    #     {year: {cluster:{word: count}}}
    #     '''
    #     with open('../data/clustered/cluster_words.json', 'r') as f:
    #         dataset = json.load(f)
    #     jsonfile = {}
    #     for year, clusters in dataset.items():
    #         cluster_words = {}
    #         for clst, clst_info in clusters.items():
    #             word_count = collections.defaultdict(int)
    #             for wordlist in clst_info:
    #                 for words in wordlist:
    #                     try:
    #                         word_temps = words.split(' ')
    #                     except:
    #                         continue
    #                     for word in word_temps:
    #                         word_count[word] += 1
    #             word_count_list = []
    #             for key, val in word_count.items():
    #                 word_count_list.append([key, val])
    #             cluster_words[clst] = word_count_list
    #         jsonfile[year] = cluster_words
    #     with open('../static/clustered/word_clouds.json', 'w') as f:
    #         json.dump(jsonfile, f)
    #
    # def graphSimilarity(self):
    #     '''
    #     compare similarity between two graphs
    #     3,4,5 vertices 29 cases
    #     '''
    #     patterns = [
    #         [(0, 1), (0, 2)],  # 3-1
    #         [(0, 1), (0, 2), (1, 2)],  # 3-2
    #         [(0, 1), (1, 2), (2, 3)],  # 4-1
    #         [(0, 1), (0, 2), (0, 3)],  # 4-2
    #         [(0, 1), (1, 2), (2, 3), (0, 3)],  # 4-3
    #         [(0, 1), (1, 2), (1, 3), (2, 3)],  # 4-4
    #         [(0, 1), (0, 2), (1, 2), (2, 3), (0, 3)],  # 4-5
    #         [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (1, 3)],  # 4-6
    #         [(0, 1), (1, 2), (2, 3), (3, 4)],  # 5-1
    #         [(0, 1), (0, 2), (0, 3), (3, 4)],  # 5-2
    #         [(0, 1), (0, 2), (0, 3), (0, 4)],  # 5-3
    #         [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)],  # 5-4
    #         [(0, 1), (0, 2), (1, 2), (0, 3), (3, 4)],  # 5-5
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2)],  # 5-6
    #         [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)],  # 5-7
    #         [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4)],  # 5-8
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4)],  # 5-9
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (3, 4)],  # 5-10
    #         [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 4)],  # 5-11
    #         [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-12
    #         [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)],  # 5-13
    #         [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-14
    #         [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)],  # 5-15
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 4), (3, 4)],  # 5-16
    #         [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-17
    #         [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3),
    #          (2, 3), (1, 4), (2, 4)],  # 5-18
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
    #          (2, 3), (3, 4), (0, 4)],  # 5-19
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
    #          (1, 3), (2, 3), (1, 4), (2, 4)],  # 5-20
    #         [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3),
    #          (1, 4), (2, 3), (2, 4), (3, 4)],  # 5-21
    #     ]
    #     pattern_graphs = []
    #     # init pattern graphs | target graphs
    #     for pattern in patterns:
    #         temp = nx.Graph()
    #         for edge in pattern:
    #             s, t = edge[0], edge[1]
    #             temp.add_edge(s, t)
    #         pattern_graphs.append(temp)
    #     print('init pattern graphs done')
    #     graphlets = {}
    #     for _, mon in self.month.items():
    #         print('in month:', mon)
    #         with open(self.path + 'target/' + mon + '.json', 'r') as f:
    #             graph = json.load(f)
    #             nodes = graph['nodes']
    #             edges = graph['edges']
    #             reserved = []
    #             distrib = [0] * len(patterns)
    #             for cc, node in enumerate(nodes):  # check each node
    #                 print('===========node: ', cc, node[
    #                       'degree'], '===========')
    #                 # init source graph
    #                 source = nx.Graph()
    #                 uid = node['name']
    #                 degree = node['degree']
    #                 if degree < 2:
    #                     print('no match pattern')
    #                     continue
    #                 elif degree > 100:
    #                     print('reserved node')
    #                     reserved.append(uid)
    #                     continue
    #                 else:
    #                     source_nodes = [uid]
    #                     for edge in edges:
    #                         if len(source_nodes) == degree + 1:
    #                             break
    #                         s, t = edge['source'], edge['target']
    #                         if s == uid:
    #                             source.add_edge(s, t)
    #                             source_nodes.append(t)
    #                         if t == uid:
    #                             source.add_edge(s, t)
    #                             source_nodes.append(s)
    #                     for edge in edges:
    #                         s, t = edge['source'], edge['target']
    #                         if s in source_nodes[1:] and t in source_nodes[1:]:
    #                             source.add_edge(s, t)
    #                     print('source graph complete')
    #                     # check each pattern (geanerate target graph)
    #                     for i, pg in enumerate(pattern_graphs):
    #                         print('pattern: ', i)
    #                         if i < 2:  # 3 nodes
    #                             for sub_nodes in itertools.combinations(
    #                                     source_nodes[1:], 2):
    #                                 subg = source.subgraph(sub_nodes + (uid,))
    #                                 if nx.is_connected(subg) and \
    #                                         nx.is_isomorphic(subg, pg):
    #                                     distrib[i] += 1
    #                                     break
    #                         elif i >= 2 and i < 8:  # 4 nodes
    #                             for sub_nodes in itertools.combinations(
    #                                     source_nodes[1:], 3):
    #                                 subg = source.subgraph(sub_nodes + (uid,))
    #                                 if nx.is_connected(subg) and \
    #                                         nx.is_isomorphic(subg, pg):
    #                                     distrib[i] += 1
    #                                     break
    #                         else:  # 5 nodes
    #                             for sub_nodes in itertools.combinations(
    #                                     source_nodes[1:], 4):
    #                                 subg = source.subgraph(sub_nodes + (uid,))
    #                                 if nx.is_connected(subg) and \
    #                                         nx.is_isomorphic(subg, pg):
    #                                     distrib[i] += 1
    #                                     break
    #                     print(distrib)
    #         graphlets[mon] = dict(distrib=distrib, reserved=reserved)
    #     with open(self.path + 'graphlets.json', 'w') as f:
    #         json.dump(graphlets, f)


if __name__ == '__main__':
    processor = Processor()
    processor.forcelayoutJSON()
    # processor.cluster_similarity()
    # processor.active_influencer()
    # processor.graphSimilarity()
    # processor.cluster_overview()
    # processor.cluster_contour()
    # processor.active_users()
    # processor.word_process()
    # processor.word_clouds()