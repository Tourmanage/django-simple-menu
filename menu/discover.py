def autodiscover():
    """
    load_menus loops through INSTALLED_APPS and loads the menu.py
    files from them.
    """
    import django
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    # Fetch all installed app names
    if django.VERSION < (1, 7):
        mods = [(app, import_module(app)) for app in settings.INSTALLED_APPS]
    else:
        from django.apps import apps
        mods = [(app_config.name, app_config.module) for app_config in apps.get_app_configs()]

    # loop through our INSTALLED_APPS
    for (app, mod) in mods:
        # skip any django apps
        if app.startswith("django."):
            continue

        module = '%s.menus' % app
        try:
            import_module(module)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have an menus module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'menus'):
                raise
