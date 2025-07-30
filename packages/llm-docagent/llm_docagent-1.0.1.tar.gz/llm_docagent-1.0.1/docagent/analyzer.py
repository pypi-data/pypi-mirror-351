import os
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
@dataclass
class CodeFile:
    """Represents a code file with metadata"""
    path: Path
    relative_path: str
    extension: str
    size: int
    lines: int
    content: str
    language: str
    modified: datetime
    hash: str = ""

    def __post_init__(self):
        """Calculate file hash after initialization"""
        self.hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
class CodeAnalyzer:
    """Enhanced code analyzer with better language detection and filtering"""
    
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript', '.jsx': 'javascript',
        '.ts': 'typescript', '.tsx': 'typescript',
        '.java': 'java', '.kt': 'kotlin', '.scala': 'scala',
        '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
        '.c': 'c', '.h': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.sh': 'bash', '.bash': 'bash', '.zsh': 'bash',
        '.yml': 'yaml', '.yaml': 'yaml',
        '.json': 'json',
        '.md': 'markdown', '.rst': 'rst',
        '.html': 'html', '.htm': 'html',
        '.css': 'css', '.scss': 'scss', '.sass': 'sass',
        '.sql': 'sql',
        '.r': 'r',
        '.swift': 'swift',
        '.dart': 'dart',
        '.lua': 'lua',
        '.xml': 'xml',
        '.dockerfile': 'dockerfile'
    }
    
    IGNORE_PATTERNS = {
        'directories': {
            # Version control
            '.git', '.svn', '.hg', '.bzr',
            # Python
            '__pycache__', '.pytest_cache', '.tox', '.mypy_cache',
            'venv', '.venv', 'env', '.env', 'myenv', '.myenv', 'virtualenv',
            # Node.js
            'node_modules', '.npm', '.yarn',
            # Build directories
            'build', 'dist', 'target', 'bin', 'obj', 'out',
            # IDE/Editor
            '.idea', '.vscode', '.vs', '.atom', '.sublime-project',
            # OS
            '.DS_Store', 'Thumbs.db',
            # Other
            'coverage', '.nyc_output', '.next', '.nuxt', 'tmp', 'temp',
            # Java
            '.gradle', '.m2',
            # Rust
            'target',
            # Go
            'vendor'
        },
        'files': {
            # Environment and config
            '.env', '.env.local', '.env.development', '.env.production',
            '.env.staging', '.env.test', '.env.example', '.env.sample',
            # Version control
            '.gitignore', '.gitkeep', '.gitattributes', '.gitmodules',
            '.hgignore', '.svnignore',
            # OS files
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            # Compiled files
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
            # Logs
            '*.log', '*.out', '*.err',
            # Cache and temp
            '*.tmp', '*.temp', '*.cache', '*.bak', '*.swp', '*.swo',
            # Lock files
            'package-lock.json', 'yarn.lock', 'Pipfile.lock', 'poetry.lock',
            'composer.lock', 'Gemfile.lock', 'Cargo.lock',
            # IDE files
            '*.iml', '*.ipr', '*.iws',
            # Archives
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
            # Images (usually not code)
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.svg', '*.ico',
            '*.bmp', '*.tiff', '*.webp',
            # Media
            '*.mp4', '*.avi', '*.mov', '*.wmv', '*.flv', '*.mp3', '*.wav',
            # Documents
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx'
        },
        'exact_names': {
            # Exact file names to ignore
            'LICENSE', 'CHANGELOG', 'HISTORY', 'AUTHORS', 'CONTRIBUTORS',
            'MANIFEST', 'INSTALL', 'NEWS', 'COPYING', 'NOTICE'
        }
    }
    
    # Files that should be considered for documentation even if they match ignore patterns
    DOCUMENTATION_FILES = {
        'readme.md', 'readme.txt', 'readme.rst', 'readme',
        'docs.md', 'documentation.md', 'guide.md',
        'changelog.md', 'history.md', 'license.md',
        'contributing.md', 'code_of_conduct.md'
    }
    
    # Configuration files that are important for project understanding
    CONFIG_FILES = {
        'package.json', 'setup.py', 'requirements.txt', 'pyproject.toml',
        'pom.xml', 'build.gradle', 'cargo.toml', 'go.mod',
        'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        'makefile', 'cmake.txt', '.travis.yml', '.github'
    }
    
    def __init__(self, root_directory: str):
        self.root = Path(root_directory).resolve()
        self.files: List[CodeFile] = []
        self.max_file_size = 2 * 1024 * 1024  # 2MB limit
        self.max_total_content = 100 * 1024  # 100KB total for LLM context
        self.min_file_size = 1  # Ignore empty files
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase with progress tracking"""
        print(f"🔍 Analyzing codebase: {self.root}")
        
        self.files = []
        
        # Check if directory exists and is accessible
        if not self.root.exists():
            raise ValueError(f"Directory does not exist: {self.root}")
        
        if not self.root.is_dir():
            raise ValueError(f"Path is not a directory: {self.root}")
        
        # Check if directory is empty or only contains ignored files
        if self._is_directory_empty_or_ignored():
            print("  Directory appears to be empty or contains only ignored files")
            return self._create_empty_analysis()
        
        file_count = self._count_files()
        print(f"   Found {file_count} potential files to analyze")
        
        if file_count == 0:
            print("  No analyzable files found")
            return self._create_empty_analysis()
        
        self._scan_directory(self.root)
        
        if not self.files:
            print("  No valid code files found after filtering")
            return self._create_empty_analysis()
        
        analysis = {
            "project_root": str(self.root),
            "total_files": len(self.files),
            "languages": self._get_language_stats(),
            "structure": self._get_directory_structure(),
            "files": [self._file_to_dict(f) for f in self.files],
            "main_files": self._identify_main_files(),
            "project_type": self._detect_project_type(),
            "analysis_timestamp": datetime.now().isoformat(),
            "total_lines": sum(f.lines for f in self.files),
            "total_size": sum(f.size for f in self.files)
        }
        
        print(f"   ✅ Analyzed {len(self.files)} code files")
        print(f"   📊 Languages: {', '.join(analysis['languages'].keys())}")
        print(f"   📝 Total lines: {analysis['total_lines']:,}")
        
        return analysis
    
    def _is_directory_empty_or_ignored(self) -> bool:
        """Check if directory is empty or contains only ignored files/directories"""
        try:
            items = list(self.root.iterdir())
            if not items:
                return True
            
            # Check if all items are ignored
            for item in items:
                if item.is_file():
                    if self._should_analyze_file(item):
                        return False
                elif item.is_dir():
                    if not self._should_ignore_directory(item):
                        # Recursively check subdirectories
                        sub_analyzer = CodeAnalyzer(str(item))
                        if not sub_analyzer._is_directory_empty_or_ignored():
                            return False
            
            return True
        except (PermissionError, OSError):
            return True
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create analysis structure for empty directories"""
        return {
            "project_root": str(self.root),
            "total_files": 0,
            "languages": {},
            "structure": {},
            "files": [],
            "main_files": [],
            "project_type": "empty",
            "analysis_timestamp": datetime.now().isoformat(),
            "total_lines": 0,
            "total_size": 0
        }
    
    def _count_files(self) -> int:
        """Count total files for progress tracking"""
        count = 0
        try:
            for item in self.root.rglob("*"):
                if item.is_file() and self._should_analyze_file(item):
                    count += 1
        except (PermissionError, OSError):
            pass
        return count
    
    def _scan_directory(self, directory: Path):
        """Recursively scan directory for code files"""
        try:
            items = list(directory.iterdir())
            
            for item in items:
                # Skip hidden files/directories unless they're important
                if item.name.startswith('.') and item.name.lower() not in self.DOCUMENTATION_FILES:
                    continue
                
                if item.is_dir():
                    if not self._should_ignore_directory(item):
                        self._scan_directory(item)
                elif item.is_file():
                    if self._should_analyze_file(item):
                        code_file = self._analyze_file(item)
                        if code_file:
                            self.files.append(code_file)
                            
        except (PermissionError, OSError) as e:
            print(f"   Skipped {directory}: {e}")
    
    def _should_ignore_directory(self, dir_path: Path) -> bool:
        """Check if directory should be ignored"""
        dir_name = dir_path.name.lower()
        
        # Check against ignore patterns
        if dir_name in self.IGNORE_PATTERNS['directories']:
            return True
        
        # Check for environment-related directories
        env_patterns = ['venv', 'env', 'virtualenv', '.venv', '.env']
        for pattern in env_patterns:
            if pattern in dir_name:
                return True
        
        # Check for build/cache directories
        build_patterns = ['build', 'dist', 'target', 'cache', 'temp', 'tmp']
        for pattern in build_patterns:
            if pattern in dir_name:
                return True
        
        return False
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Enhanced file filtering with better environment file detection"""
        file_name = file_path.name
        file_name_lower = file_name.lower()
        
        # Check file size first (skip empty files)
        try:
            stat_info = file_path.stat()
            if stat_info.st_size < self.min_file_size:
                return False
            if stat_info.st_size > self.max_file_size:
                return False
        except OSError:
            return False
        
        # Always include important documentation files
        if file_name_lower in self.DOCUMENTATION_FILES:
            return True
        
        # Always include important configuration files
        if file_name_lower in self.CONFIG_FILES:
            return True
        
        # Skip environment files
        if file_name_lower.startswith('.env'):
            return False
        
        # Skip files in exact_names ignore list
        if file_name in self.IGNORE_PATTERNS['exact_names']:
            return False
        
        # Check file name patterns
        for pattern in self.IGNORE_PATTERNS['files']:
            if pattern.startswith('*'):
                # Pattern like *.pyc
                if file_name_lower.endswith(pattern[1:]):
                    return False
            elif file_name_lower == pattern:
                return False
        
        # Check extension
        extension = file_path.suffix.lower()
        if extension not in self.LANGUAGE_MAP:
            return False
        
        # Additional checks for specific file types
        if extension == '.json':
            # Skip large package-lock.json and similar files
            if 'lock' in file_name_lower or file_name_lower in ['package-lock.json', 'yarn.lock']:
                return False
        
        return True
    
    def _analyze_file(self, file_path: Path) -> Optional[CodeFile]:
        """Analyze a single code file with better error handling"""
        try:
            stat_info = file_path.stat()
            
            # Try different encodings
            content = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if content is None:
                return None
            
            # Skip files that are mostly binary or have very little content
            if len(content.strip()) < 10:  # Skip nearly empty files
                return None
            
            # Calculate lines more accurately
            lines = len([line for line in content.split('\n') if line.strip()])
            
            return CodeFile(
                path=file_path,
                relative_path=str(file_path.relative_to(self.root)),
                extension=file_path.suffix.lower(),
                size=stat_info.st_size,
                lines=lines,
                content=content,
                language=self.LANGUAGE_MAP.get(file_path.suffix.lower(), 'text'),
                modified=datetime.fromtimestamp(stat_info.st_mtime)
            )
        
        except (PermissionError, OSError, UnicodeError) as e:
            # Only print warning for unexpected errors
            if not isinstance(e, PermissionError):
                print(f"   Could not analyze {file_path}: {e}")
            return None
    
    def _get_language_stats(self) -> Dict[str, Dict[str, int]]:
        """Get comprehensive language statistics"""
        stats = {}
        for file in self.files:
            lang = file.language
            if lang not in stats:
                stats[lang] = {"files": 0, "lines": 0, "size": 0}
            
            stats[lang]["files"] += 1
            stats[lang]["lines"] += file.lines
            stats[lang]["size"] += file.size
        
        # Sort by number of lines
        return dict(sorted(stats.items(), key=lambda x: x[1]["lines"], reverse=True))
    
    def _get_directory_structure(self) -> Dict[str, Any]:
        """Get enhanced directory structure"""
        structure = {}
        for file in self.files:
            parts = Path(file.relative_path).parts
            current = structure
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {"type": "directory", "children": {}}
                current = current[part]["children"]
            
            current[parts[-1]] = {
                "type": "file",
                "language": file.language,
                "size": file.size,
                "lines": file.lines
            }
        
        return structure
    
    def _identify_main_files(self) -> List[Dict[str, Any]]:
        """Identify main/entry point files"""
        main_files = []
        
        main_patterns = [
            'main.py', 'app.py', '__main__.py', 'run.py', 'manage.py',
            'index.js', 'main.js', 'app.js', 'server.js', 'index.ts',
            'main.go', 'main.cpp', 'main.c', 'main.java', 'app.java',
            'package.json', 'setup.py', 'requirements.txt', 'pyproject.toml',
            'pom.xml', 'build.gradle', 'cargo.toml', 'go.mod',
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'makefile', 'cmake.txt',
            'readme.md', 'readme.txt', 'readme.rst'
        ]
        
        for file in self.files:
            file_name_lower = file.path.name.lower()
            if file_name_lower in main_patterns:
                main_files.append({
                    "path": file.relative_path,
                    "language": file.language,
                    "size": file.size,
                    "lines": file.lines,
                    "type": "main_file"
                })
        
        # Sort by importance (readme first, then config, then code)
        def sort_key(item):
            name = item["path"].lower()
            if "readme" in name:
                return (0, name)
            elif any(config in name for config in ["package.json", "setup.py", "pom.xml"]):
                return (1, name)
            elif "main" in name or "app" in name:
                return (2, name)
            else:
                return (3, name)
        
        return sorted(main_files, key=sort_key)
    
    def _detect_project_type(self) -> str:
        """Detect project type based on files"""
        if not self.files:
            return "empty"
        
        type_indicators = {
            "python": ["setup.py", "requirements.txt", "pyproject.toml", "__init__.py", "manage.py"],
            "javascript": ["package.json", "index.js", "app.js"],
            "typescript": ["tsconfig.json", "package.json", ".ts", ".tsx"],
            "java": ["pom.xml", "build.gradle", ".java"],
            "go": ["go.mod", "go.sum", "main.go"],
            "rust": ["Cargo.toml", "Cargo.lock", ".rs"],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "web": ["index.html", ".css", ".js", ".html"]
        }
        
        file_names = [f.path.name.lower() for f in self.files]
        file_extensions = [f.extension for f in self.files]
        
        scores = {}
        for project_type, indicators in type_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator.startswith('.'):
                    score += file_extensions.count(indicator) * 2
                else:
                    score += file_names.count(indicator) * 5
            scores[project_type] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "mixed"
    
    def _file_to_dict(self, file: CodeFile) -> Dict[str, Any]:
        """Convert CodeFile to dictionary with more info"""
        return {
            "path": file.relative_path,
            "language": file.language,
            "size": file.size,
            "lines": file.lines,
            "modified": file.modified.isoformat(),
            "hash": file.hash
        }
    
    def get_context_for_llm(self, max_files: int = 10) -> Dict[str, Any]:
        """Get optimized context for LLM generation"""
        if not self.files:
            return {
                "files": [],
                "total_files_shown": 0,
                "total_files": 0
            }
        
        # Prioritize important files
        important_files = []
        
        # Add main files first
        main_patterns = ['main', 'app', 'index', 'server', '__init__', 'readme']
        for file in self.files:
            name_lower = file.path.stem.lower()
            if any(pattern in name_lower for pattern in main_patterns):
                important_files.append(file)
        
        # Add other files up to limit
        remaining_files = [f for f in self.files if f not in important_files]
        remaining_files.sort(key=lambda x: (-x.lines, x.path.name))  # Sort by lines desc, name asc
        
        selected_files = (important_files + remaining_files)[:max_files]
        
        # Truncate content if too long
        total_content_size = 0
        file_previews = []
        
        for file in selected_files:
            if total_content_size >= self.max_total_content:
                break
                
            content_preview = file.content
            if len(content_preview) > 2000:  # Truncate long files
                content_preview = content_preview[:2000] + "\n... (truncated)"
            
            total_content_size += len(content_preview)
            if total_content_size > self.max_total_content:
                # Truncate this file to fit
                available_space = self.max_total_content - (total_content_size - len(content_preview))
                content_preview = content_preview[:available_space] + "\n... (truncated)"
            
            file_previews.append({
                "path": file.relative_path,
                "language": file.language,
                "lines": file.lines,
                "size": file.size,
                "content": content_preview
            })
        
        return {
            "files": file_previews,
            "total_files_shown": len(file_previews),
            "total_files": len(self.files)
        }

