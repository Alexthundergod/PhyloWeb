import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from phylo_utils import allowed_file, align_sequences, process_phylogenetic_data

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["RESULTS_FOLDER"] = "results/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)

# Global variable to track active process
processing_lock = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    global processing_lock
    if processing_lock:
        return (
            jsonify({"error": "Another process is currently running. Please wait."}),
            429,
        )

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            processing_lock = True
            filename = secure_filename(file.filename)
            unique_id = uuid.uuid4().hex
            request_folder = os.path.join(app.config["RESULTS_FOLDER"], unique_id)
            os.makedirs(request_folder, exist_ok=True)
            unique_filename = f"{unique_id}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(filepath)

            return (
                jsonify(
                    {"message": "File uploaded successfully", "filepath": filepath}
                ),
                200,
            )
        except Exception as e:
            processing_lock = False
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400


@app.route("/align", methods=["POST"])
def align_sequences_route():
    global processing_lock
    if not processing_lock:
        return jsonify({"error": "No active process. Please upload a file first."}), 400

    data = request.json
    filepath = data.get("filepath")
    if not filepath or not os.path.exists(filepath):
        processing_lock = False
        return jsonify({"error": "Invalid file path"}), 400

    try:
        filename = os.path.basename(filepath)
        unique_id = filename.split("_")[0]
        request_folder = os.path.join(app.config["RESULTS_FOLDER"], unique_id)
        aligned_filepath = os.path.join(request_folder, "aligned.fasta")

        align_sequences(filepath, aligned_filepath)
        return (
            jsonify(
                {"message": "Alignment completed", "aligned_filepath": aligned_filepath}
            ),
            200,
        )
    except Exception as e:
        processing_lock = False
        return jsonify({"error": str(e)}), 500


@app.route("/build_tree", methods=["POST"])
def build_tree():
    global processing_lock
    if not processing_lock:
        return jsonify({"error": "No active process. Please upload a file first."}), 400

    try:
        data = request.json
        aligned_filepath = data.get("aligned_filepath")
        if not aligned_filepath or not os.path.exists(aligned_filepath):
            processing_lock = False
            return jsonify({"error": "Invalid aligned file path"}), 400

        request_folder = os.path.dirname(aligned_filepath)
        tree_filepath = os.path.join(request_folder, "tree.nwk")
        json_tree_filepath = os.path.join(request_folder, "tree.json")

        execution_time, _ = process_phylogenetic_data(
            aligned_filepath, tree_filepath, json_tree_filepath
        )

        print(f"\nPhylogenetic tree building time: {execution_time:.2f} seconds\n")

        processing_lock = False
        return (
            jsonify(
                {
                    "message": "Phylogenetic tree built",
                    "tree_filepath": tree_filepath,
                    "json_tree_filepath": json_tree_filepath,
                }
            ),
            200,
        )

    except Exception as e:
        processing_lock = False
        return jsonify({"error": str(e)}), 500


@app.route("/results/<path:filename>")
def get_results(filename):
    return send_from_directory(app.config["RESULTS_FOLDER"], filename)


@app.route("/save_tree", methods=["POST"])
def save_tree():
    try:
        data = request.json
        svg_content = data.get("svg")
        request_id = data.get("request_id")

        if not svg_content or not request_id:
            return jsonify({"error": "Missing required data"}), 400

        request_folder = os.path.join(app.config["RESULTS_FOLDER"], request_id)
        svg_filepath = os.path.join(request_folder, "tree.svg")

        with open(svg_filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

        return (
            jsonify({"message": "Tree saved successfully", "filepath": svg_filepath}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
