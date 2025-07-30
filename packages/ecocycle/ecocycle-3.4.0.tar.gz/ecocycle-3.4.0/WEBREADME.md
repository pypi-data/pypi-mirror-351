# EcoCycle - Comprehensive Documentation

<p align="center">
    <img src="https://i.postimg.cc/T2qM7Z1T/Eco-Cycle-Logo-Rounded.png" width="200" />
</p>

<p align="center">
    <strong>Cycle into a greener tomorrow</strong><br>
    A comprehensive cycling activity tracker and environmental impact calculator
</p>

---

## 🏡 Home

EcoCycle is a feature-rich application designed to help cyclists track their activities, plan eco-friendly routes, calculate environmental impact, and engage with a community of environmentally conscious cyclists. Originally developed for the Lenovo and Intel EDUtech ASIA hackathon under the sustainable campus theme, EcoCycle has evolved into a comprehensive platform promoting cycling as a sustainable mode of transportation.

### Key Value Proposition
- **Environmental Impact**: Calculate and visualize your carbon footprint reduction through cycling
- **Smart Route Planning**: AI-powered route recommendations with weather integration
- **Comprehensive Tracking**: Detailed statistics, trip logging, and progress visualization
- **Community Engagement**: Social features, challenges, and achievements
- **Multi-Platform**: CLI, web interface, and mobile-friendly design

---

## 🚀 Getting Started

### Prerequisites and System Requirements
- **Python**: 3.8 or higher (3.11+ recommended)
- **Memory**: 4GB RAM minimum
- **Storage**: 500MB free disk space
- **Network**: Internet connection for weather data, AI features, and sync
- **Operating System**: Windows, macOS, or Linux

### Installation

#### Option 1: Using pip (Recommended)
```bash
pip install ecocycle
```

#### Option 2: From Source
```bash
git clone https://github.com/shirishpothi/ecocycle.git
cd ecocycle
pip install -r requirements.txt
```

#### Option 3: Using Poetry
```bash
git clone https://github.com/shirishpothi/ecocycle.git
cd ecocycle
poetry install
```

### Environment Configuration

1. **Create Environment File**: Copy `template.env` to `.env`
```bash
cp template.env .env
```

2. **Required Environment Variables**:
```bash
# Essential for session security
SESSION_SECRET_KEY=your_secure_random_key_here

# Email configuration (for verification and notifications)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# Optional API keys for enhanced features
GEMINI_API_KEY=your_gemini_api_key_for_ai_features
OPENWEATHERMAP_API_KEY=your_weather_api_key
GOOGLE_MAPS_API_KEY=your_maps_api_key
```

3. **Generate SESSION_SECRET_KEY**:
```python
import secrets
print(secrets.token_hex(32))
```

### Initial Setup and First-Time User Guidance

1. **Launch Application**:
```bash
python main.py
```

2. **First Run Setup**:
   - Automatic dependency checking and installation
   - Database initialization
   - User account creation or authentication
   - Profile setup (weight, preferences, etc.)

3. **Authentication Options**:
   - **Guest Mode**: Quick access with limited features
   - **Local Account**: Full functionality with local storage
   - **Google OAuth**: Enhanced features with cloud sync
   - **Developer Mode**: Advanced tools and diagnostics (password: `developer123`)

---

## ✨ Features

### Core Functionality
- **🚴 Trip Logging**: Record cycling trips with distance, duration, route data
- **📊 Statistics Dashboard**: Comprehensive analytics and progress tracking
- **📈 Data Visualization**: Charts, graphs, and progress reports
- **🌍 Carbon Footprint Calculator**: Environmental impact calculations
- **🌦️ Weather Integration**: Real-time weather data and cycling conditions
- **🗺️ Route Planning**: Basic and AI-powered route recommendations

### Advanced Features
- **🤖 AI-Powered Route Planning**: Gemini AI integration for intelligent route suggestions
- **📧 Email Verification System**: Secure 6-digit code verification
- **🔐 Two-Factor Authentication**: Enhanced security options
- **🏆 Social Gamification**: Achievements, challenges, and leaderboards
- **🔔 Notification System**: Email, SMS, and in-app notifications
- **📱 Web Interface**: Modern web dashboard with responsive design

