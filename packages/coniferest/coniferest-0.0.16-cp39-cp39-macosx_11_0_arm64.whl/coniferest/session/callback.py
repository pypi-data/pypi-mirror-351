import webbrowser

import click

from coniferest.datasets import Label


def prompt_decision_callback(metadata, data, session) -> Label:
    """
    Prompt user to label the object as anomaly or regular.

    If user sends keyboard interrupt, terminate the session.
    """
    try:
        result = click.confirm(f"Is {metadata} anomaly?")
        return Label.ANOMALY if result else Label.REGULAR

    except click.Abort:
        session.terminate()
        return Label.UNKNOWN


def viewer_decision_callback(metadata, data, session) -> Label:
    """
    Open SNAD Viewer for ZTF DR object. Metadata must be ZTF DR object ID.
    """
    url = "https://ztf.snad.space/view/{}".format(metadata)

    try:
        webbrowser.get().open_new_tab(url)
    except webbrowser.Error:
        click.echo("Check {} for details".format(url))

    return prompt_decision_callback(metadata, data, session)


class TerminateAfter:
    """
    Terminate session after given number of iterations.

    This callback to be used as "on decision callback":
    Session(..., on_decision_callbacks=[TerminateAfter(budget)])

    Parameters
    ----------
    budget : int
        Number of iterations after which session will be terminated.
    """

    def __init__(self, budget: int):
        self.budget = budget
        self.iteration = 0

    def __call__(self, metadata, data, session) -> None:
        self.iteration += 1
        if self.iteration >= self.budget:
            session.terminate()


class TerminateAfterNAnomalies:
    """
    Terminate session after given number of newly labeled anomalies.

    This callback to be used as "on decision callback":
    Session(..., on_decision_callbacks=[TerminateAfter(budget)])

    Parameters
    ----------
    budget : int
        Number of anomalies to stop after.
    """

    def __init__(self, budget: int):
        self.budget = budget
        self.anomalies_count = 0

    def __call__(self, label, _data, session) -> None:
        self.anomalies_count += label == Label.ANOMALY
        if self.anomalies_count >= self.budget:
            session.terminate()
