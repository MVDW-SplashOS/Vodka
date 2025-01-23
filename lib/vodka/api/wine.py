from ..util import createAPIResponse
from ..manager import VodkaManager


def WineInstallVersion(version):
    try:
        manager = VodkaManager()
        success = manager.install_version(version)
        if success:
            return createAPIResponse(200, {"version": version})
        else:
            return createAPIResponse(409, None, "Version already installed")
    except Exception as e:
        return createAPIResponse(500, None, str(e))


def WineGetInstalled():
    try:
        manager = VodkaManager()
        versions = manager.get_versions()
        return createAPIResponse(200, {"versions": versions})
    except Exception as e:
        return createAPIResponse(500, None, str(e))


def WineRefreshVersionList():
    try:
        manager = VodkaManager()
        manager.download_versions()
        return createAPIResponse(200)
    except Exception as e:
        return createAPIResponse(500, None, str(e))
