# Any N & M: Parity
FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK
- I encode my data in N blocks, each of size 1/Kth of the original data, where K=N-M
  - E.g., M=2, N=6 -> K=4 -> 6 blocks of size 25GB

- I can decode any K of those blocks to recover my original data
  - E.g., any 4 of the N=6 blocks in the example
  - Once again, I just need any blocks totaling 100GB to recover my original data

- Redundancy: N/(N-M)
  - 1.5 in the example, 150GB total


  <div style="text-align: center; font-size:8px;">(4. Erasure Coding)</div>