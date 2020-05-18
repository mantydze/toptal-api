""" Entry point of an API """

from app import create_app, db

application = create_app()

create_dummy_database = False

if application.config["DEBUG"] and create_dummy_database:

    import random
    import datetime
    from app.modules.users.models import User
    from app.modules.runs.models import Run
    from app.utils.roles import Role

    with application.app_context():
        db.drop_all()
        db.create_all()

        for role in Role.roles():
            for uid in range(1, 11):
                user_data = {"username": "{}{}".format(role, uid),
                             "password": "password{}".format(uid)}
                user = User.create(user_data)

                for rid in range(1, uid+1):
                    run_data = {
                        "user_id": user.user_id,
                        "date": datetime.date.today().isoformat(),
                        "duration": random.randint(100, 1000),
                        "distance": random.randint(100, 1000),
                        "latitude": 54.687157,
                        "longitude": 25.279652
                    }
                    Run.create(run_data)

            # Default role is USER, set MANAGER and ADMIN roles
            db.engine.execute("""
                UPDATE USER
                SET ROLE="{0}"
                WHERE USERNAME LIKE '%{0}%'""".format(role))

if __name__ == "__main__":
    application.run(debug=application.config.get("DEBUG", "True"),
                    host=application.config.get("HOST", "0.0.0.0"),
                    port=application.config.get("PORT", "4567"),
                    threaded=True)
