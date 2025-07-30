"""
Validate the submission.
"""

import os
import sys

from ciocore.validator import Validator
from cionuke import const as k
from cionuke.components import frames,  advanced, assets
from cionuke import connect

from ciocore import data as coredata


import json


class ValidateConductorData(Validator):

    def run(self, _):
        """
        This validator checks that the Conductor data is valid and has not become outdated.

        It is required because the user may have opened an old scene file pointing to resources that are no longer available on Conductor.

        It remmbers existing values for project, instance type, and Nuke version. It then connects to Conductor (which updates the selected values) and checks to see if the available values have changed. If they have, it warns the user. It does not block the submission, because the changed resource may be perfectly acceptable. Example: Trojan War => Troy, or Nuke14.0 => Nuke14.5

        If for some reason after connecting, the data is still invalid, it will block the submission.

        No messages are generated if all the data is valid and did not change after a connect.
        """

        invalid_msg = "Conductor data is not valid. Please press the Connect button and check the configuration for Project, Instance type, and Nuke version before you re-submit."

        orig_project = self._submitter.knob("cio_project").value()
        orig_insttype = self._submitter.knob("cio_insttype").value()
        orig_software = self._submitter.knob("cio_software").value()

        connect.connect(self._submitter)

        project = self._submitter.knob("cio_project").value()
        insttype = self._submitter.knob("cio_insttype").value()
        software = self._submitter.knob("cio_software").value()

        if (
            not coredata.valid()
            or project == k.NOT_CONNECTED
            or insttype == k.NOT_CONNECTED
            or software == k.NOT_CONNECTED
        ):
            self.add_error(invalid_msg)
            return

        template = "Available {resource}s on Conductor may have changed since you last set the value: {orig_value} -> {new_value}. If {new_value} is incorrect, close this panel and choose the correct {resource}."

        msgs = []
        if project != orig_project:
            msgs.append(
                template.format(
                    resource="project", orig_value=orig_project, new_value=project
                )
            )

        if insttype != orig_insttype:
            msgs.append(
                template.format(
                    resource="instance type",
                    orig_value=orig_insttype,
                    new_value=insttype,
                )
            )

        if software != orig_software:
            msgs.append(
                template.format(
                    resource="Nuke version",
                    orig_value=orig_software,
                    new_value=software,
                )
            )

        if msgs:
            self.add_warning("\n\n".join(msgs))


# TODO: Implement auto chunking for over k.MAX_TASK_COUNT frames. Then we'll be able to remove this validator. Check Maya submitter for reference.
class ValidateTaskCount(Validator):
    def run(self, _):
        main_seq, scout_seq = frames.get_sequences(self._submitter)

        count = len(main_seq.chunks())
        if count > 1000:
            self.add_warning(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(
                    count
                )
            )

class ValidateOutputPath(Validator):
    def run(self, _):
        
        output_path = advanced.evaluate_output_path(self._submitter)
            
 
        if not output_path:
            self.add_error("The Conductor output path has not been set. Please ensure the the file knob on your Write nodes is properly set.")
            return

        invalid_asset_paths = []

        output_paths = assets.resolve(self._submitter, should_scrape_assets=True)
            
        for p in output_paths:

            if os.path.abspath(p).startswith(os.path.abspath(output_path)):
                invalid_asset_paths.append(p)

        if invalid_asset_paths:
            self.add_error(
                "This submission contains dependencies that are located within the output path ({}). The output path can not be the root of any files being uploaded as part of this job.\n\nPlease change the output path to a more specific folder. Alternatively, relocate the offending dependencies.\n\n\t{}".format(
                    output_path, "\n\t".join(invalid_asset_paths)
                )
            )

def run(submitter):

    meta_warnings = set()

    validators = [plugin(submitter) for plugin in Validator.plugins()]

    for validator in validators:
        try:
            validator.run(None)
        except BaseException as ex:
            meta_warnings.add(
                "[{}]:\nValidator failed to run. Don't panic, it's probably due to an unsupported feature and can be ignored.\n{}".format(
                    validator.title(), str(ex)
                )
            )

    return {
        "error": list(set.union(*[validator.errors for validator in validators])),
        "warning": list(set.union(*[validator.warnings for validator in validators]))
        + list(meta_warnings),
        "info": list(set.union(*[validator.notices for validator in validators])),
    }

