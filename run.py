""" Entry point of an API """

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=application.config.get("DEBUG", "True"),
                    host=application.config.get("HOST", "0.0.0.0"),
                    port=application.config.get("PORT", "4567"),
                    threaded=True)
