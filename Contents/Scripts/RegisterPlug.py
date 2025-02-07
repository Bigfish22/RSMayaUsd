import mayaUsd
import pxr
import os
import sys
import maya.cmds as cmds


print("Registering RSMayaUSD")

current_path = cmds.pluginInfo("RegisterPlug", query=True, path=True)
pluginPath = os.path.dirname(current_path)

path = os.path.join(pluginPath, 'plugInfo.json')
sys.path.insert(0, path)

primWriterPath = os.path.join(pluginPath, "primWriter", 'plugInfo.json')
sys.path.insert(0, os.path.join(pluginPath, "primWriter"))

import RSMaterialWriterContext
import RSExportChaser
pxr.Plug.Registry().RegisterPlugins(path)
pxr.Plug.Registry().RegisterPlugins(primWriterPath)