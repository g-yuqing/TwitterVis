import json
import collections
import datetime


class Node():
    def __init__(self, value, word, depth):
        self.value = value  # a,b,c,d
        self.word = word
        self.depth = depth
        self.child = []
        self.parent = None


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

    def pop_income(self, gnode):
        if gnode in self.incomes:
            self.incomes.remove(gnode)

    def pop_outcome(self, gnode):
        if gnode in self.outcomes:
            self.outcomes.remove(gnode)

    def dump_incomes(self):
        return self.incomes

    def dump_outcomes(self):
        return self.outcomes


def topic_graph(leafnodes):
    # generate graph
    word_gnode, idx = {}, 0
    for lfnode in leafnodes:
        words = lfnode.value.split(',')
        for i in range(len(words)-1):
            word1, word2 = words[i], words[i+1]
            if word1 not in word_gnode:
                gnode = GNode(idx, word1)
                word_gnode[word1] = gnode
                idx += 1
            if word2 not in word_gnode:
                gnode = GNode(idx, word2)
                word_gnode[word2] = gnode
                idx += 1
            gnode1, gnode2 = word_gnode[word1], word_gnode[word2]
            gnode2.add_income(gnode1)
            gnode1.add_outcome(gnode2)

    # process circle
    # reconstruct word tree
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
        # remove cycle
        for res in result:
            gnode1, gnode2 = res[0], res[1]
            # print(gnode1.value, gnode2.value)
            gnode2.pop_income(gnode1)
            gnode1.pop_outcome(gnode2)
    process_cycle(word_gnode)

    # word level
    def set_level(word_gnode):
        def dfs(gnode):
            if not gnode.incomes:  # empty
                gnode.level = 1
            else:
                levellist = []
                for ignode in gnode.incomes:
                    if ignode.level == 0:
                        dfs(ignode)
                    levellist.append(ignode.level)
                gnode.level = 1 + max(levellist)
        for word, gnode in word_gnode.items():
            dfs(gnode)
    set_level(word_gnode)

    # set topic graph: constraints, nodes, links
    nodes, links = [], []
    xoffsets = []
    # level_gnode = collections.defaultdict(list)
    for _, gnode in word_gnode.items():
        # level_gnode[gnode.level].append(gnode)
        xoffsets.append(dict(node=gnode.nid, offset=(gnode.level-1)*15))
        nodes.append(dict(id=gnode.nid, word=gnode.value, color='#777'))
        for outnode in gnode.dump_outcomes():
            links.append(dict(source=gnode.nid, target=outnode.nid))
    # xoffsets = []
    # for lvl, gnlist in level_gnode.items():
    #     for gn in gnlist:
    #         xoffsets.append(dict(node=gn.nid, offset=gn.level*7))
    constraints = [
        dict(type='alignment', axis='x', offsets=xoffsets)]

    res = dict(nodes=nodes, links=links, constraints=constraints)
    with open('../data/retweet-2011/topic_graph.json', 'w') as f:
            json.dump(res, f)

