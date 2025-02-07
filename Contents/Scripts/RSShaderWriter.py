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
from pxr import UsdShade, Sdf, Gf, Vt
import maya.api.OpenMaya as om2
import traceback
from math import pi
import re

mayaTypeToSdf = {'kFloat' : Sdf.ValueTypeNames.Float,
                'kInt' : Sdf.ValueTypeNames.Int,
                'kColor' : Sdf.ValueTypeNames.Color3f,
                'Kstring' : Sdf.ValueTypeNames.String,
                'k2Float' : Sdf.ValueTypeNames.Float2,
                'k3Float' : Sdf.ValueTypeNames.Float3,
                'kEnum' : Sdf.ValueTypeNames.Int,
                'kBool' : Sdf.ValueTypeNames.Bool}


# mayaShaderToRS = {"RedshiftStandardMaterial": ['StandardMaterial', 'outColor'],
#                   "RedshiftJitter"          : ['Jitter', 'outColor'],
#                   "RedshiftDisplacement"    : ['Displacement', 'out'],
#                   "file"                    : ['TextureSampler', 'outColor']}

mayaShaderToRS = {"MultiOutputChannelTexmapToTexmap" : ["", 'out'],
                "RedshiftAmbientOcclusion" : ['AmbientOcclusion', 'out'],
                "RedshiftMathAbs" : ['RSMathAbs', 'out'],
                "RedshiftMathAdd" : ['RSMathAdd', 'out'],
                "RedshiftMathATan2" : ['RSMathArcTan2', 'out'],
                "RedshiftMathACos" : ['RSMathArcCos', 'out'],
                "RedshiftMathASin" : ['RSMathArcSin', 'out'],
                "RedshiftMathATan" : ['RSMathArcTan', 'out'],
                "RedshiftMathBias" : ['RSMathBias', 'out'],
                "RedshiftBrick" : ['Brick', 'outColor'],
                "RedshiftBumpBlender" : ['BumpBlender', 'outDisplacementVector'],
                "RedshiftBumpMap" : ['BumpMap', 'out'],
                "RedshiftCameraMap" : ['RSCameraMap', 'outColor'],
                "RedshiftMathRange" : ['RSMathRange', 'out'],
                "RedshiftMathAbsColor" : ['RSMathAbsColor', 'outColor'],
                "RedshiftMathBiasColor" : ['RSMathBiasColor', 'outColor'],
                "RedshiftColorRange" : ['RSColorRange', 'out'],
                "RedshiftColorConstant" : ['RSColorConstant', 'outColor'],
                "colorConstant" : ['RSColorConstant', 'outColor'], #Maya color Constant
                "floatConstant" : ['RSScalarConstant', 'out'], #Maya float Constant
                "RedshiftMathExpColor" : ['RSMathExpColor', 'outColor'],
                "RedshiftMathGainColor" : ['RSMathGainColor', 'outColor'],
                "RedshiftMathInvColor" : ['RSMathInvertColor', 'out'],
                "RedshiftColorMaker" : ['RSColorMaker', 'outColor'],
                "RedshiftColorMix" : ['RSColorMix', 'outColor'],
                "blendColors" : ['RSColorMix', 'outColor'], #Maya blend colors
                "RedshiftMathSaturateColor" : ['RSMathSaturateColor', 'outColor'],
                "RedshiftColorSplitter" : ['RSColorSplitter', ''],
                "RedshiftMathSubColor" : ['RSMathSubColor', 'outColor'],
                "RedshiftColor2HSV" : ['RSColor2HSV', 'outColor'],
                "RedshiftUserDataColor" : ['RSUserDataColor', 'out'],
                "RedshiftMathCos" : ['RSMathCos', 'out'],
                "RedshiftMathCrossVector" : ['RSCrossProduct', 'out'],
                "RedshiftCurvature" : ['RSCurvature', 'out'],
                "RedshiftDisplacement" : ['Displacement', 'out'],
                "RedshiftDisplacementBlender" : ['DisplacementBlender', 'out'],
                "RedshiftMathDiv" : ['RSMathDiv', 'out'],
                "RedshiftMathDotVector" : ['RSDotProduct', 'out'],
                "RedshiftEnvironment" : ['RSEnvironment', 'outColor'],
                "RedshiftMathExp" : ['RSMathExp', 'out'],
                "RedshiftFlakes" : ['RSFlakes', 'out'],
                "RedshiftMathFloor" : ['RSMathFloor', 'out'],
                "RedshiftMathFrac" : ['RSMathFrac', 'out'],
                "RedshiftFresnel" : ['RSFresnel', 'out'],
                "RedshiftMathGain" : ['RSMathGain', 'out'],
                "RedshiftHSV2Color" : ['RSHSVToColor', 'outColor'],
                "RedshiftHairPosition" : ['RSHairPosition', 'outVector'],
                "RedshiftHairRandomColor" : ['RSHairRandomColor', 'out'],
                "RedshiftIORToMetalTints" : ['RSIORToMetalTints', ''],
                "RedshiftUserDataInteger" : ['RSUserDataInteger', 'out'],
                "RedshiftMathInv" : ['RSMathInv', 'out'],
                "RedshiftJitter" : ['Jitter', 'outColor'],
                "RedshiftMathLn" : ['RSMathLn', 'out'],
                "RedshiftMathLog" : ['RSMathLog', 'out'],
                "RedshiftMatCap" : ['RSMatCap', 'out'],
                "RedshiftMathMax" : ['RSMathMax', 'out'],
                "RedshiftMaxonNoise" : ['MaxonNoise', 'outColor'],
                "RedshiftMathMin" : ['RSMathMin', 'out'],
                "RedshiftMathMix" : ['RSMathMix', 'out'],
                "RedshiftMathMod" : ['RSMathMod', 'out'],
                "RedshiftMathMul" : ['RSMathMul', 'out'],
                "RedshiftMathNeg" : ['RSMathNeg', 'out'],
                "RedshiftMathNormalizeVector" : ['RSMathNormalizeVector', 'out'],
                "RedshiftOSLMap" : ['rsOSL', ''],
                "RedshiftPavement" : ['RSPavement', ''],
                "RedshiftPhysicalSky" : ['RSPhysicalSky', 'outColor'],
                "RedshiftMathPow" : ['RSMathPow', 'out'],
                "RedshiftRaySwitch" : ['RaySwitch', 'outColor'],
                "RedshiftMathRcp" : ['RSMathRcp', 'out'],
                "RedshiftRoundCorners" : ['RoundCorners', 'out'],
                "RedshiftMathSaturate" : ['RSMathSaturate', 'out'],
                "RedshiftUserDataScalar" : ['RSUserDataScalar', 'out'],
                "RedshiftShaderSwitch" : ['RSShaderSwitch', 'outColor'],
                "RedshiftShave" : ['RSShave', 'out'],
                "RedshiftMathSign" : ['RSMathSign', 'out'],
                "RedshiftMathSin" : ['RSMathSin', 'out'],
                "RedshiftMathSqrt" : ['RSMathSqrt', 'out'],
                "RedshiftState" : ['State', 'out'],
                "RedshiftMathSub" : ['RSMathSub', 'out'],
                "RedshiftMathTan" : ['RSMathTan', 'out'],
                "RedshiftTexture" : ['TextureSampler', 'outColor'],
                "RedshiftTiles" : ['RSTiles', ''],
                "RedshiftTriPlanar" : ['TriPlanar', 'outColor'],
                "RedshiftUVProjection" : ['UVProjection', 'out'],
                "RedshiftMathAbsVector" : ['RSMathAbsVector', 'out'],
                "RedshiftMathAddVector" : ['RSMathAddVector', 'out'],
                "RedshiftMathBiasVector" : ['RSMathBiasVector', 'out'],
                "RedshiftMathRangeVector" : ['RSMathRangeVector', 'out'],
                "RedshiftMathDivVector" : ['RSMathDivVector', 'out'],
                "RedshiftMathExpVector" : ['RSMathExpVector', 'out'],
                "RedshiftMathFloorVector" : ['RSMathFloorVector', 'out'],
                "RedshiftMathFracVector" : ['RSMathFracVector', 'out'],
                "RedshiftMathGainVector" : ['RSMathGainVector', 'out'],
                "RedshiftMathInvVector" : ['RSMathInvVector', 'out'],
                "reverse"               : ['RSMathInvVector', 'out'], #maya reverse
                "RedshiftMathLengthVector" : ['RSMathLengthVector', 'out'],
                "RedshiftMathLnVector" : ['RSMathLnVector', 'out'],
                "RedshiftMathLogVector" : ['RSMathLogVector', 'out'],
                "RedshiftVectorMaker" : ['RSVectorMaker', 'out'],
                "RedshiftMathMaxVector" : ['RSMathMaxVector', 'out'],
                "RedshiftMathMinVector" : ['RSMathMinVector', 'out'],
                "RedshiftMathMixVector" : ['RSMathMixVector', 'out'],
                "RedshiftMathModVector" : ['RSMathModVector', 'out'],
                "RedshiftMathMulVector" : ['RSMathMulVector', 'out'],
                "RedshiftMathNegVector" : ['RSMathNegVector', 'out'],
                "RedshiftMathPowVector" : ['RSMathPowVector', 'out'],
                "RedshiftMathRcpVector" : ['RSMathRcpVector', 'out'],
                "RedshiftMathSaturateVector" : ['RSMathSaturateVector', 'out'],
                "RedshiftMathSignVector" : ['RSMathSignVector', 'out'],
                "RedshiftMathSqrtVector" : ['RSMathSqrtVector', 'out'],
                "RedshiftMathSubVector" : ['RSMathSubVector', 'out'],
                "RedshiftVectorToScalars" : ['RSVectorToScalars', 'out'],
                "RedshiftUserDataVector" : ['RSUserDataVector', 'out'],
                "RedshiftWireFrame" : ['WireFrame', 'out'],
                "RedshiftStandardMaterial" : ['StandardMaterial', 'outColor'],
                "RedshiftMaterialSwitch" : ["RSShaderSwitch", 'outClosure'],
                "RedshiftPrincipledHair" : ['Hair2', 'out'],
                "RedshiftSprite" : ['Sprite', 'outColor'],
                "RedshiftMaterialBlender" : ['MaterialBlender', 'out'],
                "RedshiftVolume" : ['Volume', 'outColor'],
                "RedshiftIncandescent" : ['Incandescent', 'outColor'],
                "RedshiftStoreColorToAOV" : ['StoreColorToAOV', 'outColor'],
                "RedshiftColorCorrection" : ['RSColorCorrection', 'outColor'],
                "RedshiftColorLayer" :      ['RSColorLayer', 'outColor'],
                "RedshiftMaterial" :        ['Material', 'outColor'],
                "remapValue" :              ['RSMathRange', 'out'],
                "RedshiftVertexColor " :      ['RSUserDataColor', 'out']}

