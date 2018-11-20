import json
import collections
import MeCab
import unicodedata
import random
import pandas as pd


def csv2json():
    '''
    convert csv of tweet-2011 to json file
    '''
    def is_japanese(string):
        for ch in string:
            name = unicodedata.name(ch)
            if "CJK UNIFIED" in name \
                    or "HIRAGANA" in name or "KATAKANA" in name:
                return True
        return False
    mt = MeCab.Tagger()
    mt.parse('')
    filepath = '../data/retweet-2011/retweet-2011.csv'
    dataset = pd.read_csv(filepath).values  # tid,date,infl,user,text,count
    tid_info = collections.defaultdict(dict)
    print(len(dataset))
    for data in dataset:
        # for json dump
        tid, author, text, count = str(data[0]), int(data[2]),\
             str(data[4]), int(data[5])
        if tid in tid_info:
            continue
        tid_info[tid]['author'] = author
        tid_info[tid]['count'] = count
        tid_info[tid]['rtd'] = collections.defaultdict(int)
        tid_info[tid]['text'] = text
        tid_info[tid]['words'] = []
        if text[:2] == 'RT':
            pos = text.find(':')
            text = text[pos+1:]
        node = mt.parseToNode(text)
        while node:
            fields = node.feature.split(',')
            # and fields[2] == '一般'
            if fields[0] == '名詞' and\
                    fields[1] != '代名詞' and fields[1] != '連体化' and\
                    fields[1] != '非自立':
                word = node.surface
                if is_japanese(word):
                    tid_info[tid]['words'].append(word)
            else:
                pass
            node = node.next
    for data in dataset:
        tid, date = str(data[0]), str(data[1])
        tid_info[tid]['rtd'][date] += 1
    print(len(tid_info))
    # return tweet_id
    with open('../data/retweet-2011/tweet_info.json', 'w') as f:
        json.dump(tid_info, f)


def sample_dataset():
    with open('../data/retweet-2011/tweet_info.json', 'r') as f:
        dataset = json.load(f)
    print(len(dataset))
    keys = list(dataset.keys())
    keys = random.sample(keys, 100000)
    sample = {}
    for key in keys:
        sample[key] = dataset[key]
    with open('../data/retweet-2011/sample.json', 'w') as f:
        json.dump(sample, f)


if __name__ == '__main__':
    # csv2json()
    sample_dataset()
