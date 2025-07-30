#! python
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, send_from_directory, abort, request, jsonify
from flask_uploads import UploadSet, configure_uploads, ALL
from werkzeug.utils import secure_filename
from waitress import serve
from pathlib import Path
from functools import wraps

logger = logging.getLogger("upboard.server")

def create_app(base_dir='assets', password=None):
    app = Flask(__name__)

    # 基础配置
    app.config.update({
        'UPLOAD_PASSWORD': password,
        'UPLOADED_FILES_DEST': Path(base_dir).resolve() / 'RELEASES',
        'MAX_CONTENT_LENGTH': 200 * 1024 * 1024,  # 200MB 文件大小限制
        'JSONIFY_PRETTYPRINT_REGULAR': True,
        'JSON_SORT_KEYS': False
    })
    
    # 配置上传扩展
    files = UploadSet('files', ALL)
    configure_uploads(app, files)
    
    @app.after_request
    def after_request(response):
        logger.info(f'{request.remote_addr} {request.scheme} {request.method} {request.full_path} {response.status}')
        return response

    def auth_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not app.config['UPLOAD_PASSWORD']:
                return f(*args, **kwargs)
                
            auth = request.headers.get('Authorization')
            if not auth or auth != app.config['UPLOAD_PASSWORD']:
                logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Valid authorization token required'
                }), 401
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/api/v1/releases/<product>/<platform>/<arch>/<filename>', methods=['PUT'])
    @app.route('/api/v1/releases/<product>/<platform>/<arch>/<version>/<filename>', methods=['PUT'])
    @auth_required
    def releases(product, platform, arch, filename, version=None):
        filename = secure_filename(filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400

        save_dir = os.path.join(product, platform, arch)
        if version:
            save_dir = os.path.join(save_dir, version)
        
        try:
            file_storage = request.files.get('file')
            if not file_storage:
                return jsonify({'error': 'No file provided'}), 400
            
            # 处理已存在文件
            oldfile = os.path.join(app.config['UPLOADED_FILES_DEST'], save_dir, filename)
            if os.path.exists(oldfile):
                if os.path.isdir(oldfile):
                    shutil.rmtree(oldfile)
                else:
                    os.remove(oldfile)

            # 保存文件（自动创建目录）
            saved_filename = files.save(
                file_storage,
                folder=save_dir,
                name=filename
            )
            logger.info(f"New release uploaded: {saved_filename}")

            saved_filename = saved_filename.replace(os.path.sep, '/')
            return jsonify({
                'message': 'File uploaded successfully',
                'path': saved_filename,
                'url': '/api/v1/update/' + saved_filename,
            }), 201

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'error': str(e),
                'message': 'File upload failed'
            }), 500

    @app.route('/api/v1/updates/<product>/<platform>/<arch>/<filename>')
    @app.route('/api/v1/updates/<product>/<platform>/<arch>/<version>/<filename>')
    def updates(product, platform, arch, filename, version=None):
        direcory = app.config['UPLOADED_FILES_DEST']

        # 先尝试带版本号的路径
        if version:
            version_path = os.path.join(direcory, product, platform, arch, version, filename)
            if os.path.exists(version_path):
                return send_from_directory(os.path.join(direcory, product, platform, arch, version), filename)

        # 如果带版本号的路径不存在，尝试不带版本号的路径
        no_version_path = os.path.join(direcory, product, platform, arch, filename)
        if os.path.exists(no_version_path):
            return send_from_directory(os.path.join(direcory, product, platform, arch), filename)

        abort(404)

    return app

def main():
    parser = argparse.ArgumentParser(description='UpBoard - Lightweight Software Update Server')
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('-P', '--port', type=int, default=5001, help='Port to listen on (default: 5001)')
    parser.add_argument('-d', '--dir', default='.', help='Base directory for releases (default: current directory)')
    parser.add_argument('-p', '--password', help='Password for publish API (optional)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%m%d %H:%M:%S",
        handlers=[
            TimedRotatingFileHandler(
                filename=os.path.join(args.dir, "upboard.server.log"),
                when="midnight",  # Rotate at midnight
                interval=1,  # Daily rotation
                backupCount=7,  # Keep 7 days of logs
                delay=True,  # Delay file creation until the first log message
            ),
            logging.StreamHandler(),  # Also log to console
        ],
    )

    if not os.path.exists(args.dir):
        logging.error(f"Directory does not exist: {args.dir}")
        os.exit(1)

    # Create the Flask app
    app = create_app(args.dir, args.password)
    if args.debug:
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Running in DEBUG mode")

    logger.info(f"UpBoard server starting on http://{args.host}:{args.port}")
    logger.info(f"Serving releases from: {Path(args.dir).resolve()}")
    logger.info(f"")
    logger.info(f"API Endpoints:")
    logger.info(f" GET /api/v1/updates/<product>/<platform>/[<version>/]<filename>")
    logger.info(f" PUT /api/v1/releases/<product>/<platform>/[<version>/]<filename>")
    logger.info(f"")
    logger.info(f"PUT Example:")
    logger.info(f" 1. upboard_publish -p admin\\")
    logger.info(f"      http://127.0.0.1:{args.port}/api/v1/releases/your-project/win32/x64/ ./RELEASES")
    logger.info(f" 2. curl -X PUT -H 'Authorization: admin' -F file=@RELEASES \\")
    logger.info(f"      http://127.0.0.1:{args.port}/api/v1/releases/your-project/win32/x64/RELEASES")
    logger.info(f"GET Example:")
    logger.info(f" 1. curl http://127.0.0.1:{args.port}/api/v1/updates/your-project/win32/x64/RELEASES")
    logger.info(f"")

    if args.password:
        logger.info("Publish API authentication is ENABLED")
    else:
        logger.warning("Publish API authentication is DISABLED")
    logger.info("Press Ctrl+C to quit")

    if app.config.get("ENV", "production") == "development":
        app.run(host=args.host, port=args.port, debug=True)
    else:
        serve(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
