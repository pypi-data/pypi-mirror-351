from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.dynamic_obj.dynamic_obj import DynamicObj
from ..fable_modules.dynamic_obj.dyn_obj import (set_property, set_optional_property)
from ..fable_modules.fable_library.list import (iterate, map, empty, is_empty, head, tail, of_array)
from ..fable_modules.fable_library.map import (FSharpMap__get_Keys, FSharpMap__get_Values)
from ..fable_modules.fable_library.map_util import get_item_from_dict
from ..fable_modules.fable_library.option import some
from ..fable_modules.fable_library.seq import (to_array, delay, collect, append, empty as empty_1, singleton, item, length)
from ..fable_modules.fable_library.string_ import (to_text, printf, to_fail, ends_with_exact, replace)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (get_enumerator, dispose, IEnumerable_1, ignore)
from ..fable_modules.yamlicious.decode import (object, IGetters, IOptionalGetter, string, IRequiredGetter, bool_1, map as map_1, resizearray, float_1, int_1, read)
from ..fable_modules.yamlicious.yamlicious_types import YAMLElement
from .cwltypes import (DirentInstance, CWLType, FileInstance__ctor, DirectoryInstance__ctor, SoftwarePackage, SchemaDefRequirementType__ctor_541DA560, SchemaDefRequirementType)
from .inputs import (InputBinding, CWLInput)
from .outputs import (OutputBinding, CWLOutput)
from .requirements import (DockerRequirement, EnvironmentDef, ResourceRequirementInstance__ctor_D76FC00, ResourceRequirementInstance, Requirement)
from .tool_description import CWLToolDescription
from .workflow_description import CWLWorkflowDescription
from .workflow_steps import (StepInput, StepOutput, WorkflowStep)

__B = TypeVar("__B")

__A = TypeVar("__A")

def ResizeArray_map(f: Callable[[__A], __B], a: Array[Any]) -> Array[Any]:
    b: Array[__B] = []
    enumerator: Any = get_enumerator(a)
    try: 
        while enumerator.System_Collections_IEnumerator_MoveNext():
            i: __A = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
            (b.append(f(i)))

    finally: 
        dispose(enumerator)

    return b


def Decode_overflowDecoder(dyn_obj: DynamicObj, dict_1: Any) -> DynamicObj:
    enumerator: Any = get_enumerator(dict_1)
    try: 
        while enumerator.System_Collections_IEnumerator_MoveNext():
            e: Any = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
            match_value: YAMLElement = e[1]
            (pattern_matching_result, v, s) = (None, None, None)
            if match_value.tag == 3:
                if not is_empty(match_value.fields[0]):
                    if head(match_value.fields[0]).tag == 1:
                        if is_empty(tail(match_value.fields[0])):
                            pattern_matching_result = 0
                            v = head(match_value.fields[0]).fields[0]

                        else: 
                            pattern_matching_result = 2


                    elif head(match_value.fields[0]).tag == 2:
                        if is_empty(tail(match_value.fields[0])):
                            pattern_matching_result = 1
                            s = head(match_value.fields[0]).fields[0]

                        else: 
                            pattern_matching_result = 2


                    else: 
                        pattern_matching_result = 2


                else: 
                    pattern_matching_result = 2


            else: 
                pattern_matching_result = 2

            if pattern_matching_result == 0:
                set_property(e[0], v.Value, dyn_obj)

            elif pattern_matching_result == 1:
                new_dyn_obj: DynamicObj = DynamicObj()
                def action(x: DynamicObj) -> None:
                    set_property(e[0], x, dyn_obj)

                def mapping(arg: YAMLElement) -> DynamicObj:
                    def getter(get: IGetters, arg: Any=arg) -> Any:
                        return get.Overflow.FieldList(empty())

                    return Decode_overflowDecoder(new_dyn_obj, object(getter, arg))

                iterate(action, map(mapping, s))

            elif pattern_matching_result == 2:
                set_property(e[0], e[1], dyn_obj)


    finally: 
        dispose(enumerator)

    return dyn_obj


def Decode_decodeStringOrExpression(y_ele: YAMLElement) -> str:
    (pattern_matching_result, v, c, v_1) = (None, None, None, None)
    if y_ele.tag == 1:
        pattern_matching_result = 0
        v = y_ele.fields[0]

    elif y_ele.tag == 3:
        if not is_empty(y_ele.fields[0]):
            if head(y_ele.fields[0]).tag == 1:
                if is_empty(tail(y_ele.fields[0])):
                    pattern_matching_result = 0
                    v = head(y_ele.fields[0]).fields[0]

                else: 
                    pattern_matching_result = 2


            elif head(y_ele.fields[0]).tag == 0:
                if head(y_ele.fields[0]).fields[1].tag == 3:
                    if not is_empty(head(y_ele.fields[0]).fields[1].fields[0]):
                        if head(head(y_ele.fields[0]).fields[1].fields[0]).tag == 1:
                            if is_empty(tail(head(y_ele.fields[0]).fields[1].fields[0])):
                                if is_empty(tail(y_ele.fields[0])):
                                    pattern_matching_result = 1
                                    c = head(y_ele.fields[0]).fields[0]
                                    v_1 = head(head(y_ele.fields[0]).fields[1].fields[0]).fields[0]

                                else: 
                                    pattern_matching_result = 2


                            else: 
                                pattern_matching_result = 2


                        else: 
                            pattern_matching_result = 2


                    else: 
                        pattern_matching_result = 2


                else: 
                    pattern_matching_result = 2


            else: 
                pattern_matching_result = 2


        else: 
            pattern_matching_result = 2


    else: 
        pattern_matching_result = 2

    if pattern_matching_result == 0:
        return v.Value

    elif pattern_matching_result == 1:
        return to_text(printf("%s: %s"))(c.Value)(v_1.Value)

    elif pattern_matching_result == 2:
        return to_fail(printf("%A"))(y_ele)