propertyRemaps = {"RedshiftMaterialBlender" : {"outColor": "out"},
                  "RedshiftBumpBlender" : {"outColor" : "outDisplacementVector"},
                  "blendColors" : {"color1" : "input1", "color2" : "input2", "blender" : "mixAmount", "output" : "outColor"},
                  "reverse"  : {"output" : "out"},
                  "colorConstant" : {"inColor": "color"},
                  "floatConstant" : {"inFloat": "val", "outFloat" : "out"},
                  "file" : {"outAlpha" : "outColor"},
                  "remapValue" : {"inputValue" : "input", "inputMin" : "old_min", "inputMax" : "old_max", "outputMin" : "new_min", "outputMax" : "new_max", "outColor" : "out", "outValue" : "out"}
                  }

class RSShaderWriter(mayaUsd.lib.ShaderWriter):
    def Write(self, usdTime):
        try:
            isSurfaceNode = False
            surfConnections = {}

            mayaNode = om2.MFnDependencyNode(self.GetMayaObject())
            materialPrim = UsdShade.Material.Get(self.GetUsdStage(), (self.GetUsdPath()).GetParentPath())
            materialNodeName = str((self.GetUsdPath()).GetParentPath()).split("/")[-1]
            
            nodeShader = UsdShade.Shader.Define(self.GetUsdStage(), (self.GetUsdPath()))
            nodeShader.CreateIdAttr("redshift::" + mayaShaderToRS[mayaNode.typeName][0])

            for i in range(0, mayaNode.attributeCount()):
                attrName : str = om2.MFnAttribute(mayaNode.attribute(i)).name
                if attrName.endswith(('R','G','B','X','Y','Z')):
                    continue
                plug = mayaNode.findPlug(attrName, True)

                if plug.isConnected:
                    self.addNode(nodeShader, mayaNode, attrName, plug)
                    destinations = plug.destinations()
                    for destPlug in destinations:
                        destNode = om2.MFnDependencyNode(destPlug.node())
                        if destNode.typeName == "shadingEngine" and destNode.name() == materialNodeName:
                            isSurfaceNode = True
                            surfConnections[destPlug.partialName(useLongNames = True)] = attrName
                else:
                    self.addProperty(nodeShader, mayaNode, attrName, plug)

            
            if isSurfaceNode:
                surfaceShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath("redshift_usd_material1"))
                surfaceShader.CreateIdAttr("redshift_usd_material")
                
                
                materialPrim.CreateSurfaceOutput('Redshift').ConnectToSource(surfaceShader.ConnectableAPI(), "shader")

                for surfaceInput in surfConnections:
                    surfaceShader.CreateInput(surfaceInput.replace("Shader", "").capitalize(), Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), self.usdAttrName(mayaNode.typeName, surfConnections[surfaceInput]))
            

                
            return True
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def addProperty(self, prim, mayaNode, attrName, plug):
        if plug.isChild:
            return
        if plug.isDefaultValue():
            return
        type = self.getMayaType(plug)
        if type is None:
            return

        
        sdfType = Sdf.ValueTypeNames.Token

        if type == 'k3Float':
            value = (plug.child(0).asFloat(), plug.child(1).asFloat(), plug.child(2).asFloat())
            if plug.child(0).name().endswith("R"):
                sdfType = mayaTypeToSdf['kColor']
            else:
                sdfType = mayaTypeToSdf[type]
        elif type == 'kFloat':
            value = plug.asFloat()
            sdfType = mayaTypeToSdf[type]
        elif type == 'k2Float':
            value = (plug.child(0).asFloat(), plug.child(1).asFloat())
            sdfType = mayaTypeToSdf[type]
        elif type == 'kInt' or type == 'kEnum':
            value = plug.asInt()
            sdfType = mayaTypeToSdf[type]
        elif type == "kBool":
            value = plug.asBool()
            sdfType = mayaTypeToSdf[type]
        elif type == "Kstring":
            if attrName == "tex0":
                sdfType = Sdf.ValueTypeNames.Asset
            else:
                sdfType = mayaTypeToSdf[type]
            value = plug.asString()
        else:
            return

        attrName = self.usdAttrName(mayaNode.typeName, attrName)
        prim.CreateInput(attrName, sdfType).Set(value)

    def addNode(self, prim, mayaNode, attrName, plug):
        try:
            nodeToAdd = om2.MFnDependencyNode(plug.source().node())
            
            if nodeToAdd.name() == 'nullptr':
                return
            
            outputAttrName = plug.source().partialName(useLongNames = True)
            outputAttrName = self.usdAttrName(nodeToAdd.typeName, outputAttrName)

            nodePrim = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(nodeToAdd.name()))

            attrName = self.usdAttrName(mayaNode.typeName, attrName)
            sdfType = mayaTypeToSdf[self.getMayaType(plug)]
            prim.CreateInput(attrName, sdfType).ConnectToSource(nodePrim.ConnectableAPI(), outputAttrName)
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
        
    def clearSubChannel(self, attrName):
        if attrName.endswith(('R','G','B')):
            return attrName[:-1]
        return attrName

    def usdAttrName(self, className, attrName):
        attrName = self.clearSubChannel(attrName)
        if className in propertyRemaps:
            for property in propertyRemaps[className]:
                if property == attrName:
                    attrName = propertyRemaps[className][property]
        return attrName


    def getMayaType(self, plug):
        """
        typeMap = {#om2.MFnNumericData.kByte: 'kByte',
                   #om2.MFnNumericData.kBoolean: 'kBool',
                   #om2.MFnNumericData.kInt:   'kInt',
                    #om2.MFnNumericData.kChar:  'kChar',
                    #om2.MFnNumericData.kShort: 'kShort',
                    #om2.MFnNumericData.kLong:  'kLong',
                    #om2.MFnNumericData.kFloat: 'kFloat',
                    #om2.MFnNumericData.kDouble:'kDouble',
                    om2.MFnNumericData.k3Float: 'k3Float',
                    #om2.MFnNumericData.k3Double: 'k3Double',
                    om2.MFnData.kString:       'Kstring'}
        """
        
        typeMap = {om2.MFnNumericData.kFloat:   'kFloat',
                   om2.MFnNumericData.k2Float:  'k2Float',
                    om2.MFnNumericData.k3Float: 'k3Float',
                    om2.MFnNumericData.kBoolean: 'kBool',
                    om2.MFnData.kString:        'Kstring',
                    om2.MFnNumericData.kInt:   'kInt'}
        
        attrObj = plug.attribute()
        if attrObj.hasFn(om2.MFn.kNumericAttribute):
            fnAttr = om2.MFnNumericAttribute(attrObj)
            mayaType = fnAttr.numericType()
            if mayaType in typeMap:
                return typeMap[mayaType]
        elif attrObj.hasFn(om2.MFn.kTypedAttribute):
            fnAttr = om2.MFnTypedAttribute(attrObj)
            mayaType = fnAttr.attrType()
            if mayaType in typeMap:
                return typeMap[mayaType]
        elif attrObj.hasFn(om2.MFn.kEnumAttribute):
            return 'kEnum'
        
        return None
            
    @classmethod
    def CanExport(cls, exportArgs):
        if "redshift_usd_material" in exportArgs.convertMaterialsTo:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Supported
        else:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Unsupported
            
