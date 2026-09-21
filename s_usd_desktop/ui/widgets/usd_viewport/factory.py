def create_usd_viewport(parent=None):
    try:
        from .viewport_widget import UsdViewportWidget
    except ModuleNotFoundError as error:
        if error.name != "pxr.Usdviewq" and not error.name.startswith(
            "pxr.Usdviewq."
        ):
            raise

        from .unavailable_viewport import UnavailableUsdViewportWidget

        return UnavailableUsdViewportWidget(
            reason=f"Missing optional dependency: {error.name}",
            parent=parent
        )

    return UsdViewportWidget(parent=parent)