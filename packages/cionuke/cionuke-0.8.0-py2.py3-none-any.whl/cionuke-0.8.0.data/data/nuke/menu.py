import os
import sys

# Add cionuke and all its dependencies. If pip wasn't used to install, those dependencies will need
# to be added to PYTHONPATH env variable
lib_path = os.path.abspath(os.path.join("..", os.path.dirname(os.path.dirname(__file__))))
sys.path.append(lib_path)

import ciocore.loggeria
import ciocore.config
import ciocore.api_client

# Setup logging
# Nuke monkeypatches sys.stdout, resulting logging from threads being unsafe
# Until a workaround is found, we only log to file
logging_dir = ciocore.loggeria.get_default_log_dir()
ciocore.loggeria.setup_conductor_logging(
    logger_level =  ciocore.loggeria.LEVEL_MAP.get(ciocore.config.get()['log_level']),
    disable_console_logging = True,
    propagate=False,
    log_filename="nuke_submitter"
 )

ciocore.api_client.ApiClient.register_client(client_name="cionuke")

print ("Conductor log: {}".format(ciocore.loggeria.LOG_PATH))

from cionuke.components import  environment, metadata, preview, assets

from cionuke import conductor_menu, entry 
from cionuke import const as k



nuke.menu("Nuke").addCommand("Render/Render selected on Conductor", lambda: entry.add_to_nodes())

if k.FEATURE_DEV:
    nuke.menu("Nuke").addCommand("Render/CIO Dev Refresh and Create", lambda: conductor_menu.dev_reload_recreate())