### Developer and Admin Tools
- **🛠️ Developer Mode**: System diagnostics, performance monitoring, database management
- **📊 Performance Monitoring**: Real-time system health dashboard
- **💾 Backup & Restore**: Comprehensive data backup and recovery
- **📋 Health Monitoring**: System health checks and alerts
- **🔍 Log Analysis**: Detailed logging and debugging tools

### Data Management
- **💾 SQLite Database**: Local data storage with automatic backups
- **☁️ Google Sheets Integration**: Optional cloud synchronization
- **📤 Export Functionality**: CSV, JSON, PDF export options
- **🔄 Sync Service**: Cross-platform data synchronization

---

## 🌐 Hosting Options

### Local Development
```bash
python main.py
```

### Web Application
```bash
# Start web server
python web/web_app.py

# Access at http://localhost:5050
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t ecocycle .
docker run -p 5050:5050 ecocycle

# Or use Docker Compose
docker-compose up -d
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5050 web.web_app:app

# Environment variables for production
export SESSION_SECRET_KEY="your-production-secret"
export DEBUG=false
```

---

## 📖 Usage Guide

### Basic Trip Logging
1. Launch EcoCycle: `python main.py`
2. Select "Log a cycling trip" from main menu
3. Enter trip details:
   - Date (defaults to today)
   - Distance in kilometers
   - Duration in minutes
4. Review calculated metrics (speed, calories, CO2 saved)
5. Confirm to save

### AI Route Planning
1. Navigate to "Weather and route planning"
2. Select "AI-powered route recommendations"
3. Enter location and preferences
4. Review AI-generated route suggestions
5. Save favorite routes for future use

### Weather Integration
1. Access "Check weather forecast for cycling"
2. Enter location or use current location
3. View cycling-specific weather conditions
4. Get recommendations for optimal cycling times

### Data Visualization
1. Go to "View statistics"
2. Select "View detailed charts and graphs"
3. Choose visualization type:
   - Activity Summary Dashboard
   - Trip History Analysis
   - Carbon Savings Visualization
   - Progress Over Time

### Developer Tools Access
1. From main menu, select "Settings and preferences"
2. Choose "Developer Tools" (requires developer password)
3. Access advanced features:
   - System diagnostics
   - Performance monitoring
   - Database management
   - Backup operations

---

## 📝 Changelog

### Version 3.4.0 (Current)
- Enhanced AI route planning with Gemini integration
- Improved email verification system
- Advanced developer tools and monitoring
- Web interface improvements
- Performance optimizations

### Version 3.0.0
- Major architecture refactoring
- Modular design implementation
- Enhanced security features
- Comprehensive testing suite

### Version 2.5.0
- Google Sheets integration
- Social gamification features
- Notification system
- Data export functionality

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Missing dependencies
**Solution**: Run `python main.py` - automatic dependency management will install required packages

**Issue**: Email verification not working
**Solution**: Check email configuration in `.env` file and ensure app passwords are used for Gmail

**Issue**: AI features unavailable
**Solution**: Set `GEMINI_API_KEY` in environment variables and restart application

**Issue**: Database errors
**Solution**: Use developer tools to run database diagnostics and repair

**Issue**: Session persistence problems
**Solution**: Ensure `SESSION_SECRET_KEY` is set in environment variables

### Expected Warnings (Non-Critical)
- Rich library fallback warnings
- Optional module import warnings
- Box parameter issues with Rich fallbacks
- Admin panel attribute warnings

### Log Files
- `Logs/ecocycle.log`: General application logs
- `Logs/ecocycle_debug.log`: Detailed debug information
- `Logs/error.log`: Error tracking
- `Logs/performance.log`: Performance metrics

---

## ❓ FAQ

**Q: Is my data private and secure?**
A: Yes, all data is stored locally by default. Cloud sync is optional and uses secure authentication.

