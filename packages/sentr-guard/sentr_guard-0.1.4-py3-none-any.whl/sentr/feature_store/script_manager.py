"""
Redis Lua script manager for atomic feature store operations.

Handles script loading, caching, and execution for maximum performance.
Performance Polish: Enhanced with unified operations and better error handling.
"""

import logging
import time
from typing import Dict, List, Optional

from .lua_scripts import (
    ENHANCED_BATCH_HINCRBY,
    ENHANCED_ROLLING_WINDOW,
    GET_WINDOW_BUCKETS,
    BULK_WINDOW_OPERATION,
    UNIFIED_HASH_OPERATION,
    # Legacy imports for backward compatibility
    HINCRBY_WITH_TTL,
    HSET_WITH_TTL,
    BATCH_HINCRBY,
    ROLLING_WINDOW_UPDATE,
)

logger = logging.getLogger(__name__)

# Import metrics for RTT tracking
try:
    from infra.metrics import redis_rtt_seconds
except ImportError:
    # Fallback if metrics not available
    class NoOpMetric:
        def labels(self, **kwargs):
            return self

        def observe(self, value):
            pass

    redis_rtt_seconds = NoOpMetric()


class LuaScriptManager:
    """
    Manages Redis Lua scripts for atomic operations.

    Provides high-performance atomic operations that eliminate
    multiple Redis round trips.

    Performance Polish: Added unified operations and enhanced error handling.
    """

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self._script_shas: Dict[str, str] = {}
        self._loaded = False
        self._performance_mode = True  # Use enhanced scripts by default

    async def load_scripts(self) -> None:
        """Load all Lua scripts into Redis and cache their SHAs."""
        if self._loaded:
            return

        # Enhanced scripts for better performance
        enhanced_scripts = {
            "unified_hash_operation": UNIFIED_HASH_OPERATION,
            "enhanced_batch_hincrby": ENHANCED_BATCH_HINCRBY,
            "enhanced_rolling_window": ENHANCED_ROLLING_WINDOW,
            "bulk_window_operation": BULK_WINDOW_OPERATION,
            "get_window_buckets": GET_WINDOW_BUCKETS,
        }

        # Legacy scripts for backward compatibility
        legacy_scripts = {
            "hincrby_with_ttl": HINCRBY_WITH_TTL,
            "hset_with_ttl": HSET_WITH_TTL,
            "batch_hincrby": BATCH_HINCRBY,
            "rolling_window_update": ROLLING_WINDOW_UPDATE,
        }

        # Load enhanced scripts first
        scripts_to_load = enhanced_scripts if self._performance_mode else {}
        scripts_to_load.update(legacy_scripts)

        for name, script in scripts_to_load.items():
            try:
                sha = self.redis_client.script_load(script)
                self._script_shas[name] = sha
                logger.debug(f"Loaded Lua script '{name}': {sha}")
            except Exception as e:
                logger.error(f"Failed to load Lua script '{name}': {e}")
                raise

        self._loaded = True
        logger.info(
            f"Loaded {len(self._script_shas)} Lua scripts for atomic operations"
        )

    def _execute_with_metrics(
        self, script_name: str, sha: str, num_keys: int, *args
    ) -> any:
        """Execute script with performance metrics tracking."""
        start_time = time.perf_counter()
        try:
            result = self.redis_client.evalsha(sha, num_keys, *args)

            # Track successful RTT
            rtt = time.perf_counter() - start_time
            redis_rtt_seconds.labels(script_name=script_name).observe(rtt)

            return result
        except Exception as e:
            # Track failed RTT
            rtt = time.perf_counter() - start_time
            redis_rtt_seconds.labels(script_name=f"{script_name}_error").observe(rtt)
            logger.error(f"Error in {script_name}: {e}")
            raise

    async def atomic_hincrby(
        self, hash_key: str, field: str, amount: int = 1, ttl_seconds: int = 3600
    ) -> int:
        """
        Atomic HINCRBY with TTL in single Redis call.

        Performance Polish: Now uses unified operation script for better performance.

        Args:
            hash_key: Redis hash key
            field: Hash field to increment
            amount: Amount to increment by
            ttl_seconds: TTL to set if hash doesn't have one

        Returns:
            New value after increment
        """
        await self.load_scripts()

        if self._performance_mode and "unified_hash_operation" in self._script_shas:
            # Use enhanced unified script
            result = self._execute_with_metrics(
                "unified_hash_operation",
                self._script_shas["unified_hash_operation"],
                1,  # Number of keys
                hash_key,
                "hincrby",
                field,
                amount,
                ttl_seconds,
            )
        else:
            # Fallback to legacy script
            result = self._execute_with_metrics(
                "hincrby_with_ttl",
                self._script_shas["hincrby_with_ttl"],
                1,
                hash_key,
                field,
                amount,
                ttl_seconds,
            )

        return int(result)

    async def atomic_hset_unique(
        self, hash_key: str, field: str, value: str = "1", ttl_seconds: int = 3600
    ) -> int:
        """
        Atomic HSET with TTL for unique values.

        Performance Polish: Now uses unified operation script.

        Args:
            hash_key: Redis hash key
            field: Hash field to set
            value: Value to set
            ttl_seconds: TTL to set if hash doesn't have one

        Returns:
            1 if new field, 0 if field already existed
        """
        await self.load_scripts()

        if self._performance_mode and "unified_hash_operation" in self._script_shas:
            # Use enhanced unified script
            result = self._execute_with_metrics(
                "unified_hash_operation",
                self._script_shas["unified_hash_operation"],
                1,
                hash_key,
                "hset",
                field,
                value,
                ttl_seconds,
            )
        else:
            # Fallback to legacy script
            result = self._execute_with_metrics(
                "hset_with_ttl",
                self._script_shas["hset_with_ttl"],
                1,
                hash_key,
                field,
                value,
                ttl_seconds,
            )

        return int(result)

    async def get_window_buckets(
        self, hash_key: str, bucket_fields: List[str]
    ) -> List[Optional[int]]:
        """
        Get specific bucket values using HMGET (faster than HGETALL).

        Args:
            hash_key: Redis hash key
            bucket_fields: List of bucket field names to retrieve

        Returns:
            List of bucket values (None for missing fields)
        """
        await self.load_scripts()

        if not bucket_fields:
            return []

        result = self._execute_with_metrics(
            "get_window_buckets",
            self._script_shas["get_window_buckets"],
            1,
            hash_key,
            *bucket_fields,
        )

        # Convert Redis response to integers (None for missing fields)
        return [int(val) if val is not None else None for val in result]

    async def enhanced_batch_increment(
        self, hash_key: str, field_amounts: Dict[str, int], ttl_seconds: int = 3600
    ) -> Dict[str, int]:
        """
        Enhanced batch increment multiple fields atomically.

        Performance Polish: Uses improved batch operation with better error handling.

        Args:
            hash_key: Redis hash key
            field_amounts: Dict of field -> amount to increment
            ttl_seconds: TTL to set if hash doesn't have one

        Returns:
            Dict of field -> new value after increment
        """
        await self.load_scripts()

        if not field_amounts:
            return {}

        # Flatten field_amounts to [field1, amount1, field2, amount2, ...]
        args = []
        for field, amount in field_amounts.items():
            args.extend([field, amount])
        args.append(ttl_seconds)

        script_name = (
            "enhanced_batch_hincrby" if self._performance_mode else "batch_hincrby"
        )
        results = self._execute_with_metrics(
            script_name,
            self._script_shas[script_name],
            1,
            hash_key,
            *args,
        )

        # Map results back to field names
        field_names = list(field_amounts.keys())
        return {field_names[i]: int(results[i]) for i in range(len(results))}

    async def enhanced_rolling_window_update(
        self,
        hash_key: str,
        current_time: float,
        decay_factor: float = 0.9,
        window_size: float = 60.0,
        ttl_seconds: int = 3600,
    ) -> float:
        """
        Update rolling window with configurable parameters.

        Performance Polish: Enhanced with configurable decay factor and window size.

        Args:
            hash_key: Redis hash key
            current_time: Current timestamp
            decay_factor: Exponential decay factor (0.0 to 1.0)
            window_size: Window size in seconds
            ttl_seconds: TTL for the hash

        Returns:
            New rolling value after update
        """
        await self.load_scripts()

        script_name = (
            "enhanced_rolling_window"
            if self._performance_mode
            else "rolling_window_update"
        )

        if self._performance_mode:
            result = self._execute_with_metrics(
                script_name,
                self._script_shas[script_name],
                1,
                hash_key,
                current_time,
                decay_factor,
                window_size,
                ttl_seconds,
            )
        else:
            # Legacy call
            result = self._execute_with_metrics(
                script_name,
                self._script_shas[script_name],
                1,
                hash_key,
                current_time,
                decay_factor,
                ttl_seconds,
            )

        return float(result)

    async def bulk_window_operation(
        self,
        hash_key: str,
        operation_type: str,
        current_time: float,
        window_size: int = 60,
        ttl_seconds: int = 3600,
        **kwargs,
    ) -> List[int]:
        """
        High-performance bulk operation for sliding windows.

        Performance Polish: New unified operation for better throughput.

        Args:
            hash_key: Redis hash key
            operation_type: "increment" or "unique"
            current_time: Current timestamp
            window_size: Window size in seconds
            ttl_seconds: TTL for the hash
            **kwargs: Additional operation-specific parameters

        Returns:
            List of operation results
        """
        await self.load_scripts()

        if (
            not self._performance_mode
            or "bulk_window_operation" not in self._script_shas
        ):
            raise NotImplementedError("Bulk operations require performance mode")

        args = [operation_type, current_time, window_size, ttl_seconds]

        if operation_type == "increment":
            amount = kwargs.get("amount", 1)
            args.append(amount)
        elif operation_type == "unique":
            unique_value = kwargs.get("unique_value", "")
            args.append(unique_value)
        else:
            raise ValueError(f"Invalid operation type: {operation_type}")

        results = self._execute_with_metrics(
            "bulk_window_operation",
            self._script_shas["bulk_window_operation"],
            1,
            hash_key,
            *args,
        )

        return [int(r) for r in results]

    # Legacy method aliases for backward compatibility
    async def batch_increment(
        self, hash_key: str, field_amounts: Dict[str, int], ttl_seconds: int = 3600
    ) -> Dict[str, int]:
        """Legacy alias for enhanced_batch_increment."""
        return await self.enhanced_batch_increment(hash_key, field_amounts, ttl_seconds)

    async def rolling_window_update(
        self, hash_key: str, current_time: float, ttl_seconds: int = 3600
    ) -> float:
        """Legacy alias for enhanced_rolling_window_update."""
        return await self.enhanced_rolling_window_update(
            hash_key, current_time, ttl_seconds=ttl_seconds
        )


# Global script manager instance cache for performance
_script_managers: Dict[int, LuaScriptManager] = {}


def get_script_manager(redis_client) -> LuaScriptManager:
    """
    Get or create a script manager for the given Redis client.

    Performance Polish: Caches managers to avoid repeated script loading.

    Args:
        redis_client: Redis client instance

    Returns:
        LuaScriptManager instance
    """
    client_id = id(redis_client)

    if client_id not in _script_managers:
        _script_managers[client_id] = LuaScriptManager(redis_client)

    return _script_managers[client_id]
