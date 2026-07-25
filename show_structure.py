#!/usr/bin/env python3
# show_structure.py - نمایش کامل ساختار فایل‌های پروژه

import os
import json
from pathlib import Path
from datetime import datetime

def get_project_structure(base_path='.', ignore_dirs=None):
    """
    نمایش کامل ساختار فایل‌های پروژه
    """
    if ignore_dirs is None:
        ignore_dirs = {
            '__pycache__', '.git', 'venv', 'env', 'node_modules', 
            'dist', 'build', '.pytest_cache', '.mypy_cache',
            '__pycache__', 'logs', 'temp', 'tmp', '.vscode', '.idea'
        }
    
    structure = {
        'project_root': str(Path(base_path).absolute()),
        'scan_time': datetime.now().isoformat(),
        'files': {},
        'directories': [],
        'summary': {
            'total_files': 0,
            'total_dirs': 0,
            'python_files': 0,
            'javascript_files': 0,
            'other_files': 0
        }
    }
    
    for root, dirs, files in os.walk(base_path):
        # حذف پوشه‌های ناخواسته
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        # ذخیره مسیر پوشه
        rel_path = os.path.relpath(root, base_path)
        if rel_path == '.':
            rel_path = ''
        
        structure['directories'].append(rel_path)
        
        # بررسی فایل‌های هر پوشه
        for file in files:
            if file.startswith('.') or file in ['show_structure.py']:
                continue
                
            file_path = os.path.join(rel_path, file) if rel_path else file
            full_path = os.path.join(root, file)
            
            # اطلاعات فایل
            try:
                stat = os.stat(full_path)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            except:
                size = 0
                modified = ''
            
            # تشخیص نوع فایل
            ext = os.path.splitext(file)[1].lower()
            file_type = 'other'
            if ext in ['.py']:
                file_type = 'python'
                structure['summary']['python_files'] += 1
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                file_type = 'javascript'
                structure['summary']['javascript_files'] += 1
            elif ext in ['.html', '.css', '.json', '.yml', '.yaml', '.env']:
                file_type = 'config'
            elif ext in ['.md', '.txt']:
                file_type = 'documentation'
            elif ext in ['.sqlite', '.db']:
                file_type = 'database'
            else:
                file_type = 'other'
                structure['summary']['other_files'] += 1
            
            structure['files'][file_path] = {
                'type': file_type,
                'size_bytes': size,
                'size_kb': round(size / 1024, 2) if size > 0 else 0,
                'modified': modified,
                'extension': ext,
                'directory': rel_path
            }
            
            structure['summary']['total_files'] += 1
    
    structure['summary']['total_dirs'] = len(structure['directories'])
    
    return structure

def print_structure_summary(structure):
    """چاپ خلاصه ساختار"""
    print("\n" + "="*80)
    print(f"📁 PROJECT STRUCTURE SCAN")
    print("="*80)
    print(f"📍 مسیر: {structure['project_root']}")
    print(f"🕐 زمان اسکن: {structure['scan_time']}")
    print("-"*80)
    print(f"📊 خلاصه:")
    print(f"   • تعداد کل فایل‌ها: {structure['summary']['total_files']}")
    print(f"   • تعداد پوشه‌ها: {structure['summary']['total_dirs']}")
    print(f"   • فایل‌های Python: {structure['summary']['python_files']}")
    print(f"   • فایل‌های JavaScript: {structure['summary']['javascript_files']}")
    print(f"   • سایر فایل‌ها: {structure['summary']['other_files']}")
    print("-"*80)

def print_detailed_structure(structure):
    """چاپ جزئیات فایل‌ها به تفکیک پوشه"""
    print("\n📂 **DETAILED FILE LIST**")
    print("-"*80)
    
    # گروه‌بندی بر اساس پوشه
    dirs = {}
    for file_path, info in structure['files'].items():
        dir_name = info['directory'] if info['directory'] else '(root)'
        if dir_name not in dirs:
            dirs[dir_name] = []
        dirs[dir_name].append((file_path, info))
    
    # مرتب‌سازی پوشه‌ها
    for dir_name in sorted(dirs.keys()):
        print(f"\n📁 {dir_name}/")
        for file_path, info in sorted(dirs[dir_name]):
            emoji = '🐍' if info['type'] == 'python' else '📄'
            emoji = '🟨' if info['type'] == 'javascript' else emoji
            emoji = '📋' if info['type'] == 'config' else emoji
            emoji = '📝' if info['type'] == 'documentation' else emoji
            emoji = '🗄️' if info['type'] == 'database' else emoji
            
            print(f"   {emoji} {file_path} ({info['size_kb']} KB)")

def save_structure_to_file(structure, filename='project_structure.json'):
    """ذخیره ساختار در فایل JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print(f"\n✅ ساختار پروژه در فایل '{filename}' ذخیره شد.")

def find_key_files(structure):
    """پیدا کردن فایل‌های کلیدی پروژه"""
    key_files = {
        'models.py': [],
        'engine.py': [],
        'run_analysis.py': [],
        'main.py': [],
        'server.py': [],
        'config.py': [],
        'requirements.txt': [],
        'Dockerfile': [],
        'docker-compose.yml': []
    }
    
    for file_path in structure['files'].keys():
        file_name = os.path.basename(file_path)
        for key in key_files.keys():
            if file_name == key:
                key_files[key].append(file_path)
    
    print("\n🎯 **فایل‌های کلیدی شناسایی شده:**")
    print("-"*80)
    for key, paths in key_files.items():
        if paths:
            print(f"   ✅ {key}: {', '.join(paths)}")
        else:
            print(f"   ❌ {key}: پیدا نشد")

if __name__ == "__main__":
    # اسکن از پوشه جاری
    structure = get_project_structure('.')
    
    # نمایش خلاصه
    print_structure_summary(structure)
    
    # نمایش فایل‌های کلیدی
    find_key_files(structure)
    
    # نمایش جزئیات
    print_detailed_structure(structure)
    
    # ذخیره در فایل برای بررسی بهتر
    save_structure_to_file(structure)
    
    print("\n" + "="*80)
    print("💡 **مرحله بعد:**")
    print("   لطفاً خروجی این اسکریپت رو برام بفرستید.")
    print("   من بر اساس اون بهتون می‌گم هر فایل رو چطور اصلاح کنیم.")
    print("="*80)