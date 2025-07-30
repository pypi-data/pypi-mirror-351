def print_version():
    """Prints the version of the tool."""
    # version = pkg_resources.get_distribution('python-sysinformer').version
    # use importlib.resources to get the version
    try:
        from importlib.metadata import (  # pylint: disable=import-outside-toplevel
            version,
        )

        pcc_version = version("python-containerchecker")
        print(f"containerchecker version {pcc_version}")
    except ImportError:
        print("importlib.metadata not found")
