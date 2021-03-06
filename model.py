#!/usr/bin/env python3

import bisect
import collections
import doctest
import math
import random

A='A'
B='B'
PLAYERS=[A,B]

ACTUAL = .6
HOUSE  = .5

AWARD = 100

def score(pred, prev):
    """
    >>> score(80, 40)
    100
    >>> score(1.414214, 1)
    50
    """
    return round(100 * math.log2(float(pred) / prev))

# https://stackoverflow.com/a/4322940
def weighted_choice(values, weights):
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect(cum_weights, x)
    return values[i]

def norm_scores(scores):
    """
    >>> norm_scores([-3, 10, 2])
    [1, 14, 6]
    >>> norm_scores([10, 20])
    [1, 11]
    """
    minsc = min(scores)
    scores = [s - minsc + 1 for s in scores]
    assert min(scores) == 1
    return scores


def raffle_ev(scores):
    """
    >>> raffle_ev({A:1, B:2}) == {A: 33.33, B: 66.67}
    True
    >>> raffle_ev({A:-10, B:20}) == {A: 3.12, B: 96.88}
    True
    """
    assert all(int(s) == s for s in scores.values())

    players, scores = zip(*scores.items())
    tickets = norm_scores(scores)
    tickets_total = sum(tickets)
    evs = [round(AWARD*float(t)/tickets_total, 2) for t in tickets]
    return dict(zip(players, evs))

def points_ev(scores):
    return scores

def simulate(B_pred, payoff_func):
    scores = {
        A:0,
        B:0,
    }

    yes_scores = {
        A:0,
        B:score(B_pred, HOUSE),
    }

    no_scores = {
        A:0,
        B:score( (1-B_pred), (1-HOUSE) ),
    }

    ev_dollars = collections.defaultdict(float)
    for p, scores in zip([ACTUAL, 1-ACTUAL], [yes_scores, no_scores]):
        payoff_evs = payoff_func(scores)
        for player in PLAYERS:
            ev_dollars[player] += p*payoff_evs[player]
    return ev_dollars[B]

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite())
    return tests

if __name__ == '__main__':
    preds = [pred/100. for pred in range(1,100,1)]
    funcs = [points_ev, raffle_ev]
    results = [[simulate(pred, func)
                for pred in preds]
               for func in funcs]
    maxs = [max(seq) for seq in results]
    for row in range(len(preds)):
        pred = preds[row]
        print(pred, end='')

        maxfuncs = []
        for col in range(len(funcs)):
            if maxs[col] == results[col][row]:
                maxfuncs.append(funcs[col].__name__)

            print(' ', round(results[col][row], 2), end='')

        if len(maxfuncs) > 0:
            print(' <-- max', ' '.join(maxfuncs))
        else:
            print()
