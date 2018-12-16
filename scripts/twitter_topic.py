import json
import collections
import datetime
import sys
sys.setrecursionlimit(100000)


def generate_graph(roots, kwlist):
    class TopicNode():
        def __init__(self, nid, word):
            self.nid = nid
            self.word = word
            self.color = '#2A363B'  # '#474747'
            self.frequency = 0
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

    # init topic graph
    idxnode = {}

    def init_topicgrpah():
        idx = 0

        def dfs(treenode1, topicnode1):
            if not treenode1.child:  # empty
                return
            else:
                nonlocal idx
                value1 = treenode1.value
                for treenode2 in treenode1.child:
                    value2 = treenode2.value
                    word2 = treenode2.word
                    topicnode2 = TopicNode(idx, word2)
                    idxnode[idx] = topicnode2
                    idx += 1
                    # check left or right side
                    if value1.split(',') == value2.split(',')[1:]:  # left
                        topicnode1.add_income(topicnode2)
                        topicnode2.add_outcome(topicnode1)
                    else:  # right side
                        topicnode2.add_income(topicnode1)
                        topicnode1.add_outcome(topicnode2)
                    dfs(treenode2, topicnode2)
        for root in roots:
            word1 = root.word
            topicnode = TopicNode(idx, word1)
            idxnode[idx] = topicnode
            idx += 1
            dfs(root, topicnode)
    init_topicgrpah()

    # process circle
    # reconstruct topic tree
    def process_cycle(idxnode):
        stack = {}
        visited = {}
        result = []
        for _, node in idxnode.items():
            visited[node] = False
            stack[node] = False

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
        for _, node in idxnode.items():
            dfs(node)
        # remove cycle
        for res in result:
            node1, node2 = res[0], res[1]
            node2.pop_income(node1)
            node1.pop_outcome(node2)
    process_cycle(idxnode)

    # set word level
    def set_level(idxnode):
        def dfs(node):
            if not node.incomes:  # empty
                node.level = 1
            else:
                levellist = []
                for inode in node.incomes:
                    if inode.level == 0:
                        dfs(inode)
                    levellist.append(inode.level)
                node.level = max(levellist) + 1
        for _, node in idxnode.items():
            dfs(node)
    set_level(idxnode)

    # generate topic graph
    frequency = collections.defaultdict(int)
    for _, node in idxnode.items():
        frequency[node.word] += 1
    nodes, links, constraints = [], [], []
    xoffsets = []
    for _, node in idxnode.items():
        innodes, outnodes = node.dump_incomes(), node.dump_outcomes()
        inlen, outlen = len(innodes), len(outnodes)
        # nodes
        if node.word in kwlist:
            node.color = '#E84A5F'  # '#CC527A'
        nodes.append(dict(id=node.nid, word=node.word, color=node.color,
                          tf=frequency[node.word]+inlen+outlen))
        # links
        for outnode in outnodes:
            links.append(dict(source=node.nid, target=outnode.nid))
        # constraints
        # vertical
        for i in range(outlen-1):
            onode1, onode2 = outnodes[i], outnodes[i+1]
            # constraints.append(dict(axis='x', left=onode1.nid,
            #                         right=onode2.nid, gap=0, equality='true'))
            constraints.append(dict(axis='y', left=onode1.nid,
                                    right=onode2.nid, gap=10))
        # horizontal
        if outlen > 0:
            # constraints.append(dict(axis='y', left=node.nid,
            #                         right=outnodes[int(outlen/2)].nid,
            #                         gap=0, equality='true'))
            # constraints.append(dict(axis='x', left=node.nid,
            #                         right=outnodes[int(outlen/2)].nid, gap=25))
            length = list(map(lambda d: len(d.word), outnodes))
            right = length.index(max(length))
            constraints.append(dict(axis='x', left=node.nid,
                                    right=outnodes[right].nid, gap=10))
    graph = dict(nodes=nodes, links=links, constraints=constraints)
    # with open('../data/retweet-2011/topic_graph.json', 'w') as f:
    #     json.dump(graph, f)
    return graph


