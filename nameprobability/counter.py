import Levenshtein as edist
import numpy as np
from collections import defaultdict
from numba import jit

@jit
def _editCounts(name_samp):
    # to compute probability of edit operations use a subsample of names
    edit_count = defaultdict(int)
    p = len(name_samp)
    total_edits = 0
    for i in range(p):
        for j in range(i + 1, p):
            if i < j:
                edits = edist.editops(name_samp[i], name_samp[j])
                p = len(edits)
                lene = p
                total_edits += len(edits)
                for k in range(lene):
                    edit_count[edits[k]] += 1
    return edit_count, total_edits

@jit
def _ngramCount(name_list, ngram_len):
    ngram_count = defaultdict(int)
    for i in range(len(name_list)):
        if len(name_list[i]) > ngram_len - 1:
            for start in range(len(name_list[i]) - (ngram_len-1)):
                ngram_count[name_list[i][start:(start + ngram_len)]] += 1
                ngram_count[name_list[i][start:((start + ngram_len)-1)]] += 1
            ngram_count[name_list[i][(start + 1):(start + ngram_len)]] += 1
    return ngram_count

@jit
def _probName(name, ngram_len, ngram_count, smoothing, memoize):
    log_prob = 0.0
    for start in range(len(name) - (ngram_len - 1)):
        numer = ngram_count[name[start:(start + ngram_len)]] + smoothing
        denom = ngram_count[name[start:(start + ngram_len)-1]] + smoothing
        log_prob += np.log(numer / denom)
    memoize[name] = np.exp(log_prob)
    return memoize

@jit
def _condProbName(name1, name2, edit_count, total_edits, smoothing, cp_memoize):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        temp_count = {}
        holder = 0.0
        for k, v in edit_count.iteritems():
            temp_count[k] = v / total_edits
        edits = edist.editops(name1, name2)
        for e in edits:
            try:
                holder += np.log(temp_count[e] + smoothing)
            except:
                holder += np.log(smoothing)
        log_cnd_prob = np.sum(holder)
        cp_memoize[(name1, name2)] = np.exp(log_cnd_prob)
        return cp_memoize

@jit
def _probSamePerson(name1, name2, pop_size, edit_count, total_edits, smoothing,
                    ngram_len, ngram_count, memoize, cp_memoize, psp_memoize):
    # computes the probability that the two names belong to the same person.
    if (name1, name2) not in cp_memoize:
        cp_memoize = _condProbName(name1, name2, edit_count, total_edits, smoothing, cp_memoize)
    if name1 not in memoize:
        memoize = _probName(name1, ngram_len, ngram_count, smoothing, memoize)
    if name2 not in memoize:
        memoize = _probName(name2, ngram_len, ngram_count, smoothing, memoize)
    p1 = memoize[name1]
    p2 = memoize[name2]
    p2given1 = cp_memoize[name1, name2]
    try:
        psp_memoize[(name1, name2)] = (p1 * p2given1) / ((pop_size - 1.0) * p1 * p2 + p1 * p2given1)
    except
        psp_memoize[(name1, name2)] = 0.0
    return [psp_memoize, cp_memoize, memoize]