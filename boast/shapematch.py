import yaml
import json

class ShapeException(Exception):
    pass

class Path():
    pass

class Shape():
    "Compare the shape of OpenAPI definition schema to a real JSON record"
    def __init__(self, openAPIConfigFile) -> None:
        self.yamlDict = None
        try:
            with open(openAPIConfigFile) as f:
                self.yamlDict = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError as notFound:
            raise ShapeException(notFound)
        except yaml.YAMLError as yamlErr:
            raise ShapeException(yamlErr)

    def getPath(self, pathStr) -> Path:
        if pathStr not in self.yamlDict['paths']:
            raise ShapeException(f"The specified path {pathStr} is not in OpenAPI")
        return Path(self, pathStr)

    def compare(pathName, jsonDict):
        """ works on specific path, which should exist in OpenAPI file
            do the comparison and make assertions. Should be invoked in test environment
            It a recursive function
        """

    def resolveReferences(self, schema:dict) -> dict:
        "solve references like: '$ref': '#/components/schemas/Hello'"
        if isinstance(schema, dict) and '$ref' not in schema:
            # is's a dict, so durectly return it
            return schema
        refStr = schema['$ref']
        start = refStr.index('#/')
        if start == -1:
            raise ShapeException(f"The refererence string {refStr} is not matching, Example: #/components/schemas/Hello")
        ref = refStr[start +2:].replace('/', '.')
        return Path.dotNotationExtract(ref, self.yamlDict)


def indentRecursion(func):
    def wrapperForIndent(*args, **kwargs):
        Path.indent += 5 
        func(*args, **kwargs)
        Path.indent -= 5

    return wrapperForIndent


class Path():
    "represents a specific path in the API config"
    indent = 0

    @staticmethod
    def dotNotationExtract(notation, aDict):
        "extract subDictionary based on dot notation. Example: get.parameters"
        notList = notation.split('.')
        currDict = aDict
        for level in notList:
            if level not in currDict:
                raise ShapeException(f"The item {level} is missing in the API config " +json.dumps(aDict, indent=3))
            currDict = currDict[level]
        return currDict

    def __init__(self, config: Shape, path: str):
        "expect a dictionary for a path got from OpenAPI json file"
        "also only a get method will be tested and must exist"
        self.config = config
        self.path = path
        self.pathDict = config.yamlDict['paths'][path]
        self.schema = None
        """ self.parameters = None
        if 'get' not in pathDict:
            raise ShapeException("get method must exists in path definition:" +json.dumps(pathDict, indent=3))
        getDict = pathDict['get']
        self.parameters = getDict.get('parameters', None)
        if 'responses' not in getDict or '200' not in getDict['responses']:
            raise ShapeException("responses and response 200 must exist in the path definition" +json.dumps(pathDict, indent=3))
        twoHundredDict = getDict['responses']['200']
        if 'content' not in twoHundredDict or 'application/json' not in twoHundredDict['content']\
            or 'schema' not in 
            raise ShapeException("responses and response 200 must exist in the path definition" +json.dumps(pathDict, indent=3)) """
        self.parameters = Path.dotNotationExtract('get.parameters', self.pathDict)
        self.schema = Path.dotNotationExtract('get.responses.200.content.application/json.schema', self.pathDict)
        #self.schema = Path.resolveReferences(self.schema, config.yamlDict)

    def compareShapes(self, shape: dict, response: dict) -> bool:
        "compares API JSON response against OpenAPI definition shape"
        "check if the shape is not a reference"
        shape = self.config.resolveReferences(shape)
        print(f'{" "*Path.indent}Test shape: {shape}, to item: {response}')
        if not isinstance(shape, dict):
            raise ShapeException(f"{' '*Path.indent}The shape parameter must be a dictionary")
        if 'type' not in shape:
            raise ShapeException(f"{' '*Path.indent}The shape {shape} do not contain type 'item'")
        typeDef = str(shape['type']).upper()
        if typeDef == 'STRING':
            #raise ShapeException(f'shape: {shape}, response: {response}, isinstance_str: {isinstance(response, str)}')
            res = isinstance(response, str)
            if not res:
                raise ShapeException(f"{' '*Path.indent}The item: {response} is not of type string")
            return True
        elif typeDef == 'INTEGER':
            try:
                int(response)
                return True
            except ValueError:
                raise ShapeException(f"{' '*Path.indent}The item: {response} is not of type integer")
        elif typeDef == 'OBJECT':
            if 'properties' not in shape:
                raise ShapeException(f"{' '*Path.indent}The shape {shape} do not contain 'properties' item")
            # iterate simultaneously schema and the JSON response
            subShape = shape['properties']
            for key in subShape:
                #assert key in response
                if key not in response:
                    raise ShapeException(f"{' '*Path.indent}The response {response} do not contain item {key}")
                Path.indent += 5 
                res = self.compareShapes(subShape[key], response[key])
                #raise ShapeException(f'res returned: {res}')
                Path.indent -= 5
                if not res:
                    return False
            return True
        elif typeDef == 'ARRAY':
            if 'items' not in shape:
                raise ShapeException(f"{' '*Path.indent}The shape {shape} do not contain 'items' item")
            subShape = shape['items']
            try:
                response.__iter__()
            except TypeError:
                raise ShapeException(f"{' '*Path.indent}The JSON {response} must be an array")
            for e in response:
                Path.indent += 5 
                res = self.compareShapes(subShape, e)
                Path.indent -= 5 
                #raise ShapeException(f'res returned: {res}')
                if not res:
                    return False
            return True
        return True


    def testPath(self, ApiQuery: callable) -> bool:
        Path.indent =0
        if not callable(ApiQuery):
            raise ShapeException("The provided Api query function is not callable")
        print('Start testing path:' + self.path)
        print('-'*25)
        print('Schema captured from OpenAPI:' +json.dumps(self.schema, indent=3))
        response = ApiQuery(self.path)
        print('Response retunrned: ' +json.dumps(response, indent=3))
        try:
            return self.compareShapes(self.schema, response)
            #print('OK Matched.')
        except ShapeException as e:
            print(str(e))
            print('Not matched!')
        return False