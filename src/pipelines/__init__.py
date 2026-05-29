"""Universal Translation Hub — Pipeline modules"""
from .base import BasePipeline, PipelineResult
from .game import GamePipeline
from .manga import MangaPipeline
from .film import FilmPipeline

__all__ = ["BasePipeline", "PipelineResult", "GamePipeline", "MangaPipeline", "FilmPipeline"]
