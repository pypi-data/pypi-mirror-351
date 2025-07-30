def parse(packages_string: str):
    packages = packages_string.splitlines()
    packages_formatted = []
    for p in packages:
        if p != "" and not p.startswith("# "):
            packages_formatted.append(p)
    return packages_formatted

def get_package_list(path: str = "./src/packages.nv"):
    with open(path, "r") as f:
        return parse(f.read())