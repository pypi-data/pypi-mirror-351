"""Dependency resolution for SQLFlow pipelines."""

import logging
from typing import Dict, List, Optional, Set

from sqlflow.core.errors import CircularDependencyError

logger = logging.getLogger(__name__)


class DependencyResolver:
    """Resolves dependencies between pipeline files."""

    def __init__(self):
        """Initialize a DependencyResolver."""
        self.dependencies: Dict[str, List[str]] = {}
        self.visited: Set[str] = set()
        self.temp_visited: Set[str] = set()
        self.execution_order: List[str] = []
        self.last_resolved_order: Optional[List[str]] = None
        logger.debug("DependencyResolver initialized with empty state")

    def add_dependency(self, pipeline: str, depends_on: str) -> None:
        """Add a dependency between pipelines.

        Args:
        ----
            pipeline: Pipeline that depends on another
            depends_on: Pipeline that is depended on

        """
        if pipeline not in self.dependencies:
            self.dependencies[pipeline] = []
        self.dependencies[pipeline].append(depends_on)
        logger.debug("Added dependency: %s depends on %s", pipeline, depends_on)
        logger.debug("Current dependencies: %s", self.dependencies)

    def extract_dependencies(self, pipeline_path: str) -> List[str]:
        """Extract dependencies from a pipeline file.

        Args:
        ----
            pipeline_path: Path to the pipeline file

        Returns:
        -------
            List of dependencies

        """
        return []

    def resolve_dependencies(self, start_pipeline: str) -> List[str]:
        """Resolve all dependencies in execution order.

        Args:
        ----
            start_pipeline: Starting pipeline

        Returns:
        -------
            List of pipelines in execution order

        Raises:
        ------
            CircularDependencyError: If a circular dependency is detected

        """
        logger.debug("Resolving dependencies starting from %s", start_pipeline)
        logger.debug("Current dependency graph: %s", self.dependencies)

        self.visited = set()
        self.temp_visited = set()
        self.execution_order = []

        self._visit(start_pipeline)

        self.last_resolved_order = self.execution_order.copy()
        logger.debug("Resolved execution order: %s", self.last_resolved_order)
        return self.execution_order

    def validate(self, pipeline: str) -> None:
        """Validate that a pipeline has no circular dependencies.

        Args:
        ----
            pipeline: Pipeline to validate

        Raises:
        ------
            CircularDependencyError: If a circular dependency is detected

        """
        # This will raise CircularDependencyError if a cycle is detected
        self.resolve_dependencies(pipeline)

    def _visit(self, pipeline: str) -> None:
        """Visit a pipeline and its dependencies.

        Args:
        ----
            pipeline: Pipeline to visit

        Raises:
        ------
            CircularDependencyError: If a circular dependency is detected

        """
        logger.debug("Visiting %s", pipeline)
        logger.debug("temp_visited=%s, visited=%s", self.temp_visited, self.visited)

        if pipeline in self.temp_visited:
            cycle = self._find_cycle(pipeline)
            logger.debug("Cycle detected: %s", cycle)
            raise CircularDependencyError(cycle)

        if pipeline in self.visited:
            logger.debug("Already visited %s, skipping", pipeline)
            return

        self.temp_visited.add(pipeline)

        for dependency in self.dependencies.get(pipeline, []):
            logger.debug("Processing dependency %s of %s", dependency, pipeline)
            self._visit(dependency)

        self.temp_visited.remove(pipeline)
        self.visited.add(pipeline)
        self.execution_order.append(pipeline)
        logger.debug("Added %s to execution order: %s", pipeline, self.execution_order)

    def _find_cycle(self, start: str) -> List[str]:
        """Find a cycle in the dependency graph.

        Args:
        ----
            start: Starting pipeline

        Returns:
        -------
            List of pipelines forming a cycle

        """
        cycle = [start]
        current = start

        while True:
            found_next = False
            for dependency in self.dependencies.get(current, []):
                if dependency in self.temp_visited:
                    cycle.append(dependency)
                    current = dependency
                    found_next = True
                    if dependency == start:
                        return cycle
                    break

            if not found_next:
                return cycle
