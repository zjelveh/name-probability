import numpy as np
import os
from collections import defaultdict
import Levenshtein as edist
from name_cleaver import IndividualNameCleaver as indiv, OrganizationNameCleaver as company
import cPickle

class NameMatcher():
    def __init__(self, name_list=None, ngram_len=5, smoothing=.001,
                 standardizeType=None, unique=True, useSS=True):
        '''
        standardizeType can be set to 'Indiv' or 'Company'
        '''
        self.smoothing = smoothing
        self.ngram_count = defaultdict(int)
        self.edit_count = defaultdict(int)
        self.ngram_len = ngram_len
        self.pop_size = 0
        self.total_edits = 0
        self.standardizeFunc = None
        self.DATA_PATH = os.path.join(os.path.split(__file__)[0], "data")
        
        if standardizeType == 'Indiv':
                self.standardizeFunc = lambda name: indiv(name).parse(safe=True).name_str().lower()
        if standardizeType == 'Company':
                self.standardizeFunc = lambda name: company(name).parse(safe=True).name_str().lower()
                
        if useSS:
            with open(os.path.join(self.DATA_PATH, 'ss_data.pkl'),'rb') as ss_data:
                print 'Loading Social Security Data'
                self.ngram_count, self.edit_count = cPickle.load(ss_data)
                self.pop_size = 24e6
                self.total_edits += sum(self.edit_count.itervalues())
                for k, v in self.edit_count.iteritems():
                    self.edit_count[k] = v / float(self.total_edits)
                    
        if name_list:
            if not isinstance(name_list, list):
                name_list = list(name_list)
            self.name_list = [self.standardizeFunc(self.name) for name in name_list]
            self.name_list = np.array(name_list)
            if unique:
                self.name_list = np.unique(self.name_list)

            # crude measure of population size
            self.pop_size += self.name_list.shape[0]
            self.ngramCount(self.name_list)
            print "Starting editCounts"
            self.editCounts(self.name_list)

    def ngramCount(self, name_list):
        for c, name in enumerate(name_list):
            if len(name) > self.ngram_len - 1:
                for start in range(len(name) - (self.ngram_len-1)):
                    self.ngram_count[name[start:(start + self.ngram_len)]] += 1
                    self.ngram_count[name[start:((start + self.ngram_len)-1)]] += 1
                self.ngram_count[name[(start + 1):(start + self.ngram_len)]] += 1

    def updateCounts(self, name_list):
        name_list = np.array(name_list)
        if self.standardizeFunc:
            name_list = [self.standardizeFunc(name) for name in name_list]
        name_list = np.unique(name_list)
        self.pop_size += name_list.shape[0]
        self.ngramCount(name_list)
        self.editCounts(name_list)
    
    def editCounts(self, name_list):
        # to compute probability of edit operations use a subsample of names
        if len(name_list) < 10000:
            name_samp = name_list
        else:
            name_samp = name_list[np.random.randint(0, len(self.name_list), 10000)].tolist()
        for i, name1 in enumerate(name_samp):
            for j in range(i + 1, len(name_samp)):
                if i < j:
                    edits = edist.editops(name1, name_samp[j])
                    self.total_edits += len(edits)
                    for e in edits:
                        self.edit_count[e] += 1

    def probName(self, name):
        if self.standardizeFunc:
            name = self.standardizeFunc(name)    
        # compute the probability of name based on the training data
        if len(name) < self.ngram_len:
            print 'name too short'
            return 0

        log_prob = 0
        for start in range(len(name) - (self.ngram_len - 1)):
            numer = self.ngram_count[name[start:(start + self.ngram_len)]] + self.smoothing
            denom = self.ngram_count[name[start:(start + self.ngram_len)-1]] + self.smoothing
            log_prob += np.log(numer / denom)

        return np.exp(log_prob)

    def condProbName(self, name1, name2):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        if self.standardizeFunc:
            name1, name2 = map(self.standardizeFunc, [name1, name2])
        edits = edist.editops(name1, name2)
        log_cnd_prob = sum(np.log(self.edit_count[e]) for e in edits)
        return np.exp(log_cnd_prob)

    def probSamePerson(self, name1, name2):
        if self.standardizeFunc:
            name1, name2 = map(self.standardizeFunc, [name1, name2])
        # computes the probability that the two names belong to the same person.
        if len(name1) < self.ngram_len or len(name2) < self.ngram_len:
            print 'Both names should be at least', self.ngram_len, ' characters long'
            return np.nan
        p2given1 = self.condProbName(name1, name2)
        p1 = self.probName(name1)
        p2 = self.probName(name2)
        return (p1 * p2given1)/((self.pop_size - 1) * p1 * p2 + p1 * p2given1)

    def probUnique(self, name):
        if self.standardizeFunc:
            name = self.standardizeFunc(name)
        # compute the probability that a name is unique in the data
        return 1. / ((self.pop_size - 1) * self.probName(name) + 1)

    def surprisal(self, name):
        if self.standardizeFunc:
            name = self.standardizeFunc(name)
        return -np.log2(self.probUnique(name))

    def loadRandom(self):
        self.standardizeFunc = lambda name: indiv(name).parse(safe=True).name_str().lower()
        with open(os.path.join(self.DATA_PATH, 'sample_names.csv'), 'rb') as f:
            self.updateCounts(f.read().split('\n'))

if __name__ == '__main__':
    pass