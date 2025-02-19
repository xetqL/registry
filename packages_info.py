import glob
import json
import re
from packaging import version


DOWNLOAD_DIR = "./downloads/"
PREV_VERSIONS = "prev-versions"

def get_package_name(file):
    m = re.search(re.escape(DOWNLOAD_DIR) + "(.*)@(?:.*).json", file)
    if m:
        return m.group(1)
    return None

def extract_package_metadata(file, pkg):
    # Opening JSON file
    with open(file) as json_file:
        data = json.load(json_file)
        for package in data.get("packages", []):
            if package.get("name", "") == pkg:
                package.pop("dependencies")
                package.pop("targets")
                package.pop("features")
                return package
    return None

def list_contains(list, pkg):
    for package in list:
        if package.get("name", "") == pkg:
            return True
    return False

def update_prev_versions(list, pkg, metadata):
    for i in range(len(list)):
        curr_metadata = list[i]
        if curr_metadata.get("name", "") == pkg:
            curr_version = curr_metadata.get("version", "0.0.0")
            new_version = metadata.get("version", "0.0.0")
            curr_prev_version = curr_metadata.get(PREV_VERSIONS, [])
            if version.parse(curr_version) < version.parse(new_version):
                print(f"{new_version} is newer than {curr_version}")
                # new version is the new one
                curr_prev_version.append(curr_version)
                curr_prev_version.sort()
                metadata[PREV_VERSIONS] = curr_prev_version
                list[i] = metadata
            else:
                curr_metadata[PREV_VERSIONS].append(new_version)
                curr_metadata[PREV_VERSIONS].sort()

def add_package(list, pkg, metadata):
    if not list_contains(list, pkg):
        metadata[PREV_VERSIONS]=[]
        list.append(metadata)
    else:
        update_prev_versions(list, pkg, metadata)

if __name__ == '__main__':
    packages_list = []
    # Find all json files in downloads
    python_files = glob.glob(DOWNLOAD_DIR + "*.json")
    for file in python_files:
        if (pkg := get_package_name(file)) is not None:
            if (metadata := extract_package_metadata(file, pkg)) is not None:
                add_package(packages_list, pkg, metadata)
    packages_info = dict()
    packages_info["packages"] = packages_list
    with open('packages_info.json', 'w', encoding='utf-8') as f:
        json.dump(packages_info, f, ensure_ascii=False, indent=4)