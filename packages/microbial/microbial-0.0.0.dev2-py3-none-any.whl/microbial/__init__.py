"""Microbial

Utilities for modeling various microbiological systems.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from . import bacteria, fungi, frameworks, genomics, phylogeny, viruses

from .phylogeny import Phylogeny

from .bacteria import Bacterium
from .fungi import Fungus
from .genomics import Genome, BacterialGenome, FungalGenome, ViralGenome
from .viruses import Virus

from .frameworks import environment, executor, queue, scheduler, simulator
from .frameworks.environment import Environment
from .frameworks.executor import Executor
from .frameworks.queue import Event, Queue, ReplicationEvent
from .frameworks.scheduler import Scheduler
from .frameworks.simulator import Simulator

__all__ = [
    # ─── modules ─────────────────────────────────────────────────────────────
    "bacteria",
    "environment",
    "executor",
    "frameworks",
    "fungi",
    "genomics",
    "phylogeny",
    "scheduler",
    "simulator",
    "queue",
    "viruses",

    # ─── classes ─────────────────────────────────────────────────────────────
    "BacterialGenome",
    "Bacterium",
    "Environment",
    "Event",
    "Executor",
    "FungalGenome",
    "Fungus",
    "Genome",
    "Queue",
    "ReplicationEvent",
    "Scheduler",
    "Simulator",
    "Phylogeny",
    "ViralGenome",
    "Virus"
]
