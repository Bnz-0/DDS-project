# What is this?
![mm1_model](mm1_model.png)
FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK
This is called M/M/1 (Kendall notation) queue

- Jobs arrive in a **memoryless** fashion: no matter what happened until now, the probability of seeing a new job in a time unit **never changes**
- Jobs are served in a **memoryless** fashion: the probability of a job finishing does not depend on how long it’s been served, or anything else
- Just **one** server

Real systems are not like this, but some of the
insight does apply to real-world use cases
- The memoryless property makes it much easier to
derive closed-form formulas
- (Some of) the insight we get will be useful
- We will compare & contrast with simulations
- And we can verify whether simulations are correct too

<div style="text-align: center; font-size:8px;">(1. Introduction)</div>