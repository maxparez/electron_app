from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import tools
from tools.inv_vzd_processor import InvVzdProcessor
# from tools.zor_spec_processor import ZorSpecProcessor
# from tools.plakat_generator import PlakatGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
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
            return jsonify({
                "status": "error",
                "message": "Zpracování selhalo",
                "errors": result.get('errors', []),
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
    """Process special attendance data"""
    try:
        # Get files from request
        if 'files' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No files provided"
            }), 400
        
        files = request.files.getlist('files')
        options = request.form.get('options', {})
        
        # TODO: Implement processing logic
        logger.info(f"Processing {len(files)} files for zor-spec")
        
        return jsonify({
            "status": "success",
            "message": f"Processing {len(files)} files",
            "data": {
                "processed": len(files)
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing zor-spec: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/generate/plakat', methods=['POST'])
def generate_plakat():
    """Generate poster PDF"""
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # TODO: Implement generation logic
        logger.info("Generating plakat")
        
        return jsonify({
            "status": "success",
            "message": "Plakat generated",
            "data": {
                "file_path": "/path/to/generated.pdf"
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating plakat: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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