"""
Verify Broker Assistant setup and configuration.
Checks that all services and dependencies are properly configured.
"""
import os
import sys
import requests
from time import sleep


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_status(message, status='info'):
    """Print colored status message."""
    if status == 'success':
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == 'error':
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")


def check_env_file():
    """Check if .env file exists and has required keys."""
    print("\n=== Checking Configuration ===")

    if not os.path.exists('.env'):
        print_status(".env file not found", 'error')
        print_status("Run: cp .env.example .env", 'info')
        return False

    print_status(".env file exists", 'success')

    # Check for critical keys
    required_keys = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'KAFKA_BOOTSTRAP_SERVERS'
    ]

    optional_keys = [
        'ANTHROPIC_API_KEY',
        'ALPHA_VANTAGE_API_KEY',
        'FINNHUB_API_KEY',
        'NEWS_API_KEY'
    ]

    with open('.env', 'r') as f:
        content = f.read()

    missing_required = []
    missing_optional = []

    for key in required_keys:
        if key not in content or f"{key}=" not in content:
            missing_required.append(key)

    for key in optional_keys:
        if key not in content or content.find(f"{key}=\n") != -1 or content.endswith(f"{key}="):
            missing_optional.append(key)

    if missing_required:
        print_status(f"Missing required keys: {', '.join(missing_required)}", 'error')
        return False

    if missing_optional:
        print_status(f"Missing optional API keys: {', '.join(missing_optional)}", 'warning')
        print_status("Some features may not work without API keys", 'warning')

    print_status("All required configuration keys present", 'success')
    return True


def check_docker_services():
    """Check if Docker services are running."""
    print("\n=== Checking Docker Services ===")

    try:
        import subprocess

        result = subprocess.run(
            ['docker-compose', 'ps', '--services', '--filter', 'status=running'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print_status("docker-compose not available or services not running", 'error')
            print_status("Run: docker-compose up", 'info')
            return False

        running_services = result.stdout.strip().split('\n')
        expected_services = ['app', 'db', 'redis', 'kafka', 'zookeeper']

        all_running = True
        for service in expected_services:
            if service in running_services:
                print_status(f"{service} is running", 'success')
            else:
                print_status(f"{service} is not running", 'error')
                all_running = False

        return all_running

    except FileNotFoundError:
        print_status("docker-compose not found", 'error')
        return False


def check_api_connectivity():
    """Check if Flask API is responding."""
    print("\n=== Checking API Connectivity ===")

    try:
        response = requests.get('http://localhost:5000/api/portfolio/positions?user_id=1', timeout=5)

        if response.status_code == 200:
            print_status("API is responding", 'success')
            return True
        else:
            print_status(f"API returned status code {response.status_code}", 'warning')
            return False

    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to API on http://localhost:5000", 'error')
        print_status("Make sure services are running: docker-compose up", 'info')
        return False
    except Exception as e:
        print_status(f"Error checking API: {str(e)}", 'error')
        return False


def check_database():
    """Check database connectivity."""
    print("\n=== Checking Database ===")

    try:
        response = requests.get('http://localhost:5000/api/portfolio/positions?user_id=1', timeout=5)

        if response.status_code == 200:
            print_status("Database is accessible", 'success')
            return True
        else:
            print_status("Database might have issues", 'warning')
            return False

    except Exception as e:
        print_status(f"Cannot verify database: {str(e)}", 'error')
        return False


def check_redis():
    """Check Redis connectivity."""
    print("\n=== Checking Redis ===")

    try:
        import subprocess

        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'redis', 'redis-cli', 'ping'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and 'PONG' in result.stdout:
            print_status("Redis is responding", 'success')
            return True
        else:
            print_status("Redis is not responding", 'error')
            return False

    except Exception as e:
        print_status(f"Cannot verify Redis: {str(e)}", 'warning')
        return False


def check_kafka():
    """Check Kafka connectivity."""
    print("\n=== Checking Kafka ===")

    try:
        import subprocess

        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'kafka', 'kafka-topics', '--bootstrap-server', 'localhost:9092', '--list'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print_status("Kafka is responding", 'success')
            return True
        else:
            print_status("Kafka is not responding", 'warning')
            print_status("Kafka may still be initializing (wait 20-30 seconds)", 'info')
            return False

    except Exception as e:
        print_status(f"Cannot verify Kafka: {str(e)}", 'warning')
        return False


def check_dependencies():
    """Check Python dependencies."""
    print("\n=== Checking Python Dependencies ===")

    required_packages = [
        'flask',
        'sqlalchemy',
        'redis',
        'kafka-python',
        'pandas',
        'numpy',
        'anthropic'
    ]

    try:
        import subprocess

        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'app', 'pip', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            installed = result.stdout.lower()
            missing = []

            for package in required_packages:
                if package.lower() not in installed:
                    missing.append(package)

            if missing:
                print_status(f"Missing packages: {', '.join(missing)}", 'error')
                return False
            else:
                print_status("All required packages installed", 'success')
                return True
        else:
            print_status("Cannot check dependencies", 'warning')
            return False

    except Exception as e:
        print_status(f"Cannot verify dependencies: {str(e)}", 'warning')
        return False


def run_verification():
    """Run all verification checks."""
    print("=" * 60)
    print("Broker Assistant Setup Verification")
    print("=" * 60)

    checks = [
        ("Configuration", check_env_file),
        ("Docker Services", check_docker_services),
        ("API Connectivity", check_api_connectivity),
        ("Database", check_database),
        ("Redis", check_redis),
        ("Kafka", check_kafka),
        ("Dependencies", check_dependencies)
    ]

    results = {}

    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_status(f"Error during {check_name} check: {str(e)}", 'error')
            results[check_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for check_name, result in results.items():
        status = 'success' if result else 'error'
        print_status(f"{check_name}: {'PASSED' if result else 'FAILED'}", status)

    print("\n" + "=" * 60)

    if passed == total:
        print_status(f"All checks passed! ({passed}/{total})", 'success')
        print_status("Broker Assistant is ready to use", 'success')
        print("\nNext steps:")
        print("  - Try the examples: docker-compose exec app python scripts/example_usage.py")
        print("  - Read the API docs: cat README.md")
        print("  - Check the Quick Start: cat QUICKSTART.md")
        return 0
    else:
        print_status(f"Some checks failed ({passed}/{total} passed)", 'error')
        print_status("Please fix the issues above before using Broker Assistant", 'error')
        return 1


if __name__ == '__main__':
    sys.exit(run_verification())
