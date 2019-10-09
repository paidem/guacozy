import rules


@rules.predicate
def is_owner(user, obj):
    if obj is None:
        return True
    return obj.owner == user


rules.add_perm('backend.add_personalnamedcredentials', is_owner)
rules.add_perm('backend.view_personalnamedcredentials', is_owner)
rules.add_perm('backend.change_personalnamedcredentials', is_owner)
rules.add_perm('backend.delete_personalnamedcredentials', is_owner)
rules.add_perm('backend.personalnamedcredentials', is_owner)
