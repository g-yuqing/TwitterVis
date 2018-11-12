import json
import collections
import datetime
import sys
sys.setrecursionlimit(100000)


def generate_graph(leaves):
    class TopicNode():
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

    wordnode, idx = {}, 0
    # generate initial graph
    for sentence in leaves:
        wordlist = sentence.split(',')
        for i in range(len(wordlist)-1):
            word1, word2 = wordlist[i], wordlist[i+1]
            if word1 not in wordnode:
                node1 = TopicNode(idx, word1)
                wordnode[word1] = node1
                idx += 1
            if word2 not in wordnode:
                node2 = TopicNode(idx, word2)
                wordnode[word2] = node2
                idx += 1
            node1, node2 = wordnode[word1], wordnode[word2]
            node2.add_income(node1)
            node1.add_outcome(node2)

    # process circle
    # reconstruct topic tree
    def process_cycle(wordnode):
        stack = {}
        visited = {}
        result = []
        for word, node in wordnode.items():
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
        for word, node in wordnode.items():
            dfs(node)
        # remove cycle
        for res in result:
            node1, node2 = res[0], res[1]
            node2.pop_income(node1)
            node1.pop_outcome(node2)
    process_cycle(wordnode)

    # set word level
    def set_level(wordnode):
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
        for word, node in wordnode.items():
            dfs(node)
    set_level(wordnode)

    # generate topic graph
    nodes, links = [], []
    xoffsets = []
    for _, node in wordnode.items():
        xoffsets.append(dict(node=node.nid, offset=(node.level-1)*15))
        nodes.append(dict(id=node.nid, word=node.value, color='#777'))
        for outnode in node.dump_incomes():
            links.append(dict(source=node.nid, target=outnode.nid))
    constraints = [
        dict(type='alignment', axis='x', offsets=xoffsets)]
    graph = dict(nodes=nodes, links=links, constraints=constraints)
    with open('../data/retweet-2011/topic_graph.json', 'w') as f:
        json.dump(graph, f)


def extract_sentences(corpus, kwscore):
    class TreeNode():
        def __init__(self, value, word, depth):
            self.value = value
            self.word = word
            self.depth = depth
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
            # print('empty: ', reswords, len(rescorpus), len(resempty))
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
                # print('non-empty: ', reswords, len(rescorpus), len(resempty))
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

    kwlist = list(map(lambda d: d[0], kwscore))
    print('keywords: ', kwlist)
    leaves = {'empty': corpus}  # words: corpus
    thres = 200
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
            # if len(popcorpus) == 0:
            #     print('popcorpus is empty')
            #     print(popword)
            #     return
            # # find the most frequent word pairs
            # mfword, mflist, eptylist = process_pop(popword, popcorpus)
            # if mfword is None:
            #     print('mfword is none')
            #     print(mfword)
            #     return

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
            sentree(leaves)
    sentree(leaves)
    resleaves, count = pruning(result, kwlist)
    print(count)
    for sentence in resleaves:
        print(sentence)
    return resleaves


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
    # extract sentences
    leaves = extract_sentences(corpus, kwscore)
    # generate graph
    generate_graph(leaves)


if __name__ == '__main__':
    main()
