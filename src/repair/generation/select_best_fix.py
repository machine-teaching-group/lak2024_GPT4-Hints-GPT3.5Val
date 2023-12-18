import sys
from typing import Optional, Sequence

sys.path.append(".")

from src.repair.evaluation.metrics import pass_all_test_cases
from src.repair.generation.generate_fixes import FixObject
from src.utils.edit_distance_utils import compute_edit_distance
from src.utils.program_utils import program_to_essential_tokens


def filter_by_passing_test_cases(
    dataset: str,
    fix_objects: Sequence[FixObject],
    test_script: Optional[str] = None,
    testcases_path: Optional[str] = None,
    driver_code: Optional[str] = None,
) -> Sequence[FixObject]:
    """
    Input: a list of repairs (generated by LLM).
    Output: Only the repairs that pass all test cases (i.e., correct repairs).
    """
    correct_fix_objects = []

    for fix_object in fix_objects:
        fix = fix_object.fixed_program
        if fix is not None and pass_all_test_cases(
            dataset,
            input_program=fix,
            test_script=test_script,
            testcases_folder=testcases_path,
            driver_code=driver_code,
        ):
            correct_fix_objects.append(fix_object)

    return correct_fix_objects


def select_fix_by_ed(
    buggy_program: str,
    correct_fix_objects: Sequence[FixObject],
) -> FixObject:
    """
    Input a list of correct fixed programs (i.e., the repairs that pass all test cases).
    Select the final fixed program: The correct program with the shortest edit distance to the buggy program.
    """
    if len(correct_fix_objects) == 0:
        return FixObject(None, None)

    # Select the program with the shortest edit distance
    buggy_tokens = program_to_essential_tokens(buggy_program)
    best_fix_object, minimum_ed = FixObject(None, None), 1e9
    for fix_object in correct_fix_objects:
        ed = compute_edit_distance(buggy_tokens, program_to_essential_tokens(fix_object.fixed_program))
        if ed < minimum_ed:
            minimum_ed = ed
            best_fix_object = fix_object

    return best_fix_object


if __name__ == "__main__":
    pass