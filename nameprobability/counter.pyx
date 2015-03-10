import Levenshtein as edist
import numpy as np
cimport numpy as np
from collections import defaultdict

def _editCounts(name_samp):
    # to compute probability of edit operations use a subsample of names
    cdef int i
    cdef int j
    cdef int k
    cdef int total_edits = 0
    cdef int len1
    cdef int lene
    edit_count = defaultdict(int)
    p = len(name_samp)
    len1 = p
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

def _ngramCount(name_list, ngram_len):
    cdef int i
    cdef int start
    ngram_count = defaultdict(int)
    for i in range(len(name_list)):
        if len(name_list[i]) > ngram_len - 1:
            for start in range(len(name_list[i]) - (ngram_len-1)):
                ngram_count[name_list[i][start:(start + ngram_len)]] += 1
                ngram_count[name_list[i][start:((start + ngram_len)-1)]] += 1
            ngram_count[name_list[i][(start + 1):(start + ngram_len)]] += 1
    return ngram_count

cpdef dict _probName(str name, int ngram_len, ngram_count, float smoothing,
                     dict memoize):
    cdef float log_prob = 0.0
    cdef float numer
    cdef float denom
    cdef int start
    for start in range(len(name) - (ngram_len - 1)):
        numer = ngram_count[name[start:(start + ngram_len)]] + smoothing
        denom = ngram_count[name[start:(start + ngram_len)-1]] + smoothing
        log_prob += np.log(numer / denom)
    memoize[name] = np.exp(log_prob)
    return memoize


cpdef dict _condProbName(str name1, str name2, edit_count, float total_edits,
                         float smoothing, dict cp_memoize):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        cdef dict temp_count = {}
        cdef tuple e
        cdef float holder = 0.0
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

cpdef list _probSamePerson(str name1, str name2, float pop_size, edit_count,
                           float total_edits, float smoothing, int ngram_len,
                           ngram_count, dict memoize, dict cp_memoize,
                           dict psp_memoize):
    # computes the probability that the two names belong to the same person.
    cdef float p1, p2, p2given1
    if (name1, name2) not in cp_memoize:
        cp_memoize = _condProbName(name1, name2, edit_count, total_edits, smoothing, cp_memoize)
    if name1 not in memoize:
        memoize = _probName(name1, ngram_len, ngram_count, smoothing, memoize)
    if name2 not in memoize:
        memoize = _probName(name2, ngram_len, ngram_count, smoothing, memoize)
    p1 = memoize[name1]
    p2 = memoize[name2]
    p2given1 = cp_memoize[name1, name2]
    psp_memoize[(name1, name2)] = (p1 * p2given1) / ((pop_size - 1.0) * p1 * p2 + p1 * p2given1)
    return [psp_memoize, cp_memoize, memoize]