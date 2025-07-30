# CodeAtlas

## 🚀 Overview
CodeAtlas is a groundbreaking Python library designed to help developers visualize and comprehend their codebases effortlessly. By generating interactive and intuitive diagrams, CodeAtlas provides insights into the structure and flow of your Python projects, facilitating better understanding, maintenance, and collaboration.

## 🎯 Key Features
- **Function and Class Diagrams**: Automatically generate diagrams showcasing the relationships between functions and classes in your code.
- **Module Dependency Graphs**: Visualize how different modules in your project depend on each other.
- **Interactive Web Interface**: Explore your codebase through an interactive web interface with zooming, panning, and filtering capabilities.
- **Command-Line Interface (CLI)**: Easily integrate CodeAtlas into your workflow using its powerful CLI.
- **Export Options**: Export diagrams in various formats such as PNG, SVG, and PDF for documentation or presentations.

## 🧠 Why CodeAtlas?
Understanding complex codebases can be challenging, especially when onboarding new team members or revisiting old projects. While tools like Graphviz and Doxygen exist, they often require extensive configuration and lack interactivity. CodeAtlas fills this gap by providing an easy-to-use, interactive, and visually appealing way to explore Python codebases.

## 📦 Installation
To install CodeAtlas, use the following command:

```bash
pip install codeatlas
```

## 🛠️ Usage
To generate a graph for your Python project, run the following command:

```bash
python -m codeatlas.main --path <project_path> --output <output_file>
```

Example:

```bash
python -m codeatlas.main --path examples/sample_project --output demo_graph.png
```

## 🤝 Contributing
We welcome contributions from the community! Please see the `CONTRIBUTING.md` file for guidelines on how to contribute.

## 🚀 Future Plans
- Add module dependency graphs.
- Develop an interactive web interface for exploring codebases.
- Support exporting diagrams in SVG and PDF formats.
- Enhance CLI features for better usability.

## 📜 License
CodeAtlas is licensed under the MIT License. See the `LICENSE` file for more details.

---

Happy coding with CodeAtlas! 🎉
