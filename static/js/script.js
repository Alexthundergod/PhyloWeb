function showLoading() {
    document.getElementById('loading-animation').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading-animation').style.display = 'none';
}

function uploadFile() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }
    
    // Clear previous tree visualization and show loading animation
    d3.select("#tree-container").selectAll("svg").remove();
    showLoading();
    
    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload", { method: "POST", body: formData })
        .then((response) => response.json())
        .then((data) => {
            if (data.filepath) {
                document.getElementById("status").innerText =
                    "File uploaded. Processing...";
                alignSequences(data.filepath);
            } else {
                // Keep loading bar visible only for "process running" error
                if (data.error !== "Another process is currently running. Please wait.") {
                    hideLoading();
                }
                alert("Upload failed: " + data.error);
            }
        })
        .catch((error) => {
            hideLoading();
            alert("Error: " + error);
        });
}

function alignSequences(filepath) {
    fetch("/align", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filepath }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.aligned_filepath) {
                document.getElementById("status").innerText =
                    "Alignment completed. Building tree...";
                buildTree(data.aligned_filepath);
            } else {
                hideLoading();
                alert("Alignment failed: " + data.error);
            }
        })
        .catch((error) => {
            hideLoading();
            alert("Error: " + error);
        });
}

function buildTree(aligned_filepath) {
    fetch("/build_tree", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ aligned_filepath }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.json_tree_filepath) {
                document.getElementById("status").innerText =
                    "The tree was built successfully. Rendering...";
                fetchTree(data.json_tree_filepath);
            } else {
                hideLoading();
                alert("Tree building failed: " + data.error);
            }
        })
        .catch((error) => {
            hideLoading();
            alert("Error: " + error);
        });
}

function fetchTree(jsonTreePath) {
    fetch(jsonTreePath)
        .then((response) => response.json())
        .then((treeData) => {
            // Save the current tree path before rendering
            document.getElementById("tree-container").setAttribute('data-tree-path', jsonTreePath);
            renderTree(treeData);
        });
}

function renderTree(treeData) {
    document.getElementById("status").innerText =
        "The tree was built successfully. Rendering is complete.";
    hideLoading();
    
    // Clear container
    const treeContainer = document.getElementById("tree-container");
    treeContainer.innerHTML = '';
    
    let width = 1200,
        height = 500;

    let svg = d3
        .select("#tree-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(40,40)");

    let root = d3.hierarchy(treeData);
    let treeLayout = d3.tree().size([height - 100, width - 200]);
    treeLayout(root);

    let linkGenerator = d3
        .linkHorizontal()
        .x((d) => d.y)
        .y((d) => d.x);

    // Draw tree branches
    svg
        .selectAll(".link")
        .data(root.links())
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("d", linkGenerator);

    // Draw nodes and labels
    let node = svg
        .selectAll(".node")
        .data(root.descendants())
        .enter()
        .append("g")
        .attr("transform", (d) => `translate(${d.y},${d.x})`);

    node.append("circle").attr("r", 6).attr("fill", "rgb(0, 208, 79)");

    node
        .append("text")
        .attr("dy", "0.35em")
        .attr("dx", (d) => (d.children ? -12 : 12))
        .attr("text-anchor", "right")
        .style("font-size", "12px")
        .text((d) => d.data.name);

    // Add save button
    const saveButton = document.createElement('button');
    saveButton.className = 'btn btn-upload mt-3';
    saveButton.textContent = 'Save Tree as SVG';
    saveButton.onclick = () => saveTree('svg');
    treeContainer.insertAdjacentElement('afterend', saveButton);
}

function saveTree(format = 'svg') {
    const svgElement = document.querySelector('#tree-container svg');
    if (!svgElement) {
        alert("No tree to save!");
        return;
    }

    // Get request_id from tree path (format: "/results/request_id/tree.json")
    const jsonTreePath = document.querySelector('#tree-container').getAttribute('data-tree-path');
    const matches = jsonTreePath.match(/results\/([^/]+)\/tree\.json/);
    const request_id = matches ? matches[1] : null;

    if (!request_id) {
        alert("Could not determine request ID!");
        return;
    }

    // Clone SVG for modification
    const svgClone = svgElement.cloneNode(true);
    
    // Add necessary attributes for proper SVG display
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    svgClone.setAttribute('version', '1.1');
    
    // Get SVG as string
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgClone);

    console.log("Saving tree for request_id:", request_id); // Debug info

    // Send to server for saving
    fetch("/save_tree", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            svg: svgString,
            request_id: request_id
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.filepath) {
            // Create download link
            const link = document.createElement('a');
            link.href = `/results/${request_id}/tree.svg`;
            link.download = `phylogenetic_tree.svg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert("Failed to save tree: " + data.error);
        }
    })
    .catch(error => {
        console.error("Save error:", error);
        alert("Error saving tree: " + error);
    });
} 