def wordburst_graph(roots, date):
    def dfs(trnode):
        if not trnode.child:
            return {'name': trnode.word, 'value': 1}
        else:
            children = []
            for child in trnode.child:
                children.append(dfs(child))
            return {'name': trnode.word, 'children': children}
    # children = [dfs(root)]
    # result = {'name': date, 'children': children}

    # reschildren = []
    # for root in roots:
    #     reschildren.append(dfs(root))
    # result = {'name': date, 'children': reschildren}
    result = dfs(roots[0])
    return result


def extract_sentences(corpus, kwlist, thres=100):
    class TreeNode():
        def __init__(self, word, value):
            self.word = word
            self.value = value
            self.child = []
            self.parent = None

    def pruning(result, kwlist):
        '''
        return
        1. pruned leaf words (set type)
        2. count of words
        '''
        # pruning
        resleaves = set()
        wordlist = []
        for sentence in result:
            wordlist = sentence.split(',')
            if len(wordlist) == 1:
                prune = True
                if wordlist[0] == 'empty':
                    prune = False
            elif len(wordlist) == 2:
                prune = False
                if wordlist[0] == wordlist[1] or wordlist[0] not in kwlist or\
                        wordlist[1] not in kwlist:
                    prune = True
            elif len(wordlist) == 3:
                prune = False
                for word in wordlist:
                    if word not in kwlist:
                        prune = True
                        break
            else:
                prune = True
                for word in wordlist:
                    prune = False
                    break
            if not prune:
                resleaves.add(sentence)
        # counting word
        for sentence in resleaves:
            for w in sentence.split(','):
                if w not in wordlist:
                    wordlist.append(w)
        return resleaves, len(wordlist)

    def process_pop(popword, popcorpus):
        '''
        return
        1. most frequent word
        2. text list contains word
        3. text list not contains word
        '''
        word_score = collections.defaultdict(int)
        word_corpus = collections.defaultdict(list)
        if popword == 'empty':
            for text in popcorpus:
                for word in text:
                    word_score[word] += 1
                    word_corpus[word].append(text)
            reswords = max(word_score, key=word_score.get)
            rescorpus = word_corpus[reswords]
            resempty = [t for t in popcorpus if t not in rescorpus]
            assert len(rescorpus)+len(resempty) == len(popcorpus)
            return reswords, rescorpus, resempty
        else:
            words = popword.split(',')
            wordslen = len(words)
            for text in popcorpus:
                # find sublist position
                for idx in [i for i, t in enumerate(text) if t == words[0]]:
                    if text[idx: idx+wordslen] == words:
                        start, end = idx, idx+wordslen-1
                        # previous word
                        if start > 0:
                            newword = text[start-1: end+1]
                            newword = ','.join(newword)
                            word_score[newword] += 1
                            word_corpus[newword].append(text)
                        # next word
                        if end < len(text)-1:
                            newword = text[start: end+2]
                            newword = ','.join(newword)
                            word_score[newword] += 1
                            word_corpus[newword].append(text)
            # most frequent words
            try:
                reswords = max(word_score, key=word_score.get)
                rescorpus = word_corpus[reswords]
                resempty = [t for t in popcorpus if t not in rescorpus]
                assert len(rescorpus)+len(resempty) == len(popcorpus)
            except:
                reswords = None
                rescorpus = None
                resempty = None
            return reswords, rescorpus, resempty

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
            return curwords

    # print('keywords: ', kwlist)
    leaves = {'empty': corpus}  # words: corpus
    value_node = {}
    result = set()

    def sentree(leaves):
        _, count = pruning(result, kwlist)
        if 'empty' in leaves:
            if len(leaves['empty']) < 100:
                del leaves['empty']
        if count >= thres:
            return
        else:
            # leaves infomartion
            leafwords = list(leaves.keys())
            leafcorpus = list(leaves.values())
            # find the lagerest corpus
            lengths = list(map(lambda d: len(d), leafcorpus))
            idx = lengths.index(max(lengths))
            # determine the popword according the length
            popword = leafwords[idx]
            popcorpus = leaves.pop(popword)
            mfword = most_frequent_word(popword, popcorpus)
            if mfword is None or len(popcorpus) == 0:
                return
            mflist, eptylist = seperate_corpus(mfword, popcorpus)
            # set result: leaves may contains abc & abcd
            # result only contains abcd
            if popword in result:
                result.remove(popword)
            result.add(mfword)
            leaves[mfword] = mflist
            leaves[popword] = eptylist

            # set sentence tree graph
            if popword == 'empty':
                tn = TreeNode(mfword, mfword)
                value_node[mfword] = tn
            else:
                popnode = value_node[popword]
                if popword.split(',') == mfword.split(',')[1:]:
                    curword = mfword.split(',')[0]
                else:
                    curword = mfword.split(',')[-1]
                curnode = TreeNode(curword, mfword)
                value_node[mfword] = curnode
                curnode.parent = popnode
            # set sentence tree graph end
            sentree(leaves)
    sentree(leaves)
    # prune leaves
    resleaves, count = pruning(result, kwlist)
    # print(count)
    # for sentence in resleaves:
    #     print(sentence)
    # remove root
    resroots = []
    for value, node in value_node.items():
        if node.value in resleaves:
            curnode = node
            while curnode.parent:
                if curnode not in curnode.parent.child:
                    curnode.parent.child.append(curnode)
                curnode = curnode.parent
            if curnode not in resroots:
                resroots.append(curnode)
    return resleaves, resroots


