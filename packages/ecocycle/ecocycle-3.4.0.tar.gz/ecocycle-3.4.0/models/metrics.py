"""
EcoCycle Usage Metrics Collection and Analysis
===========================================

This module handles the collection, storage, and analysis of application
usage metrics to help improve the user experience and identify areas for
enhancement.
"""

import datetime
import json
import os
import uuid
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores usage metrics throughout the application."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the MetricsCollector.
        
        Args:
            storage_path (str, optional): Path to store metrics data. If None, uses default location.
        """
        self.storage_path = storage_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                        'db', 'metrics')
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Define paths for different metric types
        self.session_file = os.path.join(self.storage_path, 'sessions.json')
        self.feature_usage_file = os.path.join(self.storage_path, 'feature_usage.json')
        self.performance_file = os.path.join(self.storage_path, 'performance.json')
        self.error_file = os.path.join(self.storage_path, 'errors.json')
        
        # Load existing metrics
        self._load_metrics()
    
    def _load_metrics(self) -> None:
        """Load existing metrics from storage."""
        # Sessions
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
            except json.JSONDecodeError:
                self.sessions = {"items": [], "summary": {}}
        else:
            self.sessions = {"items": [], "summary": {}}
        
        # Feature usage
        if os.path.exists(self.feature_usage_file):
            try:
                with open(self.feature_usage_file, 'r', encoding='utf-8') as f:
                    self.feature_usage = json.load(f)
            except json.JSONDecodeError:
                self.feature_usage = {"items": [], "summary": {}}
        else:
            self.feature_usage = {"items": [], "summary": {}}
        
        # Performance metrics
        if os.path.exists(self.performance_file):
            try:
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    self.performance = json.load(f)
            except json.JSONDecodeError:
                self.performance = {"items": [], "summary": {}}
        else:
            self.performance = {"items": [], "summary": {}}
        
        # Error tracking
        if os.path.exists(self.error_file):
            try:
                with open(self.error_file, 'r', encoding='utf-8') as f:
                    self.errors = json.load(f)
            except json.JSONDecodeError:
                self.errors = {"items": [], "summary": {}}
        else:
            self.errors = {"items": [], "summary": {}}
    
    def _save_sessions(self) -> None:
        """Save session metrics to storage."""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _save_feature_usage(self) -> None:
        """Save feature usage metrics to storage."""
        with open(self.feature_usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.feature_usage, f, indent=2)
    
    def _save_performance(self) -> None:
        """Save performance metrics to storage."""
        with open(self.performance_file, 'w', encoding='utf-8') as f:
            json.dump(self.performance, f, indent=2)
    
    def _save_errors(self) -> None:
        """Save error metrics to storage."""
        with open(self.error_file, 'w', encoding='utf-8') as f:
            json.dump(self.errors, f, indent=2)
    
    def log_session_start(self, user_id: str, platform: str, 
                         app_version: str, device_info: Dict = None) -> str:
        """
        Log the start of a user session.
        
        Args:
            user_id: User identifier (or anonymous ID for non-logged in users)
            platform: Platform identifier (desktop, web, mobile)
            app_version: Application version
            device_info: Optional device information
            
        Returns:
            str: Session ID for tracking session events
        """
        session_id = str(uuid.uuid4())
        
        # Create session record
        session = {
            "id": session_id,
            "user_id": user_id,
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "platform": platform,
            "app_version": app_version,
            "device_info": device_info or {},
            "duration_seconds": None,
            "events": []
        }
        
        # Add to sessions
        self.sessions["items"].append(session)
        self._save_sessions()
        
        # Update summary stats
        self._update_session_summary()
        
        return session_id
    
    def log_session_end(self, session_id: str) -> bool:
        """
        Log the end of a user session.
        
        Args:
            session_id: Session ID returned from log_session_start
            
        Returns:
            bool: True if successful, False otherwise
        """
        for session in self.sessions["items"]:
            if session["id"] == session_id:
                # Set end time
                end_time = datetime.datetime.now()
                session["end_time"] = end_time.isoformat()
                
                # Calculate duration
                start_time = datetime.datetime.fromisoformat(session["start_time"])
                duration = (end_time - start_time).total_seconds()
                session["duration_seconds"] = duration
                
                self._save_sessions()
                self._update_session_summary()
                return True
        
        return False
    
    def log_session_event(self, session_id: str, event_type: str, 
                        details: Dict = None) -> bool:
        """
        Log an event within a session.
        
        Args:
            session_id: Session ID
            event_type: Type of event (e.g., "page_view", "button_click")
            details: Optional event details
            
        Returns:
            bool: True if successful, False otherwise
        """
        for session in self.sessions["items"]:
            if session["id"] == session_id:
                event = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": event_type,
                    "details": details or {}
                }
                
                session["events"].append(event)
                self._save_sessions()
                return True
        
        return False
    
    def log_feature_usage(self, user_id: str, feature: str, 
                        action: str, context: Dict = None,
                        session_id: Optional[str] = None) -> None:
        """
        Log feature usage.
        
        Args:
            user_id: User identifier
            feature: Feature identifier
            action: Action taken (e.g., "view", "edit", "create")
            context: Optional context information
            session_id: Optional session ID
        """
        usage_item = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "feature": feature,
            "action": action,
            "timestamp": datetime.datetime.now().isoformat(),
            "context": context or {},
        }
        
        if session_id:
            usage_item["session_id"] = session_id
        
        self.feature_usage["items"].append(usage_item)
        self._save_feature_usage()
        self._update_feature_usage_summary()
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             user_id: Optional[str] = None,
                             context: Dict = None,
                             session_id: Optional[str] = None) -> None:
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric (e.g., "page_load_time", "query_time")
            value: Metric value (typically in milliseconds)
            user_id: Optional user identifier
            context: Optional context information
            session_id: Optional session ID
        """
        metric_item = {
            "id": str(uuid.uuid4()),
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
            "context": context or {},
        }
        
        if user_id:
            metric_item["user_id"] = user_id
        
        if session_id:
            metric_item["session_id"] = session_id
        
        self.performance["items"].append(metric_item)
        self._save_performance()
        self._update_performance_summary()
    
    def log_error(self, error_type: str, error_message: str, 
                user_id: Optional[str] = None,
                stack_trace: Optional[str] = None,
                context: Dict = None,
                session_id: Optional[str] = None) -> None:
        """
        Log an application error.
        
        Args:
            error_type: Type of error (e.g., "api_error", "database_error")
            error_message: Error message
            user_id: Optional user identifier
            stack_trace: Optional stack trace
            context: Optional context information
            session_id: Optional session ID
        """
        error_item = {
            "id": str(uuid.uuid4()),
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.datetime.now().isoformat(),
            "context": context or {},
        }
        
        if user_id:
            error_item["user_id"] = user_id
        
        if stack_trace:
            error_item["stack_trace"] = stack_trace
        
        if session_id:
            error_item["session_id"] = session_id
        
        self.errors["items"].append(error_item)
        self._save_errors()
        self._update_error_summary()
    
    def _update_session_summary(self) -> None:
        """Update summary statistics for sessions."""
        summary = self.sessions["summary"]
        
        # Count total sessions
        summary["total_sessions"] = len(self.sessions["items"])
        
        # Count by platform
        platform_counts = {}
        for session in self.sessions["items"]:
            platform = session["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        summary["by_platform"] = platform_counts
        
        # Calculate average session duration
        durations = [s["duration_seconds"] for s in self.sessions["items"] if s["duration_seconds"] is not None]
        summary["average_duration"] = sum(durations) / len(durations) if durations else 0
        
        # Sessions by day
        by_day = {}
        for session in self.sessions["items"]:
            day = session["start_time"].split("T")[0]  # Get YYYY-MM-DD part
            by_day[day] = by_day.get(day, 0) + 1
        summary["by_day"] = by_day
    
    def _update_feature_usage_summary(self) -> None:
        """Update summary statistics for feature usage."""
        summary = self.feature_usage["summary"]
        
        # Count by feature
        feature_counts = {}
        for usage in self.feature_usage["items"]:
            feature = usage["feature"]
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
        summary["by_feature"] = feature_counts
        
        # Count by action
        action_counts = {}
        for usage in self.feature_usage["items"]:
            action = usage["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        summary["by_action"] = action_counts
    
    def _update_performance_summary(self) -> None:
        """Update summary statistics for performance metrics."""
        summary = self.performance["summary"]
        
        # Calculate statistics by metric name
        metrics_stats = {}
        for metric in self.performance["items"]:
            name = metric["metric_name"]
            value = metric["value"]
            
            if name not in metrics_stats:
                metrics_stats[name] = {
                    "count": 0,
                    "sum": 0,
                    "min": float('inf'),
                    "max": float('-inf')
                }
            
            metrics_stats[name]["count"] += 1
            metrics_stats[name]["sum"] += value
            metrics_stats[name]["min"] = min(metrics_stats[name]["min"], value)
            metrics_stats[name]["max"] = max(metrics_stats[name]["max"], value)
        
        # Calculate averages
        for name, stats in metrics_stats.items():
            stats["avg"] = stats["sum"] / stats["count"]
        
        summary["by_metric"] = metrics_stats
    
    def _update_error_summary(self) -> None:
        """Update summary statistics for errors."""
        summary = self.errors["summary"]
        
        # Count by error type
        error_counts = {}
        for error in self.errors["items"]:
            error_type = error["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        summary["by_type"] = error_counts
        
        # Errors by day
        by_day = {}
        for error in self.errors["items"]:
            day = error["timestamp"].split("T")[0]  # Get YYYY-MM-DD part
            by_day[day] = by_day.get(day, 0) + 1
        summary["by_day"] = by_day
    
    def get_session_metrics(self, days: int = 30, 
                          platform: Optional[str] = None) -> Dict:
        """
        Get session metrics for analysis.
        
        Args:
            days: Number of days to include in the analysis
            platform: Optional platform filter
            
        Returns:
            Dict: Session metrics and analysis
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        # Filter sessions by date and platform
        filtered_sessions = [
            s for s in self.sessions["items"] 
            if s["start_time"] >= cutoff_date and
            (platform is None or s["platform"] == platform)
        ]
        
        # Prepare results
        results = {
            "total_sessions": len(filtered_sessions),
            "average_duration": 0,
            "by_day": {},
            "by_platform": {},
            "active_users": {
                "daily": 0,
                "weekly": 0,
                "monthly": len(set(s["user_id"] for s in filtered_sessions))
            }
        }
        
        # Calculate metrics
        if filtered_sessions:
            # Average duration
            durations = [s["duration_seconds"] for s in filtered_sessions if s["duration_seconds"] is not None]
            results["average_duration"] = sum(durations) / len(durations) if durations else 0
            
            # Sessions by day
            by_day = {}
            for session in filtered_sessions:
                day = session["start_time"].split("T")[0]
                by_day[day] = by_day.get(day, 0) + 1
            results["by_day"] = by_day
            
            # Sessions by platform
            by_platform = {}
            for session in filtered_sessions:
                platform_name = session["platform"]
                by_platform[platform_name] = by_platform.get(platform_name, 0) + 1
            results["by_platform"] = by_platform
            
            # Daily active users (last 24 hours)
            one_day_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            results["active_users"]["daily"] = len(set(
                s["user_id"] for s in filtered_sessions if s["start_time"] >= one_day_ago
            ))
            
            # Weekly active users (last 7 days)
            one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            results["active_users"]["weekly"] = len(set(
                s["user_id"] for s in filtered_sessions if s["start_time"] >= one_week_ago
            ))
        
        return results
    
    def get_feature_usage_metrics(self, days: int = 30, 
                                feature: Optional[str] = None) -> Dict:
        """
        Get feature usage metrics for analysis.
        
        Args:
            days: Number of days to include in the analysis
            feature: Optional feature filter
            
        Returns:
            Dict: Feature usage metrics and analysis
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        # Filter feature usage by date and feature
        filtered_usage = [
            u for u in self.feature_usage["items"] 
            if u["timestamp"] >= cutoff_date and
            (feature is None or u["feature"] == feature)
        ]
        
        # Prepare results
        results = {
            "total_usage_events": len(filtered_usage),
            "by_feature": {},
            "by_action": {},
            "popular_features": [],
            "by_day": {}
        }
        
        # Calculate metrics
        if filtered_usage:
            # Usage by feature
            by_feature = {}
            for usage in filtered_usage:
                feature_name = usage["feature"]
                by_feature[feature_name] = by_feature.get(feature_name, 0) + 1
            results["by_feature"] = by_feature
            
            # Usage by action
            by_action = {}
            for usage in filtered_usage:
                action_name = usage["action"]
                by_action[action_name] = by_action.get(action_name, 0) + 1
            results["by_action"] = by_action
            
            # Popular features
            popular_features = sorted(by_feature.items(), key=lambda x: x[1], reverse=True)
            results["popular_features"] = [{"feature": f, "count": c} for f, c in popular_features[:10]]
            
            # Usage by day
            by_day = {}
            for usage in filtered_usage:
                day = usage["timestamp"].split("T")[0]
                by_day[day] = by_day.get(day, 0) + 1
            results["by_day"] = by_day
        
        return results
    
    def get_performance_metrics(self, days: int = 30, 
                              metric_name: Optional[str] = None) -> Dict:
        """
        Get performance metrics for analysis.
        
        Args:
            days: Number of days to include in the analysis
            metric_name: Optional metric name filter
            
        Returns:
            Dict: Performance metrics and analysis
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        # Filter performance metrics by date and name
        filtered_metrics = [
            m for m in self.performance["items"] 
            if m["timestamp"] >= cutoff_date and
            (metric_name is None or m["metric_name"] == metric_name)
        ]
        
        # Prepare results
        results = {
            "total_metrics": len(filtered_metrics),
            "by_metric": {},
            "trends": {}
        }
        
        # Calculate metrics
        if filtered_metrics:
            # Statistics by metric name
            by_metric = {}
            for metric in filtered_metrics:
                name = metric["metric_name"]
                value = metric["value"]
                
                if name not in by_metric:
                    by_metric[name] = {
                        "count": 0,
                        "sum": 0,
                        "min": float('inf'),
                        "max": float('-inf'),
                        "values": []
                    }
                
                by_metric[name]["count"] += 1
                by_metric[name]["sum"] += value
                by_metric[name]["min"] = min(by_metric[name]["min"], value)
                by_metric[name]["max"] = max(by_metric[name]["max"], value)
                by_metric[name]["values"].append(value)
            
            # Calculate averages and standard deviations
            for name, stats in by_metric.items():
                stats["avg"] = stats["sum"] / stats["count"]
                
                # Calculate standard deviation
                if stats["count"] > 1:
                    variance = sum((x - stats["avg"]) ** 2 for x in stats["values"]) / stats["count"]
                    stats["std_dev"] = variance ** 0.5
                else:
                    stats["std_dev"] = 0
                
                # Remove raw values to save space
                del stats["values"]
            
            results["by_metric"] = by_metric
            
            # Calculate trends (weekly averages)
            if days >= 14:  # Only calculate trends if we have at least 2 weeks of data
                trends = {}
                
                for metric in filtered_metrics:
                    name = metric["metric_name"]
                    value = metric["value"]
                    date = metric["timestamp"].split("T")[0]
                    week = datetime.datetime.fromisoformat(date).strftime("%Y-W%W")
                    
                    if name not in trends:
                        trends[name] = {}
                    
                    if week not in trends[name]:
                        trends[name][week] = {"sum": 0, "count": 0}
                    
                    trends[name][week]["sum"] += value
                    trends[name][week]["count"] += 1
                
                # Calculate weekly averages
                for name, weeks in trends.items():
                    for week, data in weeks.items():
                        data["avg"] = data["sum"] / data["count"]
                
                results["trends"] = trends
        
        return results
    
    def get_error_metrics(self, days: int = 30, 
                         error_type: Optional[str] = None) -> Dict:
        """
        Get error metrics for analysis.
        
        Args:
            days: Number of days to include in the analysis
            error_type: Optional error type filter
            
        Returns:
            Dict: Error metrics and analysis
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        # Filter errors by date and type
        filtered_errors = [
            e for e in self.errors["items"] 
            if e["timestamp"] >= cutoff_date and
            (error_type is None or e["error_type"] == error_type)
        ]
        
        # Prepare results
        results = {
            "total_errors": len(filtered_errors),
            "by_type": {},
            "by_day": {},
            "common_messages": []
        }
        
        # Calculate metrics
        if filtered_errors:
            # Errors by type
            by_type = {}
            for error in filtered_errors:
                error_type = error["error_type"]
                by_type[error_type] = by_type.get(error_type, 0) + 1
            results["by_type"] = by_type
            
            # Errors by day
            by_day = {}
            for error in filtered_errors:
                day = error["timestamp"].split("T")[0]
                by_day[day] = by_day.get(day, 0) + 1
            results["by_day"] = by_day
            
            # Common error messages
            message_counts = {}
            for error in filtered_errors:
                message = error["error_message"]
                message_counts[message] = message_counts.get(message, 0) + 1
            
            common_messages = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)
            results["common_messages"] = [{"message": m, "count": c} for m, c in common_messages[:10]]
        
        return results
    
    def get_comprehensive_metrics(self, days: int = 30) -> Dict:
        """
        Get comprehensive metrics across all categories.
        
        Args:
            days: Number of days to include in the analysis
            
        Returns:
            Dict: Comprehensive metrics and analysis
        """
        return {
            "sessions": self.get_session_metrics(days),
            "feature_usage": self.get_feature_usage_metrics(days),
            "performance": self.get_performance_metrics(days),
            "errors": self.get_error_metrics(days)
        }
    
    def export_metrics(self, metric_type: str, format_type: str = "json",
                     days: int = 30) -> Any:
        """
        Export metrics data in various formats.
        
        Args:
            metric_type: Type of metrics to export ("sessions", "feature_usage", "performance", "errors", "all")
            format_type: Format type ("json", "csv")
            days: Number of days to include
            
        Returns:
            str or dict: Exported data in requested format
        """
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        if metric_type == "sessions":
            data = [s for s in self.sessions["items"] if s["start_time"] >= cutoff_date]
        elif metric_type == "feature_usage":
            data = [u for u in self.feature_usage["items"] if u["timestamp"] >= cutoff_date]
        elif metric_type == "performance":
            data = [m for m in self.performance["items"] if m["timestamp"] >= cutoff_date]
        elif metric_type == "errors":
            data = [e for e in self.errors["items"] if e["timestamp"] >= cutoff_date]
        elif metric_type == "all":
            return {
                "sessions": [s for s in self.sessions["items"] if s["start_time"] >= cutoff_date],
                "feature_usage": [u for u in self.feature_usage["items"] if u["timestamp"] >= cutoff_date],
                "performance": [m for m in self.performance["items"] if m["timestamp"] >= cutoff_date],
                "errors": [e for e in self.errors["items"] if e["timestamp"] >= cutoff_date]
            }
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")
        
        if format_type == "json":
            return data
        elif format_type == "csv":
            # Generate CSV formatted string
            if not data:
                return ""
            
            # Get headers from the first item
            headers = list(data[0].keys())
            csv_lines = [",".join(headers)]
            
            # Add data rows
            for item in data:
                row = []
                for header in headers:
                    value = item.get(header, "")
                    # Handle complex types
                    if isinstance(value, dict):
                        value = json.dumps(value).replace(',', ';')
                    # Escape commas in string values
                    if isinstance(value, str):
                        value = f'"{value}"'
                    row.append(str(value))
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
