from flask import Flask, request, Response, jsonify
import requests, json, re
import consul

app = Flask(__name__)

# Initialize Consul client
consul_client = consul.Consul(host='localhost', port=8500)

def get_service_url(service_name):
    _, services = consul_client.health.service(service_name, passing=True)
    if services:
        service = services[0]['Service']
        return f"http://{service['Address']}:{service['Port']}"
    return None

def forward_request(service_name, path):
    service_url = get_service_url(service_name)
    if not service_url:
        return jsonify({"error": f"Service {service_name} not available"}), 503
    target_url = f"{service_url}/{path}"
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.headers.items()
               if name.lower() not in excluded_headers]
    
    # Sửa nội dung HTML cho phù hợp khi đi qua gateway
    content = resp.content
    content_type = resp.headers.get('content-type', '')
    if content_type.startswith('text/html'):
        content_str = content.decode('utf-8')

        # Chuẩn hóa các liên kết/biểu mẫu để đi qua gateway
        # Users
        content_str = re.sub(r'href="/users/', 'href="/users/', content_str)
        content_str = re.sub(r'action="/users/', 'action="/users/', content_str)

        # Books
        content_str = re.sub(r'href="/books/', 'href="/books/', content_str)
        content_str = re.sub(r'action="/books/', 'action="/books/', content_str)

        # Borrow (local prefix là /borrow → gateway prefix là /borrows)
        content_str = re.sub(r'href="/borrow/', 'href="/borrows/', content_str)
        content_str = re.sub(r'action="/borrow/', 'action="/borrows/', content_str)

        content = content_str.encode('utf-8')
    
    return Response(content, resp.status_code, headers)

@app.route('/')
def home():
    return jsonify({
        "message": "Gateway API đang hoạt động",
        "services": {
            "user_service": get_service_url('user-service'),
            "book_service": get_service_url('book-service'),
            "borrow_service": get_service_url('borrow-service')
        },
        "available_endpoints": {
            "users": "/users/<path>",
            "books": "/books/<path>",
            "borrows": "/borrows/<path>"
        }
    })

# ---- USERS ----
@app.route('/users', methods=["GET","POST"])
@app.route('/users/', methods=["GET","POST"])
def user_root():
    return forward_request('user-service', "users/")

@app.route('/users/<path:path>', methods=["GET","POST","PUT","DELETE"])
def user_proxy(path):
    return forward_request('user-service', f"users/{path}")

# ---- BOOKS ----
@app.route('/books', methods=["GET","POST"])
@app.route('/books/', methods=["GET","POST"])
def book_root():
    return forward_request('book-service', "books/")

@app.route('/books/<path:path>', methods=["GET","POST","PUT","DELETE"])
def book_proxy(path):
    return forward_request('book-service', f"books/{path}")

# ---- BORROWS ----
@app.route('/borrows', methods=["GET","POST"])
@app.route('/borrows/', methods=["GET","POST"])
def borrow_root():
    return forward_request('borrow-service', "borrow/")

@app.route('/borrows/<path:path>', methods=["GET","POST","PUT","DELETE"])
def borrow_proxy(path):
    return forward_request('borrow-service', f"borrow/{path}")

# ---- STATIC ----
@app.route('/static/<path:path>', methods=["GET"])
def static_proxy(path):
    return forward_request('user-service', f"static/{path}")

if __name__ == '__main__':
    app.run(port=8000, debug=False)
