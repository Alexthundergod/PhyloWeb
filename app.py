import os
import json
import uuid
import subprocess
import Bio.Phylo as Phylo
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, send_from_directory

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'fasta', 'fa'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = uuid.uuid4().hex
        request_folder = os.path.join(app.config['RESULTS_FOLDER'], unique_id)
        os.makedirs(request_folder, exist_ok=True)
        unique_filename = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filepath': filepath}), 200
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/align', methods=['POST'])
def align_sequences():
    data = request.json
    filepath = data.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'Invalid file path'}), 400
    
    aligned_filepath = os.path.join(app.config['RESULTS_FOLDER'], 'aligned.fasta')
    try:
        subprocess.run(['clustalo', '-i', filepath, '-o', aligned_filepath, '--force'], check=True)
        return jsonify({'message': 'Alignment completed', 'aligned_filepath': aligned_filepath}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Alignment failed', 'details': str(e)}), 500

@app.route('/build_tree', methods=['POST'])
def build_tree():
    data = request.json
    aligned_filepath = data.get('aligned_filepath')
    if not aligned_filepath or not os.path.exists(aligned_filepath):
        return jsonify({'error': 'Invalid aligned file path'}), 400
    
    tree_filepath = os.path.join(app.config['RESULTS_FOLDER'], 'tree.nwk')
    json_tree_filepath = os.path.join(app.config['RESULTS_FOLDER'], 'tree.json')
    try:
        subprocess.run(['iqtree', '-s', aligned_filepath, '-nt', 'AUTO', '-redo'], check=True)
        os.rename(aligned_filepath + '.treefile', tree_filepath)
        
        tree = Phylo.read(tree_filepath, 'newick')
        tree_json = tree_to_json(tree)
        with open(json_tree_filepath, 'w') as json_file:
            json.dump(tree_json, json_file)
        
        return jsonify({'message': 'Phylogenetic tree built', 'tree_filepath': tree_filepath, 'json_tree_filepath': json_tree_filepath}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Tree construction failed', 'details': str(e)}), 500

def tree_to_json(tree):
    def recurse(clade):
        name = clade.name if clade.name else str(clade)
        if name.startswith("Node") | name.startswith("Clade"):  # Видалимо зайві ID-об'єкти
            name = ''
        
        node = {'name': name}
        
        if clade.branch_length:
            node['branch_length'] = clade.branch_length
        
        if clade.clades:
            node['children'] = [recurse(child) for child in clade.clades]
        return node

    return recurse(tree.root)

@app.route('/results/<path:filename>')
def get_results(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
