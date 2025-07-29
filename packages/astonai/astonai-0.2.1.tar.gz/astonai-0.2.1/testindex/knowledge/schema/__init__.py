"""
Knowledge Graph schema module.

This module provides schema definitions for nodes and relationships in the Knowledge Graph.
"""

__version__ = "0.1.0"

from testindex.knowledge.schema.base import Node, Relationship, SchemaItem
from testindex.knowledge.schema.nodes import (
    TestNode,
    ImplementationNode,
    ModuleNode,
    FixtureNode,
)
from testindex.knowledge.schema.relationships import (
    TestsRelationship,
    UsesFixtureRelationship,
    CallsRelationship,
    ImportsRelationship,
    InheritsFromRelationship,
    CoversPathRelationship,
    ContainsRelationship,
) 