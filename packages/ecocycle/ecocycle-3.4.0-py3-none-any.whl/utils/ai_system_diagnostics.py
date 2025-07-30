"""
EcoCycle - AI-Powered System Diagnostics Module
Provides intelligent analysis and repair suggestions using AI for system issues.
"""
import os
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Check for Rich library
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

logger = logging.getLogger(__name__)


class AISystemDiagnostics:
    """AI-powered system diagnostics and repair suggestions."""
    
    def __init__(self):
        """Initialize the AI diagnostics system."""
        self.gemini_api = None
        self.ai_available = False
        self._initialize_ai()
    
    def _initialize_ai(self) -> None:
        """Initialize the AI system (Gemini API)."""
        try:
            # Import Gemini API from the existing route planner
            from apps.route_planner.ai_planner.api.gemini_api import GeminiAPI, GEMINI_AVAILABLE
            
            if GEMINI_AVAILABLE:
                self.gemini_api = GeminiAPI()
                self.ai_available = self.gemini_api.gemini_available
                if self.ai_available:
                    logger.info("AI diagnostics system initialized successfully")
                else:
                    logger.warning("Gemini API not available for AI diagnostics")
            else:
                logger.warning("Gemini package not available for AI diagnostics")
        except ImportError as e:
            logger.warning(f"Could not import AI components: {e}")
            self.ai_available = False
    
    def is_ai_available(self) -> bool:
        """Check if AI functionality is available."""
        return self.ai_available
    
    def analyze_system_issues(self, diagnostics_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze system diagnostics data using AI to provide intelligent insights.
        
        Args:
            diagnostics_data: System diagnostics data from SystemRepair
            
        Returns:
            Tuple of (success, analysis_result)
        """
        if not self.ai_available:
            return False, {"error": "AI analysis not available"}
        
        # Prepare the analysis prompt
        prompt = self._create_analysis_prompt(diagnostics_data)
        
        # Call AI with progress indication
        if HAS_RICH:
            with Progress(
                TextColumn("[bold blue]🤖 AI Analysis"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Analyzing system issues...", total=100)
                
                # Simulate progress during AI call
                for i in range(0, 100, 20):
                    progress.update(task, completed=i)
                    time.sleep(0.1)
                
                success, response = self.gemini_api.call_gemini_api(
                    prompt, 
                    progress_message="🔍 Analyzing system diagnostics"
                )
                
                progress.update(task, completed=100)
        else:
            print("🤖 Analyzing system issues with AI...")
            success, response = self.gemini_api.call_gemini_api(
                prompt, 
                progress_message="🔍 Analyzing system diagnostics"
            )
        
        if success:
            # Parse and structure the AI response
            analysis_result = self._parse_ai_analysis(response)
            return True, analysis_result
        else:
            return False, {"error": f"AI analysis failed: {response}"}
    
    def generate_repair_suggestions(self, issues: List[str], system_context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Generate AI-powered repair suggestions for specific issues.
        
        Args:
            issues: List of identified system issues
            system_context: Additional system context information
            
        Returns:
            Tuple of (success, suggestions_result)
        """
        if not self.ai_available:
            return False, {"error": "AI repair suggestions not available"}
        
        # Prepare the repair suggestions prompt
        prompt = self._create_repair_prompt(issues, system_context)
        
        # Call AI with progress indication
        if HAS_RICH:
            with Progress(
                TextColumn("[bold green]🔧 AI Repair Suggestions"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Generating repair suggestions...", total=100)
                
                # Simulate progress during AI call
                for i in range(0, 100, 25):
                    progress.update(task, completed=i)
                    time.sleep(0.1)
                
                success, response = self.gemini_api.call_gemini_api(
                    prompt, 
                    progress_message="🛠️ Generating repair suggestions"
                )
                
                progress.update(task, completed=100)
        else:
            print("🔧 Generating AI-powered repair suggestions...")
            success, response = self.gemini_api.call_gemini_api(
                prompt, 
                progress_message="🛠️ Generating repair suggestions"
            )
        
        if success:
            # Parse and structure the AI response
            suggestions_result = self._parse_repair_suggestions(response)
            return True, suggestions_result
        else:
            return False, {"error": f"AI repair suggestions failed: {response}"}
    
    def _create_analysis_prompt(self, diagnostics_data: Dict[str, Any]) -> str:
        """Create a prompt for AI analysis of system diagnostics."""
        # Extract key information from diagnostics
        issues_found = diagnostics_data.get('issues_found', [])
        system_health = diagnostics_data.get('overall_health', 'unknown')
        
        # Build detailed system information
        system_info = []
        for category, data in diagnostics_data.items():
            if isinstance(data, dict) and 'status' in data:
                status = data['status']
                issues = data.get('issues', [])
                if issues:
                    system_info.append(f"- {category.title()}: {status} ({len(issues)} issues)")
                    for issue in issues[:3]:  # Limit to first 3 issues per category
                        system_info.append(f"  • {issue}")
                else:
                    system_info.append(f"- {category.title()}: {status}")
        
        prompt = f"""
        You are an expert system administrator analyzing the health of an EcoCycle application.
        
        SYSTEM HEALTH OVERVIEW:
        Overall Health: {system_health}
        Total Issues Found: {len(issues_found)}
        
        DETAILED SYSTEM STATUS:
        {chr(10).join(system_info)}
        
        CRITICAL ISSUES TO ANALYZE:
        {chr(10).join([f"• {issue}" for issue in issues_found[:10]])}
        
        Please provide a comprehensive analysis including:
        
        1. **SEVERITY ASSESSMENT**: Rate the overall system health (Critical/High/Medium/Low)
        2. **ROOT CAUSE ANALYSIS**: Identify the most likely root causes of the issues
        3. **IMPACT ANALYSIS**: Explain how these issues affect the application
        4. **PRIORITY RANKING**: Rank issues by priority (1=highest, 5=lowest)
        5. **RISK ASSESSMENT**: Identify potential risks if issues are not addressed
        6. **RECOMMENDATIONS**: Provide specific, actionable recommendations
        
        Format your response in clear sections with bullet points for easy reading.
        Focus on practical, implementable solutions for a Python-based cycling application.
        """
        
        return prompt
    
    def _create_repair_prompt(self, issues: List[str], system_context: Dict[str, Any]) -> str:
        """Create a prompt for AI-generated repair suggestions."""
        context_info = []
        for key, value in system_context.items():
            if isinstance(value, (str, int, float, bool)):
                context_info.append(f"- {key}: {value}")
        
        prompt = f"""
        You are an expert system administrator providing repair solutions for an EcoCycle application.
        
        SYSTEM CONTEXT:
        {chr(10).join(context_info)}
        
        ISSUES TO REPAIR:
        {chr(10).join([f"• {issue}" for issue in issues])}
        
        Please provide detailed repair suggestions including:
        
        1. **IMMEDIATE ACTIONS**: Quick fixes that can be applied right now
        2. **STEP-BY-STEP REPAIRS**: Detailed instructions for each issue
        3. **PREVENTIVE MEASURES**: How to prevent these issues in the future
        4. **TESTING PROCEDURES**: How to verify that repairs were successful
        5. **ROLLBACK PLANS**: What to do if repairs cause problems
        6. **MONITORING RECOMMENDATIONS**: How to monitor for similar issues
        
        For each repair suggestion, include:
        - Difficulty level (Easy/Medium/Hard)
        - Estimated time to complete
        - Risk level (Low/Medium/High)
        - Required tools or dependencies
        
        Format your response with clear headings and actionable steps.
        Focus on solutions specific to Python applications and file system issues.
        """
        
        return prompt
    
    def _parse_ai_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parse and structure the AI analysis response."""
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "system_diagnostics",
            "ai_response": ai_response,
            "structured_data": {
                "severity": self._extract_severity(ai_response),
                "priority_issues": self._extract_priority_issues(ai_response),
                "recommendations": self._extract_recommendations(ai_response)
            }
        }
    
    def _parse_repair_suggestions(self, ai_response: str) -> Dict[str, Any]:
        """Parse and structure the AI repair suggestions response."""
        return {
            "timestamp": datetime.now().isoformat(),
            "suggestion_type": "repair_recommendations",
            "ai_response": ai_response,
            "structured_data": {
                "immediate_actions": self._extract_immediate_actions(ai_response),
                "detailed_repairs": self._extract_detailed_repairs(ai_response),
                "preventive_measures": self._extract_preventive_measures(ai_response)
            }
        }
    
    def _extract_severity(self, response: str) -> str:
        """Extract severity assessment from AI response."""
        response_lower = response.lower()
        if "critical" in response_lower:
            return "Critical"
        elif "high" in response_lower:
            return "High"
        elif "medium" in response_lower:
            return "Medium"
        else:
            return "Low"
    
    def _extract_priority_issues(self, response: str) -> List[str]:
        """Extract priority issues from AI response."""
        # Simple extraction - look for numbered lists or bullet points
        lines = response.split('\n')
        priority_issues = []
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '•', '-')) and len(line) > 10:
                priority_issues.append(line)
        return priority_issues[:5]  # Return top 5
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from AI response."""
        # Look for recommendation sections
        lines = response.split('\n')
        recommendations = []
        in_recommendations = False
        
        for line in lines:
            line = line.strip()
            if "recommendation" in line.lower():
                in_recommendations = True
                continue
            if in_recommendations and line.startswith(('•', '-', '1.', '2.', '3.')):
                recommendations.append(line)
        
        return recommendations[:10]  # Return top 10
    
    def _extract_immediate_actions(self, response: str) -> List[str]:
        """Extract immediate actions from AI response."""
        return self._extract_section_items(response, "immediate")
    
    def _extract_detailed_repairs(self, response: str) -> List[str]:
        """Extract detailed repairs from AI response."""
        return self._extract_section_items(response, "step-by-step")
    
    def _extract_preventive_measures(self, response: str) -> List[str]:
        """Extract preventive measures from AI response."""
        return self._extract_section_items(response, "preventive")
    
    def _extract_section_items(self, response: str, section_keyword: str) -> List[str]:
        """Extract items from a specific section of the AI response."""
        lines = response.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            if section_keyword.lower() in line.lower():
                in_section = True
                continue
            if in_section:
                if line.startswith(('•', '-', '1.', '2.', '3.')) and len(line) > 10:
                    items.append(line)
                elif line.startswith('#') or (line.isupper() and len(line) > 5):
                    # New section started
                    break
        
        return items[:8]  # Return top 8 items
