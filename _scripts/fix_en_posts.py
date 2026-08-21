#!/usr/bin/env python3
"""
Batch fix for English blog articles in _posts/en/

Step 1: Replace the repetitive "Preface"/"Introduction" disclaimer with a clean English statement
Step 2: Translate remaining Chinese in code comments, LaTeX, and front matter tags
Step 3: Fix over-literal phrasing patterns

Usage:
    python3 fix_en_posts.py --step 1    # Fix Preface disclaimer
    python3 fix_en_posts.py --step 2    # Translate code comments
    python3 fix_en_posts.py --step 3    # Fix phrasing patterns
    python3 fix_en_posts.py --all       # Run all steps
"""

import os
import re
import sys
import argparse
from pathlib import Path

EN_POSTS_DIR = Path("/Users/sunyazhou/Documents/sunyazhou/_posts/en")

# Step 1: The replacement text for the disclaimer
# Short, natural English — no "close the page if uncomfortable" nonsense
NEW_DISCLAIMER = "*Personal learning notes. Feel free to share with attribution and a link back.*"

# Patterns that identify the disclaimer paragraph (any of these keywords = it's the disclaimer)
DISCLAIMER_PATTERNS = [
    "strongly colored by personal",
    "highly personal in tone",
    "strong personal feelings",
    "strong personal opinions",
    "carries strong personal",
    "strong personal tone",
    "strong personal sentiment",
    "contains strong personal",
]

# Step 2: Common Chinese-to-English translations for code comments
# This is a curated dictionary — not every possible phrase, but the ones that appear frequently
CODE_COMMENT_TRANSLATIONS = {
    # Common in objc runtime articles
    "查看对象实例是否有效": "Check if the object instance is valid",
    "无效对象直接导致指针释放": "Invalid object causes the pointer to be released directly",
    "这里传递了三个 bool 数值": "Three bool values are passed here",
    "使用 template 进行常量参数传递是为了优化性能": "Using template for constant parameter passing optimizes performance",
    "变量有值": "variable has a value",
    "需要被及时清理": "needs to be cleaned up promptly",
    "当前值可能为 nil": "current value may be nil",
    "需要被分配的新值": "new value to be assigned",
    "不需要分配新值": "no new value needs to be assigned",
    "说明 newObj 已经释放": "indicates newObj has been deallocated",
    "newObj 不支持弱引用": "newObj does not support weak references",
    "该过程需要暂停": "this process needs to be paused",
    "用 nil 替代存储": "store nil as replacement",
    "初始化 previouslyInitializedClass 指针": "Initialize previouslyInitializedClass pointer",
    "声明两个 SideTable": "Declare two SideTables",
    "新旧散列创建": "create old and new hash tables",
    "获得新值和旧值的锁存位置": "Get the latch positions of new and old values",
    "用地址作为唯一标示": "use address as unique identifier",
    "通过地址来建立索引标志": "establish index flags via address",
    "防止桶重复": "prevent bucket duplication",
    "下面指向的操作会改变旧值": "the following operations will change the old value",
    "更改指针": "update pointer",
    "获得以 oldObj 为索引所存储的值地址": "get the value address stored indexed by oldObj",
    "更改新值指针": "update new value pointer",
    "获得以 newObj 为索引所存储的值地址": "get the value address stored indexed by newObj",
    "加锁操作": "Lock operation",
    "防止多线程中竞争冲突": "prevent race conditions in multithreading",
    "避免线程冲突重处理": "avoid thread conflict reprocessing",
    "location 应该与 oldObj 保持一致": "location should be consistent with oldObj",
    "如果不同": "if different",
    "说明当前的 location 已经处理过 oldObj 可是又被其他线程所修改": "indicates the current location has already processed oldObj but was modified by another thread",
    "防止弱引用间死锁": "prevent deadlock between weak references",
    "并且通过 +initialize 初始化构造器保证所有弱引用的 isa 非空指向": "and ensure all weak references' isa is non-null via +initialize",
    "获得新对象的 isa 指针": "get the new object's isa pointer",
    "判断 isa 非空且已经初始化": "check if isa is non-null and initialized",
    "解锁": "unlock",
    "如果该类已经完成执行 +initialize 方法是最理想情况": "ideal case: the class has already executed +initialize",
    "如果该类 +initialize 在线程中": "if the class's +initialize is in a thread",
    "例如 +initialize 正在调用 storeWeak 方法": "e.g. +initialize is calling storeWeak",
    "需要手动对其增加保护策略": "need to manually add protection strategy",
    "并设置 previouslyInitializedClass 指针进行标记": "and set previouslyInitializedClass pointer as marker",
    "重试": "retry",
    "清除旧值": "clear old value",
    "分配新值": "assign new value",
    "如果弱引用被释放": "if the weak reference is deallocated",
    "weak_register_no_lock 方法返回 nil": "weak_register_no_lock returns nil",
    "在引用计数表中设置若引用标记位": "set weak reference flag in the reference count table",
    "弱引用位初始化操作": "weak reference bit initialization",
    "引用计数那张散列表的weak引用对象的引用计数中标识为weak引用": "mark as weak reference in the refcount table's weak ref count",
    "之前不要设置 location 对象": "do not set location object before this",
    "这里需要更改指针指向": "update pointer direction here",
    "没有新值": "no new value",
    "则无需更改": "no change needed",

    # Common in Metal/GPU articles
    "这行代码": "this line",
    "这个应该拿到的就是带Kerning信息的position": "this should get the position with Kerning info",
    "在这里使用strongSelf进行操作": "use strongSelf for operations here",
    "某个输入值": "some input value",
    "结果为": "result is",
    "余数": "remainder",
    "二进制": "binary",
    "即十进制": "i.e. decimal",

    # Common in interview articles
    "前言": "Preface",
    "总结": "Summary",
    "原理": "principle",

    # Misc
    "摘录来自": "Excerpted from",
    "此材料可能受版权保护": "This material may be protected by copyright",
}

