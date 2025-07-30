import nuke
import json
from ciocore import data as coredata
from cionuke import const as k

TOOLTIPS = {
    "cio_insttype": "Choose a machine spec to run the job. To avoid unwanted costs, dont choose a GPU enabled machine if your script diesn't make use of a graphics card.",
    "cio_preemptible": 'Preemptible instances are lower cost, but may be shut down for long running tasks in favour of other cloud users. This rarely happens with Nuke.',
    }

def build(submitter):
    """Build knobs to specify instance type."""
    knob = nuke.CascadingEnumeration_Knob(
        "cio_insttype",
        "Instance type", [k.NOT_CONNECTED])

    knob.setTooltip(TOOLTIPS["cio_insttype"])
    knob.setFlag(nuke.STARTLINE)

    submitter.addKnob(knob)

    knob = nuke.Boolean_Knob("cio_preemptible", "Preemptible")
    knob.setTooltip(TOOLTIPS["cio_preemptible"])
    submitter.addKnob(knob)
    knob.setValue(1)

def rebuild_menu(submitter, instance_types):
    """
    Repopulate the dropdown menu.

    Args:
        submitter (the submitter node)
        instance_types (list(dict)): new instance types
    """
    model = coredata.data()['instance_types'].get_model()
    items = []

    for instance_category in model:
        category_label = instance_category['label']
        for it in instance_category['content']:
                
                if  instance_types.find(it['value'])['operating_system'].lower() != 'linux':
                    print ("Omitting {}".format(instance_types.find(it['value'])))
                    continue

                desc = it["label"]
                gpu_label = "GPU" if "gpu" in desc.lower() else "CPU"

                if len(model) >= 2:
                    items.append("{}/{}/{}".format(gpu_label,category_label,desc))
                else:
                    items.append("{}/{}".format(gpu_label,desc))

    submitter.knob("cio_insttype").setValues(items or [k.NOT_CONNECTED])

    if coredata.data()['instance_types'].provider == "cw":
        submitter.knob("cio_preemptible").setVisible(False)
        submitter.knob("cio_preemptible").setValue(False)

    else:
        submitter.knob("cio_preemptible").setVisible(True)

def resolve(submitter, **kwargs):
    instance_type = k.INVALID
    if coredata.valid():
        desc = submitter.knob("cio_insttype").value().split("/")[-1]
        instance_type = next((it["name"] for it in coredata.data()["instance_types"].instance_types.values() if it["description"] == desc), k.INVALID)

    return {
        "instance_type":instance_type,
        "preemptible": bool(submitter.knob("cio_preemptible").getValue()) 
    }

def affector_knobs():
    return [
        "cio_insttype",
        "cio_preemptible"
    ]