**Q: How accurate are the environmental calculations?**
A: Calculations use research-based formulas. CO2 savings are based on average car emissions, calories on cycling metabolic rates.

**Q: Can I use EcoCycle offline?**
A: Core features work offline. Weather, AI routes, and cloud sync require internet connectivity.

**Q: How do I back up my data?**
A: Use developer tools for comprehensive backups, or enable Google Sheets integration for automatic cloud backup.

**Q: What APIs does EcoCycle use?**
A: Optional APIs include Google Gemini (AI), OpenWeatherMap (weather), Google Maps (routing), and Google Sheets (sync).

**Q: Can I contribute to the project?**
A: Yes! EcoCycle is open source under Apache 2.0 license. See contributing guidelines in the repository.

---

## 📄 License

EcoCycle is licensed under the Apache License 2.0. This license allows for both personal and commercial use, modification, and distribution while requiring attribution and license inclusion.

**Key Points**:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ License and copyright notice required
- ⚠️ State changes if modified

Full license text available in [LICENSE.md](LICENSE.md).

---

## 🤝 Code of Conduct

EcoCycle is committed to providing a welcoming and inclusive environment for all contributors and users. Our community standards include:

- **Respectful Communication**: Treat all community members with respect and kindness
- **Inclusive Environment**: Welcome people of all backgrounds and experience levels
- **Constructive Feedback**: Provide helpful, actionable feedback
- **Professional Conduct**: Maintain professional standards in all interactions

**Reporting**: Issues can be reported to shirish.pothi.27@gmail.com

Full code of conduct available in [Code of Conduct.md](Code%20of%20Conduct.md).

---

## 📞 Contact & Support

### Primary Developer
**Shirish Pothi**
- Email: shirish.pothi.27@gmail.com
- GitHub: [@shirishpothi](https://github.com/shirishpothi)

### Development Team
- **Shirish Pothi** - Lead Developer
- **Ryan Eng** - Contributor
- **Ashlesha Sahoo** - Contributor  
- **Rochelle Joseph** - Contributor

*All from Nexus International School*

### Support Channels
- **GitHub Issues**: [Report bugs and request features](https://github.com/shirishpothi/ecocycle/issues)
- **Email Support**: Use the pre-formatted email link in the repository
- **Documentation**: [Comprehensive docs](https://rebrand.ly/ecocycle)
- **Live Demo**: [Try EcoCycle online](https://colab.research.google.com/drive/1RzraMhybgZHFUTL3HoQrAXEwq6j6H-xs?usp=sharing)

---

## 🔒 Security Policy

### Supported Versions
| Version | Supported |
|---------|-----------|
| 3.0+    | ✅ |
| 2.5     | ✅ |
| < 2.5   | ❌ |

### Reporting Security Vulnerabilities
1. **GitHub Issues**: [Create security issue](https://github.com/shirishpothi/ecocycle/issues)
2. **Direct Email**: Use the security reporting template in the repository
3. **Response Time**: Security issues are prioritized and addressed within 48 hours

### Security Features
- Secure session management with HMAC verification
- Password hashing using bcrypt
- Email verification with time-limited codes
- Two-factor authentication support
- Secure API key management
- Input validation and sanitization

**Important**: Always use the latest supported version for optimal security.

---

<p align="center">
    <strong>Thank you for using EcoCycle!</strong><br>
    <em>Together, we're cycling into a greener tomorrow. 🌱🚴‍♀️</em>
</p>

<p align="center">
    <a href="https://github.com/shirishpothi/ecocycle">
        <img alt="GitHub" src="https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github">
    </a>
    <a href="https://pypi.org/project/ecocycle/">
        <img alt="PyPI" src="https://img.shields.io/badge/PyPI-Package-orange?style=for-the-badge&logo=pypi">
    </a>
    <a href="https://rebrand.ly/ecocycle">
        <img alt="Documentation" src="https://img.shields.io/badge/Documentation-Online-green?style=for-the-badge&logo=bookstack">
    </a>
</p>
