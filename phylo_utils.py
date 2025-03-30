import os
import json
import subprocess
import Bio.Phylo as Phylo
from typing import Dict, Any, Tuple


def align_sequences(input_filepath: str, output_filepath: str) -> None:
    """
    Align sequences using Clustal Omega.

    Args:
        input_filepath: Path to input file
        output_filepath: Path to output file

    Raises:
        subprocess.CalledProcessError: If clustalo execution fails
    """
    subprocess.run(
        ["clustalo", "-i", input_filepath, "-o", output_filepath, "--force"], check=True
    )


def build_phylogenetic_tree(aligned_filepath: str, tree_filepath: str) -> None:
    """
    Build phylogenetic tree using IQ-TREE.

    Args:
        aligned_filepath: Path to aligned sequences file
        tree_filepath: Path to output tree file

    Raises:
        subprocess.CalledProcessError: If iqtree execution fails
    """
    subprocess.run(["iqtree", "-s", aligned_filepath, "-nt", "1", "-redo"], check=True)
    os.rename(aligned_filepath + ".treefile", tree_filepath)


def tree_to_json(tree) -> Dict[str, Any]:
    """
    Convert tree to JSON format.

    Args:
        tree: Bio.Phylo tree object

    Returns:
        Dict[str, Any]: JSON representation of the tree
    """

    def recurse(clade):
        name = clade.name if clade.name else str(clade)
        # Remove redundant ID objects
        if name.startswith("Node") | name.startswith("Clade"):
            name = ""

        node = {"name": name}

        if clade.branch_length:
            node["branch_length"] = clade.branch_length

        if clade.clades:
            node["children"] = [recurse(child) for child in clade.clades]
        return node

    return recurse(tree.root)


def process_phylogenetic_data(
    aligned_filepath: str, tree_filepath: str, json_tree_filepath: str
) -> Tuple[float, Dict[str, Any]]:
    """
    Process phylogenetic data: build tree and convert to JSON.

    Args:
        aligned_filepath: Path to aligned sequences file
        tree_filepath: Path to output tree file
        json_tree_filepath: Path to JSON tree file

    Returns:
        Tuple[float, Dict[str, Any]]: Execution time and JSON tree representation
    """
    import time

    start_time = time.time()

    # Build tree
    build_phylogenetic_tree(aligned_filepath, tree_filepath)

    # Convert to JSON
    tree = Phylo.read(tree_filepath, "newick")
    tree_json = tree_to_json(tree)

    with open(json_tree_filepath, "w") as json_file:
        json.dump(tree_json, json_file)

    execution_time = time.time() - start_time

    return execution_time, tree_json


def allowed_file(filename: str) -> bool:
    """
    Check if file has allowed extension.

    Args:
        filename: Name of the file

    Returns:
        bool: True if file has allowed extension
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"fasta", "fa"}
