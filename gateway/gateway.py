from flask import Flask, request, Response, jsonify
import requests, json, re

app = Flask(__name__)

# Load registry
with open("registry.json") as f:
    registry = json.load(f)

def forward_request(service_url, path):
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
            "user_service": registry['user_service'],
            "book_service": registry['book_service'],
            "borrow_service": registry['borrow_service']
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
    return forward_request(registry['user_service'], "users/")

@app.route('/users/<path:path>', methods=["GET","POST","PUT","DELETE"])
def user_proxy(path):
    return forward_request(registry['user_service'], f"users/{path}")

# ---- BOOKS ----
@app.route('/books', methods=["GET","POST"])
@app.route('/books/', methods=["GET","POST"])
def book_root():
    return forward_request(registry['book_service'], "books/")

@app.route('/books/<path:path>', methods=["GET","POST","PUT","DELETE"])
def book_proxy(path):
    return forward_request(registry['book_service'], f"books/{path}")

# ---- BORROWS ----
@app.route('/borrows', methods=["GET","POST"])
@app.route('/borrows/', methods=["GET","POST"])
def borrow_root():
    return forward_request(registry['borrow_service'], "borrow/")

@app.route('/borrows/<path:path>', methods=["GET","POST","PUT","DELETE"])
def borrow_proxy(path):
    return forward_request(registry['borrow_service'], f"borrow/{path}")

# ---- STATIC ----
@app.route('/static/<path:path>', methods=["GET"])
def static_proxy(path):
    return forward_request(registry['user_service'], f"static/{path}")

if __name__ == '__main__':
    app.run(port=8000, debug=False)
