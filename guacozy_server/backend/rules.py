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

