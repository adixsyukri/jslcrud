from morepath.publish import resolve_model as _resolve_model


def resolve_model(request):
    newreq = request.app.request_class(
        request.environ.copy(), request.app, path_info=request.path)
    context = _resolve_model(newreq)
    context.request = request
    return context

