# ModuleX 📁

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/modulex.svg)](https://pypi.org/project/modulex/)

A simple and intuitive Python package for file and folder management operations. ModuleX provides easy-to-use functions for creating, deleting, and managing files and directories with built-in error handling.

## ✨ Features

-   **Create Folders**: Easily create new directories with automatic name formatting
-   **Delete Folders**: Remove directories with safety checks
-   **Create Files**: Generate text files with custom content
-   **Delete Files**: Remove files with confirmation and error handling
-   **Smart Input Processing**: Automatic space-to-underscore conversion
-   **Error Handling**: Built-in exception handling for robust operations

## 🚀 Installation

```bash
pip install modulex
```

That's it! No additional dependencies required.

## 📖 Quick Start

```python
import modulex

# The package provides interactive functions
# Simply call the functions and follow the prompts

# Create a new folder
modulex.createfolder()

# Create a new text file
modulex.createFile()

# Delete a folder
modulex.deletefolder()

# Delete a file
modulex.deleteFile()
```

## 🎯 Usage Examples

### Creating a Folder

```python
import modulex

modulex.createfolder()
# Prompts: "Enter a name for a new folder: "
# Input: "my project folder"
# Creates: "my_project_folder" directory
```

### Creating a Text File

```python
import modulex

modulex.createFile()
# Prompts for filename (max 20 characters)
# Currently supports .txt files only
# Allows you to add content to the file
```

### Managing Files and Folders

-   All functions include automatic input validation
-   Spaces in names are automatically converted to underscores
-   Built-in checks prevent overwriting existing files/folders
-   Error messages guide you through any issues

## 📋 Function Reference

| Function         | Description                          | Input Requirements                   |
| ---------------- | ------------------------------------ | ------------------------------------ |
| `createfolder()` | Creates a new directory              | Folder name (any length)             |
| `deletefolder()` | Removes an existing directory        | Existing folder name                 |
| `createFile()`   | Creates a new text file with content | Filename (≤20 chars), .txt extension |
| `deleteFile()`   | Removes an existing file             | Existing filename                    |

## ⚠️ Important Notes

-   File names are limited to 20 characters maximum
-   Currently supports only `.txt` file extension
-   Folder and file names with spaces are automatically converted (spaces → underscores)
-   All operations include safety checks to prevent accidental overwrites

## 🛠️ Requirements

-   Python 3.6 or higher
-   No external dependencies required

## 🤝 Contributing

We welcome contributions! If you have suggestions for improvements or find any issues, please feel free to reach out through PyPI or create discussions around the package.

## 📝 License

This project is licensed under the MIT License.

## 🐛 Issues & Support

If you encounter any issues or have questions about ModuleX, you can:

-   Check the PyPI project page for updates
-   Review the documentation above
-   Contact the maintainer through PyPI

## 🚧 Roadmap

-   [ ] Support for additional file extensions
-   [ ] Batch operations for multiple files/folders
-   [ ] Configuration file support
-   [ ] Enhanced error reporting
-   [ ] GUI interface option

---

**Made with ❤️ by BGeorgiev120**
