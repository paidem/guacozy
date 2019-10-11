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
        add_folder_to_tree_dictionary(child, resulting_set, False)


def check_folder_permissions(folder, resulting_set, user):
    """
    Recursively check folders and adds it's ancestors/descendants if any permissions found.

    :type user: users.User
    :type resulting_set: set
    :type folder: backend.Folder
    """
    if rules.test_rule('has_direct_permission', user, folder):
        add_folder_to_tree_dictionary(folder, resulting_set, include_ancestors=True)
    else:
        for child in folder.children.all():
            check_folder_permissions(child, resulting_set, user)


def folder_to_object(folder, user, folders_allowed_to_list=None, allowed_to_view=False, include_objects=True):
    """
    Given folder converts it and it's children and objects to a tree format, which is used in API

    :type folder: Folder
    :type user: users.User
    :type folders_allowed_to_list: set
    :type allowed_to_view: bool
    :type include_objects: bool
    """

    if folders_allowed_to_list is None:
        folders_allowed_to_list = set()

    # Include children either if directed or if this folder has inherited permission
    # which means full access to all children
    allowed_to_view = allowed_to_view or rules.test_rule('has_inherited_permission', user, folder)

    result = {'id': folder.id, 'text': folder.name, 'isFolder': True}
    result_children = []

    # For every child check if it is included in allowed folders
    # (precalculated list of folders allowed and
    # their ancestors, which is needed to get to this folder
    for child in folder.children.all():
        if allowed_to_view or child in folders_allowed_to_list:
            result_children += [folder_to_object(
                folder=child,
                user=user,
                folders_allowed_to_list=folders_allowed_to_list,
                allowed_to_view=allowed_to_view,
                include_objects=include_objects
            )
            ]

    # Ff we are asked (include_objects) and allowd (auto_allow_objects) -
    # include all objects currently only connections,
    # but in the future something else can be in folders
    if include_objects and allowed_to_view:
        for connection in folder.connections.all():
            connection_object = {'id': connection.id, 'text': connection.name,
                                 'isFolder': False}
            result_children += [connection_object]

    result['children'] = result_children

    return result


def user_allowed_folders(user):
    """
    Return set of folders user is allowed to list
    Check all folders to determine folders allowed to list
    We allow not only folders where permission is defined,
    but all descendants (permission propagation) and all ancestores
    (needed to build tree path to this folder from root folders)

    :type user: users.User
    """
    resulting_folder = set()

    # iterate over root folders
    for folder in Folder.objects.all().filter(parent=None):
        check_folder_permissions(folder, resulting_folder, user)
    return resulting_folder


def user_allowed_folders_ids(user):
    """
    Return list of ids of folders user is allowed to list

    :type user: users.User
    """
    resulting_set = set()
    for folder in user_allowed_folders(user):
        resulting_set.add(folder.id)

    return resulting_set
