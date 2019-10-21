import rules

from backend.models import Folder


def add_folder_to_tree_dictionary(folder, resulting_set, include_ancestors=False):
    """
    Adds folder, folder's ancestors and folder's descendants

    Ancestors are needed to build the traverse path in tree view
    Descendants are needed because user has permission to see them

    :type folder: Folder
    :type resulting_set: set
    :type include_ancestors: bool}
    """
    # Include all ancestors, which we get from django-mptt's get_ancestors()
    # it's a "cheap" query
    if include_ancestors and folder.parent is not None:
        for ancestor in folder.parent.get_ancestors(ascending=False, include_self=True):
            resulting_set.add(ancestor)

    # add this folder
    resulting_set.add(folder)

    # add all foldres children
    for child in folder.children.all():
        add_folder_to_tree_dictionary(child, resulting_set, include_ancestors=False)


def check_folder_permissions(folder, resulting_set, user, require_view_permission=False):
    """
    Recursively check folders and adds it to resulting_set if user has direct permission on folder
    If require_view_permission is set to True, it returns only folders with direct permission and all child folders
    If require_view_permission is set to True, it also returns all ancestor folders

    :type folder: backend.Folder
    :type user: users.User
    :type resulting_set: set
    :type require_view_permission: bool
    """
    if rules.test_rule('has_direct_permission', user, folder):
        add_folder_to_tree_dictionary(folder, resulting_set, include_ancestors=not require_view_permission)
    else:
        for child in folder.children.all():
            check_folder_permissions(child, resulting_set, user, require_view_permission)


def folder_to_object(folder, user, allowed_to_list=None, allowed_to_view=None, include_objects=True):
    """
    Given folder converts it and it's children and objects to a tree format, which is used in API

    :type folder: Folder
    :type user: users.User
    :type allowed_to_list: set
    :type allowed_to_view: set
    :type include_objects: bool
    """

    if allowed_to_list is None:
        allowed_to_list = user_allowed_folders_ids(user, require_view_permission=False)

    if allowed_to_view is None:
        allowed_to_view = user_allowed_folders_ids(user, require_view_permission=True)

    result = {'id': folder.id, 'text': folder.name, 'isFolder': True}
    result_children = []

    # For every child check if it is included in allowed folders
    # (precalculated list of folders allowed and
    # their ancestors, which is needed to get to this folder
    for child in folder.children.all():
        if child in allowed_to_list:
            result_children += [folder_to_object(
                folder=child,
                user=user,
                allowed_to_list=allowed_to_list,
                allowed_to_view=allowed_to_view,
                include_objects=include_objects
            )
            ]

    # If we are asked (include_objects) and folder is in allowed_to_view list
    # include all objects (currently only connections)
    if include_objects and folder.id in allowed_to_view:
        for connection in folder.connections.all():
            connection_object = {'id': connection.id,
                                 'text': connection.name,
                                 'isFolder': False,
                                 'protocol': connection.protocol,
                                 }
            result_children += [connection_object]

    result['children'] = result_children

    return result


def user_allowed_folders(user, require_view_permission=False):
    """
    If require_view_permission is False, return list of folders user is allowed to list
    If require_view_permission is True, return list of folders user is allowed to view

    :type require_view_permission: bool
    :type user: users.User
    """
    resulting_folder = set()

    # iterate over root folders
    for folder in Folder.objects.all().filter(parent=None):
        check_folder_permissions(folder, resulting_folder, user, require_view_permission)
    return resulting_folder


def user_allowed_folders_ids(user, require_view_permission=False):
    """
    If require_view_permission is False, return list of ids of folders user is allowed to list
    If require_view_permission is True, return list of ids of folders user is allowed to view

    :type require_view_permission: bool
    :type user: users.User
    """
    resulting_set = set()
    for folder in user_allowed_folders(user, require_view_permission):
        resulting_set.add(folder.id)

    return resulting_set
