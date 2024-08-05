import pulumi

PROJECT_NAME = pulumi.get_project()
STACK_NAME = pulumi.get_stack()


def prefix_name(name: str = "") -> str:
    prefix = f"{PROJECT_NAME}-{STACK_NAME}"
    return prefix if name == "" else f"{prefix}-{name}"
