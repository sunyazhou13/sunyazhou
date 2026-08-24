/**
 * 命令行速查手册 — 纯前端，数据内置
 *
 * 支持 Linux / macOS / Unix / Windows 平台常用命令查询：
 *   - 平台筛选（单选/多选）
 *   - 实时搜索（名称 + 描述 + 参数）
 *   - 命令卡片：语法高亮、参数表格、示例、注意事项
 *   - 一键复制示例命令
 *
 * 类名前缀 cr-，与既有工具同构。
 */
(function () {
  'use strict';

  var ROOT = document.getElementById('cr-app');
  if (!ROOT) return;

  var LANG = (document.documentElement.lang || '').toLowerCase() === 'en' ? 'en' : 'zh';
  var I18N = {
    zh: {
      'search-placeholder': '搜索命令、功能或参数…',
      'all-platforms': '全部',
      'commands-count': '条命令',
      'syntax': '语法',
      'options': '常用参数',
      'examples': '示例',
      'notes': '注意事项',
      'related': '相关命令',
      'copy': '复制',
      'copied': '已复制',
      'no-results': '未找到匹配的命令',
      'try-search': '尝试其他关键词或切换平台筛选',
      'platform-linux': 'Linux',
      'platform-macos': 'macOS',
      'platform-unix': 'Unix',
      'platform-windows': 'Windows',
      'flag': '参数',
      'description': '说明',
      'common': '常用',
    },
    en: {
      'search-placeholder': 'Search command, function, or flag…',
      'all-platforms': 'All',
      'commands-count': 'commands',
      'syntax': 'Syntax',
      'options': 'Common Options',
      'examples': 'Examples',
      'notes': 'Notes',
      'related': 'Related',
      'copy': 'Copy',
      'copied': 'Copied',
      'no-results': 'No matching commands found',
      'try-search': 'Try different keywords or change platform filter',
      'platform-linux': 'Linux',
      'platform-macos': 'macOS',
      'platform-unix': 'Unix',
      'platform-windows': 'Windows',
      'flag': 'Flag',
      'description': 'Description',
      'common': 'common',
    }
  };

  function T(key) { return (I18N[LANG] && I18N[LANG][key]) || key; }

  /* ========== 命令数据库 ========== */
  var COMMANDS = [
    /* ─── Linux / Unix / macOS 核心 ─── */
    {
      name: 'ls', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '列出目录内容', en: 'List directory contents' },
      syntax: 'ls [OPTIONS] [FILE...]',
      options: [
        { flag: '-l', desc: { zh: '长格式列表，显示权限、所有者、大小、修改时间等', en: 'Long format: permissions, owner, size, time' }, common: true },
        { flag: '-a', desc: { zh: '显示所有文件，包括以点开头的隐藏文件', en: 'Show all files, including hidden ones' }, common: true },
        { flag: '-h', desc: { zh: '与 -l 配合，以人类可读格式显示文件大小（K/M/G）', en: 'Human-readable sizes (K/M/G) with -l' }, common: true },
        { flag: '-t', desc: { zh: '按修改时间排序，最新的在前', en: 'Sort by modification time, newest first' }, common: true },
        { flag: '-r', desc: { zh: '反向排序', en: 'Reverse order' }, common: false },
        { flag: '-S', desc: { zh: '按文件大小排序，最大的在前', en: 'Sort by file size, largest first' }, common: false },
        { flag: '-d', desc: { zh: '只列出目录本身，而非其内容', en: 'List directories themselves, not their contents' }, common: false },
        { flag: '-R', desc: { zh: '递归列出子目录内容', en: 'Recursively list subdirectories' }, common: false },
      ],
      examples: [
        { cmd: 'ls -lah', desc: { zh: '详细列出所有文件（含隐藏），大小人类可读', en: 'Detailed list of all files with human-readable sizes' } },
        { cmd: 'ls -lt', desc: { zh: '按时间排序列出文件，最新的在前', en: 'List files sorted by time, newest first' } },
        { cmd: 'ls -lah /var/log', desc: { zh: '查看 /var/log 目录的详细内容', en: 'Detailed listing of /var/log directory' } },
      ],
      notes: { zh: '-lh 是日常最常用组合；-lt 适合查看最新修改的文件。', en: '-lh is the most common daily combo; -lt helps find recently modified files.' },
      related: ['cd', 'pwd', 'find']
    },
    {
      name: 'cd', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '切换当前工作目录', en: 'Change the working directory' },
      syntax: 'cd [DIRECTORY]',
      options: [
        { flag: '(none)', desc: { zh: '不带参数时进入用户主目录（$HOME）', en: 'Without argument, goes to home directory ($HOME)' }, common: true },
        { flag: '-', desc: { zh: '切换到上一次所在的目录', en: 'Go to the previous directory' }, common: true },
        { flag: '~', desc: { zh: '用户主目录简写', en: 'Shorthand for home directory' }, common: true },
        { flag: '.', desc: { zh: '当前目录', en: 'Current directory' }, common: false },
        { flag: '..', desc: { zh: '上级目录', en: 'Parent directory' }, common: false },
      ],
      examples: [
        { cmd: 'cd /usr/local/bin', desc: { zh: '进入绝对路径', en: 'Enter absolute path' } },
        { cmd: 'cd ..', desc: { zh: '返回上级目录', en: 'Go to parent directory' } },
        { cmd: 'cd -', desc: { zh: '回到刚才离开的目录', en: 'Return to the previous directory' } },
        { cmd: 'cd ~/Documents', desc: { zh: '进入主目录下的 Documents', en: 'Enter Documents under home' } },
      ],
      notes: { zh: 'cd 是 shell 内置命令，不存在于文件系统。', en: 'cd is a shell builtin, not an actual file on disk.' },
      related: ['ls', 'pwd', 'mkdir']
    },
    {
      name: 'pwd', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '打印当前工作目录的绝对路径', en: 'Print working directory' },
      syntax: 'pwd [OPTIONS]',
      options: [
        { flag: '-L', desc: { zh: '显示逻辑路径（包含符号链接）', en: 'Print logical path (with symlinks)' }, common: true },
        { flag: '-P', desc: { zh: '显示物理路径（解析所有符号链接）', en: 'Print physical path (resolve symlinks)' }, common: false },
      ],
      examples: [
        { cmd: 'pwd', desc: { zh: '显示当前所在目录', en: 'Show current directory' } },
        { cmd: 'pwd -P', desc: { zh: '显示真实物理路径', en: 'Show real physical path' } },
      ],
      notes: { zh: '脚本中常用 $(pwd) 获取当前路径。', en: 'Often used as $(pwd) in scripts to capture current path.' },
      related: ['cd', 'ls']
    },
    {
      name: 'cp', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '复制文件或目录', en: 'Copy files and directories' },
      syntax: 'cp [OPTIONS] SOURCE... DEST',
      options: [
        { flag: '-r / -R', desc: { zh: '递归复制目录及其内容', en: 'Copy directories recursively' }, common: true },
        { flag: '-i', desc: { zh: '覆盖前询问确认', en: 'Prompt before overwriting' }, common: true },
        { flag: '-v', desc: { zh: '显示复制过程中的文件名', en: 'Verbose: show filenames being copied' }, common: false },
        { flag: '-p', desc: { zh: '保留文件的属性（时间戳、权限等）', en: 'Preserve file attributes (timestamps, permissions)' }, common: false },
        { flag: '-f', desc: { zh: '强制覆盖，不提示', en: 'Force overwrite without prompting' }, common: false },
        { flag: '-u', desc: { zh: '仅在源文件比目标新或目标不存在时才复制', en: 'Copy only when source is newer or missing' }, common: false },
      ],
      examples: [
        { cmd: 'cp file.txt backup/', desc: { zh: '复制文件到目录', en: 'Copy file to directory' } },
        { cmd: 'cp -r dir1/ dir2/', desc: { zh: '递归复制整个目录', en: 'Recursively copy entire directory' } },
        { cmd: 'cp -i *.txt backup/', desc: { zh: '批量复制，覆盖时提示', en: 'Batch copy with overwrite prompt' } },
        { cmd: 'cp -rv src/ dst/', desc: { zh: '递归复制并显示过程', en: 'Recursive copy with verbose output' } },
      ],
      notes: { zh: '复制目录必须加 -r，否则报错。', en: 'Must use -r to copy directories, otherwise it will fail.' },
      related: ['mv', 'rm', 'rsync']
    },
    {
      name: 'mv', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '移动或重命名文件/目录', en: 'Move or rename files/directories' },
      syntax: 'mv [OPTIONS] SOURCE... DEST',
      options: [
        { flag: '-i', desc: { zh: '覆盖前询问确认', en: 'Prompt before overwriting' }, common: true },
        { flag: '-v', desc: { zh: '显示移动过程中的文件名', en: 'Verbose: show filenames being moved' }, common: false },
        { flag: '-f', desc: { zh: '强制覆盖，不提示', en: 'Force overwrite without prompting' }, common: false },
        { flag: '-n', desc: { zh: '不覆盖已存在的目标文件', en: 'Do not overwrite existing files' }, common: false },
      ],
      examples: [
        { cmd: 'mv old.txt new.txt', desc: { zh: '重命名文件', en: 'Rename a file' } },
        { cmd: 'mv file.txt /tmp/', desc: { zh: '移动文件到 /tmp 目录', en: 'Move file to /tmp directory' } },
        { cmd: 'mv -i *.log archive/', desc: { zh: '批量移动日志文件，覆盖时提示', en: 'Move logs with overwrite prompt' } },
      ],
      notes: { zh: 'mv 跨文件系统移动大文件时较慢（实际是先复制后删除）。', en: 'Moving across filesystems is slow (copies then deletes).' },
      related: ['cp', 'rm', 'rename']
    },
    {
      name: 'rm', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '删除文件或目录', en: 'Remove files or directories' },
      syntax: 'rm [OPTIONS] FILE...',
      options: [
        { flag: '-r / -R', desc: { zh: '递归删除目录及其内容', en: 'Remove directories recursively' }, common: true },
        { flag: '-f', desc: { zh: '强制删除，不提示确认', en: 'Force removal without prompting' }, common: true },
        { flag: '-i', desc: { zh: '删除前逐个询问确认', en: 'Prompt before every removal' }, common: false },
        { flag: '-v', desc: { zh: '显示删除的文件名', en: 'Verbose: show files being removed' }, common: false },
        { flag: '-d', desc: { zh: '删除空目录', en: 'Remove empty directories' }, common: false },
      ],
      examples: [
        { cmd: 'rm file.txt', desc: { zh: '删除单个文件', en: 'Remove a single file' } },
        { cmd: 'rm -r dir/', desc: { zh: '递归删除目录', en: 'Recursively remove directory' } },
        { cmd: 'rm -rf dir/', desc: { zh: '强制递归删除（极度危险）', en: 'Force recursive remove (DANGEROUS)' } },
        { cmd: 'rm -i *.txt', desc: { zh: '批量删除前逐个确认', en: 'Batch remove with individual confirmation' } },
      ],
      notes: { zh: 'rm -rf / 会删除整个系统！使用通配符前先用 ls 检查。', en: 'rm -rf / will delete the entire system! Always test wildcards with ls first.' },
      related: ['rmdir', 'mv', 'shred']
    },
    {
      name: 'mkdir', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '创建目录', en: 'Make directories' },
      syntax: 'mkdir [OPTIONS] DIRECTORY...',
      options: [
        { flag: '-p', desc: { zh: '递归创建多级目录（父目录不存在时自动创建）', en: 'Create parent directories as needed' }, common: true },
        { flag: '-v', desc: { zh: '显示创建的目录名', en: 'Verbose: show created directories' }, common: false },
        { flag: '-m MODE', desc: { zh: '创建时指定权限模式', en: 'Set file mode at creation' }, common: false },
      ],
      examples: [
        { cmd: 'mkdir newdir', desc: { zh: '创建单个目录', en: 'Create a single directory' } },
        { cmd: 'mkdir -p a/b/c', desc: { zh: '递归创建多级目录', en: 'Create nested directories' } },
        { cmd: 'mkdir -p ~/projects/{src,docs,tests}', desc: { zh: '批量创建多个同级目录', en: 'Create multiple sibling directories' } },
      ],
      notes: { zh: '-p 是最常用的选项，避免"父目录不存在"报错。', en: '-p is the most common option, avoids "parent does not exist" errors.' },
      related: ['rmdir', 'cd', 'touch']
    },
    {
      name: 'touch', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '创建空文件或更新文件时间戳', en: 'Create empty file or update timestamps' },
      syntax: 'touch [OPTIONS] FILE...',
      options: [
        { flag: '-a', desc: { zh: '只修改访问时间（access time）', en: 'Change only access time' }, common: false },
        { flag: '-m', desc: { zh: '只修改修改时间（modification time）', en: 'Change only modification time' }, common: false },
        { flag: '-t STAMP', desc: { zh: '使用指定时间 [[CC]YY]MMDDhhmm[.ss]', en: 'Use specified time' }, common: false },
        { flag: '-c', desc: { zh: '不创建不存在的文件', en: 'Do not create non-existent files' }, common: false },
      ],
      examples: [
        { cmd: 'touch newfile.txt', desc: { zh: '创建空文件', en: 'Create an empty file' } },
        { cmd: 'touch -t 202401011200 file.txt', desc: { zh: '将文件时间戳设为 2024-01-01 12:00', en: 'Set timestamp to 2024-01-01 12:00' } },
        { cmd: 'touch existing.txt', desc: { zh: '更新现有文件的时间戳到当前时间', en: 'Update existing file timestamp to now' } },
      ],
      notes: { zh: '文件不存在时创建空文件；存在时更新时间戳。', en: 'Creates file if missing; updates timestamp if exists.' },
      related: ['mkdir', 'cat', 'echo']
    },
    {
      name: 'cat', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '连接文件并输出到标准输出', en: 'Concatenate files and print to stdout' },
      syntax: 'cat [OPTIONS] [FILE...]',
      options: [
        { flag: '-n', desc: { zh: '显示行号', en: 'Number all output lines' }, common: true },
        { flag: '-b', desc: { zh: '对非空行显示行号', en: 'Number non-empty lines' }, common: false },
        { flag: '-s', desc: { zh: '压缩多个连续空行成一行', en: 'Suppress repeated empty lines' }, common: false },
        { flag: '-E', desc: { zh: '行尾显示 $ 符号', en: 'Display $ at end of each line' }, common: false },
        { flag: '-T', desc: { zh: '将制表符显示为 ^I', en: 'Display tabs as ^I' }, common: false },
        { flag: '-A', desc: { zh: '等价于 -vET，显示所有不可见字符', en: 'Equivalent to -vET, show all non-printing' }, common: false },
      ],
      examples: [
        { cmd: 'cat file.txt', desc: { zh: '查看文件全部内容', en: 'Display entire file content' } },
        { cmd: 'cat -n file.txt', desc: { zh: '带行号查看', en: 'Display with line numbers' } },
        { cmd: 'cat file1.txt file2.txt > combined.txt', desc: { zh: '合并多个文件到新文件', en: 'Concatenate files into a new file' } },
        { cmd: 'cat > file.txt', desc: { zh: '从键盘输入写入文件（Ctrl+D 结束）', en: 'Write from keyboard (Ctrl+D to finish)' } },
      ],
      notes: { zh: '大文件用 less 或 more 代替 cat，避免刷屏。', en: 'Use less or more for large files to avoid flooding the screen.' },
      related: ['less', 'more', 'head', 'tail', 'tac']
    },
    {
      name: 'less', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '分页查看文件内容（支持前后翻页）', en: 'Page through text (forward and backward)' },
      syntax: 'less [OPTIONS] FILE',
      options: [
        { flag: '-N', desc: { zh: '显示行号', en: 'Show line numbers' }, common: true },
        { flag: '-i', desc: { zh: '搜索时忽略大小写', en: 'Case-insensitive search' }, common: true },
        { flag: '-F', desc: { zh: '内容少于一屏时直接退出（类似 cat）', en: 'Exit if content fits on one screen' }, common: false },
        { flag: '-S', desc: { zh: '不换行截断长行', en: 'Chop long lines instead of wrapping' }, common: false },
        { flag: '+F', desc: { zh: '类似 tail -f，实时跟踪文件追加', en: 'Like tail -f, follow file growth' }, common: false },
      ],
      examples: [
        { cmd: 'less file.txt', desc: { zh: '分页查看文件', en: 'View file with paging' } },
        { cmd: 'less -N /var/log/syslog', desc: { zh: '带行号查看日志', en: 'View log with line numbers' } },
        { cmd: 'cat file.txt | less', desc: { zh: '管道接 less', en: 'Pipe to less' } },
        { cmd: 'less +F /var/log/app.log', desc: { zh: '实时跟踪日志追加', en: 'Follow log file in real-time' } },
      ],
      notes: { zh: 'less 中常用操作：q 退出，/ 搜索，n/N 下一个/上一个匹配，g/G 首行/末行，Space 下翻页。', en: 'Common less keys: q quit, / search, n/N next/prev match, g/G first/last line, Space page down.' },
      related: ['more', 'cat', 'head', 'tail']
    },
    {
      name: 'head', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '输出文件开头部分', en: 'Output the first part of files' },
      syntax: 'head [OPTIONS] [FILE...]',
      options: [
        { flag: '-n NUM', desc: { zh: '显示前 NUM 行（默认 10 行）', en: 'Print first NUM lines (default 10)' }, common: true },
        { flag: '-c NUM', desc: { zh: '显示前 NUM 字节', en: 'Print first NUM bytes' }, common: false },
        { flag: '-q', desc: { zh: '多文件时不显示文件名头部', en: 'Never print headers with file names' }, common: false },
        { flag: '-v', desc: { zh: '总是显示文件名头部', en: 'Always print headers with file names' }, common: false },
      ],
      examples: [
        { cmd: 'head file.txt', desc: { zh: '显示前 10 行', en: 'Show first 10 lines' } },
        { cmd: 'head -n 20 file.txt', desc: { zh: '显示前 20 行', en: 'Show first 20 lines' } },
        { cmd: 'head -n 5 *.log', desc: { zh: '显示每个日志文件的前 5 行', en: 'Show first 5 lines of each log' } },
      ],
      notes: { zh: 'head -n -5 表示除最后 5 行外全部显示。', en: 'head -n -5 shows all but the last 5 lines.' },
      related: ['tail', 'cat', 'less']
    },
    {
      name: 'tail', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '输出文件末尾部分（常用于看日志）', en: 'Output the last part of files' },
      syntax: 'tail [OPTIONS] [FILE...]',
      options: [
        { flag: '-n NUM', desc: { zh: '显示最后 NUM 行（默认 10 行）', en: 'Print last NUM lines (default 10)' }, common: true },
        { flag: '-f', desc: { zh: '实时跟踪文件追加（follow mode）', en: 'Follow file as it grows' }, common: true },
        { flag: '-F', desc: { zh: '类似 -f，但文件被删除重建时重新打开', en: 'Like -f, but reopen if file is recreated' }, common: false },
        { flag: '-c NUM', desc: { zh: '显示最后 NUM 字节', en: 'Print last NUM bytes' }, common: false },
        { flag: '--pid=PID', desc: { zh: '配合 -f，在指定进程结束后退出', en: 'With -f, exit when PID dies' }, common: false },
      ],
      examples: [
        { cmd: 'tail -f /var/log/nginx/access.log', desc: { zh: '实时跟踪 Nginx 访问日志', en: 'Follow Nginx access log in real-time' } },
        { cmd: 'tail -n 100 app.log | grep ERROR', desc: { zh: '查看最后 100 行并过滤错误', en: 'Check last 100 lines and filter errors' } },
        { cmd: 'tail -f log.txt | grep "keyword"', desc: { zh: '实时跟踪并过滤关键词', en: 'Follow and filter by keyword' } },
      ],
      notes: { zh: 'tail -f 是查看实时日志的标准做法。Ctrl+C 退出。', en: 'tail -f is the standard way to watch live logs. Press Ctrl+C to quit.' },
      related: ['head', 'less', 'grep']
    },
    {
      name: 'grep', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '文本搜索，支持正则表达式', en: 'Search text using patterns (regex)' },
      syntax: 'grep [OPTIONS] PATTERN [FILE...]',
      options: [
        { flag: '-i', desc: { zh: '忽略大小写', en: 'Case-insensitive search' }, common: true },
        { flag: '-r / -R', desc: { zh: '递归搜索目录', en: 'Recursive directory search' }, common: true },
        { flag: '-n', desc: { zh: '显示匹配行的行号', en: 'Show line numbers' }, common: true },
        { flag: '-v', desc: { zh: '反向匹配，显示不包含模式的行', en: 'Invert match, show non-matching lines' }, common: true },
        { flag: '-l', desc: { zh: '只列出包含匹配的文件名', en: 'List only filenames with matches' }, common: false },
        { flag: '-c', desc: { zh: '统计每个文件的匹配行数', en: 'Count matching lines per file' }, common: false },
        { flag: '-E', desc: { zh: '使用扩展正则表达式（相当于 egrep）', en: 'Use extended regex (same as egrep)' }, common: false },
        { flag: '-o', desc: { zh: '只输出匹配到的部分，而非整行', en: 'Show only matching parts, not whole line' }, common: false },
        { flag: '-A NUM', desc: { zh: '显示匹配行后 NUM 行', en: 'Show NUM lines after match' }, common: false },
        { flag: '-B NUM', desc: { zh: '显示匹配行前 NUM 行', en: 'Show NUM lines before match' }, common: false },
        { flag: '-C NUM', desc: { zh: '显示匹配行前后各 NUM 行', en: 'Show NUM lines before and after' }, common: false },
        { flag: '--color=auto', desc: { zh: '高亮匹配文本', en: 'Highlight matching text' }, common: false },
      ],
      examples: [
        { cmd: 'grep -n "error" log.txt', desc: { zh: '在文件中搜索 error 并显示行号', en: 'Search for "error" with line numbers' } },
        { cmd: 'grep -ri "todo" src/', desc: { zh: '递归忽略大小写搜索 todo', en: 'Recursively case-insensitive search for "todo"' } },
        { cmd: 'grep -v "^#" config.txt', desc: { zh: '排除以 # 开头的注释行', en: 'Exclude lines starting with #' } },
        { cmd: 'ps aux | grep nginx', desc: { zh: '管道接 grep 过滤进程', en: 'Pipe to grep to filter processes' } },
        { cmd: 'grep -E "(error|warning)" log.txt', desc: { zh: '使用扩展正则匹配多个关键词', en: 'Extended regex matching multiple keywords' } },
      ],
      notes: { zh: 'grep 默认使用基本正则（BRE），复杂模式用 -E（ERE）。', en: 'grep uses Basic Regex by default; use -E for Extended Regex with complex patterns.' },
      related: ['find', 'awk', 'sed', 'rg']
    },
    {
      name: 'find', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '在目录树中搜索文件', en: 'Search for files in directory hierarchy' },
      syntax: 'find [PATH] [EXPRESSION]',
      options: [
        { flag: '-name PATTERN', desc: { zh: '按文件名匹配（区分大小写）', en: 'Match filename (case-sensitive)' }, common: true },
        { flag: '-iname PATTERN', desc: { zh: '按文件名匹配（忽略大小写）', en: 'Match filename (case-insensitive)' }, common: true },
        { flag: '-type TYPE', desc: { zh: '按类型筛选：f=文件 d=目录 l=符号链接', en: 'Filter by type: f=file d=directory l=symlink' }, common: true },
        { flag: '-size [+-]N[cwbkMG]', desc: { zh: '按大小筛选（+大于 -小于，单位 b/k/M/G）', en: 'Filter by size (+greater -less, units b/k/M/G)' }, common: true },
        { flag: '-mtime N', desc: { zh: '按修改时间筛选（N 天内）', en: 'Modified within N days' }, common: false },
        { flag: '-exec CMD {} +', desc: { zh: '对匹配结果执行命令', en: 'Execute command on matched files' }, common: true },
        { flag: '-maxdepth N', desc: { zh: '最大搜索深度', en: 'Maximum search depth' }, common: false },
        { flag: '-mindepth N', desc: { zh: '最小搜索深度', en: 'Minimum search depth' }, common: false },
        { flag: '-perm MODE', desc: { zh: '按权限模式筛选', en: 'Filter by permission mode' }, common: false },
        { flag: '-user USER', desc: { zh: '按所有者筛选', en: 'Filter by owner' }, common: false },
        { flag: '-empty', desc: { zh: '只找空文件或空目录', en: 'Find empty files or directories' }, common: false },
        { flag: '-delete', desc: { zh: '删除匹配的文件（谨慎使用）', en: 'Delete matched files (use carefully)' }, common: false },
        { flag: '-print0', desc: { zh: '以 null 字符分隔输出，配合 xargs -0 处理含空格文件名', en: 'Null-separated output for xargs -0' }, common: false },
      ],
      examples: [
        { cmd: 'find . -name "*.js"', desc: { zh: '当前目录递归查找所有 .js 文件', en: 'Find all .js files recursively' } },
        { cmd: 'find /var/log -type f -mtime -7', desc: { zh: '查找 /var/log 下 7 天内修改过的文件', en: 'Find files modified in last 7 days under /var/log' } },
        { cmd: 'find . -type f -size +100M', desc: { zh: '查找大于 100MB 的文件', en: 'Find files larger than 100MB' } },
        { cmd: 'find . -name "*.tmp" -delete', desc: { zh: '删除所有 .tmp 临时文件', en: 'Delete all .tmp temporary files' } },
        { cmd: 'find . -type f -exec grep -l "TODO" {} +', desc: { zh: '查找包含 TODO 的所有文件', en: 'Find all files containing "TODO"' } },
        { cmd: 'find . -name "*.log" -print0 | xargs -0 rm', desc: { zh: '安全删除含空格的日志文件', en: 'Safely delete log files with spaces in names' } },
      ],
      notes: { zh: 'find 的表达式是从左到右短路求值，顺序影响性能。先用 -type 过滤再用 -name。', en: 'Expressions evaluate left-to-right. Put -type before -name for better performance.' },
      related: ['locate', 'grep', 'xargs']
    },
    {
      name: 'chmod', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '修改文件或目录的权限', en: 'Change file mode bits (permissions)' },
      syntax: 'chmod [OPTIONS] MODE FILE...',
      options: [
        { flag: '-R', desc: { zh: '递归修改目录及内容权限', en: 'Change permissions recursively' }, common: true },
        { flag: '-v', desc: { zh: '显示每个处理的文件', en: 'Verbose: show each file processed' }, common: false },
        { flag: '-c', desc: { zh: '只在权限改变时报告', en: 'Report only when changes are made' }, common: false },
      ],
      examples: [
        { cmd: 'chmod 755 script.sh', desc: { zh: '设置文件为 rwxr-xr-x（所有者可读写执行，其他可读执行）', en: 'Set to rwxr-xr-x (owner rwx, others rx)' } },
        { cmd: 'chmod +x script.sh', desc: { zh: '给所有用户添加执行权限', en: 'Add execute permission for all users' } },
        { cmd: 'chmod -R 755 ~/projects', desc: { zh: '递归设置目录权限', en: 'Recursively set directory permissions' } },
        { cmd: 'chmod u+w file.txt', desc: { zh: '给所有者添加写权限', en: 'Add write permission for owner' } },
        { cmd: 'chmod go-rwx secret.txt', desc: { zh: '移除组和其他用户的所有权限', en: 'Remove all permissions for group and others' } },
      ],
      notes: { zh: '权限数字：4=读(r) 2=写(w) 1=执行(x)，三个数字分别对应 所有者/组/其他。', en: 'Permission digits: 4=read 2=write 1=execute; three digits for owner/group/others.' },
      related: ['chown', 'chgrp', 'ls -l']
    },
    {
      name: 'chown', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '修改文件或目录的所有者和组', en: 'Change file owner and group' },
      syntax: 'chown [OPTIONS] [OWNER][:[GROUP]] FILE...',
      options: [
        { flag: '-R', desc: { zh: '递归修改', en: 'Operate on files and directories recursively' }, common: true },
        { flag: '-v', desc: { zh: '显示处理过程', en: 'Verbose output' }, common: false },
        { flag: '--reference=RFILE', desc: { zh: '将权限设成与参考文件相同', en: 'Set permissions to match reference file' }, common: false },
      ],
      examples: [
        { cmd: 'chown user file.txt', desc: { zh: '将文件所有者改为 user', en: 'Change owner to user' } },
        { cmd: 'chown user:group file.txt', desc: { zh: '同时修改所有者和组', en: 'Change both owner and group' } },
        { cmd: 'chown -R user:group /var/www', desc: { zh: '递归修改目录的所有者和组', en: 'Recursively change owner and group' } },
        { cmd: 'chown :admin file.txt', desc: { zh: '只修改组（所有者不变）', en: 'Change only the group' } },
      ],
      notes: { zh: '只有 root 或文件所有者才能修改所有者（chown 通常需要 sudo）。', en: 'Only root or the file owner can change ownership (chown usually requires sudo).' },
      related: ['chmod', 'chgrp', 'sudo']
    },
    {
      name: 'tar', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '归档工具，打包/解包文件', en: 'Archiving utility for packaging files' },
      syntax: 'tar [OPTIONS] [FILE...]',
      options: [
        { flag: '-c', desc: { zh: '创建新归档（create）', en: 'Create a new archive' }, common: true },
        { flag: '-x', desc: { zh: '解包归档（extract）', en: 'Extract files from archive' }, common: true },
        { flag: '-t', desc: { zh: '列出归档内容（list）', en: 'List contents of archive' }, common: true },
        { flag: '-f FILE', desc: { zh: '指定归档文件名', en: 'Use archive file' }, common: true },
        { flag: '-v', desc: { zh: '显示处理过程中的文件名', en: 'Verbose: show filenames' }, common: true },
        { flag: '-z', desc: { zh: '通过 gzip 压缩/解压', en: 'Filter through gzip' }, common: true },
        { flag: '-j', desc: { zh: '通过 bzip2 压缩/解压', en: 'Filter through bzip2' }, common: false },
        { flag: '-J', desc: { zh: '通过 xz 压缩/解压', en: 'Filter through xz' }, common: false },
        { flag: '-C DIR', desc: { zh: '切换到指定目录再操作', en: 'Change to directory before operation' }, common: false },
        { flag: '-p', desc: { zh: '保留文件权限', en: 'Preserve file permissions' }, common: false },
        { flag: '--exclude=PATTERN', desc: { zh: '排除匹配的文件', en: 'Exclude files matching pattern' }, common: false },
      ],
      examples: [
        { cmd: 'tar -czvf archive.tar.gz dir/', desc: { zh: '将目录打包并 gzip 压缩', en: 'Create gzipped archive of directory' } },
        { cmd: 'tar -xzvf archive.tar.gz', desc: { zh: '解压 .tar.gz 文件', en: 'Extract gzipped archive' } },
        { cmd: 'tar -tzvf archive.tar.gz', desc: { zh: '查看归档内文件列表', en: 'List contents without extracting' } },
        { cmd: 'tar -czvf backup.tar.gz --exclude="*.log" project/', desc: { zh: '打包时排除所有 .log 文件', en: 'Archive excluding all .log files' } },
      ],
      notes: { zh: '常见组合：czvf=创建压缩包，xzvf=解压，tzvf=查看。注意 f 必须放在选项最后（紧跟文件名）。', en: 'Common combos: czvf=create, xzvf=extract, tzvf=list. Note: f must be last before filename.' },
      related: ['gzip', 'zip', 'rsync']
    },
    {
      name: 'gzip', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '压缩/解压 gzip 格式文件', en: 'Compress or expand files (gzip)' },
      syntax: 'gzip [OPTIONS] [FILE...]',
      options: [
        { flag: '-d', desc: { zh: '解压（decompress）', en: 'Decompress' }, common: true },
        { flag: '-k', desc: { zh: '压缩时保留原文件', en: 'Keep original file' }, common: true },
        { flag: '-r', desc: { zh: '递归压缩目录中的文件', en: 'Recursively compress directory' }, common: false },
        { flag: '-l', desc: { zh: '列出压缩文件信息', en: 'List compressed file info' }, common: false },
        { flag: '-1 .. -9', desc: { zh: '压缩级别（1=最快，9=最小，默认 6）', en: 'Compression level (1=fastest, 9=best, default 6)' }, common: false },
      ],
      examples: [
        { cmd: 'gzip file.txt', desc: { zh: '压缩文件为 file.txt.gz（原文件被删除）', en: 'Compress to file.txt.gz (original removed)' } },
        { cmd: 'gzip -k file.txt', desc: { zh: '压缩并保留原文件', en: 'Compress while keeping original' } },
        { cmd: 'gzip -d file.txt.gz', desc: { zh: '解压文件', en: 'Decompress file' } },
        { cmd: 'gunzip file.txt.gz', desc: { zh: 'gunzip 等价于 gzip -d', en: 'gunzip is equivalent to gzip -d' } },
      ],
      notes: { zh: 'gzip 只能压缩单个文件，多个文件先用 tar 打包。', en: 'gzip only compresses single files; use tar first for multiple files.' },
      related: ['gunzip', 'tar', 'zip']
    },
    {
      name: 'ps', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '报告当前进程状态', en: 'Report process status' },
      syntax: 'ps [OPTIONS]',
      options: [
        { flag: 'aux', desc: { zh: '显示所有用户的全部进程（BSD 风格）', en: 'Show all processes for all users (BSD style)' }, common: true },
        { flag: '-ef', desc: { zh: '显示所有进程的完整信息（System V 风格）', en: 'Show all processes full info (System V style)' }, common: true },
        { flag: '-u USER', desc: { zh: '显示指定用户的进程', en: 'Show processes for specific user' }, common: false },
        { flag: '-p PID', desc: { zh: '显示指定 PID 的进程', en: 'Show specific process by PID' }, common: false },
        { flag: '--sort=-%cpu', desc: { zh: '按 CPU 使用率降序排序', en: 'Sort by CPU usage descending' }, common: false },
        { flag: '--sort=-%mem', desc: { zh: '按内存使用率降序排序', en: 'Sort by memory usage descending' }, common: false },
      ],
      examples: [
        { cmd: 'ps aux', desc: { zh: '查看所有进程', en: 'Show all processes' } },
        { cmd: 'ps aux | grep nginx', desc: { zh: '查找 nginx 相关进程', en: 'Find nginx-related processes' } },
        { cmd: 'ps -ef --sort=-%cpu | head', desc: { zh: '查看 CPU 占用最高的进程', en: 'Show top CPU-consuming processes' } },
        { cmd: 'ps -p 1234 -o pid,ppid,cmd,%mem,%cpu', desc: { zh: '查看指定 PID 的详细信息', en: 'Show detailed info for specific PID' } },
      ],
      notes: { zh: 'ps aux 输出中 RSS 是实际内存，VSZ 是虚拟内存。', en: 'In ps aux output, RSS is real memory, VSZ is virtual memory.' },
      related: ['top', 'htop', 'kill', 'pkill']
    },
    {
      name: 'kill', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '向进程发送信号（默认终止）', en: 'Send signal to a process (default: terminate)' },
      syntax: 'kill [OPTIONS] PID...',
      options: [
        { flag: '-l', desc: { zh: '列出所有可用信号', en: 'List all available signals' }, common: true },
        { flag: '-s SIGNAL', desc: { zh: '发送指定信号（可用数字或名称）', en: 'Send specified signal' }, common: true },
        { flag: '-9', desc: { zh: 'SIGKILL：强制终止，无法被进程捕获', en: 'SIGKILL: force kill, cannot be caught' }, common: true },
        { flag: '-15', desc: { zh: 'SIGTERM：优雅请求终止（默认，可被捕获）', en: 'SIGTERM: graceful terminate (default, catchable)' }, common: false },
        { flag: '-HUP', desc: { zh: 'SIGHUP：重载配置（很多守护进程用此信号）', en: 'SIGHUP: reload config (used by many daemons)' }, common: false },
        { flag: '-INT', desc: { zh: 'SIGINT：等同于 Ctrl+C', en: 'SIGINT: same as Ctrl+C' }, common: false },
      ],
      examples: [
        { cmd: 'kill 1234', desc: { zh: '优雅终止 PID 为 1234 的进程', en: 'Gracefully terminate process 1234' } },
        { cmd: 'kill -9 1234', desc: { zh: '强制终止进程', en: 'Force kill process' } },
        { cmd: 'kill -HUP 1234', desc: { zh: '让进程重载配置', en: 'Reload process configuration' } },
        { cmd: 'kill -l', desc: { zh: '列出所有信号名称', en: 'List all signal names' } },
      ],
      notes: { zh: '先用 kill -15（或默认）优雅终止，无效再用 kill -9。kill -9 不会清理资源，可能导致数据丢失。', en: 'Try kill -15 first, then -9 if needed. kill -9 does not clean up resources, may cause data loss.' },
      related: ['killall', 'pkill', 'ps', 'top']
    },
    {
      name: 'df', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '报告文件系统磁盘空间使用情况', en: 'Report file system disk space usage' },
      syntax: 'df [OPTIONS] [FILE...]',
      options: [
        { flag: '-h', desc: { zh: '人类可读格式（K/M/G）', en: 'Human-readable sizes' }, common: true },
        { flag: '-T', desc: { zh: '显示文件系统类型', en: 'Show file system type' }, common: true },
        { flag: '-i', desc: { zh: '显示 inode 信息而非块用量', en: 'Show inode info instead of block usage' }, common: false },
        { flag: '-a', desc: { zh: '显示所有文件系统（含虚拟文件系统）', en: 'Show all filesystems including virtual' }, common: false },
      ],
      examples: [
        { cmd: 'df -h', desc: { zh: '查看磁盘空间（人类可读）', en: 'Check disk space (human-readable)' } },
        { cmd: 'df -h .', desc: { zh: '查看当前目录所在分区的空间', en: 'Check space for current directory partition' } },
        { cmd: 'df -Th', desc: { zh: '显示文件系统类型和空间', en: 'Show filesystem type and space' } },
      ],
      notes: { zh: '当磁盘"还有空间"却无法写入时，检查 inode 使用率（df -i）。', en: 'When disk "has space" but writes fail, check inode usage with df -i.' },
      related: ['du', 'lsblk', 'mount']
    },
    {
      name: 'du', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '估算文件和目录的磁盘使用空间', en: 'Estimate file and directory space usage' },
      syntax: 'du [OPTIONS] [FILE...]',
      options: [
        { flag: '-h', desc: { zh: '人类可读格式', en: 'Human-readable sizes' }, common: true },
        { flag: '-s', desc: { zh: '只显示总计（summarize）', en: 'Display only a total for each argument' }, common: true },
        { flag: '-a', desc: { zh: '显示所有文件（不只是目录）', en: 'Show all files, not just directories' }, common: false },
        { flag: '-c', desc: { zh: '最后显示总计', en: 'Produce a grand total' }, common: false },
        { flag: '--max-depth=N', desc: { zh: '只显示 N 层深度的目录', en: 'Show directories only up to N levels deep' }, common: false },
        { flag: '-k', desc: { zh: '以 KB 为单位显示', en: 'Display in kilobytes' }, common: false },
        { flag: '-m', desc: { zh: '以 MB 为单位显示', en: 'Display in megabytes' }, common: false },
        { flag: '-L', desc: { zh: '统计符号链接指向的实际文件大小', en: 'Dereference symlinks' }, common: false },
      ],
      examples: [
        { cmd: 'du -sh /var/log', desc: { zh: '查看 /var/log 总大小', en: 'Check total size of /var/log' } },
        { cmd: 'du -h --max-depth=1 ~', desc: { zh: '查看主目录下各子目录的大小', en: 'Show sizes of subdirectories in home' } },
        { cmd: 'du -sh * | sort -rh | head -10', desc: { zh: '查看当前目录下最大的 10 个文件/目录', en: 'Show 10 largest files/directories' } },
      ],
      notes: { zh: 'du -sh 是最常用的组合。注意符号链接默认不统计目标文件大小。', en: 'du -sh is the most common combo. Symlinks are not dereferenced by default.' },
      related: ['df', 'ls', 'find']
    },
    {
      name: 'ssh', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '安全远程登录/执行命令', en: 'Secure remote login and command execution' },
      syntax: 'ssh [OPTIONS] [USER@]HOSTNAME [COMMAND]',
      options: [
        { flag: '-p PORT', desc: { zh: '指定端口（默认 22）', en: 'Connect to specified port (default 22)' }, common: true },
        { flag: '-i FILE', desc: { zh: '指定私钥文件', en: 'Identity file (private key)' }, common: true },
        { flag: '-X', desc: { zh: '启用 X11 转发', en: 'Enable X11 forwarding' }, common: false },
        { flag: '-L [bind:]port:host:hostport', desc: { zh: '本地端口转发', en: 'Local port forwarding' }, common: true },
        { flag: '-R [bind:]port:host:hostport', desc: { zh: '远程端口转发', en: 'Remote port forwarding' }, common: false },
        { flag: '-N', desc: { zh: '不执行远程命令（用于端口转发）', en: 'Do not execute remote command (for port forwarding)' }, common: false },
        { flag: '-f', desc: { zh: '后台运行', en: 'Run in background' }, common: false },
        { flag: '-v / -vv / -vvv', desc: { zh: '详细模式（越多 v 越详细）', en: 'Verbose mode (more v = more verbose)' }, common: false },
        { flag: '-o Option', desc: { zh: '指定配置文件选项', en: 'Specify configuration option' }, common: false },
      ],
      examples: [
        { cmd: 'ssh user@host', desc: { zh: '登录远程服务器', en: 'Login to remote server' } },
        { cmd: 'ssh -p 2222 user@host', desc: { zh: '使用非默认端口登录', en: 'Login with non-default port' } },
        { cmd: 'ssh -i ~/.ssh/id_rsa user@host', desc: { zh: '使用指定私钥登录', en: 'Login with specific private key' } },
        { cmd: 'ssh user@host "ls -la"', desc: { zh: '远程执行命令后断开', en: 'Execute command remotely and disconnect' } },
        { cmd: 'ssh -L 8080:localhost:80 user@host', desc: { zh: '将本地 8080 转发到远程的 80', en: 'Forward local 8080 to remote port 80' } },
        { cmd: 'ssh -N -L 3306:db.internal:3306 user@bastion', desc: { zh: '通过跳板机建立数据库隧道', en: 'Create DB tunnel through bastion host' } },
      ],
      notes: { zh: '首次连接时会提示保存主机指纹到 ~/.ssh/known_hosts。', en: 'First connection prompts to save host fingerprint to ~/.ssh/known_hosts.' },
      related: ['scp', 'rsync', 'sftp']
    },
    {
      name: 'scp', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '通过 SSH 安全复制文件', en: 'Secure copy (remote file copy program)' },
      syntax: 'scp [OPTIONS] SOURCE... DEST',
      options: [
        { flag: '-P PORT', desc: { zh: '指定 SSH 端口（注意大写 P）', en: 'Connect to specified port (note: capital P)' }, common: true },
        { flag: '-i FILE', desc: { zh: '指定私钥文件', en: 'Identity file' }, common: true },
        { flag: '-r', desc: { zh: '递归复制目录', en: 'Recursively copy directories' }, common: true },
        { flag: '-p', desc: { zh: '保留修改时间、访问时间和模式', en: 'Preserve modification times, access times, and modes' }, common: false },
        { flag: '-C', desc: { zh: '启用压缩', en: 'Enable compression' }, common: false },
        { flag: '-q', desc: { zh: '静默模式', en: 'Quiet mode' }, common: false },
        { flag: '-v', desc: { zh: '详细模式', en: 'Verbose mode' }, common: false },
      ],
      examples: [
        { cmd: 'scp file.txt user@host:/tmp/', desc: { zh: '上传文件到远程', en: 'Upload file to remote' } },
        { cmd: 'scp user@host:/tmp/file.txt ./', desc: { zh: '从远程下载文件', en: 'Download file from remote' } },
        { cmd: 'scp -r localdir/ user@host:/var/www/', desc: { zh: '递归上传目录', en: 'Upload directory recursively' } },
        { cmd: 'scp -P 2222 -i key.pem file.txt user@host:/tmp/', desc: { zh: '使用非默认端口和私钥', en: 'Use non-default port and key' } },
      ],
      notes: { zh: 'scp 已逐渐被更强大的 rsync 取代。', en: 'scp is gradually being superseded by the more capable rsync.' },
      related: ['rsync', 'ssh', 'sftp']
    },
    {
      name: 'rsync', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '快速、多功能的远程/本地文件同步工具', en: 'Fast, versatile remote/local file sync' },
      syntax: 'rsync [OPTIONS] SOURCE... DEST',
      options: [
        { flag: '-a', desc: { zh: '归档模式（递归、保留符号链接、权限、时间戳等）', en: 'Archive mode (recursive, preserve symlinks, permissions, times)' }, common: true },
        { flag: '-v', desc: { zh: '显示详细过程', en: 'Verbose' }, common: true },
        { flag: '-z', desc: { zh: '传输时压缩', en: 'Compress during transfer' }, common: true },
        { flag: '-P', desc: { zh: '显示进度，支持断点续传', en: 'Show progress and allow resuming' }, common: true },
        { flag: '--delete', desc: { zh: '删除目标端有多余的文件', en: 'Delete extraneous files at destination' }, common: false },
        { flag: '--exclude=PATTERN', desc: { zh: '排除匹配的文件', en: 'Exclude files matching pattern' }, common: true },
        { flag: '-n / --dry-run', desc: { zh: '模拟运行，不实际执行', en: 'Simulate run without making changes' }, common: true },
        { flag: '-e SSH', desc: { zh: '指定远程 shell（如自定义 SSH 端口）', en: 'Specify remote shell' }, common: false },
        { flag: '--progress', desc: { zh: '显示传输进度', en: 'Show transfer progress' }, common: false },
        { flag: '-h', desc: { zh: '人类可读格式输出', en: 'Human-readable output' }, common: false },
      ],
      examples: [
        { cmd: 'rsync -avz local/ user@host:/var/www/', desc: { zh: '同步本地目录到远程', en: 'Sync local directory to remote' } },
        { cmd: 'rsync -avz --delete local/ user@host:/var/www/', desc: { zh: '完全镜像同步（删除目标端多余文件）', en: 'Mirror sync (delete extra files at destination)' } },
        { cmd: 'rsync -avzP --exclude="*.log" src/ dst/', desc: { zh: '同步时排除日志文件，显示进度', en: 'Sync excluding logs, show progress' } },
        { cmd: 'rsync -avzn src/ dst/', desc: { zh: '先模拟运行查看会做什么', en: 'Dry-run to preview changes' } },
        { cmd: 'rsync -avz -e "ssh -p 2222" local/ user@host:/path/', desc: { zh: '通过非标准 SSH 端口同步', en: 'Sync through non-standard SSH port' } },
      ],
      notes: { zh: 'rsync 只传输差异部分，适合大文件和增量备份。末尾的 / 很重要：src/ 同步内容，src 同步目录本身。', en: 'rsync only transfers differences, great for large files and incremental backups. Trailing / matters: src/ syncs contents, src syncs directory itself.' },
      related: ['scp', 'ssh', 'cp']
    },
    {
      name: 'git', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '分布式版本控制工具', en: 'Distributed version control system' },
      syntax: 'git COMMAND [OPTIONS]',
      options: [
        { flag: 'init', desc: { zh: '在当前目录初始化新仓库', en: 'Initialize a new repository' }, common: true },
        { flag: 'clone URL', desc: { zh: '克隆远程仓库', en: 'Clone remote repository' }, common: true },
        { flag: 'status', desc: { zh: '查看工作区状态', en: 'Show working tree status' }, common: true },
        { flag: 'add FILE', desc: { zh: '将文件加入暂存区', en: 'Add files to staging area' }, common: true },
        { flag: 'commit -m MSG', desc: { zh: '提交暂存区的改动', en: 'Commit staged changes' }, common: true },
        { flag: 'push', desc: { zh: '推送本地提交到远程', en: 'Push commits to remote' }, common: true },
        { flag: 'pull', desc: { zh: '拉取远程更新并合并', en: 'Fetch and merge from remote' }, common: true },
        { flag: 'log --oneline', desc: { zh: '简洁查看提交历史', en: 'Concise commit history' }, common: true },
        { flag: 'branch', desc: { zh: '列出/创建/删除分支', en: 'List/create/delete branches' }, common: true },
        { flag: 'checkout BRANCH', desc: { zh: '切换到指定分支', en: 'Switch to branch' }, common: true },
        { flag: 'merge BRANCH', desc: { zh: '合并指定分支到当前分支', en: 'Merge branch into current' }, common: true },
        { flag: 'diff', desc: { zh: '查看改动差异', en: 'Show differences' }, common: true },
        { flag: 'stash', desc: { zh: '临时保存未提交改动', en: 'Stash uncommitted changes' }, common: false },
        { flag: 'reset --hard', desc: { zh: '硬重置到某提交（危险：丢弃改动）', en: 'Hard reset (DANGEROUS: discards changes)' }, common: false },
        { flag: 'rebase BRANCH', desc: { zh: '变基到指定分支', en: 'Rebase onto branch' }, common: false },
      ],
      examples: [
        { cmd: 'git init', desc: { zh: '初始化仓库', en: 'Initialize repository' } },
        { cmd: 'git clone https://github.com/user/repo.git', desc: { zh: '克隆仓库', en: 'Clone repository' } },
        { cmd: 'git add .', desc: { zh: '暂存所有改动', en: 'Stage all changes' } },
        { cmd: 'git commit -m "Fix bug"', desc: { zh: '提交改动', en: 'Commit changes' } },
        { cmd: 'git push origin master', desc: { zh: '推送到 master 分支', en: 'Push to master branch' } },
        { cmd: 'git log --oneline --graph --all', desc: { zh: '图形化查看所有分支历史', en: 'Graphical view of all branches history' } },
        { cmd: 'git checkout -b feature', desc: { zh: '创建并切换到新分支', en: 'Create and switch to new branch' } },
        { cmd: 'git stash pop', desc: { zh: '恢复最近一次 stash', en: 'Restore latest stash' } },
      ],
      notes: { zh: 'git status 是了解当前仓库状态的最佳起点。', en: 'git status is the best starting point to understand repository state.' },
      related: ['git status', 'git log', 'git branch']
    },
    {
      name: 'sudo', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '以超级用户权限执行命令', en: 'Execute command as superuser' },
      syntax: 'sudo [OPTIONS] COMMAND',
      options: [
        { flag: '-u USER', desc: { zh: '以指定用户身份执行', en: 'Run command as specified user' }, common: true },
        { flag: '-i', desc: { zh: '模拟初始登录，进入 root shell', en: 'Simulate initial login, start root shell' }, common: true },
        { flag: '-S', desc: { zh: '从标准输入读取密码', en: 'Read password from stdin' }, common: false },
        { flag: '-E', desc: { zh: '保留当前用户环境变量', en: 'Preserve user environment variables' }, common: false },
        { flag: '-n', desc: { zh: '非交互模式，无密码缓存时失败', en: 'Non-interactive, fail if no password cache' }, common: false },
        { flag: '-l', desc: { zh: '列出当前用户可执行的命令', en: 'List available commands for current user' }, common: false },
      ],
      examples: [
        { cmd: 'sudo apt update', desc: { zh: '以 root 权限更新包列表', en: 'Update package list as root' } },
        { cmd: 'sudo -i', desc: { zh: '进入 root shell', en: 'Enter root shell' } },
        { cmd: 'sudo -u www-data ls /var/www', desc: { zh: '以 www-data 用户身份执行', en: 'Run as www-data user' } },
        { cmd: 'sudo !!', desc: { zh: '用 sudo 重新执行上一条命令', en: 'Re-run last command with sudo' } },
      ],
      notes: { zh: 'sudo 会记录到 /var/log/auth.log。密码默认缓存 15 分钟。', en: 'sudo is logged to /var/log/auth.log. Password cached for 15 minutes by default.' },
      related: ['su', 'whoami', 'chown']
    },
    {
      name: 'curl', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '命令行数据传输工具（HTTP/FTP 等）', en: 'Command line data transfer tool' },
      syntax: 'curl [OPTIONS] URL',
      options: [
        { flag: '-o FILE', desc: { zh: '输出到指定文件（替代重定向）', en: 'Write output to file' }, common: true },
        { flag: '-O', desc: { zh: '使用远程文件名保存', en: 'Save with remote filename' }, common: true },
        { flag: '-L', desc: { zh: '跟随重定向', en: 'Follow redirects' }, common: true },
        { flag: '-I / --head', desc: { zh: '只获取响应头', en: 'Fetch headers only' }, common: true },
        { flag: '-v', desc: { zh: '详细模式，显示请求/响应详情', en: 'Verbose mode' }, common: true },
        { flag: '-s', desc: { zh: '静默模式（配合 -S 显示错误）', en: 'Silent mode' }, common: true },
        { flag: '-S', desc: { zh: '显示错误信息', en: 'Show errors' }, common: false },
        { flag: '-X METHOD', desc: { zh: '指定 HTTP 方法（GET/POST/PUT/DELETE）', en: 'Specify HTTP method' }, common: true },
        { flag: '-d DATA', desc: { zh: '发送 POST 数据', en: 'Send POST data' }, common: true },
        { flag: '-H HEADER', desc: { zh: '添加请求头', en: 'Add request header' }, common: true },
        { flag: '-u USER:PASS', desc: { zh: '基本认证用户名密码', en: 'Basic auth credentials' }, common: false },
        { flag: '--cookie "NAME=VAL"', desc: { zh: '发送 Cookie', en: 'Send cookie' }, common: false },
        { flag: '--max-time SEC', desc: { zh: '最大执行时间', en: 'Maximum time allowed' }, common: false },
        { flag: '--retry NUM', desc: { zh: '失败时重试次数', en: 'Retry on failure' }, common: false },
      ],
      examples: [
        { cmd: 'curl -o file.zip https://example.com/file.zip', desc: { zh: '下载文件', en: 'Download file' } },
        { cmd: 'curl -I https://example.com', desc: { zh: '查看响应头', en: 'Check response headers' } },
        { cmd: 'curl -X POST -d "name=value" https://api.example.com/submit', desc: { zh: '发送 POST 请求', en: 'Send POST request' } },
        { cmd: 'curl -H "Authorization: Bearer TOKEN" https://api.example.com/data', desc: { zh: '发送带认证头的请求', en: 'Request with auth header' } },
        { cmd: 'curl -L -o file.html https://bit.ly/xxx', desc: { zh: '跟随短链接重定向后下载', en: 'Follow short link and download' } },
      ],
      notes: { zh: 'curl 比 wget 更通用，支持更多协议（FTP/SFTP/SMB 等）。', en: 'curl is more versatile than wget, supporting more protocols (FTP/SFTP/SMB etc.).' },
      related: ['wget', 'httpie']
    },
    {
      name: 'wget', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '非交互式网络下载工具', en: 'Non-interactive network downloader' },
      syntax: 'wget [OPTIONS] URL',
      options: [
        { flag: '-O FILE', desc: { zh: '指定输出文件名', en: 'Output to specified file' }, common: true },
        { flag: '-P DIR', desc: { zh: '保存到指定目录', en: 'Save to specified directory' }, common: true },
        { flag: '-c', desc: { zh: '断点续传', en: 'Continue partial download' }, common: true },
        { flag: '-q', desc: { zh: '静默模式', en: 'Quiet mode' }, common: false },
        { flag: '--no-check-certificate', desc: { zh: '忽略 SSL 证书验证', en: 'Ignore SSL certificate check' }, common: false },
        { flag: '-t NUM', desc: { zh: '重试次数', en: 'Number of retries' }, common: false },
        { flag: '-T SEC', desc: { zh: '超时秒数', en: 'Timeout in seconds' }, common: false },
        { flag: '--user=USER --password=PASS', desc: { zh: 'HTTP/FTP 认证', en: 'HTTP/FTP authentication' }, common: false },
        { flag: '-r', desc: { zh: '递归下载', en: 'Recursive download' }, common: false },
        { flag: '--spider', desc: { zh: '不下载，只检查 URL 是否存在', en: 'Check URL without downloading' }, common: false },
      ],
      examples: [
        { cmd: 'wget https://example.com/file.zip', desc: { zh: '下载文件到当前目录', en: 'Download file to current directory' } },
        { cmd: 'wget -c https://example.com/large.iso', desc: { zh: '断点续传大文件', en: 'Resume large file download' } },
        { cmd: 'wget -P /tmp https://example.com/file.zip', desc: { zh: '下载到 /tmp 目录', en: 'Download to /tmp directory' } },
        { cmd: 'wget --spider https://example.com/file.zip', desc: { zh: '检查文件是否存在', en: 'Check if file exists' } },
      ],
      notes: { zh: 'wget 默认会重试，适合不稳定网络。curl 更适合 API 调试。', en: 'wget retries by default, good for unstable networks. curl is better for API debugging.' },
      related: ['curl', 'axel']
    },
    {
      name: 'vim', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '强大的文本编辑器', en: 'Powerful text editor' },
      syntax: 'vim [OPTIONS] [FILE...]',
      options: [
        { flag: '+NUM', desc: { zh: '打开后跳到第 NUM 行', en: 'Open and jump to line NUM' }, common: true },
        { flag: '+/PATTERN', desc: { zh: '打开后跳到第一个匹配', en: 'Open and jump to first match' }, common: false },
        { flag: '-R', desc: { zh: '只读模式', en: 'Read-only mode' }, common: false },
        { flag: '-b', desc: { zh: '二进制模式', en: 'Binary mode' }, common: false },
        { flag: '-d FILE1 FILE2', desc: { zh: 'diff 模式，对比两个文件', en: 'Diff mode, compare two files' }, common: false },
        { flag: '-o[num]', desc: { zh: '水平分割打开多个文件', en: 'Open files in horizontal splits' }, common: false },
        { flag: '-O[num]', desc: { zh: '垂直分割打开多个文件', en: 'Open files in vertical splits' }, common: false },
      ],
      examples: [
        { cmd: 'vim file.txt', desc: { zh: '编辑文件', en: 'Edit file' } },
        { cmd: 'vim +20 file.txt', desc: { zh: '打开并跳到第 20 行', en: 'Open and jump to line 20' } },
        { cmd: 'vim -d file1.txt file2.txt', desc: { zh: '对比两个文件差异', en: 'Compare two files' } },
        { cmd: 'vim -O3 a.txt b.txt c.txt', desc: { zh: '垂直三栏编辑', en: 'Edit three files side by side' } },
      ],
      notes: { zh: 'vim 常用操作：i 进入插入模式，Esc 返回普通模式，:w 保存，:q 退出，:wq 保存并退出，:q! 强制退出不保存。', en: 'vim basics: i=insert, Esc=normal, :w=save, :q=quit, :wq=save&quit, :q!=force quit.' },
      related: ['nano', 'emacs', 'vi']
    },
    {
      name: 'nano', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '简单易用的终端文本编辑器', en: 'Simple terminal text editor' },
      syntax: 'nano [OPTIONS] [FILE]',
      options: [
        { flag: '+NUM', desc: { zh: '跳到指定行', en: 'Jump to line number' }, common: true },
        { flag: '-l', desc: { zh: '显示行号', en: 'Show line numbers' }, common: true },
        { flag: '-i', desc: { zh: '自动缩进', en: 'Auto-indent' }, common: false },
        { flag: '-m', desc: { zh: '启用鼠标支持', en: 'Enable mouse support' }, common: false },
        { flag: '-E', desc: { zh: '将制表符转换为空格', en: 'Convert tabs to spaces' }, common: false },
        { flag: '-T NUM', desc: { zh: '制表符宽度', en: 'Tab width' }, common: false },
      ],
      examples: [
        { cmd: 'nano file.txt', desc: { zh: '编辑文件', en: 'Edit file' } },
        { cmd: 'nano +10 file.txt', desc: { zh: '打开并跳到第 10 行', en: 'Open at line 10' } },
        { cmd: 'nano -l file.txt', desc: { zh: '显示行号编辑', en: 'Edit with line numbers' } },
      ],
      notes: { zh: 'nano 底部始终显示快捷键提示：^O=保存，^X=退出，^K=剪切行，^U=粘贴。', en: 'nano shows shortcuts at bottom: ^O=save, ^X=exit, ^K=cut line, ^U=paste.' },
      related: ['vim', 'pico']
    },
    {
      name: 'awk', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '文本处理语言，按模式扫描和处理文本', en: 'Pattern scanning and processing language' },
      syntax: 'awk [OPTIONS] \'PROGRAM\' [FILE...]',
      options: [
        { flag: '-F SEP', desc: { zh: '指定字段分隔符（默认空格/制表符）', en: 'Field separator (default: space/tab)' }, common: true },
        { flag: '-v VAR=VAL', desc: { zh: '设置变量初始值', en: 'Assign variable value' }, common: true },
        { flag: '-f FILE', desc: { zh: '从文件读取 awk 程序', en: 'Read program from file' }, common: false },
      ],
      examples: [
        { cmd: 'awk \'{print $1}\' file.txt', desc: { zh: '打印每行第一个字段', en: 'Print first field of each line' } },
        { cmd: 'awk -F: \'{print $1}\' /etc/passwd', desc: { zh: '以冒号为分隔符打印用户名', en: 'Print usernames from /etc/passwd' } },
        { cmd: 'awk \'$3 > 100 {print $1, $3}\' file.txt', desc: { zh: '条件筛选：第三字段大于 100 时打印', en: 'Conditional: print when 3rd field > 100' } },
        { cmd: 'awk \'{sum+=$1} END {print sum}\' numbers.txt', desc: { zh: '计算第一列的总和', en: 'Sum of first column' } },
        { cmd: 'awk -F, \'{print NF}\' csv.txt', desc: { zh: '统计 CSV 每行的字段数', en: 'Count fields per CSV line' } },
      ],
      notes: { zh: '$0 表示整行，$1-$n 表示第 n 个字段，NF 是字段总数，NR 是当前行号。', en: '$0=entire line, $1-$n=nth field, NF=field count, NR=line number.' },
      related: ['sed', 'grep', 'cut']
    },
    {
      name: 'sed', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '流编辑器，批量文本替换/删除/插入', en: 'Stream editor for filtering and transforming text' },
      syntax: 'sed [OPTIONS] COMMAND [FILE...]',
      options: [
        { flag: '-i', desc: { zh: '直接修改文件（原地编辑）', en: 'Edit files in place' }, common: true },
        { flag: '-e CMD', desc: { zh: '执行多个命令', en: 'Execute multiple commands' }, common: true },
        { flag: '-n', desc: { zh: '静默模式，只打印 p 命令的输出', en: 'Silent, only print p command output' }, common: true },
        { flag: '-r', desc: { zh: '使用扩展正则表达式', en: 'Use extended regex' }, common: false },
        { flag: '-E', desc: { zh: 'macOS 上的扩展正则（等价于 -r）', en: 'Extended regex on macOS (same as -r)' }, common: false },
      ],
      examples: [
        { cmd: 'sed \'s/foo/bar/g\' file.txt', desc: { zh: '将所有 foo 替换为 bar（输出到屏幕）', en: 'Replace all foo with bar (print to screen)' } },
        { cmd: 'sed -i \'s/foo/bar/g\' file.txt', desc: { zh: '原地替换文件内容', en: 'Replace in file in-place' } },
        { cmd: 'sed -i \'.bak\' \'s/foo/bar/g\' file.txt', desc: { zh: '替换前备份（macOS 需要指定扩展名）', en: 'Backup before replace (macOS needs extension)' } },
        { cmd: 'sed -n \'10,20p\' file.txt', desc: { zh: '只打印第 10-20 行', en: 'Print only lines 10-20' } },
        { cmd: 'sed \'/^#/d\' file.txt', desc: { zh: '删除以 # 开头的注释行', en: 'Delete lines starting with #' } },
        { cmd: 'sed -e \'s/foo/bar/g\' -e \'s/baz/qux/g\' file.txt', desc: { zh: '执行多个替换', en: 'Multiple substitutions' } },
      ],
      notes: { zh: 'macOS 的 sed -i 必须带备份后缀（如 -i \'\'），Linux 可以直接 sed -i。', en: 'macOS sed -i requires backup suffix (e.g., -i \'\'), Linux sed -i works directly.' },
      related: ['awk', 'grep', 'tr']
    },
    {
      name: 'grep', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '文本搜索，支持正则表达式', en: 'Search text using patterns (regex)' },
      syntax: 'grep [OPTIONS] PATTERN [FILE...]',
      options: [
        { flag: '-i', desc: { zh: '忽略大小写', en: 'Case-insensitive search' }, common: true },
        { flag: '-r / -R', desc: { zh: '递归搜索目录', en: 'Recursive directory search' }, common: true },
        { flag: '-n', desc: { zh: '显示匹配行的行号', en: 'Show line numbers' }, common: true },
        { flag: '-v', desc: { zh: '反向匹配，显示不包含模式的行', en: 'Invert match' }, common: true },
        { flag: '-l', desc: { zh: '只列出包含匹配的文件名', en: 'List only filenames with matches' }, common: false },
        { flag: '-c', desc: { zh: '统计每个文件的匹配行数', en: 'Count matching lines per file' }, common: false },
        { flag: '-E', desc: { zh: '使用扩展正则表达式', en: 'Use extended regex' }, common: false },
        { flag: '-o', desc: { zh: '只输出匹配到的部分', en: 'Show only matching parts' }, common: false },
        { flag: '-A NUM', desc: { zh: '显示匹配行后 NUM 行', en: 'Show NUM lines after match' }, common: false },
        { flag: '-B NUM', desc: { zh: '显示匹配行前 NUM 行', en: 'Show NUM lines before match' }, common: false },
        { flag: '-C NUM', desc: { zh: '显示匹配行前后各 NUM 行', en: 'Show NUM lines before and after' }, common: false },
      ],
      examples: [
        { cmd: 'grep -n "error" log.txt', desc: { zh: '搜索 error 并显示行号', en: 'Search with line numbers' } },
        { cmd: 'grep -ri "todo" src/', desc: { zh: '递归搜索 todo', en: 'Recursively search for todo' } },
        { cmd: 'grep -v "^#" config.txt', desc: { zh: '排除注释行', en: 'Exclude comment lines' } },
        { cmd: 'grep -E "(error|warning)" log.txt', desc: { zh: '扩展正则匹配多个词', en: 'Extended regex for multiple keywords' } },
      ],
      notes: { zh: 'grep 默认使用基本正则（BRE），复杂模式用 -E。', en: 'grep uses Basic Regex by default; use -E for Extended Regex.' },
      related: ['find', 'awk', 'sed', 'rg']
    },

    /* ─── macOS 专属 ─── */
    {
      name: 'pbcopy', platforms: ['macos'],
      desc: { zh: '将标准输入复制到剪贴板', en: 'Copy stdin to clipboard' },
      syntax: 'pbcopy [OPTIONS]',
      options: [
        { flag: '-pboard {general | find | font}', desc: { zh: '指定剪贴板（默认 general）', en: 'Specify pasteboard (default: general)' }, common: false },
        { flag: '-Prefer {txt | rtf | ps}', desc: { zh: '指定数据类型偏好', en: 'Specify data type preference' }, common: false },
      ],
      examples: [
        { cmd: 'echo "hello" | pbcopy', desc: { zh: '将文本复制到剪贴板', en: 'Copy text to clipboard' } },
        { cmd: 'cat file.txt | pbcopy', desc: { zh: '将文件内容复制到剪贴板', en: 'Copy file contents to clipboard' } },
        { cmd: 'pbcopy < file.txt', desc: { zh: '重定向方式复制', en: 'Copy via redirection' } },
      ],
      notes: { zh: '与 pbpaste 配合使用。Linux 可用 xclip 或 xsel 替代。', en: 'Use with pbpaste. On Linux, use xclip or xsel instead.' },
      related: ['pbpaste', 'xclip']
    },
    {
      name: 'pbpaste', platforms: ['macos'],
      desc: { zh: '将剪贴板内容输出到标准输出', en: 'Paste clipboard to stdout' },
      syntax: 'pbpaste [OPTIONS]',
      options: [
        { flag: '-pboard {general | find | font}', desc: { zh: '指定剪贴板', en: 'Specify pasteboard' }, common: false },
        { flag: '-Prefer {txt | rtf | ps}', desc: { zh: '指定数据类型偏好', en: 'Specify data type preference' }, common: false },
      ],
      examples: [
        { cmd: 'pbpaste', desc: { zh: '输出剪贴板内容', en: 'Output clipboard contents' } },
        { cmd: 'pbpaste > file.txt', desc: { zh: '将剪贴板保存到文件', en: 'Save clipboard to file' } },
        { cmd: 'pbpaste | grep "keyword"', desc: { zh: '过滤剪贴板内容', en: 'Filter clipboard contents' } },
      ],
      notes: { zh: 'pbpaste 是 pbcopy 的逆操作，组合使用可实现文件内容在终端和 GUI 间的传递。', en: 'pbpaste is the inverse of pbcopy; combine them to transfer data between terminal and GUI.' },
      related: ['pbcopy', 'xclip']
    },
    {
      name: 'open', platforms: ['macos'],
      desc: { zh: '使用默认程序打开文件/目录/URL', en: 'Open files/directories/URLs with default app' },
      syntax: 'open [OPTIONS] FILE...',
      options: [
        { flag: '-a APP', desc: { zh: '指定打开的应用程序', en: 'Open with specific application' }, common: true },
        { flag: '-e', desc: { zh: '用 TextEdit 打开', en: 'Open with TextEdit' }, common: false },
        { flag: '-t', desc: { zh: '用默认文本编辑器打开', en: 'Open with default text editor' }, common: false },
        { flag: '-f', desc: { zh: '从标准输入读取并在默认编辑器打开', en: 'Read from stdin and open in default editor' }, common: false },
        { flag: '-R', desc: { zh: '在 Finder 中显示文件并选中', en: 'Reveal in Finder' }, common: true },
        { flag: '-W', desc: { zh: '等待应用程序退出后再返回', en: 'Wait for app to exit' }, common: false },
        { flag: '-n', desc: { zh: '强制打开新实例（不激活已有窗口）', en: 'Open new instance' }, common: false },
        { flag: '-g', desc: { zh: '不将应用带到前台', en: 'Do not bring app to foreground' }, common: false },
      ],
      examples: [
        { cmd: 'open file.txt', desc: { zh: '用默认程序打开文件', en: 'Open with default app' } },
        { cmd: 'open -a "Visual Studio Code" .', desc: { zh: '用 VS Code 打开当前目录', en: 'Open current directory in VS Code' } },
        { cmd: 'open -R file.txt', desc: { zh: '在 Finder 中定位并选中文件', en: 'Reveal file in Finder' } },
        { cmd: 'open https://example.com', desc: { zh: '用默认浏览器打开 URL', en: 'Open URL in default browser' } },
        { cmd: 'open -a Safari https://example.com', desc: { zh: '用 Safari 打开 URL', en: 'Open URL in Safari' } },
      ],
      notes: { zh: 'open 是 macOS 的"双击"命令行等价物。', en: 'open is the command-line equivalent of double-clicking in macOS.' },
      related: ['pbcopy', 'pbpaste']
    },
    {
      name: 'say', platforms: ['macos'],
      desc: { zh: '文本转语音', en: 'Text-to-speech' },
      syntax: 'say [OPTIONS] [STRING]',
      options: [
        { flag: '-v VOICE', desc: { zh: '指定语音（如 Alex, Ting-Ting, Mei-Jia）', en: 'Specify voice' }, common: true },
        { flag: '-o FILE', desc: { zh: '输出到音频文件（aiff 格式）', en: 'Output to audio file (aiff)' }, common: true },
        { flag: '-f FILE', desc: { zh: '从文件读取文本', en: 'Read text from file' }, common: false },
        { flag: '-r RATE', desc: { zh: '语速（每分钟字数，默认约 175）', en: 'Speech rate in words per minute' }, common: false },
      ],
      examples: [
        { cmd: 'say "Hello world"', desc: { zh: '朗读文本', en: 'Speak text' } },
        { cmd: 'say -v Alex "Hello"', desc: { zh: '使用 Alex 语音', en: 'Use Alex voice' } },
        { cmd: 'say -o output.aiff "Hello"', desc: { zh: '保存为音频文件', en: 'Save as audio file' } },
        { cmd: 'say -f file.txt', desc: { zh: '朗读文件内容', en: 'Speak file contents' } },
      ],
      notes: { zh: 'say --voice=? 列出所有可用语音。', en: 'say --voice=? lists all available voices.' },
      related: []
    },

    /* ─── Windows 专属 ─── */
    {
      name: 'dir', platforms: ['windows'],
      desc: { zh: '列出目录内容（Windows 版 ls）', en: 'List directory contents (Windows ls)' },
      syntax: 'dir [OPTIONS] [PATH]',
      options: [
        { flag: '/w', desc: { zh: '宽列表格式（多列显示）', en: 'Wide list format' }, common: true },
        { flag: '/s', desc: { zh: '递归显示子目录', en: 'Show subdirectories recursively' }, common: true },
        { flag: '/b', desc: { zh: '裸格式，只显示文件名', en: 'Bare format, filenames only' }, common: true },
        { flag: '/a', desc: { zh: '显示隐藏文件和系统文件', en: 'Show hidden and system files' }, common: true },
        { flag: '/o', desc: { zh: '按名称排序', en: 'Sort by name' }, common: false },
        { flag: '/t:w', desc: { zh: '按最后写入时间排序', en: 'Sort by last write time' }, common: false },
        { flag: '/q', desc: { zh: '显示文件所有者', en: 'Show file owner' }, common: false },
        { flag: '/-c', desc: { zh: '显示文件实际大小而非千分位格式', en: 'Show file size without thousands separator' }, common: false },
      ],
      examples: [
        { cmd: 'dir', desc: { zh: '列出当前目录', en: 'List current directory' } },
        { cmd: 'dir /s /b *.txt', desc: { zh: '递归查找所有 .txt 文件（仅文件名）', en: 'Recursively find all .txt files' } },
        { cmd: 'dir /o /s', desc: { zh: '递归并按名称排序', en: 'Recursive, sorted by name' } },
      ],
      notes: { zh: 'dir 是 cmd.exe 内置命令。PowerShell 中可用 Get-ChildItem (gci/ls)。', en: 'dir is a cmd.exe builtin. In PowerShell, use Get-ChildItem (gci/ls).' },
      related: ['cd', 'tree', 'Get-ChildItem']
    },
    {
      name: 'cls', platforms: ['windows'],
      desc: { zh: '清屏', en: 'Clear screen' },
      syntax: 'cls',
      options: [],
      examples: [
        { cmd: 'cls', desc: { zh: '清空命令行屏幕', en: 'Clear command line screen' } },
      ],
      notes: { zh: 'PowerShell 中可用 Clear-Host (clear/cls)。', en: 'In PowerShell, use Clear-Host (clear/cls).' },
      related: ['clear']
    },
    {
      name: 'tasklist', platforms: ['windows'],
      desc: { zh: '显示运行中的进程列表', en: 'Display running processes' },
      syntax: 'tasklist [OPTIONS]',
      options: [
        { flag: '/v', desc: { zh: '显示详细信息', en: 'Show verbose info' }, common: true },
        { flag: '/fi "FILTER"', desc: { zh: '按条件筛选（如 /fi "imagename eq notepad.exe"）', en: 'Filter by condition' }, common: true },
        { flag: '/fo {TABLE | LIST | CSV}', desc: { zh: '输出格式', en: 'Output format' }, common: false },
        { flag: '/svc', desc: { zh: '显示每个进程中的服务', en: 'Show services in each process' }, common: false },
        { flag: '/m MODULE', desc: { zh: '显示加载了指定 DLL 的进程', en: 'Show processes using specified DLL' }, common: false },
      ],
      examples: [
        { cmd: 'tasklist', desc: { zh: '查看所有进程', en: 'Show all processes' } },
        { cmd: 'tasklist /v | findstr "chrome"', desc: { zh: '查找 chrome 进程', en: 'Find chrome processes' } },
        { cmd: 'tasklist /fi "memusage gt 100000"', desc: { zh: '查找内存大于 100MB 的进程', en: 'Find processes using >100MB memory' } },
      ],
      notes: { zh: 'tasklist 类似于 Linux 的 ps aux。', en: 'tasklist is similar to Linux ps aux.' },
      related: ['taskkill', 'findstr', 'Get-Process']
    },
    {
      name: 'taskkill', platforms: ['windows'],
      desc: { zh: '终止进程', en: 'Terminate processes' },
      syntax: 'taskkill [OPTIONS]',
      options: [
        { flag: '/pid PID', desc: { zh: '按 PID 终止', en: 'Terminate by PID' }, common: true },
        { flag: '/im IMAGENAME', desc: { zh: '按进程名终止', en: 'Terminate by image name' }, common: true },
        { flag: '/f', desc: { zh: '强制终止', en: 'Force termination' }, common: true },
        { flag: '/t', desc: { zh: '同时终止子进程', en: 'Terminate process and children' }, common: false },
        { flag: '/fi "FILTER"', desc: { zh: '按条件筛选终止', en: 'Filter before terminating' }, common: false },
      ],
      examples: [
        { cmd: 'taskkill /im notepad.exe', desc: { zh: '终止记事本进程', en: 'Kill notepad' } },
        { cmd: 'taskkill /f /im chrome.exe', desc: { zh: '强制终止 Chrome', en: 'Force kill Chrome' } },
        { cmd: 'taskkill /pid 1234 /f', desc: { zh: '强制终止指定 PID', en: 'Force kill specific PID' } },
      ],
      notes: { zh: 'taskkill 类似于 Linux 的 kill 命令。', en: 'taskkill is similar to Linux kill command.' },
      related: ['tasklist', 'Get-Process', 'Stop-Process']
    },
    {
      name: 'ipconfig', platforms: ['windows'],
      desc: { zh: '显示网络配置信息', en: 'Display network configuration' },
      syntax: 'ipconfig [OPTIONS]',
      options: [
        { flag: '/all', desc: { zh: '显示完整配置', en: 'Show full configuration' }, common: true },
        { flag: '/release', desc: { zh: '释放当前获取的 IP 地址（DHCP）', en: 'Release current IP (DHCP)' }, common: true },
        { flag: '/renew', desc: { zh: '重新获取 IP 地址（DHCP）', en: 'Renew IP address (DHCP)' }, common: true },
        { flag: '/flushdns', desc: { zh: '刷新 DNS 缓存', en: 'Flush DNS cache' }, common: true },
        { flag: '/displaydns', desc: { zh: '显示 DNS 缓存内容', en: 'Display DNS cache' }, common: false },
      ],
      examples: [
        { cmd: 'ipconfig', desc: { zh: '查看基本网络配置', en: 'Show basic network config' } },
        { cmd: 'ipconfig /all', desc: { zh: '查看完整网络配置', en: 'Show full network config' } },
        { cmd: 'ipconfig /flushdns', desc: { zh: '刷新 DNS 缓存', en: 'Flush DNS cache' } },
        { cmd: 'ipconfig /release && ipconfig /renew', desc: { zh: '重新获取 IP', en: 'Release and renew IP' } },
      ],
      notes: { zh: 'ipconfig /flushdns 解决 DNS 解析问题非常有效。', en: 'ipconfig /flushdns is very effective for DNS resolution issues.' },
      related: ['ping', 'tracert', 'nslookup']
    },
    {
      name: 'ping', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '测试网络连通性', en: 'Test network connectivity' },
      syntax: 'ping [OPTIONS] HOST',
      options: [
        { flag: '-c COUNT', desc: { zh: '发送指定次数后停止（Linux/macOS）', en: 'Stop after sending COUNT packets' }, common: true },
        { flag: '-n COUNT', desc: { zh: 'Windows 版：发送次数', en: 'Windows: number of packets' }, common: true },
        { flag: '-i SEC', desc: { zh: '间隔秒数（Linux/macOS）', en: 'Interval between packets' }, common: false },
        { flag: '-t', desc: { zh: 'Windows：持续 ping 直到 Ctrl+C', en: 'Windows: ping until Ctrl+C' }, common: true },
        { flag: '-s SIZE', desc: { zh: '指定数据包大小', en: 'Specify packet size' }, common: false },
        { flag: '-W MS', desc: { zh: '等待响应超时毫秒数', en: 'Wait timeout in milliseconds' }, common: false },
      ],
      examples: [
        { cmd: 'ping google.com', desc: { zh: '测试到 Google 的连通性', en: 'Test connectivity to Google' } },
        { cmd: 'ping -c 4 google.com', desc: { zh: 'Linux/macOS：ping 4 次', en: 'Linux/macOS: ping 4 times' } },
        { cmd: 'ping -n 4 google.com', desc: { zh: 'Windows：ping 4 次', en: 'Windows: ping 4 times' } },
        { cmd: 'ping -t google.com', desc: { zh: 'Windows：持续 ping', en: 'Windows: continuous ping' } },
      ],
      notes: { zh: 'Linux/macOS 默认无限 ping，Windows 默认 4 次。', en: 'Linux/macOS pings indefinitely by default; Windows defaults to 4.' },
      related: ['traceroute', 'tracert', 'curl']
    },
    {
      name: 'systeminfo', platforms: ['windows'],
      desc: { zh: '显示详细的系统配置信息', en: 'Display detailed system configuration' },
      syntax: 'systeminfo [OPTIONS]',
      options: [
        { flag: '/fo {TABLE | LIST | CSV}', desc: { zh: '输出格式', en: 'Output format' }, common: false },
        { flag: '/nh', desc: { zh: '不显示列标题', en: 'No column headers' }, common: false },
        { flag: '/s COMPUTER', desc: { zh: '查询远程计算机', en: 'Query remote computer' }, common: false },
      ],
      examples: [
        { cmd: 'systeminfo', desc: { zh: '显示完整系统信息', en: 'Show complete system info' } },
        { cmd: 'systeminfo | findstr /B /C:"OS"', desc: { zh: '只查看操作系统信息', en: 'Show only OS info' } },
      ],
      notes: { zh: 'systeminfo 输出信息非常丰富，配合 findstr 过滤。', en: 'systeminfo output is very rich; filter with findstr.' },
      related: ['msinfo32', 'wmic']
    },
    {
      name: 'robocopy', platforms: ['windows'],
      desc: { zh: '强大的文件复制工具（支持断点续传、镜像同步）', en: 'Robust file copy with resume and mirror' },
      syntax: 'robocopy SOURCE DEST [FILES] [OPTIONS]',
      options: [
        { flag: '/S', desc: { zh: '复制子目录（不含空目录）', en: 'Copy subdirectories (excluding empty)' }, common: true },
        { flag: '/E', desc: { zh: '复制子目录（含空目录）', en: 'Copy subdirectories (including empty)' }, common: true },
        { flag: '/MIR', desc: { zh: '镜像同步（相当于 /E + /PURGE，删除目标端多余文件）', en: 'Mirror mode (/E + /PURGE)' }, common: true },
        { flag: '/Z', desc: { zh: '断点续传模式', en: 'Restartable mode' }, common: true },
        { flag: '/MT:N', desc: { zh: '使用 N 个线程并行复制', en: 'Multi-threaded with N threads' }, common: true },
        { flag: '/XD DIRS', desc: { zh: '排除指定目录', en: 'Exclude directories' }, common: false },
        { flag: '/XF FILES', desc: { zh: '排除指定文件', en: 'Exclude files' }, common: false },
        { flag: '/MAX:N', desc: { zh: '最大文件大小（字节）', en: 'Maximum file size' }, common: false },
        { flag: '/MIN:N', desc: { zh: '最小文件大小（字节）', en: 'Minimum file size' }, common: false },
        { flag: '/LOG:FILE', desc: { zh: '输出日志到文件', en: 'Output log to file' }, common: false },
        { flag: '/NP', desc: { zh: '不显示进度百分比', en: 'No progress percentage' }, common: false },
        { flag: '/R:N', desc: { zh: '失败时重试 N 次（默认 1M）', en: 'Retry N times on failure' }, common: false },
        { flag: '/W:N', desc: { zh: '重试间隔 N 秒（默认 30）', en: 'Wait N seconds between retries' }, common: false },
      ],
      examples: [
        { cmd: 'robocopy C:\\source D:\\backup /MIR', desc: { zh: '镜像同步两个目录', en: 'Mirror sync two directories' } },
        { cmd: 'robocopy C:\\source D:\\backup /E /Z /MT:8', desc: { zh: '断点续传并行复制', en: 'Resumeable multi-threaded copy' } },
        { cmd: 'robocopy C:\\source D:\\backup /E /XF *.tmp *.log', desc: { zh: '复制时排除临时文件和日志', en: 'Copy excluding temp and log files' } },
      ],
      notes: { zh: 'robocopy 是 Windows 上最强大的文件复制工具，退出码 1-7 表示成功。', en: 'robocopy is the most powerful file copy tool on Windows; exit codes 1-7 indicate success.' },
      related: ['xcopy', 'copy', 'move']
    },

    /* ─── 跨平台通用 ─── */
    {
      name: 'ping', platforms: ['linux', 'macos', 'unix', 'windows'],
      desc: { zh: '测试网络连通性', en: 'Test network connectivity' },
      syntax: 'ping [OPTIONS] HOST',
      options: [
        { flag: '-c COUNT', desc: { zh: '发送指定次数后停止（Linux/macOS）', en: 'Stop after sending COUNT packets' }, common: true },
        { flag: '-n COUNT', desc: { zh: 'Windows 版：发送次数', en: 'Windows: number of packets' }, common: true },
        { flag: '-i SEC', desc: { zh: '间隔秒数（Linux/macOS）', en: 'Interval between packets' }, common: false },
        { flag: '-t', desc: { zh: 'Windows：持续 ping 直到 Ctrl+C', en: 'Windows: ping until Ctrl+C' }, common: true },
        { flag: '-s SIZE', desc: { zh: '指定数据包大小', en: 'Specify packet size' }, common: false },
        { flag: '-W MS', desc: { zh: '等待响应超时毫秒数', en: 'Wait timeout in milliseconds' }, common: false },
      ],
      examples: [
        { cmd: 'ping google.com', desc: { zh: '测试到 Google 的连通性', en: 'Test connectivity to Google' } },
        { cmd: 'ping -c 4 google.com', desc: { zh: 'Linux/macOS：ping 4 次', en: 'Linux/macOS: ping 4 times' } },
        { cmd: 'ping -n 4 google.com', desc: { zh: 'Windows：ping 4 次', en: 'Windows: ping 4 times' } },
        { cmd: 'ping -t google.com', desc: { zh: 'Windows：持续 ping', en: 'Windows: continuous ping' } },
      ],
      notes: { zh: 'Linux/macOS 默认无限 ping，Windows 默认 4 次。', en: 'Linux/macOS pings indefinitely by default; Windows defaults to 4.' },
      related: ['traceroute', 'tracert', 'curl']
    },
    {
      name: 'clear', platforms: ['linux', 'macos', 'unix'],
      desc: { zh: '清屏', en: 'Clear terminal screen' },
      syntax: 'clear',
      options: [],
      examples: [
        { cmd: 'clear', desc: { zh: '清空终端屏幕', en: 'Clear terminal screen' } },
        { cmd: 'Ctrl+L', desc: { zh: '快捷键等价于 clear', en: 'Keyboard shortcut equivalent' } },
      ],
      notes: { zh: 'clear 只是清屏，不删除历史。', en: 'clear only clears the screen, does not delete history.' },
      related: ['cls', 'reset']
    },
  ];

  /* 去重（按名称，保留第一个） */
  var seen = {};
  COMMANDS = COMMANDS.filter(function (cmd) {
    if (seen[cmd.name]) return false;
    seen[cmd.name] = true;
    return true;
  });

  /* ========== DOM 引用 ========== */
  var $search = document.getElementById('cr-search');
  var $platforms = document.getElementById('cr-platforms');
  var $list = document.getElementById('cr-list');
  var $stats = document.getElementById('cr-stats');

  /* ========== 状态 ========== */
  var activePlatform = 'all';
  var expandedCard = null;

  /* ========== 初始化平台筛选 ========== */
  function initPlatforms() {
    if (!$platforms) return;
    var platforms = [
      { key: 'all', label: T('all-platforms') },
      { key: 'linux', label: T('platform-linux') },
      { key: 'macos', label: T('platform-macos') },
      { key: 'unix', label: T('platform-unix') },
      { key: 'windows', label: T('platform-windows') },
    ];
    var html = '';
    platforms.forEach(function (p) {
      var cls = p.key === 'all' ? 'cr-platform-chip cr-active' : 'cr-platform-chip';
      html += '<button class="' + cls + '" data-platform="' + p.key + '">' + escapeHtml(p.label) + '</button>';
    });
    $platforms.innerHTML = html;

    $platforms.querySelectorAll('.cr-platform-chip').forEach(function (btn) {
      btn.addEventListener('click', function () {
        $platforms.querySelectorAll('.cr-platform-chip').forEach(function (b) { b.classList.remove('cr-active'); });
        btn.classList.add('cr-active');
        activePlatform = btn.getAttribute('data-platform');
        renderList();
      });
    });
  }

  /* ========== 渲染命令列表 ========== */
  function renderList() {
    var query = ($search && $search.value || '').toLowerCase().trim();
    var filtered = COMMANDS.filter(function (cmd) {
      /* 平台筛选 */
      if (activePlatform !== 'all' && cmd.platforms.indexOf(activePlatform) === -1) return false;
      /* 搜索 */
      if (!query) return true;
      var searchIn = (cmd.name + ' ' +
        (cmd.desc[LANG] || cmd.desc.en || '') + ' ' +
        cmd.options.map(function (o) { return o.flag + ' ' + (o.desc[LANG] || o.desc.en || ''); }).join(' ')).toLowerCase();
      return searchIn.indexOf(query) !== -1;
    });

    if ($stats) $stats.textContent = filtered.length + ' ' + T('commands-count');

    if (filtered.length === 0) {
      $list.innerHTML = '<div class="cr-empty">' +
        '<i class="fas fa-search"></i>' +
        '<div>' + escapeHtml(T('no-results')) + '</div>' +
        '<div style="font-size:0.85rem;margin-top:0.3rem;">' + escapeHtml(T('try-search')) + '</div>' +
        '</div>';
      return;
    }

    var html = '';
    filtered.forEach(function (cmd) {
      html += renderCard(cmd);
    });
    $list.innerHTML = html;

    /* 绑定卡片展开 */
    $list.querySelectorAll('.cr-card-header').forEach(function (header) {
      header.addEventListener('click', function () {
        var card = header.parentElement;
        var isOpen = card.classList.contains('cr-open');
        /* 关闭其他 */
        $list.querySelectorAll('.cr-card.cr-open').forEach(function (c) { c.classList.remove('cr-open'); });
        if (!isOpen) {
          card.classList.add('cr-open');
          expandedCard = card;
        } else {
          expandedCard = null;
        }
      });
    });

    /* 绑定复制按钮 */
    $list.querySelectorAll('.cr-copy-btn').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var code = btn.getAttribute('data-cmd');
        if (code) {
          navigator.clipboard.writeText(code).then(function () {
            var orig = btn.textContent;
            btn.textContent = T('copied');
            setTimeout(function () { btn.textContent = orig; }, 1500);
          });
        }
      });
    });
  }

  function renderCard(cmd) {
    var badges = cmd.platforms.map(function (p) {
      return '<span class="cr-cmd-badge">' + escapeHtml(p) + '</span>';
    }).join('');

    /* 语法高亮 */
    var syntaxHtml = highlightSyntax(cmd.syntax);

    /* 参数表格 */
    var optsHtml = '';
    if (cmd.options && cmd.options.length) {
      optsHtml += '<div class="cr-section"><div class="cr-section-title">' + escapeHtml(T('options')) + '</div>';
      optsHtml += '<table class="cr-options-table"><thead><tr>' +
        '<th>' + escapeHtml(T('flag')) + '</th>' +
        '<th>' + escapeHtml(T('description')) + '</th></tr></thead><tbody>';
      cmd.options.forEach(function (opt) {
        var commonBadge = opt.common ? '<span class="cr-opt-common">' + escapeHtml(T('common')) + '</span>' : '';
        optsHtml += '<tr><td class="cr-opt-flag">' + escapeHtml(opt.flag) + commonBadge + '</td>' +
          '<td>' + escapeHtml(opt.desc[LANG] || opt.desc.en || '') + '</td></tr>';
      });
      optsHtml += '</tbody></table></div>';
    }

    /* 示例 */
    var examplesHtml = '';
    if (cmd.examples && cmd.examples.length) {
      examplesHtml += '<div class="cr-section"><div class="cr-section-title">' + escapeHtml(T('examples')) + '</div>';
      cmd.examples.forEach(function (ex) {
        examplesHtml += '<div class="cr-example">' +
          '<div class="cr-example-desc">' + escapeHtml(ex.desc[LANG] || ex.desc.en || '') + '</div>' +
          '<div class="cr-example-cmd"><code>' + escapeHtml(ex.cmd) + '</code>' +
          '<button class="cr-copy-btn" data-cmd="' + escapeHtml(ex.cmd) + '">' + escapeHtml(T('copy')) + '</button></div>' +
          '</div>';
      });
      examplesHtml += '</div>';
    }

    /* 注意事项 */
    var notesHtml = '';
    if (cmd.notes) {
      notesHtml = '<div class="cr-section"><div class="cr-section-title">' + escapeHtml(T('notes')) + '</div>' +
        '<div class="cr-note">' + escapeHtml(cmd.notes[LANG] || cmd.notes.en || '') + '</div></div>';
    }

    /* 相关命令 */
    var relatedHtml = '';
    if (cmd.related && cmd.related.length) {
      relatedHtml = '<div class="cr-section"><div class="cr-section-title">' + escapeHtml(T('related')) + '</div>' +
        '<div style="display:flex;gap:0.4rem;flex-wrap:wrap;">' +
        cmd.related.map(function (r) {
          return '<span class="cr-cmd-badge" style="cursor:pointer;" data-related="' + escapeHtml(r) + '">' + escapeHtml(r) + '</span>';
        }).join('') + '</div></div>';
    }

    return '<div class="cr-card">' +
      '<div class="cr-card-header">' +
      '<span class="cr-cmd-name">' + escapeHtml(cmd.name) + '</span>' +
      '<span class="cr-cmd-desc">' + escapeHtml(cmd.desc[LANG] || cmd.desc.en || '') + '</span>' +
      '<span class="cr-cmd-platforms">' + badges + '</span>' +
      '<span class="cr-expand-icon"><i class="fas fa-chevron-right"></i></span>' +
      '</div>' +
      '<div class="cr-detail">' +
      '<div class="cr-section"><div class="cr-section-title">' + escapeHtml(T('syntax')) + '</div>' +
      '<div class="cr-syntax">' + syntaxHtml + '</div></div>' +
      optsHtml + examplesHtml + notesHtml + relatedHtml +
      '</div>' +
      '</div>';
  }

  /* 简单语法高亮 */
  function highlightSyntax(syntax) {
    return syntax
      .replace(/\[/g, '<span class="cr-comment">[</span>')
      .replace(/\]/g, '<span class="cr-comment">]</span>')
      .replace(/\{([^}]+)\}/g, '<span class="cr-opt">{$1}</span>')
      .replace(/\b([A-Z][A-Z_]+)\b/g, '<span class="cr-arg">$1</span>')
      .replace(/\b(\w+)\b/g, function (m, w) {
        if (['OPTIONS', 'FILE', 'DIRECTORY', 'PATH', 'HOST', 'USER', 'PORT', 'PATTERN', 'COMMAND', 'URL', 'DEST', 'SOURCE', 'MSG', 'NUM', 'SEC', 'MS', 'PID', 'MODE', 'SIZE', 'APP', 'BRANCH', 'DATA', 'VOICE', 'RATE', 'STAMP', 'COUNT', 'TYPE'].indexOf(w) !== -1) {
          return '<span class="cr-arg">' + w + '</span>';
        }
        return '<span class="cr-kw">' + w + '</span>';
      });
  }

  /* ========== 搜索事件 ========== */
  if ($search) {
    $search.addEventListener('input', function () {
      renderList();
    });
    $search.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        $search.value = '';
        renderList();
      }
    });
  }

  /* ========== 相关命令点击 ========== */
  if ($list) {
    $list.addEventListener('click', function (e) {
      var badge = e.target.closest('[data-related]');
      if (!badge) return;
      var name = badge.getAttribute('data-related');
      if ($search) {
        $search.value = name;
        renderList();
        /* 高亮目标卡片 */
        setTimeout(function () {
          var target = $list.querySelector('.cr-cmd-name');
          if (target) {
            var card = target.closest('.cr-card');
            if (card) {
              card.classList.add('cr-open');
              card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }
        }, 50);
      }
    });
  }

  /* ========== 工具函数 ========== */
  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ========== 启动 ========== */
  initPlatforms();
  renderList();
})();
