from structlog import get_logger
logger = get_logger()

from functools import cached_property
from attrs import define
import networkx as nx

from doc_analytics.collections import DocumentList
from doc_analytics.document import Document


@define
class BaseOrganizer:
    docs: DocumentList

    def __call__(self):
        raise NotImplementedError


@define
class BreadcrumbOrganizer(BaseOrganizer):
    docs: DocumentList

    def __call__(self):
        for d in self.docs:
            if len(d.metadata.breadcrumbs) == 1:
                d.parent = self.overall_root_doc
                continue

            parent_breadcrumbs = d.metadata.breadcrumbs[:-1]
            candidates = self.docs.filter.by_breadcrumbs(parent_breadcrumbs)
            if not candidates:
                logger.warning(
                    'No parent document found',
                    doc_title=d.title,
                    parent_breadcrumb=parent_breadcrumbs
                )
                continue
            if len(candidates) > 1:
                logger.warning(
                    'Expected single document as parent, but found multiple',
                    doc_title=d.title,
                    n_parents=len(candidates),
                    possible_parents=[doc.title for doc in candidates]
                )

            d.parent = candidates[0]

    @cached_property
    def overall_root_doc(self):
        return Document(docId='rootOfRoots', title='RootofRoots', markdown='RootOfRoots')



    def get_level(self, level: int) -> DocumentList:
            docs = DocumentList()
            for node in self.graph.nodes:
                num_ancestors = len(nx.ancestors(self.graph, node))
                if num_ancestors == level:
                    doc = self.docs.filter.by_identifier(node)
                    docs.append(doc)
            return docs
           
    @cached_property
    def maximum_level(self):
        for i in range(99):
            if self.get_level(i) == []:
                return i - 1
            if i == 99:
                raise ValueError(f'more than 99 levels of documents currently not supported to find maximum. Regardless this Error, the graph still works with unknown max levels.')
            
    def get_successors(self, doc: Document) -> DocumentList:
        successors = list(self.graph.successors(doc.identifier))
        if successors:
            successors = self.docs.filter.by_identifiers(*successors)
        return DocumentList(items=successors)

    @cached_property
    def graph(self):
        # Create a directed graph
        G = nx.DiGraph()

        G.add_nodes_from([d.identifier for d in self.docs])

        for doc in self.docs:
            if doc.parent is None:
                continue
            for other_doc in self.docs:
                if other_doc.identifier == doc.parent.identifier:
                    G.add_edge(other_doc.identifier, doc.identifier)

        return G

