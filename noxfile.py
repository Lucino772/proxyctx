import nox


@nox.session(python=["3.7", "3.8", "3.9"])
def tests(session: nox.Session):
    session.install("-r", "requirements/requirements-tests.txt")
    session.install(".")
    session.run("pytest")


@nox.session
def lint(session: nox.Session):
    session.install("pre-commit")
    session.run("pre-commit", "run", *session.posargs)


@nox.session
def build(session: nox.Session):
    session.install("build")
    session.run("python", "-m", "build")
