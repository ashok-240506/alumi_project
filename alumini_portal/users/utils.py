def has_role(user, role_name):
    print("Checking role for:", user)
    roles = user.user_role.all()
    print("User roles:", [r.role.role_name for r in roles])
    return user.user_role.filter(role__role_name__iexact=role_name).exists()

