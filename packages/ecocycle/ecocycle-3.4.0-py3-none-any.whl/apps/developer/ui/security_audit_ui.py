"""
EcoCycle - Security Audit UI Component
Handles security auditing functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Prompt


class SecurityAuditUI(BaseUI):
    """UI component for security auditing."""

    def handle_security_audit(self):
        """Handle security audit interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🔒 Security Audit[/bold cyan]")
            console.print("1. Run security scan")
            console.print("2. Check file permissions")
            console.print("3. Audit user accounts")
            console.print("4. Review access logs")
            console.print("5. Vulnerability assessment")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nSecurity Audit")
            print("1. Run security scan")
            print("2. Check file permissions")
            print("3. Audit user accounts")
            print("4. Review access logs")
            print("5. Vulnerability assessment")
            print("0. Back to main menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            self._run_security_scan()
        elif choice == "2":
            self._check_file_permissions()
        elif choice == "3":
            self._audit_user_accounts()
        elif choice == "4":
            self._review_access_logs()
        elif choice == "5":
            self._vulnerability_assessment()

    def _run_security_scan(self):
        """Run comprehensive security scan."""
        self.display_info("🔍 Comprehensive Security Scan")

        status = self.show_status("Running security scan...")
        if status:
            with status:
                # Run all security audits
                password_audit = self.developer_tools.security_audit('password')
                session_audit = self.developer_tools.security_audit('session')
                permissions_audit = self.developer_tools.security_audit('permissions')
                config_audit = self.developer_tools.security_audit('config')
                vulnerability_audit = self.developer_tools.security_audit('vulnerability')
        else:
            # Run all security audits
            password_audit = self.developer_tools.security_audit('password')
            session_audit = self.developer_tools.security_audit('session')
            permissions_audit = self.developer_tools.security_audit('permissions')
            config_audit = self.developer_tools.security_audit('config')
            vulnerability_audit = self.developer_tools.security_audit('vulnerability')

        # Display comprehensive results
        audits = [
            ('Password Security', password_audit),
            ('Session Security', session_audit),
            ('File Permissions', permissions_audit),
            ('Configuration Security', config_audit),
            ('Vulnerability Assessment', vulnerability_audit)
        ]

        overall_risk = 'low'
        total_issues = 0

        for audit_name, audit_result in audits:
            risk_level = audit_result.get('risk_level', 'unknown')
            issues = len(audit_result.get('issues', []))
            total_issues += issues

            if risk_level == 'critical':
                overall_risk = 'critical'
            elif risk_level == 'high' and overall_risk != 'critical':
                overall_risk = 'high'
            elif risk_level == 'medium' and overall_risk not in ['critical', 'high']:
                overall_risk = 'medium'

            status_icon = {
                'low': '✅',
                'medium': '⚠️',
                'high': '🔴',
                'critical': '🚨'
            }.get(risk_level, '❓')

            self.display_info(f"{status_icon} {audit_name}: {risk_level.upper()} risk ({issues} issues)")

        # Overall summary
        overall_icon = {
            'low': '✅',
            'medium': '⚠️',
            'high': '🔴',
            'critical': '🚨'
        }.get(overall_risk, '❓')

        self.display_info(f"\n{overall_icon} Overall Security Status: {overall_risk.upper()}")
        self.display_info(f"📊 Total Issues Found: {total_issues}")

    def _check_file_permissions(self):
        """Check file permissions."""
        self.display_info("📁 File Permissions Audit")

        status = self.show_status("Checking file permissions...")
        if status:
            with status:
                audit_result = self.developer_tools.security_audit('permissions')
        else:
            audit_result = self.developer_tools.security_audit('permissions')

        if 'error' in audit_result:
            self.display_error(f"Audit failed: {audit_result['error']}")
            return

        risk_level = audit_result.get('risk_level', 'unknown')
        issues = audit_result.get('issues', [])
        file_analysis = audit_result.get('file_analysis', {})

        # Display risk level
        risk_colors = {
            'low': '✅',
            'medium': '⚠️',
            'high': '🔴',
            'critical': '🚨'
        }
        risk_icon = risk_colors.get(risk_level, '❓')

        self.display_info(f"{risk_icon} Permission Risk Level: {risk_level.upper()}")
        self.display_info(f"📊 Issues Found: {len(issues)}")

        # Show issues
        if issues:
            self.display_info("\n🚨 Permission Issues:")
            for i, issue in enumerate(issues[:10], 1):
                self.display_info(f"  {i}. {issue}")
            if len(issues) > 10:
                self.display_info(f"  ... and {len(issues) - 10} more issues")

        # Show file analysis summary
        if file_analysis:
            self.display_info("\n📋 File Analysis Summary:")
            for file_path, analysis in list(file_analysis.items())[:5]:
                permissions = analysis.get('permissions', 'Unknown')
                owner = analysis.get('owner', 'Unknown')
                self.display_info(f"  {file_path}: {permissions} (owner: {owner})")

    def _audit_user_accounts(self):
        """Audit user accounts."""
        self.display_info("👥 User Account Audit")

        status = self.show_status("Auditing user accounts...")
        if status:
            with status:
                # Get user data for audit
                try:
                    user_data = self.developer_tools.export_data('users')
                    session_data = self.developer_tools.manage_sessions('statistics')
                except Exception as e:
                    self.display_error(f"Failed to get user data: {e}")
                    return
        else:
            # Get user data for audit
            try:
                user_data = self.developer_tools.export_data('users')
                session_data = self.developer_tools.manage_sessions('statistics')
            except Exception as e:
                self.display_error(f"Failed to get user data: {e}")
                return

        if 'error' in user_data:
            self.display_error(f"User data error: {user_data['error']}")
            return

        users = user_data.get('users', [])
        stats = session_data.get('statistics', {})

        # Analyze user accounts
        total_users = len(users)
        active_users = 0
        admin_users = 0
        guest_users = 0
        inactive_users = 0

        for user in users:
            username = user.get('username', '')
            if 'guest' in username.lower():
                guest_users += 1
            if user.get('is_admin'):
                admin_users += 1
            if user.get('last_login'):
                active_users += 1
            else:
                inactive_users += 1

        # Display audit results
        self.display_info(f"📊 Total Users: {total_users}")
        self.display_info(f"👤 Active Users: {active_users}")
        self.display_info(f"🔒 Admin Users: {admin_users}")
        self.display_info(f"👻 Guest Users: {guest_users}")
        self.display_info(f"😴 Inactive Users: {inactive_users}")

        # Security recommendations
        recommendations = []
        if admin_users > 2:
            recommendations.append("Consider reducing number of admin accounts")
        if guest_users > 5:
            recommendations.append("Review guest account usage")
        if inactive_users > total_users * 0.3:
            recommendations.append("Clean up inactive user accounts")

        if recommendations:
            self.display_info("\n💡 Security Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                self.display_info(f"  {i}. {rec}")

    def _review_access_logs(self):
        """Review access logs."""
        self.display_info("📋 Access Log Review")

        status = self.show_status("Analyzing access logs...")
        if status:
            with status:
                log_data = self.developer_tools.analyze_logs()
        else:
            log_data = self.developer_tools.analyze_logs()

        if 'error' in log_data:
            self.display_error(f"Log analysis failed: {log_data['error']}")
            return

        recent_entries = log_data.get('recent_entries', {})

        # Analyze for security events
        security_events = []
        failed_logins = []
        suspicious_activity = []

        for log_file, entries in recent_entries.items():
            for entry in entries:
                entry_lower = entry.lower()
                if any(keyword in entry_lower for keyword in ['failed', 'error', 'unauthorized', 'denied']):
                    if 'login' in entry_lower or 'auth' in entry_lower:
                        failed_logins.append(entry)
                    else:
                        security_events.append(entry)

                if any(keyword in entry_lower for keyword in ['suspicious', 'attack', 'intrusion', 'breach']):
                    suspicious_activity.append(entry)

        # Display results
        self.display_info(f"🔍 Security Events Found: {len(security_events)}")
        self.display_info(f"🚫 Failed Login Attempts: {len(failed_logins)}")
        self.display_info(f"⚠️ Suspicious Activity: {len(suspicious_activity)}")

        # Show recent security events
        if security_events:
            self.display_info("\n🚨 Recent Security Events:")
            for i, event in enumerate(security_events[-5:], 1):
                self.display_info(f"  {i}. {event[:100]}...")

        if failed_logins:
            self.display_info("\n🚫 Recent Failed Logins:")
            for i, login in enumerate(failed_logins[-3:], 1):
                self.display_info(f"  {i}. {login[:100]}...")

        if suspicious_activity:
            self.display_info("\n⚠️ Suspicious Activity:")
            for i, activity in enumerate(suspicious_activity[-3:], 1):
                self.display_info(f"  {i}. {activity[:100]}...")

        if not (security_events or failed_logins or suspicious_activity):
            self.display_info("\n✅ No security issues found in recent logs")

    def _vulnerability_assessment(self):
        """Perform vulnerability assessment."""
        self.display_info("🛡️ Vulnerability Assessment")

        status = self.show_status("Performing vulnerability assessment...")
        if status:
            with status:
                assessment_result = self.developer_tools.security_audit('vulnerability')
        else:
            assessment_result = self.developer_tools.security_audit('vulnerability')

        if 'error' in assessment_result:
            self.display_error(f"Assessment failed: {assessment_result['error']}")
            return

        risk_level = assessment_result.get('risk_level', 'unknown')
        vulnerabilities = assessment_result.get('vulnerabilities', [])
        checks_performed = assessment_result.get('checks_performed', [])
        recommendations = assessment_result.get('recommendations', [])

        # Display risk level
        risk_colors = {
            'low': '✅',
            'medium': '⚠️',
            'high': '🔴',
            'critical': '🚨'
        }
        risk_icon = risk_colors.get(risk_level, '❓')

        self.display_info(f"{risk_icon} Vulnerability Risk Level: {risk_level.upper()}")
        self.display_info(f"🔍 Checks Performed: {len(checks_performed)}")
        self.display_info(f"🚨 Vulnerabilities Found: {len(vulnerabilities)}")

        # Show vulnerabilities
        if vulnerabilities:
            self.display_info("\n🚨 Vulnerabilities Found:")
            for i, vuln in enumerate(vulnerabilities[:10], 1):
                self.display_info(f"  {i}. {vuln}")
            if len(vulnerabilities) > 10:
                self.display_info(f"  ... and {len(vulnerabilities) - 10} more vulnerabilities")
        else:
            self.display_info("\n✅ No vulnerabilities detected")

        # Show recommendations
        if recommendations:
            self.display_info("\n💡 Security Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                self.display_info(f"  {i}. {rec}")

        # Show checks performed
        if checks_performed:
            self.display_info(f"\n🔍 Assessment included: {', '.join(checks_performed)}")
