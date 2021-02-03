# M=1, Any N: Parity
FRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACKFRONTBACK
- I split my data in K=N-1 blocks of the same size
  - E.g., N=6, 100GB: 5 blocks B0, …, BK-1 of 20GB each
- I create a parity redundant block BR
  - BR = B1 XOR B2 XOR … XOR BN
- If I lose one of the blocks Bi, I can recover it as
  - Bi = B1 XOR B2 … XOR Bi-1 XOR Bi+1… XOR BK-1 XOR BR
  - This is because x XOR (x XOR y) = y
  - Here y=B1 XOR B2 … XOR Bi-1 XOR Bi+1… XOR BK-1 XOR BR
- Redundancy: N/K=N/(N-1)
  - Say N=6, 100GB: redundancy 6/5=1.2, I need 120GB
  - Again, only 100GB to recover all original data


<div style="text-align: center; font-size:8px;">(4. Erasure Coding)</div>
