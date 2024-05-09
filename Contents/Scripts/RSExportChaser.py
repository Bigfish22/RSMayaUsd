# Copyright 2024 Benjamin Mikhaiel

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mayaUsd
import traceback
import maya.api.OpenMaya as om2
from pxr import Sdf, Gf

mayaTypeToSdf = {'kFloat' : Sdf.ValueTypeNames.Float,
                'kDouble' : Sdf.ValueTypeNames.Float,
                'kInt' : Sdf.ValueTypeNames.Int,
                'k3Float' : Sdf.ValueTypeNames.Color3f,
                'Kstring' : Sdf.ValueTypeNames.String,
                'k3Float' : Sdf.ValueTypeNames.Float3,
                'kBool' : Sdf.ValueTypeNames.Bool}

#Displacement
rsTessDispAttrs = {"rsAutoBumpMap": "primvars:redshift:object:RS_objprop_displace_autob",
                    "rsEnableDisplacement": "primvars:redshift:object:RS_objprop_displace_enabl",
                    "rsMaxDisplacement": "primvars:redshift:object:RS_objprop_displace_max",
                    "rsDisplacementScale": "primvars:redshift:object:RS_objprop_displace_scale",
                    #Tessalation
                    "rsEnableSubdivision": "primvars:redshift:object:RS_objprop_rstess_enable",
                    "rsLimitOutOfFrustumTessellation": "primvars:redshift:object:RS_objprop_rstess_looft",
                    "rsMaxOutOfFrustumTessellationSubdivs": "primvars:redshift:object:RS_objprop_rstess_looftSubd",
                    "rsMaxTessellationSubdivs": "primvars:redshift:object:RS_objprop_rstess_maxsubd",
                    "rsMinTessellationLength": "primvars:redshift:object:RS_objprop_rstess_melenght",
                    "rsOutOfFrustumTessellationFactor": "primvars:redshift:object:RS_objprop_rstess_ooftf",
                    "rsSubdivisionRule": "primvars:redshift:object:RS_objprop_rstess_rule",
                    #"rsDoSmoothUVBoundaries": "primvars:redshift:object:RS_objprop_rstess_smoothBound",
                    "rsDoSmoothSubdivision": "primvars:redshift:object:RS_objprop_rstess_smoothsub",
                    "rsScreenSpaceAdaptive": "primvars:redshift:object:RS_objprop_rstess_ssadaptive"}

class RSExportChaser(mayaUsd.lib.ExportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        self.dagMap = factoryContext.GetDagToUsdMap()
        self.stage = factoryContext.GetStage()
        
    def ExportDefault(self):
        return True
    
    def ExportFrame(self, frame):
        return True
    
    def PostExport(self):
        try:
            for dagPair in self.dagMap:
                node = dagPair.key().node()
                
                if node.apiType() == 296:
                    prim = self.stage.GetPrimAtPath(dagPair.data())
                    mayaNode = om2.MFnDependencyNode(node)
                    for mayaAttr in rsTessDispAttrs:
                        plug = mayaNode.findPlug(mayaAttr, False)
                        mayaType = self.getMayaType(plug)
                        value = None
                        if mayaType == 'kFloat':
                            value = plug.asFloat()
                        elif mayaType == 'kInt':
                            value = plug.asInt()
                        elif mayaType == 'kBool':
                            value = plug.asBool()
                        elif mayaType == 'kDouble':
                            value = plug.asDouble()
                            
                        if value != None:
                            prim.CreateAttribute(rsTessDispAttrs[mayaAttr], mayaTypeToSdf[mayaType]).Set(value)
                            
                
        except Exception as e:
            print('Chaser Export - Error: %s' % str(e))
            print(traceback.format_exc())
        return True
        
    def getMayaType(self, plug):
        typeMap = {om2.MFnNumericData.kFloat:   'kFloat',
                    om2.MFnNumericData.k3Float: 'k3Float',
                    om2.MFnNumericData.kBoolean: 'kBool',
                    om2.MFnNumericData.kDouble: 'kDouble',
                    om2.MFnData.kString:        'Kstring',
                    om2.MFnNumericData.kInt:   'kInt'}
        
        attrObj = plug.attribute()
        if attrObj.hasFn(om2.MFn.kNumericAttribute):
            fnAttr = om2.MFnNumericAttribute(attrObj)
            mayaType = fnAttr.numericType()
            if mayaType in typeMap:
                return typeMap[mayaType]
        else:
            return None
        
        
mayaUsd.lib.ExportChaser.Register(RSExportChaser, "RSExportChaserStr")