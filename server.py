from flask import Flask, render_template, request, send_file, send_from_directory
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

root_directory = "/home/horlakz/"

def list_files_and_directories(path):
    files = []
    directories = []

    # Traverse the directory and collect files and directories
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            directories.append({
                'name': item,
                'content': list_files_and_directories(item_path)  # Recursively list contents
            })

    return {'files': files, 'directories': directories}

def list_directories(path):
    directories = []

    # list only directories in the root directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            directories.append(item)

    return {'directories': directories}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    upload_folder = root_directory + '/Downloads/file_transfer'
    

    file = request.files['file']
    if file:
        # create downloads folder if not exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file.save(os.path.join(upload_folder, file.filename))
        # create a json file to store list of files that have been recieved
        with open('recieved_files.txt', 'a') as f:
            f.write(file.filename + '\n')

        return render_template('upload_success.html')
    else:
        return render_template('upload_failed.html')


@app.route('/list', methods=['GET'])
def list_files():
    directories = list_directories(root_directory)
    return render_template('list.html', directories=directories)

@app.route('/list/<path:directory_path>')
def directory_listing(directory_path):
    full_directory_path = os.path.join(root_directory, directory_path)
    directory_content = list_files_and_directories(full_directory_path)
    return render_template('directory_listing.html', directory_path=directory_path, directory_content=directory_content)

@app.route('/download/<path:file_path>')
def download(file_path):
    file_path = os.path.join(root_directory, file_path)
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
