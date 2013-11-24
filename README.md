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

Background
-----------

The probability of a name is computed as follows. Given a string of length n, the joint probabilty of the characters in the string can be broken down like this:

![equation](http://www.sciweavers.org/upload/Tex2Img_1385225204/eqn.png)

To make things a little easier, a Markovian assumption is made so that the n-th character in the string is only dependent on the k prior characters:

![equation](http://www.sciweavers.org/upload/Tex2Img_1385225220/eqn.png)

Training Data
--------------

The conditional probabilities are computed using rouhgly 28 million names from the Social Security Death Master file.
