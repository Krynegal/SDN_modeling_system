#!/usr/bin/python
import os
import sys

conf_path = os.getcwd()
# sys.path.append("/onos")
sys.path.append("..")
sys.path.append(conf_path)
print(sys.path)

from core.read_scenario import get_yaml_content

res = get_yaml_content()
print(res)