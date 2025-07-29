import argparse
import os
import sys
import re
from humanfriendly import InvalidSize, parse_size

import yaml

from sentinelc_appfeed.utils.jinja import extract_jinja_variables
from sentinelc_appfeed.utils.safe_yaml import safe_jinja_yaml_render
from .utils.ArgparseCustomTypes import ArgparseCustomTypes

from .utils.exceptions import ValidationError
from .utils.logger import eprint

from .utils.utils import (
    get_all_localization_files,
    get_localized_objects_yaml,
    load_file_text,
    timestamp_to_json_string,
    safe_get,
    load_file_to_base64_str,
)

description_translatable_fields = ["description"]

mandatory_description_fields = ["display_name", "description", "category", "version"]

description_defaults = {"homepage": None, "documentation": None}

recipe_variables_translatable_fields = ["label", "description"]

recipe_variables_defaults = {
    "type": "text",
    "required": False,
    "regexp": None,
    "default": "",
    "auto": False,
    "secret": False,
    "immutable": False,
    "reveal_once": False,
}

networks_translatable_fields = ["description"]

recipe_networks_defaults = {
    "description": None,
    "type": "VLAN",
}

default_network = {
    "description": {
        "en": "Zone where the service will be installed",
        "fr": "Zone dans laquelle le service sera installé.",
    },
    "type": "VLAN",
}

accepted_variable_types = {
    "text",
    "checkbox",
    "number",
    "password",
    "email",
    "url",
    "textarea",
}

accepted_archs = ["amd64", "arm64"]

requirement_defaults = {"storage": None, "memory": None}

app_name_regexp = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

version_regexp = r"(^[a-z0-9\.\-]+?)(-r([0-9]+))?$"

logo_formats = dict(jpg="image/jpeg", webp="image/webp", png="image/png")

expose_port_regexp = r"^([\d]+)/(tcp|udp)$"


def is_valid_port_number(port_number):
    return type(port_number) is int and port_number > 0 and port_number <= 65535


def validate_version(version_string):
    return re.search(version_regexp, version_string)


def validate_app_name(app_name):
    # lowercase a-z, 0-9 and dashes allowed. Cannot start or end with a dash.
    return re.search(app_name_regexp, app_name)


def get_last_commit_timestamp(filename):
    timestamp = os.popen(f"git log --format=%ct {filename}").read()
    timestamp = timestamp[:-1]
    return timestamp_to_json_string(timestamp.split("\n")[-1])


def merge_translations(translations, recipe_dict, translatable_fields, namespace):
    if namespace not in recipe_dict:
        recipe_dict[namespace] = {}

    # shift down the default texts: {key: "default value"} becomes {key: {en: "default value"}}
    for var in recipe_dict[namespace]:
        for key in translatable_fields:
            if key in recipe_dict[namespace][var]:
                recipe_dict[namespace][var][key] = {"en": recipe_dict[namespace][var][key]}
            else:
                recipe_dict[namespace][var][key] = {}

    # merge in translations
    for locale_name, locale_values in translations.items():
        for var in recipe_dict[namespace]:
            if namespace not in locale_values:
                continue
            if var in locale_values[namespace]:
                for key in translatable_fields:
                    if key in locale_values[namespace][var]:
                        recipe_dict[namespace][var][key][locale_name] = locale_values[namespace][
                            var
                        ][key]


