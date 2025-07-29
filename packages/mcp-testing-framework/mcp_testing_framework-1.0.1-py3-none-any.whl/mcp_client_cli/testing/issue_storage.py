"""
Issue Tracking Storage System for MCP Server Issues.

This module extends the existing storage patterns to provide persistent tracking
of issues, remediation attempts, and health metrics following the ConversationManager
pattern from the existing codebase.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from ..const import DATA_DIR
from .issue_detector import HealthMetrics, Issue, IssueSeverity, IssueType
from .remediation import RemediationResult, RemediationStatus


class IssueTrackingManager:
    """
    Issue Tracking Storage Manager.

    This class extends the existing storage patterns to provide persistent
    tracking of issues, remediation attempts, and health metrics for MCP servers.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the issue tracking manager.

        Args:
            db_path: Optional custom database path
        """
        if db_path is None:
            db_path = DATA_DIR / "issue_tracking.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def _init_db(self, db) -> None:
        """Initialize database schema for issue tracking."""
        # Issues table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id TEXT PRIMARY KEY,
                issue_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                server_name TEXT NOT NULL,
                test_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                error_message TEXT,
                stack_trace TEXT,
                context TEXT,
                suggested_remediation TEXT,
                related_issues TEXT,
                status TEXT DEFAULT 'open',
                resolved_at TEXT,
                resolution_notes TEXT
            )
        """
        )

        # Remediation results table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS remediation_results (
                id TEXT PRIMARY KEY,
                action_id TEXT NOT NULL,
                issue_id TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                execution_time REAL NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                error_info TEXT,
                follow_up_actions TEXT,
                FOREIGN KEY (issue_id) REFERENCES issues (id)
            )
        """
        )

        # Health metrics table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS health_metrics (
                id TEXT PRIMARY KEY,
                server_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                connection_success_rate REAL NOT NULL,
                tool_execution_success_rate REAL NOT NULL,
                average_response_time REAL NOT NULL,
                error_count INTEGER NOT NULL,
                warning_count INTEGER NOT NULL,
                uptime_percentage REAL NOT NULL,
                last_successful_connection TEXT,
                consecutive_failures INTEGER NOT NULL
            )
        """
        )

        # Issue patterns table for learning
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS issue_patterns (
                id TEXT PRIMARY KEY,
                pattern_signature TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                common_remediation TEXT
            )
        """
        )

        # Create indexes for performance
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_server_name ON issues (server_name)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_timestamp ON issues (timestamp)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_type ON issues (issue_type)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_remediation_issue_id ON remediation_results (issue_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_health_metrics_server ON health_metrics (server_name)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_health_metrics_timestamp ON health_metrics (timestamp)"
        )

        await db.commit()

    async def save_issue(self, issue: Issue) -> None:
        """
        Save an issue to the database.

        Args:
            issue: Issue to save
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            await db.execute(
                """
                INSERT OR REPLACE INTO issues (
                    id, issue_type, severity, confidence_score, title, description,
                    server_name, test_name, timestamp, error_message, stack_trace,
                    context, suggested_remediation, related_issues
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    issue.issue_id,
                    issue.issue_type.value,
                    issue.severity.value,
                    issue.confidence_score,
                    issue.title,
                    issue.description,
                    issue.server_name,
                    issue.test_name,
                    issue.timestamp.isoformat(),
                    issue.error_message,
                    issue.stack_trace,
                    json.dumps(issue.context),
                    json.dumps(issue.suggested_remediation),
                    json.dumps(issue.related_issues),
                ),
            )

            await db.commit()

    async def save_remediation_result(self, result: RemediationResult) -> None:
        """
        Save a remediation result to the database.

        Args:
            result: Remediation result to save
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            result_id = str(uuid.uuid4())

            await db.execute(
                """
                INSERT INTO remediation_results (
                    id, action_id, issue_id, status, confidence_score, execution_time,
                    message, timestamp, details, error_info, follow_up_actions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result_id,
                    result.action_id,
                    result.issue_id,
                    result.status.value,
                    result.confidence_score,
                    result.execution_time,
                    result.message,
                    result.timestamp.isoformat(),
                    json.dumps(result.details),
                    result.error_info,
                    json.dumps(result.follow_up_actions),
                ),
            )

            await db.commit()

    async def save_health_metrics(self, metrics: HealthMetrics) -> None:
        """
        Save health metrics to the database.

        Args:
            metrics: Health metrics to save
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            metrics_id = str(uuid.uuid4())

            await db.execute(
                """
                INSERT INTO health_metrics (
                    id, server_name, timestamp, connection_success_rate,
                    tool_execution_success_rate, average_response_time, error_count,
                    warning_count, uptime_percentage, last_successful_connection,
                    consecutive_failures
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics_id,
                    metrics.server_name,
                    metrics.timestamp.isoformat(),
                    metrics.connection_success_rate,
                    metrics.tool_execution_success_rate,
                    metrics.average_response_time,
                    metrics.error_count,
                    metrics.warning_count,
                    metrics.uptime_percentage,
                    (
                        metrics.last_successful_connection.isoformat()
                        if metrics.last_successful_connection
                        else None
                    ),
                    metrics.consecutive_failures,
                ),
            )

            await db.commit()

    async def get_issues(
        self,
        server_name: Optional[str] = None,
        issue_type: Optional[IssueType] = None,
        severity: Optional[IssueSeverity] = None,
        status: str = "open",
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Issue]:
        """
        Retrieve issues from the database with filtering.

        Args:
            server_name: Filter by server name
            issue_type: Filter by issue type
            severity: Filter by severity
            status: Filter by status (open, resolved)
            since: Filter by timestamp
            limit: Maximum number of results

        Returns:
            List[Issue]: Filtered issues
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            query = "SELECT * FROM issues WHERE 1=1"
            params = []

            if server_name:
                query += " AND server_name = ?"
                params.append(server_name)

            if issue_type:
                query += " AND issue_type = ?"
                params.append(issue_type.value)

            if severity:
                query += " AND severity = ?"
                params.append(severity.value)

            if status:
                query += " AND status = ?"
                params.append(status)

            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()

            issues = []
            for row in rows:
                issue = Issue(
                    issue_id=row[0],
                    issue_type=IssueType(row[1]),
                    severity=IssueSeverity(row[2]),
                    confidence_score=row[3],
                    title=row[4],
                    description=row[5],
                    server_name=row[6],
                    test_name=row[7],
                    timestamp=datetime.fromisoformat(row[8]),
                    error_message=row[9],
                    stack_trace=row[10],
                    context=json.loads(row[11]) if row[11] else {},
                    suggested_remediation=(
                        json.loads(row[12]) if row[12] else []
                    ),
                    related_issues=json.loads(row[13]) if row[13] else [],
                )
                issues.append(issue)

            return issues

    async def get_remediation_results(
        self,
        issue_id: Optional[str] = None,
        status: Optional[RemediationStatus] = None,
        limit: int = 100,
    ) -> List[RemediationResult]:
        """
        Retrieve remediation results from the database.

        Args:
            issue_id: Filter by issue ID
            status: Filter by remediation status
            limit: Maximum number of results

        Returns:
            List[RemediationResult]: Filtered remediation results
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            query = "SELECT * FROM remediation_results WHERE 1=1"
            params = []

            if issue_id:
                query += " AND issue_id = ?"
                params.append(issue_id)

            if status:
                query += " AND status = ?"
                params.append(status.value)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()

            results = []
            for row in rows:
                result = RemediationResult(
                    action_id=row[1],
                    issue_id=row[2],
                    status=RemediationStatus(row[3]),
                    confidence_score=row[4],
                    execution_time=row[5],
                    message=row[6],
                    timestamp=datetime.fromisoformat(row[7]),
                    details=json.loads(row[8]) if row[8] else {},
                    error_info=row[9],
                    follow_up_actions=json.loads(row[10]) if row[10] else [],
                )
                results.append(result)

            return results

    async def get_health_metrics(
        self,
        server_name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[HealthMetrics]:
        """
        Retrieve health metrics from the database.

        Args:
            server_name: Filter by server name
            since: Filter by timestamp
            limit: Maximum number of results

        Returns:
            List[HealthMetrics]: Filtered health metrics
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            query = "SELECT * FROM health_metrics WHERE 1=1"
            params = []

            if server_name:
                query += " AND server_name = ?"
                params.append(server_name)

            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()

            metrics_list = []
            for row in rows:
                metrics = HealthMetrics(
                    server_name=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    connection_success_rate=row[3],
                    tool_execution_success_rate=row[4],
                    average_response_time=row[5],
                    error_count=row[6],
                    warning_count=row[7],
                    uptime_percentage=row[8],
                    last_successful_connection=(
                        datetime.fromisoformat(row[9]) if row[9] else None
                    ),
                    consecutive_failures=row[10],
                )
                metrics_list.append(metrics)

            return metrics_list

    async def resolve_issue(
        self, issue_id: str, resolution_notes: str = ""
    ) -> bool:
        """
        Mark an issue as resolved.

        Args:
            issue_id: ID of the issue to resolve
            resolution_notes: Optional notes about the resolution

        Returns:
            bool: True if issue was found and resolved
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            cursor = await db.execute(
                """
                UPDATE issues 
                SET status = 'resolved', resolved_at = ?, resolution_notes = ?
                WHERE id = ? AND status = 'open'
            """,
                (datetime.now().isoformat(), resolution_notes, issue_id),
            )

            await db.commit()
            return cursor.rowcount > 0

    async def get_issue_statistics(
        self,
        server_name: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive issue statistics.

        Args:
            server_name: Filter by server name
            since: Filter by timestamp

        Returns:
            Dict[str, Any]: Issue statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Base query conditions
            where_clause = "WHERE 1=1"
            params = []

            if server_name:
                where_clause += " AND server_name = ?"
                params.append(server_name)

            if since:
                where_clause += " AND timestamp >= ?"
                params.append(since.isoformat())

            # Total issues
            async with db.execute(
                f"SELECT COUNT(*) FROM issues {where_clause}", params
            ) as cursor:
                total_issues = (await cursor.fetchone())[0]

            # Issues by type
            async with db.execute(
                f"""
                SELECT issue_type, COUNT(*) 
                FROM issues {where_clause} 
                GROUP BY issue_type
            """,
                params,
            ) as cursor:
                issues_by_type = dict(await cursor.fetchall())

            # Issues by severity
            async with db.execute(
                f"""
                SELECT severity, COUNT(*) 
                FROM issues {where_clause} 
                GROUP BY severity
            """,
                params,
            ) as cursor:
                issues_by_severity = dict(await cursor.fetchall())

            # Resolution rate
            async with db.execute(
                f"""
                SELECT status, COUNT(*) 
                FROM issues {where_clause} 
                GROUP BY status
            """,
                params,
            ) as cursor:
                status_counts = dict(await cursor.fetchall())

            resolved_count = status_counts.get("resolved", 0)
            resolution_rate = (
                resolved_count / total_issues if total_issues > 0 else 0.0
            )

            # Average confidence score
            async with db.execute(
                f"""
                SELECT AVG(confidence_score) 
                FROM issues {where_clause}
            """,
                params,
            ) as cursor:
                avg_confidence = (await cursor.fetchone())[0] or 0.0

            # Remediation success rate
            remediation_params = params.copy()
            remediation_where = where_clause.replace(
                "issues",
                "remediation_results r JOIN issues i ON r.issue_id = i.id",
            )

            async with db.execute(
                f"""
                SELECT r.status, COUNT(*) 
                FROM remediation_results r 
                JOIN issues i ON r.issue_id = i.id 
                {remediation_where.replace("WHERE 1=1", "WHERE 1=1")}
                GROUP BY r.status
            """,
                remediation_params,
            ) as cursor:
                remediation_status_counts = dict(await cursor.fetchall())

            total_remediations = sum(remediation_status_counts.values())
            successful_remediations = remediation_status_counts.get(
                "success", 0
            )
            remediation_success_rate = (
                successful_remediations / total_remediations
                if total_remediations > 0
                else 0.0
            )

            return {
                "total_issues": total_issues,
                "issues_by_type": issues_by_type,
                "issues_by_severity": issues_by_severity,
                "resolution_rate": resolution_rate,
                "average_confidence_score": avg_confidence,
                "remediation_success_rate": remediation_success_rate,
                "status_distribution": status_counts,
                "remediation_status_distribution": remediation_status_counts,
            }

    async def learn_from_pattern(
        self, issue: Issue, remediation_success: bool
    ) -> None:
        """
        Learn from issue patterns to improve future detection and remediation.

        Args:
            issue: Issue to learn from
            remediation_success: Whether remediation was successful
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            # Create pattern signature
            pattern_signature = f"{issue.server_name}_{issue.issue_type.value}_{hash(issue.error_message or '')}"

            # Check if pattern exists
            async with db.execute(
                """
                SELECT id, occurrence_count, success_rate 
                FROM issue_patterns 
                WHERE pattern_signature = ?
            """,
                (pattern_signature,),
            ) as cursor:
                existing = await cursor.fetchone()

            if existing:
                # Update existing pattern
                pattern_id, occurrence_count, current_success_rate = existing
                new_occurrence_count = occurrence_count + 1

                # Update success rate using exponential moving average
                if remediation_success:
                    new_success_rate = current_success_rate * 0.8 + 0.2
                else:
                    new_success_rate = current_success_rate * 0.8

                await db.execute(
                    """
                    UPDATE issue_patterns 
                    SET occurrence_count = ?, last_seen = ?, success_rate = ?
                    WHERE id = ?
                """,
                    (
                        new_occurrence_count,
                        datetime.now().isoformat(),
                        new_success_rate,
                        pattern_id,
                    ),
                )
            else:
                # Create new pattern
                pattern_id = str(uuid.uuid4())
                initial_success_rate = 1.0 if remediation_success else 0.0

                await db.execute(
                    """
                    INSERT INTO issue_patterns (
                        id, pattern_signature, issue_type, occurrence_count,
                        first_seen, last_seen, success_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        pattern_id,
                        pattern_signature,
                        issue.issue_type.value,
                        1,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        initial_success_rate,
                    ),
                )

            await db.commit()

    async def get_pattern_insights(
        self, server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get insights from learned patterns.

        Args:
            server_name: Filter by server name

        Returns:
            Dict[str, Any]: Pattern insights
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            where_clause = ""
            params = []

            if server_name:
                where_clause = "WHERE pattern_signature LIKE ?"
                params.append(f"{server_name}_%")

            # Most common patterns
            async with db.execute(
                f"""
                SELECT issue_type, SUM(occurrence_count) as total_occurrences
                FROM issue_patterns {where_clause}
                GROUP BY issue_type
                ORDER BY total_occurrences DESC
                LIMIT 10
            """,
                params,
            ) as cursor:
                common_patterns = await cursor.fetchall()

            # Patterns with high success rates
            async with db.execute(
                f"""
                SELECT issue_type, AVG(success_rate) as avg_success_rate, COUNT(*) as pattern_count
                FROM issue_patterns {where_clause}
                GROUP BY issue_type
                HAVING pattern_count >= 3
                ORDER BY avg_success_rate DESC
            """,
                params,
            ) as cursor:
                successful_patterns = await cursor.fetchall()

            # Problematic patterns (low success rate, high occurrence)
            async with db.execute(
                f"""
                SELECT pattern_signature, issue_type, occurrence_count, success_rate
                FROM issue_patterns {where_clause}
                WHERE occurrence_count >= 3 AND success_rate < 0.5
                ORDER BY occurrence_count DESC
                LIMIT 10
            """,
                params,
            ) as cursor:
                problematic_patterns = await cursor.fetchall()

            return {
                "most_common_patterns": [
                    {"issue_type": row[0], "occurrences": row[1]}
                    for row in common_patterns
                ],
                "successful_patterns": [
                    {
                        "issue_type": row[0],
                        "success_rate": row[1],
                        "pattern_count": row[2],
                    }
                    for row in successful_patterns
                ],
                "problematic_patterns": [
                    {
                        "signature": row[0],
                        "issue_type": row[1],
                        "occurrences": row[2],
                        "success_rate": row[3],
                    }
                    for row in problematic_patterns
                ],
            }

    async def cleanup_old_data(
        self, retention_days: int = 90
    ) -> Dict[str, int]:
        """
        Clean up old data beyond retention period.

        Args:
            retention_days: Number of days to retain data

        Returns:
            Dict[str, int]: Count of cleaned up records
        """
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_iso = cutoff_date.isoformat()

            # Clean up old resolved issues
            cursor = await db.execute(
                """
                DELETE FROM issues 
                WHERE status = 'resolved' AND resolved_at < ?
            """,
                (cutoff_iso,),
            )
            cleaned_issues = cursor.rowcount

            # Clean up old health metrics
            cursor = await db.execute(
                """
                DELETE FROM health_metrics 
                WHERE timestamp < ?
            """,
                (cutoff_iso,),
            )
            cleaned_metrics = cursor.rowcount

            # Clean up orphaned remediation results
            cursor = await db.execute(
                """
                DELETE FROM remediation_results 
                WHERE issue_id NOT IN (SELECT id FROM issues)
            """,
                (),
            )
            cleaned_remediations = cursor.rowcount

            await db.commit()

            return {
                "cleaned_issues": cleaned_issues,
                "cleaned_metrics": cleaned_metrics,
                "cleaned_remediations": cleaned_remediations,
            }
