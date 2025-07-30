import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from .analyzer import CodeAnalyzer
from .providers import LLMManager, FallbackProvider

# Version info
__version__ = "1.0.0"
class DocumentationGenerator:
    """Enhanced documentation generator with multiple templates"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
    
    def generate_comprehensive_docs(self, analysis: Dict[str, Any], code_context: Dict[str, Any]) -> str:
        """Generate comprehensive documentation using the best available LLM"""
        
        provider = self.llm_manager.get_best_provider()
        
        if isinstance(provider, FallbackProvider):
            return self._generate_template_docs(analysis, code_context)
        
        try:
            prompt = self._build_comprehensive_prompt(analysis, code_context)
            documentation = provider.generate_text(prompt, max_tokens=4000, temperature=0.2)
            return self._format_final_documentation(documentation, analysis)
        
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}")
            print("   Falling back to template documentation...")
            return self._generate_template_docs(analysis, code_context)
    
    def _build_comprehensive_prompt(self, analysis: Dict[str, Any], code_context: Dict[str, Any]) -> str:
        """Build detailed prompt for comprehensive documentation"""
        
        project_type = analysis.get('project_type', 'mixed')
        main_language = list(analysis['languages'].keys())[0] if analysis['languages'] else 'unknown'
        
        prompt = f"""I need you to generate comprehensive technical documentation for a {project_type} project written primarily in {main_language}.

PROJECT STATISTICS:
- Total files: {analysis['total_files']}
- Languages: {', '.join(analysis['languages'].keys())}
- Total lines of code: {analysis['total_lines']:,}
- Project type: {project_type}

MAIN FILES IDENTIFIED:
{self._format_main_files(analysis.get('main_files', []))}

KEY SOURCE FILES (showing {code_context['total_files_shown']} of {code_context['total_files']}):
"""
        
        for file_info in code_context['files'][:5]:  # Limit to avoid token limits
            prompt += f"""
File: {file_info['path']} ({file_info['language']}, {file_info['lines']} lines)
```{file_info['language']}
{file_info['content']}
```
"""
        
        prompt += f"""

LANGUAGE BREAKDOWN:
{self._format_language_stats(analysis['languages'])}

Please create comprehensive documentation with these sections:

1. **Project Title & Description**: What this project does and its main purpose
2. **Features**: Key features and capabilities  
3. **Architecture**: How the code is organized and main components
4. **Installation**: Step-by-step setup instructions for {main_language}
5. **Usage**: How to run and use the project with examples
6. **API/Code Reference**: Key functions, classes, or modules
7. **Configuration**: Environment variables or config files needed
8. **Development**: How to contribute and develop locally
9. **Dependencies**: What external libraries/tools are required

Make the documentation:
- Professional and clear
- Include specific code examples where relevant
- Use proper markdown formatting
- Be helpful for both users and developers
- Include realistic installation commands for {project_type} projects

Focus on being practical and actionable rather than generic."""
        
        return prompt
    
    def _format_main_files(self, main_files: List[Dict]) -> str:
        """Format main files for prompt"""
        if not main_files:
            return "- No specific main files identified"
        
        formatted = []
        for file in main_files:
            formatted.append(f"- {file['path']} ({file['language']})")
        return '\n'.join(formatted)
    
    def _format_language_stats(self, languages: Dict[str, Dict]) -> str:
        """Format language statistics for prompt"""
        formatted = []
        for lang, stats in languages.items():
            formatted.append(f"- {lang.title()}: {stats['files']} files, {stats['lines']:,} lines")
        return '\n'.join(formatted)
    
    def _generate_template_docs(self, analysis: Dict[str, Any], code_context: Dict[str, Any]) -> str:
        """Generate template-based documentation when LLM is not available"""
        
        project_type = analysis.get('project_type', 'Software')
        main_language = list(analysis['languages'].keys())[0] if analysis['languages'] else 'Multiple'
        
        # Detect project name from path
        project_name = Path(analysis['project_root']).name
        
        doc = f"""# {project_name.replace('_', ' ').replace('-', ' ').title()}

A {project_type} project written in {main_language}.

## Overview

This project contains {analysis['total_files']} files with {analysis['total_lines']:,} lines of code across {len(analysis['languages'])} programming languages.

## Project Structure

```
{self._generate_tree_structure(analysis['structure'])}
```

