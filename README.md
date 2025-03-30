# PhyloWeb

PhyloWeb is a web application for building and visualizing phylogenetic trees from sequence data. It provides a simple interface for uploading FASTA files, performing sequence alignment, and generating interactive phylogenetic trees.

## Features

- File upload support for FASTA format (.fasta, .fa)
- Sequence alignment using Clustal Omega
- Phylogenetic tree construction using IQ-TREE
- Interactive tree visualization using D3.js
- SVG export functionality
- Process locking to prevent concurrent operations
- Real-time status updates
- Execution time tracking

## Prerequisites

Before running the application, make sure you have the following installed:
- Python 3.8 or higher
- Clustal Omega
- IQ-TREE
- conda

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Alexthundergod/PhyloWeb.git
cd PhyloWeb
```

2. Create a virtual environment:
```bash
conda env create -f environment.yml
```

## Usage

1. Start the Flask application:
```bash
flask run
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload a FASTA file using the interface
4. Wait for the alignment and tree construction to complete
5. Interact with the generated tree visualization
6. Save the tree as SVG if needed

## API Endpoints

- `GET /` - Main page
- `POST /upload` - File upload endpoint
- `POST /align` - Sequence alignment endpoint
- `POST /build_tree` - Tree construction endpoint
- `POST /save_tree` - SVG saving endpoint
- `GET /results/<filename>` - Results retrieval endpoint

## Development

The application is built using:
- Flask (Backend framework)
- D3.js (Tree visualization)
- Bootstrap (UI styling)
- Clustal Omega (Sequence alignment)
- IQ-TREE (Phylogenetic tree construction)

Key files:
- `app.py` - Flask application and route handlers
- `phylo_utils.py` - Bioinformatics utility functions
- `script.js` - Frontend logic and visualization
- `style.css` - Custom styling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

