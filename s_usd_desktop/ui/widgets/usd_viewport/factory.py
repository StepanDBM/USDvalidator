from s_usd_desktop.runtime import detect_runtime_capabilities


def create_usd_viewport(parent=None, capabilities=None):
    capabilities = capabilities or detect_runtime_capabilities()

    if not capabilities.viewport_available:
        return _unavailable(capabilities, parent)

    try:
        from .viewport_widget import UsdViewportWidget
        return UsdViewportWidget(parent=parent)
    except (ImportError, OSError, RuntimeError) as error:
        return _unavailable(
            capabilities,
            parent,
            startup_error=f"{type(error).__name__}: {error}"
        )


def _unavailable(capabilities, parent, startup_error=""):
    from .unavailable_viewport import UnavailableUsdViewportWidget

    return UnavailableUsdViewportWidget(
        capabilities=capabilities,
        startup_error=startup_error,
        parent=parent
    )
