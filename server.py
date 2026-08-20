import json
from wsgiref.simple_server import make_server

tasks = {}
next_id = 0


def app(env, start_response):
    global next_id

    def json_response(dict, status):
        start_response(status, [("Content-Type", "application/json")])
        return [json.dumps(dict).encode()]

    def empty_response(status):
        start_response(status, [("Content-Type", "text/plain")])
        return [b""]

    method = env["REQUEST_METHOD"]
    path = env["PATH_INFO"]
    length = int(env["CONTENT_LENGTH"] or "0")
    query = env["wsgi.input"].read(length) or "{}"
    data = json.loads(query)

    path_parts = path.split("/")

    if len(path_parts) < 2 or path_parts[1] != "tasks":
        return empty_response("404 Not Found")

    task_id = int(path_parts[2]) if len(path_parts) >= 3 else None

    if method == "GET":
        if task_id == None:
            return json_response(tasks, "200 OK")
        else:
            if task_id in tasks:
                return json_response(tasks[task_id], "200 OK")
            else:
                return empty_response("404 Not Found")
    elif method == "POST":
        tasks[next_id] = data
        next_id = next_id + 1

        return json_response({"id": next_id - 1, "title": data["title"]}, "201 Created")
    elif method == "PATCH":
        if task_id == None or task_id not in tasks:
            return empty_response("404 Not Found")
        else:
            for key in data:
                tasks[task_id][key] = data[key]
            return json_response(tasks[task_id], "200 OK")
    elif method == "DELETE":
        if task_id == None or task_id not in tasks:
            return empty_response("404 Not Found")
        else:
            del tasks[task_id]
            return empty_response("200 OK")


with make_server("", 9200, app) as server:
    print(f"Started on port {server.server_port}")
    server.serve_forever()
