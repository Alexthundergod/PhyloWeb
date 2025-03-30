function uploadFile() {
  let fileInput = document.getElementById("fileInput");
  let file = fileInput.files[0];
  if (!file) {
    alert("Please select a file.");
    return;
  }
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
        alert("Upload failed: " + data.error);
      }
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
        alert("Alignment failed: " + data.error);
      }
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
        alert("Tree building failed: " + data.error);
      }
    });
}

function fetchTree(jsonTreePath) {
  fetch(jsonTreePath)
    .then((response) => response.json())
    .then((treeData) => {
      renderTree(treeData);
    });
}

function renderTree(treeData) {
  document.getElementById("status").innerText =
    "The tree was built successfully. Rendering is complete.";
  d3.select("#tree-container").selectAll("svg").remove();
  let width = 800,
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

  let node = svg
    .selectAll(".node")
    .data(root.descendants())
    .enter()
    .append("g")
    .attr("transform", (d) => `translate(${d.y},${d.x})`);

  node.append("circle").attr("r", 6).attr("fill", "rgb(13, 110, 253)");

  node
    .append("text")
    .attr("dy", "0.35em")
    .attr("dx", (d) => (d.children ? -12 : 12))
    .attr("text-anchor", "right")
    .style("font-size", "12px")
    .text((d) => d.data.name);
}