def validate_network(name, network):
    if type(network) is not dict:
        raise ValidationError(f"Network {name} should be a dict. Received {type(network)}.")

    # Adds defaults
    for option, default in recipe_networks_defaults.items():
        if option not in network:
            network[option] = default

    network_type = network.get("type")

    if network_type not in ("VLAN", "PORT"):
        raise ValidationError(
            f"Network {name}: Invalid type: {network_type}. Should be VLAN or PORT."
        )

    if "expose" in network:
        if network_type != "VLAN":
            raise ValidationError(
                f"Network {name}: Cannot use the 'expose' option: type must be VLAN."
            )

        expose = network.get("expose")
        if type(expose) is not list:
            raise ValidationError(f"Network {name}: 'expose' should be a list.")

        for exposed_port in expose:
            match = re.search(expose_port_regexp, exposed_port)
            if not match:
                raise ValidationError(
                    f"Network {name}: Invalid expose port format: {exposed_port}."
                )
            expose_port_number, expose_proto = exposed_port.split("/")
            expose_port_number = int(expose_port_number)
            if not is_valid_port_number(expose_port_number):
                raise ValidationError(
                    f"Network {name}: Invalid expose port number: {exposed_port}."
                )


def validate(manifest_path, app_name):
    bail_on_shallow_git_repos()
    path = f"{manifest_path}/{app_name}"

    # Validate App Name
    # app_name = path.split("/")[-1]
    eprint(f"- Validating {app_name}")

    if not validate_app_name(app_name):
        raise ValidationError(f"Invalid app name: {app_name}")

    # Get App Infos
    app_files = get_localized_objects_yaml(path, app_name, "description file")

    if app_files["en"] is None:
        raise ValidationError(
            f"The main description file could not be loaded : {path}/{app_name}.yml"
        )

    app = app_files["en"]
    del app_files["en"]

    app["name"] = app_name
    app["publish_date"] = get_last_commit_timestamp(f"{path}/{app_name}.yml")

    for field in description_translatable_fields:
        if field in app:
            app[field] = {"en": app[field]}

    for locale in app_files:
        current_app_file = app_files[locale]
        for field in description_translatable_fields:
            if field in current_app_file:
                app[field][locale] = current_app_file[field]

    # Get full descriptions (readmes)
    app["full_description"] = {}
    readmes = get_all_localization_files(path, "README.md")

    for locale in readmes:
        current_readme = load_file_text(f"{path}/{readmes[locale]}", "readme file")
        app["full_description"][locale] = current_readme

    # Check for mandatory fields
    has_mandatory_fields = True
    for field in mandatory_description_fields:
        if field not in app:
            if field in description_translatable_fields:
                if app[field]["en"] is None:
                    has_mandatory_fields = False
                    eprint(f"  - Mandatory field '{field}' from is missing")
            else:
                has_mandatory_fields = False
                eprint(f"  - Mandatory field '{field}' is missing")

    # Return object if valid
    if not has_mandatory_fields:
        raise ValidationError("Missing mandatory field(s)")

    # validate version
    if not validate_version(app["version"]):
        raise ValidationError(
            "Version name is invalid. It must be alphanumeric, and can include dashes and dots."
        )

    # Optional fields - will be filled with nulls
    for field in description_defaults:
        if field not in app:
            app[field] = description_defaults[field]

    # variables translations
    merge_translations(app_files, app, recipe_variables_translatable_fields, "vars")

    # networks translations
    merge_translations(app_files, app, networks_translatable_fields, "networks")

    # validate architectures
    if "architectures" not in app:
        raise ValidationError("Missing architectures")

    for arch in app["architectures"]:
        if arch not in accepted_archs:
            raise ValidationError(f"Invalid architecture: {arch}")

    if len(app["architectures"]) != len(set(app["architectures"])):
        raise ValidationError("Duplicate architecture defined.")

    # validate requirements
    if "requirements" not in app:
        app["requirements"] = {}

    # adds defaults
    for key in requirement_defaults:
        if key not in app["requirements"]:
            app["requirements"][key] = requirement_defaults[key]

    for key in app["requirements"]:
        cur_requirement = app["requirements"][key]
        if cur_requirement is not None:
            try:
                app["requirements"][key] = parse_size(cur_requirement, False)
            except InvalidSize:
                raise ValidationError(f"Requirement {key} in {app_name} is not parsable")

    # Validate variables
    if "vars" not in app:
        app["vars"] = []

    for key in app["vars"]:
        var = app["vars"][key]

        # Adds defaults
        for option, default in recipe_variables_defaults.items():
            if option not in var:
                var[option] = default

        # Copy the var name as the label if none provided.
        if not var["label"].get("en"):
            var["label"]["en"] = key

        # Block posibility of an automatic,mutable variable
        if var["auto"] and not var["immutable"]:
            raise ValidationError(f"{key} in App {app_name} can't be automatic and mutable")

        # Block posibility of an reveal_once other if the variable is not secret
        if var["reveal_once"] and not var["secret"]:
            raise ValidationError(
                f"{key} in App {app_name} doesn't need to be revealed_once if not secret"
            )

        if var["type"] not in accepted_variable_types:
            raise ValidationError(f"Var {key} in {app_name}: Invalid type: " + var["type"])

        if "regexp" in var and var["regexp"] is not None:
            try:
                re.compile(var["regexp"])
            except re.error:
                raise ValidationError(
                    f"{key} in App {app_name} contains an invalid regular expression"
                )

    # Adds kube
    kube_yml_filename = f"{path}/{app_name}.kube.yml"
    kube_string = load_file_text(
        kube_yml_filename,
        "kubernetes template file",
    )
    if not kube_string:
        raise ValidationError(f"{kube_yml_filename} is missing.")

    # Validate parameter parity
    template_vars = extract_jinja_variables(kube_string)
    defined_vars = set(app["vars"].keys())

    if template_vars != defined_vars:
        missing_vars = ", ".join(template_vars - defined_vars)
        extra_vars = ", ".join(defined_vars - template_vars)
        raise ValidationError(
            f"Vars used in template do not match the defined ones: missing: "
            f"{missing_vars} extra: {extra_vars}."
        )

    kube_document = validate_kube_yaml(kube_string, kube_yml_filename)

    # Validate networks
    host_networking = safe_get(kube_document, "spec", "hostNetwork")
    networks = app.get("networks")

    # if the kube spec asks for hostNetwork, it cannot also specify CNI networks in the version info
    # file
    if host_networking:
        app["network_mode"] = "HOST"
        if networks:
            raise ValidationError(
                "The kube spec file declares hostNetwork is enabled. This disables network "
                "isolation of the pod and cannot be mixed with 'networks' in the version "
                "info file. Either remove the hostNetwork: true in your spec file, or the "
                "list of networks: in the version info file."
            )

    else:
        app["network_mode"] = "CNI"

        # add a default network if networks: key is fully missing
        if not networks:
            networks = dict(default=default_network)
            app["networks"] = networks

        if type(networks) is not dict:
            raise ValidationError(
                f"The 'networks' key of the recipe version should be a dict, "
                f"received {type(networks)}"
            )

        for network_name, network in networks.items():
            validate_network(network_name, network)

    # cloudProxy
    if "cloud_proxy" in app:
        if app["network_mode"] != "CNI":
            raise ValidationError(
                "network mode must be set to CNI in order to enable the cloud_proxy feature."
            )

        cloud_proxy_network = "default"
        if "network" in app["cloud_proxy"]:
            cloud_proxy_network = app["cloud_proxy"]["network"]

        if cloud_proxy_network not in app["networks"]:
            raise ValidationError(f"cloud_proxy network {cloud_proxy_network} does not exist.")

        if app["networks"][cloud_proxy_network]["type"] != "VLAN":
            raise ValidationError(
                f"cloud_proxy network {cloud_proxy_network} must be a VLAN network."
            )

        cloud_proxy_port = safe_get(app, "cloud_proxy", "port")
        if not cloud_proxy_port:
            raise ValidationError("port parameter is required for cloud_proxy.")

        if not is_valid_port_number(cloud_proxy_port):
            raise ValidationError("Invalid cloud proxy port number.")

        protect_from_vlan = safe_get(app, "cloud_proxy", "protect_from_vlan")
        if protect_from_vlan is None:
            protect_from_vlan = True
        if type(protect_from_vlan) is not bool:
            raise ValidationError("cloud_proxy protect_from_vlan should be true or false.")

        app["cloud_proxy"] = dict(
            port=cloud_proxy_port, network=cloud_proxy_network, protect_from_vlan=protect_from_vlan
        )

    # add logo
    logo, mime_type = get_logo_base64(path)
    if logo:
        app["logo"] = dict(default=dict(mime_type=mime_type, data=logo))
    else:
        app["logo"] = None

    app["kube"] = kube_string

    return app


