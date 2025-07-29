def path(*subpath) -> str:
    return "/" + "/".join(
        f"{i}".removeprefix("/").removesuffix("/") for i in subpath
    )