# Step 3: Phrasing fixes (pattern -> replacement)
PHRASING_FIXES = [
    # Remove the standalone "Damn." that appears after questions
    (r'\n\n?Damn\.\n', '\n\n'),
    # "Obviously, " at the start of sentences — often unnecessary
    (r'\nObviously, ', '\n'),
    # "highfalutin" -> "fancy"
    (r'\bhighfalutin\b', 'fancy'),
    # "comes down to a rise in awareness" -> more natural
    (r'comes down to a rise in awareness', 'is really about knowing the right tools exist'),
    # "The above is a must-watch for any iOS developer" -> more natural
    (r'The above is a must-watch for any iOS developer', 'These are essential viewing for any iOS developer'),
    # "SwiftKit" -> "SwiftUI" (common typo)
    (r'\bSwiftKit\b', 'SwiftUI'),
]


def fix_preface(content, filepath):
    """Step 1: Replace the repetitive disclaimer with a clean English statement."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    changed = False
    # Track whether we're inside the Preface/Introduction heading section
    in_preface_section = False
    preface_heading_found = False
    disclaimer_found = False

    while i < len(lines):
        line = lines[i]

        # Detect "# Preface" or "# Introduction" heading
        if re.match(r'^#{1,3}\s+(Preface|Introduction)\s*$', line):
            in_preface_section = True
            preface_heading_found = True
            # Skip the heading — we'll replace the whole section
            i += 1
            # Skip blank lines after heading
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue

        if in_preface_section and not disclaimer_found:
            # Check if this line contains the disclaimer
            line_stripped = line.lstrip('> ').strip()
            is_disclaimer = any(p in line for p in DISCLAIMER_PATTERNS)

            if is_disclaimer:
                # Replace with new disclaimer, preserving blockquote if needed
                if line.startswith('>'):
                    new_lines.append('> ' + NEW_DISCLAIMER)
                else:
                    new_lines.append(NEW_DISCLAIMER)
                disclaimer_found = True
                changed = True
                i += 1
                # Skip any continuation of the disclaimer (it's usually one long line)
                # and trailing blank lines
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                in_preface_section = False
                continue
            else:
                # We're in Preface section but no disclaimer found —
                # this might be a different content under Preface
                # Keep the heading we skipped and restore it
                if preface_heading_found and not disclaimer_found:
                    # Put back a simple intro
                    new_lines.append(NEW_DISCLAIMER)
                    changed = True
                    disclaimer_found = True
                    in_preface_section = False
                # Don't skip this line, process it normally
                in_preface_section = False

        new_lines.append(line)
        i += 1

    # If we found and removed the Preface heading but there's now a leading blank section,
    # clean it up
    result = '\n'.join(new_lines)

    # Clean up: remove empty "# Preface" sections that might remain
    # Also handle the case where "# Preface" was followed immediately by content (no disclaimer)
    if not changed:
        # Try a more aggressive approach: find any line matching the disclaimer patterns
        for pattern in DISCLAIMER_PATTERNS:
            if pattern in result:
                # Find the full line(s) containing this pattern and replace
                result = re.sub(
                    r'^(> )?.*' + re.escape(pattern) + r'.*$',
                    lambda m: (m.group(1) if m.group(1) else '') + NEW_DISCLAIMER if (m.group(1) if m.group(1) else '') else NEW_DISCLAIMER,
                    result,
                    flags=re.MULTILINE
                )
                changed = True

    return result, changed


def fix_chinese_in_code(content, filepath):
    """Step 2: Translate remaining Chinese in code comments, LaTeX, and front matter."""
    changed = False
    result = content

    # Translate Chinese in code comments (lines starting with // inside code blocks)
    for cn, en in CODE_COMMENT_TRANSLATIONS.items():
        if cn in result:
            result = result.replace(cn, en)
            changed = True

    # Translate common standalone Chinese words that appear as labels
    # in LaTeX and inline text
    latex_translations = {
        "余数": "remainder",
        "二进制": "binary",
        "即十进制": "i.e. decimal",
        "结果为": "result:",
    }
    for cn, en in latex_translations.items():
        if cn in result:
            result = result.replace(cn, en)
            changed = True

    # Fix front matter: translate Chinese in categories and tags
    # e.g., categories: [iOS, 系统理论实践] -> categories: [iOS, System Theory & Practice]
    front_matter_translations = {
        "系统理论实践": "System Theory & Practice",
        "系统理论": "System Theory",
        "前沿技术探索": "Frontier Tech",
        "前沿技术": "Frontier Tech",
        "开源项目": "Open Source",
        "动画": "Animation",
        "音视频": "Audio & Video",
        "面试": "Interview",
        "算法": "Algorithm",
        "数据结构": "Data Structure",
        "网络": "Networking",
        "工具": "Tools",
        "随笔": "Notes",
        "逆向": "Reverse Engineering",
        "鸿蒙OS开发": "HarmonyOS",
        "跨平台": "Cross-Platform",
        "设计模式": "Design Patterns",
        "性能优化": "Performance",
        "源码解析": "Source Code Analysis",
        "新闻": "News",
        "安全": "Security",
        "数据库": "Database",
        "图像处理": "Image Processing",
        "数学": "Math",
        "图形学": "Computer Graphics",
    }

    for cn, en in front_matter_translations.items():
        if cn in result:
            result = result.replace(cn, en)
            changed = True

    return result, changed


def fix_phrasing(content, filepath):
    """Step 3: Fix over-literal phrasing patterns."""
    changed = False
    result = content

    for pattern, replacement in PHRASING_FIXES:
        new_result = re.sub(pattern, replacement, result)
        if new_result != result:
            result = new_result
            changed = True

    return result, changed


def remove_duplicate_blocks(content, filepath):
    """Step 3b: Remove obviously duplicated content blocks."""
    changed = False
    result = content

    # Find consecutive duplicate paragraphs (3+ lines)
    lines = result.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        # Check if this line and the next few form a block
        # that's repeated immediately after a blank line
        block_start = i
        block_end = i
        while block_end < len(lines) and lines[block_end].strip():
            block_end += 1
        block_size = block_end - block_start

        if block_size >= 3:  # Only check blocks of 3+ lines
            block_text = '\n'.join(lines[block_start:block_end])
            # Look ahead for a duplicate after blank lines
            j = block_end
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_block_end = j
                while next_block_end < len(lines) and lines[next_block_end].strip():
                    next_block_end += 1
                next_block_text = '\n'.join(lines[j:next_block_end])
                if block_text == next_block_text:
                    # Skip the duplicate block + preceding blank lines
                    i = next_block_end
                    changed = True
                    continue

        new_lines.append(lines[i])
        i += 1

    if changed:
        result = '\n'.join(new_lines)

    return result, changed


def process_file(filepath, steps):
    """Process a single file with the given steps."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ERROR reading {filepath.name}: {e}")
        return False

    original = content
    changes = []

    if 1 in steps:
        content, changed = fix_preface(content, filepath)
        if changed:
            changes.append("preface")

    if 2 in steps:
        content, changed = fix_chinese_in_code(content, filepath)
        if changed:
            changes.append("chinese-in-code")

    if 3 in steps:
        content, changed = fix_phrasing(content, filepath)
        if changed:
            changes.append("phrasing")
        content, changed = remove_duplicate_blocks(content, filepath)
        if changed:
            changes.append("dedup")

    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        except Exception as e:
            print(f"  ERROR writing {filepath.name}: {e}")
            return False

    return False


