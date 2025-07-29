import inspect
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from fastapi import APIRouter, FastAPI, params
from fastapi.routing import APIRoute, APIWebSocketRoute

from fastapi_exts._utils import (
    Is,
    add_parameter,
    list_parameters,
    new_function,
    update_signature,
)
from fastapi_exts.logger import logger
from fastapi_exts.responses import Response, build_responses

from ._utils import iter_class_dependency


T = TypeVar("T")


Fn = TypeVar("Fn", bound=Callable)


class CBV:
    def __init__(self, router: APIRouter | FastAPI, /) -> None:
        self.router = router
        self._router = APIRouter()

    @property
    def get(self):
        return self._router.get

    @property
    def put(self):
        return self._router.put

    @property
    def post(self):
        return self._router.post

    @property
    def delete(self):
        return self._router.delete

    @property
    def patch(self):
        return self._router.patch

    @property
    def trace(self):
        return self._router.trace

    @property
    def websocket(self):
        return self._router.websocket

    @property
    def ws(self):
        return self._router.websocket

    def route_handle(
        self,
        endpoint: Callable,
        handle: Callable[[APIRoute], None | APIRoute],
    ):
        for route in self._router.routes:
            if isinstance(route, APIRoute) and route.endpoint == endpoint:
                handle(route)

    def responses(self, *responses: Response) -> Callable[[Fn], Fn]:
        def decorator(fn: Fn) -> Fn:
            self.route_handle(
                fn,
                lambda route: route.responses.update(
                    build_responses(*responses)
                ),
            )

            return fn

        return decorator

    def _create_class_dependencies(self, cls: type):
        def collect_class_dependencies(**kwds):
            return kwds

        parameters = [
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=dep,
                annotation=typ,
            )
            for name, dep, typ in iter_class_dependency(cls)
        ]

        update_signature(collect_class_dependencies, parameters=parameters)
        return collect_class_dependencies

    @staticmethod
    def _create_class_instance(*, cls: type, **dependencies):
        """创建类实例"""
        instance = cls()
        for k, v in dependencies.items():
            setattr(instance, k, v)

        post_init = getattr(instance, "__post_init__", None)
        if callable(post_init):
            post_init()

        return instance

    def _create_instance_function(self, origin: Callable, cls: type):
        """创建实例函数"""

        class_dependencies = self._create_class_dependencies(cls)
        name = class_dependencies.__name__

        no_self_arguments = list_parameters(origin)[1:]
        parameters = add_parameter(
            no_self_arguments,
            name=name,
            default=params.Depends(class_dependencies),
        )

        # 创建一个不带有 self 参数的函数, 并且带有类依赖的函数
        fn = new_function(origin, parameters=parameters)
        if Is.coroutine_function(origin):

            @wraps(fn)
            async def async_wrapper(*args, **kwds):
                dependencies = kwds.pop(name)
                instance = self._create_class_instance(cls=cls, **dependencies)
                return await origin(instance, *args, **kwds)

            return async_wrapper

        @wraps(fn)
        def wrapper(*args, **kwds):
            dependencies = kwds.pop(name)
            instance = self._create_class_instance(cls=cls, **dependencies)
            return origin(instance, *args, **kwds)

        return wrapper

    def __call__(self, cls: type[T], /) -> type[T]:
        api_routes = [
            (index, i)
            for index, i in enumerate(self._router.routes)
            if isinstance(i, APIRoute | APIWebSocketRoute)
        ]

        for _index, route in api_routes:
            endpoint = route.endpoint
            if hasattr(cls, endpoint.__name__):
                self._router.routes.remove(route)
                if not isinstance(endpoint, staticmethod):
                    new_fn = self._create_instance_function(endpoint, cls)
                    setattr(route, "endpoint", new_fn)
                    logger.debug(
                        f"Update route {route.path} endpoint to {new_fn.__name__}"  # noqa: E501
                    )
                self._router.routes.append(route)

        self.router.include_router(self._router)
        self._router.routes = []

        return cls
