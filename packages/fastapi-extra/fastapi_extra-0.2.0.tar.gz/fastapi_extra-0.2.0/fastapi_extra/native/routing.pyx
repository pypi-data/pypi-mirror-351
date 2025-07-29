__author__ = "ziyan.yin"
__describe__ = ""

cimport cython

from typing import MutableMapping

from starlette import _utils as starlette_utils
from starlette.datastructures import URL
from starlette.responses import RedirectResponse


@cython.no_gc
cdef class RouteNode:
    cdef readonly:
        list routes
        dict leaves
        unicode prefix

    def __cinit__(self, prefix):
        self.prefix = prefix
        self.routes = []
        self.leaves = {}

    def add_route(self, route):
        self.routes.append(route)

    def add_leaf(self, node):
        if node.prefix in self.leaves:
            raise KeyError(node.prefix)
        else:
            self.leaves[node.prefix] = node


cdef list change_path_to_ranks(unicode path):
    ranks = path.lstrip('/').split('/')
    return ranks


cdef void add_route(unicode path, RouteNode root, object route):
    current_node = root
    ranks = change_path_to_ranks(path)
    for r in ranks:
        if r.find('{') >= 0 and r.find('}') > 0:
            break
        if not r:
            continue
        if r in current_node.leaves:
            current_node = current_node.leaves[r]
        else:
            next_node = RouteNode.__new__(RouteNode, r)
            current_node.add_leaf(next_node)
            current_node = next_node
    current_node.add_route(route)


cdef list find_routes(unicode path, RouteNode root):
    current_node = root
    ranks = change_path_to_ranks(path)

    routes = []
    if current_node.routes:
        routes += current_node.routes
    for r in ranks:
        if not r:
            continue
        if r in current_node.leaves:
            current_node = current_node.leaves[r]
            if current_node.routes:
                routes += current_node.routes
            continue
        break
    return routes


root_node = RouteNode.__new__(RouteNode, "")


async def handle(router, scope, receive, send):
    assert scope["type"] in ("http", "websocket", "lifespan")

    if "router" not in scope:
        scope["router"] = router

    if scope["type"] == "lifespan":
        await router.lifespan(scope, receive, send)
        return

    partial = None

    scope["path"] = route_path = starlette_utils.get_route_path(scope)
    scope["root_path"] = ""
    matched_routes = find_routes(route_path, root_node)
    n = len(matched_routes)

    for i in range(n):
        route = matched_routes[n - i - 1]
        match, child_scope = route.matches(scope)
        if match.value == 2:
            scope.update(child_scope)
            await route.handle(scope, receive, send)
            return
        elif match.value == 1 and partial is None:
            partial = route
            partial_scope = child_scope

    if partial is not None:
        scope.update(partial_scope)
        await partial.handle(scope, receive, send)
        return


    if scope["type"] == "http" and router.redirect_slashes and route_path != "/":
        redirect_scope = dict(scope)
        if route_path.endswith("/"):
            redirect_scope["path"] = redirect_scope["path"].rstrip("/")
        else:
            redirect_scope["path"] = redirect_scope["path"] + "/"

        for i in range(n):
            route = matched_routes[n - i - 1]
            match, child_scope = route.matches(redirect_scope)
            if match.value != 0:
                redirect_url = URL(scope=redirect_scope)
                response = RedirectResponse(url=str(redirect_url))
                await response(scope, receive, send)
                return

    await router.default(scope, receive, send)


def install(app):
    for route in app.routes:
        add_route(route.path, root_node, route)
    app.router.app = handle
