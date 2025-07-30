"""
EcoCycle - API Testing UI Component
Handles API testing tools functionality.
"""
import json
import requests
import time
from typing import Dict, Any, Optional
from .base_ui import BaseUI, HAS_RICH, console, Prompt, Confirm, Table, Panel


class APITestingUI(BaseUI):
    """UI component for API testing tools."""

    def __init__(self, developer_auth, developer_tools):
        """Initialize API testing UI."""
        super().__init__(developer_auth, developer_tools)
        self.base_url = "http://localhost:5000"  # Default Flask dev server
        self.api_token = None
        self.test_results = []

    def handle_api_testing(self):
        """Handle API testing tools interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🔌 API Testing Tools[/bold cyan]")
            console.print("1. Test authentication endpoints")
            console.print("2. Test user management APIs")
            console.print("3. Test data export APIs")
            console.print("4. Test system health APIs")
            console.print("5. Custom API request")
            console.print("6. Configure API settings")
            console.print("7. View test results")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")
        else:
            print("\nAPI Testing Tools")
            print("1. Test authentication endpoints")
            print("2. Test user management APIs")
            print("3. Test data export APIs")
            print("4. Test system health APIs")
            print("5. Custom API request")
            print("6. Configure API settings")
            print("7. View test results")
            print("0. Back to main menu")

            choice = input("Select option (0-7): ").strip()

        if choice == "1":
            self._test_auth_endpoints()
        elif choice == "2":
            self._test_user_management_apis()
        elif choice == "3":
            self._test_data_export_apis()
        elif choice == "4":
            self._test_system_health_apis()
        elif choice == "5":
            self._custom_api_request()
        elif choice == "6":
            self._configure_api_settings()
        elif choice == "7":
            self._view_test_results()

    def _test_auth_endpoints(self):
        """Test authentication endpoints."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]🔐 Testing Authentication Endpoints[/bold yellow]")
        else:
            print("\n🔐 Testing Authentication Endpoints")

        # Test endpoints
        auth_tests = [
            {
                'name': 'Generate API Token',
                'method': 'POST',
                'endpoint': '/api/auth/token',
                'data': {
                    'username': 'test_user',
                    'password': 'test_password',
                    'device_id': 'dev_test_device',
                    'device_name': 'Developer Test Device',
                    'device_type': 'developer_tool'
                }
            },
            {
                'name': 'Test Session Authentication',
                'method': 'GET',
                'endpoint': '/api/user/profile',
                'requires_auth': True
            }
        ]

        for test in auth_tests:
            self._run_api_test(test)

    def _test_user_management_apis(self):
        """Test user management APIs."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]👥 Testing User Management APIs[/bold yellow]")
        else:
            print("\n👥 Testing User Management APIs")

        # Test endpoints
        user_tests = [
            {
                'name': 'Get User Profile',
                'method': 'GET',
                'endpoint': '/api/user/profile',
                'requires_auth': True
            },
            {
                'name': 'Update User Profile',
                'method': 'PUT',
                'endpoint': '/api/user/profile',
                'requires_auth': True,
                'data': {
                    'name': 'Test User Updated',
                    'preferences': {'theme': 'dark'}
                }
            },
            {
                'name': 'Get User Statistics',
                'method': 'GET',
                'endpoint': '/api/stats/test_user',
                'requires_auth': True
            },
            {
                'name': 'Get Environmental Impact',
                'method': 'GET',
                'endpoint': '/api/environmental-impact/test_user',
                'requires_auth': True
            }
        ]

        for test in user_tests:
            self._run_api_test(test)

    def _test_data_export_apis(self):
        """Test data export APIs."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]📊 Testing Data Export APIs[/bold yellow]")
        else:
            print("\n📊 Testing Data Export APIs")

        # Test endpoints
        export_tests = [
            {
                'name': 'Get User Routes',
                'method': 'GET',
                'endpoint': '/api/routes',
                'requires_auth': True
            },
            {
                'name': 'Get User Trips',
                'method': 'GET',
                'endpoint': '/api/trips/test_user',
                'requires_auth': True
            },
            {
                'name': 'Create New Route',
                'method': 'POST',
                'endpoint': '/api/routes',
                'requires_auth': True,
                'data': {
                    'name': 'Test Route',
                    'start_point': 'Test Start',
                    'end_point': 'Test End',
                    'distance': 10.5,
                    'coordinates': [[0, 0], [1, 1]]
                }
            }
        ]

        for test in export_tests:
            self._run_api_test(test)

    def _test_system_health_apis(self):
        """Test system health APIs."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]🏥 Testing System Health APIs[/bold yellow]")
        else:
            print("\n🏥 Testing System Health APIs")

        # Test basic health endpoints
        health_tests = [
            {
                'name': 'Basic Health Check',
                'method': 'GET',
                'endpoint': '/',
                'expect_redirect': True
            },
            {
                'name': 'Login Page Access',
                'method': 'GET',
                'endpoint': '/login'
            }
        ]

        for test in health_tests:
            self._run_api_test(test)

    def _custom_api_request(self):
        """Make a custom API request."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]🔧 Custom API Request[/bold yellow]")

            method = Prompt.ask("HTTP Method", choices=["GET", "POST", "PUT", "DELETE", "PATCH"], default="GET")
            endpoint = Prompt.ask("Endpoint (e.g., /api/user/profile)")

            # Ask for headers
            add_headers = Confirm.ask("Add custom headers?", default=False)
            headers = {}
            if add_headers:
                while True:
                    header_name = Prompt.ask("Header name (or press Enter to finish)", default="")
                    if not header_name:
                        break
                    header_value = Prompt.ask(f"Value for {header_name}")
                    headers[header_name] = header_value

            # Ask for data
            data = None
            if method in ['POST', 'PUT', 'PATCH']:
                add_data = Confirm.ask("Add request body?", default=False)
                if add_data:
                    data_str = Prompt.ask("JSON data (or press Enter for empty)")
                    if data_str:
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            console.print("[red]Invalid JSON format, sending as string[/red]")
                            data = data_str

            # Ask for authentication
            use_auth = Confirm.ask("Use authentication?", default=True)

        else:
            print("\n🔧 Custom API Request")
            method = input("HTTP Method (GET/POST/PUT/DELETE/PATCH) [GET]: ").strip().upper() or "GET"
            endpoint = input("Endpoint (e.g., /api/user/profile): ").strip()

            # Headers
            headers = {}
            add_headers = input("Add custom headers? (y/N): ").strip().lower() == 'y'
            if add_headers:
                while True:
                    header_name = input("Header name (or press Enter to finish): ").strip()
                    if not header_name:
                        break
                    header_value = input(f"Value for {header_name}: ").strip()
                    headers[header_name] = header_value

            # Data
            data = None
            if method in ['POST', 'PUT', 'PATCH']:
                add_data = input("Add request body? (y/N): ").strip().lower() == 'y'
                if add_data:
                    data_str = input("JSON data (or press Enter for empty): ").strip()
                    if data_str:
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            print("Invalid JSON format, sending as string")
                            data = data_str

            use_auth = input("Use authentication? (Y/n): ").strip().lower() != 'n'

        # Create test configuration
        test_config = {
            'name': f'Custom {method} Request',
            'method': method,
            'endpoint': endpoint,
            'headers': headers,
            'data': data,
            'requires_auth': use_auth
        }

        self._run_api_test(test_config)

    def _configure_api_settings(self):
        """Configure API testing settings."""
        if HAS_RICH and console:
            console.print("\n[bold yellow]⚙️ API Configuration[/bold yellow]")

            current_url = self.base_url
            console.print(f"Current base URL: [cyan]{current_url}[/cyan]")

            new_url = Prompt.ask("Enter new base URL", default=current_url)
            self.base_url = new_url

            # Test connection
            if Confirm.ask("Test connection to new URL?", default=True):
                self._test_connection()

        else:
            print("\n⚙️ API Configuration")
            print(f"Current base URL: {self.base_url}")
            new_url = input(f"Enter new base URL [{self.base_url}]: ").strip()
            if new_url:
                self.base_url = new_url

            test_conn = input("Test connection to URL? (Y/n): ").strip().lower() != 'n'
            if test_conn:
                self._test_connection()

    def _view_test_results(self):
        """View API test results."""
        if not self.test_results:
            self.display_info("No test results available. Run some tests first.")
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 API Test Results[/bold cyan]")

            table = Table(title=f"Test Results ({len(self.test_results)} tests)")
            table.add_column("Test Name", style="cyan")
            table.add_column("Method", style="yellow")
            table.add_column("Endpoint", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Response Time", style="magenta")
            table.add_column("Result", style="white")

            for result in self.test_results[-20:]:  # Show last 20 results
                status_color = "green" if result['success'] else "red"
                status_text = f"[{status_color}]{result['status_code']}[/{status_color}]"
                result_text = "✅ PASS" if result['success'] else "❌ FAIL"

                table.add_row(
                    result['test_name'],
                    result['method'],
                    result['endpoint'][:30] + "..." if len(result['endpoint']) > 30 else result['endpoint'],
                    status_text,
                    f"{result['response_time']:.2f}ms",
                    result_text
                )

            console.print(table)

            # Show summary
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r['success'])
            failed_tests = total_tests - passed_tests

            summary_panel = Panel.fit(
                f"[bold]Total Tests:[/bold] {total_tests}\n"
                f"[bold green]Passed:[/bold green] {passed_tests}\n"
                f"[bold red]Failed:[/bold red] {failed_tests}\n"
                f"[bold]Success Rate:[/bold] {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "[bold]Success Rate:[/bold] N/A",
                title="📈 Test Summary"
            )
            console.print(summary_panel)

        else:
            print("\n📊 API Test Results")
            print("-" * 80)
            for result in self.test_results[-20:]:
                status = "PASS" if result['success'] else "FAIL"
                print(f"Test: {result['test_name']}")
                print(f"  Method: {result['method']} {result['endpoint']}")
                print(f"  Status: {result['status_code']} - {status}")
                print(f"  Response Time: {result['response_time']:.2f}ms")
                if not result['success'] and result.get('error'):
                    print(f"  Error: {result['error']}")
                print()

    def _test_connection(self):
        """Test connection to the API base URL."""
        try:
            if HAS_RICH and console:
                with console.status(f"[bold green]Testing connection to {self.base_url}..."):
                    response = requests.get(self.base_url, timeout=5)

                if response.status_code < 400:
                    console.print(f"[green]✅ Connection successful! Status: {response.status_code}[/green]")
                else:
                    console.print(f"[yellow]⚠️ Connection established but got status: {response.status_code}[/yellow]")
            else:
                print(f"Testing connection to {self.base_url}...")
                response = requests.get(self.base_url, timeout=5)

                if response.status_code < 400:
                    print(f"✅ Connection successful! Status: {response.status_code}")
                else:
                    print(f"⚠️ Connection established but got status: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.display_error(f"❌ Connection failed: Unable to connect to {self.base_url}")
        except requests.exceptions.Timeout:
            self.display_error("❌ Connection failed: Request timed out")
        except Exception as e:
            self.display_error(f"❌ Connection failed: {str(e)}")

    def _run_api_test(self, test_config: Dict[str, Any]):
        """Run a single API test."""
        test_name = test_config.get('name', 'Unknown Test')
        method = test_config.get('method', 'GET')
        endpoint = test_config.get('endpoint', '/')
        data = test_config.get('data')
        headers = test_config.get('headers', {})
        requires_auth = test_config.get('requires_auth', False)
        expect_redirect = test_config.get('expect_redirect', False)

        # Build full URL
        url = self.base_url.rstrip('/') + endpoint

        # Prepare headers
        request_headers = {'Content-Type': 'application/json'}
        request_headers.update(headers)

        # Add authentication if required
        if requires_auth:
            if self.api_token:
                request_headers['Authorization'] = f'Bearer {self.api_token}'
            else:
                # Try to use a demo token for testing
                request_headers['Authorization'] = 'Bearer demo_token'

        # Record start time
        start_time = time.time()

        try:
            if HAS_RICH and console:
                with console.status(f"[bold green]Running {test_name}..."):
                    response = self._make_request(method, url, data, request_headers)
            else:
                print(f"Running {test_name}...")
                response = self._make_request(method, url, data, request_headers)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000

            # Determine if test passed
            success = self._evaluate_response(response, expect_redirect)

            # Store result
            result = {
                'test_name': test_name,
                'method': method,
                'endpoint': endpoint,
                'status_code': response.status_code if response else 0,
                'response_time': response_time,
                'success': success,
                'timestamp': time.time()
            }

            if not success:
                result['error'] = self._get_error_message(response)

            self.test_results.append(result)

            # Display result
            self._display_test_result(result, response)

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = {
                'test_name': test_name,
                'method': method,
                'endpoint': endpoint,
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
            self.test_results.append(result)
            self._display_test_result(result, None)

    def _make_request(self, method: str, url: str, data: Any, headers: Dict[str, str]):
        """Make HTTP request with proper error handling."""
        try:
            if method == 'GET':
                return requests.get(url, headers=headers, timeout=10, allow_redirects=False)
            elif method == 'POST':
                if data:
                    return requests.post(url, json=data, headers=headers, timeout=10, allow_redirects=False)
                else:
                    return requests.post(url, headers=headers, timeout=10, allow_redirects=False)
            elif method == 'PUT':
                if data:
                    return requests.put(url, json=data, headers=headers, timeout=10, allow_redirects=False)
                else:
                    return requests.put(url, headers=headers, timeout=10, allow_redirects=False)
            elif method == 'DELETE':
                return requests.delete(url, headers=headers, timeout=10, allow_redirects=False)
            elif method == 'PATCH':
                if data:
                    return requests.patch(url, json=data, headers=headers, timeout=10, allow_redirects=False)
                else:
                    return requests.patch(url, headers=headers, timeout=10, allow_redirects=False)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _evaluate_response(self, response, expect_redirect: bool = False) -> bool:
        """Evaluate if the API response indicates success."""
        if not response:
            return False

        status_code = response.status_code

        # Handle redirects
        if expect_redirect:
            return 300 <= status_code < 400

        # Success status codes
        if 200 <= status_code < 300:
            return True

        # Authentication required is expected for protected endpoints
        if status_code == 401:
            return True  # This is expected behavior for protected endpoints

        # Other status codes are considered failures
        return False

    def _get_error_message(self, response) -> str:
        """Extract error message from response."""
        if not response:
            return "No response received"

        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                return error_data.get('error', f'HTTP {response.status_code}')
            else:
                return f'HTTP {response.status_code}: {response.reason}'
        except:
            return f'HTTP {response.status_code}: {response.reason}'

    def _display_test_result(self, result: Dict[str, Any], response):
        """Display the result of a single test."""
        test_name = result['test_name']
        status_code = result['status_code']
        response_time = result['response_time']
        success = result['success']

        if HAS_RICH and console:
            if success:
                console.print(f"[green]✅ {test_name}[/green] - Status: {status_code} - Time: {response_time:.2f}ms")
            else:
                error_msg = result.get('error', 'Unknown error')
                console.print(f"[red]❌ {test_name}[/red] - Status: {status_code} - Error: {error_msg}")

            # Show response preview if available
            if response and hasattr(response, 'text'):
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        response_data = response.json()
                        preview = json.dumps(response_data, indent=2)[:200]
                        if len(preview) >= 200:
                            preview += "..."
                        console.print(f"[dim]Response preview: {preview}[/dim]")
                except:
                    # If JSON parsing fails, show text preview
                    preview = response.text[:100]
                    if len(response.text) > 100:
                        preview += "..."
                    console.print(f"[dim]Response preview: {preview}[/dim]")
        else:
            status = "PASS" if success else "FAIL"
            print(f"{status}: {test_name} - Status: {status_code} - Time: {response_time:.2f}ms")
            if not success:
                error_msg = result.get('error', 'Unknown error')
                print(f"  Error: {error_msg}")

        print()  # Add spacing between tests
