import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import sys

def parse_from(line):
    """
    Parse the from directive.
    """
    # Clean up cruft after image name (as, digest, etc)
    base_image_tag = re.split(" (AS|as) ", line)[0]
    base_image_tag = base_image_tag.split("@")[0]
    return base_image_tag.split()[0]


def parse_run(line):
    """
    Parse a run directive for software.
    """
    # Basic package manager inference (same as before)
    if "apt-get install" in args:
        packages_match = re.search(r"apt-get install\s+(?:-y\s+)?(.*?)", args)
        if packages_match:
            packages_str = packages_match.group(1).strip()
            packages = packages_str.split()
            for pkg in packages:
                pkg = (
                    pkg.replace("--no-install-recommends", "").replace("-y", "").strip()
                )
                if pkg:
                    yield pkg

    elif "yum install" in args or "dnf install" in args:
        packages_match = re.search(r"(?:yum|dnf) install\s+(?:-y\s+)?(.*?)", args)
        if packages_match:
            packages_str = packages_match.group(1).strip()
            packages = packages_str.split()
            for pkg in packages:
                pkg = pkg.replace("-y", "").strip()
                if pkg:
                    yield pkg

    elif "apk add" in args:
        packages_match = re.search(r"apk add\s+(?:--no-cache\s+)?(.*?)", args)
        if packages_match:
            packages_str = packages_match.group(1).strip()
            packages = packages_str.split()
            for pkg in packages:
                pkg = pkg.replace("--no-cache", "").strip()
                if pkg:
                    yield pkg

    elif "pip install" in args or "pip3 install" in args:
        packages_match = re.search(r"(?:pip|pip3) install\s+(?:-r\s+)?(.*?)", args)
        if packages_match:
            packages_str = packages_match.group(1).strip()
            packages = packages_str.split()
            for pkg in packages:
                pkg = pkg.replace("--no-cache-dir", "").replace("-U", "").strip()
                if pkg:
                    yield f"python-package:{pkg}"

    elif "npm install" in args:
        packages_match = re.search(r"npm install\s+(?:--production\s+)?(.*?)", args)
        if packages_match:
            packages_str = packages_match.group(1).strip()
            packages = packages_str.split()
            for pkg in packages:
                pkg = pkg.replace("--production", "").replace("--save-dev", "").strip()
                if pkg:
                    yield f"node-package:{pkg}"

    if "nvidia" in args or "cuda" in args or "cudnn" in args:
        yield "nvidia-driver"
        yield "nvidia"
        yield "cuda-toolkit"
        yield "cudnn"

def parse_env(line):
    """
    Parse the environment and yield any software dependencies.
    """
    env_vars = line.split()
    for var in env_vars:
        if "=" in var:
            key, value = var.split("=", 1)
            key = key.strip()
            value = value.strip()
            if "PATH" in key or "LIBRARY_PATH" in key or "LD_LIBRARY_PATH" in key:
                if "python" in value:
                    yield "python"
                if "node" in value or "npm" in value:
                    yield "nodejs"
                if "java" in value:
                    yield "java"
            if "CUDA_HOME" in key or "CUDA_PATH" in key:
                    yield "cuda-toolkit"
                    yield "nvidia-driver"


def parse_dockerfile(content, model_name="google/gemma-3-27b-it"):
    """
    Analyzes a Dockerfile using a Gemma model from Hugging Face and extracts software dependencies,
    formatting the output as JSON.

    Args:
        dockerfile_path (str): The path to the Dockerfile.
        model_name (str): The name of the Gemma model on Hugging Face.

    Returns:
        str: A JSON string representing the software dependencies.
    """
    import IPython
    IPython.embed()

    prompt = f"""
    You are a Dockerfile analyzer.  Your task is to identify the software dependencies
    listed in the following Dockerfile.  Output a JSON object with the following keys:
    "base_image" (string, or null if not present) and "installed_software" (a list of strings).
    Be as comprehensive as possible. I only want JSON as the output, without any additional
    formatting or comment.

    Dockerfile:
    ```
    {content}
    ```
    """
    model = genai.GenerativeModel(
        model_name=args.model,
        generation_config=generation_config,
        safety_settings=safety_settings,
    )

    try:
        # It's good practice to handle potential API errors
        response = model.generate_content(prompt)
    except Exception as e:
        print(Fore.LIGHTRED_EX + str(e) + Style.RESET_ALL)
        return None, None

    # When it was too complex (and couldn't generate json) this came back empty
    if not response.parts:
        alert = f"👉 Response for {os.path.basename(filename)} has no parse"
        print(Fore.LIGHTRED_EX + alert + Style.RESET_ALL)
        if hasattr(response, "prompt_feedback") and response.prompt_feedback:
            print(f"  Prompt Feedback: {response.prompt_feedback}")
        return None, None

    # We got a response?
    response_text = response.text

    if not response_text:
        return None, None
    try:
        metadata, script = response_text.split("=====================")
    except:
        print(f"Issue splitting by delimiter: {response_text}")
        return {}, response_text


    try:
        json_output = json.loads(response_text)
        return json.dumps(json_output, indent=4)
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}\nResponse from Gemma: {response_text}"