class RSTextureWriter(mayaUsd.lib.ShaderWriter):
    def Write(self, usdTime):
        try:
            mayaNode = om2.MFnDependencyNode(self.GetMayaObject()) 
            nodeName = mayaNode.name()

            textureShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(nodeName))
            textureShader.CreateIdAttr('redshift::TextureSampler')

            
            texturePath = mayaNode.findPlug('fileTextureName', True).asString()
            if mayaNode.findPlug('uvTilingMode', False).asInt() == 3:
                texturePath = re.sub("1[0-9]{3}", "<UDIM>", texturePath)
            textureShader.CreateInput("tex0", Sdf.ValueTypeNames.Asset).Set(texturePath)
            colorspace = mayaNode.findPlug('colorSpace', True).asString()
            textureShader.CreateInput("tex0_colorSpace", Sdf.ValueTypeNames.String).Set(colorspace)


            mayaTexCord = om2.MFnDependencyNode(mayaNode.findPlug("uvCoord", True).source().node())
            tilingU = mayaTexCord.findPlug("repeatU", True).asFloat()
            tilingV = mayaTexCord.findPlug("repeatV", True).asFloat()
            rotate  = mayaTexCord.findPlug("rotateUV", True).asFloat() * (180/pi)
            offsetU = mayaTexCord.findPlug("offsetU", True).asFloat()
            offsetV = mayaTexCord.findPlug("offsetV", True).asFloat()
            textureShader.CreateInput("scale", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(tilingU, tilingV))
            textureShader.CreateInput("rotate", Sdf.ValueTypeNames.Float).Set(rotate)
            textureShader.CreateInput("offset", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(offsetU, offsetV))

            return True
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
        
    @classmethod
    def CanExport(cls, exportArgs):
        if "redshift_usd_material" in exportArgs.convertMaterialsTo:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Supported
        else:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Unsupported

