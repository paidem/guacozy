import rules

# PersonalNamedCredentials permissions
@rules.predicate
def is_owner(user, obj):
    if obj is None:
        return True
    return obj.owner == user


rules.add_perm('backend.add_personalnamedcredentials', is_owner)
rules.add_perm('backend.view_personalnamedcredentials', is_owner)
rules.add_perm('backend.change_personalnamedcredentials', is_owner)
rules.add_perm('backend.delete_personalnamedcredentials', is_owner)

# Ticket permissions
@rules.predicate
def can_see_ticket(user, obj):
    if obj is None:
        return True
    return obj.author == user or obj.user == user


@rules.predicate
def is_ticket_user_or_author(user, obj):
    if obj is None:
        return False
    return obj.author == user or obj.user == user


rules.add_perm('backend.add_ticket', is_ticket_user_or_author)
rules.add_perm('backend.view_ticket', is_ticket_user_or_author)
rules.add_perm('backend.change_ticket', is_ticket_user_or_author)
rules.add_perm('backend.delete_ticket', is_ticket_user_or_author)

# Folder rules

# Check if user / group has direct permission specified in folder
@rules.predicate
def has_direct_permission(user, node):

    # Check if user is specified in any of folders permissions
    if user in node.users.all():
        return True

    # Check all user groups and see if any of them is specified in
    # any of folders permissions
    for group in user.groups.all():
        if group in node.groups.all():
            return True

    return False


# Check if user / group has inhereted permissions to a folder
@rules.predicate
def has_inherited_permission(user, node):
    # check if user / group specified directly on this node
    if has_direct_permission(user, node):
        return True

    # check if user / group is specified on any ancestor
    for n in node.get_ancestors(ascending=True):
        if has_direct_permission(user, n):
            return True


rules.add_rule('has_direct_permission', has_direct_permission)
rules.add_rule('has_inherited_permission', has_inherited_permission)
