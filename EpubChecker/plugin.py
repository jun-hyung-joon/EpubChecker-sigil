#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sigil EPUB Checker Plugin
Plugin for validating EPUB files using epubcheck
"""

import sys
import os
import tempfile
import subprocess
import json
import zipfile
import platform
import glob
import re

def run(bk):
    """Main function for Sigil plugin"""
    try:
        print("=" * 60)
        print("🔍 Starting EPUB validation")
        print("=" * 60)
        
        # Check epubcheck installation
        tool_info = check_tool_installation()
        if not tool_info:
            print_installation_guide()
            return -1
        
        # Create EPUB file
        print("📖 Preparing current EPUB file...")
        epub_path = create_temp_epub(bk)
        
        try:
            # Run validation
            print("🔍 Running validation...")
            result = run_epubcheck(tool_info, epub_path)
            
            # Display results
            display_results(result)
            
        finally:
            try:
                os.unlink(epub_path)
            except:
                pass
        
        print("=" * 60)
        print("✅ Validation completed")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return -1

def check_java_installation():
    """Check Java installation and return path"""
    # Check PATH
    for java_cmd in ['java', 'java.exe']:
        try:
            result = subprocess.run([java_cmd, '-version'], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return java_cmd
        except:
            continue
    
    # Check common installation paths
    java_patterns = [
        'C:\\Program Files\\OpenJDK\\*\\bin\\java.exe',
        'C:\\Program Files\\Java\\*\\bin\\java.exe',
        'C:\\ProgramData\\chocolatey\\lib\\openjdk*\\tools\\*\\bin\\java.exe'
    ]
    
    for pattern in java_patterns:
        for java_path in glob.glob(pattern):
            if os.path.exists(java_path):
                try:
                    result = subprocess.run([java_path, '-version'], 
                                           capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return java_path
                except:
                    continue
    
    return None

def find_epubcheck_executable():
    """Find epubcheck executable or JAR file"""
    system = platform.system().lower()
    
    # Search for JAR files with improved patterns
    jar_locations = []
    if system == 'windows':
        jar_locations = [
            'C:\\ProgramData\\chocolatey\\lib\\epubcheck\\tools\\epubcheck-*\\epubcheck.jar',
            'C:\\Program Files\\epubcheck\\epubcheck.jar',
            os.path.expanduser('~\\Desktop\\epubcheck.jar'),
            os.path.expanduser('~\\Downloads\\epubcheck.jar'),
            'epubcheck.jar'
        ]
    else:
        # Mac and Linux paths
        jar_locations = [
            '/usr/local/bin/epubcheck.jar',
            '/usr/local/lib/epubcheck/epubcheck.jar',
            '/usr/local/lib/epubcheck-*/epubcheck.jar',
            '/opt/homebrew/lib/epubcheck/epubcheck.jar',  # Homebrew on Apple Silicon
            '/opt/homebrew/bin/epubcheck.jar',
            '/usr/local/Cellar/epubcheck/*/libexec/epubcheck.jar',  # Homebrew Intel
            '/opt/homebrew/Cellar/epubcheck/*/libexec/epubcheck.jar',  # Homebrew Apple Silicon
            os.path.expanduser('~/Desktop/epubcheck.jar'),
            os.path.expanduser('~/Downloads/epubcheck.jar'),
            os.path.expanduser('~/Applications/epubcheck.jar'),
            'epubcheck.jar'
        ]
    
    java_cmd = check_java_installation()
    
    # Find JAR files using glob patterns
    for jar_pattern in jar_locations:
        jar_files = glob.glob(jar_pattern)
        for jar_path in jar_files:
            if os.path.exists(jar_path) and java_cmd:
                return ('jar', jar_path, java_cmd)
    
    # Search for executable files
    exe_locations = []
    if system == 'windows':
        exe_locations = ['C:\\ProgramData\\chocolatey\\bin\\epubcheck.exe']
    else:
        # Mac and Linux executable paths
        exe_locations = [
            '/usr/local/bin/epubcheck', 
            '/usr/bin/epubcheck',
            '/opt/homebrew/bin/epubcheck',  # Homebrew on Apple Silicon
            '/usr/local/Cellar/epubcheck/*/bin/epubcheck',  # Homebrew Intel
            '/opt/homebrew/Cellar/epubcheck/*/bin/epubcheck'  # Homebrew Apple Silicon
        ]
    
    for exe_pattern in exe_locations:
        exe_files = glob.glob(exe_pattern)
        for exe_path in exe_files:
            if os.path.exists(exe_path):
                return ('exe', exe_path, None)
    
    return None

def check_tool_installation():
    """Check epubcheck installation status"""
    print("🔧 Checking epubcheck installation...")
    
    tool_info = find_epubcheck_executable()
    if not tool_info:
        print("❌ epubcheck is not installed.")
        return None
    
    tool_type, tool_path, java_cmd = tool_info
    
    try:
        if tool_type == 'jar' and java_cmd:
            result = subprocess.run([java_cmd, '-jar', tool_path, '--version'], 
                                   capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run([tool_path, '--version'], 
                                   capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            version_info = result.stdout.strip() or result.stderr.strip()
            print(f"✅ epubcheck found: {version_info}")
            return tool_info
    except Exception as e:
        print(f"Error running epubcheck: {str(e)}")
    
    return None

def print_installation_guide():
    """Print installation guide"""
    java_cmd = check_java_installation()
    if java_cmd:
        print("✅ Java is installed.")
    else:
        print("❌ Java is not installed!")
        system = platform.system().lower()
        if system == 'darwin':  # Mac
            print("Install Java: brew install openjdk")
        else:
            print("Install Java: choco install openjdk")
        print()
    
    print("epubcheck installation methods:")
    system = platform.system().lower()
    if system == 'darwin':  # Mac
        print("1. brew install epubcheck")
        print("2. https://github.com/w3c/epubcheck/releases")
        print("3. Save epubcheck.jar to Desktop")
    else:
        print("1. https://github.com/w3c/epubcheck/releases")
        print("2. Save epubcheck.jar to Desktop")
        print("3. Or use: choco install epubcheck")

def create_temp_epub(bk):
    """Create temporary EPUB file from current document"""
    try:
        epub_title = bk.getmetadatavalue('title') or "Current_EPUB"
        epub_title = re.sub(r'[<>:"/\\|?*]', '_', epub_title)
    except:
        epub_title = "Current_EPUB"
    
    epub_path = os.path.join(tempfile.gettempdir(), f"{epub_title}.epub")
    
    try:
        if os.path.exists(epub_path):
            os.unlink(epub_path)
    except:
        pass
    
    try:
        with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # mimetype
            zipf.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
            
            # Track added files
            added_files = {'mimetype'}
            
            # Check if container.xml already exists
            has_container = False
            for book_href in bk.other_iter():
                if book_href == 'META-INF/container.xml':
                    has_container = True
                    break
            
            # Handle container.xml
            if not has_container:
                container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
                zipf.writestr('META-INF/container.xml', container_xml)
                added_files.add('META-INF/container.xml')
            
            # OPF file
            zipf.writestr('OEBPS/content.opf', bk.get_opf())
            added_files.add('OEBPS/content.opf')
            
            # NCX file
            ncx_data = None
            try:
                ncx_data = bk.get_ncx()
                if ncx_data:
                    zipf.writestr('OEBPS/toc.ncx', ncx_data)
                    added_files.add('OEBPS/toc.ncx')
            except:
                pass
            
            # Manifest files
            for (file_id, href, mime_type) in bk.manifest_iter():
                try:
                    zip_path = f'OEBPS/{href}'
                    if zip_path in added_files:
                        continue
                    
                    file_data = bk.readfile(file_id)
                    if isinstance(file_data, str):
                        file_data = file_data.encode('utf-8')
                    
                    zipf.writestr(zip_path, file_data)
                    added_files.add(zip_path)
                except Exception as e:
                    print(f"⚠️ Failed to add manifest file: {href} - {str(e)}")
                    continue
            
            # Other files
            for book_href in bk.other_iter():
                try:
                    if book_href in added_files:
                        continue
                    
                    file_data = bk.readotherfile(book_href)
                    if isinstance(file_data, str):
                        file_data = file_data.encode('utf-8')
                    
                    zipf.writestr(book_href, file_data)
                    added_files.add(book_href)
                except Exception as e:
                    print(f"⚠️ Failed to add other file: {book_href} - {str(e)}")
                    continue
        
        file_size = os.path.getsize(epub_path)
        print(f"📦 EPUB created: {epub_title}.epub (size: {file_size:,} bytes)")
        return epub_path
        
    except Exception as e:
        try:
            os.unlink(epub_path)
        except:
            pass
        raise Exception(f"Failed to create EPUB file: {str(e)}")

def run_epubcheck(tool_info, epub_path):
    """Run epubcheck validation"""
    tool_type, tool_path, java_cmd = tool_info
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            json_output = os.path.join(temp_dir, 'result.json')
            
            if tool_type == 'jar' and java_cmd:
                cmd = [java_cmd, '-jar', tool_path, epub_path, '--json', json_output]
            else:
                cmd = [tool_path, epub_path, '--json', json_output]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                print("📄 epubcheck processing completed")
            
            if os.path.exists(json_output):
                with open(json_output, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
                
        except subprocess.TimeoutExpired:
            raise Exception("Validation timeout (5 minutes)")
        except Exception as e:
            raise Exception(f"Error running epubcheck: {str(e)}")

def display_results(result):
    """Display validation results"""
    print()
    print("📊 Validation Results")
    print("=" * 60)
    
    if isinstance(result, dict) and 'messages' in result:
        messages = result['messages']
        errors = [msg for msg in messages if msg.get('severity') == 'ERROR']
        warnings = [msg for msg in messages if msg.get('severity') == 'WARNING']
        warnings_fatal = [msg for msg in messages if msg.get('severity') == 'WARNING_FATAL']
        infos = [msg for msg in messages if msg.get('severity') == 'INFO']
        
        print(f"Total messages: {len(messages)}")
        print(f"Fatal warnings: {len(warnings_fatal)} 💥")
        print(f"Errors: {len(errors)} ❌")
        print(f"Warnings: {len(warnings)} ⚠️")
        print(f"Info: {len(infos)} ℹ️")
        print()
        
        # Fatal warnings
        if warnings_fatal:
            print("💥 Fatal Warnings:")
            print("-" * 60)
            for i, warning in enumerate(warnings_fatal, 1):
                print_message(i, warning)
        
        # Errors
        if errors:
            print("❌ Errors Found:")
            print("-" * 60)
            for i, error in enumerate(errors, 1):
                print_message(i, error)
        
        # Warnings (max 10)
        if warnings:
            print("⚠️ Warnings:")
            print("-" * 60)
            for i, warning in enumerate(warnings[:10], 1):
                print_message(i, warning)
            
            if len(warnings) > 10:
                print(f"   ... and {len(warnings) - 10} more warnings.")
                print()
        
        # Result evaluation
        if not errors and not warnings_fatal:
            if not warnings:
                print("🎉 Perfect! No issues found!")
            else:
                print("✅ No critical issues. Please review warnings.")
    
    else:
        if isinstance(result, dict):
            if result.get('returncode') == 0:
                print("✅ Validation successful!")
            if 'stdout' in result and result['stdout']:
                print("Output:", result['stdout'])
            if 'stderr' in result and result['stderr']:
                print("Messages:", result['stderr'])
        else:
            print(str(result))

def print_message(index, message):
    """Print detailed message information"""
    try:
        msg_text = message.get('message', 'Unknown message')
        msg_id = message.get('ID', '')
        
        print(f"📋 Error Code: {msg_id}")
        print(f"📄 Error Content: {msg_text}")
        
        # Location information
        locations = message.get('locations', [])
        if locations:
            print(f"📍 Error Location:")
            for loc_idx, loc in enumerate(locations[:3], 1):
                try:
                    path = loc.get('path', '')
                    line = loc.get('line', '')
                    column = loc.get('column', '')
                    
                    if path:
                        # Remove temporary file path
                        path = re.sub(r'^.*[/\\]AppData[/\\]Local[/\\]Temp[/\\][^/\\]*\.epub[/\\]?', '', path)
                        path = re.sub(r'^[/\\]', '', path)
                        if not path:
                            path = "EPUB file root"
                    
                    location_str = f"   {loc_idx}. File: {path}"
                    if line and line != -1:
                        location_str += f" (line {line}"
                        if column and column != -1:
                            location_str += f", column {column}"
                        location_str += ")"
                    
                    print(location_str)
                except Exception as e:
                    print(f"   {loc_idx}. Location processing error: {str(e)}")
        
        print()
        
    except Exception as e:
        print(f"{index}. Message output error: {str(e)}")
        print()

if __name__ == "__main__":
    print("This script should only be run as a Sigil plugin.")
    print("In Sigil, select Plugins → EpubChecker to run.")
    print()
    print("💡 Features:")
    print("- EPUB validation")
    print("- Detailed error/warning information")
    print("- Cross-platform support")
    sys.exit(-1)