class RSRampWriter(mayaUsd.lib.ShaderWriter):
    def Write(self, usdTime):
        try:
            mayaNode = om2.MFnDependencyNode(self.GetMayaObject()) 
            nodeName = mayaNode.name()

            textureShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(nodeName))
            textureShader.CreateIdAttr('redshift::RSRamp')

            knotCount = 0
            interp = []
            positions = []
            values = []

            interpTypes = ["constant", "linear", "linear", "linear", "linear", "linear"]
            interpType = interpTypes[mayaNode.findPlug("interpolation", False).asInt()]

            attr = mayaNode.findPlug("colorEntryList", True)
            knotCount = attr.numElements()
            for i in range(knotCount):
                element = attr.elementByLogicalIndex(i)
                position = element.child(0)
                color = element.child(1)

                interp.append(interpType)
                positions.append(position.asFloat())
                values.append((color.child(0).asFloat(), color.child(1).asFloat(), color.child(2).asFloat()))
            
            #textureShader.CreateInput("inputInvert", Sdf.ValueTypeNames.Int).Set(0)
            #textureShader.CreateInput("inputMapping", Sdf.ValueTypeNames.Token).Set('1') #to go the same direction as max, also why is this a token?
        
            textureShader.CreateInput("ramp", Sdf.ValueTypeNames.Int).Set(knotCount)
            textureShader.CreateInput("ramp_basis", Sdf.ValueTypeNames.TokenArray).Set(Vt.TokenArray(interp))
            textureShader.CreateInput("ramp_keys", Sdf.ValueTypeNames.FloatArray).Set(Vt.FloatArray(positions))
            textureShader.CreateInput("ramp_values", Sdf.ValueTypeNames.Color3fArray).Set(Vt.Vec3fArray(values))

            return True
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
        
    @classmethod
    def CanExport(cls, exportArgs):
        if "redshift_usd_material" in exportArgs.convertMaterialsTo:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Supported
        else:
            return mayaUsd.lib.ShaderWriter.ContextSupport.Unsupported

for shaderName in mayaShaderToRS:
    mayaUsd.lib.ShaderWriter.Register(RSShaderWriter, shaderName)

mayaUsd.lib.ShaderWriter.Register(RSTextureWriter, "file")
mayaUsd.lib.ShaderWriter.Register(RSRampWriter, "ramp")
