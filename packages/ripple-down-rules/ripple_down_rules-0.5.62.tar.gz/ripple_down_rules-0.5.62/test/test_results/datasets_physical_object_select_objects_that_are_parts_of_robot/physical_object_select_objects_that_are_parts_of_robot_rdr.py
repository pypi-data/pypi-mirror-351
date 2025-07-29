from typing_extensions import Dict, Any
from ripple_down_rules.rdr import GeneralRDR
from ripple_down_rules.datastructures.case import Case, create_case
from typing import Dict
from . import physical_object_select_objects_that_are_parts_of_robot_output__mcrdr as output__classifier


classifiers_dict = dict()
classifiers_dict['output_'] = output__classifier


def classify(case: Dict) -> Dict[str, Any]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)
    return GeneralRDR._classify(classifiers_dict, case)
