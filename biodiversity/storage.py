from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    If a file isn’t found in the staticfiles.json manifest at runtime, a ValueError is raised.
    This behavior can be disabled by subclassing ManifestStaticFilesStorage and setting the
    manifest_strict attribute to False – nonexistent paths will remain unchanged.
    """
    manifest_strict = False