def _parse_dockerfile(content):
    """
    Parses a Dockerfile content and extracts potential requirements.
    We want to use a static approach since it is simple and can get
    high level requirements like software, devices, etc.

    Args:
        dockerfile_content (str): The content of the Dockerfile as a single string.

    Returns:
        dict: A dictionary containing extracted requirements:
              {
                  'base_image': str,
                  'software': set,
                  'kernel_modules': set,
                  'device_drivers': set
              }
    """
    requires = {
        "base_image": None,
        "software": set(),
        "kernel_modules": set(),
        "device_drivers": set(),
    }
    lines = content.strip().split("\n")
    directive_regex = re.compile(r"^([A-Z]+)\s+(.*)\s")

    # Go through lines and parse directives, or continued line
    current_directive = None
    current_args = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.endswith("\\"):
            current_args.append(line[:-1].strip())
            continue
        elif current_directive:
            current_args.append(line)
            full_line = " ".join(current_args)
            current_directive = None
            current_args = []
        else:
            full_line = line

        match = directive_regex.match(full_line)
        if match:
            instruction = match.group(1)
            args = match.group(2).strip()

            # Did we find a base image?
            # We need to consider the base image because additional requirements could be
            # here. E.g., nvidia/cuda and similar.
            if instruction == "FROM":
                requires["base_image"] = parse_from(args)

            elif instruction == "RUN":
                for pkg in parse_run(args):
                    requires["software"].add(pkg)

            # How do we account for this? We could extract the layer, but
            # that might be overkill.
            elif instruction == "COPY" or instruction == "ADD":
                if "requirements.txt" in args and "pip" in full_line:
                    requirements["software"].add(
                        "python-packages-from-requirements.txt"
                    )

            elif instruction == "ENV":
                for software in parse_env(args):
                    requires["software"].add(software)

    requires["software"] = list(requires["software"])
    requires["kernel_modules"] = list(requires["kernel_modules"])
    requires["device_drivers"] = list(requires["device_drivers"])
    return requirements


def get_base_image_config(image_name):
    """
    Fetches and parses the image configuration from a registry using skopeo.

    Args:
        image_name (str): The full image name and tag (e.g., 'ubuntu:20.04', 'my-registry/my-image:v1').

    Returns:
        dict: The parsed image configuration dictionary, or None if fetching fails.
    """
    try:
        # Use skopeo inspect to get the image configuration
        result = subprocess.run(
            ["skopeo", "inspect", "--format=json", image_name],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ.copy(),  # Pass environment variables for potential auth
        )
        config_data = json.loads(result.stdout)
        return config_data
    except subprocess.CalledProcessError as e:
        print(f"Error fetching image config for '{image_name}': {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: 'skopeo' command not found. Please install skopeo.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON output from skopeo for '{image_name}': {e}")
        print(f"Output: {result.stdout}")
        return None


