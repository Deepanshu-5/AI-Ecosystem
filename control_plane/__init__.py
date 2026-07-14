"""
Control Plane Orchestrator package

Public boundary: exposes a single entry point representing one Control Plane
execution. The implementation depends exclusively on validated subsystem public
interfaces supplied by the caller (dependency injection).

The package intentionally does not construct, configure, or dispose of injected
subsystem interfaces or provider objects. Creation and lifetime management of
those dependencies remain the responsibility of the caller.
"""

from .orchestrator import run_control_plane
from .result import ControlPlaneResult

__all__ = ["run_control_plane", "ControlPlaneResult"]