def _arrow3361(value_1: YAMLElement) -> OutputBinding:
    def getter(get: IGetters) -> OutputBinding:
        def _arrow3360(__unit: None=None, get: Any=get) -> str | None:
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("glob", string)

        return OutputBinding(_arrow3360())

    return object(getter, value_1)


Decode_outputBindingGlobDecoder: Callable[[YAMLElement], OutputBinding] = _arrow3361

def _arrow3362(value: YAMLElement) -> OutputBinding | None:
    def getter(get: IGetters) -> OutputBinding | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("outputBinding", Decode_outputBindingGlobDecoder)

    return object(getter, value)


Decode_outputBindingDecoder: Callable[[YAMLElement], OutputBinding | None] = _arrow3362

def _arrow3366(value_1: YAMLElement) -> CWLType:
    def getter(get: IGetters) -> CWLType:
        def _arrow3363(__unit: None=None, get: Any=get) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("entry", Decode_decodeStringOrExpression)

        def _arrow3364(__unit: None=None, get: Any=get) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("entryname", Decode_decodeStringOrExpression)

        def _arrow3365(__unit: None=None, get: Any=get) -> bool | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("writable", bool_1)

        return CWLType(2, DirentInstance(_arrow3363(), _arrow3364(), _arrow3365()))

    return object(getter, value_1)


Decode_direntDecoder: Callable[[YAMLElement], CWLType] = _arrow3366

def _arrow3368(value_1: YAMLElement) -> CWLType:
    def getter(get: IGetters) -> CWLType:
        items: str
        object_arg: IRequiredGetter = get.Required
        def arg_1(value: YAMLElement, get: Any=get) -> str:
            return string(value)

        items = object_arg.Field("items", arg_1)
        if items == "File":
            return CWLType(11, CWLType(0, FileInstance__ctor()))

        elif items == "Directory":
            return CWLType(11, CWLType(1, DirectoryInstance__ctor()))

        elif items == "Dirent":
            def _arrow3367(__unit: None=None, get: Any=get) -> CWLType:
                object_arg_1: IRequiredGetter = get.Required
                return object_arg_1.Field("listing", Decode_direntDecoder)

            return CWLType(11, _arrow3367())

        elif items == "string":
            return CWLType(11, CWLType(3))

        elif items == "int":
            return CWLType(11, CWLType(4))

        elif items == "long":
            return CWLType(11, CWLType(5))

        elif items == "float":
            return CWLType(11, CWLType(6))

        elif items == "double":
            return CWLType(11, CWLType(7))

        elif items == "boolean":
            return CWLType(11, CWLType(8))

        else: 
            raise Exception("Invalid CWL type")


    return object(getter, value_1)


Decode_cwlArrayTypeDecoder: Callable[[YAMLElement], CWLType] = _arrow3368

def Decode_cwlTypeStringMatcher(t: str, get: IGetters) -> tuple[CWLType, bool]:
    pattern_input: tuple[bool, str] = ((True, replace(t, "?", ""))) if ends_with_exact(t, "?") else ((False, t))
    new_t: str = pattern_input[1]
    def _arrow3369(__unit: None=None, t: Any=t, get: Any=get) -> CWLType:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("listing", Decode_direntDecoder)

    def _arrow3370(__unit: None=None, t: Any=t, get: Any=get) -> CWLType:
        object_arg_1: IRequiredGetter = get.Required
        return object_arg_1.Field("listing", Decode_direntDecoder)

    def _arrow3371(__unit: None=None, t: Any=t, get: Any=get) -> CWLType:
        raise Exception("Invalid CWL type")

    return (CWLType(0, FileInstance__ctor()) if (new_t == "File") else (CWLType(1, DirectoryInstance__ctor()) if (new_t == "Directory") else (_arrow3369() if (new_t == "Dirent") else (CWLType(3) if (new_t == "string") else (CWLType(4) if (new_t == "int") else (CWLType(5) if (new_t == "long") else (CWLType(6) if (new_t == "float") else (CWLType(7) if (new_t == "double") else (CWLType(8) if (new_t == "boolean") else (CWLType(11, CWLType(0, FileInstance__ctor())) if (new_t == "File[]") else (CWLType(11, CWLType(1, DirectoryInstance__ctor())) if (new_t == "Directory[]") else (CWLType(11, _arrow3370()) if (new_t == "Dirent[]") else (CWLType(11, CWLType(3)) if (new_t == "string[]") else (CWLType(11, CWLType(4)) if (new_t == "int[]") else (CWLType(11, CWLType(5)) if (new_t == "long[]") else (CWLType(11, CWLType(6)) if (new_t == "float[]") else (CWLType(11, CWLType(7)) if (new_t == "double[]") else (CWLType(11, CWLType(8)) if (new_t == "boolean[]") else (CWLType(9) if (new_t == "stdout") else (CWLType(10) if (new_t == "null") else _arrow3371()))))))))))))))))))), pattern_input[0])


