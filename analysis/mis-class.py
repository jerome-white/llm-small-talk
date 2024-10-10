import sys
import csv
import logging
import collections as cl
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import Pool, Queue

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def records(fp):
    df = pd.read_csv(fp)
    for ((q, c), g) in df.groupby(['query', 'gt'], sort=False):
        acc = g['pr'].eq(g['gt']).mean()
        ctype = 'query' if c else 'small-talk'
        yield {
            'query': q,
            'ctype': ctype,
            'acc': acc,
        }

if __name__ == '__main__':
    arguments = ArgumentParser()
    arguments.add_argument('--output', type=Path)
    arguments.add_argument('--dump-raw', type=Path)
    arguments.add_argument('--bottom-k', type=int, default=10)
    arguments.add_argument('--without-zero', action='store_true')
    args = arguments.parse_args()

    df = pd.DataFrame.from_records(records(sys.stdin))
    assert df['query'].value_counts().eq(1).all()

    if args.dump_raw is not None:
        df.to_csv(args.dump_raw, index=False)
    if args.without_zero:
        df = df.query('acc > 0')

    df = (df
          .sort_values(by='acc')
          .head(args.bottom_k))

    fig = plt.gcf()
    (w, h) = fig.get_size_inches()
    fig.set_size_inches(w * 2, h)

    sns.barplot(data=df,
                y='query',
                x='acc',
                hue='ctype')
    plt.legend(title='Query type')
    plt.xlabel('Fraction of models correctly classifying')
    plt.ylabel('')
    plt.savefig(args.output, bbox_inches='tight')
