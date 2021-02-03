# CAP Theorem Proof
FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK
- Suppose the system is partitioned in two parts, G1 and G2: no communication happens between them

- A write happens in G1
- A read happens in G2

- The result of the write is not accessible from G2, so one of these happens:
  - The system returns an error (we lose availability)
  - The system returns old data (we lose consistency)
  - The system doesn’t reply (we lose partition tolerance)


## The Not-So-Obvious Consequences
- When creating a distributed system, you have to choose a tradeoff:
  - Either (part of) your system will be offline until the network partition is resolved
  - Or you will have to live with inconsistent and stale data
- In the rest of the course, we'll dive in work that explores this tradeoff. Distributed systems are very often about tradeoffs!

<div style="text-align: center; font-size:8px;">(1. Introduction)</div>