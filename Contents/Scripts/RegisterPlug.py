import mayaUsd
import pxr
import os
import sys
import maya.cmds as cmds


print("Registering RSMayaUSD")

current_path = cmds.pluginInfo("RegisterPlug", query=True, path=True)
pluginPath = os.path.dirname(current_path)

path = os.path.join(pluginPath, 'plugInfo.json')
sys.path.insert(0, "pluginPath")

import RSMaterialWriterContext
pxr.Plug.Registry().RegisterPlugins(path)