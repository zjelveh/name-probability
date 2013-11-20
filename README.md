name-probability
================

This repo implements the disambiguation methodology outlined in "<a href="http://planete.inrialpes.fr/papers/high_entropy.pdf">How Unique and Traceable are Usernames?</a>" to link users across platforms. 

Example output:

```python
>>> name_prob.probSamePerson('smith, john','smith, john r')
>>> 0.0029767677513424344
>>> name_prob.probSamePerson('jelveh, zubin','jelveh, zubin r')
>>> 0.99999999999999689
```

Of course, the above results depend on the training data. The data directory contains a list of 250,000 random names generated from Census and Social Security data. I'd highly recommend using a domain-specific list.

