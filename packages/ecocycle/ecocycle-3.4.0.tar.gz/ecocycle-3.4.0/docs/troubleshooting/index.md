# EcoCycle Troubleshooting Guide

This guide helps you diagnose and resolve common issues you might encounter while using EcoCycle. Find your specific issue below for step-by-step solutions.

## Installation Issues

### Application Fails to Install

**Symptoms:**
- Installation process stops unexpectedly
- Error messages during installation
- Application not appearing after installation

**Solutions:**

1. **Check System Requirements**
   - Verify you have Python 3.8 or higher installed
   - Ensure you have at least 500MB of free disk space
   - Confirm your operating system is supported (Windows 10+, macOS 10.14+, or Ubuntu 18.04+)

2. **Permission Issues**
   - Run the installer with administrator privileges
   - Check if your antivirus is blocking the installation
   - Ensure you have write permissions to the installation directory

3. **Dependency Problems**
   - Try reinstalling with `pip install ecocycle --force-reinstall --no-cache-dir`
   - If specific package errors appear, install those packages manually first
   - Update pip with `pip install --upgrade pip` before installing

4. **Clean Installation**
   - Remove any previous installation attempts
   - Clear pip cache with `pip cache purge`
   - Restart your computer and try again

### Application Won't Start

**Symptoms:**
- Application crashes immediately after launching
- Application freezes on the splash screen
- Nothing happens when trying to launch

**Solutions:**

1. **Check Error Logs**
   - Look in the `Logs` folder for error messages
   - Run from command line to see console output: `python -m ecocycle`

2. **Configuration Problems**
   - Rename or remove the configuration file in `~/.ecocycle/son`
   - Application will create a new default configuration file

3. **Database Issues**
   - Try restoring from a backup in `db/backups`
   - If no backup, rename the database file and let the application create a new one

4. **Full Reset**
   - Uninstall the application completely
   - Remove all data files in the application directory
   - Reinstall from scratch
   - Note: This will result in data loss if not backed up

## Account and Authentication Problems

### Can't Log In

**Symptoms:**
- Invalid username/password errors despite correct credentials
- Endless login loop
- Authentication server connection errors

**Solutions:**

1. **Reset Password**
   - Use the "Forgot Password" function to reset your credentials
   - Check your email (including spam folder) for the reset link

2. **Account Locked**
   - Wait 30 minutes if you've had too many failed attempts
   - Contact support if you believe your account was locked erroneously

3. **OAuth Issues**
   - Try the standard username/password method instead of Google login
   - Clear browser cookies and cache if using the web version
   - Check if your Google account has two-factor authentication issues

4. **Connection Problems**
   - Verify your internet connection
   - Try using a different network (mobile data instead of Wi-Fi)
   - Check if ecocycle.org is accessible in your browser

### Sync Issues Between Devices

**Symptoms:**
- Data not appearing on all devices
- Conflicts between different versions of data
- Sync appearing to start but never completing

**Solutions:**

1. **Force Manual Sync**
   - Go to Settings > Sync > Force Full Sync on each device
   - This will reconcile differences but may take longer than normal sync

2. **Check Account Status**
   - Verify you're logged into the same account on all devices
   - Check if any device is in offline mode

3. **Clear Sync Cache**
   - Go to Settings > Advanced > Clear Sync Cache
   - Restart the application and perform a full sync

4. **Resolve Conflicts**
   - If prompted about conflicts, choose "Keep Both" to avoid data loss
   - Later, manually review and clean up duplicates

## Data and Performance Issues

### Slow Application Performance

**Symptoms:**
- Menus take a long time to open
- Maps render slowly
- General sluggishness throughout the app

**Solutions:**

1. **Check Resources**
   - Verify your system has sufficient free RAM and CPU
   - Close other resource-intensive applications
   - Restart the application and/or your computer

2. **Optimize Data**
   - Go to Settings > Data > Optimize Database
   - Consider archiving old activities (Settings > Data > Archive)

3. **Reduce Graphics Settings**
   - Go to Settings > Display > Performance Mode
   - Disable high-resolution maps and animations

4. **Clear Caches**
   - Go to Settings > Advanced > Clear All Caches
   - This removes temporary data but preserves your actual cycling data

### Data Loss or Corruption

**Symptoms:**
- Missing activities or routes
- Garbled text or incorrect values
- Application crashes when accessing specific data

**Solutions:**

1. **Restore from Backup**
   - Go to Settings > Data > Restore from Backup
   - Choose the most recent backup before the issue occurred

2. **Repair Database**
   - Go to Settings > Advanced > Repair Database
   - Follow the prompts to attempt automatic repair

3. **Import from Export**
   - If you previously exported your data, try importing it
   - Go to Settings > Data > Import

4. **Partial Recovery**
   - If full recovery isn't possible, try importing just essential data
   - Go to Settings > Data > Selective Import

## GPS and Activity Tracking Issues

### Inaccurate GPS Tracking

**Symptoms:**
- Routes showing incorrect paths
- Jumps or gaps in tracked routes
- Speed or distance calculations seem wrong

