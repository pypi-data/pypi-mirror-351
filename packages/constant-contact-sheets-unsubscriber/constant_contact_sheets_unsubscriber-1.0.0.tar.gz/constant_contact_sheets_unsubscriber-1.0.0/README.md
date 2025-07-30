# Constant Contact Google Sheets Unsubscriber

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for automatically unsubscribing emails from Constant Contact using Google Sheets as the data source. Perfect for automating email list management and compliance.

## ✨ Features

- 🔄 **Real-time monitoring** of Google Sheets for new emails
- 📊 **Smart tracking** - only processes new emails, ignores already processed ones
- 📝 **Comprehensive logging** with timestamps
- 🔧 **PM2 support** for production deployment
- 🛡️ **Rate limiting** to respect API limits
- ⚙️ **Configurable** via environment variables
- 🚀 **Easy installation** via pip

## 📦 Installation

```bash
pip install constant-contact-sheets-unsubscriber
```

## 🔧 Quick Setup

### 1. Constant Contact API Setup

1. Create a developer account at [Constant Contact Developer Portal](https://developer.constantcontact.com/)
2. Create an API application to get your credentials
3. Generate access and refresh tokens

### 2. Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API
4. Create a Service Account and download the credentials JSON file
5. Share your Google Spreadsheet with the service account email

### 3. Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables:

```bash
CONSTANT_CONTACT_API_KEY=your_api_key
CONSTANT_CONTACT_ACCESS_TOKEN=your_access_token
CONSTANT_CONTACT_REFRESH_TOKEN=your_refresh_token
CONSTANT_CONTACT_CLIENT_SECRET=your_client_secret
CONSTANT_CONTACT_REDIRECT_URI=https://localhost
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 🚀 Usage

### Command Line Interface

```bash
# Initialize - mark all existing emails as processed (first run only)
cc-unsubscriber --spreadsheet-id "your_sheet_id" --range "Sheet1!B:B" --initialize

# Process new emails
cc-unsubscriber --spreadsheet-id "your_sheet_id" --range "Sheet1!B:B"

# Start continuous monitoring
cc-monitor --spreadsheet-id "your_sheet_id" --range "Sheet1!B:B"
```

### Python API

```python
from constant_contact_unsubscriber import ConstantContactUnsubscriber, Config

# Initialize configuration
config = Config()

# Create unsubscriber instance
unsubscriber = ConstantContactUnsubscriber(config)

# Process emails from Google Sheets
unsubscriber.process_sheet(
    spreadsheet_id="your_spreadsheet_id",
    range_name="Sheet1!B:B",
    initialize_mode=False  # Set to True for first run
)
```

## 📊 Google Sheets Format

Your Google Spreadsheet should have emails in a single column:

| A    | B (Email Address) | C     |
| ---- | ----------------- | ----- |
| Date | user1@example.com | Notes |
| Date | user2@example.com | Notes |
| Date | user3@example.com | Notes |

- **Column B**: Email addresses to unsubscribe
- **Range**: Use `Sheet1!B:B` to read all emails from column B

## 🔄 Production Deployment

### With PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start the monitor
pm2 start cc-monitor --name "unsubscribe-monitor" -- --spreadsheet-id "your_id" --range "Sheet1!B:B"

# Save PM2 configuration
pm2 save
pm2 startup
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["cc-monitor", "--spreadsheet-id", "your_id", "--range", "Sheet1!B:B"]
```

## 📈 Monitoring

The package creates several files for tracking and logging:

- `processed_emails.json` - Tracks which emails have been processed
- `unsubscribe_success_log.txt` - Log of successful unsubscribes with timestamps
- Application logs via Python logging module

### Monitoring Commands

```bash
# Check total unsubscribes
wc -l unsubscribe_success_log.txt

# View recent activity
tail -f unsubscribe_success_log.txt

# Check processed count
python -c "import json; print(f'Processed: {len(json.load(open(\"processed_emails.json\")))}')"
```

## ⚙️ Configuration Options

| Environment Variable      | Default                       | Description                  |
| ------------------------- | ----------------------------- | ---------------------------- |
| `RATE_LIMIT_SECONDS`      | 5                             | Seconds between API requests |
| `CHECK_INTERVAL_SECONDS`  | 300                           | Seconds between sheet checks |
| `PROCESSED_EMAILS_FILE`   | `processed_emails.json`       | Tracking file path           |
| `SUCCESS_LOG_FILE`        | `unsubscribe_success_log.txt` | Success log path             |
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json`            | Google API credentials       |

## 🔒 Security

- All sensitive credentials are stored in environment variables
- Google Service Account uses minimal required permissions
- Rate limiting prevents API abuse
- No sensitive data is logged or tracked in version control

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'dotenv'"**

```bash
pip install python-dotenv
```

**"Error: CONSTANT_CONTACT_API_KEY not found"**

- Check your `.env` file exists and has the correct variables
- Ensure the `.env` file is in your working directory

**"Permission denied" for Google Sheets**

- Verify the service account email has access to your spreadsheet
- Check the `credentials.json` file exists and is valid

**"Contact not found" for all emails**

- Verify emails exist in your Constant Contact account
- Check API credentials are correct and have proper permissions

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
cc-unsubscriber --spreadsheet-id "your_id" --range "Sheet1!B:B"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Constant Contact API](https://developer.constantcontact.com/) for email management
- [Google Sheets API](https://developers.google.com/sheets/api) for spreadsheet integration
- Built with Python and love ❤️

## 📞 Support

- 📋 [Issue Tracker](https://github.com/yourusername/constant-contact-sheets-unsubscriber/issues)
- 📖 [Documentation](https://github.com/yourusername/constant-contact-sheets-unsubscriber#readme)
- 💬 [Discussions](https://github.com/yourusername/constant-contact-sheets-unsubscriber/discussions)
