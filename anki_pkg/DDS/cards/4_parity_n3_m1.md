# N=3, M=1: Parity
FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK
- I split my data in 2 blocks B0
 and B1
  - E.g., N=2 blocks of 50GB each
- I create a parity redundant block BR
  - BR = B0 XOR B1
- If I lose one of the blocks Bi, I can recover it as
  - Bi = BR XOR B(1-i)
  - This is because x XOR (x XOR y) = y
- Redundancy: 1.5
  - E.g., for 100GB, I need 150GB storage
  - Only 100GB to recover all the original data


<div style="text-align: center; font-size:8px;">(4. Erasure Coding)</div>
