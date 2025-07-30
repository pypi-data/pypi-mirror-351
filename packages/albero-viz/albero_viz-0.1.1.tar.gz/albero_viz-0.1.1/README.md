# 🌳 Albero-viz — Directory Tree Visualization Tool

**Albero-viz** is a simple, fast, and colorful command-line tool to visualize directory structures.

## ✨ Features

- 🌲 **Tree-style visualization** of directory structures  
- 🎨 **Colored output**  
  - **Blue** for directories  
  - **Green** for files  
- 📁 Option to **display only directories**  
- ⚡ **Fast and lightweight**  
- 🐍 **Pure Python** — no external dependencies  

## 📦 Installation

```bash
pip install albero-viz
```

## 🚀 Usage

### Show a directory tree

```bash
albero -p /path/to/directory
# or
albero --path /home/user/projects
```

### Show only directories

```bash
albero -f -p /path/to/directory
```

## 🛠️ Options

| Option        | Description                         |
|---------------|-------------------------------------|
| `-p`          | Path to the directory to visualize  |
| `-f`          | Show only folders (no files)        |


