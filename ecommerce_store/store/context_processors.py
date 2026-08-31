# store/context_processors.py
def vendor_store(request):
    if request.user.is_authenticated and hasattr(request.user, "vendor"):
        return {"store": request.user.vendor}   # not .vendor.store
    return {}