"""
Module for geometry parser agents
"""

from sc_kpm import ScModule
from .geometry_sequence_parser_agent import GeometrySequenceParserAgent


class GeometryParserModule(ScModule):
    def __init__(self):
        super().__init__(
            GeometrySequenceParserAgent()
        )