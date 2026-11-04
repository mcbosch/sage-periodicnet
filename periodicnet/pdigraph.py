r"""
Periodic graphs.

A periodic graph is encoded by its quotient graph: a finite :class:`DiGraph`
whose vertices are the fundamental domain `D_V` and whose arcs are the edge
representatives `D_E`, each labelled by its index `ind_H(e) \in \Gamma`.
The group `\Gamma` is a finitely generated additive abelian group.

A vertex of the (infinite) periodic graph is a pair ``(v, gamma)`` standing for
`\gamma v` with `v \in D_V`, so `\xi((v, \gamma)) = \gamma`. The action is
`\gamma \cdot (v, \delta) = (v, \gamma + \delta)` and an arc ``(u, v, gamma)``
of the quotient lifts to the edges ``((u, delta), (v, delta + gamma))``.
Bridge edges are the arcs with nonzero index.

EXAMPLES:

The square lattice::

    sage: from periodicnet.pgraph import PGraph
    sage: P = PGraph([(0, 0, (1, 0)), (0, 0, (0, 1))], group=[0, 0])
    sage: P
    Periodic graph on 1 vertex over Additive abelian group isomorphic to Z + Z
    sage: P.periodic_neighbors(P.periodic_vertex(0, (2, 3)))
    [(0, (2, 4)), (0, (3, 3)), (0, (2, 2)), (0, (1, 3))]
    sage: P.lift([(0, 0), (1, 0), (0, 1), (1, 1)])
    Graph on 4 vertices
"""
from sage.graphs.graph import Graph
from sage.graphs.digraph import DiGraph
from sage.graphs.generic_graph import GenericGraph
from sage.groups.abelian_gps.abelian_group import AbelianGroup
from sage.groups.abelian_gps.abelian_group import AbelianGroup_class
from sage.structure.element import parent


class PDiGraph(DiGraph):
    r"""
    Periodic graph given by a Fundamental Domain graph with edge indices as 
    labels.

    INPUT:

    - ``data`` -- anything accepted by :class:`DiGraph`; edge labels are the
      indices (``None`` is the identity). Undirected graphs are oriented as
      their edges are listed.
    - ``group`` -- an additive abelian group or a list of invariants
      (``[0, 0]`` is `\ZZ^2`); taken from ``data`` if it is a :class:`PGraph`.
    - ``boundary`` -- a list of 3-tuples, (u, v, ind)

    The other arguments are the ones of :class:`DiGraph` from SageMath, except that
    ``loops`` and ``multiedges`` default to ``True``, since non trivial quotients
    are going to have loops or multiedges.
    """

    def __init__(self, data=None, group=None, pos=None, loops=None,
                 format=None, weighted=None, data_structure='sparse',
                 vertex_labels=True, name=None, multiedges=None,
                 convert_empty_dict_labels_to_None=None, sparse=True,
                 immutable=False, hash_labels=None):

        # Define the group acting on G
        if group is None and isinstance(data, PGraph):
            group = data.group()
        self._group = group

        # bridges u can define multiedges or self-loops
        loops = True if loops is None else loops
        multiedges = True if multiedges is None else multiedges
        if immutable:
            data_structure, sparse = 'sparse', True

        # Define fundamental graph
        DiGraph.__init__(self, data=data, pos=pos, loops=loops, format=format,
                         weighted=weighted, data_structure=data_structure,
                         vertex_labels=vertex_labels, name=name,
                         multiedges=multiedges,
                         convert_empty_dict_labels_to_None=convert_empty_dict_labels_to_None,
                         sparse=sparse, immutable=False, hash_labels=hash_labels)

        # We check if all the edges indices are defined (as labels)
        raw = []
        for e in self.edge_iterator():
            if isinstance(e[2], dict) and parent(e[2].get('ind', None)) is not self._group:
                raw.append(e)
            elif not isinstance(e[2], dict):
                e[2] = {'label': e[2]}
                raw.append(e)
        if raw:
            self.delete_edges(raw)
            self.add_edges(raw)

        if immutable:
            from sage.graphs.base.static_sparse_backend import StaticSparseBackend
            self._backend = StaticSparseBackend(self, loops=self.allows_loops(),
                                                multiedges=self.allows_multiple_edges())
            self._immutable = True

    def _repr_(self):
        n = self.order()
        s = "Periodic graph on %d vert%s over %s" % (n, "ex" if n == 1 else "ices", self._group)
        return self.name() + ": " + s if self.name() else s


    def _index(self, index):
        r"""
        Coerce ``index`` into the group (``None`` is the identity).
        """
        if self._group is None:
            # e.g. empty copies built internally by Sage
            if not isinstance(parent(index), AbelianGroup_class):
                raise ValueError("the group of the periodic graph is not defined")
            self._group = parent(index)

        return self._group.one() if index is None else self._group(index)

    def add_edge(self, u, v, label=None, index=None):
        dd = {}
        if isinstance(label, dict):
            dd.update(label)
        elif label is not None:
            dd['label'] = label
        
        if 'ind' not in dd:
            dd['ind'] = self._index(index)
        
        ddi = dd.copy()
        ddi['ind'] = dd['ind']**-1

        DiGraph.add_edge(self, u, v, dd)
        DiGraph.add_edge(self, v, u, ddi)

    def add_edges(self, edges, loops=True, add_sym=True):
        def with_index(e):
            u, v, dd = e
            if not isinstance(dd, dict):
                if dd:
                    dd = {'label': dd}
                else:
                    dd = {}

            dd['ind'] = dd.get('ind', self._index(None))
            return u, v, dd
        
        def inv_with_index(e):
            u, v, *dd = e
            if not isinstance(dd, dict):
                dd = {'label': dd}

            dd['ind'] = dd.get('ind', self._index(None))**-1
            return v, u, dd

        DiGraph.add_edges(self, (with_index(e) for e in edges), loops=loops)
        DiGraph.add_edges(self, (inv_with_index(e) for e in edges), loops=loops)

    def set_edge_label(self, u, v, l):
        DiGraph.set_edge_label(self, u, v, self._index(l))

    # Structure

    def group(self):
        r"""
        Return the group `\Gamma` acting on the periodic graph.
        """
        return self._group

    def fundamental_domain(self):
        r"""
        Return `(D_V, D_E)` as vertices and edges of the periodic graph.
        """
        o = self._group.one()
        D_V = [(u, o) for u in self]
        for u, _ in D_V:
            for e in self.outgoing_edge_iterator(u):
                D_E = [((u, 0), (e[1], e[2]['ind']))]
        return (D_V, D_E)

    def internal_edges(self):
        r"""
        Return the arcs of index one (both ends in `D_V`).
        """
        return [e for e in self.edge_iterator() if e[2]['ind'].is_one()]

    def bridge_edges(self):
        r"""
        Return the bridge edges `B(H, V)`, i.e. the arcs of non 1 index.
        """
        return [e for e in self.edge_iterator() if not e[2]['ind'].is_one()]
