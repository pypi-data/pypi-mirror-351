from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import importlib
import threading
import time
from waitress import serve
from pathlib import Path
import yaml

class ModelServer:
    def __init__(self, models_path='./models', port=4299, num_workers=1):
        """
        Initialize the Model Server

        Args:
            models_path (str): Path to the directory containing the models.
            port (int): Port number to run the server on.
            num_workers (int): Number of worker threads Waitress should use.
        """
        self.models_path = Path(models_path)
        self.port = port
        self.threads = num_workers

        self.app = Flask(__name__)
        CORS(self.app)

        self.models = {}
        self.model_lock = threading.Lock()
        
        # Ensure models directory exists
        if not self.models_path.exists():
            self.models_path.mkdir(parents=True)
            print(f"Created models directory at {self.models_path}")

        # Ensure models.yaml file exists
        yaml_path = self.models_path / 'models.yaml'
        if not yaml_path.exists():
            with open(yaml_path, 'w') as yaml_file:
                yaml_file.write("models:\n")  # Initialize with an empty models list
            print(f"Created models.yaml at {yaml_path}")

        # Setup Flask routes
        self.setup_routes()

        # Start a background cleanup thread for removing stale models
        self.cleanup_thread = threading.Thread(target=self._model_cleanup, daemon=True)
        self.cleanup_thread.start()

    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Simple endpoint to verify server is running"""
            return jsonify({
                "status": "ok",
                "message": "Model server is running",
                "models_path": str(self.models_path),
                "port": self.port
            }), 200

        @self.app.route('/testlocalchat', methods=['POST'])
        def testlocalchat():
            """
            Test a local model by directly loading and calling its 'chat' function.
            Expects JSON data: { "message": "...", "model": "...", ... }
            """
            data = request.get_json()
            
            if data and 'message' in data and 'model' in data:
                user_message = data['message']
                # Strip off '.py' if present
                model_name = data['model'][:-3] if data['model'].endswith('.py') else data['model']

                try:
                    test_model = importlib.import_module(f'models.{model_name}')
                    response = test_model.chat(user_message)
                except ModuleNotFoundError:
                    return jsonify(message="Model not found", trigger=False), 400
                except AttributeError:
                    return jsonify(message="Model module does not have a 'chat' function", trigger=False), 400

                if response:
                    return jsonify(message=response, trigger=True), 200
                else:
                    return jsonify(message="No message provided by model", trigger=False), 400
            else:
                return jsonify(message="Invalid request data", trigger=False), 400

        @self.app.route('/get_existing_models', methods=['GET'])
        def get_existing_models():
            """
            Return a list of all model files in the models directory along with their metadata.
            If a models.yaml file exists, include metadata from it.
            Accepts an optional 'model_name' query parameter to filter for a specific model.
            """
            model_files = []
            yaml_config = self._parse_yaml_config()
            requested_model_name = request.args.get('model_name') # Get model_name from query params
            
            for f in os.listdir(self.models_path):
                if not os.path.isfile(os.path.join(self.models_path, f)) or f == 'models.yaml':
                    continue
                    
                creation_time = os.path.getctime(os.path.join(self.models_path, f))
                formatted_time = datetime.fromtimestamp(creation_time).strftime('%Y/%m/%d %H:%M:%S')
                
                # Create base model info with filename as default model_name
                model_info = {
                    "model_file": f,
                    "model_name": f,  # Default to filename
                    "time": formatted_time,
                    "input_modalities": ["text"],  # default
                    "output_modalities": ["text"],  # default
                    "description": ""
                }
                
                # Update with YAML config if available
                current_model_name_from_yaml = f # Default to filename if not in YAML
                if yaml_config and 'models' in yaml_config:
                    for model_config in yaml_config['models']:
                        if model_config.get('file') == f:
                            # Make sure we're copying all fields from YAML
                            if 'name' in model_config:
                                model_info["model_name"] = model_config['name']
                                current_model_name_from_yaml = model_config['name']
                            if 'input_modalities' in model_config:
                                model_info["input_modalities"] = model_config['input_modalities']
                            if 'output_modalities' in model_config:
                                model_info["output_modalities"] = model_config['output_modalities']
                            if 'description' in model_config:
                                model_info["description"] = model_config['description']
                            break
                
                # If a specific model_name is requested, only add it if it matches
                if requested_model_name:
                    # Check against filename (e.g., "model.py") and YAML name (e.g., "My Model")
                    if requested_model_name == f or requested_model_name == model_info["model_name"] or requested_model_name == current_model_name_from_yaml:
                        model_files.append(model_info)
                        break # Found the requested model, no need to check further
                else:
                    # If no specific model is requested, add all models
                    model_files.append(model_info)
            
            if requested_model_name and not model_files:
                return jsonify(message=f"Model '{requested_model_name}' not found.", trigger=False), 404
            
            return jsonify(message=model_files, trigger=True), 200

        @self.app.route('/get_thread_count', methods=['GET'])
        def get_thread_count():
            """
            Return the current number of active threads.
            """
            active_threads = threading.active_count()
            return jsonify({
                "active_threads": active_threads
            }), 200

        @self.app.route('/chat', methods=['POST'])
        def chat():
            """
            Generic chat endpoint that retrieves or loads a model by name and process_id, 
            calls the model with the prompt, and returns its response.
            
            Expects JSON data with:
              {
                "prompt": "...",
                "process_id": "...",
                "model_name": "...",
                "finish_flag": bool
              }
            """
            data = request.get_json()
            prompt = data.get('prompt')
            process_id = data.get('process_id')
            model_name = data.get('model_name')
            finish_flag = data.get('finish_flag', False)

            # Get (or create) the model for this process_id + model_name
            model = self._get_model(process_id, model_name)

            try:
                answer = model(prompt)
                # If finish_flag is set, remove the model from the cache
                if finish_flag:
                    with self.model_lock:
                        if process_id in self.models:
                            del self.models[process_id]

                return jsonify({'answer': answer})
            except Exception as e:
                print(f"Server error occurred: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    def _parse_yaml_config(self):
        """
        Parse the models.yaml file if it exists.
        Returns the parsed YAML config or None if file doesn't exist.
        """
        yaml_path = self.models_path / 'models.yaml'
        if not yaml_path.exists():
            return None
            
        try:
            with open(yaml_path, 'r') as yaml_file:
                return yaml.safe_load(yaml_file)
        except Exception as e:
            print(f"Error parsing models.yaml: {str(e)}")
            return None
            

    def _load_model(self, model_name: str):
        """
        Dynamically load the model's chat function from the models folder.
        
        model_name is typically the filename, like 'some_model.py'.
        We'll import models.some_model, then return the 'chat' attribute.
        """
        # Strip off '.py' if present
        module_name = model_name[:-3] if model_name.endswith('.py') else model_name
        model_module = importlib.import_module(f'models.{module_name}')
        importlib.reload(model_module)
        return model_module.chat

    def _get_model(self, process_id: str, model_name: str):
        """
        Retrieve a cached model by process_id, or load it if not present. 
        Update its 'last_accessed' time to keep it from being cleaned up.
        """
        with self.model_lock:
            if process_id not in self.models:
                self.models[process_id] = {
                    'model': self._load_model(model_name),
                    'last_accessed': time.time()
                }
            else:
                # Ensure the model is still valid, or reload if needed
                # (Optional step if you want to ensure code changes are reloaded each time)
                # For now, we just update access time.
                pass

            self.models[process_id]['last_accessed'] = time.time()
            return self.models[process_id]['model']

    def _model_cleanup(self):
        """
        Background thread that periodically removes models that haven't been accessed
        for > 180 seconds (3 minutes).
        """
        while True:
            time.sleep(60)
            with self.model_lock:
                current_time = time.time()
                to_delete = [
                    pid for pid, model_info in self.models.items()
                    if current_time - model_info['last_accessed'] > 180
                ]
                for pid in to_delete:
                    del self.models[pid]

    def start(self):
        """
        Start the server with Waitress using the specified number of threads.
        """
        print(f"Starting Model Server on http://127.0.0.1:{self.port} with {self.threads} threads.")
        serve(self.app, host='0.0.0.0', port=self.port, threads=self.threads)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the model server")
    parser.add_argument('--models_path', type=str, default='./models',
                       help='Path to the models directory (default: ./models)')
    parser.add_argument('--port', type=int, default=4299,
                       help='Port number to run the server on (default: 4299)')
    parser.add_argument('--threads', type=int, default=1,
                       help='Number of worker threads for Waitress (default: 1)')
    
    args = parser.parse_args()

    server = ModelServer(
        models_path=args.models_path,
        port=args.port,
        num_workers=args.threads
    )
    server.start()