def get_logo_base64(path):
    for ext in logo_formats.keys():
        filename = f"{path}/logo.{ext}"
        if os.path.isfile(filename):
            return load_file_to_base64_str(filename), logo_formats[ext]
    return None, None


def validate_kube_yaml(kube_string, filepath):
    if not kube_string:
        raise ValidationError(f"No kube file found : {filepath}")

    validation_kube_string = safe_jinja_yaml_render(kube_string, allow_undefined_variables=True)

    if not kube_yaml_is_single_document(validation_kube_string):
        raise ValidationError(
            f"Kube yaml must contain a single document: {filepath}. Remove the --- footer."
        )

    kube_document = yaml.safe_load(validation_kube_string)

    error = (
        kube_yaml_has_basic_fields(kube_document)
        or kube_yaml_has_at_least_one_container(kube_document)
        or kube_yaml_has_no_status(kube_document)
        or kube_yaml_has_no_restart_policy(kube_document)
    )
    if error:
        raise ValidationError(f"{filepath}: {error}")

    return kube_document


def kube_yaml_is_single_document(kube_string):
    try:
        yaml.safe_load(kube_string)
        return True
    except yaml.composer.ComposerError:
        return False


def kube_yaml_has_basic_fields(kube_document):
    if kube_document.get("apiVersion") != "v1":
        return "apiVersion must be v1"
    if kube_document.get("kind") != "Pod":
        return "kind must be Pod"