# class Neighbor():
#     def __init__(self):
#         self.lefts = set()
#         self.rights = set()
#
#
# def topic_graph(root, leafnodes, valnode, keywords):
#     nodes, links, constraints = [], [], []
#     nodeidx = {}
#     paths = []
#
#     def depth_search(curnode, path):
#         '''
#         save all sentences into paths
#         '''
#         if not curnode.child:
#             paths.append(path)
#         else:
#             for childnode in curnode.child:
#                 depth_search(childnode, path+[childnode])
#     # calculate all possible paths
#     depth_search(root, [])
#     # print path
#     for node in leafnodes:
#         print(node.value)
#     print(len(paths), len(leafnodes))
#     # extract effective paths
#     sentpaths = [path for path in paths if path[-1] in leafnodes]
#     print(len(sentpaths))
#     nodeidx, idx = {}, 0
#     # add nodes and links
#     for sentpath in sentpaths:  # sentpath list of nodes in text order
#         prevnode = None
#         for node in sentpath:
#             if node not in nodeidx:
#                 nodeidx[node] = idx
#                 color = '#4682b4' if node.word in keywords else '#777'
#                 nodes.append(dict(id=idx, word=node.word, color=color))
#                 idx += 1
#             if prevnode:
#                 links.append(dict(source=nodeidx[prevnode],
#                                   target=nodeidx[node]))
#             prevnode = node
#     # constraints
#     # collect neighbor information
#     nodeneighbor = collections.defaultdict(Neighbor)
#     for node in nodeidx:
#         for sentpath in sentpaths:
#             for i in range(len(sentpath)):
#                 if node == sentpath[i]:
#                     if i > 0:
#                         nodeneighbor[node].lefts.add(sentpath[i-1])
#                     if i < len(sentpath) - 1:
#                         nodeneighbor[node].rights.add(sentpath[i+1])
#     # set constraints
#     for node1, neighbor in nodeneighbor.items():
#         lefts, rights = list(neighbor.lefts), list(neighbor.rights)
#         # process left nodes
#         if len(lefts) == 0:
#             pass
#         else:
#             prevnode = None
#             for node2 in lefts:
#                 # x: 25
#                 constraints.append(dict(axis='x', left=nodeidx[node2],
#                                         right=nodeidx[node1], gap=25))
#                 if prevnode:
#                     # x: 0, y: 15 => vertical
#                     constraints.append(dict(axis='x', left=nodeidx[prevnode],
#                                             right=nodeidx[node2], gap=0))
#                     constraints.append(dict(axis='y', left=nodeidx[prevnode],
#                                             right=nodeidx[node2], gap=10))
#                 else:
#                     # y: 0 => horizontal
#                     # constraints.append(dict(axis='y', left=nodeidx[node2],
#                     #                         right=nodeidx[node1], gap=10))
#                     pass
#                 prevnode = node2
#         # process right nodes
#         if len(rights) == 0:
#             pass
#         else:
#             prevnode = None
#             for node2 in rights:
#                 # x: 25
#                 constraints.append(dict(axis='x', left=nodeidx[node1],
#                                         right=nodeidx[node2], gap=25))
#                 if prevnode:
#                     # x: 0, y: 15 => vertical
#                     constraints.append(dict(axis='x', left=nodeidx[prevnode],
#                                             right=nodeidx[node2], gap=0))
#                     # constraints.append(dict(axis='y', left=nodeidx[prevnode],
#                     #                         right=nodeidx[node2], gap=25))
#                 else:
#                     # y: 0 => horizontal
#                     # constraints.append(dict(axis='y', left=nodeidx[node1],
#                     #                         right=nodeidx[node2], gap=0))
#                     pass
#                 prevnode = node2
#
#     with open('../data/retweet-2011/topic_graph.json', 'w') as f:
#         json.dump(dict(nodes=nodes, links=links, constraints=constraints), f)


