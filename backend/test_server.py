from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "AI Pet Backend API"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        print(f"Received POST request to: {self.path}")
        if self.path == '/api/chat' or self.path.endswith('/api/chat'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "response": f"你好！我收到了你的消息12312：{data.get('message', '')}。这是一个简化版的回复，完整功能需要配置Qwen API和Milvus向量数据库。"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    PORT = 8888
    server = HTTPServer(('127.0.0.1', PORT), SimpleHTTPRequestHandler)
    print(f'Server running at http://127.0.0.1:{PORT}')
    server.serve_forever()
