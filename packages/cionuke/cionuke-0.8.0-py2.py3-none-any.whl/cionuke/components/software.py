import nuke
from ciocore import data as coredata
from cionuke import const as k

def build(submitter):
    """
    Build knobs to specify software configuration.

    Currently only Nuke version.
    """
    knob = nuke.Enumeration_Knob("cio_software", "Nuke version", [k.NOT_CONNECTED])
    knob.setTooltip("Choose a Nuke version.")
    knob.setFlag(nuke.STARTLINE)
    submitter.addKnob(knob)


def rebuild_menu(submitter, software_data):

    if not software_data:
        return

    items = sorted(software_data.supported_host_names())
    submitter.knob("cio_software").setValues(items or [k.NOT_CONNECTED])


def resolve(submitter, **kwargs):

    if (not coredata.valid()) or submitter.knob(
        "cio_software"
    ).value() == k.NOT_CONNECTED:
        return {"software_package_ids": [k.INVALID]}
    tree_data = coredata.data()["software"]
    selected = submitter.knob("cio_software").value()
    package_ids = []
    package = tree_data.find_by_path(selected)
    if package:
        package_ids = [package["package_id"]]
    return {"software_package_ids": package_ids}


def affector_knobs():
    return ["cio_software"]


def _version_parts(version):
    """
    Split a version string into its parts.

    Args:
        version (str): The version string.

    Returns:
        tuple: A tuple of the version parts.
    """
    return tuple(map(int, version.split(".")))

def find_closest_version(input_version, version_list):
    """
    Find the closest version in a list to the input version.

    Args:
        input_version (str): The version to compare.
        version_list (list): List of versions to compare against.

    Returns:
        str: The closest version to the input version.

    Logic is as follows:

    If we find the same major and minor and patch version, we use it.
    If we find the same major and minor we use the highest patch available, which might be lower than the target.
    
    If no major.minor match is found, we return the next highest version. This may be same-major, higher-minor, or it may be higher major.
    
    If no highter version is found, we use the highest version available.
    """

    the_version =   _version_parts(input_version.replace("v", "."))
    
    versions = [ _version_parts(v) for v in version_list]
    
    exact_major_minor_patch = [v for v in versions if v == the_version]
    if exact_major_minor_patch:
        return ".".join(map(str, exact_major_minor_patch[0]))
    
    same_major_minor = [v for v in versions if v[:2] == the_version[:2]]
    if same_major_minor:
        same_major_minor.sort()
        return ".".join(map(str, same_major_minor[-1]))
    
    higher_major_minor = [v for v in versions if v[:2] > the_version[:2]]
    if higher_major_minor:
        higher_major_minor.sort()
        return ".".join(map(str, higher_major_minor[0]))

    # none the same major_minor and none higher. Just return the latest version.
    versions.sort()
    return ".".join(map(str, versions[-1]))

def set_closet_version(submitter):
    """
    Detect the Nuke version and set the knob to the current version.
    """

    current_version = nuke.NUKE_VERSION_STRING
    versions = coredata.data()["software"].supported_host_names()
    version_map = {str(v.split()[1]): str(v) for v in versions}
    closest_version = find_closest_version(current_version, version_map.keys())
    submitter.knob("cio_software").setValue(version_map[closest_version])