def kube_yaml_has_at_least_one_container(kube_document):
    spec = kube_document.get("spec")
    if type(spec) is not dict:
        return "missing or invalid spec"

    containers = spec.get("containers")
    if type(containers) is not list:
        return "missing or invalid containers"

    if len(containers) == 0:
        return "should define at least one container"


def kube_yaml_has_no_status(kube_document):
    status = kube_document.get("status")
    if status or status != {}:
        return "should not define a status"


def kube_yaml_has_no_restart_policy(kube_document):
    restart_policy = safe_get(kube_document, "spec", "restartPolicy")
    if restart_policy and restart_policy != "Always":
        return "restartPolicy can only be set to Always."


def bail_on_shallow_git_repos():
    is_shallow = os.popen("git rev-parse --is-shallow-repository").read()[:-1]
    if is_shallow == "true":
        eprint(
            "You appear to be running in a shallow git clone. This script uses the "
            "git log command to get commit dates of your packages and will fail in a "
            "shallow clone."
        )
        eprint(
            "If you are using gitlab-ci, set the Git shallow clone settings to 0"
            + " in your project's CI:CD settings."
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="""
        Validates a specific app in the manifests.
                
        how to use
        ------------
        `applib-recipe newapp`
        Validates the `newapp` app located inside the ./manifests folder
        
        `applib-recipe -p newmanifest newapp`
        Validates the `newapp` app located inside the ./newmanifest folder
        """  # noqa: W293 E501
    )

    parser.add_argument(
        "-p",
        "--path",
        action="store",
        help='Specify the root of the manifest folder. Default: "manifests"',
        type=ArgparseCustomTypes.dir_path,
        default="manifests",
    )

    parser.add_argument(
        "app_name",
        action="store",
        help="Specify the name of the app to validate.",
    )

    args = parser.parse_args()

    validate(args.path, args.app_name)


if __name__ == "__main__":
    main()
