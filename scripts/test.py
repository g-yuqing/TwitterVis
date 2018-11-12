import collections
import json
import math


class GNode():
    def __init__(self, nid, value):
        self.nid = nid
        self.value = value
        self.level = 0
        self.incomes = []
        self.outcomes = []

    def add_income(self, gnode):
        if gnode not in self.incomes:
            self.incomes.append(gnode)

    def add_outcome(self, gnode):
        if gnode not in self.outcomes:
            self.outcomes.append(gnode)

    def dump_incomes(self):
        return self.incomes

    def dump_outcomes(self):
        return self.outcomes


if __name__ == '__main__':
    gnode1 = GNode(0, 'A')
    gnode2 = GNode(1, 'B')
    gnode2.incomes = [gnode1]
    gnode3 = GNode(2, 'C')
    gnode3.incomes = [gnode1]
    gnode4 = GNode(3, 'D')
    gnode4.incomes = [gnode1]
    gnode5 = GNode(4, 'E')
    gnode5.incomes = [gnode2]
    gnode6 = GNode(5, 'F')
    gnode6.incomes = [gnode4]
    gnode7 = GNode(6, 'G')
    gnode7.incomes = [gnode5]
    # outcomes
    gnode1.outcomes = [gnode2, gnode3, gnode4]
    gnode2.outcomes = [gnode5]
    gnode4.outcomes = [gnode6]
    gnode5.outcomes = [gnode7]
    gnode7.outcomes = [gnode1]
    word_gnode = {
        'A': gnode1,
        'B': gnode2,
        'C': gnode3,
        'D': gnode4,
        'E': gnode5,
        'F': gnode6,
        'G': gnode7
    }

    def process_cycle(word_gnode):
        stack = {}
        visited = {}
        result = []
        for word, gnode in word_gnode.items():
            visited[gnode] = False
            stack[gnode] = False

        def dfs(u):
            if visited[u]:
                return
            visited[u] = True
            stack[u] = True
            for v in u.outcomes:
                if stack[v]:
                    result.append([u, v])
                else:
                    dfs(v)
            # del stack[u]
            stack[u] = False
        for word, gnode in word_gnode.items():
            dfs(gnode)
        for res in result:
            print(res[0].value, res[1].value)

    process_cycle(word_gnode)

    def set_level(gnode):
        if not gnode.incomes:  # empty
            gnode.level = 1
        else:
            levellist = []
            for ignode in gnode.incomes:
                if ignode.level == 0:
                    set_level(ignode)
                levellist.append(ignode.level)
            gnode.level = 1 + max(levellist)
    for gnode in [gnode3, gnode6, gnode7]:
        set_level(gnode)
    nodes = [
        dict(id=0, word='A', color='#4682b4'),
        dict(id=1, word='B', color='#4682b4'),
        dict(id=2, word='C', color='#4682b4'),
        dict(id=3, word='D', color='#4682b4'),
        dict(id=4, word='E', color='#4682b4'),
        dict(id=5, word='F', color='#4682b4'),
        dict(id=6, word='G', color='#4682b4')]
    links = [
        dict(source=0, target=1),
        dict(source=0, target=2),
        dict(source=0, target=3),
        dict(source=1, target=4),
        dict(source=3, target=5),
        dict(source=4, target=6)]
    xoffsets = []
    level_node = collections.defaultdict(list)
    for _, node in word_gnode.items():
        level_node[node.level].append(node)
    prevlist = []
    for lvl, gnlist in level_node.items():
        for gn in gnlist:
            xoffsets.append(dict(node=gn.nid, offset=gn.level*25))
        prevlist = gnlist
    constraints = [
        dict(type='alignment', axis='x', offsets=xoffsets)]
    res = dict(nodes=nodes, links=links, constraints=constraints)
    with open('../data/retweet-2011/topic_graph.json', 'w') as f:
            json.dump(res, f)