def generate_database(timestep=5, movestep=1):
    count = 5 * timestep
    bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
    with open('../data/retweet-2011/sample.json', 'r') as f:
        tid_info = json.load(f)
    date_word_text = collections.defaultdict(list)
    for tid, info in tid_info.items():
        words = info['words']
        count = info['count']
        content = info['text']
        while content[:2] == 'RT':
            idx = content.find(':') + 2
            content = content[idx:]
        date_rt = info['rtd']  # dictionary
        for date in date_rt:
            date_word_text[date].append(dict(words=words, text=content,
                                             count=count))
    with open('../data/retweet-2011/keywords.json', 'r') as f:
        date_keywords = json.load(f)
    # rearrange date
    state_kwscore, state_corpus = {}, collections.defaultdict(list)
    start = datetime.date(2011, 3, 11)
    end = datetime.date(2011, 12, 31) - datetime.timedelta(days=timestep-1)
    current = start
    while current <= end:
        kw_weight = collections.Counter()
        # corpuslist = []
        word_text_list = []
        for i in range(timestep):
            date = (current+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            # keywords
            kw_weight += collections.Counter(date_keywords[date])
            # corpus
            word_text_list += date_word_text[date]
        # keywords
        # remove big words
        for bw in bigwords:
            if bw in kw_weight:
                del kw_weight[bw]
        kwscore = kw_weight.most_common(count)
        state_kwscore[current.strftime('%Y-%m-%d')] = kwscore
        # corpus
        # remove the repeated word in each words
        for idx, word_text in enumerate(word_text_list):
            words = list(tuple(word_text['words']))
            text = word_text['text']
            count = word_text['count']
            # [{words:[str1, str2, ], corpus: str}, {}]
            word_text_list[idx] = dict(words=words, text=text, count=count)
        state_corpus[current.strftime('%Y-%m-%d')] = word_text_list
        current += datetime.timedelta(days=movestep)
    with open('../data/retweet-2011/state_database.json', 'w') as f:
        json.dump(dict(corpus=state_corpus, kwscore=state_kwscore), f)


def main():
    timestep, movestep = 5, 1
    count = 5 * timestep
    bigwords = ['福島', '福島県', '原発', '福島原発', '東電', '放射能', '放射線']
    # date words
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
    # sentence tree
    state = '2011-04-11'
    corpus, kwscore = state_corpus[state], state_kwscore[state]
    kwlist = list(map(lambda d: d[0], kwscore)) + bigwords
    # extract sentences
    _, roots = extract_sentences(corpus, kwlist)
    # generate graph
    generate_graph(roots, kwlist)


if __name__ == '__main__':
    # main()
    generate_database()
