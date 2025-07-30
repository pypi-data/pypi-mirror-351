#!/usr/bin/env python3
"""
EcoCycle - Setup Script
This script is used to package the EcoCycle application.
"""
from setuptools import setup, find_packages
import os
import re

# Read the version from config/config.py
with open(os.path.join('config', 'config.py'), 'r') as f:
    content = f.read()
    version_match = re.search(r"VERSION\s*=\s*['\"]([^'\"]+)['\"]", content)
    if version_match:
        version = version_match.group(1)
    else:
        version = '0.0.0'

# Read the README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='ecocycle',
    version=version,
    description='EcoCycle - Sustainable Transportation Tracker and Route Planner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Shirish Pothi',
    author_email='shirish.pothi.27@gmail.com',
    url='https://github.com/shirishpothi/ecocycle',
    project_urls={
        'Documentation': 'https://rebrand.ly/ecocycle',
        'Source': 'https://github.com/shirishpothi/ecocycle',
        'Tracker': 'https://github.com/shirishpothi/ecocycle/issues',
    },
    packages=find_packages(exclude=['Tests*', 'Demo Modules*', 'backups*', 'temp*']),
    include_package_data=True,
    install_requires=[
        'colorama>=0.4.6',
        'python-dotenv>=1.0.1',
        'tqdm>=4.66.1',
        'rich>=14.0.0',
        'termcolor>=2.3.0',
        'blessed>=1.20.0',
        'yaspin>=3.0.1',
        'packaging>=23.0.0',
        'setuptools>=78.1.0',
        'requests>=2.32.3',
        'cryptography>=44.0.1',
        'bcrypt>=4.1.3',
        'psutil>=5.9.0',
    ],
    extras_require={
        'visualization': [
            'matplotlib>=3.7.0',
            'numpy>=2.2.4',
            'plotly>=5.14.0',
        ],
        'route_planning': [
            'folium>=0.14.0',
            'requests>=2.32.3',
        ],
        'data_export': [
            'fpdf>=1.7.2',
            'tabulate>=0.9.0',
        ],
        'social_sharing': [
            'pillow>=10.0.0',
            'qrcode>=7.4.0',
        ],
        'notifications': [
            'sendgrid>=6.10.0',
            'twilio>=8.5.0',
            'yagmail>=0.15.293',
        ],
        'sheets_integration': [
            'google-api-python-client>=2.149.0',
            'google-auth-httplib2>=0.2.0',
            'google-auth-oauthlib>=1.0.0',
            'google-auth>=2.35.0',
            'oauthlib>=3.2.2',
        ],
        'ai_features': [
            'openai>=1.74.0',
            'google-generativeai>=0.8.4',
        ],
        'weather': [
            'weatherapi>=0.0.4',
        ],
        'web': [
            'flask>=3.1.0',
            'flask-cors>=5.0.0',
            'werkzeug>=3.0.0',
            'gunicorn>=21.0.0',
            'eventlet>=0.33.0',
            'flask-socketio>=5.3.0',
        ],
        'dev': [
            'pytest>=7.4.0',
            'pytest-mock>=3.11.1',
            'pytest-cov>=4.1.0',
            'pytest-benchmark>=4.0.0',
            'pytest-xdist>=3.5.0',
            'black>=23.7.0',
            'mypy>=1.5.1',
            'flake8>=6.1.0',
            'isort>=5.13.2',
            'pre-commit>=3.6.0',
            'bandit>=1.7.7',
            'ruff>=0.1.6',
        ],
        'all': [
            'matplotlib>=3.7.0', 'numpy>=2.2.4', 'plotly>=5.14.0',
            'folium>=0.14.0', 'fpdf>=1.7.2', 'tabulate>=0.9.0',
            'pillow>=10.0.0', 'qrcode>=7.4.0', 'sendgrid>=6.10.0',
            'twilio>=8.5.0', 'yagmail>=0.15.293', 'google-api-python-client>=2.149.0',
            'google-auth-httplib2>=0.2.0', 'google-auth-oauthlib>=1.0.0',
            'google-auth>=2.35.0', 'oauthlib>=3.2.2', 'openai>=1.74.0',
            'google-generativeai>=0.8.4', 'weatherapi>=0.0.4', 'flask>=3.1.0',
            'flask-cors>=5.0.0', 'werkzeug>=3.0.0', 'gunicorn>=21.0.0',
            'eventlet>=0.33.0', 'flask-socketio>=5.3.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='cycling sustainability eco-friendly route-planning carbon-footprint transportation',
    python_requires='>=3.11',
    entry_points={
        'console_scripts': [
            'ecocycle=cli:main',
            'eco=cli:main',
        ],
    },
    zip_safe=False,
)