## Languages Used

{self._format_language_breakdown(analysis['languages'])}

## Main Files

{self._format_main_files_detailed(analysis.get('main_files', []))}

## Installation
"""
        
        # Add language-specific installation instructions
        if 'python' in analysis['languages']:
            doc += f"""
### Python Setup
```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```
"""
        
        if 'javascript' in analysis['languages']:
            doc += f"""
### Node.js Setup
```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
npm install
# or
yarn install

# Run the application
npm start
```
"""
        
        if 'java' in analysis['languages']:
            doc += """
### Java Setup
```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name + """

# Build with Maven
mvn clean install

# Or build with Gradle
./gradlew build
```
"""
        
        if 'go' in analysis['languages']:
            doc += f"""
### Go Setup
```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Download dependencies
go mod tidy

# Build and run
go build
./{project_name}
```
"""
        
        doc += """
## Usage

Refer to the main files and source code for specific usage instructions. Key entry points are typically found in:

"""
        
        # Add usage examples based on main files
        main_files = analysis.get('main_files', [])
        if main_files:
            for file in main_files[:3]:  # Show top 3 main files
                if 'main' in file['path'].lower() or 'app' in file['path'].lower():
                    doc += f"- `{file['path']}` - Main application entry point\n"
                elif 'readme' in file['path'].lower():
                    doc += f"- `{file['path']}` - Additional documentation\n"
                else:
                    doc += f"- `{file['path']}` - {file['language'].title()} file\n"
        
        doc += f"""

## File Overview

{self._format_file_overview(code_context['files'])}

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Architecture

The project is organized as follows:

"""
        
        # Add architecture based on languages and structure
        for lang, stats in list(analysis['languages'].items())[:3]:
            doc += f"- **{lang.title()}**: {stats['files']} files containing core functionality\n"
        
        doc += f"""

## Dependencies

Based on the project structure, you may need:

"""
        
        # Suggest dependencies based on project type
        if 'python' in analysis['languages']:
            doc += "- Python 3.7+ and pip\n- Virtual environment (recommended)\n"
        if 'javascript' in analysis['languages']:
            doc += "- Node.js and npm/yarn\n"
        if 'java' in analysis['languages']:
            doc += "- Java JDK 8+\n- Maven or Gradle\n"
        if 'go' in analysis['languages']:
            doc += "- Go 1.16+\n"
        
        doc += f"""

## Statistics

- **Total Files**: {analysis['total_files']}
- **Total Lines**: {analysis['total_lines']:,}
- **Languages**: {len(analysis['languages'])}
- **Last Analyzed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*This documentation was generated automatically by DocAgent v2. For more detailed information, please refer to the source code and comments within individual files.*
"""
        
        return doc
    
    def _generate_tree_structure(self, structure: Dict, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> str:
        """Generate a tree structure representation"""
        if current_depth >= max_depth:
            return prefix + "...\n"
        
        tree = ""
        items = list(structure.items())
        
        for i, (name, info) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            if info.get("type") == "directory":
                tree += f"{prefix}{current_prefix}{name}/\n"
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree += self._generate_tree_structure(
                    info["children"], next_prefix, max_depth, current_depth + 1
                )
            else:
                tree += f"{prefix}{current_prefix}{name}\n"
        
        return tree
    
    def _format_language_breakdown(self, languages: Dict[str, Dict]) -> str:
        """Format detailed language breakdown"""
        breakdown = ""
        for lang, stats in languages.items():
            percentage = (stats['lines'] / sum(s['lines'] for s in languages.values())) * 100
            breakdown += f"- **{lang.title()}**: {stats['files']} files, {stats['lines']:,} lines ({percentage:.1f}%)\n"
        return breakdown
    
    def _format_main_files_detailed(self, main_files: List[Dict]) -> str:
        """Format main files with more detail"""
        if not main_files:
            return "No specific main files identified automatically."
        
        formatted = ""
        for file in main_files:
            formatted += f"- **{file['path']}** ({file['language']}) - {file.get('size', 0):,} bytes\n"
        return formatted
    
    def _format_file_overview(self, files: List[Dict]) -> str:
        """Format file overview section"""
        overview = ""
        for file in files[:5]:  # Show top 5 files
            overview += f"""