def _arrow3373(value_1: YAMLElement) -> tuple[CWLType, bool]:
    def getter(get: IGetters) -> tuple[CWLType, bool]:
        cwl_type: str | None
        object_arg: IRequiredGetter = get.Required
        def arg_1(value: YAMLElement, get: Any=get) -> str | None:
            (pattern_matching_result, v) = (None, None)
            if value.tag == 1:
                pattern_matching_result = 0
                v = value.fields[0]

            elif value.tag == 3:
                if not is_empty(value.fields[0]):
                    if head(value.fields[0]).tag == 1:
                        if is_empty(tail(value.fields[0])):
                            pattern_matching_result = 0
                            v = head(value.fields[0]).fields[0]

                        else: 
                            pattern_matching_result = 1


                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 2

            if pattern_matching_result == 0:
                return v.Value

            elif pattern_matching_result == 1:
                return None

            elif pattern_matching_result == 2:
                raise Exception("Unexpected YAMLElement")


        cwl_type = object_arg.Field("type", arg_1)
        if cwl_type is None:
            def _arrow3372(__unit: None=None, get: Any=get) -> CWLType:
                object_arg_1: IRequiredGetter = get.Required
                return object_arg_1.Field("type", Decode_cwlArrayTypeDecoder)

            return (_arrow3372(), False)

        else: 
            return Decode_cwlTypeStringMatcher(cwl_type, get)


    return object(getter, value_1)


Decode_cwlTypeDecoder: Callable[[YAMLElement], tuple[CWLType, bool]] = _arrow3373

def _arrow3380(value_2: YAMLElement) -> Array[CWLOutput]:
    def getter(get: IGetters) -> Array[CWLOutput]:
        dict_1: Any = get.Overflow.FieldList(empty())
        def _arrow3379(__unit: None=None, get: Any=get) -> IEnumerable_1[CWLOutput]:
            def _arrow3378(key: str) -> IEnumerable_1[CWLOutput]:
                value: YAMLElement = get_item_from_dict(dict_1, key)
                output_binding: OutputBinding | None = Decode_outputBindingDecoder(value)
                output_source: str | None
                object_arg: IOptionalGetter = get.Optional
                output_source = object_arg.Field("outputSource", string)
                output: CWLOutput = CWLOutput(key, (((Decode_cwlTypeStringMatcher(head(value.fields[0]).fields[0].Value, get)[0] if is_empty(tail(value.fields[0])) else Decode_cwlTypeDecoder(value)[0]) if (head(value.fields[0]).tag == 1) else Decode_cwlTypeDecoder(value)[0]) if (not is_empty(value.fields[0])) else Decode_cwlTypeDecoder(value)[0]) if (value.tag == 3) else Decode_cwlTypeDecoder(value)[0])
                def _expr3374():
                    set_optional_property("outputBinding", output_binding, output)
                    return empty_1()

                def _arrow3377(__unit: None=None) -> IEnumerable_1[CWLOutput]:
                    def _expr3375():
                        set_optional_property("outputSource", output_source, output)
                        return empty_1()

                    def _arrow3376(__unit: None=None) -> IEnumerable_1[CWLOutput]:
                        return singleton(output)

                    return append(_expr3375() if (output_source is not None) else empty_1(), delay(_arrow3376))

                return append(_expr3374() if (output_binding is not None) else empty_1(), delay(_arrow3377))

            return collect(_arrow3378, dict_1.keys())

        return list(to_array(delay(_arrow3379)))

    return object(getter, value_2)


Decode_outputArrayDecoder: Callable[[YAMLElement], Array[CWLOutput]] = _arrow3380

def _arrow3381(value: YAMLElement) -> Array[CWLOutput]:
    def getter(get: IGetters) -> Array[CWLOutput]:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("outputs", Decode_outputArrayDecoder)

    return object(getter, value)


Decode_outputsDecoder: Callable[[YAMLElement], Array[CWLOutput]] = _arrow3381