def infer_requirements_from_image_config(image_config):
    """
    Infers requirements from the parsed image configuration dictionary.

    Args:
        image_config (dict): The parsed image configuration dictionary.

    Returns:
        dict: A dictionary containing inferred requirements:
              {
                  'software': set,
                  'kernel_modules': set,
                  'device_drivers': set
              }
    """
    inferred_requirements = {
        "software": set(),
        "kernel_modules": set(),
        "device_drivers": set(),
    }

    if not image_config or "Config" not in image_config:
        return inferred_requirements

    config = image_config["Config"]

    # Infer software from environment variables
    if "Env" in config:
        for env_var in config["Env"]:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                key = key.strip()
                value = value.strip()

                if "PATH" in key or "LIBRARY_PATH" in key or "LD_LIBRARY_PATH" in key:
                    if "python" in value or "/opt/python" in value:
                        inferred_requirements["software"].add("python-runtime")
                    if "node" in value or "npm" in value:
                        inferred_requirements["software"].add("nodejs")
                    if "java" in value:
                        inferred_requirements["software"].add("java-runtime")
                if "CUDA_HOME" in key or "CUDA_PATH" in key:
                    inferred_requirements["software"].add("cuda-toolkit")
                    inferred_requirements["device_drivers"].add("nvidia-driver")

    # Infer software from entrypoint/cmd (very basic)
    if "Entrypoint" in config and config["Entrypoint"]:
        entrypoint_str = " ".join(config["Entrypoint"])
        if "python" in entrypoint_str:
            inferred_requirements["software"].add("python-runtime")
        if "node" in entrypoint_str:
            inferred_requirements["software"].add("nodejs")
        if "java" in entrypoint_str:
            inferred_requirements["software"].add("java-runtime")

    if "Cmd" in config and config["Cmd"]:
        cmd_str = " ".join(config["Cmd"])
        if "python" in cmd_str:
            inferred_requirements["software"].add("python-runtime")
        if "node" in cmd_str:
            inferred_requirements["software"].add("nodejs")
        if "java" in cmd_str:
            inferred_requirements["software"].add("java-runtime")

    # Infer device drivers/modules (e.g., NVIDIA)
    # This is highly heuristic and might require looking for specific labels or env vars in the image config itself
    if "Labels" in config:
        for key, value in config["Labels"].items():
            if (
                "nvidia" in key.lower()
                or "nvidia" in value.lower()
                or "cuda" in value.lower()
            ):
                # Look for labels explicitly mentioning NVIDIA components
                if (
                    "nvidia" in value.lower()
                    or "cuda" in value.lower()
                    or "cudnn" in value.lower()
                ):
                    inferred_requirements["device_drivers"].add("nvidia-driver")
                    inferred_requirements["kernel_modules"].add("nvidia")
                    inferred_requirements["software"].add("cuda-toolkit")
                    inferred_requirements["software"].add("cudnn")

    # Add generic kernel modules if needed (e.g., based on base image name)
    # This is very speculative
    # if 'ubuntu' in image_name.lower() or 'debian' in image_name.lower():
    #     inferred_requirements['kernel_modules'].add('linux-generic')

    inferred_requirements["software"] = set(inferred_requirements["software"])
    inferred_requirements["kernel_modules"] = set(
        inferred_requirements["kernel_modules"]
    )
    inferred_requirements["device_drivers"] = set(
        inferred_requirements["device_drivers"]
    )

    return inferred_requirements


def format_for_oci_compat(requirements):
    """
    Formats the extracted requirements into a dictionary suitable for OCI compatibility spec.

    Args:
        requirements (dict): The dictionary of requirements extracted.

    Returns:
        dict: A dictionary formatted according to a simplified OCI 'compatibilities' structure.
    """
    oci_compat = {"compatibilities": {}}

    # Add base image as a basic requirement
    if requirements["base_image"]:
        oci_compat["compatibilities"]["base_image"] = requirements["base_image"]

    # Add software requirements
    if requirements["software"]:
        oci_compat["compatibilities"]["software"] = sorted(
            list(requirements["software"])
        )

    # Add kernel module requirements
    if requirements["kernel_modules"]:
        oci_compat["compatibilities"]["kernel_modules"] = sorted(
            list(requirements["kernel_modules"])
        )

    # Add device driver requirements
    if requirements["device_drivers"]:
        oci_compat["compatibilities"]["device_drivers"] = sorted(
            list(requirements["device_drivers"])
        )

    return oci_compat


#if base_image_example:
#    print(f"Fetching config for base image: {base_image_example}")
#    image_config_example = get_base_image_config(base_image_example)
#    if image_config_example:
#        inferred_example = infer_requirements_from_image_config(image_config_example)
        # Combine Dockerfile inferences with image config inferences
#        requirements_example["software"].update(inferred_example["software"])
#        requirements_example["kernel_modules"].update(
#            inferred_example["kernel_modules"]
#        )
#        requirements_example["device_drivers"].update(
#            inferred_example["device_drivers"]
#        )


#oci_compat_example = format_for_oci_compat(requirements_example)

#print("--- Example Dockerfile Requirements (with base image config) ---")
#print(json.dumps(oci_compat_example, indent=2))

#print("\n" + "=" * 40 + "\n")

# Parse the GPU example Dockerfile
#requirements_gpu = parse_dockerfile(dockerfile_gpu_example)
#base_image_gpu = requirements_gpu.get("base_image")

#if base_image_gpu:
 #   print(f"Fetching config for base image: {base_image_gpu}")
 #   image_config_gpu = get_base_image_config(base_image_gpu)
 #   if image_config_gpu:
 #       inferred_gpu = infer_requirements_from_image_config(image_config_gpu)
        # Combine Dockerfile inferences with image config inferences
 #       requirements_gpu["software"].update(inferred_gpu["software"])
 #       requirements_gpu["kernel_modules"].update(inferred_gpu["kernel_modules"])
 #       requirements_gpu["device_drivers"].update(inferred_gpu["device_drivers"])

#oci_compat_gpu = format_for_oci_compat(requirements_gpu)

#print("--- GPU Dockerfile Requirements (with base image config) ---")
#print(json.dumps(oci_compat_gpu, indent=2))
