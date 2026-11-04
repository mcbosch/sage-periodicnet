# periodicnet

This python package aims to create a tool based in SageMath to work with periodic graphs. Periodic graphs is a mathematical object defined by a graph $G = (V, E)$ where there's a group action acting on $G$. 

This package is in process, feel free to join, share ideas or things that could help you. In Future updates we'll give more information and formal definitions.

## Periodic Graph

A Periodic Graph consists of a graph $G = (V, E)$ toghether with a free  group action of finite generated abelian group $\Gamma = \langle g_1,\ldots, g_n\rangle$ s.t. there's a fundamental domain $H=(D_V, D_E)$ verifying the following conditions:

1. $D_E\subset E(D_V, V)$, i.e. the edges of the fundamental domain have at least one side in $D_V$ but not necessarly both. The edges that have one side in $D_V$ and the other outside, are called bridge edges, and we use the notation $B(H,V)$.
2. $V=\bigcup_{\gamma\in \Gamma}\gamma D_V$  and  $E=\bigcup_{\gamma\in \Gamma}\gamma D_E$, i.e. the action is transitive with the fundamental domain, or the hole graph are copies of the fundamental domain.
3. $\gamma_1\ne\gamma_2\Rightarrow \gamma_1 D_V\cap \gamma_2 D_V = \emptyset$, and analogue for edges. This can be understood as it the fundamental domain is the minimum structure s.t. every action falls outside, but we can recover the hole graph.

An important thing to define on a periodic graph are the indices of the edges. Because the action is free and we have the condition (2) on the fundamental domain, $\forall v\in$, $\exists! \xi(v)\in \Gamma$ and $v_0\in D_V$ s.t. $v=\xi(v)v_0$. This allows us to define the index of an edge as:
$$
ind_H(e):=\xi(\partial_+e)(\xi(\partial_-e))^{-1}\in \Gamma.
$$
Then the indices generates $\Gamma$, and it's a good way to move around copies of the fundamental domain in the graph.