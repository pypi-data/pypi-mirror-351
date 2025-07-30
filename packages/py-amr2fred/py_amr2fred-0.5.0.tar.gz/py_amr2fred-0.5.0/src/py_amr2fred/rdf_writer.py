import re

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import NamespaceManager

from .glossary import Glossary
from .node import Node


class RdfWriter:
    """
    A class for converting a hierarchical structure of nodes into an RDF graph using `rdflib`.

    This class manages RDF graph construction, namespace binding, serialization, and visibility handling.
    """
    def __init__(self):
        self.queue = []
        self.graph: Graph | None = None
        self.not_visible_graph: Graph | None = None
        self.namespace_manager = NamespaceManager(Graph(), bind_namespaces="rdflib")
        self.new_graph()

        for i, name_space in enumerate(Glossary.NAMESPACE):
            self.namespace_manager.bind(Glossary.PREFIX[i][:-1], name_space)

    def new_graph(self):
        """
        Creates a new RDF graph and a secondary graph for non-visible triples.
        Also, assigns the namespace manager to both graphs.
        """
        self.graph = Graph()
        self.not_visible_graph = Graph()
        self.graph.namespace_manager = self.namespace_manager
        self.not_visible_graph.namespace_manager = self.namespace_manager

    def get_prefixes(self) -> list[str]:
        """
        Retrieves the list of namespace prefixes bound to the RDF graph.

        :return: A list of tuples containing (prefix, namespace URI).
        :rtype: list[str]
        """
        names = []
        for prefix, namespace in self.graph.namespaces():
            names.append([prefix, namespace])
        return names

    def to_rdf(self, root: Node):
        """
        Converts a hierarchical structure of `Node` objects into an RDF graph.

        :param root: The root node of the structure to be transformed into RDF.
        :type root: Node
        """
        self.new_graph()
        if not isinstance(root, Node):
            return
        self.queue = []
        self.queue.append(root)
        while len(self.queue) > 0:
            n = self.queue.pop(0)
            for node in n.node_list:
                self.queue.append(node)
            uri = self.get_uri(n.var)

            for n1 in n.node_list:
                if not uri.startswith("http"):
                    break
                s = URIRef(uri)
                if n1.relation != Glossary.TOP:
                    p = URIRef(self.get_uri(n1.relation))
                    if re.match(Glossary.NN_INTEGER2, n1.var):
                        o = Literal(n1.var, datatype=Glossary.NN_INTEGER_NS)
                    elif re.match(Glossary.DATE_SCHEMA, n1.var):
                        o = Literal(n1.var, datatype=Glossary.DATE_SCHEMA_NS)
                    elif re.match(Glossary.TIME_SCHEMA, n1.var):
                        o = Literal(n1.var, datatype=Glossary.TIME_SCHEMA2_NS)
                    elif (n1.relation == Glossary.RDFS_LABEL
                          or re.match(Glossary.NN_RATIONAL, n1.var)
                          or Glossary.AMR_RELATION_BEGIN not in n1.var):
                        o = Literal(n1.var, datatype=Glossary.STRING_SCHEMA_NS)
                    else:
                        o = URIRef(self.get_uri(n1.var))
                    self.graph.add((s, p, o))
                    if not n.visibility or not n1.visibility:
                        self.not_visible_graph.add((s, p, o))

    def serialize(self, rdf_format: Glossary.RdflibMode) -> str:
        """
        Serializes the RDF graph into the specified format.

        :param rdf_format: The format in which to serialize the RDF graph.
        :type rdf_format: Glossary.RdflibMode
        :return: The serialized RDF data as a string.
        :rtype: str
        """
        if rdf_format.value in Glossary.RDF_MODE:
            return self.graph.serialize(format=rdf_format.value)

    @staticmethod
    def get_uri(var: str) -> str:
        """
        Resolves a variable name into a full URI based on predefined namespaces.

        :param var: The variable name to be converted into a URI.
        :type var: str
        :return: The corresponding URI.
        :rtype: str
        """
        if Glossary.NON_LITERAL not in var:
            return Glossary.FRED_NS + var
        pref = var.split(Glossary.NON_LITERAL)[0] + Glossary.NON_LITERAL
        name = var.split(Glossary.NON_LITERAL)[1]
        if pref in Glossary.PREFIX:
            return Glossary.NAMESPACE[Glossary.PREFIX.index(pref)] + name
        if pref == "_:":
            return var
        return Glossary.FRED_NS + var
