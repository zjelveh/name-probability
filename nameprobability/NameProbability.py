import numpy as np
import os
from collections import defaultdict
import Levenshtein as edist
from name_cleaver import IndividualNameCleaver as indiv, OrganizationNameCleaver as company
import cPickle
from counter import _editCounts, _ngramCount, _probName

class NameMatcher():
    def __init__(self, name_list=None, ngram_len=5, smoothing=.001,
                 standardizeType=None, unique=True, useSS=True, edit_count_max=None):
        '''
        - standardizeType can be set to 'Indiv' or 'Company'
        - edit_count_max is used to limit the number of samples to consider 
        when computing edit operation counts
        '''
        self.smoothing = smoothing
        self.ngram_count = defaultdict(int)
        self.edit_count = defaultdict(int)
        self.ngram_len = ngram_len
        self.pop_size = 0
        self.total_edits = 0
        self.standardizeFunc = None
        self.unique = unique
        self.edit_count_max = edit_count_max
        self.DATA_PATH = os.path.join(os.path.split(__file__)[0], "data")
        self.memoize = {}
        
        if standardizeType == 'Indiv':
                self.standardizeFunc = lambda name: indiv(name).parse(safe=True).name_str().lower()
        if standardizeType == 'Company':
                self.standardizeFunc = lambda name: company(name).parse(safe=True).name.lower()
                
        if useSS:
            with open(os.path.join(self.DATA_PATH, 'ss_data.pkl'),'rb') as ss_data:
                print 'Loading Social Security Data'
                self.ngram_count, self.edit_count = cPickle.load(ss_data)
                self.pop_size = 24e6
                self.total_edits += sum(self.edit_count.itervalues())
                    
        if name_list:
            if not isinstance(name_list, list):
                name_list = list(name_list)
            if standardizeType:
                name_list = [self.standardizeFunc(name) for name in name_list]
            if self.unique:
                name_list = list(set(name_list))

            # crude measure of population size
            self.pop_size += len(name_list)
            self.ngramCount(name_list)
            print "Starting editCounts"
            self.editCounts(name_list)

    def ngramCount(self, name_list):
        ngram_count = _ngramCount(name_list, self.ngram_len)
        for k, v in ngram_count.iteritems():
            self.ngram_count[k] += v
            
    def updateCounts(self, name_list):
        if self.standardizeFunc:
            name_list = [self.standardizeFunc(name) for name in name_list]
        if self.unique:
            name_list = list(set(name_list))
        self.pop_size += len(name_list)
        self.ngramCount(name_list)
        self.editCounts(name_list)
    
    def editCounts(self, name_list):
        # to compute probability of edit operations use a subsample of names
        if self.edit_count_max:
            name_list = np.array(name_list)
            name_samp = name_list[np.random.randint(0, len(name_list), 
                                                    self.edit_count_max)].tolist()
        else:
            name_samp = name_list
        edit_count, total_edits = _editCounts(name_samp)
        self.total_edits += total_edits
        for k, v in edit_count.iteritems():
            self.edit_count[k] += v
                                
    def probName(self, name):
        if self.standardizeFunc:
            name = self.standardizeFunc(name)    
        # compute the probability of name based on the training data
        if len(name) < self.ngram_len:
            return 0
        pn, self.momoize = _probName(name, self.ngram_len, self.ngram_count, self.smoothing, self.memoize)
        return pn

    def condProbName(self, name1, name2):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        temp_count = {}
        for k, v in self.edit_count.iteritems():
            temp_count[k] = v / float(self.total_edits)
        if self.standardizeFunc:
            name1, name2 = map(self.standardizeFunc, [name1, name2])
        edits = edist.editops(name1, name2)
        log_cnd_prob = sum(np.log(temp_count[e] + self.smoothing) for e in edits)
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

    temp = NameProbability.NameMatcher(name_list=['abc company', 'bcd inc'], standardizeType='Company', useSS=False)