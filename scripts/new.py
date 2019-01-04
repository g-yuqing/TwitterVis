import json
import collections
import datetime
import sys
sys.setrecursionlimit(100000)


def extract_sentences(corpus, kwlist, thres=100):
    class TreeNode():
        def __init__(self, word, value, corlen):
            self.word = word
            self.value = value
            self.corlen = corlen
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
        2. list of text contain word
        3. list of text not contain word
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

    leaves = {'empty': corpus}  # words: corpus
    value_node = {}
    result = set()

    def sentree(leaves):
        _, count = pruning(result, kwlist)
        if count >= thres:
            return
        else:
            # leaves information
            leafwords = list(leaves.keys())
            leafcorpus = list(leaves.values())
            # find the largest corpus
            lengths = list(map(lambda d: len(d), leafcorpus))
            idx = lengths.index(max(lengths))
            # determine the popword according the length
            popword = leafwords[idx]
            popcorpus = leaves.pop(popword)
            mfword, mflist, eptylist = process_pop(popword, popcorpus)
            if mfword is None:
                return
            # set result: leaves may contain abc & abcd
            # result only contains abcd
            if popword in result:
                result.remove(popword)
            result.add(mfword)
            leaves[mfword] = mflist
            leaves[popword] = eptylist
            # set sentence tree graph
            if popword == 'empty':
                tn = TreeNode(mfword, mfword, len(mflist))
                value_node[mfword] = tn
            else:
                popnode = value_node[popword]
                if popword.split(',') == mfword.split(',')[1:]:
                    curword = mfword.split(',')[0]
                else:
                    curword = mfword.split(',')[-1]
                curnode = TreeNode(curword, mfword, len(mflist))
                value_node[mfword] = curnode
                curnode.parent = popnode
            # recursive
            sentree(leaves)
    # call sentree function
    sentree(leaves)
    resleaves, count = pruning(result, kwlist)
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
