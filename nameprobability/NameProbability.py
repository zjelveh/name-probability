import numpy as np
import os
from collections import defaultdict
import Levenshtein as edist
from name_cleaver import IndividualNameCleaver as inc
import cPickle


class NameMatcher():
    def __init__(self, name_list = None, ngram_len = 5, smoothing = .001,
                 standardize = False, unique = True, useSS = True):
        self.smoothing = smoothing
        self.ngram_count = defaultdict(int)
        self.edit_count = defaultdict(int)
        self.ngram_len = ngram_len
        self.total_edits = 0
        self.pop_size = 0
        if useSS:
            with open('/Users/zubin/board-colors/name-probability/nameprobability/data/ss_data.pickle','rb') as ss_data: 
##            with open(os.path.join(os.path.dirname(__file__), 'data/ss_data.pickle')) as ss_data:
                print 'Loading Social Security Data'
                self.ngram_count, self.edit_count = cPickle.load(ss_data)
                self.pop_size = 24e6
                self.total_edits += sum(self.edit_count.itervalues())
                print 'Done'
        if name_list:
            self.name_list = np.array(name_list)
            if standardize:
                self.standardizeNames(self.name_list)
            if unique:
                self.name_list = np.unique(self.name_list)
            
            # crude measure of population size
            self.pop_size += self.name_list.shape[0]
            self.ngramCount(self.name_list)
            self.editCounts(self.name_list)
            self.total_edits += sum(self.edit_count.values())

    def standardize(self, name):
        return inc(name).parse(safe=True).name_str().lower()

    def standardizeNames(self, name_list):
        for i, name in enumerate(name_list):
            parsed_name = inc(name).parse(safe=True)
            if parsed_name != '':
                name_list[i] = parsed_name.name_str().lower()
        return name_list

    def ngramCount(self, name_list):
        for c, name in enumerate(name_list):            
            if c%10000==0:
                print c
            if len(name) > self.ngram_len - 1:
                for start in range(len(name)-(self.ngram_len-1)):
                    self.ngram_count[name[start:(start+self.ngram_len)]] += 1
                    self.ngram_count[name[start:((start+self.ngram_len)-1)]] += 1
                self.ngram_count[name[(start+1):(start+self.ngram_len)]] += 1

    def updateCounts(self,name_list,standardize = False):
        name_list = np.array(name_list)
        if standardize:
            name_list = self.standardizeNames(name_list)
        name_list = np.unique(name_list)
        self.pop_size += name_list.shape[0]
        self.ngramCount(name_list)
        self.editCounts(name_list)

    def editCounts(self,name_list):
        # to compute probability of edit operations
        # use a subsample of names
        if len(name_list) < 50000:
            name_samp = name_list
        else:
            name_samp = name_list[np.random.randint(0, len(self.name_list),
                                                         50000)].tolist()
        for i, name1 in enumerate(name_samp):
            for j in range(i + 1, len(name_samp)):
                if i < j:
                    edits = edist.editops(name1, name_samp[j])
                    self.total_edits += len(edits)
                    for e in edits:
                        self.edit_count[e] += 1

    def probName(self, name):
        name = self.standardize(name)
        # compute the probability of name based on the training data
        if len(name) < self.ngram_len:
            print 'name too short'
            return 0
        else:
            log_prob = 0
            for start in range(len(name) - (self.ngram_len - 1)):
                numer = self.ngram_count[name[start:(start+self.ngram_len)]] + self.smoothing
                denom = self.ngram_count[name[start:(start+self.ngram_len)-1]] + self.smoothing
                if denom == 0:
                    return 0
                else:
                    log_prob += np.log(numer) - np.log(denom)
            return np.exp(log_prob)
                    
    def condProbName(self, name1, name2):
        # computes the conditional probability of arriving at name1
        # by performing a series of operation on name2.
        name1, name2 = map(self.standardize, [name1, name2])
        edits = edist.editops(name1, name2)
        log_cnd_prob = 0
        for e in edits:
            log_cnd_prob += np.log(self.edit_count[e] + self.smoothing)
        return np.exp(log_cnd_prob-len(edits) *
                      np.log(self.total_edits+self.smoothing*len(edits)))
    
    def probSamePerson(self, name1, name2):
        name1, name2 = map(self.standardize, [name1, name2])
        # computes the probability that the two names belong to the same person. 
        if len(name1) < self.ngram_len or len(name2) < self.ngram_len:
            print 'Both names should be at least', self.ngram_len, ' characters \
                long'
            return np.nan
        p2given1 = self.condProbName(name1, name2)
        p1 = self.probName(name1)
        p2 = self.probName(name2)
        result = (p1 * p2given1)/((self.pop_size - 1) * p1 * p2 + p1 * p2given1)
        return result
    
    def probUnique(self, name):
        name = self.standardize(name)
        # compute the probability that a name is unique in the data
        return 1. / ((self.pop_size - 1) * self.probName(name) + 1)

    def surprisal(self, name):
        name = self.standardize(name)
        return -np.log2(self.probUnique(name))

    def loadRandom(self):
        list_of_names = file(os.path.abspath('data/sample_names.csv')).read().split('\n')
        self.updateCounts(list_of_names)
        del list_of_names

if __name__ == '__main__':
    pass
