from enum import StrEnum


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMINISTRATOR = "administrator"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class Permission(StrEnum):
    READ = "read"
    CONTRIBUTE = "contribute"
    MANAGE_PROJECTS = "manage_projects"
    PUBLISH = "publish"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_ADMINISTRATORS = "manage_administrators"
    DEACTIVATE_WORKSPACE = "deactivate_workspace"


ROLE_PERMISSIONS = {
    WorkspaceRole.VIEWER: frozenset({Permission.READ}),
    WorkspaceRole.CONTRIBUTOR: frozenset({Permission.READ, Permission.CONTRIBUTE}),
    WorkspaceRole.ADMINISTRATOR: frozenset(
        {
            Permission.READ,
            Permission.CONTRIBUTE,
            Permission.MANAGE_PROJECTS,
            Permission.PUBLISH,
            Permission.MANAGE_MEMBERS,
        }
    ),
    WorkspaceRole.OWNER: frozenset(Permission),
}


def role_allows(role: str | WorkspaceRole, permission: Permission) -> bool:
    try:
        workspace_role = WorkspaceRole(role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS[workspace_role]
