"""
Module for geometry search agents
"""

from sc_kpm import ScModule
from .geometry_search_agent import GeometrySearchAgent
from .geometry_sequence_extractor_agent import GeometrySequenceExtractorAgent
from .geometry_sequence_parser_agent import GeometrySequenceParserAgent


class GeometrySearchModule(ScModule):
    def __init__(self):
        super().__init__(
            GeometrySearchAgent(),
            GeometrySequenceExtractorAgent(),
            GeometrySequenceParserAgent()
        )