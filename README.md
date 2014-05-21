name-probability
================

This repo implements the disambiguation methodology outlined in "<a href="http://planete.inrialpes.fr/papers/high_entropy.pdf">How Unique and Traceable are Usernames?</a>" to link users across platforms. While the paper is interested in usernames, I've typically used it as an additional feature in record linkage tasks -- for example, linking campaign contributions to employment data.

Usage
--------------
```python
>>> import nameprobability.NameProbability as nm
>>> nameprob = nm.NameMatcher()
Loading Social Security Data
Done
>>> nameprob.probSamePerson('smith, john','smith, john r')
>>> 0.0029767677513424344
>>> nameprob.probSamePerson('jelveh, zubin','jelveh, zubin r')
>>> 0.99999999999999689
```



Training Data
--------------

The conditional probabilities are computed using roughly 28 million names from the Social Security Death Master file with the obvious downside that newer names are under-represented.

To-Dos
--------------
In order to compute P(u_1 | u_2) -- the probability person A uses name one given that person A uses name two -- we have to compute the probability of each edit operation that takes us from u_1 to u_2. The current implementation does this empirically by taking a sample of 50,000 names and counting the occurrence of each type of edit operation. This is time consuming and inelegant. Future versions should cache these results and/or come up with a better way of computing the probabilities.
