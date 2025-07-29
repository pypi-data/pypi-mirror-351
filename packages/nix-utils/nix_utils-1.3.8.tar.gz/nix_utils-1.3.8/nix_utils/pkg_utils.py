import pkgutil


def get_content(package_path, file_name):
    """
    Retrieves the binary content of a file packaged within the provided package.

    Returns:
        bytes: The binary content of the specified file.
    """
    return pkgutil.get_data(package_path, file_name)
