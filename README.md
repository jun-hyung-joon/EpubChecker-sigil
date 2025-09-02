# EpubChecker-sigil

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/jun-hyung-joon/EpubChecker-sigil)
[![Sigil](https://img.shields.io/badge/Sigil-1.0%2B-blue)](https://sigil-ebook.com/)

A Sigil plugin that validates EPUB files using epubcheck, providing detailed error reports and warnings directly within the Sigil editor. The plugin automatically detects and uses the latest installed version of epubcheck, ensuring you're always validating with the most up-to-date standards.

## Installation

### 1. Install epubcheck

**Option A: Package Manager (Recommended)**
```bash
# Windows (Chocolatey)
choco install epubcheck

# macOS (Homebrew)
brew install epubcheck

# Linux (varies by distribution)
sudo apt install epubcheck  # Ubuntu/Debian
```

**Option B: Manual Installation**
1. Download `epubcheck.jar` from [epubcheck releases](https://github.com/w3c/epubcheck/releases)
2. Save it to your Desktop or Downloads folder

### 2. Install Java (if not already installed)

```bash
# Windows
choco install openjdk

# macOS
brew install openjdk

# Linux
sudo apt install openjdk-11-jdk  # Ubuntu/Debian
```

### 3. Install the Sigil Plugin

1. Download the latest `EpubChecker.zip` from [releases](https://github.com/jun-hyung-joon/EpubChecker-sigil-plugin/releases)
2. In Sigil, go to **Plugins** → **Manage Plugins**
3. Click **Add Plugin** and select the downloaded file

## Usage

1. Open your EPUB project in Sigil
2. Go to **Plugins** → **EpubChecker**
3. The plugin will:
   - Check for epubcheck installation
   - Automatically detect the latest installed epubcheck version
   - Generate a temporary EPUB file
   - Run validation using the newest available epubcheck
   - Display detailed results

> **Note**: When you update epubcheck to a newer version, the plugin will automatically use the latest version without requiring any configuration changes.

### Sample Output

```
🔍 Starting EPUB validation
============================================================
🔧 Checking epubcheck installation...
✅ epubcheck found: epubcheck v5.1.0
📖 Preparing current EPUB file...
📦 EPUB created: MyBook.epub (size: 1,234,567 bytes)
🔍 Running validation...
📄 epubcheck processing completed

📊 Validation Results
============================================================
Total messages: 3
Fatal warnings: 0 💥
Errors: 1 ❌
Warnings: 2 ⚠️
Info: 0 ℹ️

❌ Errors Found:
------------------------------------------------------------
📋 Error Code: RSC-005
📄 Error Content: Element "title" must not be empty.
📍 Error Location:
   1. File: OEBPS/Text/Chapter01.xhtml (line 6, column 10)
```

## Supported Environments

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 11 | ✅ | Supports Chocolatey and manual installation |
| macOS | ✅ | Intel and Apple Silicon, Homebrew support |
| Linux | ✅ | Most distributions with Java support |


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **[epubcheck](https://github.com/w3c/epubcheck)** - The official EPUB validation tool by W3C. This plugin is a wrapper that integrates epubcheck into Sigil.
- [Sigil](https://sigil-ebook.com/) - The amazing EPUB editor

## Dependencies

This plugin requires and integrates with:
- **[epubcheck](https://github.com/w3c/epubcheck)** (BSD 3-Clause License) - Official EPUB validation tool
- **Java Runtime Environment** - Required to run epubcheck

## Legal Notice

This plugin is a third-party integration tool and is not affiliated with or endorsed by the W3C or the epubcheck project. epubcheck is developed and maintained by the W3C and is licensed under the BSD 3-Clause License.
