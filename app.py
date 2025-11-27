import os
import threading
import zipfile
import io
import sys
import time
import webview
import psutil
import importlib
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from werkzeug.utils import secure_filename

HAS_GPU = False
GPU_NAME = "CPU Mode"
try:
    import onnxruntime as ort
    providers = ort.get_available_providers()
    if 'DmlExecutionProvider' in providers: 
        HAS_GPU = True
        GPU_NAME = "DirectML (AMD/Intel)"
    elif 'CUDAExecutionProvider' in providers:
        HAS_GPU = True
        GPU_NAME = "NVIDIA CUDA"
    import pynvml
    pynvml.nvmlInit()
except: pass

import suno_splitter
import suno_cleaner
import suno_dereverb
import suno_vocal_split
import suno_remaster
import universal_analyzer
import technical_report

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    WORK_DIR = os.path.dirname(sys.executable)
    os.environ["PATH"] += os.pathsep + BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORK_DIR = BASE_DIR

template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

FOLDER_MAP = {
    'input': os.path.join(WORK_DIR, 'Input'),
    'output': os.path.join(WORK_DIR, 'Output'),
    'clean': os.path.join(WORK_DIR, 'Cleaned_Master'),
    'dry': os.path.join(WORK_DIR, 'Dry_Vocals'),
    'split': os.path.join(WORK_DIR, 'Split_Vocals'),
    'master': os.path.join(WORK_DIR, 'FINAL_MASTER')
}

for path in FOLDER_MAP.values():
    if not os.path.exists(path): os.makedirs(path)

current_status = "Prêt."
current_sub_step = ""
current_progress = 0
is_processing = False
last_analysis_results = [{"name": "Aucune donnée", "bpm": "-", "key": "-"}]

def update_status(msg):
    global current_status, current_sub_step
    current_status = msg
    current_sub_step = ""
    print(f"STATUS: {msg}")

def update_progress(val, message=None):
    global current_progress, current_sub_step
    current_progress = int(val)
    if message: current_sub_step = message

def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    gpu = 0
    if "NVIDIA" in GPU_NAME:
        try:
            import pynvml
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        except: pass
    return {'cpu': cpu, 'ram': ram, 'gpu': gpu, 'gpu_name': GPU_NAME}

def run_wrapper(func, name, **kwargs):
    global is_processing
    is_processing = True
    update_progress(0, "Init...")
    update_status(f"{name} en cours...")
    try:
        original_cwd = os.getcwd()
        os.chdir(WORK_DIR)
        func(progress_callback=update_progress, **kwargs)
        os.chdir(original_cwd)
        update_status(f"{name} terminé.")
        update_progress(100, "Done.")
    except Exception as e: update_status(f"Erreur: {e}")
    finally: is_processing = False

def run_analyze_wrapper():
    global is_processing, last_analysis_results
    is_processing = True
    update_progress(0, "Loading...")
    update_status("Analyse en cours...")
    try:
        input_path = FOLDER_MAP['input']
        importlib.reload(universal_analyzer)
        results = universal_analyzer.analyze_folder_and_return_data(input_path, progress_callback=update_progress)
        if results: last_analysis_results = results
        update_status("Analyse terminée.")
        update_progress(100, "Done.")
    except Exception as e: update_status(f"Erreur Analyse: {e}")
    finally: is_processing = False

@app.route('/')
def index():
    counts = {}
    for key, path in FOLDER_MAP.items():
        try: counts[key] = len([f for f in os.listdir(path) if f.lower().endswith(('.wav', '.mp3', '.flac'))])
        except: counts[key] = 0
    return render_template('index.html', status=current_status, counts=counts, gpu_name=GPU_NAME)

@app.route('/status')
def get_status(): 
    return jsonify({'status': current_status, 'sub_step': current_sub_step, 'processing': is_processing, 'progress': current_progress, 'sys': get_system_stats()})

@app.route('/get_analysis')
def get_analysis(): return jsonify(last_analysis_results)

