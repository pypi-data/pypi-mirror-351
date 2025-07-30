"""
Handle the submission.
"""
import os
from ciocore import data as coredata
from cionuke import const as k
from cionuke.components import instance_type, project, software
import ciocore.loggeria

logger = ciocore.loggeria.get_conductor_logger()

# In development, you can use fixtures for packages, projects, instance types.
# It saves time. Fixtures
FIXTURES_DIR = os.path.expanduser(os.path.join("~", "conductor_fixtures"))
 

def connect(submitter, force=True):
    """
    Connect to Conductor in order to access users account data.

    Menus must be repopulated.
    """

    coredata.init(product="nuke")
    if k.FEATURE_DEV:
        use_fixtures = submitter.knob("cio_use_fixtures").getValue()
        fixtures_dir = FIXTURES_DIR if use_fixtures else None
        coredata.set_fixtures_dir(fixtures_dir)

    try:
        coredata.data(force=force)
    except BaseException as ex:
        logger.exception("Try again after deleting your credentials file (~/.config/conductor/credentials)")
        raise ex
      
    if coredata.valid():
        project.rebuild_menu(submitter, coredata.data()["projects"])
        instance_type.rebuild_menu(submitter, coredata.data()["instance_types"])
        software.rebuild_menu(submitter, coredata.data().get("software"))