### {file['path']}
- **Language**: {file['language'].title()}
- **Lines**: {file['lines']:,}
- **Size**: {file['size']:,} bytes

"""
            # Add a snippet of content if available
            if 'content' in file and file['content']:
                preview = file['content'][:200].replace('\n', ' ').strip()
                if len(file['content']) > 200:
                    preview += "..."
                overview += f"*Preview*: {preview}\n\n"
        
        if len(files) > 5:
            overview += f"*... and {len(files) - 5} more files*\n"
        
        return overview
    
    def _format_final_documentation(self, documentation: str, analysis: Dict[str, Any]) -> str:
        """Add metadata and formatting to final documentation"""
        
        footer = f"""

---

## Project Statistics

- **Total Files**: {analysis['total_files']}
- **Total Lines of Code**: {analysis['total_lines']:,}
- **Languages**: {', '.join(analysis['languages'].keys())}
- **Project Type**: {analysis.get('project_type', 'Mixed').title()}
- **Documentation Generated**: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}

*Generated by DocAgent v{__version__} - AI-powered documentation generator*
"""
        
        return documentation + footer

class DocAgent:
    """Main DocAgent application"""
    
    def __init__(self):
        self.version = __version__
        self.analyzer = None
        self.llm_manager = None
        self.doc_generator = None
    
    def run(self, directory: str, output_file: str = "README.md", provider: str = "auto", 
            max_files: int = 10) -> bool:
        """Run the complete documentation generation process"""
        
        print(f" DocAgent v{self.version} - AI Documentation Generator")
        print(f"   Target: {directory}")
        print(f"   Output: {output_file}")
        print(f"   Provider: {provider}")
        print()
        
        try:
            # Initialize components
            self.analyzer = CodeAnalyzer(directory)
            self.llm_manager = LLMManager(provider)
            self.doc_generator = DocumentationGenerator(self.llm_manager)
            
            # Step 1: Analyze codebase
            print(" Step 1: Analyzing codebase...")
            analysis = self.analyzer.analyze_codebase()
            
            if not analysis['files']:
                print("No code files found to analyze!")
                return False
            
            # Step 2: Prepare context for LLM
            print("Step 2: Preparing context for AI...")
            code_context = self.analyzer.get_context_for_llm(max_files)
            
            # Step 3: Generate documentation
            print(" Step 3: Generating documentation...")
            documentation = self.doc_generator.generate_comprehensive_docs(analysis, code_context)
            
            # Step 4: Save documentation
            print(f"Step 4: Saving to {output_file}...")
            output_path = Path(directory) / output_file
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            
            print(f" Documentation generated successfully!")
            print(f"   Output: {output_path}")
            print(f"    Length: {len(documentation):,} characters")
            print()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Operation cancelled by user")
            return False
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description=f"DocAgent v{__version__} - AI-powered documentation generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  docagent .                           # Analyze current directory
  docagent /path/to/project            # Analyze specific directory  
  docagent . --output docs/README.md   # Custom output file
  docagent . --provider openai         # Use specific LLM provider
  docagent . --max-files 15            # Analyze more files

Supported LLM Providers:
  - openai      (requires OPENAI_API_KEY)
  - huggingface (requires HUGGINGFACE_API_KEY or HF_TOKEN)  
  - ollama      (requires local Ollama server)
  - auto        (automatically detect best available)

Environment Variables:
  OPENAI_API_KEY      - OpenAI API key
  HUGGINGFACE_API_KEY - Hugging Face API key (or HF_TOKEN)
        """
    )
    
    parser.add_argument(
        "directory",
        nargs='?',
        default='.',
        help="Directory to analyze (default: current directory)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="README.md",
        help="Output file name (default: README.md)"
    )
    
    parser.add_argument(
        "-p", "--provider", 
        choices=['auto', 'openai', 'huggingface', 'ollama','groq'],
        default='auto',
        help="LLM provider to use (default: auto)"
    )
    
    parser.add_argument(
        "-m", "--max-files",
        type=int,
        default=10,
        help="Maximum number of files to analyze in detail (default: 10)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"DocAgent v{__version__}"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        sys.exit(1)
    
    # Create and run DocAgent
    agent = DocAgent()
    success = agent.run(
        directory=args.directory,
        output_file=args.output,
        provider=args.provider,
        max_files=args.max_files
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()