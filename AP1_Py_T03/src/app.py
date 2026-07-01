from di.container import Container
from web.module.app_module import create_app


container = Container()
app = create_app(container)


if __name__ == "__main__":
    app.run(debug=True)
