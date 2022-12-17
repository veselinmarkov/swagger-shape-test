from chalice.test import Client
from app import app
from boast.shapematch import Shape

def test_index():
    api = Shape('OpenAPI_config.yaml')
    rootPath = api.getPath('/')
    assert rootPath.testPath(subTest)
#    with Client(app) as client:
#        response = client.http.get('/')
#        subTest(response)

# callable to be provided to testPath. It should return API JSON response
def subTest(path):
    with Client(app) as client:
        return client.http.get(path).json_body

#if __name__ != "":
    #with open('OpenAPI_config.yaml') as f:
    #    data = yaml.load(f, Loader=yaml.FullLoader)
        #print(json.dumps(data['paths'], indent=3))

#    api = ApiConfig('OpenAPI_config.yaml')
#    rootPath = api.getPath('/')
#    print (rootPath.testPath(subTest))