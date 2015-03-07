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
    
cpdef list _probName(str name, int ngram_len, ngram_count, float smoothing, dict memoize):
    cdef float log_prob = 0.0
    cdef float numer
    cdef float denom
    cdef int start
    if name in memoize:
        return [memoize[name], memoize]
    else:
        for start in range(len(name) - (ngram_len - 1)):
            numer = ngram_count[name[start:(start + ngram_len)]] + smoothing
            denom = ngram_count[name[start:(start + ngram_len)-1]] + smoothing
            log_prob += np.log(numer / denom)
        memoize[name] = np.exp(log_prob)
        return [memoize[name], memoize]