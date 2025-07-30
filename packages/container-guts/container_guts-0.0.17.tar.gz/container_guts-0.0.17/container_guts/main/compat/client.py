__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2025, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import shutil
import re
import json
import subprocess
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

from container_guts import utils
from container_guts.logger import logger
from container_guts.main.container.base import ContainerName
from container_guts.main.container.decorator import ensure_container
from .dockerfile import parse_dockerfile


class CompatGenerator:
    """
    Generate a Compatibility specification.
    """

    def __init__(self, tech="docker"):
        self.init_container_tech(tech)
        self.manifests = {}

    def generate(self, image):
        """
        Generate the compatibility specification.
        """
        # Case 1: We are give a Dockerfile
        if os.path.exists(image):
            content = utils.read_file(image)
            requires = parse_dockerfile(content)

        # Parse the example Dockerfile
        # requirements_example = parse_dockerfile(dockerfile_example)
        # base_image_example = requirements_example.get('base_image')

        import IPython

        IPython.embed()

    def init_container_tech(self, tech):
        """
        Add the container operator
        """
        if tech == "docker":
            from container_guts.main.container import DockerContainer
        else:
            logger.exit(f"Container technology {tech} is not supported.")
        self.container = DockerContainer()

    @ensure_container
    def save_path(self, image):
        """
        Derive a save path, if desired.
        """
        return image.path

    def get_container(self, image):
        """
        Courtesy function to get a container from a URI.
        """
        if isinstance(image, ContainerName):
            return image
        return ContainerName(image)

    def get_manifests(self, root):
        """
        Given the root of a container extracted meta directory, read all json
        configs and derive a final set of paths to explore.
        """
        manifest = {"paths": set()}
        for jsonfile in utils.recursive_find(root, "json$"):
            data = utils.read_json(jsonfile)
            if "manifest" in jsonfile:
                continue
            print("Found layer config %s" % jsonfile)

            # Fallback to config
            cfg = data.get("container_config") or data.get("config")
            if not cfg:
                continue

            # Get entrypoint, command, labels
            for attr in ["Entrypoint", "Cmd", "WorkingDir", "Labels"]:
                if cfg.get(attr) and attr.lower() not in manifest:
                    manifest[attr.lower()] = cfg[attr]

            # Populate paths
            for envar in cfg.get("Env") or []:
                [manifest["paths"].add(x) for x in self._parse_paths(envar)]
        return manifest

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[guts-compat-generator]"
