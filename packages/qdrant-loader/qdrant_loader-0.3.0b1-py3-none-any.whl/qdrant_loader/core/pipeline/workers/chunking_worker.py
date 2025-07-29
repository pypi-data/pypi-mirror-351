"""Chunking worker for processing documents into chunks."""

import asyncio
import concurrent.futures
from collections.abc import AsyncIterator

import psutil

from qdrant_loader.core.chunking.chunking_service import ChunkingService
from qdrant_loader.core.document import Document
from qdrant_loader.core.monitoring import prometheus_metrics
from qdrant_loader.utils.logging import LoggingConfig

from .base_worker import BaseWorker

logger = LoggingConfig.get_logger(__name__)


class ChunkingWorker(BaseWorker):
    """Handles document chunking with controlled concurrency."""

    def __init__(
        self,
        chunking_service: ChunkingService,
        chunk_executor: concurrent.futures.ThreadPoolExecutor,
        max_workers: int = 10,
        queue_size: int = 1000,
        shutdown_event: asyncio.Event | None = None,
    ):
        super().__init__(max_workers, queue_size)
        self.chunking_service = chunking_service
        self.chunk_executor = chunk_executor
        self.shutdown_event = shutdown_event or asyncio.Event()

    async def process(self, document: Document) -> list:
        """Process a single document into chunks.

        Args:
            document: The document to chunk

        Returns:
            List of chunks
        """
        logger.debug(f"Chunker_worker started for doc {document.id}")

        try:
            # Check for shutdown signal
            if self.shutdown_event.is_set():
                logger.debug(f"Chunker_worker {document.id} exiting due to shutdown")
                return []

            # Update metrics
            prometheus_metrics.CPU_USAGE.set(psutil.cpu_percent())
            prometheus_metrics.MEMORY_USAGE.set(psutil.virtual_memory().percent)

            # Run chunking in a thread pool for true parallelism
            with prometheus_metrics.CHUNKING_DURATION.time():
                # Calculate adaptive timeout based on document size
                adaptive_timeout = self._calculate_adaptive_timeout(document)

                # Log timeout decision for debugging
                logger.debug(
                    f"Adaptive timeout for {document.url}: {adaptive_timeout:.1f}s "
                    f"(size: {len(document.content)} bytes)"
                )

                # Add timeout to prevent hanging on chunking
                chunks = await asyncio.wait_for(
                    asyncio.get_running_loop().run_in_executor(
                        self.chunk_executor,
                        self.chunking_service.chunk_document,
                        document,
                    ),
                    timeout=adaptive_timeout,
                )

                # Check for shutdown before returning chunks
                if self.shutdown_event.is_set():
                    logger.debug(
                        f"Chunker_worker {document.id} exiting due to shutdown after chunking"
                    )
                    return []

                # Add document reference to chunk for later state tracking
                for chunk in chunks:
                    chunk.metadata["parent_document"] = document

                logger.debug(f"Chunked doc {document.id} into {len(chunks)} chunks")
                return chunks

        except asyncio.CancelledError:
            logger.debug(f"Chunker_worker {document.id} cancelled")
            raise
        except TimeoutError:
            logger.error(f"Chunking timed out for doc {document.url}")
            raise
        except Exception as e:
            logger.error(f"Chunking failed for doc {document.url}: {e}")
            raise

    async def process_documents(self, documents: list[Document]) -> AsyncIterator:
        """Process documents into chunks.

        Args:
            documents: List of documents to process

        Yields:
            Chunks from processed documents
        """
        logger.debug("ChunkingWorker started")

        try:
            # Process documents with controlled concurrency
            tasks = [self.process_with_semaphore(doc) for doc in documents]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Yield chunks from successful results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Chunking task failed: {result}")
                    continue

                # result should be a list of chunks
                if (
                    isinstance(result, list) and result
                ):  # Check if result is a list and not empty
                    for chunk in result:
                        if not self.shutdown_event.is_set():
                            yield chunk
                        else:
                            logger.debug("ChunkingWorker exiting due to shutdown")
                            return

        except asyncio.CancelledError:
            logger.debug("ChunkingWorker cancelled")
            raise

    def _calculate_adaptive_timeout(self, document: Document) -> float:
        """Calculate adaptive timeout based on document characteristics.

        Args:
            document: The document to calculate timeout for

        Returns:
            Timeout in seconds
        """
        doc_size = len(document.content)

        # Universal scaling based on document characteristics
        if doc_size < 1_000:  # Very small files (< 1KB)
            base_timeout = 10.0
        elif doc_size < 10_000:  # Small files (< 10KB)
            base_timeout = 20.0
        elif doc_size < 50_000:  # Medium files (10-50KB)
            base_timeout = 60.0
        elif doc_size < 100_000:  # Large files (50-100KB)
            base_timeout = 120.0
        else:  # Very large files (> 100KB)
            base_timeout = 180.0

        # Special handling for HTML files which can have complex structures
        if document.content_type and document.content_type.lower() == "html":
            base_timeout *= 1.5  # Give HTML files 50% more time

        # Additional scaling factors
        size_factor = min(doc_size / 50000, 4.0)  # Up to 4x for very large files

        # Final adaptive timeout
        adaptive_timeout = base_timeout * (1 + size_factor)

        # Cap maximum timeout to prevent indefinite hanging
        return min(adaptive_timeout, 300.0)  # 5 minute maximum
