__all__ = ['Service']

from importlib.util import spec_from_file_location, module_from_spec
from os import getcwd, listdir, environ
from os.path import isfile, join, splitext, basename
from sys import modules

from openapi_core import OpenAPI
from openapi_core.contrib.starlette.middlewares import StarletteOpenAPIMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class Service(Starlette):
    def __init__(self):
        openapi = Service.load_openapi()
        middleware = Service.build_middleware(openapi)
        routes = Service.build_routes(Service.load_controllers(), openapi)

        super().__init__(
            routes=routes,
            middleware=middleware,
        )

    @staticmethod
    def build_routes(controllers, openapi):
        routes = []
        paths = openapi.spec / 'paths'

        if not paths.exists():
            raise ValueError('No paths in specification')

        allowed_methods = {'get', 'post', 'put', 'patch', 'delete'}

        for path, path_object in paths.items():
            for method, operation in path_object.items():
                if method in allowed_methods and 'operationId' in operation:
                    operation_id = operation['operationId']
                    controller = controllers[operation_id]
                    endpoint = Service.build_endpoint(controller)

                    routes.append(Route(
                        path=path,
                        endpoint=endpoint,
                        methods=[method],
                    ))

        return routes

    @staticmethod
    def build_endpoint(controller):
        async def endpoint(request):
            result = await controller({
                **request.scope['openapi'].parameters.path,
                **request.scope['openapi'].parameters.query,
                'body': request.scope['openapi'].body
            })

            return JSONResponse(result) if result else Response()

        return endpoint

    @staticmethod
    def build_middleware(openapi):
        return [Middleware(StarletteOpenAPIMiddleware, openapi=openapi)]

    @staticmethod
    def load_openapi():
        spec_path = environ.get('APIFACTORY_SPEC_PATH', './spec.yml')

        return OpenAPI.from_file_path(join(getcwd(), spec_path))

    @staticmethod
    def load_controllers():
        controllers = {}
        controllers_path = environ.get('APIFACTORY_CONTROLLERS_PATH', './controllers')

        for filename in listdir(controllers_dir := join(getcwd(), controllers_path)):
            if isfile(file_path := join(controllers_dir, filename)) and filename.endswith('.py'):
                module_name = 'controllers.' + splitext(basename(file_path))[0]
                spec = spec_from_file_location(module_name, file_path)
                module = module_from_spec(spec)
                modules[module_name] = module
                spec.loader.exec_module(module)
                controllers.update(module.__dict__)

        return controllers
