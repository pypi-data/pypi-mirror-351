"""
Test Result Storage Manager.

This module provides persistent storage for MCP test results,
extending the ConversationManager pattern from storage.py.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from ..const import CACHE_DIR
from .mcp_tester import TestResult, TestStatus, TestSuite


class TestResultManager:
    """
    Manages test result persistence in SQLite database.

    Extends the ConversationManager pattern for storing and retrieving
    MCP test results with comprehensive querying capabilities.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the Test Result Manager.

        Args:
            db_path: Optional path to database file (defaults to cache directory)
        """
        if db_path is None:
            db_path = CACHE_DIR / "test_results.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def _init_db(self, db) -> None:
        """
        Initialize database schema for test results.

        Args:
            db: The database connection object
        """
        # Test suites table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_suites (
                id TEXT PRIMARY KEY,
                server_name TEXT NOT NULL,
                total_tests INTEGER NOT NULL,
                passed_tests INTEGER NOT NULL,
                failed_tests INTEGER NOT NULL,
                error_tests INTEGER NOT NULL,
                skipped_tests INTEGER NOT NULL,
                overall_confidence REAL NOT NULL,
                execution_time REAL NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Individual test results table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id TEXT PRIMARY KEY,
                suite_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                execution_time REAL NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                error_info TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (suite_id) REFERENCES test_suites (id)
            )
        """
        )

        # Create indexes for better query performance
        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_suites_server_name 
            ON test_suites (server_name)
        """
        )

        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_suites_timestamp 
            ON test_suites (timestamp)
        """
        )

        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_suite_id 
            ON test_results (suite_id)
        """
        )

        await db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_status 
            ON test_results (status)
        """
        )

        await db.commit()

    async def save_test_suite(self, suite: TestSuite) -> str:
        """
        Save a test suite and its results to the database.

        Args:
            suite: TestSuite object to save

        Returns:
            str: The suite ID
        """
        suite_id = uuid.uuid4().hex

        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Save test suite
            await db.execute(
                """
                INSERT INTO test_suites (
                    id, server_name, total_tests, passed_tests, failed_tests,
                    error_tests, skipped_tests, overall_confidence, execution_time,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    suite_id,
                    suite.server_name,
                    suite.total_tests,
                    suite.passed_tests,
                    suite.failed_tests,
                    suite.error_tests,
                    suite.skipped_tests,
                    suite.overall_confidence,
                    suite.execution_time,
                    suite.timestamp.isoformat(),
                ),
            )

            # Save individual test results
            for result in suite.results:
                result_id = uuid.uuid4().hex
                await db.execute(
                    """
                    INSERT INTO test_results (
                        id, suite_id, test_name, status, confidence_score,
                        execution_time, message, details, error_info, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result_id,
                        suite_id,
                        result.test_name,
                        result.status.value,
                        result.confidence_score,
                        result.execution_time,
                        result.message,
                        json.dumps(result.details) if result.details else None,
                        result.error_info,
                        result.timestamp.isoformat(),
                    ),
                )

            await db.commit()

        return suite_id

    async def get_test_suite(self, suite_id: str) -> Optional[TestSuite]:
        """
        Retrieve a test suite by ID.

        Args:
            suite_id: The suite ID to retrieve

        Returns:
            Optional[TestSuite]: The test suite if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Get suite data
            async with db.execute(
                """
                SELECT server_name, total_tests, passed_tests, failed_tests,
                       error_tests, skipped_tests, overall_confidence, 
                       execution_time, timestamp
                FROM test_suites WHERE id = ?
            """,
                (suite_id,),
            ) as cursor:
                suite_row = await cursor.fetchone()

            if not suite_row:
                return None

            # Get test results
            async with db.execute(
                """
                SELECT test_name, status, confidence_score, execution_time,
                       message, details, error_info, timestamp
                FROM test_results WHERE suite_id = ?
                ORDER BY timestamp
            """,
                (suite_id,),
            ) as cursor:
                result_rows = await cursor.fetchall()

            # Reconstruct test results
            results = []
            for row in result_rows:
                (
                    test_name,
                    status,
                    confidence_score,
                    execution_time,
                    message,
                    details_json,
                    error_info,
                    timestamp,
                ) = row

                details = json.loads(details_json) if details_json else {}

                result = TestResult(
                    test_name=test_name,
                    status=TestStatus(status),
                    confidence_score=confidence_score,
                    execution_time=execution_time,
                    message=message,
                    details=details,
                    timestamp=datetime.fromisoformat(timestamp),
                    error_info=error_info,
                )
                results.append(result)

            # Reconstruct test suite
            (
                server_name,
                total_tests,
                passed_tests,
                failed_tests,
                error_tests,
                skipped_tests,
                overall_confidence,
                execution_time,
                timestamp,
            ) = suite_row

            suite = TestSuite(
                server_name=server_name,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                error_tests=error_tests,
                skipped_tests=skipped_tests,
                overall_confidence=overall_confidence,
                execution_time=execution_time,
                results=results,
                timestamp=datetime.fromisoformat(timestamp),
            )

            return suite

    async def get_latest_test_suites(
        self, server_name: Optional[str] = None, limit: int = 10
    ) -> List[TestSuite]:
        """
        Get the latest test suites, optionally filtered by server name.

        Args:
            server_name: Optional server name filter
            limit: Maximum number of suites to return

        Returns:
            List[TestSuite]: List of test suites ordered by timestamp (newest first)
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Build query
            if server_name:
                query = """
                    SELECT id FROM test_suites 
                    WHERE server_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """
                params = (server_name, limit)
            else:
                query = """
                    SELECT id FROM test_suites 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """
                params = (limit,)

            # Get suite IDs
            async with db.execute(query, params) as cursor:
                suite_ids = [row[0] for row in await cursor.fetchall()]

            # Retrieve full suites
            suites = []
            for suite_id in suite_ids:
                suite = await self.get_test_suite(suite_id)
                if suite:
                    suites.append(suite)

            return suites

    async def get_test_statistics(
        self, server_name: Optional[str] = None, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get test statistics for analysis.

        Args:
            server_name: Optional server name filter
            days: Number of days to include in statistics

        Returns:
            Dict[str, Any]: Statistics including success rates, confidence trends, etc.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Calculate date threshold
            threshold_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            threshold_date = threshold_date.replace(
                day=threshold_date.day - days
            )
            threshold_str = threshold_date.isoformat()

            # Build base query conditions
            if server_name:
                server_condition = "AND ts.server_name = ?"
                params = [threshold_str, server_name]
            else:
                server_condition = ""
                params = [threshold_str]

            # Get overall statistics
            async with db.execute(
                f"""
                SELECT 
                    COUNT(*) as total_suites,
                    AVG(overall_confidence) as avg_confidence,
                    AVG(execution_time) as avg_execution_time,
                    SUM(passed_tests) as total_passed,
                    SUM(failed_tests) as total_failed,
                    SUM(error_tests) as total_errors,
                    SUM(total_tests) as total_tests
                FROM test_suites ts
                WHERE ts.timestamp >= ? {server_condition}
            """,
                params,
            ) as cursor:
                stats_row = await cursor.fetchone()

            if not stats_row or stats_row[0] == 0:
                return {
                    "total_suites": 0,
                    "success_rate": 0.0,
                    "average_confidence": 0.0,
                    "average_execution_time": 0.0,
                    "test_distribution": {
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                    },
                    "server_breakdown": {},
                }

            (
                total_suites,
                avg_confidence,
                avg_execution_time,
                total_passed,
                total_failed,
                total_errors,
                total_tests,
            ) = stats_row

            # Calculate success rate
            success_rate = (
                (total_passed / total_tests) if total_tests > 0 else 0.0
            )

            # Get server breakdown if not filtering by server
            server_breakdown = {}
            if not server_name:
                async with db.execute(
                    """
                    SELECT 
                        server_name,
                        COUNT(*) as suite_count,
                        AVG(overall_confidence) as avg_confidence,
                        SUM(passed_tests) as passed,
                        SUM(total_tests) as total
                    FROM test_suites
                    WHERE timestamp >= ?
                    GROUP BY server_name
                """,
                    [threshold_str],
                ) as cursor:
                    server_rows = await cursor.fetchall()

                for row in server_rows:
                    (
                        server,
                        suite_count,
                        server_confidence,
                        server_passed,
                        server_total,
                    ) = row
                    server_success_rate = (
                        (server_passed / server_total)
                        if server_total > 0
                        else 0.0
                    )
                    server_breakdown[server] = {
                        "suite_count": suite_count,
                        "success_rate": server_success_rate,
                        "average_confidence": server_confidence or 0.0,
                    }

            return {
                "total_suites": total_suites,
                "success_rate": success_rate,
                "average_confidence": avg_confidence or 0.0,
                "average_execution_time": avg_execution_time or 0.0,
                "test_distribution": {
                    "passed": total_passed,
                    "failed": total_failed,
                    "errors": total_errors,
                },
                "server_breakdown": server_breakdown,
            }

    async def cleanup_old_results(self, days_to_keep: int = 90) -> int:
        """
        Clean up old test results to manage database size.

        Args:
            days_to_keep: Number of days of results to keep

        Returns:
            int: Number of test suites deleted
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Calculate cutoff date
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(
                day=cutoff_date.day - days_to_keep
            )
            cutoff_str = cutoff_date.isoformat()

            # Get suite IDs to delete
            async with db.execute(
                """
                SELECT id FROM test_suites WHERE timestamp < ?
            """,
                (cutoff_str,),
            ) as cursor:
                suite_ids = [row[0] for row in await cursor.fetchall()]

            if not suite_ids:
                return 0

            # Delete test results first (foreign key constraint)
            placeholders = ",".join("?" * len(suite_ids))
            await db.execute(
                f"""
                DELETE FROM test_results WHERE suite_id IN ({placeholders})
            """,
                suite_ids,
            )

            # Delete test suites
            await db.execute(
                f"""
                DELETE FROM test_suites WHERE id IN ({placeholders})
            """,
                suite_ids,
            )

            await db.commit()

            return len(suite_ids)
