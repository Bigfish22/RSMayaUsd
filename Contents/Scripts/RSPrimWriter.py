import mayaUsd
from pxr import UsdLux, Sdf, Gf
import maya.api.OpenMaya as om2
import traceback


class RSLightPrimWriter(mayaUsd.lib.PrimWriter):
    def __init__(self, *args, **kwargs):

        super(RSLightPrimWriter, self).__init__(*args, **kwargs)

        node = om2.MFnDependencyNode(self.GetMayaObject())
        lightType = node.findPlug("lightType", True).asInt()
        if lightType == 0: #area
            shape = node.findPlug("areaShape", True).asInt()
            if shape == 0:
                primSchema = UsdLux.RectLight.Define(self.GetUsdStage(), self.GetUsdPath())
            elif shape == 1:
                primSchema = UsdLux.DiskLight.Define(self.GetUsdStage(), self.GetUsdPath())
            elif shape == 2:
                primSchema = UsdLux.SphereLight.Define(self.GetUsdStage(), self.GetUsdPath())
            elif shape == 3:
                primSchema = UsdLux.CylinderLight.Define(self.GetUsdStage(), self.GetUsdPath())
            else:
                 #just for now catch any types we didn't grab before
                 primSchema = UsdLux.RectLight.Define(self.GetUsdStage(), self.GetUsdPath())
        elif lightType == 3:
            primSchema = UsdLux.DistantLight.Define(self.GetUsdStage(), self.GetUsdPath())
        else:
            #just for now catch any types we didn't grab before
            primSchema = UsdLux.RectLight.Define(self.GetUsdStage(), self.GetUsdPath())
        
        usdPrim = primSchema.GetPrim()

        self._SetUsdPrim(usdPrim)

    def Write(self, usdTime):
        try:
            node = om2.MFnDependencyNode(self.GetMayaObject())

            usdPrim = self.GetUsdPrim()
            lightPrim = UsdLux.RectLight(usdPrim)

            #it would probably nicer to remove the scale and set these correctly based on the scale, as to avoid the lights having scales
            #on them in other apps
            lightPrim.CreateWidthAttr().Set(2.0, usdTime)
            lightPrim.CreateHeightAttr().Set(2.0, usdTime)

            WriteProperty(lightPrim.CreateIntensityAttr(), node, "intensity", usdTime)
            WriteProperty(lightPrim.CreateExposureAttr(), node, "exposure", usdTime)
            if node.findPlug("colorMode", True).asInt() == 1:
                lightPrim.CreateEnableColorTemperatureAttr(True)
            WriteProperty(lightPrim.CreateColorTemperatureAttr(), node, "temperature", usdTime)
            WritePropertyColor(lightPrim.CreateColorAttr(), node, "color", usdTime)

            if usdPrim.GetTypeName() == "DiskLight":
                lightPrim = UsdLux.DiskLight(usdPrim)
                lightPrim.CreateRadiusAttr().Set(1)
            elif usdPrim.GetTypeName() == "SphereLight":
                lightPrim = UsdLux.SphereLight(usdPrim)
                lightPrim.CreateRadiusAttr().Set(1)
            elif usdPrim.GetTypeName() == "CylinderLight":
                lightPrim = UsdLux.SphereLight(usdPrim)
                lightPrim.CreateRadiusAttr().Set(1)
                lightPrim.CreateLengthAttr().Set(2)

        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())

    @classmethod
    def CanExport(cls, exportArgs, exportObj=None):
        return mayaUsd.lib.PrimWriter.ContextSupport.Supported
    

def WriteProperty(usdAttribute, depNode, property, usdTime):
    mayaAttr = depNode.findPlug(property, True)
    usdAttribute.Set(mayaAttr.asFloat(), usdTime)

def WritePropertyColor(usdAttribute, depNode, property, usdTime):
    mayaAttr = depNode.findPlug(property, True)
    usdAttribute.Set((mayaAttr.child(0).asFloat(), mayaAttr.child(1).asFloat(), mayaAttr.child(2).asFloat()), usdTime)
    
mayaUsd.lib.PrimWriter.Register(RSLightPrimWriter, "RedshiftPhysicalLight")