def main():
    parser = argparse.ArgumentParser(description="Fix English blog articles")
    parser.add_argument('--step', type=int, choices=[1, 2, 3], help="Run specific step")
    parser.add_argument('--all', action='store_true', help="Run all steps")
    parser.add_argument('--dry-run', action='store_true', help="Show what would change without writing")
    args = parser.parse_args()

    if args.all:
        steps = [1, 2, 3]
    elif args.step:
        steps = [args.step]
    else:
        print("Specify --step N or --all")
        sys.exit(1)

    md_files = sorted(EN_POSTS_DIR.glob("*.md"))
    print(f"Found {len(md_files)} markdown files\n")

    total_changed = 0
    change_log = []

    for filepath in md_files:
        changes = process_file(filepath, steps)
        if changes:
            total_changed += 1
            change_log.append((filepath.name, changes))
            print(f"  FIXED: {filepath.name} ({', '.join(changes)})")

    print(f"\n{'='*60}")
    print(f"Total files processed: {len(md_files)}")
    print(f"Files modified: {total_changed}")
    print(f"Files unchanged: {len(md_files) - total_changed}")

    if change_log:
        print(f"\nModified files:")
        for name, changes in change_log:
            print(f"  {name}: {', '.join(changes)}")


if __name__ == '__main__':
    main()
