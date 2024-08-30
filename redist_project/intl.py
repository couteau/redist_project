from qgis.PyQt.QtCore import QCoreApplication


def tr(message):
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('redistricting', message)
