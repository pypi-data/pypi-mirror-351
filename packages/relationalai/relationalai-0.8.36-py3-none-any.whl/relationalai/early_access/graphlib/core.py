"""
Core functionality for the graphlib package.
"""
from typing import Optional

from relationalai.early_access.builder import Concept, Relationship
from relationalai.early_access.builder import Integer#, Float
from relationalai.early_access.builder import where, define, count

class Graph():
    def __init__(self,
            *,
            directed: bool,
            weighted: bool,
            aggregator: Optional[str] = None,
        ):
        assert isinstance(directed, bool), "The `directed` argument must be a boolean."
        assert isinstance(weighted, bool), "The `weighted` argument must be a boolean."
        self.directed = directed
        self.weighted = weighted

        assert isinstance(aggregator, type(None)), "Weight aggregation not yet supported."
        # TODO: In the hopefully not-too-distant future, this argument will
        #   allow the user to specify whether and how to aggregate weights
        #   for multi-edges that exist at the user interface (Edge) level
        #   to construct the internal edge/weight list representation.
        #   The `str` type is just a placeholder; it should be something else.

        # Introduce Node and Edge concepts.
        Node = Concept("Node")
        Edge = Concept("Edge")
        Edge.src = Relationship("{edge:Edge} has source {src:Node}")
        Edge.dst = Relationship("{edge:Edge} has destination {dst:Node}")
        Edge.weight = Relationship("{edge:Edge} has weight {weight:Float}")
        self.Node = Node
        self.Edge = Edge

        # TODO: Require that each Edge has an Edge.src.
        # TODO: Require that each Edge has an Edge.dst.
        # TODO: If weighted, require that each Edge has an Edge.weight.
        # TODO: If not weighted, require that each Edge does not have an Edge.weight.

        # TODO: Suppose that type checking should in future restrict `src` and
        #   `dst` to be `Node`s, but at the moment we may need a require for that.
        # TODO: Suppose that type checking should in future restrict `weight` to be
        #   `Float`s, but at the moment we may need a require for that.

        # TODO: Transform Node and Edge into underlying edge-/weight-list representation.
        # NOTE: Operate under the assumption that `Node` contains all
        #   possible nodes, i.e. we can use the `Node` Concept directly as
        #   the node list. Has the additional benefit of allowing relationships
        #   (for which it makes sense) to be properties of `Node` rather than standalone.
        self._define_edge_relationships()
 
        self._define_num_nodes_relationship()
        self._define_num_edges_relationship()

        self._define_neighbor_relationships()
        self._define_count_neighbor_relationships()
        self._define_common_neighbor_relationship()
        self._define_count_common_neighbor_relationship()

        self._define_degree_relationships()


    def _define_edge_relationships(self):
        """
        Define the self._edge and self._weight relationships,
        consuming the Edge concept's `src`, `dst`, and `weight` relationships.
        """
        self._edge = Relationship("{src:Node} has edge to {dst:Node}")
        self._weight = Relationship("{src:Node} has edge to {dst:Node} with weight {weight:Float}")

        Edge = self.Edge
        if self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._edge(Edge.src, Edge.dst)
            )
        elif self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._edge(Edge.src, Edge.dst)
            )
        elif not self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._weight(Edge.dst, Edge.src, Edge.weight),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )
        elif not self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._weight(Edge.dst, Edge.src, 1.0),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )

    def _define_num_nodes_relationship(self):
        """Define the self.num_nodes relationship."""
        self.num_nodes = Relationship("The graph has {num_nodes:Integer} nodes")
        define(self.num_nodes(count(self.Node) | 0))

    def _define_num_edges_relationship(self):
        """Define the self.num_edges relationship."""
        self.num_edges = Relationship("The graph has {num_edges:Integer} edges")

        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            define(self.num_edges(count(src, dst, self._edge(src, dst)) | 0))
        elif not self.directed:
            define(self.num_edges(count(src, dst, self._edge(src, dst), src <= dst) | 0))
            # TODO: Generates an UnresolvedOverload warning from the typer.
            #   Should be sorted out by improvements in the typer (to allow
            #   comparisons between instances of concepts).


    def _define_neighbor_relationships(self):
        """Define the self.[in,out]neighbor relationships."""
        self.neighbor = Relationship("{src:Node} has neighbor {dst:Node}")
        self.inneighbor = Relationship("{dst:Node} has inneighbor {src:Node}")
        self.outneighbor = Relationship("{src:Node} has outneighbor {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._edge(src, dst)).define(self.neighbor(src, dst), self.neighbor(dst, src))
        where(self._edge(dst, src)).define(self.inneighbor(src, dst))
        where(self._edge(src, dst)).define(self.outneighbor(src, dst))
        # Note that these definitions happen to work for both
        # directed and undirected graphs due to `edge` containing
        # each edge's symmetric partner in the undirected case.

    def _define_count_neighbor_relationships(self):
        """
        Define the self.count_[in,out]neighbor relationships.
        Note that these relationships differ from corresponding
        [in,out]degree relationships in that they yield empty
        rather than zero absent [in,out]neighbors.
        Primarily for internal consumption.
        """
        self.count_neighbor = Relationship("{src:Node} has neighbor count {count:Integer}")
        self.count_inneighbor = Relationship("{dst:Node} has inneighbor count {count:Integer}")
        self.count_outneighbor = Relationship("{src:Node} has outneighbor count {count:Integer}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self.neighbor(src, dst)).define(self.count_neighbor(src, count(dst).per(src)))
        where(self.inneighbor(dst, src)).define(self.count_inneighbor(dst, count(src).per(dst)))
        where(self.outneighbor(src, dst)).define(self.count_outneighbor(src, count(dst).per(src)))

    def _define_common_neighbor_relationship(self):
        """Define the self.common_neighbor relationship."""
        self.common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor {node_c:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self.neighbor(node_a, node_c), self.neighbor(node_b, node_c)).define(self.common_neighbor(node_a, node_b, node_c))

    def _define_count_common_neighbor_relationship(self):
        """Define the self.count_common_neighbor relationship."""
        self.count_common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor count {count:Integer}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self.common_neighbor(node_a, node_b, node_c)).define(self.count_common_neighbor(node_a, node_b, count(node_c).per(node_a, node_b)))


    def _define_degree_relationships(self):
        """Define the self.[in,out]degree relationships."""
        self.degree = Relationship("{node:Node} has degree {count:Integer}")
        self.indegree = Relationship("{node:Node} has indegree {count:Integer}")
        self.outdegree = Relationship("{node:Node} has outdegree {count:Integer}")

        incount, outcount = Integer.ref(), Integer.ref()

        where(
            _indegree := where(self.count_inneighbor(self.Node, incount)).select(incount),
        ).define(self.indegree(self.Node, _indegree | 0))

        where(
            _outdegree := where(self.count_outneighbor(self.Node, outcount)).select(outcount),
        ).define(self.outdegree(self.Node, _outdegree | 0))

        if self.directed:
            where(
                _indegree := where(self.indegree(self.Node, incount)).select(incount),
                _outdegree := where(self.outdegree(self.Node, outcount)).select(outcount),
            ).define(self.degree(self.Node, (_indegree | 0) + (_outdegree | 0)))
        elif not self.directed:
            neighcount = Integer.ref()
            where(
                _degree := where(self.count_neighbor(self.Node, neighcount)).select(neighcount),
            ).define(self.degree(self.Node, _degree | 0))
