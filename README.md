name-probability
================

This repo implements the disambiguation methodology outlined in "<a href="http://planete.inrialpes.fr/papers/high_entropy.pdf">How Unique and Traceable are Usernames?</a>" to link users across platforms. While the paper is interested in usernames, I've typically used it as an additional feature in record linkage tasks -- for example, linking campaign contributions to employment data.

Usage
--------------
```python
>>> from NameProbability import NameMatcher
>>> name_list_src = '~/NameProbability/data/sample_names.csv'
>>> nameprob = NameMatcher(name_list_location=name_list_src, last_comma_first=True)
>>> nameprob.probSamePerson('john smith', 'john r smith')
>>> 0.008288431595531668
>>> nameprob.probSamePerson('zubin jelveh', 'zubin r jelveh')
>>> 0.999999999999234634
```



Installation
--------------
```
python setup.py install
```

<!-- Training Data
--------------

The conditional probabilities are computed using roughly 28 million names from the Social Security Death Master file with the obvious downside that newer names are under-represented. -->

Edit Operation Probability
--------------
In order to compute P(u_1 | u_2) -- the probability person A uses name one given that person A uses name two -- we have to compute the probability of each edit operation that takes us from u_1 to u_2. The current implementation does this empirically by taking a sample of 50,000 names and counting the occurrence of each type of edit operation. Room for improvement here.
