"""Embedding worker for processing chunks into embeddings."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from qdrant_loader.core.embedding.embedding_service import EmbeddingService
from qdrant_loader.core.monitoring import prometheus_metrics
from qdrant_loader.utils.logging import LoggingConfig

from .base_worker import BaseWorker

logger = LoggingConfig.get_logger(__name__)


class EmbeddingWorker(BaseWorker):
    """Handles chunk embedding with batching."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        max_workers: int = 4,
        queue_size: int = 1000,
        shutdown_event: asyncio.Event | None = None,
    ):
        super().__init__(max_workers, queue_size)
        self.embedding_service = embedding_service
        self.shutdown_event = shutdown_event or asyncio.Event()

    async def process(self, chunks: list[Any]) -> list[tuple[Any, list[float]]]:
        """Process a batch of chunks into embeddings.

        Args:
            chunks: List of chunks to embed

        Returns:
            List of (chunk, embedding) tuples
        """
        if not chunks:
            return []

        try:
            logger.debug(f"EmbeddingWorker processing batch of {len(chunks)} items")

            with prometheus_metrics.EMBEDDING_DURATION.time():
                # Add timeout to prevent hanging and check for shutdown
                embeddings = await asyncio.wait_for(
                    self.embedding_service.get_embeddings([c.content for c in chunks]),
                    timeout=120.0,  # 2 minute timeout
                )

                # Check for shutdown before returning
                if self.shutdown_event.is_set():
                    logger.debug("EmbeddingWorker skipping result due to shutdown")
                    return []

                result = list(zip(chunks, embeddings, strict=False))
                logger.debug(f"EmbeddingWorker completed batch of {len(chunks)} items")
                return result

        except TimeoutError:
            logger.error("EmbeddingWorker timed out processing batch")
            raise
        except Exception as e:
            logger.error(f"EmbeddingWorker error processing batch: {e}")
            raise

    async def process_chunks(
        self, chunks: AsyncIterator[Any]
    ) -> AsyncIterator[tuple[Any, list[float]]]:
        """Process chunks into embeddings.

        Args:
            chunks: AsyncIterator of chunks to process

        Yields:
            (chunk, embedding) tuples
        """
        logger.debug("EmbeddingWorker started")
        batch_size = self.embedding_service.batch_size
        batch = []

        try:
            async for chunk in chunks:
                if self.shutdown_event.is_set():
                    logger.debug("EmbeddingWorker exiting due to shutdown")
                    break

                batch.append(chunk)

                # Process batch when it reaches the desired size
                if len(batch) >= batch_size:
                    try:
                        results = await self.process(batch)
                        for result in results:
                            yield result
                    except Exception as e:
                        logger.error(f"EmbeddingWorker batch processing failed: {e}")
                        # Mark chunks as failed but continue processing
                        for chunk in batch:
                            logger.error(f"Embedding failed for chunk {chunk.id}: {e}")

                    batch = []

            # Process any remaining chunks in the final batch
            if batch and not self.shutdown_event.is_set():
                try:
                    results = await self.process(batch)
                    for result in results:
                        yield result
                except Exception as e:
                    logger.error(f"EmbeddingWorker final batch processing failed: {e}")
                    for chunk in batch:
                        logger.error(f"Embedding failed for chunk {chunk.id}: {e}")

        except asyncio.CancelledError:
            logger.debug("EmbeddingWorker cancelled")
            raise
        finally:
            logger.debug("EmbeddingWorker exited")