def sentree(corpus, kwscore):
    '''
    return list of leaf pattern(list)
    '''
    def seperate_corpus(words, corpus):
        '''
        return 2 lists containing words and not
        '''
        def sublist(words, text):
            '''
            check wheather is a sublist
            '''
            for idx in [i for i, t in enumerate(text) if t == words[0]]:
                if text[idx: idx+len(words)] == words:
                    return True
            return False
        # convert string to list
        words = words.split(',')
        trglist, eptylist = [], []
        for text in corpus:
            if sublist(words, text):
                trglist.append(text)
            else:
                eptylist.append(text)
        assert(len(trglist)+len(eptylist) == len(corpus))
        return trglist, eptylist

    def most_frequent_word(words, corpus):
        if words == 'empty':
            curwords_score = collections.defaultdict(int)
            for text in corpus:
                for word in text:
                    curwords_score[word] += 1
            curwords = max(curwords_score, key=curwords_score.get)
            # temp = list(curwords_score.keys())
            # print('most_frequent_word: => ', temp,
            #       [curwords_score[k] for k in temp], len(temp),
            #       curwords, ':', curwords_score[curwords])
            return curwords
        else:
            # convert string to list
            words = words.split(',')
            wordslen = len(words)
            curwords_score = collections.defaultdict(int)
            for text in corpus:
                # find sublist position
                for idx in [i for i, t in enumerate(text) if t == words[0]]:
                    if text[idx: idx+wordslen] == words:
                        start, end = idx, idx+wordslen-1
                        # take previous word
                        if start > 0:
                            newword = text[start-1: end+1]
                            curwords_score[','.join(newword)] += 1
                        # take next word
                        if end < len(text)-1:
                            newword = text[start: end+2]
                            curwords_score[','.join(newword)] += 1
            # get the most frequent words
            try:
                curwords = max(curwords_score, key=curwords_score.get)
            except:
                curwords = None
            # temp = list(curwords_score.keys())
            # print('most_frequent_word: => ', temp,
            #       [curwords_score[k] for k in temp], len(temp),
            #       curwords, ':', curwords_score[curwords])
            return curwords

    def pruning(value_node):
        leaflist = []
        for word, node in value_node.items():
            if not node.child:  # is leaf
                leaflist.append(node)
        resnode = []
        for idx, leafnode in enumerate(leaflist):
            templist = leafnode.value.split(',')
            if len(templist) == 1:
                prune = True
            elif len(templist) == 2:
                prune = False
                if templist[0] == templist[1] or templist[0] not in kwlist or\
                        templist[1] not in kwlist:
                    prune = True
            elif len(templist) == 3:
                prune = False
                for word in templist:
                    if word not in kwlist:
                        prune = True
                        break
            else:
                prune = True
                for word in templist:
                    if word in kwlist:
                        prune = False
                        break
            if not prune:
                resnode.append(leafnode)
        # print('result: ', [d.value for d in resnode])
        return resnode

    # nodes, links, constraints = [], [], []
    kwlist = list(map(lambda d: d[0], kwscore))
    print('keywords: ', kwlist)
    # candidates = []
    # for text in corpus:
    #     temp = [w for w in text if w in kwlist]
    #     if len(temp) > 1:
    #         candidates.append(list(set(temp)))
    # print('corpus&candidates length: ', len(corpus), len(candidates))
    leafptns = {'empty': corpus}  # words: corpus
    root = Node('empty', 'empty', 0)
    value_node = {'empty': root}
    count = 0
    wordscount = 200
    while True:
        leafwords = list(leafptns.keys())
        leafcorpus = [leafptns[k] for k in leafwords]
        # pop longest words and corpus in leafptns
        lengths = list(map(lambda d: len(d), leafcorpus))
        idx = lengths.index(max(lengths))
        popwords = leafwords[idx]
        popcorpus = leafptns.pop(popwords)
        # process poped (longest) corpus
        curtarget = most_frequent_word(popwords, popcorpus)
        if curtarget is None or len(popcorpus) == 0:
            break
        trglist, eptylist = seperate_corpus(curtarget, popcorpus)
        # add to leafptns
        leafptns[popwords] = eptylist
        leafptns[curtarget] = trglist
        # add to tree graph
        popnode = value_node[popwords]
        # init curnode
        if popwords.split(',') == curtarget.split(',')[1:]:
            tempword = curtarget.split(',')[0]
        else:
            tempword = curtarget.split(',')[-1]
        curnode = Node(curtarget, tempword, popnode.depth+1)
        value_node[curtarget] = curnode
        popnode.child.append(curnode)
        curnode.parent = popnode
        # print(count, ': words => ', popwords, curtarget)
        # print(count, ': length => ', len(trglist), len(eptylist))
        # print(count, ': leafptns => ', list(leafptns.keys()))
        # print(count, ': leafptns => ',
        #       [len(leafptns[k]) for k in list(leafptns.keys())])
        count += 1
        # check whether stop
        wordset = set()
        # for words in list(leafptns.keys()):
        for words in [d.value for d in pruning(value_node)]:
            wordset = wordset.union(set(words.split(',')))
        if len(wordset) > wordscount:
            break
    # pruning
    leafnodes = pruning(value_node)
    for ln in leafnodes:
        print(ln.value)
    # topic_graph(root, leafnodes, value_node, kwlist)
    topic_graph(leafnodes)


def main():
    timestep, movestep = 5, 1
    count = 5 * timestep
    bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
    with open('../data/retweet-2011/sample.json', 'r') as f:
        tid_info = json.load(f)
    date_corpus = collections.defaultdict(list)
    for tid, info in tid_info.items():
        text = info['words']
        date_rt = info['rtd']  # dictionary
        for date in date_rt:
            date_corpus[date].append(text)
    with open('../data/retweet-2011/keywords.json', 'r') as f:
        date_keywords = json.load(f)
    # rearrange date
    state_kwscore, state_corpus = {}, collections.defaultdict(list)
    start = datetime.date(2011, 3, 11)
    end = datetime.date(2011, 12, 31) - datetime.timedelta(days=timestep-1)
    current = start
    while current <= end:
        kw_weight = collections.Counter()
        corpuslist = []
        for i in range(timestep):
            date = (current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            # keywords
            kw_weight += collections.Counter(date_keywords[date])
            # corpus
            corpuslist += date_corpus[date]
        # keywords
        # remove big words
        for bw in bigwords:
            if bw in kw_weight:
                del kw_weight[bw]
        kwscore = kw_weight.most_common(count)
        state_kwscore[current.strftime('%Y-%m-%d')] = kwscore
        # corpus
        # remove the repeated word in each text
        temp = set(map(tuple, corpuslist))  # {(), (), ()}
        # state_corpus: [[word1, word2], [word3, word4, word5],]
        state_corpus[current.strftime('%Y-%m-%d')] = list(map(list, temp))
        current += datetime.timedelta(days=movestep)
    # for state, kwscore in state_kwscore.items():
    #     corpus = state_corpus[state]
    #     sentree(corpus, kwscore)
    #     break
    state = '2011-03-11'
    corpus, kwscore = state_corpus[state], state_kwscore[state]
    sentree(corpus, kwscore)


if __name__ == '__main__':
    main()
