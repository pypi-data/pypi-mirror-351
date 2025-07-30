import nox

@nox.session(python=["3.11", "3.12", "3.13"])
def tests(session):
    session.run("uv", "sync", "--active", "-q", external=True)
    session.run("pytest")
