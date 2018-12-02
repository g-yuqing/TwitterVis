import json

for fn in ['A', 'B', 'C', 'D', 'E']:
    with open('/Users/yuqingguan/Documents/TwitterVis/data/retweet-2011/test/'+fn+'/keywords.json', 'r') as f:
        dataset = json.load(f)
    d = sorted(dataset.items(), key=lambda kv: kv[1])[-20:]
    print(fn)
    for i in d[::-1]:
        print(i[0])
    print('======================')
