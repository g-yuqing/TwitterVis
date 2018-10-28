import json
import collections
import datetime


class Node():
    def __init__(self, value, word, depth):
        self.val = value  # a,b,c,d
        self.word = word
        self.depth = depth
        self.child = []
        self.parent = None


idx = 0


def topic_graph(root, leafnodes, valnode):
    nodes, links, constraints = [], [], []
    nodeidx = {}
    paths = []

    def depth_search(curnode, path):
        global idx
        if not curnode.child:
            paths.append(path)
        else:
            for childnode in curnode.child:
                if childnode not in nodeidx:
                    nodeidx[childnode] = idx
                    idx += 1
                depth_search(childnode, path+[childnode])
    depth_search(root, [])
    # print path
    for path in paths:
        print(path[-1].val)
    print('===============')
    for node in leafnodes:
        print(node.val)
    print(len(paths), len(leafnodes))
    # generate graph
    wordnode, gnodeidx, index = {}, {}, 0
    sentences = []
    leafval = [d.val for d in leafnodes]
    for path in paths:
        if path[-1].val in leafval:  # effective path
            prevnode = None
            sentences.append(path[-1].val)
            for node in path:
                if node not in gnodeidx:
                    gnodeidx[node] = index
                    wordnode[node.word] = node
                    index += 1
                    nodes.append(dict(id=gnodeidx[node], word=node.word))
                if prevnode:
                    links.append(dict(source=gnodeidx[prevnode],
                                      target=gnodeidx[node]))
                prevnode = node
    # constedlist = []
    # for sentence in sentences:
    #     wordlist = sentence.split(',')
    #     for i in range(len(wordlist)-1):
    #         node1 = wordnode[wordlist[i]]
    #         node2 = wordnode[wordlist[i+1]]
    #         idx1 = gnodeidx[node1]
    #         idx2 = gnodeidx[node2]
    #         # horizonal constraints
    #         constraints.append(dict(axis='x', left=idx1, right=idx2, gap=15))
    #         # vertical constraints
    #         if node1 not in constedlist:
    #             constedlist.append(node1)
    #             effectivechild = [n for n in node1.child if n in gnodeidx]
    #             for j in range(len(effectivechild)-1):
    #                 cnidx1 = gnodeidx[effectivechild[j]]
    #                 cnidx2 = gnodeidx[effectivechild[j+1]]
    #                 constraints.append(dict(axis='y', left=cnidx1,
    #                                         right=cnidx2, gap=7, equality='true'))
    with open('../data/retweet-2011/topic_graph.json', 'w') as f:
        json.dump(dict(nodes=nodes, links=links, constraints=constraints), f)


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

    def pruning(leaflist):
        resnode = []
        for idx, leafnode in enumerate(leaflist):
            templist = leafnode.val.split(',')
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
        # print('result: ', [d.val for d in resnode])
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
    wordscount = 1000
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
        # check weather stop
        tempset = set()
        for words in list(leafptns.keys()):
            tempset = tempset.union(set(words.split(',')))
        if len(tempset) > wordscount:
            break
    # pruning
    leaflist = []
    for word, node in value_node.items():
        if not node.child:  # is leaf
            leaflist.append(node)
    resnode = pruning(leaflist)
    topic_graph(root, resnode, value_node)


def main():
    timestep, movestep = 5, 1
    count = 5 * timestep
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
        kwscore = kw_weight.most_common(count)
        state_kwscore[current.strftime('%Y-%m-%d')] = kwscore
        # corpus
        temp = set(map(tuple, corpuslist))
        state_corpus[current.strftime('%Y-%m-%d')] = list(map(list, temp))
        current += datetime.timedelta(days=movestep)
    # for state, kwscore in state_kwscore.items():
    #     corpus = state_corpus[state]
    #     sentree(corpus, kwscore)
    #     break
    state = '2011-09-26'
    corpus, kwscore = state_corpus[state], state_kwscore[state]
    sentree(corpus, kwscore)
    with open('./test1.json', 'w') as f:
        json.dump({'test': corpus}, f)


if __name__ == '__main__':
    main()