@app.route('/get_tech_report')
def get_tech_report():
    importlib.reload(technical_report)
    report = technical_report.get_audio_metadata(FOLDER_MAP['input'])
    bpm_map = {item['name']: item for item in last_analysis_results} if last_analysis_results else {}
    data = []
    for item in report:
        info = bpm_map.get(item['filename'], {"bpm": "-", "key": "-"})
        item['bpm'] = info.get('bpm', '-')
        item['key'] = info.get('key', '-')
        data.append(item)
    return jsonify(data)

@app.route('/list_files/<category>')
def list_files_route(category):
    folder = FOLDER_MAP.get(category)
    if not folder: return jsonify([])
    try: files = [f for f in os.listdir(folder) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
    except: files = []
    return jsonify(files)

@app.route('/audio/<category>/<filename>')
def serve_audio(category, filename): return send_from_directory(FOLDER_MAP.get(category), filename)
@app.route('/download/<category>/<filename>')
def download_file(category, filename): return send_from_directory(FOLDER_MAP.get(category), filename, as_attachment=True)
@app.route('/download_zip/<category>')
def download_zip(category):
    folder = FOLDER_MAP.get(category)
    if not folder or not os.path.exists(folder): return "Error", 404
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        found = False
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.flac')) and not file.startswith('.'):
                    zf.write(os.path.join(root, file), file)
                    found = True
    if not found: return "Empty", 404
    memory_file.seek(0)
    return send_file(memory_file, download_name=f"{category}_pack.zip", as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files: return jsonify({'error': 'No file'}), 400
    files = request.files.getlist('files[]')
    saved_count = 0
    if not os.path.exists(FOLDER_MAP['input']): os.makedirs(FOLDER_MAP['input'])
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            save_path = os.path.join(FOLDER_MAP['input'], filename)
            try:
                file.save(save_path)
                if os.path.getsize(save_path) > 0: saved_count += 1
                else: os.remove(save_path)
            except: pass
    update_status(f"{saved_count} fichier(s) importé(s).")
    return jsonify({'message': 'OK', 'count': saved_count})

@app.route('/clear_data', methods=['POST'])
def clear_data():
    global is_processing, last_analysis_results, current_progress, current_sub_step
    if is_processing: return jsonify({'error': 'Busy'}), 400
    for folder in FOLDER_MAP.values():
        if os.path.exists(folder):
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.path.isfile(fp) and not f.startswith('.'):
                    try: os.remove(fp)
                    except: pass
    last_analysis_results = [{"name": "No Data", "bpm": "-", "key": "-"}]
    current_progress = 0
    current_sub_step = ""
    update_status("Session cleared.")
    return jsonify({'message': 'Clean'})

@app.route('/action/<action_name>', methods=['POST'])
def trigger_action(action_name):
    global is_processing, current_progress
    if is_processing: return jsonify({'error': 'Busy'}), 400
    current_progress = 0
    thread = None
    data = request.get_json(silent=True) or {}
    
    if action_name == 'split': thread = threading.Thread(target=run_wrapper, args=(suno_splitter.process_audio, "Splitter"), kwargs={'smart_recovery': data.get('recovery', False), 'stem_mode': data.get('stems', '6s')})
    elif action_name == 'clean': thread = threading.Thread(target=run_wrapper, args=(suno_cleaner.batch_clean, "Cleaner"), kwargs={'mode': data.get('mode', 'hifi')})
    elif action_name == 'dereverb': thread = threading.Thread(target=run_wrapper, args=(suno_dereverb.process_dereverb, "De-Reverb"))
    elif action_name == 'vocals': thread = threading.Thread(target=run_wrapper, args=(suno_vocal_split.process_vocal_split, "Vocal Split"))
    elif action_name == 'master': thread = threading.Thread(target=run_wrapper, args=(suno_remaster.AutoMixer().run_mastering, "Mastering"))
    elif action_name == 'analyze': thread = threading.Thread(target=run_analyze_wrapper)
    
    if thread:
        thread.start()
        return jsonify({'message': 'OK'})
    return jsonify({'error': '?'}), 404

def start_server(): app.run(host='127.0.0.1', port=54321, use_reloader=False)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    time.sleep(1)
    webview.create_window("Universal Audio Studio V2.34", "http://127.0.0.1:54321", width=1280, height=900, resizable=True, min_size=(1000, 700), background_color='#1a1a2e')
    webview.start()
