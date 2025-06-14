from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import tempfile

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import tools
from tools.inv_vzd_processor import InvVzdProcessor
from tools.zor_spec_dat_processor import ZorSpecDatProcessor
from tools.plakat_generator import PlakatGenerator

# Initialize logging
from logger import init_logging
server_logger, tool_logger = init_logging()

# DEBUG mode - set to False for production
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Force debug mode to be always on for debugging InvVzd issues
DEBUG_MODE = True
print(f"[SERVER] DEBUG MODE ENABLED: {DEBUG_MODE}")

def debug_print(*args, **kwargs):
    """Print debug messages only in DEBUG_MODE"""
    if DEBUG_MODE:
        server_logger.debug(' '.join(str(arg) for arg in args))

# Configure UTF-8 encoding for Windows
if sys.platform == 'win32':
    # Force UTF-8 encoding for Windows console
    import codecs
    if hasattr(sys.stdout, 'detach'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    if hasattr(sys.stderr, 'detach'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask logging
import logging
app.logger.handlers = []
app.logger.propagate = True

# Suppress werkzeug logging in production
if not DEBUG_MODE:
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Python backend is running"
    })

@app.route('/api/detect/template-version', methods=['POST'])
def detect_template_version():
    """Detect template version from file"""
    try:
        data = request.get_json()
        template_path = data.get('templatePath')
        
        if not template_path:
            return jsonify({
                "success": False,
                "message": "No template path provided"
            }), 400
        
        # Convert path if needed
        import platform
        if platform.system() == 'Linux' and len(template_path) >= 3 and template_path[1:3] == ':\\':
            drive_letter = template_path[0].lower()
            remaining_path = template_path[3:].replace('\\', '/')
            template_path = f'/mnt/{drive_letter}/{remaining_path}'
        
        # Use InvVzdProcessor to detect version
        processor = InvVzdProcessor(tool_logger)
        version = processor._detect_template_version(template_path)
        
        if version:
            return jsonify({
                "success": True,
                "version": version,
                "message": f"Detekována verze: {version} hodin"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Nepodařilo se detekovat verzi šablony - neplatný formát"
            })
            
    except Exception as e:
        server_logger.error(f"Error detecting template version: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Chyba při detekci verze: {str(e)}"
        }), 500

@app.route('/api/detect/source-version', methods=['POST'])
def detect_source_version():
    """Detect source file version"""
    try:
        data = request.get_json()
        source_path = data.get('sourcePath')
        
        if not source_path:
            return jsonify({
                "success": False,
                "message": "No source path provided"
            }), 400
        
        # Convert path if needed
        import platform
        if platform.system() == 'Linux' and len(source_path) >= 3 and source_path[1:3] == ':\\':
            drive_letter = source_path[0].lower()
            remaining_path = source_path[3:].replace('\\', '/')
            source_path = f'/mnt/{drive_letter}/{remaining_path}'
        
        # Use InvVzdProcessor to detect source version
        processor = InvVzdProcessor(tool_logger)
        version = processor._detect_source_version(source_path)
        
        if version:
            return jsonify({
                "success": True,
                "version": version,
                "message": f"Detekována verze: {version} hodin"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Nepodařilo se detekovat verzi zdrojového souboru"
            })
            
    except Exception as e:
        server_logger.error(f"Error detecting source version: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Chyba při detekci verze: {str(e)}"
        }), 500

@app.route('/api/detect/zor-spec-version', methods=['POST'])
def detect_zor_spec_version():
    """Detect ZorSpec file version from 'Úvod a postup vyplňování' sheet"""
    try:
        data = request.get_json()
        file_path = data.get('filePath')
        
        if not file_path:
            return jsonify({
                "success": False,
                "message": "No file path provided"
            }), 400
        
        # Convert path if needed
        import platform
        if platform.system() == 'Linux' and len(file_path) >= 3 and file_path[1:3] == ':\\':
            drive_letter = file_path[0].lower()
            remaining_path = file_path[3:].replace('\\', '/')
            file_path = f'/mnt/{drive_letter}/{remaining_path}'
        
        # Check if file has the required sheet and detect version
        processor = ZorSpecDatProcessor(tool_logger)
        sheet_info = processor.detect_file_info(file_path)
        
        if sheet_info['has_intro_sheet']:
            return jsonify({
                "success": True,
                "has_intro_sheet": True,
                "version": sheet_info['version'],
                "message": f"Detekována verze: {sheet_info['version']}"
            })
        else:
            return jsonify({
                "success": False,
                "has_intro_sheet": False,
                "message": "Soubor neobsahuje list 'Úvod a postup vyplňování'"
            })
            
    except Exception as e:
        server_logger.error(f"Error detecting ZorSpec version: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Chyba při detekci verze: {str(e)}"
        }), 500

