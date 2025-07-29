import os

import pytest
import yaml
from xprocess import ProcessStarter


@pytest.fixture
def synapse(xprocess, tmp_path):
    path = os.path.dirname(__file__)
    new_config_filename = os.path.join(tmp_path, "homeserver.yaml")

    files_to_replace = [
        "homeserver.yaml",
        "matrix.aleksis.example.org.log.config",
    ]
    for filename in files_to_replace:
        new_filename = os.path.join(tmp_path, filename)

        with open(os.path.join(path, "synapse", filename), "r") as read_file:
            content = read_file.read()

        content = content.replace("%path%", path)
        content = content.replace("%tmp_path%", str(tmp_path))

        with open(new_filename, "w") as write_file:
            write_file.write(content)

    with open(new_config_filename, "r") as f:
        config = yaml.safe_load(f)

    config["server_url"] = "http://127.0.0.1:8008"

    class SynapseStarter(ProcessStarter):
        # startup pattern
        pattern = "SynapseSite starting on 8008"

        # command to start process
        args = [
            "python",
            "-m",
            "synapse.app.homeserver",
            "--enable-registration",
            "-c",
            new_config_filename,
        ]

        max_read_lines = 400
        timeout = 10

    xprocess.ensure("synapse", SynapseStarter)

    yield config

    xprocess.getinfo("synapse").terminate()
