def has_role(user, role_type):
    return user.user_role.filter(role__role_type=role_type).exists()
