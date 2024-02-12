#!/usr/bin/env python
import yaml
from os import environ, system, path
from shutil import copyfile

def loadConfig(filename):
    with open(filename, "r+") as filecontent:
        data = yaml.safe_load(filecontent)
    return data

def writeConfig(filename,configdata):
    with open(filename, 'w') as f:
       yaml.dump(configdata, f)

def setConfig(setting, value, configdata, section=None):
    if section is not None:
        if "/" in section:
            parent, subsection = section.split("/", 1)
            if parent not in configdata:
                configdata[parent] = {}
            return setConfig(setting, value, configdata[parent], section=subsection)
        if section not in configdata:
            configdata[section] = {}
        configdata[section][setting] = value
    else:
        configdata[setting] = value

def strToBool(string):
    if string in ["true", "True", "yes", "y", "1"]:
        return True
    else:
        return False

strToInt = lambda x: int(x)
strToFloat = lambda x: float(x)

configfile = "config.yaml"

if not path.exists(configfile):
    copyfile("config_default.yaml", configfile)

configdata = loadConfig(configfile)

env_vars = {
    "HAL_QUERY": {
        "hierarchy": "corpus",
        "key": "query"
    },
    "DEFAULT_NB_RESULTS": {
        "hierarchy": "app",
        "key": "show",
        "convert": strToInt
    },
    "RETRIEVE_TOP": {
        "hierarchy": "app/retrieve",
        "key": "top_k",
        "convert": strToInt
    },
    "RETRIEVE_THRESHOLD": {
        "hierarchy": "app/retrieve",
        "key": "score_threshold",
        "convert": strToFloat
    },
    "RANK_METRIC": {
        "hierarchy": "app/retrieve",
        "key": "rank_metric",
        "valid_values": ["median", "log-mean"]
    }
}

for var, specs in env_vars.items():
    if var in environ:
        val = environ[var]
        if specs.get("convert"):
            val = specs["convert"](val)
        if specs.get("valid_values") and val not in specs["valid_values"]:
            sys.exit("Environment variable %s is set to unacceptable value, allowed options are: %s" % (var, ", ".join(specs.valid_values)))
        setConfig(specs["key"], val, configdata, specs.get("hierarchy"))

writeConfig(configfile, configdata)
