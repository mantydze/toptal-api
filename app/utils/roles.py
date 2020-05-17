""" utils/roles.py """


class Role():

    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

    @staticmethod
    def roles():
        """ Returns list of roles available """
        return [Role.USER, Role.MANAGER, Role.ADMIN]
