from typing import Any, Dict, List, Tuple

from src.assignments import Assignment, AssignmentList
from src.environment import Environment
from src.errors import ConfigurationError, FormInputError
from src.sheets import Sheet
from src.utils import cast_list_int, cast_list_str


class FormSubmission:
    """
    A container to hold, manage, and format student form submissions (extension requests).
    """

    def __init__(self, form_payload: Dict[str, Any], question_sheet: Sheet, assignments: AssignmentList) -> None:
        """
        Initializes a FormSubmission object to process a student's form submissions. We use an intermediary
        "Form Questions" spreadsheet to allow us to rename form questions without impacting the underlying
        data pointers.
        """
        self.assignments = assignments

        self.responses = {}

        for row in question_sheet.get_all_records():
            question = row.get("question")
            if not question:
                continue
            key = row.get("key")
            if not key:
                raise ConfigurationError(f"The Form Question sheet is missing a key for question: {question}")
            if question in form_payload:
                self.responses[key] = str(form_payload[question][0])

        self.responses["Timestamp"] = form_payload["Timestamp"][0]
        self.responses["Course Name"] = Environment.get_course_name()
        print(self.responses)

    def get_timestamp(self) -> str:
        return self.responses["Timestamp"]

    def get_email(self) -> str:
        return str(self.responses["email"]).lower()

    def knows_assignments(self) -> bool:
        # Encoding default behavior: if form doesn't contain knows_assignments field, then we assume
        # that the student definitely knows their assignments.
        if "knows_assignments" not in self.responses:
            return True

        return self.responses["knows_assignments"] == "Yes"

    def get_raw_requests(self) -> str:
        assert self.knows_assignments()
        return self.responses["assignments"]

    def get_num_requests(self) -> int:
        assert self.knows_assignments()
        return len(self.responses["assignments"].split(","))

    def get_requests(self) -> List[Tuple[Assignment, int]]:
        """
        Fetch a map of ID to # days requested.
        """
        assert self.knows_assignments()
        try:
            names = cast_list_str(self.responses["assignments"])
            try:
                days = cast_list_int(self.responses["days"])
            except Exception:
                raise FormInputError(
                    "Failed to process student input for # days. Please correct and reprocess. "
                    + f'Input: {self.responses["days"]}'
                )

            # A little logic to help with the case where a student selects P1, P1 Checkpoint and asks for "7" days
            # Apply "7" to both P1 and P1 checkpoint
            if len(days) == 1 and len(names) > 1:
                days = [days[0] for _ in range(len(names))]

            if len(names) != len(days):
                raise FormInputError("# assignment names provided does not equal # days requested for each assignment.")

            requests = []
            for name, num_days in zip(names, days):
                assignment = self.assignments.from_name(name)
                if num_days <= 0:
                    raise FormInputError("# requested days must be > 0")

                requests.append((assignment, num_days))

            return requests

        except Exception as e:
            raise FormInputError(f"An error occurred while processing this student's form submission: {e}")

    def get_reason(self) -> str:
        assert self.knows_assignments()
        return self.responses["reason"]

    def get_documentation(self) -> str:
        return self.responses["documentation"]

    def get_game_plan(self) -> str:
        assert not self.knows_assignments()
        return self.responses["game_plan"]