def Decode_dockerRequirementDecoder(get: IGetters) -> DockerRequirement:
    def _arrow3382(__unit: None=None, get: Any=get) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("dockerPull", string)

    def _arrow3384(__unit: None=None, get: Any=get) -> Any | None:
        object_arg_1: IOptionalGetter = get.Optional
        def arg_3(value_1: YAMLElement) -> Any:
            def key_decoder(x: str, value_1: Any=value_1) -> str:
                return x

            def _arrow3383(value_2: YAMLElement, value_1: Any=value_1) -> str:
                return string(value_2)

            return map_1(key_decoder, _arrow3383, value_1)

        return object_arg_1.Field("dockerFile", arg_3)

    def _arrow3385(__unit: None=None, get: Any=get) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("dockerImageId", string)

    return DockerRequirement(_arrow3382(), _arrow3384(), _arrow3385())


def Decode_envVarRequirementDecoder(get: IGetters) -> Array[EnvironmentDef]:
    object_arg: IRequiredGetter = get.Required
    def arg_1(value_3: YAMLElement, get: Any=get) -> Array[EnvironmentDef]:
        def decoder(value_2: YAMLElement, value_3: Any=value_3) -> EnvironmentDef:
            def getter(get2: IGetters, value_2: Any=value_2) -> EnvironmentDef:
                def _arrow3386(__unit: None=None, get2: Any=get2) -> str:
                    object_arg_1: IRequiredGetter = get2.Required
                    return object_arg_1.Field("envName", string)

                def _arrow3387(__unit: None=None, get2: Any=get2) -> str:
                    object_arg_2: IRequiredGetter = get2.Required
                    return object_arg_2.Field("envValue", string)

                return EnvironmentDef(_arrow3386(), _arrow3387())

            return object(getter, value_2)

        return resizearray(decoder, value_3)

    return object_arg.Field("envDef", arg_1)


def Decode_softwareRequirementDecoder(get: IGetters) -> Array[SoftwarePackage]:
    object_arg: IRequiredGetter = get.Required
    def arg_1(value_6: YAMLElement, get: Any=get) -> Array[SoftwarePackage]:
        def decoder(value_5: YAMLElement, value_6: Any=value_6) -> SoftwarePackage:
            def getter(get2: IGetters, value_5: Any=value_5) -> SoftwarePackage:
                def _arrow3388(__unit: None=None, get2: Any=get2) -> str:
                    object_arg_1: IRequiredGetter = get2.Required
                    return object_arg_1.Field("package", string)

                def _arrow3390(__unit: None=None, get2: Any=get2) -> Array[str] | None:
                    object_arg_2: IOptionalGetter = get2.Optional
                    def arg_5(value_1: YAMLElement) -> Array[str]:
                        def _arrow3389(value_2: YAMLElement, value_1: Any=value_1) -> str:
                            return string(value_2)

                        return resizearray(_arrow3389, value_1)

                    return object_arg_2.Field("version", arg_5)

                def _arrow3392(__unit: None=None, get2: Any=get2) -> Array[str] | None:
                    object_arg_3: IOptionalGetter = get2.Optional
                    def arg_7(value_3: YAMLElement) -> Array[str]:
                        def _arrow3391(value_4: YAMLElement, value_3: Any=value_3) -> str:
                            return string(value_4)

                        return resizearray(_arrow3391, value_3)

                    return object_arg_3.Field("specs", arg_7)

                return SoftwarePackage(_arrow3388(), _arrow3390(), _arrow3392())

            return object(getter, value_5)

        return resizearray(decoder, value_6)

    return object_arg.Field("packages", arg_1)


def Decode_initialWorkDirRequirementDecoder(get: IGetters) -> Array[CWLType]:
    object_arg: IRequiredGetter = get.Required
    def arg_1(value: YAMLElement, get: Any=get) -> Array[CWLType]:
        return resizearray(Decode_direntDecoder, value)

    return object_arg.Field("listing", arg_1)