@app.route('/api/select-folder', methods=['POST'])
def select_folder():
    """Select and scan folder for attendance files"""
    try:
        data = request.get_json()
        folder_path = data.get('folderPath')
        tool_type = data.get('toolType', 'inv-vzd')
        
        server_logger.info(f"[SELECT-FOLDER] Request received for tool: {tool_type}")
        server_logger.info(f"[SELECT-FOLDER] Folder path: {folder_path}")
        
        if not folder_path:
            return jsonify({
                "success": False,
                "message": "No folder path provided"
            }), 400
        
        # Convert Windows path to WSL path if needed
        import platform
        if platform.system() == 'Linux' and len(folder_path) >= 3 and folder_path[1:3] == ':\\':
            drive_letter = folder_path[0].lower()
            remaining_path = folder_path[3:].replace('\\', '/')
            folder_path = f'/mnt/{drive_letter}/{remaining_path}'
            server_logger.info(f"[SELECT-FOLDER] Converted to WSL path: {folder_path}")
        
        if tool_type == 'inv-vzd':
            # Create InvVzdProcessor without version for scanning
            processor = InvVzdProcessor(logger=tool_logger)
            result = processor.select_folder(folder_path)
            server_logger.info(f"[SELECT-FOLDER] InvVzd scan result: {result}")
            return jsonify(result)
        else:
            server_logger.warning(f"[SELECT-FOLDER] Unknown tool type: {tool_type}")
            return jsonify({
                "success": False,
                "message": f"Unknown tool type: {tool_type}"
            }), 400
            
    except Exception as e:
        server_logger.error(f"[SELECT-FOLDER] Error: {str(e)}")
        import traceback
        server_logger.error(f"[SELECT-FOLDER] Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"Chyba při procházení složky: {str(e)}"
        }), 500

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
            processor = InvVzdProcessor(tool_logger)
            
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
        server_logger.error(f"Error processing inv-vzd: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process/inv-vzd-paths', methods=['POST'])
def process_inv_vzd_paths():
    """Process innovative education attendance files using file paths"""
    try:
        debug_print("=== InvVzd Processing Started ===")
        server_logger.info("=== InvVzd Processing Started ===")
        data = request.get_json()
        debug_print(f"Received data: {data}")
        server_logger.info(f"Received data: {data}")
        
        if not data:
            debug_print("ERROR: No data provided in request")
            server_logger.error("No data provided in request")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        file_paths = data.get('filePaths', [])
        template_path = data.get('templatePath')
        options = data.get('options', {})
        
        # Debug: Log original paths
        server_logger.info(f"Original template_path: {template_path}")
        server_logger.info(f"Original file_paths: {file_paths}")
        
        # Convert Windows paths to WSL paths if needed (only on Linux/WSL)
        def convert_path_if_needed(path):
            if path and isinstance(path, str):
                server_logger.info(f"Checking path for conversion: {path}")
                # Only convert if we're on Linux/WSL and path is Windows format
                import platform
                if platform.system() == 'Linux' and len(path) >= 3 and path[1:3] == ':\\':
                    drive_letter = path[0].lower()
                    remaining_path = path[3:].replace('\\', '/')
                    wsl_path = f'/mnt/{drive_letter}/{remaining_path}'
                    server_logger.info(f"Converting Windows path to WSL: {path} -> {wsl_path}")
                    return wsl_path
                else:
                    server_logger.info(f"Path does not match Windows pattern or not on Linux, keeping as-is: {path}")
            return path
        
        # Convert paths
        template_path = convert_path_if_needed(template_path)
        file_paths = [convert_path_if_needed(fp) for fp in file_paths]
        
        # Debug: Log converted paths
        server_logger.info(f"Converted template_path: {template_path}")
        server_logger.info(f"Converted file_paths: {file_paths}")
        
        if not file_paths:
            return jsonify({
                "status": "error",
                "message": "No file paths provided"
            }), 400
            
        if not template_path:
            server_logger.error("No template path provided")
            return jsonify({
                "status": "error",
                "message": "No template path provided"
            }), 400
        
        server_logger.info("Creating InvVzdProcessor...")
        # Process with InvVzdProcessor
        processor = InvVzdProcessor(tool_logger)
        server_logger.info(f"InvVzdProcessor created successfully")
        
        # Add template to options
        options['template'] = template_path
        server_logger.info(f"Processing with options: {options}")
        
        # Process files
        server_logger.info(f"Starting to process {len(file_paths)} files...")
        server_logger.info(f"Files to process: {file_paths}")
        server_logger.info(f"Template: {options.get('template')}")
        
        result = processor.process(file_paths, options)
        
        server_logger.info(f"Processing result: success={result.get('success')}, errors={result.get('errors', [])}")
        server_logger.info(f"Full result: {result}")
        
        # Check if we have ANY data or messages
        has_data = result.get('data') and result.get('data', {}).get('processed_files')
        has_info = result.get('info', [])
        has_errors = result.get('errors', [])
        has_warnings = result.get('warnings', [])
        
        # Prepare output files list - keep per-file structure for UI
        output_files = []
        if has_data:
            for processed in result['data']['processed_files']:
                # Convert numpy/pandas types to native Python types for JSON serialization
                hours_value = processed['hours']
                if hasattr(hours_value, 'item'):
                    hours_value = hours_value.item()  # Convert numpy/pandas scalar to Python type
                elif hasattr(hours_value, 'tolist'):
                    hours_value = hours_value.tolist()  # Convert numpy array to list
                
                # Preserve per-file structure with output filename properly set
                output_files.append({
                    'source': processed['source'],
                    'output': processed['output'] if processed['output'] else None,
                    'hours': int(hours_value) if hours_value is not None else 0,
                    'status': processed.get('status', 'unknown'),
                    'errors': processed.get('errors', []),
                    'warnings': processed.get('warnings', []),
                    'info': processed.get('info', [])
                })
        
        # Enhanced error message for path issues
        enhanced_errors = []
        for error in has_errors:
            if 'neexistuje' in error and ('D:\\' in error or 'C:\\' in error):
                enhanced_errors.append(f"{error} - PROBLÉM: Používáte Windows cestu na Linux systému. Zkopírujte soubory do Linux souborového systému nebo použijte WSL mount cestu (např. /mnt/d/...)")
            else:
                enhanced_errors.append(error)
        
        # Always return info/errors/warnings in the data field so UI can display them
        # Use "success" status even if result['success'] is False to ensure UI displays the detailed report
        return jsonify({
            "status": "success" if result['success'] else "partial",
            "message": f"Úspěšně zpracováno {len(output_files)} souborů" if output_files else "Zpracování dokončeno s chybami",
            "data": {
                "processed": len(output_files),
                "files": output_files,
                "info": has_info,
                "errors": enhanced_errors,
                "warnings": has_warnings
            },
            "errors": enhanced_errors,
            "warnings": has_warnings,
            "info": has_info
        })
            
    except Exception as e:
        debug_print(f"EXCEPTION in inv-vzd-paths: {str(e)}")
        server_logger.error(f"Error processing inv-vzd-paths: {str(e)}")
        import traceback
        debug_print(traceback.format_exc())
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
            processor = ZorSpecDatProcessor(tool_logger)
            
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
        server_logger.error(f"Error processing zor-spec: {str(e)}")
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
        auto_save = data.get('autoSave', False)  # Auto-save to source folder
        
        # Convert Windows paths to WSL paths if needed (only on Linux/WSL)
        def convert_path_if_needed(path):
            if path and isinstance(path, str):
                # Only convert if we're on Linux/WSL and path is Windows format
                import platform
                if platform.system() == 'Linux' and len(path) >= 3 and path[1:3] == ':\\':
                    drive_letter = path[0].lower()
                    remaining_path = path[3:].replace('\\', '/')
                    wsl_path = f'/mnt/{drive_letter}/{remaining_path}'
                    server_logger.info(f"Converting Windows path to WSL: {path} -> {wsl_path}")
                    return wsl_path
            return path
        
        # Convert paths
        file_paths = [convert_path_if_needed(fp) for fp in file_paths]
        
        if not file_paths:
            return jsonify({
                "status": "error",
                "message": "No file paths provided"
            }), 400
        
        # Determine output directory
        if auto_save and file_paths:
            # Use the directory of the first file as output directory
            first_file_dir = os.path.dirname(file_paths[0])
            output_dir = first_file_dir
            server_logger.info(f"Auto-save enabled, using source directory: {output_dir}")
        else:
            # Create temporary directory for processing
            output_dir = tempfile.mkdtemp()
        
        try:
            # Process with ZorSpecDatProcessor
            processor = ZorSpecDatProcessor(tool_logger)
            
            # Process files using paths directly
            result = processor.process_paths(file_paths, output_dir, options)
            
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
                
                response_data = {
                    "status": "success",
                    "message": f"Úspěšně zpracováno {result['files_processed']} souborů",
                    "data": {
                        "files_processed": result['files_processed'],
                        "unique_students": result['unique_students'],
                        "output_files": output_files,
                        "auto_saved": auto_save,
                        "output_directory": output_dir if auto_save else None
                    },
                    "errors": result.get('errors', []),
                    "warnings": result.get('warnings', []),
                    "info": result.get('info', [])
                }
                
                if auto_save:
                    response_data["message"] += f" a uloženo do zdrojové složky: {output_dir}"
                
                return jsonify(response_data)
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
            # Cleanup temp files only if not auto-save (temp directory was used)
            if not auto_save:
                import shutil
                shutil.rmtree(output_dir, ignore_errors=True)
            
    except Exception as e:
        server_logger.error(f"Error processing zor-spec-paths: {str(e)}")
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
        processor = ZorSpecDatProcessor(tool_logger)
        
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
        server_logger.error(f"Error processing zor-spec-directory: {str(e)}")
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
        processor = PlakatGenerator(tool_logger)
        
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
        server_logger.error(f"Error in plakat processing: {str(e)}")
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
    server_logger.info(f"Starting Flask server on port {port}")
    server_logger.info(f"DEBUG MODE: {DEBUG_MODE}")
    app.run(host='127.0.0.1', port=port, debug=DEBUG_MODE)