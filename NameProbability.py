import numpy as np
import os
import re
from collections import defaultdict
import Levenshtein as edist

class NameProbability():
    
    def __init__(self,name_list,ngram_len=5,smoothing=.001):
        # smoothing factor
        self.smoothing = smoothing
        self.name_list = np.array(name_list)
        self.name_list = np.unique(self.name_list)
        self.ngram_count = defaultdict(int)
        self.edit_count = defaultdict(int)
        self.ngram_len = ngram_len
        # crude measure of population size
        self.pop_size = len(self.name_list)
        self.total_edits = 0

        def ngramCount():
            for name in self.name_list:
                if len(name)>4:
                    for start in range(len(name)-(self.ngram_len-1)):
                        self.ngram_count[name[start:(start+self.ngram_len)]] += 1
                        self.ngram_count[name[start:((start+self.ngram_len)-1)]] += 1
                    self.ngram_count[name[(start+1):(start+self.ngram_len)]] += 1

        def editCounts():
            # to compute probability of edit operations
            # use a subsample of names
            if len(self.name_list)<1000:
                name_samp = self.name_list
            else:
                name_samp = self.name_list[np.random.randint(0,len(self.name_list),
                                                             1000)].tolist()
            for name1 in range(len(name_samp)):
                for name2 in range(len(name_samp[name1+1:])):
                    edits = edist.editops(name_samp[name1],
                                          name_samp[name2])
                    self.total_edits += len(edits)
                    for e in edits:
                        self.edit_count[e] += 1
            
        ngramCount()
        editCounts()

    def probName(self,name):
        # compute the probability of name based on the training data
        if len(name) < self.ngram_len:
            print 'name too short'
            return 0
        else:
            log_prob = 0
            for start in range(len(name)-(self.ngram_len-1)):
                numer = self.ngram_count[name[start:(start+self.ngram_len)]]+self.smoothing
                denom = self.ngram_count[name[start:(start+self.ngram_len)-1]]+self.smoothing
                if denom == 0:
                    return 0
                else:
                    log_prob += np.log(numer)-np.log(denom)
            return np.exp(log_prob)
                    
    def condProbName(self,name1,name2):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        edits = edist.editops(name1,name2)
        log_cnd_prob = 0
        for e in edits:
            log_cnd_prob += np.log(self.edit_count[e]+self.smoothing)
        return np.exp(log_cnd_prob-len(edits)*np.log(self.total_edits+self.smoothing*len(edits)))
    
    def probSamePerson(self,name1,name2):
        # computes the probability that the two names belong to the same person. 
        if len(name1) < self.ngram_len or len(name2) < self.ngram_len:
            print 'Both names should be at least', self.ngram_len, ' characters \
                long'
            return np.nan
        p2given1 = self.condProbName(name1,name2)
        p1 = self.probName(name1)
        p2 = self.probName(name2)
        result = (p1 * p2given1)/((self.pop_size-1) * p1 * p2 + p1 * p2given1)
        return result
    
    def probUnique(self,name):
        # compute the probability that a name is unique in the data
        return 1./((self.pop_size-1)*self.probName(name)+1)

    def surprisal(self,name):
        return -np.log2(self.probUnique(name))
        
if __name__ == '__main__':
    list_of_names = file(os.path.abspath('data/sample_names.csv')).read().split('\n')
    name_prob = NameProbability(list_of_names)
    
