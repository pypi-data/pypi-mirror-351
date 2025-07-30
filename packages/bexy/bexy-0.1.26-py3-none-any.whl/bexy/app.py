#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bexy Application Entry Point

This module serves as the entry point for the Bexy service.
It provides a REST API for executing Python code in a sandbox environment.
"""

import argparse
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Initialize logging with LogLama
from bexy.logging_config import init_logging, get_logger

# Initialize logging first, before any other imports
init_logging()

# Get a logger for this module
logger = get_logger('app')

class BexyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'ok',
                'message': 'Bexy service is healthy'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'message': 'Not found'
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                code = data.get('code', '')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'output': f'Dummy execution of code: {code[:50]}...',
                    'error': None
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'error',
                    'message': str(e)
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'message': 'Not found'
            }
            self.wfile.write(json.dumps(response).encode())

def run_server(host='127.0.0.1', port=8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, BexyHandler)
    logger.info(f'Starting Bexy server on {host}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Stopping Bexy server')
        httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description='Bexy - Python Code Execution Sandbox')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
