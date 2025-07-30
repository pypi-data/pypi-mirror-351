"""
Row of action buttons at the top of the submitter.

Currently, Connect, Validate, Submit
"""
import os
import nuke
import cionuke
from cionuke import submit, connect
 

# In development, you can use fixtures for packages, projects, instance types.
# It saves time. Fixtures
FIXTURES_DIR = os.path.expanduser(os.path.join("~", "conductor_fixtures"))
 
CONNECT_TOOLTIP = """
Connects to your acccount on Conductor. You may be asked to log in. 
Once connected, you'll see the software, project, and machine type dropdown menus are populated.
"""
VALIDATE_TOOLTIP = """
Runs several validations to check that your scene is in a fit state to submit. 
Results are presented in a modal panel.
"""
SUBMIT_TOOLTIP = """
Submits the job to Conductor's render service. 
You'll see the same validation panel first, and if there are critical errors the submission will be blocked.
"""

def build(submitter):
    """Build action knobs."""

    knob = nuke.PyScript_Knob("cio_connect", "Connect")
    knob.setTooltip(CONNECT_TOOLTIP)
    submitter.addKnob(knob)

    knob = nuke.PyScript_Knob("cio_validate", "Validate")
    knob.setTooltip(VALIDATE_TOOLTIP)
    submitter.addKnob(knob)

    knob = nuke.PyScript_Knob("cio_submit", "Submit")
    knob.setTooltip(SUBMIT_TOOLTIP)
    submitter.addKnob(knob)

    knob = nuke.Text_Knob("cio_cionukeversion", "     cionuke")
    knob.setValue("v{}".format(cionuke.__version__))
    knob.clearFlag(nuke.STARTLINE)
    submitter.addKnob(knob)


def knobChanged(node, knob):
    """
    Respond to button pushes.

    Submit has a validate step before submission. 
    submitting=False causes the operation to stop after validation. 
    """
    knob_name = knob.name()
    if knob_name == "cio_connect":
        connect.connect(node)
    elif knob_name == "cio_validate":
        submit.submit(node, submitting=False)
    elif knob_name == "cio_submit":
        submit.submit(node, submitting=True)


def affector_knobs():
    """
    Knobs in this component that affect the payload when changed.

    If a write node is added, or if the connect button is pressed, the payload needs to be updated.
    """

    return ["inputChange", "cio_connect"]
 