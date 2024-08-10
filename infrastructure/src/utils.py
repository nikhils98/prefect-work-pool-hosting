import pulumi

PROJECT_NAME = pulumi.get_project()
STACK_NAME = pulumi.get_stack()


# helper function to prefix the name of resources
# with project and stack. This helps with maintaining
# uniqueness of names when there are multiple resources
# based on different projects in our aws account.
def prefix_name(name: str = "") -> str:
    prefix = f"{PROJECT_NAME}-{STACK_NAME}"
    return prefix if name == "" else f"{prefix}-{name}"
