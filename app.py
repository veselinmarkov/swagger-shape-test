from chalice import Chalice
from swagger_ui import chalice_api_doc

app = Chalice(app_name='helloworld')

spec_string = '{"openapi":"3.0.1","info":{"title":"python-swagger-ui test api","description":"python-swagger-ui test api","version":"1.0.0"},"servers":[{"url":"http://127.0.0.1:8989/api"}],"tags":[{"name":"default","description":"default tag"}],"paths":{"/hello/world":{"get":{"tags":["default"],"summary":"output hello world.","responses":{"200":{"description":"OK","content":{"application/text":{"schema":{"type":"object","example":"Hello World!!!"}}}}}}}},"components":{}}'

chalice_api_doc(app, config_spec=spec_string, url_prefix='/api/doc', title='API doc')

@app.route('/', cors=True)
def index():
    return {'hello': [42, 'is', 'great']}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