def Decode_resourceRequirementDecoder(get: IGetters) -> ResourceRequirementInstance:
    def _arrow3393(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg: IOptionalGetter = get.Optional
        def arg_1(x: YAMLElement) -> YAMLElement:
            return x

        return object_arg.Field("coresMin", arg_1)

    def _arrow3394(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_1: IOptionalGetter = get.Optional
        def arg_3(x_1: YAMLElement) -> YAMLElement:
            return x_1

        return object_arg_1.Field("coresMax", arg_3)

    def _arrow3395(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_2: IOptionalGetter = get.Optional
        def arg_5(x_2: YAMLElement) -> YAMLElement:
            return x_2

        return object_arg_2.Field("ramMin", arg_5)

    def _arrow3396(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_3: IOptionalGetter = get.Optional
        def arg_7(x_3: YAMLElement) -> YAMLElement:
            return x_3

        return object_arg_3.Field("ramMax", arg_7)

    def _arrow3397(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_4: IOptionalGetter = get.Optional
        def arg_9(x_4: YAMLElement) -> YAMLElement:
            return x_4

        return object_arg_4.Field("tmpdirMin", arg_9)

    def _arrow3398(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_5: IOptionalGetter = get.Optional
        def arg_11(x_5: YAMLElement) -> YAMLElement:
            return x_5

        return object_arg_5.Field("tmpdirMax", arg_11)

    def _arrow3399(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_6: IOptionalGetter = get.Optional
        def arg_13(x_6: YAMLElement) -> YAMLElement:
            return x_6

        return object_arg_6.Field("outdirMin", arg_13)

    def _arrow3400(__unit: None=None, get: Any=get) -> YAMLElement | None:
        object_arg_7: IOptionalGetter = get.Optional
        def arg_15(x_7: YAMLElement) -> YAMLElement:
            return x_7

        return object_arg_7.Field("outdirMax", arg_15)

    return ResourceRequirementInstance__ctor_D76FC00(some(_arrow3393()), some(_arrow3394()), some(_arrow3395()), some(_arrow3396()), some(_arrow3397()), some(_arrow3398()), some(_arrow3399()), some(_arrow3400()))


def Decode_schemaDefRequirementDecoder(get: IGetters) -> Array[SchemaDefRequirementType]:
    def f(m: Any, get: Any=get) -> SchemaDefRequirementType:
        return SchemaDefRequirementType__ctor_541DA560(item(0, FSharpMap__get_Keys(m)), item(0, FSharpMap__get_Values(m)))

    def _arrow3402(__unit: None=None, get: Any=get) -> Array[Any]:
        object_arg: IRequiredGetter = get.Required
        def arg_1(value_2: YAMLElement) -> Array[Any]:
            def decoder(value: YAMLElement, value_2: Any=value_2) -> Any:
                def key_decoder(x: str, value: Any=value) -> str:
                    return x

                def _arrow3401(value_1: YAMLElement, value: Any=value) -> str:
                    return string(value_1)

                return map_1(key_decoder, _arrow3401, value)

            return resizearray(decoder, value_2)

        return object_arg.Field("types", arg_1)

    return ResizeArray_map(f, _arrow3402())


def Decode_toolTimeLimitRequirementDecoder(get: IGetters) -> float:
    object_arg: IRequiredGetter = get.Required
    def arg_1(value: YAMLElement, get: Any=get) -> float:
        return float_1(value)

    return object_arg.Field("timelimit", arg_1)


def _arrow3403(value_2: YAMLElement) -> Array[Requirement]:
    def decoder(value_1: YAMLElement) -> Requirement:
        def getter(get: IGetters, value_1: Any=value_1) -> Requirement:
            cls: str
            object_arg: IRequiredGetter = get.Required
            def arg_1(value: YAMLElement, get: Any=get) -> str:
                return string(value)

            cls = object_arg.Field("class", arg_1)
            if cls == "InlineJavascriptRequirement":
                return Requirement(0)

            elif cls == "SchemaDefRequirement":
                return Requirement(1, Decode_schemaDefRequirementDecoder(get))

            elif cls == "DockerRequirement":
                return Requirement(2, Decode_dockerRequirementDecoder(get))

            elif cls == "SoftwareRequirement":
                return Requirement(3, Decode_softwareRequirementDecoder(get))

            elif cls == "InitialWorkDirRequirement":
                return Requirement(4, Decode_initialWorkDirRequirementDecoder(get))

            elif cls == "EnvVarRequirement":
                return Requirement(5, Decode_envVarRequirementDecoder(get))

            elif cls == "ShellCommandRequirement":
                return Requirement(6)

            elif cls == "ResourceRequirement":
                return Requirement(7, Decode_resourceRequirementDecoder(get))

            elif cls == "WorkReuse":
                return Requirement(8)

            elif cls == "NetworkAccess":
                return Requirement(9)

            elif cls == "InplaceUpdateRequirement":
                return Requirement(10)

            elif cls == "ToolTimeLimit":
                return Requirement(11, Decode_toolTimeLimitRequirementDecoder(get))

            elif cls == "SubworkflowFeatureRequirement":
                return Requirement(12)

            elif cls == "ScatterFeatureRequirement":
                return Requirement(13)

            elif cls == "MultipleInputFeatureRequirement":
                return Requirement(14)

            elif cls == "StepInputExpressionRequirement":
                return Requirement(15)

            else: 
                raise Exception("Invalid requirement")


        return object(getter, value_1)

    return resizearray(decoder, value_2)


Decode_requirementArrayDecoder: Callable[[YAMLElement], Array[Requirement]] = _arrow3403

def _arrow3404(value: YAMLElement) -> Array[Requirement] | None:
    def getter(get: IGetters) -> Array[Requirement] | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("requirements", Decode_requirementArrayDecoder)

    return object(getter, value)


Decode_requirementsDecoder: Callable[[YAMLElement], Array[Requirement] | None] = _arrow3404

def _arrow3405(value: YAMLElement) -> Array[Requirement] | None:
    def getter(get: IGetters) -> Array[Requirement] | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("hints", Decode_requirementArrayDecoder)

    return object(getter, value)


Decode_hintsDecoder: Callable[[YAMLElement], Array[Requirement] | None] = _arrow3405

def _arrow3410(value_5: YAMLElement) -> InputBinding | None:
    def getter_1(get: IGetters) -> InputBinding | None:
        object_arg: IOptionalGetter = get.Optional
        def arg_1(value_4: YAMLElement, get: Any=get) -> InputBinding:
            def getter(get_0027: IGetters, value_4: Any=value_4) -> InputBinding:
                def _arrow3406(__unit: None=None, get_0027: Any=get_0027) -> str | None:
                    object_arg_1: IOptionalGetter = get_0027.Optional
                    return object_arg_1.Field("prefix", string)

                def _arrow3407(__unit: None=None, get_0027: Any=get_0027) -> int | None:
                    object_arg_2: IOptionalGetter = get_0027.Optional
                    return object_arg_2.Field("position", int_1)

                def _arrow3408(__unit: None=None, get_0027: Any=get_0027) -> str | None:
                    object_arg_3: IOptionalGetter = get_0027.Optional
                    return object_arg_3.Field("itemSeparator", string)

                def _arrow3409(__unit: None=None, get_0027: Any=get_0027) -> bool | None:
                    object_arg_4: IOptionalGetter = get_0027.Optional
                    return object_arg_4.Field("separate", bool_1)

                return InputBinding(_arrow3406(), _arrow3407(), _arrow3408(), _arrow3409())

            return object(getter, value_4)

        return object_arg.Field("inputBinding", arg_1)

    return object(getter_1, value_5)


Decode_inputBindingDecoder: Callable[[YAMLElement], InputBinding | None] = _arrow3410

def _arrow3417(value_1: YAMLElement) -> Array[CWLInput]:
    def getter(get: IGetters) -> Array[CWLInput]:
        dict_1: Any = get.Overflow.FieldList(empty())
        def _arrow3416(__unit: None=None, get: Any=get) -> IEnumerable_1[CWLInput]:
            def _arrow3415(key: str) -> IEnumerable_1[CWLInput]:
                value: YAMLElement = get_item_from_dict(dict_1, key)
                input_binding: InputBinding | None = Decode_inputBindingDecoder(value)
                pattern_input: tuple[CWLType, bool] = (((Decode_cwlTypeStringMatcher(head(value.fields[0]).fields[0].Value, get) if is_empty(tail(value.fields[0])) else Decode_cwlTypeDecoder(value)) if (head(value.fields[0]).tag == 1) else Decode_cwlTypeDecoder(value)) if (not is_empty(value.fields[0])) else Decode_cwlTypeDecoder(value)) if (value.tag == 3) else Decode_cwlTypeDecoder(value)
                input: CWLInput = CWLInput(key, pattern_input[0])
                def _expr3411():
                    set_optional_property("inputBinding", input_binding, input)
                    return empty_1()

                def _arrow3414(__unit: None=None) -> IEnumerable_1[CWLInput]:
                    def _expr3412():
                        set_optional_property("optional", True, input)
                        return empty_1()

                    def _arrow3413(__unit: None=None) -> IEnumerable_1[CWLInput]:
                        return singleton(input)

                    return append(_expr3412() if pattern_input[1] else empty_1(), delay(_arrow3413))

                return append(_expr3411() if (input_binding is not None) else empty_1(), delay(_arrow3414))

            return collect(_arrow3415, dict_1.keys())

        return list(to_array(delay(_arrow3416)))

    return object(getter, value_1)


Decode_inputArrayDecoder: Callable[[YAMLElement], Array[CWLInput]] = _arrow3417

def _arrow3418(value: YAMLElement) -> Array[CWLInput] | None:
    def getter(get: IGetters) -> Array[CWLInput] | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("inputs", Decode_inputArrayDecoder)

    return object(getter, value)


Decode_inputsDecoder: Callable[[YAMLElement], Array[CWLInput] | None] = _arrow3418

def _arrow3420(value_2: YAMLElement) -> Array[str] | None:
    def getter(get: IGetters) -> Array[str] | None:
        object_arg: IOptionalGetter = get.Optional
        def arg_1(value: YAMLElement, get: Any=get) -> Array[str]:
            def _arrow3419(value_1: YAMLElement, value: Any=value) -> str:
                return string(value_1)

            return resizearray(_arrow3419, value)

        return object_arg.Field("baseCommand", arg_1)

    return object(getter, value_2)


Decode_baseCommandDecoder: Callable[[YAMLElement], Array[str] | None] = _arrow3420

def _arrow3421(value_1: YAMLElement) -> str:
    def getter(get: IGetters) -> str:
        object_arg: IRequiredGetter = get.Required
        def arg_1(value: YAMLElement, get: Any=get) -> str:
            return string(value)

        return object_arg.Field("cwlVersion", arg_1)

    return object(getter, value_1)


Decode_versionDecoder: Callable[[YAMLElement], str] = _arrow3421

def _arrow3422(value_1: YAMLElement) -> str:
    def getter(get: IGetters) -> str:
        object_arg: IRequiredGetter = get.Required
        def arg_1(value: YAMLElement, get: Any=get) -> str:
            return string(value)

        return object_arg.Field("class", arg_1)

    return object(getter, value_1)


Decode_classDecoder: Callable[[YAMLElement], str] = _arrow3422

def Decode_stringOptionFieldDecoder(field: str) -> Callable[[YAMLElement], str | None]:
    def _arrow3423(value_1: YAMLElement, field: Any=field) -> str | None:
        def getter(get: IGetters) -> str | None:
            object_arg: IOptionalGetter = get.Optional
            def arg_1(value: YAMLElement, get: Any=get) -> str:
                return string(value)

            return object_arg.Field(field, arg_1)

        return object(getter, value_1)

    return _arrow3423


def Decode_stringFieldDecoder(field: str) -> Callable[[YAMLElement], str]:
    def _arrow3424(value_1: YAMLElement, field: Any=field) -> str:
        def getter(get: IGetters) -> str:
            object_arg: IRequiredGetter = get.Required
            def arg_1(value: YAMLElement, get: Any=get) -> str:
                return string(value)

            return object_arg.Field(field, arg_1)

        return object(getter, value_1)

    return _arrow3424


def _arrow3428(value_1: YAMLElement) -> Array[StepInput]:
    def getter(get: IGetters) -> Array[StepInput]:
        dict_1: Any = get.Overflow.FieldList(empty())
        def _arrow3427(__unit: None=None, get: Any=get) -> IEnumerable_1[StepInput]:
            def _arrow3426(key: str) -> IEnumerable_1[StepInput]:
                value: YAMLElement = get_item_from_dict(dict_1, key)
                def _arrow3425(__unit: None=None) -> str | None:
                    s1: str | None = (((head(value.fields[0]).fields[0].Value if is_empty(tail(value.fields[0])) else None) if (head(value.fields[0]).tag == 1) else None) if (not is_empty(value.fields[0])) else None) if (value.tag == 3) else None
                    s2: str | None = Decode_stringOptionFieldDecoder("source")(value)
                    return s1 if (s1 is not None) else (s2 if (s2 is not None) else None)

                return singleton(StepInput(key, _arrow3425(), Decode_stringOptionFieldDecoder("default")(value), Decode_stringOptionFieldDecoder("valueFrom")(value)))

            return collect(_arrow3426, dict_1.keys())

        return list(to_array(delay(_arrow3427)))

    return object(getter, value_1)


Decode_inputStepDecoder: Callable[[YAMLElement], Array[StepInput]] = _arrow3428

def _arrow3430(value_2: YAMLElement) -> Array[str]:
    def getter(get: IGetters) -> Array[str]:
        object_arg: IRequiredGetter = get.Required
        def arg_1(value: YAMLElement, get: Any=get) -> Array[str]:
            def _arrow3429(value_1: YAMLElement, value: Any=value) -> str:
                return string(value_1)

            return resizearray(_arrow3429, value)

        return object_arg.Field("out", arg_1)

    return object(getter, value_2)


Decode_outputStepsDecoder: Callable[[YAMLElement], Array[str]] = _arrow3430

def _arrow3438(value_1: YAMLElement) -> Array[WorkflowStep]:
    def getter(get: IGetters) -> Array[WorkflowStep]:
        dict_1: Any = get.Overflow.FieldList(empty())
        def _arrow3437(__unit: None=None, get: Any=get) -> IEnumerable_1[WorkflowStep]:
            def _arrow3436(key: str) -> IEnumerable_1[WorkflowStep]:
                value: YAMLElement = get_item_from_dict(dict_1, key)
                run: str = Decode_stringFieldDecoder("run")(value)
                def _arrow3431(get_1: IGetters) -> Array[StepInput]:
                    object_arg: IRequiredGetter = get_1.Required
                    return object_arg.Field("in", Decode_inputStepDecoder)

                inputs: Array[StepInput] = object(_arrow3431, value)
                outputs: StepOutput = StepOutput(Decode_outputStepsDecoder(value))
                requirements: Array[Requirement] | None = Decode_requirementsDecoder(value)
                hints: Array[Requirement] | None = Decode_hintsDecoder(value)
                wf_step: WorkflowStep = WorkflowStep(key, inputs, outputs, run)
                def _expr3432():
                    wf_step.Requirements = requirements
                    return empty_1()

                def _arrow3435(__unit: None=None) -> IEnumerable_1[WorkflowStep]:
                    def _expr3433():
                        wf_step.Hints = hints
                        return empty_1()

                    def _arrow3434(__unit: None=None) -> IEnumerable_1[WorkflowStep]:
                        return singleton(wf_step)

                    return append(_expr3433() if (hints is not None) else empty_1(), delay(_arrow3434))

                return append(_expr3432() if (requirements is not None) else empty_1(), delay(_arrow3435))

            return collect(_arrow3436, dict_1.keys())

        return list(to_array(delay(_arrow3437)))

    return object(getter, value_1)


Decode_stepArrayDecoder: Callable[[YAMLElement], Array[WorkflowStep]] = _arrow3438

def _arrow3439(value: YAMLElement) -> Array[WorkflowStep]:
    def getter(get: IGetters) -> Array[WorkflowStep]:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("steps", Decode_stepArrayDecoder)

    return object(getter, value)


Decode_stepsDecoder: Callable[[YAMLElement], Array[WorkflowStep]] = _arrow3439

def Decode_decodeCommandLineTool(cwl: str) -> CWLToolDescription:
    yaml_cwl: YAMLElement = read(cwl)
    cwl_version: str = Decode_versionDecoder(yaml_cwl)
    outputs: Array[CWLOutput] = Decode_outputsDecoder(yaml_cwl)
    inputs: Array[CWLInput] | None = Decode_inputsDecoder(yaml_cwl)
    requirements: Array[Requirement] | None = Decode_requirementsDecoder(yaml_cwl)
    hints: Array[Requirement] | None = Decode_hintsDecoder(yaml_cwl)
    base_command: Array[str] | None = Decode_baseCommandDecoder(yaml_cwl)
    description: CWLToolDescription = CWLToolDescription(outputs, cwl_version)
    metadata: DynamicObj
    md: DynamicObj = DynamicObj()
    def getter(get: IGetters, cwl: Any=cwl) -> DynamicObj:
        return Decode_overflowDecoder(md, get.Overflow.FieldList(of_array(["inputs", "outputs", "class", "id", "label", "doc", "requirements", "hints", "cwlVersion", "baseCommand", "arguments", "stdin", "stderr", "stdout", "successCodes", "temporaryFailCodes", "permanentFailCodes"])))

    ignore(object(getter, yaml_cwl))
    metadata = md
    def getter_1(get_1: IGetters, cwl: Any=cwl) -> DynamicObj:
        return Decode_overflowDecoder(description, get_1.MultipleOptional.FieldList(of_array(["id", "label", "doc", "arguments", "stdin", "stderr", "stdout", "successCodes", "temporaryFailCodes", "permanentFailCodes"])))

    ignore(object(getter_1, yaml_cwl))
    if inputs is not None:
        description.Inputs = inputs

    if requirements is not None:
        description.Requirements = requirements

    if hints is not None:
        description.Hints = hints

    if base_command is not None:
        description.BaseCommand = base_command

    if length(metadata.GetProperties(False)) > 0:
        description.Metadata = metadata

    return description


def Decode_decodeWorkflow(cwl: str) -> CWLWorkflowDescription:
    yaml_cwl: YAMLElement = read(cwl)
    cwl_version: str = Decode_versionDecoder(yaml_cwl)
    outputs: Array[CWLOutput] = Decode_outputsDecoder(yaml_cwl)
    inputs: Array[CWLInput]
    match_value: Array[CWLInput] | None = Decode_inputsDecoder(yaml_cwl)
    if match_value is None:
        raise Exception("Inputs are required for a workflow")

    else: 
        inputs = match_value

    requirements: Array[Requirement] | None = Decode_requirementsDecoder(yaml_cwl)
    hints: Array[Requirement] | None = Decode_hintsDecoder(yaml_cwl)
    description: CWLWorkflowDescription = CWLWorkflowDescription(Decode_stepsDecoder(yaml_cwl), inputs, outputs, cwl_version)
    metadata: DynamicObj
    md: DynamicObj = DynamicObj()
    def getter(get: IGetters, cwl: Any=cwl) -> DynamicObj:
        return Decode_overflowDecoder(md, get.Overflow.FieldList(of_array(["inputs", "outputs", "class", "steps", "id", "label", "doc", "requirements", "hints", "cwlVersion"])))

    ignore(object(getter, yaml_cwl))
    metadata = md
    def getter_1(get_1: IGetters, cwl: Any=cwl) -> DynamicObj:
        return Decode_overflowDecoder(description, get_1.MultipleOptional.FieldList(of_array(["id", "label", "doc"])))

    ignore(object(getter_1, yaml_cwl))
    if requirements is not None:
        description.Requirements = requirements

    if hints is not None:
        description.Hints = hints

    if length(metadata.GetProperties(False)) > 0:
        description.Metadata = metadata

    return description


__all__ = ["ResizeArray_map", "Decode_overflowDecoder", "Decode_decodeStringOrExpression", "Decode_outputBindingGlobDecoder", "Decode_outputBindingDecoder", "Decode_direntDecoder", "Decode_cwlArrayTypeDecoder", "Decode_cwlTypeStringMatcher", "Decode_cwlTypeDecoder", "Decode_outputArrayDecoder", "Decode_outputsDecoder", "Decode_dockerRequirementDecoder", "Decode_envVarRequirementDecoder", "Decode_softwareRequirementDecoder", "Decode_initialWorkDirRequirementDecoder", "Decode_resourceRequirementDecoder", "Decode_schemaDefRequirementDecoder", "Decode_toolTimeLimitRequirementDecoder", "Decode_requirementArrayDecoder", "Decode_requirementsDecoder", "Decode_hintsDecoder", "Decode_inputBindingDecoder", "Decode_inputArrayDecoder", "Decode_inputsDecoder", "Decode_baseCommandDecoder", "Decode_versionDecoder", "Decode_classDecoder", "Decode_stringOptionFieldDecoder", "Decode_stringFieldDecoder", "Decode_inputStepDecoder", "Decode_outputStepsDecoder", "Decode_stepArrayDecoder", "Decode_stepsDecoder", "Decode_decodeCommandLineTool", "Decode_decodeWorkflow"]

