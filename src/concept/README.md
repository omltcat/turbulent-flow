# Notes and Proof of Concept
## Notations
| Symbol | Explanation |
|--------|---------|
| $\mathbf{x}$ | Position vector in $[x, y, z]$<br> **Bold** font means vector|
| $\mathbf{x}^k$ | Position of eddy $k$-th <br> Superscript $k$ means eddy specific|

## Fluctuation and Shape Function
Current shape function used by Nikita in MATLAB code:

$$
q(d^k) = 3.6276e^{-0.5\pi(d^k)^2}
$$

He has he own reasoning for the number 3.6276. We can document this with his work. Since the program allows user-defined shape function, this can be one of them.

The shape function should be used to plug into velocity fluctuation function in the form of:

$$
\mathbf{u}' = \sum_{k=1}^Nq(d^k)\mathbf{r}^k\times\boldsymbol{\alpha}^k
$$

For spherical eddy:

$$
\mathbf{r}^k = \frac{\mathbf{x}-\mathbf{x}^k}{\sigma^k}
$$

### To be implemented:
Non-spherical eddy has two length-scales: radial $\sigma^k_r$ and axial $\sigma^k_a$. These are local to the eddy orientation. A gamma $\gamma$ value determine how "tall" or "fat" an eddy is. 

$$
\begin{align*}
\sigma^k_r &= \gamma^{-1/3}\sigma^k\\
\sigma^k_a &= \gamma^{2/3}\sigma^k\\
\end{align*}
$$

In Nikita's code, when all eddies are pointing up (0, 0, 1) initially, this is handles as:

$$
d^k = \sqrt{\frac{(x-x^k)^2}{\sigma^k_r}+\frac{(y-y^k)^2}{\sigma^k_r}+\frac{(z-z^k_3)^2}{\sigma^k_a}}
$$

Maybe we can use a transformation matrix to rotate everything to upright, find $\mathbf{r}^k$ and $d^k$, then rotate back to the original orientation.

<!-- Potentially, if we want to implement non-spherical eddy, we may be able to do the following:
$$
\begin{align*}
\mathbf{r} &=
\begin{bmatrix}
\frac{\mathbf{x}_1-\mathbf{x}^k_1}{\sigma^k_r}\\
\frac{\mathbf{x}_2-\mathbf{x}^k_2}{\sigma^k_r}\\
\frac{\mathbf{x}_3-\mathbf{x}^k_3}{\sigma^k_a}
\end{bmatrix}
\end{align*}
$$

Where $\mathbf{x}_3$ is the z-component (scalar) of the a position. $\sigma^k_r$ and $\sigma^k_a$ are the radial and axial length-scale . -->