# 📧 Gmail SMTP Setup Guide for Script Runner App

This guide explains how to configure Gmail SMTP to automatically send invitation emails to new users.

## 🎯 **Current vs New Behavior**

### **Before (Manual Process):**
1. ❌ Admin enters email in admin panel
2. ❌ System generates registration link 
3. ❌ **Admin must manually copy and send the link**
4. ❌ Pending invitations show raw URLs in admin panel

### **After (Automatic Email):**
1. ✅ Admin enters email in admin panel
2. ✅ System generates registration link
3. ✅ **System automatically sends beautiful HTML email**
4. ✅ User receives professional invitation email
5. ✅ Admin panel shows email status and backup copy function

## 🔧 **Gmail SMTP Configuration**

### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click **Security** in the left menu
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the setup process to enable 2FA

### **Step 2: Generate App Password**
1. In Google Account Security settings
2. Under "Signing in to Google", click **App passwords**
3. Select app: **Mail**
4. Select device: **Other (Custom name)**
5. Enter: **Script Runner App**
6. Click **Generate**
7. **Copy the 16-digit password** (you won't see it again!)

### **Step 3: Update Environment Variables**
Update your `.env` file with these settings:

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop  # 16-digit app password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Script Runner App
BASE_URL=http://localhost:8000

# Optional: Customize email appearance
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
```

### **Step 4: Restart Application**
```bash
# Stop the current server (Ctrl+C)
# Restart with new configuration
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📨 **What Users Receive**

Users will receive a professional HTML email with:

- 🎨 **Beautiful Design**: Modern styling with your app branding
- 🔐 **Clear Call-to-Action**: Prominent "Complete Registration" button
- 📋 **Step-by-Step Instructions**: What to do next
- ✨ **Feature Highlights**: Platform capabilities overview
- 🔗 **Backup Link**: Manual registration URL if button doesn't work
- 🛡️ **Security Notice**: One-time use token information

## 🖥️ **Admin Panel Features**

### **Email Configuration Section**
- Shows setup instructions
- Displays Gmail app password requirements
- Security best practices

### **Enhanced Invitation Management**
- **Send Email Invitation** button (instead of manual links)
- **Email Status**: Success/failure notifications
- **Backup Copy Function**: Click to copy registration link manually
- **Duplicate Prevention**: Checks for existing users/invitations

### **Improved Pending Invitations**
- Clean status display (no raw URLs)
- One-click link copying for manual backup
- Professional status badges

## 🔄 **Fallback Behavior**

If Gmail SMTP is **not configured** or **fails**:

1. ⚠️ System shows configuration warning
2. 🔗 Admin panel provides manual registration link
3. 📋 Admin can copy/paste link to send manually
4. 📧 Error message explains what went wrong

## 🧪 **Testing the Setup**

### **Test Email Configuration:**
```bash
# Run this to test your Gmail settings
python -c "
from app.email_service import email_service
success, message = email_service.test_connection()
print(message)
"
```

### **Send Test Invitation:**
1. Go to admin panel: `http://localhost:8000/admin`
2. Enter password: `admin123`
3. Enter your own email in "Invite User"
4. Click "Send Email Invitation"
5. Check your inbox for the invitation email

## 🔒 **Security Best Practices**

### **App Passwords vs Regular Passwords:**
- ✅ **App passwords** are more secure
- ✅ Can be **revoked independently**
- ✅ **Don't expire** when you change your main password
- ✅ **Limited scope** (only email access)

### **Environment Security:**
- 🔐 **Never commit** `.env` file to version control
- 🔐 Use **different credentials** for production
- 🔐 **Rotate app passwords** periodically
- 🔐 **Monitor email activity** in Google Account

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **"Authentication failed"**
- ❌ **Wrong email/password** → Check credentials
- ❌ **2FA not enabled** → Enable 2-factor authentication
- ❌ **Using regular password** → Use app password instead

#### **"Connection failed"**
- ❌ **Firewall blocking** → Check port 587
- ❌ **Network issues** → Try different network
- ❌ **Gmail SMTP disabled** → Contact IT department

#### **"Email not received"**
- ❌ **Spam folder** → Check recipient's spam
- ❌ **Wrong email address** → Verify recipient email
- ❌ **Corporate blocking** → Check email filters

### **Debug Information:**
Check the console output when starting the app:
```bash
✅ Gmail SMTP connection successful    # Working correctly
⚠️  Gmail SMTP not configured         # Need to set up .env
❌ Gmail SMTP configuration error     # Check credentials
```

## 📋 **Complete .env Example**

```bash
# FastAPI Script Runner App Configuration

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-make-it-very-long-and-random
ADMIN_PASSWORD=admin123

# Database
DATABASE_URL=sqlite:///./app.db

# Application
APP_NAME=Script Runner App
APP_VERSION=1.0.0

# Gmail SMTP Configuration
GMAIL_EMAIL=admin@yourcompany.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=admin@yourcompany.com
FROM_NAME=YourCompany Script Runner
BASE_URL=https://your-domain.com

# Optional overrides
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587

# File Management
CLEANUP_FILES_AFTER_EMAIL=true  # Auto-cleanup files after email (default: true)
```

## 🎉 **Benefits of Email Integration**

- 🚀 **Professional Experience**: Users get proper email invitations
- ⚡ **Faster Onboarding**: No manual copy/paste required
- 🎨 **Brand Consistency**: Customizable email templates
- 📊 **Better Tracking**: Know when emails are sent/failed
- 🔒 **Enhanced Security**: App passwords and audit trails
- 💼 **Enterprise Ready**: Scales for larger organizations

---

**Need Help?** Check the admin panel for live configuration status and setup instructions! 