**Solutions:**

1. **Improve GPS Signal**
   - Ensure your device has a clear view of the sky
   - Keep your device in an exposed position (handlebar mount)
   - Wait for GPS to fully initialize before starting

2. **Calibrate GPS**
   - Go to Settings > GPS > Calibrate
   - Stand in an open area during calibration

3. **Adjust Tracking Settings**
   - Go to Settings > Tracking > GPS Accuracy
   - Higher accuracy uses more battery but improves tracking
   - Enable "Smart Recording" to filter out GPS noise

4. **Hardware Issues**
   - Try using an external GPS device if your device's GPS is faulty
   - Update your device's operating system and location services

### Activity Not Saving

**Symptoms:**
- Activity disappears after completion
- Error message when trying to save
- Application crashes during save process

**Solutions:**

1. **Recovery From Temporary Storage**
   - Go to Settings > Recovery > Unsaved Activities
   - Look for auto-saved versions of your activity

2. **Check Storage Space**
   - Ensure your device has sufficient free storage
   - Clear unnecessary files if storage is low

3. **File Permission Issues**
   - Verify the application has permission to write to storage
   - Check system settings for restricted permissions

4. **Manual Data Entry**
   - If recovery isn't possible, manually recreate essential activities
   - Go to Activities > Add Manually

## Feature-Specific Issues

### Route Planning Problems

**Symptoms:**
- Cannot create or modify routes
- Routes calculate incorrectly
- Map displays incorrectly

**Solutions:**

1. **Map Data Issues**
   - Go to Settings > Maps > Update Map Data
   - Try switching to a different map provider

2. **Route Calculation**
   - Check your routing preferences (Settings > Routes)
   - Try different routing algorithms (fastest, shortest, safest)

3. **Clear Route Cache**
   - Go to Settings > Advanced > Clear Route Cache
   - Force reload the map tiles

4. **Connection Issues**
   - Verify your internet connection for online maps
   - Try using offline maps if online services are unavailable

### Challenge and Goal Issues

**Symptoms:**
- Challenge progress not updating
- Cannot join or create challenges
- Goals showing incorrect completion status

**Solutions:**

1. **Refresh Challenge Data**
   - Go to Challenges > Refresh
   - Force a data sync with the server

2. **Check Eligibility**
   - Verify you meet all requirements for the challenge
   - Check if the challenge has expired

3. **Goal Calculation Fix**
   - Go to Settings > Goals > Recalculate All
   - This forces a fresh calculation of all goal progress

4. **Join Issues**
   - Try joining via invitation link instead of code, or vice versa
   - Check if the challenge has reached its participant limit

## Web and Mobile-Specific Issues

### Web Interface Problems

**Symptoms:**
- Pages not loading properly
- Features missing from the web version
- Display issues or visual glitches

**Solutions:**

1. **Browser Compatibility**
   - Try a different browser (Chrome, Firefox, Edge are best supported)
   - Ensure your browser is updated to the latest version

2. **Clear Browser Data**
   - Clear cache and cookies for the EcoCycle website
   - Try using incognito/private browsing mode

3. **Plugin Conflicts**
   - Disable browser extensions, especially ad blockers or privacy tools
   - Test if the issue persists

4. **Display Settings**
   - Try adjusting zoom level (Ctrl+/Ctrl-)
   - Check if browser has site-specific display settings

### Mobile App Issues

**Symptoms:**
- App crashes frequently
- Features not working as expected
- Performance problems or battery drain

**Solutions:**

1. **Update the App**
   - Ensure you have the latest version from the app store
   - Enable auto-updates for future fixes

2. **Permission Issues**
   - Check if the app has all required permissions
   - Especially location, storage, and network permissions

3. **Clear App Cache**
   - Go to your device's Settings > Apps > EcoCycle > Storage
   - Clear Cache (not data, unless you want to reset everything)

4. **Reinstall**
   - Uninstall and reinstall the app
   - Note: Ensure your data is synced to the cloud first

## Still Need Help?

If you've tried the solutions above and are still experiencing issues:

1. **Check the Knowledge Base**
   - Search our [Knowledge Base](../knowledge_base/index.md) for detailed articles
   - Many specific issues have dedicated troubleshooting guides

2. **Community Support**
   - Post in the [Community Forum](https://ecocycle.org/forum/help)
   - Other users may have encountered and solved similar issues

3. **Contact Support**
   - Submit a detailed support ticket with:
     - Your system information
     - Steps to reproduce the issue
     - Screenshots or error messages
     - Log files from the `Logs` directory

4. **Live Chat**
   - For Premium users, live chat support is available
   - Access through Help > Live Support in the application

## Generating Diagnostic Information

When contacting support, it's helpful to include diagnostic information:

1. Go to Help > Generate Diagnostics in the application
2. Wait for the diagnostic report to be created
3. Find the report file in your Documents folder
4. Attach this file when contacting support

This file contains system information, application logs, and other useful troubleshooting data without including your personal cycling data.
