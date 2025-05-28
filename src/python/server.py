from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import tempfile

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import tools
from tools.inv_vzd_processor import InvVzdProcessor
from tools.zor_spec_dat_processor import ZorSpecDatProcessor
from tools.plakat_generator import PlakatGenerator

# Configure logging with UTF-8 encoding for Windows
import sys
if sys.platform == 'win32':
    # Force UTF-8 encoding for Windows console
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Python backend is running"
    })

@app.route('/api/process/inv-vzd', methods=['POST'])
def process_inv_vzd():
    """Process innovative education attendance files"""
    try:
        # Get files from request
        if 'files' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No files provided"
            }), 400
        
        files = request.files.getlist('files')
        
        # Get template file
        if 'template' not in request.files:
            return jsonify({
                "status": "error", 
                "message": "No template file provided"
            }), 400
            
        template_file = request.files['template']
        
        # Parse options
        import json
        options = json.loads(request.form.get('options', '{}'))
        
        # Save files temporarily
        import tempfile
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        try:
            # Save source files
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                file_paths.append(file_path)
                
            # Save template
            template_path = os.path.join(temp_dir, template_file.filename)
            template_file.save(template_path)
            
            # Process with InvVzdProcessor
            processor = InvVzdProcessor(logger)
            
            # Add template to options
            options['template'] = template_path
            options['output_dir'] = temp_dir
            
            # Process files
            result = processor.process(file_paths, options)
            
            if result['success']:
                # Read output files and prepare response
                output_files = []
                for processed in result['data']['processed_files']:
                    output_path = processed['output']
                    with open(output_path, 'rb') as f:
                        output_content = f.read()
                        output_files.append({
                            'filename': os.path.basename(output_path),
                            'content': output_content.hex(),  # Convert to hex for JSON
                            'source': os.path.basename(processed['source']),
                            'hours': processed['hours']
                        })
                
                return jsonify({
                    "status": "success",
                    "message": f"Úspěšně zpracováno {len(output_files)} souborů",
                    "data": {
                        "processed": len(output_files),
                        "files": output_files
                    },
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', []),
                    "info": result.get('info', [])
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Zpracování selhalo",
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', [])
                }), 400
                
        finally:
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"Error processing inv-vzd: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/inv-vzd-paths', methods=['POST'])
def process_inv_vzd_paths():
    """Process innovative education attendance files using file paths"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        file_paths = data.get('filePaths', [])
        template_path = data.get('templatePath')
        options = data.get('options', {})
        
        # Debug: Log original paths
        logger.info(f"Original template_path: {template_path}")
        logger.info(f"Original file_paths: {file_paths}")
        
        # Convert Windows paths to WSL paths if needed (only on Linux/WSL)
        def convert_path_if_needed(path):
            if path and isinstance(path, str):
                logger.info(f"Checking path for conversion: {path}")
                # Only convert if we're on Linux/WSL and path is Windows format
                import platform
                if platform.system() == 'Linux' and len(path) >= 3 and path[1:3] == ':\\':
                    drive_letter = path[0].lower()
                    remaining_path = path[3:].replace('\\', '/')
                    wsl_path = f'/mnt/{drive_letter}/{remaining_path}'
                    logger.info(f"Converting Windows path to WSL: {path} -> {wsl_path}")
                    return wsl_path
                else:
                    logger.info(f"Path does not match Windows pattern or not on Linux, keeping as-is: {path}")
            return path
        
        # Convert paths
        template_path = convert_path_if_needed(template_path)
        file_paths = [convert_path_if_needed(fp) for fp in file_paths]
        
        # Debug: Log converted paths
        logger.info(f"Converted template_path: {template_path}")
        logger.info(f"Converted file_paths: {file_paths}")
        
        if not file_paths:
            return jsonify({
                "status": "error",
                "message": "No file paths provided"
            }), 400
            
        if not template_path:
            return jsonify({
                "status": "error",
                "message": "No template path provided"
            }), 400
            
        # Process with InvVzdProcessor
        processor = InvVzdProcessor(logger)
        
        # Add template to options
        options['template'] = template_path
        
        # Process files
        result = processor.process(file_paths, options)
        
        if result['success']:
            # Prepare response
            output_files = []
            for processed in result['data']['processed_files']:
                output_files.append({
                    'filename': os.path.basename(processed['output']),
                    'source': os.path.basename(processed['source']),
                    'hours': processed['hours'],
                    'path': processed['output']
                })
            
            return jsonify({
                "status": "success",
                "message": f"Úspěšně zpracováno {len(output_files)} souborů",
                "data": {
                    "processed": len(output_files),
                    "files": output_files
                },
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', []),
                "info": result.get('info', [])
            })
        else:
            # Enhanced error message for path issues
            errors = result.get('errors', [])
            enhanced_errors = []
            for error in errors:
                if 'neexistuje' in error and ('D:\\' in error or 'C:\\' in error):
                    enhanced_errors.append(f"{error} - PROBLÉM: Používáte Windows cestu na Linux systému. Zkopírujte soubory do Linux souborového systému nebo použijte WSL mount cestu (např. /mnt/d/...)")
                else:
                    enhanced_errors.append(error)
            
            return jsonify({
                "status": "error", 
                "message": "Zpracování selhalo",
                "errors": enhanced_errors,
                "warnings": result.get('warnings', [])
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing inv-vzd-paths: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/zor-spec', methods=['POST'])
def process_zor_spec():
    """Process special attendance data for ZoR"""
    try:
        # Get files from request
        if 'files' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No files provided"
            }), 400
        
        files = request.files.getlist('files')
        
        # Parse options
        import json
        options = json.loads(request.form.get('options', '{}'))
        
        # Get exclude list file if provided
        exclude_file = None
        if 'exclude_list' in request.files:
            exclude_file = request.files['exclude_list']
        
        # Save files temporarily
        import tempfile
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        try:
            # Save source files
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                file_paths.append(file_path)
                
            # Save exclude list if provided
            if exclude_file:
                exclude_path = os.path.join(temp_dir, exclude_file.filename)
                exclude_file.save(exclude_path)
                options['exclude_list'] = exclude_path
            
            # Process with ZorSpecDatProcessor
            processor = ZorSpecDatProcessor(logger)
            
            # Add output directory to options
            options['output_dir'] = temp_dir
            
            # Process files
            result = processor.process(file_paths, options)
            
            if result['success']:
                # Read output files and prepare response
                data = result['data']
                output_files = []
                
                for output_path in data['output_files']:
                    with open(output_path, 'rb') as f:
                        output_content = f.read()
                        output_files.append({
                            'filename': os.path.basename(output_path),
                            'content': output_content.hex(),  # Convert to hex for JSON
                            'size': len(output_content)
                        })
                
                return jsonify({
                    "status": "success",
                    "message": f"Úspěšně zpracováno {data['files_processed']} souborů",
                    "data": {
                        "files_processed": data['files_processed'],
                        "unique_students": data['unique_students'],
                        "output_files": output_files
                    },
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', []),
                    "info": result.get('info', [])
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Zpracování selhalo",
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', [])
                }), 400
                
        finally:
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"Error processing zor-spec: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/zor-spec-paths', methods=['POST'])
def process_zor_spec_paths():
    """Process ZorSpec attendance files using file paths"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        file_paths = data.get('filePaths', [])
        options = data.get('options', {})
        
        # Convert Windows paths to WSL paths if needed (only on Linux/WSL)
        def convert_path_if_needed(path):
            if path and isinstance(path, str):
                # Only convert if we're on Linux/WSL and path is Windows format
                import platform
                if platform.system() == 'Linux' and len(path) >= 3 and path[1:3] == ':\\':
                    drive_letter = path[0].lower()
                    remaining_path = path[3:].replace('\\', '/')
                    wsl_path = f'/mnt/{drive_letter}/{remaining_path}'
                    logger.info(f"Converting Windows path to WSL: {path} -> {wsl_path}")
                    return wsl_path
            return path
        
        # Convert paths
        file_paths = [convert_path_if_needed(fp) for fp in file_paths]
        
        if not file_paths:
            return jsonify({
                "status": "error",
                "message": "No file paths provided"
            }), 400
        
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Process with ZorSpecDatProcessor
            processor = ZorSpecDatProcessor(logger)
            
            # Process files using paths directly
            result = processor.process_paths(file_paths, temp_dir, options)
            
            if result['success']:
                # Prepare response with output files
                output_files = []
                for output_file in result['output_files']:
                    # Read file content for download
                    with open(output_file['path'], 'rb') as f:
                        file_content = f.read()
                        output_files.append({
                            'filename': output_file['filename'],
                            'content': file_content.hex(),  # Convert to hex for JSON
                            'size': len(file_content),
                            'type': output_file.get('type', 'file')
                        })
                
                return jsonify({
                    "status": "success",
                    "message": f"Úspěšně zpracováno {result['files_processed']} souborů",
                    "data": {
                        "files_processed": result['files_processed'],
                        "unique_students": result['unique_students'],
                        "output_files": output_files
                    },
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', []),
                    "info": result.get('info', [])
                })
            else:
                # Enhanced error message for path issues
                errors = result.get('errors', [])
                enhanced_errors = []
                for error in errors:
                    if 'neexistuje' in error and ('D:\\' in error or 'C:\\' in error):
                        enhanced_errors.append(f"{error} - PROBLÉM: Používáte Windows cestu na Linux systému. Zkopírujte soubory do Linux souborového systému nebo použijte WSL mount cestu (např. /mnt/d/...)")
                    else:
                        enhanced_errors.append(error)
                
                return jsonify({
                    "status": "error",
                    "message": "Zpracování selhalo",
                    "errors": enhanced_errors,
                    "warnings": result.get('warnings', [])
                }), 400
                
        finally:
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        logger.error(f"Error processing zor-spec-paths: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/zor-spec-directory', methods=['POST'])
def process_zor_spec_directory():
    """Process special attendance data from directory"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        source_dir = data.get('sourceDir')
        output_dir = data.get('outputDir')
        exclude_list = data.get('excludeList')
        options = data.get('options', {})
        
        if not source_dir:
            return jsonify({
                "status": "error",
                "message": "No source directory provided"
            }), 400
            
        # Process with ZorSpecDatProcessor
        processor = ZorSpecDatProcessor(logger)
        
        # Set up options
        options['source_dir'] = source_dir
        options['output_dir'] = output_dir or source_dir
        if exclude_list:
            options['exclude_list'] = exclude_list
        
        # Process files (empty list since we're using directory)
        result = processor.process([], options)
        
        if result['success']:
            data = result['data']
            return jsonify({
                "status": "success",
                "message": f"Úspěšně zpracováno {data['files_processed']} souborů",
                "data": {
                    "files_processed": data['files_processed'],
                    "unique_students": data['unique_students'],
                    "html_report": data['html_report'],
                    "names_list": data['names_list']
                },
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', []),
                "info": result.get('info', [])
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Zpracování selhalo",
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', [])
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing zor-spec-directory: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/plakat', methods=['POST'])
def process_plakat():
    """Generate PDF posters for projects"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Požadavek musí obsahovat JSON data"}), 400
        
        # Validate required fields
        required_fields = ['projects', 'orientation', 'common_text']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Chybí povinné pole: {field}"}), 400
        
        projects = data['projects']
        orientation = data['orientation']
        common_text = data['common_text']
        
        # Validate projects format
        if not isinstance(projects, list) or not projects:
            return jsonify({"error": "Projekty musí být neprázdný seznam"}), 400
        
        for i, project in enumerate(projects):
            if not isinstance(project, dict) or 'id' not in project or 'name' not in project:
                return jsonify({"error": f"Projekt {i+1} musí obsahovat 'id' a 'name'"}), 400
        
        # Validate orientation
        if orientation not in ['portrait', 'landscape']:
            return jsonify({"error": "Orientace musí být 'portrait' nebo 'landscape'"}), 400
        
        # Validate common text
        if not isinstance(common_text, str) or len(common_text) > 255:
            return jsonify({"error": "Společný text musí být string s max. 255 znaky"}), 400
        
        # Process with PlakatGenerator
        processor = PlakatGenerator(logger)
        
        # Create temporary output directory
        temp_dir = tempfile.mkdtemp()
        options = {
            'projects': projects,
            'orientation': orientation,
            'common_text': common_text,
            'output_dir': temp_dir
        }
        
        result = processor.process([], options)
        
        if result['success']:
            # Read output files and prepare response
            output_files = []
            for file_path in result['data'].get('output_files', []):
                with open(file_path, 'rb') as f:
                    output_content = f.read()
                    output_files.append({
                        'filename': os.path.basename(file_path),
                        'content': output_content.hex(),  # Convert to hex for JSON
                        'size': len(output_content)
                    })
            
            return jsonify({
                "status": "success", 
                "message": result.get('message', 'Generování dokončeno'),
                "data": {
                    "successful_projects": result['data'].get('successful_projects', 0),
                    "failed_projects": result['data'].get('failed_projects', 0),
                    "total_projects": result['data'].get('total_projects', 0),
                    "output_files": output_files
                },
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', []),
                "info": result.get('info', [])
            })
        else:
            return jsonify({
                "status": "error",
                "message": result.get('message', 'Generování selhalo'),
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', [])
            }), 400
            
    except Exception as e:
        logger.error(f"Error in plakat processing: {str(e)}")
        return jsonify({"error": f"Vnitřní chyba serveru: {str(e)}"}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration"""
    return jsonify({
        "status": "success",
        "data": {
            "version": "1.0.0",
            "tools": [
                {
                    "id": "inv-vzd",
                    "name": "Inovativní vzdělávání",
                    "description": "Zpracování docházky inovativního vzdělávání"
                },
                {
                    "id": "zor-spec",
                    "name": "Speciální data",
                    "description": "Zpracování speciálních dat"
                },
                {
                    "id": "plakat",
                    "name": "Generátor plakátů",
                    "description": "Generování PDF plakátů"
                }
            ]
        }
    })

if __name__ == '__main__':
    # Run the Flask server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='127.0.0.1', port=port, debug=True)