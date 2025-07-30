# coding: UTF-8
import sys
bstack1111l_opy_ = sys.version_info [0] == 2
bstack1ll1l11_opy_ = 2048
bstack11ll1l1_opy_ = 7
def bstack1l1_opy_ (bstack1l1l1l1_opy_):
    global bstack1lll111_opy_
    bstack11l1l11_opy_ = ord (bstack1l1l1l1_opy_ [-1])
    bstack11ll1ll_opy_ = bstack1l1l1l1_opy_ [:-1]
    bstack1llllll1_opy_ = bstack11l1l11_opy_ % len (bstack11ll1ll_opy_)
    bstack1l1l_opy_ = bstack11ll1ll_opy_ [:bstack1llllll1_opy_] + bstack11ll1ll_opy_ [bstack1llllll1_opy_:]
    if bstack1111l_opy_:
        bstack1l111_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll1l11_opy_ - (bstack1ll1ll_opy_ + bstack11l1l11_opy_) % bstack11ll1l1_opy_) for bstack1ll1ll_opy_, char in enumerate (bstack1l1l_opy_)])
    else:
        bstack1l111_opy_ = str () .join ([chr (ord (char) - bstack1ll1l11_opy_ - (bstack1ll1ll_opy_ + bstack11l1l11_opy_) % bstack11ll1l1_opy_) for bstack1ll1ll_opy_, char in enumerate (bstack1l1l_opy_)])
    return eval (bstack1l111_opy_)
import atexit
import datetime
import inspect
import logging
import signal
import threading
from uuid import uuid4
from bstack_utils.measure import bstack11l11l111l_opy_
from bstack_utils.percy_sdk import PercySDK
import pytest
from packaging import version
from browserstack_sdk.__init__ import (bstack1lll1l1l1_opy_, bstack11ll111ll1_opy_, update, bstack111l1111l_opy_,
                                       bstack1llll1l11_opy_, bstack11llll111_opy_, bstack11llll111l_opy_, bstack1ll111lll_opy_,
                                       bstack1ll11l11ll_opy_, bstack1ll1l1l11l_opy_, bstack111llll1l_opy_,
                                       bstack1ll11lll1_opy_, getAccessibilityResults, getAccessibilityResultsSummary, perform_scan, bstack111ll111l_opy_)
from browserstack_sdk.bstack1ll111111_opy_ import bstack1l1l1lll11_opy_
from browserstack_sdk._version import __version__
from bstack_utils import bstack1l11lllll_opy_
from bstack_utils.capture import bstack111lllllll_opy_
from bstack_utils.config import Config
from bstack_utils.percy import *
from bstack_utils.constants import bstack1l1ll11l1l_opy_, bstack11lll1l11_opy_, bstack11llll11_opy_, \
    bstack1lll111l11_opy_
from bstack_utils.helper import bstack1l11l1l1_opy_, bstack11llll111l1_opy_, bstack111l1111l1_opy_, bstack1111111ll_opy_, bstack1ll111l1111_opy_, bstack11111l1l1_opy_, \
    bstack11llll1l111_opy_, \
    bstack11ll11l111l_opy_, bstack1l1lll11_opy_, bstack1ll1l1ll11_opy_, bstack11ll1ll111l_opy_, bstack1ll11ll1_opy_, Notset, \
    bstack11llll1l1_opy_, bstack11ll1l1l1l1_opy_, bstack11l1llll1l1_opy_, Result, bstack11lll1111l1_opy_, bstack11ll111l1l1_opy_, bstack111l11l111_opy_, \
    bstack1l11ll11l1_opy_, bstack1llll1l1l_opy_, bstack11l1l11l11_opy_, bstack11ll111llll_opy_
from bstack_utils.bstack11l1111ll1l_opy_ import bstack11l111l1l11_opy_
from bstack_utils.messages import bstack1l1l11ll11_opy_, bstack1lllll1l1l_opy_, bstack1l1l1l1l1_opy_, bstack1ll1l1lll1_opy_, bstack11l1ll11l1_opy_, \
    bstack1l1l11l1_opy_, bstack11lll111ll_opy_, bstack11lllll1ll_opy_, bstack11l11lll1_opy_, bstack1lll111l_opy_, \
    bstack1llll1l1ll_opy_, bstack1lll11l1_opy_
from bstack_utils.proxy import bstack11l1l1lll1_opy_, bstack1l1l111ll_opy_
from bstack_utils.bstack1lll111l1_opy_ import bstack111l111l1l1_opy_, bstack111l1111l1l_opy_, bstack111l111ll11_opy_, bstack111l111111l_opy_, \
    bstack111l111l11l_opy_, bstack111l111l111_opy_, bstack111l111l1ll_opy_, bstack1l1l1l1ll_opy_, bstack111l11111ll_opy_
from bstack_utils.bstack11l1lll1ll_opy_ import bstack1l1111l11l_opy_
from bstack_utils.bstack1ll11l1ll_opy_ import bstack1l11l1l1l_opy_, bstack1l1l1llll_opy_, bstack11l11llll1_opy_, \
    bstack1l111llll1_opy_, bstack11lll1111_opy_
from bstack_utils.bstack111lll1ll1_opy_ import bstack111lllll11_opy_
from bstack_utils.bstack111lll1111_opy_ import bstack1l1111l1l1_opy_
import bstack_utils.accessibility as bstack1111111l1_opy_
from bstack_utils.bstack11l111111l_opy_ import bstack1ll11llll_opy_
from bstack_utils.bstack11l11l1lll_opy_ import bstack11l11l1lll_opy_
from browserstack_sdk.__init__ import bstack1l1l111ll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1llll_opy_ import bstack1llll1l11ll_opy_
from browserstack_sdk.sdk_cli.bstack1l11111lll_opy_ import bstack1l11111lll_opy_, bstack1ll111ll1_opy_, bstack11l11lllll_opy_
from browserstack_sdk.sdk_cli.test_framework import bstack1l11ll1l1l1_opy_, bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1l11111lll_opy_ import bstack1l11111lll_opy_, bstack1ll111ll1_opy_, bstack11l11lllll_opy_
bstack1ll11111_opy_ = None
bstack11lllll11l_opy_ = None
bstack1lll1ll1_opy_ = None
bstack11llllllll_opy_ = None
bstack11l1ll1l1_opy_ = None
bstack11111111l_opy_ = None
bstack111ll11l1_opy_ = None
bstack11lll1l111_opy_ = None
bstack1ll1111l1_opy_ = None
bstack1lll111ll1_opy_ = None
bstack11ll1l1111_opy_ = None
bstack1lll111lll_opy_ = None
bstack1l111111ll_opy_ = None
bstack1ll1lll11_opy_ = bstack1l1_opy_ (u"ࠨࠩ‛")
CONFIG = {}
bstack11ll1llll_opy_ = False
bstack1l111l11_opy_ = bstack1l1_opy_ (u"ࠩࠪ“")
bstack1l11ll1111_opy_ = bstack1l1_opy_ (u"ࠪࠫ”")
bstack11lllll1l_opy_ = False
bstack11l11111l_opy_ = []
bstack1lllllll11_opy_ = bstack1l1ll11l1l_opy_
bstack111111lll11_opy_ = bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ„")
bstack11lll11111_opy_ = {}
bstack1ll1ll111_opy_ = None
bstack1l1lll1l1l_opy_ = False
logger = bstack1l11lllll_opy_.get_logger(__name__, bstack1lllllll11_opy_)
store = {
    bstack1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡨࡰࡱ࡮ࡣࡺࡻࡩࡥࠩ‟"): []
}
bstack111111l1111_opy_ = False
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_111ll111l1_opy_ = {}
current_test_uuid = None
cli_context = bstack1l11ll1l1l1_opy_(
    test_framework_name=bstack1l1ll1l1l_opy_[bstack1l1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠳ࡂࡅࡆࠪ†")] if bstack1ll11ll1_opy_() else bstack1l1ll1l1l_opy_[bstack1l1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚ࠧ‡")],
    test_framework_version=pytest.__version__,
    platform_index=-1,
)
def bstack11l1l1lll_opy_(page, bstack1l1l1l1lll_opy_):
    try:
        page.evaluate(bstack1l1_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤ•"),
                      bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨ࡮ࡢ࡯ࡨࠦ࠿࠭‣") + json.dumps(
                          bstack1l1l1l1lll_opy_) + bstack1l1_opy_ (u"ࠥࢁࢂࠨ․"))
    except Exception as e:
        print(bstack1l1_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡻࡾࠤ‥"), e)
def bstack1llll1ll11_opy_(page, message, level):
    try:
        page.evaluate(bstack1l1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨ…"), bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫ‧") + json.dumps(
            message) + bstack1l1_opy_ (u"ࠧ࠭ࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠪ ") + json.dumps(level) + bstack1l1_opy_ (u"ࠨࡿࢀࠫ "))
    except Exception as e:
        print(bstack1l1_opy_ (u"ࠤࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠥࡧ࡮࡯ࡱࡷࡥࡹ࡯࡯࡯ࠢࡾࢁࠧ‪"), e)
def pytest_configure(config):
    global bstack1l111l11_opy_
    global CONFIG
    bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
    config.args = bstack1l1111l1l1_opy_.bstack11111l1ll11_opy_(config.args)
    bstack1ll11l111l_opy_.bstack1ll11lll11_opy_(bstack11l1l11l11_opy_(config.getoption(bstack1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧ‫"))))
    try:
        bstack1l11lllll_opy_.bstack11l1111l11l_opy_(config.inipath, config.rootpath)
    except:
        pass
    if cli.is_running():
        bstack1l11111lll_opy_.invoke(bstack1ll111ll1_opy_.CONNECT, bstack11l11lllll_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫ‬"), bstack1l1_opy_ (u"ࠬ࠶ࠧ‭")))
        config = json.loads(os.environ.get(bstack1l1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡏࡏࡈࡌࡋࠧ‮"), bstack1l1_opy_ (u"ࠢࡼࡿࠥ ")))
        cli.bstack1ll1lll11ll_opy_(bstack1ll1l1ll11_opy_(bstack1l111l11_opy_, CONFIG), cli_context.platform_index, bstack111l1111l_opy_)
    if cli.bstack1ll1llll1ll_opy_(bstack1llll1l11ll_opy_):
        cli.bstack1ll1lll1l1l_opy_()
        logger.debug(bstack1l1_opy_ (u"ࠣࡅࡏࡍࠥ࡯ࡳࠡࡣࡦࡸ࡮ࡼࡥࠡࡨࡲࡶࠥࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࡃࠢ‰") + str(cli_context.platform_index) + bstack1l1_opy_ (u"ࠤࠥ‱"))
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.BEFORE_ALL, bstack1lllll1111l_opy_.PRE, config)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    when = getattr(call, bstack1l1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣ′"), None)
    if cli.is_running() and when == bstack1l1_opy_ (u"ࠦࡨࡧ࡬࡭ࠤ″"):
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.LOG_REPORT, bstack1lllll1111l_opy_.PRE, item, call)
    outcome = yield
    if cli.is_running():
        if when == bstack1l1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦ‴"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.BEFORE_EACH, bstack1lllll1111l_opy_.POST, item, call, outcome)
        elif when == bstack1l1_opy_ (u"ࠨࡣࡢ࡮࡯ࠦ‵"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.LOG_REPORT, bstack1lllll1111l_opy_.POST, item, call, outcome)
        elif when == bstack1l1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤ‶"):
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.AFTER_EACH, bstack1lllll1111l_opy_.POST, item, call, outcome)
        return # skip all existing bstack1111111lll1_opy_
    skipSessionName = item.config.getoption(bstack1l1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ‷"))
    plugins = item.config.getoption(bstack1l1_opy_ (u"ࠤࡳࡰࡺ࡭ࡩ࡯ࡵࠥ‸"))
    report = outcome.get_result()
    os.environ[bstack1l1_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖࡢࡘࡊ࡙ࡔࡠࡐࡄࡑࡊ࠭‹")] = report.nodeid
    bstack11111l11l11_opy_(item, call, report)
    if bstack1l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡳࡰࡺ࡭ࡩ࡯ࠤ›") not in plugins or bstack1ll11ll1_opy_():
        return
    summary = []
    driver = getattr(item, bstack1l1_opy_ (u"ࠧࡥࡤࡳ࡫ࡹࡩࡷࠨ※"), None)
    page = getattr(item, bstack1l1_opy_ (u"ࠨ࡟ࡱࡣࡪࡩࠧ‼"), None)
    try:
        if (driver == None or driver.session_id == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None or cli.is_running()):
        bstack111111l1lll_opy_(item, report, summary, skipSessionName)
    if (page is not None):
        bstack11111l1111l_opy_(item, report, summary, skipSessionName)
def bstack111111l1lll_opy_(item, report, summary, skipSessionName):
    if report.when == bstack1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭‽") and report.skipped:
        bstack111l11111ll_opy_(report)
    if report.when in [bstack1l1_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢ‾"), bstack1l1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦ‿")]:
        return
    if not bstack1ll111l1111_opy_():
        return
    try:
        if ((str(skipSessionName).lower() != bstack1l1_opy_ (u"ࠪࡸࡷࡻࡥࠨ⁀")) and (not cli.is_running())) and item._driver.session_id:
            item._driver.execute_script(
                bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩ⁁") + json.dumps(
                    report.nodeid) + bstack1l1_opy_ (u"ࠬࢃࡽࠨ⁂"))
        os.environ[bstack1l1_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙ࡥࡔࡆࡕࡗࡣࡓࡇࡍࡆࠩ⁃")] = report.nodeid
    except Exception as e:
        summary.append(
            bstack1l1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦ࠼ࠣࡿ࠵ࢃࠢ⁄").format(e)
        )
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1_opy_ (u"ࠣࡹࡤࡷࡽ࡬ࡡࡪ࡮ࠥ⁅")))
    bstack11l11ll1l1_opy_ = bstack1l1_opy_ (u"ࠤࠥ⁆")
    bstack111l11111ll_opy_(report)
    if not passed:
        try:
            bstack11l11ll1l1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1_opy_ (u"࡛ࠥࡆࡘࡎࡊࡐࡊ࠾ࠥࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤ࡫ࡧࡩ࡭ࡷࡵࡩࠥࡸࡥࡢࡵࡲࡲ࠿ࠦࡻ࠱ࡿࠥ⁇").format(e)
            )
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack11l11ll1l1_opy_))
    if not report.skipped:
        passed = report.passed or (report.failed and hasattr(report, bstack1l1_opy_ (u"ࠦࡼࡧࡳࡹࡨࡤ࡭ࡱࠨ⁈")))
        bstack11l11ll1l1_opy_ = bstack1l1_opy_ (u"ࠧࠨ⁉")
        if not passed:
            try:
                bstack11l11ll1l1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡩ࡫ࡴࡦࡴࡰ࡭ࡳ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥࠡࡴࡨࡥࡸࡵ࡮࠻ࠢࡾ࠴ࢂࠨ⁊").format(e)
                )
            try:
                if (threading.current_thread().bstackTestErrorMessages == None):
                    threading.current_thread().bstackTestErrorMessages = []
            except Exception as e:
                threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(str(bstack11l11ll1l1_opy_))
        try:
            if passed:
                item._driver.execute_script(
                    bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣ࠮ࠣࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡨࡦࡺࡡࠣ࠼ࠣࠫ⁋")
                    + json.dumps(bstack1l1_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠢࠤ⁌"))
                    + bstack1l1_opy_ (u"ࠤ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࠧ⁍")
                )
            else:
                item._driver.execute_script(
                    bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡥࡳࡴࡲࡶࠧ࠲ࠠ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢࡥࡣࡷࡥࠧࡀࠠࠨ⁎")
                    + json.dumps(str(bstack11l11ll1l1_opy_))
                    + bstack1l1_opy_ (u"ࠦࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢃࠢ⁏")
                )
        except Exception as e:
            summary.append(bstack1l1_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡥࡳࡴ࡯ࡵࡣࡷࡩ࠿ࠦࡻ࠱ࡿࠥ⁐").format(e))
def bstack11111l11l1l_opy_(test_name, error_message):
    try:
        bstack1111111ll11_opy_ = []
        bstack11l111l1l1_opy_ = os.environ.get(bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭⁑"), bstack1l1_opy_ (u"ࠧ࠱ࠩ⁒"))
        bstack1l1ll11ll_opy_ = {bstack1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭⁓"): test_name, bstack1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ⁔"): error_message, bstack1l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ⁕"): bstack11l111l1l1_opy_}
        bstack111111l1l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠫࡵࡽ࡟ࡱࡻࡷࡩࡸࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩ⁖"))
        if os.path.exists(bstack111111l1l1l_opy_):
            with open(bstack111111l1l1l_opy_) as f:
                bstack1111111ll11_opy_ = json.load(f)
        bstack1111111ll11_opy_.append(bstack1l1ll11ll_opy_)
        with open(bstack111111l1l1l_opy_, bstack1l1_opy_ (u"ࠬࡽࠧ⁗")) as f:
            json.dump(bstack1111111ll11_opy_, f)
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡲࡨࡶࡸ࡯ࡳࡵ࡫ࡱ࡫ࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡳࡽࡹ࡫ࡳࡵࠢࡨࡶࡷࡵࡲࡴ࠼ࠣࠫ⁘") + str(e))
def bstack11111l1111l_opy_(item, report, summary, skipSessionName):
    if report.when in [bstack1l1_opy_ (u"ࠢࡴࡧࡷࡹࡵࠨ⁙"), bstack1l1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࠥ⁚")]:
        return
    if (str(skipSessionName).lower() != bstack1l1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ⁛")):
        bstack11l1l1lll_opy_(item._page, report.nodeid)
    passed = report.passed or report.skipped or (report.failed and hasattr(report, bstack1l1_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧ⁜")))
    bstack11l11ll1l1_opy_ = bstack1l1_opy_ (u"ࠦࠧ⁝")
    bstack111l11111ll_opy_(report)
    if not report.skipped:
        if not passed:
            try:
                bstack11l11ll1l1_opy_ = report.longrepr.reprcrash
            except Exception as e:
                summary.append(
                    bstack1l1_opy_ (u"ࠧ࡝ࡁࡓࡐࡌࡒࡌࡀࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡨࡪࡺࡥࡳ࡯࡬ࡲࡪࠦࡦࡢ࡫࡯ࡹࡷ࡫ࠠࡳࡧࡤࡷࡴࡴ࠺ࠡࡽ࠳ࢁࠧ⁞").format(e)
                )
        try:
            if passed:
                bstack11lll1111_opy_(getattr(item, bstack1l1_opy_ (u"࠭࡟ࡱࡣࡪࡩࠬ "), None), bstack1l1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢ⁠"))
            else:
                error_message = bstack1l1_opy_ (u"ࠨࠩ⁡")
                if bstack11l11ll1l1_opy_:
                    bstack1llll1ll11_opy_(item._page, str(bstack11l11ll1l1_opy_), bstack1l1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ⁢"))
                    bstack11lll1111_opy_(getattr(item, bstack1l1_opy_ (u"ࠪࡣࡵࡧࡧࡦࠩ⁣"), None), bstack1l1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ⁤"), str(bstack11l11ll1l1_opy_))
                    error_message = str(bstack11l11ll1l1_opy_)
                else:
                    bstack11lll1111_opy_(getattr(item, bstack1l1_opy_ (u"ࠬࡥࡰࡢࡩࡨࠫ⁥"), None), bstack1l1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ⁦"))
                bstack11111l11l1l_opy_(report.nodeid, error_message)
        except Exception as e:
            summary.append(bstack1l1_opy_ (u"ࠢࡘࡃࡕࡒࡎࡔࡇ࠻ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡻࡰࡥࡣࡷࡩࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼ࠲ࢀࠦ⁧").format(e))
def pytest_addoption(parser):
    parser.addoption(bstack1l1_opy_ (u"ࠣ࠯࠰ࡷࡰ࡯ࡰࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ⁨"), default=bstack1l1_opy_ (u"ࠤࡉࡥࡱࡹࡥࠣ⁩"), help=bstack1l1_opy_ (u"ࠥࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡨࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠤ⁪"))
    parser.addoption(bstack1l1_opy_ (u"ࠦ࠲࠳ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ⁫"), default=bstack1l1_opy_ (u"ࠧࡌࡡ࡭ࡵࡨࠦ⁬"), help=bstack1l1_opy_ (u"ࠨࡁࡶࡶࡲࡱࡦࡺࡩࡤࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠧ⁭"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1l1_opy_ (u"ࠢ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠤ⁮"), action=bstack1l1_opy_ (u"ࠣࡵࡷࡳࡷ࡫ࠢ⁯"), default=bstack1l1_opy_ (u"ࠤࡦ࡬ࡷࡵ࡭ࡦࠤ⁰"),
                         help=bstack1l1_opy_ (u"ࠥࡈࡷ࡯ࡶࡦࡴࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴࠤⁱ"))
def bstack111lll1lll_opy_(log):
    if not (log[bstack1l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⁲")] and log[bstack1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭⁳")].strip()):
        return
    active = bstack111lll11l1_opy_()
    log = {
        bstack1l1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⁴"): log[bstack1l1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭⁵")],
        bstack1l1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ⁶"): bstack111l1111l1_opy_().isoformat() + bstack1l1_opy_ (u"ࠩ࡝ࠫ⁷"),
        bstack1l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ⁸"): log[bstack1l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ⁹")],
    }
    if active:
        if active[bstack1l1_opy_ (u"ࠬࡺࡹࡱࡧࠪ⁺")] == bstack1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ⁻"):
            log[bstack1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⁼")] = active[bstack1l1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⁽")]
        elif active[bstack1l1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ⁾")] == bstack1l1_opy_ (u"ࠪࡸࡪࡹࡴࠨⁿ"):
            log[bstack1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ₀")] = active[bstack1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ₁")]
    bstack1ll11llll_opy_.bstack1ll1ll11l1_opy_([log])
def bstack111lll11l1_opy_():
    if len(store[bstack1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ₂")]) > 0 and store[bstack1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ₃")][-1]:
        return {
            bstack1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭₄"): bstack1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ₅"),
            bstack1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ₆"): store[bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ₇")][-1]
        }
    if store.get(bstack1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ₈"), None):
        return {
            bstack1l1_opy_ (u"࠭ࡴࡺࡲࡨࠫ₉"): bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࠬ₊"),
            bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ₋"): store[bstack1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭₌")]
        }
    return None
def pytest_runtest_logstart(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.INIT_TEST, bstack1lllll1111l_opy_.PRE, nodeid, location)
def pytest_runtest_logfinish(nodeid, location):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.INIT_TEST, bstack1lllll1111l_opy_.POST, nodeid, location)
def pytest_runtest_call(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.PRE, item)
        return
    try:
        global CONFIG
        item._111111ll1ll_opy_ = True
        bstack11ll1ll11_opy_ = bstack1111111l1_opy_.bstack11l1l1111l_opy_(bstack11ll11l111l_opy_(item.own_markers))
        if not cli.bstack1ll1llll1ll_opy_(bstack1llll1l11ll_opy_):
            item._a11y_test_case = bstack11ll1ll11_opy_
            if bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ₍"), None):
                driver = getattr(item, bstack1l1_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ₎"), None)
                item._a11y_started = bstack1111111l1_opy_.bstack1lll11111l_opy_(driver, bstack11ll1ll11_opy_)
        if not bstack1ll11llll_opy_.on() or bstack111111lll11_opy_ != bstack1l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ₏"):
            return
        global current_test_uuid #, bstack11l1111111_opy_
        bstack111l1l11l1_opy_ = {
            bstack1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫₐ"): uuid4().__str__(),
            bstack1l1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫₑ"): bstack111l1111l1_opy_().isoformat() + bstack1l1_opy_ (u"ࠨ࡜ࠪₒ")
        }
        current_test_uuid = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧₓ")]
        store[bstack1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠧₔ")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠫࡺࡻࡩࡥࠩₕ")]
        threading.current_thread().current_test_uuid = current_test_uuid
        _111ll111l1_opy_[item.nodeid] = {**_111ll111l1_opy_[item.nodeid], **bstack111l1l11l1_opy_}
        bstack111111ll11l_opy_(item, _111ll111l1_opy_[item.nodeid], bstack1l1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ₖ"))
    except Exception as err:
        print(bstack1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡸࡵ࡯ࡶࡨࡷࡹࡥࡣࡢ࡮࡯࠾ࠥࢁࡽࠨₗ"), str(err))
def pytest_runtest_setup(item):
    store[bstack1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡩࡵࡧࡰࠫₘ")] = item
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.BEFORE_EACH, bstack1lllll1111l_opy_.PRE, item, bstack1l1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧₙ"))
        return # skip all existing bstack1111111lll1_opy_
    global bstack111111l1111_opy_
    threading.current_thread().percySessionName = item.nodeid
    if bstack11ll1ll111l_opy_():
        atexit.register(bstack1l1ll111l1_opy_)
        if not bstack111111l1111_opy_:
            try:
                bstack111111ll111_opy_ = [signal.SIGINT, signal.SIGTERM]
                if not bstack11ll111llll_opy_():
                    bstack111111ll111_opy_.extend([signal.SIGHUP, signal.SIGQUIT])
                for s in bstack111111ll111_opy_:
                    signal.signal(s, bstack111111lllll_opy_)
                bstack111111l1111_opy_ = True
            except Exception as e:
                logger.debug(
                    bstack1l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡷ࡫ࡧࡪࡵࡷࡩࡷࠦࡳࡪࡩࡱࡥࡱࠦࡨࡢࡰࡧࡰࡪࡸࡳ࠻ࠢࠥₚ") + str(e))
        try:
            item.config.hook.pytest_selenium_runtest_makereport = bstack111l111l1l1_opy_
        except Exception as err:
            threading.current_thread().testStatus = bstack1l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪₛ")
    try:
        if not bstack1ll11llll_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack111l1l11l1_opy_ = {
            bstack1l1_opy_ (u"ࠫࡺࡻࡩࡥࠩₜ"): uuid,
            bstack1l1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩ₝"): bstack111l1111l1_opy_().isoformat() + bstack1l1_opy_ (u"࡚࠭ࠨ₞"),
            bstack1l1_opy_ (u"ࠧࡵࡻࡳࡩࠬ₟"): bstack1l1_opy_ (u"ࠨࡪࡲࡳࡰ࠭₠"),
            bstack1l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ₡"): bstack1l1_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨ₢"),
            bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡱࡥࡲ࡫ࠧ₣"): bstack1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫ₤")
        }
        threading.current_thread().current_hook_uuid = uuid
        threading.current_thread().current_test_item = item
        store[bstack1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ₥")] = item
        store[bstack1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ₦")] = [uuid]
        if not _111ll111l1_opy_.get(item.nodeid, None):
            _111ll111l1_opy_[item.nodeid] = {bstack1l1_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ₧"): [], bstack1l1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ₨"): []}
        _111ll111l1_opy_[item.nodeid][bstack1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ₩")].append(bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠫࡺࡻࡩࡥࠩ₪")])
        _111ll111l1_opy_[item.nodeid + bstack1l1_opy_ (u"ࠬ࠳ࡳࡦࡶࡸࡴࠬ₫")] = bstack111l1l11l1_opy_
        bstack11111l111l1_opy_(item, bstack111l1l11l1_opy_, bstack1l1_opy_ (u"࠭ࡈࡰࡱ࡮ࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ€"))
    except Exception as err:
        print(bstack1l1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡲࡶࡰࡷࡩࡸࡺ࡟ࡴࡧࡷࡹࡵࡀࠠࡼࡿࠪ₭"), str(err))
def pytest_runtest_teardown(item):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.POST, item)
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.AFTER_EACH, bstack1lllll1111l_opy_.PRE, item, bstack1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ₮"))
        return # skip all existing bstack1111111lll1_opy_
    try:
        global bstack11lll11111_opy_
        bstack11l111l1l1_opy_ = 0
        if bstack11lllll1l_opy_ is True:
            bstack11l111l1l1_opy_ = int(os.environ.get(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ₯")))
        if bstack11lll1l1_opy_.bstack1111lllll_opy_() == bstack1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣ₰"):
            if bstack11lll1l1_opy_.bstack11ll1l1lll_opy_() == bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨ₱"):
                bstack1111111l1l1_opy_ = bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ₲"), None)
                bstack11l1l1l1_opy_ = bstack1111111l1l1_opy_ + bstack1l1_opy_ (u"ࠨ࠭ࡵࡧࡶࡸࡨࡧࡳࡦࠤ₳")
                driver = getattr(item, bstack1l1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨ₴"), None)
                bstack1l111ll11_opy_ = getattr(item, bstack1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭₵"), None)
                bstack1l1l11llll_opy_ = getattr(item, bstack1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ₶"), None)
                PercySDK.screenshot(driver, bstack11l1l1l1_opy_, bstack1l111ll11_opy_=bstack1l111ll11_opy_, bstack1l1l11llll_opy_=bstack1l1l11llll_opy_, bstack1l111111l_opy_=bstack11l111l1l1_opy_)
        if not cli.bstack1ll1llll1ll_opy_(bstack1llll1l11ll_opy_):
            if getattr(item, bstack1l1_opy_ (u"ࠪࡣࡦ࠷࠱ࡺࡡࡶࡸࡦࡸࡴࡦࡦࠪ₷"), False):
                bstack1l1l1lll11_opy_.bstack11ll1l111_opy_(getattr(item, bstack1l1_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬ₸"), None), bstack11lll11111_opy_, logger, item)
        if not bstack1ll11llll_opy_.on():
            return
        bstack111l1l11l1_opy_ = {
            bstack1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪ₹"): uuid4().__str__(),
            bstack1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ₺"): bstack111l1111l1_opy_().isoformat() + bstack1l1_opy_ (u"࡛ࠧࠩ₻"),
            bstack1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭₼"): bstack1l1_opy_ (u"ࠩ࡫ࡳࡴࡱࠧ₽"),
            bstack1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡶࡼࡴࡪ࠭₾"): bstack1l1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ₿"),
            bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡲࡦࡳࡥࠨ⃀"): bstack1l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࠨ⃁")
        }
        _111ll111l1_opy_[item.nodeid + bstack1l1_opy_ (u"ࠧ࠮ࡶࡨࡥࡷࡪ࡯ࡸࡰࠪ⃂")] = bstack111l1l11l1_opy_
        bstack11111l111l1_opy_(item, bstack111l1l11l1_opy_, bstack1l1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ⃃"))
    except Exception as err:
        print(bstack1l1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱ࠾ࠥࢁࡽࠨ⃄"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    if bstack111l111111l_opy_(fixturedef.argname):
        store[bstack1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡲࡵࡤࡶ࡮ࡨࡣ࡮ࡺࡥ࡮ࠩ⃅")] = request.node
    elif bstack111l111l11l_opy_(fixturedef.argname):
        store[bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡩ࡬ࡢࡵࡶࡣ࡮ࡺࡥ࡮ࠩ⃆")] = request.node
    if not bstack1ll11llll_opy_.on():
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.SETUP_FIXTURE, bstack1lllll1111l_opy_.PRE, fixturedef, request)
        outcome = yield
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.SETUP_FIXTURE, bstack1lllll1111l_opy_.POST, fixturedef, request, outcome)
        return # skip all existing bstack1111111lll1_opy_
    start_time = datetime.datetime.now()
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.SETUP_FIXTURE, bstack1lllll1111l_opy_.PRE, fixturedef, request)
    outcome = yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.SETUP_FIXTURE, bstack1lllll1111l_opy_.POST, fixturedef, request, outcome)
        return # skip all existing bstack1111111lll1_opy_
    try:
        fixture = {
            bstack1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⃇"): fixturedef.argname,
            bstack1l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭⃈"): bstack11llll1l111_opy_(outcome),
            bstack1l1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩ⃉"): (datetime.datetime.now() - start_time).total_seconds() * 1000
        }
        current_test_item = store[bstack1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ⃊")]
        if not _111ll111l1_opy_.get(current_test_item.nodeid, None):
            _111ll111l1_opy_[current_test_item.nodeid] = {bstack1l1_opy_ (u"ࠩࡩ࡭ࡽࡺࡵࡳࡧࡶࠫ⃋"): []}
        _111ll111l1_opy_[current_test_item.nodeid][bstack1l1_opy_ (u"ࠪࡪ࡮ࡾࡴࡶࡴࡨࡷࠬ⃌")].append(fixture)
    except Exception as err:
        logger.debug(bstack1l1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡾࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡸ࡫ࡴࡶࡲ࠽ࠤࢀࢃࠧ⃍"), str(err))
if bstack1ll11ll1_opy_() and bstack1ll11llll_opy_.on():
    def pytest_bdd_before_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.STEP, bstack1lllll1111l_opy_.PRE, request, step)
            return
        try:
            _111ll111l1_opy_[request.node.nodeid][bstack1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡨࡦࡺࡡࠨ⃎")].bstack1lll11l11l_opy_(id(step))
        except Exception as err:
            print(bstack1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡨࡤࡥࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶ࠺ࠡࡽࢀࠫ⃏"), str(err))
    def pytest_bdd_step_error(request, step, exception):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.STEP, bstack1lllll1111l_opy_.POST, request, step, exception)
            return
        try:
            _111ll111l1_opy_[request.node.nodeid][bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⃐")].bstack111lllll1l_opy_(id(step), Result.failed(exception=exception))
        except Exception as err:
            print(bstack1l1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡣࡦࡧࡣࡸࡺࡥࡱࡡࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠬ⃑"), str(err))
    def pytest_bdd_after_step(request, step):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.STEP, bstack1lllll1111l_opy_.POST, request, step)
            return
        try:
            bstack111lll1ll1_opy_: bstack111lllll11_opy_ = _111ll111l1_opy_[request.node.nodeid][bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥ⃒ࠬ")]
            bstack111lll1ll1_opy_.bstack111lllll1l_opy_(id(step), Result.passed())
        except Exception as err:
            print(bstack1l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡳࡵࡧࡳࡣࡪࡸࡲࡰࡴ࠽ࠤࢀࢃ⃓ࠧ"), str(err))
    def pytest_bdd_before_scenario(request, feature, scenario):
        global bstack111111lll11_opy_
        try:
            if not bstack1ll11llll_opy_.on() or bstack111111lll11_opy_ != bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠨ⃔"):
                return
            if cli.is_running():
                cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.PRE, request, feature, scenario)
                return
            driver = bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫ⃕"), None)
            if not _111ll111l1_opy_.get(request.node.nodeid, None):
                _111ll111l1_opy_[request.node.nodeid] = {}
            bstack111lll1ll1_opy_ = bstack111lllll11_opy_.bstack1111l1l1lll_opy_(
                scenario, feature, request.node,
                name=bstack111l111l111_opy_(request.node, scenario),
                started_at=bstack11111l1l1_opy_(),
                file_path=feature.filename,
                scope=[feature.name],
                framework=bstack1l1_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠳ࡣࡶࡥࡸࡱࡧ࡫ࡲࠨ⃖"),
                tags=bstack111l111l1ll_opy_(feature, scenario),
                bstack111llll1ll_opy_=bstack1ll11llll_opy_.bstack111ll1llll_opy_(driver) if driver and driver.session_id else {}
            )
            _111ll111l1_opy_[request.node.nodeid][bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ⃗")] = bstack111lll1ll1_opy_
            bstack111111ll1l1_opy_(bstack111lll1ll1_opy_.uuid)
            bstack1ll11llll_opy_.bstack111llll11l_opy_(bstack1l1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥ⃘ࠩ"), bstack111lll1ll1_opy_)
        except Exception as err:
            print(bstack1l1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤࡨࡥࡧࡱࡵࡩࡤࡹࡣࡦࡰࡤࡶ࡮ࡵ࠺ࠡࡽࢀ⃙ࠫ"), str(err))
def bstack111111lll1l_opy_(bstack111lll11ll_opy_):
    if bstack111lll11ll_opy_ in store[bstack1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪ⃚ࠧ")]:
        store[bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ⃛")].remove(bstack111lll11ll_opy_)
def bstack111111ll1l1_opy_(test_uuid):
    store[bstack1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ⃜")] = test_uuid
    threading.current_thread().current_test_uuid = test_uuid
@bstack1ll11llll_opy_.bstack1111l11ll1l_opy_
def bstack11111l11l11_opy_(item, call, report):
    logger.debug(bstack1l1_opy_ (u"࠭ࡨࡢࡰࡧࡰࡪࡥ࡯࠲࠳ࡼࡣࡹ࡫ࡳࡵࡡࡨࡺࡪࡴࡴ࠻ࠢࡶࡸࡦࡸࡴࠨ⃝"))
    global bstack111111lll11_opy_
    bstack1lll1lll_opy_ = bstack11111l1l1_opy_()
    if hasattr(report, bstack1l1_opy_ (u"ࠧࡴࡶࡲࡴࠬ⃞")):
        bstack1lll1lll_opy_ = bstack11lll1111l1_opy_(report.stop)
    elif hasattr(report, bstack1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࠧ⃟")):
        bstack1lll1lll_opy_ = bstack11lll1111l1_opy_(report.start)
    try:
        if getattr(report, bstack1l1_opy_ (u"ࠩࡺ࡬ࡪࡴࠧ⃠"), bstack1l1_opy_ (u"ࠪࠫ⃡")) == bstack1l1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ⃢"):
            logger.debug(bstack1l1_opy_ (u"ࠬ࡮ࡡ࡯ࡦ࡯ࡩࡤࡵ࠱࠲ࡻࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺ࠺ࠡࡵࡷࡥࡹ࡫ࠠ࠮ࠢࡾࢁ࠱ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠢ࠰ࠤࢀࢃࠧ⃣").format(getattr(report, bstack1l1_opy_ (u"࠭ࡷࡩࡧࡱࠫ⃤"), bstack1l1_opy_ (u"ࠧࠨ⃥")).__str__(), bstack111111lll11_opy_))
            if bstack111111lll11_opy_ == bstack1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⃦"):
                _111ll111l1_opy_[item.nodeid][bstack1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ⃧")] = bstack1lll1lll_opy_
                bstack111111ll11l_opy_(item, _111ll111l1_opy_[item.nodeid], bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨ⃨ࠬ"), report, call)
                store[bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ⃩")] = None
            elif bstack111111lll11_opy_ == bstack1l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤ⃪"):
                bstack111lll1ll1_opy_ = _111ll111l1_opy_[item.nodeid][bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢ⃫ࠩ")]
                bstack111lll1ll1_opy_.set(hooks=_111ll111l1_opy_[item.nodeid].get(bstack1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ⃬࠭"), []))
                exception, bstack11l1111l1l_opy_ = None, None
                if call.excinfo:
                    exception = call.excinfo.value
                    bstack11l1111l1l_opy_ = [call.excinfo.exconly(), getattr(report, bstack1l1_opy_ (u"ࠨ࡮ࡲࡲ࡬ࡸࡥࡱࡴࡷࡩࡽࡺ⃭ࠧ"), bstack1l1_opy_ (u"⃮ࠩࠪ"))]
                bstack111lll1ll1_opy_.stop(time=bstack1lll1lll_opy_, result=Result(result=getattr(report, bstack1l1_opy_ (u"ࠪࡳࡺࡺࡣࡰ࡯ࡨ⃯ࠫ"), bstack1l1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ⃰")), exception=exception, bstack11l1111l1l_opy_=bstack11l1111l1l_opy_))
                bstack1ll11llll_opy_.bstack111llll11l_opy_(bstack1l1_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ⃱"), _111ll111l1_opy_[item.nodeid][bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ⃲")])
        elif getattr(report, bstack1l1_opy_ (u"ࠧࡸࡪࡨࡲࠬ⃳"), bstack1l1_opy_ (u"ࠨࠩ⃴")) in [bstack1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨ⃵"), bstack1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࠬ⃶")]:
            logger.debug(bstack1l1_opy_ (u"ࠫ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡴࡶࡤࡸࡪࠦ࠭ࠡࡽࢀ࠰ࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࠯ࠣࡿࢂ࠭⃷").format(getattr(report, bstack1l1_opy_ (u"ࠬࡽࡨࡦࡰࠪ⃸"), bstack1l1_opy_ (u"࠭ࠧ⃹")).__str__(), bstack111111lll11_opy_))
            bstack111llll1l1_opy_ = item.nodeid + bstack1l1_opy_ (u"ࠧ࠮ࠩ⃺") + getattr(report, bstack1l1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭⃻"), bstack1l1_opy_ (u"ࠩࠪ⃼"))
            if getattr(report, bstack1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ⃽"), False):
                hook_type = bstack1l1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠩ⃾") if getattr(report, bstack1l1_opy_ (u"ࠬࡽࡨࡦࡰࠪ⃿"), bstack1l1_opy_ (u"࠭ࠧ℀")) == bstack1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭℁") else bstack1l1_opy_ (u"ࠨࡃࡉࡘࡊࡘ࡟ࡆࡃࡆࡌࠬℂ")
                _111ll111l1_opy_[bstack111llll1l1_opy_] = {
                    bstack1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ℃"): uuid4().__str__(),
                    bstack1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ℄"): bstack1lll1lll_opy_,
                    bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧ℅"): hook_type
                }
            _111ll111l1_opy_[bstack111llll1l1_opy_][bstack1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪ℆")] = bstack1lll1lll_opy_
            bstack111111lll1l_opy_(_111ll111l1_opy_[bstack111llll1l1_opy_][bstack1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫℇ")])
            bstack11111l111l1_opy_(item, _111ll111l1_opy_[bstack111llll1l1_opy_], bstack1l1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ℈"), report, call)
            if getattr(report, bstack1l1_opy_ (u"ࠨࡹ࡫ࡩࡳ࠭℉"), bstack1l1_opy_ (u"ࠩࠪℊ")) == bstack1l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩℋ"):
                if getattr(report, bstack1l1_opy_ (u"ࠫࡴࡻࡴࡤࡱࡰࡩࠬℌ"), bstack1l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬℍ")) == bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ℎ"):
                    bstack111l1l11l1_opy_ = {
                        bstack1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬℏ"): uuid4().__str__(),
                        bstack1l1_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬℐ"): bstack11111l1l1_opy_(),
                        bstack1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧℑ"): bstack11111l1l1_opy_()
                    }
                    _111ll111l1_opy_[item.nodeid] = {**_111ll111l1_opy_[item.nodeid], **bstack111l1l11l1_opy_}
                    bstack111111ll11l_opy_(item, _111ll111l1_opy_[item.nodeid], bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫℒ"))
                    bstack111111ll11l_opy_(item, _111ll111l1_opy_[item.nodeid], bstack1l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ℓ"), report, call)
    except Exception as err:
        print(bstack1l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡣࡴ࠷࠱ࡺࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡼࡿࠪ℔"), str(err))
def bstack111111llll1_opy_(test, bstack111l1l11l1_opy_, result=None, call=None, bstack11lllllll1_opy_=None, outcome=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack111lll1ll1_opy_ = {
        bstack1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫℕ"): bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ№")],
        bstack1l1_opy_ (u"ࠨࡶࡼࡴࡪ࠭℗"): bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࠧ℘"),
        bstack1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨℙ"): test.name,
        bstack1l1_opy_ (u"ࠫࡧࡵࡤࡺࠩℚ"): {
            bstack1l1_opy_ (u"ࠬࡲࡡ࡯ࡩࠪℛ"): bstack1l1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ℜ"),
            bstack1l1_opy_ (u"ࠧࡤࡱࡧࡩࠬℝ"): inspect.getsource(test.obj)
        },
        bstack1l1_opy_ (u"ࠨ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ℞"): test.name,
        bstack1l1_opy_ (u"ࠩࡶࡧࡴࡶࡥࠨ℟"): test.name,
        bstack1l1_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ℠"): bstack1l1111l1l1_opy_.bstack111ll1l1l1_opy_(test),
        bstack1l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ℡"): file_path,
        bstack1l1_opy_ (u"ࠬࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠧ™"): file_path,
        bstack1l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭℣"): bstack1l1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨℤ"),
        bstack1l1_opy_ (u"ࠨࡸࡦࡣ࡫࡯࡬ࡦࡲࡤࡸ࡭࠭℥"): file_path,
        bstack1l1_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭Ω"): bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ℧")],
        bstack1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧℨ"): bstack1l1_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸࠬ℩"),
        bstack1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡘࡥࡳࡷࡱࡔࡦࡸࡡ࡮ࠩK"): {
            bstack1l1_opy_ (u"ࠧࡳࡧࡵࡹࡳࡥ࡮ࡢ࡯ࡨࠫÅ"): test.nodeid
        },
        bstack1l1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭ℬ"): bstack11ll11l111l_opy_(test.own_markers)
    }
    if bstack11lllllll1_opy_ in [bstack1l1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡖ࡯࡮ࡶࡰࡦࡦࠪℭ"), bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ℮")]:
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠫࡲ࡫ࡴࡢࠩℯ")] = {
            bstack1l1_opy_ (u"ࠬ࡬ࡩࡹࡶࡸࡶࡪࡹࠧℰ"): bstack111l1l11l1_opy_.get(bstack1l1_opy_ (u"࠭ࡦࡪࡺࡷࡹࡷ࡫ࡳࠨℱ"), [])
        }
    if bstack11lllllll1_opy_ == bstack1l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨℲ"):
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨℳ")] = bstack1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪℴ")
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩℵ")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪℶ")]
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪℷ")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫℸ")]
    if result:
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧℹ")] = result.outcome
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࡢ࡭ࡳࡥ࡭ࡴࠩ℺")] = result.duration * 1000
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧ℻")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨℼ")]
        if result.failed:
            bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪℽ")] = bstack1ll11llll_opy_.bstack1111l11l1l_opy_(call.excinfo.typename)
            bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭ℾ")] = bstack1ll11llll_opy_.bstack1111l11l1l1_opy_(call.excinfo, result)
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬℿ")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡸ࠭⅀")]
    if outcome:
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ⅁")] = bstack11llll1l111_opy_(outcome)
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࡣ࡮ࡴ࡟࡮ࡵࠪ⅂")] = 0
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ⅃")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ⅄")]
        if bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬⅅ")] == bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ⅆ"):
            bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࡠࡶࡼࡴࡪ࠭ⅇ")] = bstack1l1_opy_ (u"ࠨࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠩⅈ")  # bstack1111111l1ll_opy_
            bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪⅉ")] = [{bstack1l1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭⅊"): [bstack1l1_opy_ (u"ࠫࡸࡵ࡭ࡦࠢࡨࡶࡷࡵࡲࠨ⅋")]}]
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ⅌")] = bstack111l1l11l1_opy_[bstack1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡷࠬ⅍")]
    return bstack111lll1ll1_opy_
def bstack111111l11l1_opy_(test, bstack111l11111l_opy_, bstack11lllllll1_opy_, result, call, outcome, bstack11111l11111_opy_):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪⅎ")]
    hook_name = bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠨࡪࡲࡳࡰࡥ࡮ࡢ࡯ࡨࠫ⅏")]
    hook_data = {
        bstack1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ⅐"): bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠪࡹࡺ࡯ࡤࠨ⅑")],
        bstack1l1_opy_ (u"ࠫࡹࡿࡰࡦࠩ⅒"): bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ⅓"),
        bstack1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ⅔"): bstack1l1_opy_ (u"ࠧࡼࡿࠪ⅕").format(bstack111l1111l1l_opy_(hook_name)),
        bstack1l1_opy_ (u"ࠨࡤࡲࡨࡾ࠭⅖"): {
            bstack1l1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࠧ⅗"): bstack1l1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ⅘"),
            bstack1l1_opy_ (u"ࠫࡨࡵࡤࡦࠩ⅙"): None
        },
        bstack1l1_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫ⅚"): test.name,
        bstack1l1_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭⅛"): bstack1l1111l1l1_opy_.bstack111ll1l1l1_opy_(test, hook_name),
        bstack1l1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ⅜"): file_path,
        bstack1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪ⅝"): file_path,
        bstack1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ⅞"): bstack1l1_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫ⅟"),
        bstack1l1_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩⅠ"): file_path,
        bstack1l1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩⅡ"): bstack111l11111l_opy_[bstack1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪⅢ")],
        bstack1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪⅣ"): bstack1l1_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴ࠮ࡥࡸࡧࡺࡳࡢࡦࡴࠪⅤ") if bstack111111lll11_opy_ == bstack1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩ࠭Ⅵ") else bstack1l1_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶࠪⅦ"),
        bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡷࡽࡵ࡫ࠧⅧ"): hook_type
    }
    bstack1111l1lllll_opy_ = bstack111l111ll1_opy_(_111ll111l1_opy_.get(test.nodeid, None))
    if bstack1111l1lllll_opy_:
        hook_data[bstack1l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡪࡦࠪⅨ")] = bstack1111l1lllll_opy_
    if result:
        hook_data[bstack1l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭Ⅹ")] = result.outcome
        hook_data[bstack1l1_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨⅪ")] = result.duration * 1000
        hook_data[bstack1l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭Ⅻ")] = bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧⅬ")]
        if result.failed:
            hook_data[bstack1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩⅭ")] = bstack1ll11llll_opy_.bstack1111l11l1l_opy_(call.excinfo.typename)
            hook_data[bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬⅮ")] = bstack1ll11llll_opy_.bstack1111l11l1l1_opy_(call.excinfo, result)
    if outcome:
        hook_data[bstack1l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬⅯ")] = bstack11llll1l111_opy_(outcome)
        hook_data[bstack1l1_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧⅰ")] = 100
        hook_data[bstack1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬⅱ")] = bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ⅲ")]
        if hook_data[bstack1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩⅳ")] == bstack1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪⅴ"):
            hook_data[bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪⅵ")] = bstack1l1_opy_ (u"࡛ࠬ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷ࠭ⅶ")  # bstack1111111l1ll_opy_
            hook_data[bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧⅷ")] = [{bstack1l1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪⅸ"): [bstack1l1_opy_ (u"ࠨࡵࡲࡱࡪࠦࡥࡳࡴࡲࡶࠬⅹ")]}]
    if bstack11111l11111_opy_:
        hook_data[bstack1l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩⅺ")] = bstack11111l11111_opy_.result
        hook_data[bstack1l1_opy_ (u"ࠪࡨࡺࡸࡡࡵ࡫ࡲࡲࡤ࡯࡮ࡠ࡯ࡶࠫⅻ")] = bstack11ll1l1l1l1_opy_(bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨⅼ")], bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪⅽ")])
        hook_data[bstack1l1_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫⅾ")] = bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬⅿ")]
        if hook_data[bstack1l1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨↀ")] == bstack1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩↁ"):
            hook_data[bstack1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࡣࡹࡿࡰࡦࠩↂ")] = bstack1ll11llll_opy_.bstack1111l11l1l_opy_(bstack11111l11111_opy_.exception_type)
            hook_data[bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࠬↃ")] = [{bstack1l1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨↄ"): bstack11l1llll1l1_opy_(bstack11111l11111_opy_.exception)}]
    return hook_data
def bstack111111ll11l_opy_(test, bstack111l1l11l1_opy_, bstack11lllllll1_opy_, result=None, call=None, outcome=None):
    logger.debug(bstack1l1_opy_ (u"࠭ࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡥࡷࡧࡱࡸ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶࡨࡷࡹࠦࡤࡢࡶࡤࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠥ࠳ࠠࡼࡿࠪↅ").format(bstack11lllllll1_opy_))
    bstack111lll1ll1_opy_ = bstack111111llll1_opy_(test, bstack111l1l11l1_opy_, result, call, bstack11lllllll1_opy_, outcome)
    driver = getattr(test, bstack1l1_opy_ (u"ࠧࡠࡦࡵ࡭ࡻ࡫ࡲࠨↆ"), None)
    if bstack11lllllll1_opy_ == bstack1l1_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩↇ") and driver:
        bstack111lll1ll1_opy_[bstack1l1_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠨↈ")] = bstack1ll11llll_opy_.bstack111ll1llll_opy_(driver)
    if bstack11lllllll1_opy_ == bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡰ࡯ࡰࡱࡧࡧࠫ↉"):
        bstack11lllllll1_opy_ = bstack1l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭↊")
    bstack111l1lll1l_opy_ = {
        bstack1l1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ↋"): bstack11lllllll1_opy_,
        bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ↌"): bstack111lll1ll1_opy_
    }
    bstack1ll11llll_opy_.bstack111lll11l_opy_(bstack111l1lll1l_opy_)
    if bstack11lllllll1_opy_ == bstack1l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ↍"):
        threading.current_thread().bstackTestMeta = {bstack1l1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ↎"): bstack1l1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪ↏")}
    elif bstack11lllllll1_opy_ == bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬ←"):
        threading.current_thread().bstackTestMeta = {bstack1l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ↑"): getattr(result, bstack1l1_opy_ (u"ࠬࡵࡵࡵࡥࡲࡱࡪ࠭→"), bstack1l1_opy_ (u"࠭ࠧ↓"))}
def bstack11111l111l1_opy_(test, bstack111l1l11l1_opy_, bstack11lllllll1_opy_, result=None, call=None, outcome=None, bstack11111l11111_opy_=None):
    logger.debug(bstack1l1_opy_ (u"ࠧࡴࡧࡱࡨࡤ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡦࡸࡨࡲࡹࡀࠠࡂࡶࡷࡩࡲࡶࡴࡪࡰࡪࠤࡹࡵࠠࡨࡧࡱࡩࡷࡧࡴࡦࠢ࡫ࡳࡴࡱࠠࡥࡣࡷࡥ࠱ࠦࡥࡷࡧࡱࡸ࡙ࡿࡰࡦࠢ࠰ࠤࢀࢃࠧ↔").format(bstack11lllllll1_opy_))
    hook_data = bstack111111l11l1_opy_(test, bstack111l1l11l1_opy_, bstack11lllllll1_opy_, result, call, outcome, bstack11111l11111_opy_)
    bstack111l1lll1l_opy_ = {
        bstack1l1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ↕"): bstack11lllllll1_opy_,
        bstack1l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࠫ↖"): hook_data
    }
    bstack1ll11llll_opy_.bstack111lll11l_opy_(bstack111l1lll1l_opy_)
def bstack111l111ll1_opy_(bstack111l1l11l1_opy_):
    if not bstack111l1l11l1_opy_:
        return None
    if bstack111l1l11l1_opy_.get(bstack1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭↗"), None):
        return getattr(bstack111l1l11l1_opy_[bstack1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ↘")], bstack1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪ↙"), None)
    return bstack111l1l11l1_opy_.get(bstack1l1_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ↚"), None)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.LOG, bstack1lllll1111l_opy_.PRE, request, caplog)
    yield
    if cli.is_running():
        cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_.LOG, bstack1lllll1111l_opy_.POST, request, caplog)
        return # skip all existing bstack1111111lll1_opy_
    try:
        if not bstack1ll11llll_opy_.on():
            return
        places = [bstack1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭↛"), bstack1l1_opy_ (u"ࠨࡥࡤࡰࡱ࠭↜"), bstack1l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ↝")]
        logs = []
        for bstack111111l1l11_opy_ in places:
            records = caplog.get_records(bstack111111l1l11_opy_)
            bstack11111l111ll_opy_ = bstack1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ↞") if bstack111111l1l11_opy_ == bstack1l1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩ↟") else bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ↠")
            bstack11111l11lll_opy_ = request.node.nodeid + (bstack1l1_opy_ (u"࠭ࠧ↡") if bstack111111l1l11_opy_ == bstack1l1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ↢") else bstack1l1_opy_ (u"ࠨ࠯ࠪ↣") + bstack111111l1l11_opy_)
            test_uuid = bstack111l111ll1_opy_(_111ll111l1_opy_.get(bstack11111l11lll_opy_, None))
            if not test_uuid:
                continue
            for record in records:
                if bstack11ll111l1l1_opy_(record.message):
                    continue
                logs.append({
                    bstack1l1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ↤"): bstack11llll111l1_opy_(record.created).isoformat() + bstack1l1_opy_ (u"ࠪ࡞ࠬ↥"),
                    bstack1l1_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ↦"): record.levelname,
                    bstack1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭↧"): record.message,
                    bstack11111l111ll_opy_: test_uuid
                })
        if len(logs) > 0:
            bstack1ll11llll_opy_.bstack1ll1ll11l1_opy_(logs)
    except Exception as err:
        print(bstack1l1_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡥࡤࡱࡱࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡀࠠࡼࡿࠪ↨"), str(err))
def bstack1l1ll11l11_opy_(sequence, driver_command, response=None, driver = None, args = None):
    global bstack1l1lll1l1l_opy_
    bstack111llll11_opy_ = bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ↩"), None) and bstack1l11l1l1_opy_(
            threading.current_thread(), bstack1l1_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ↪"), None)
    bstack1l1ll1111_opy_ = getattr(driver, bstack1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩ↫"), None) != None and getattr(driver, bstack1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ↬"), None) == True
    if sequence == bstack1l1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫ↭") and driver != None:
      if not bstack1l1lll1l1l_opy_ and bstack1ll111l1111_opy_() and bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ↮") in CONFIG and CONFIG[bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭↯")] == True and bstack11l11l1lll_opy_.bstack11ll111l1l_opy_(driver_command) and (bstack1l1ll1111_opy_ or bstack111llll11_opy_) and not bstack111ll111l_opy_(args):
        try:
          bstack1l1lll1l1l_opy_ = True
          logger.debug(bstack1l1_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡻࡾࠩ↰").format(driver_command))
          logger.debug(perform_scan(driver, driver_command=driver_command))
        except Exception as err:
          logger.debug(bstack1l1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡹࡣࡢࡰࠣࡿࢂ࠭↱").format(str(err)))
        bstack1l1lll1l1l_opy_ = False
    if sequence == bstack1l1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࠨ↲"):
        if driver_command == bstack1l1_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠧ↳"):
            bstack1ll11llll_opy_.bstack1l11ll1lll_opy_({
                bstack1l1_opy_ (u"ࠫ࡮ࡳࡡࡨࡧࠪ↴"): response[bstack1l1_opy_ (u"ࠬࡼࡡ࡭ࡷࡨࠫ↵")],
                bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭↶"): store[bstack1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ↷")]
            })
def bstack1l1ll111l1_opy_():
    global bstack11l11111l_opy_
    bstack1l11lllll_opy_.bstack1ll11l1l1l_opy_()
    logging.shutdown()
    bstack1ll11llll_opy_.bstack111l1ll1l1_opy_()
    for driver in bstack11l11111l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
def bstack111111lllll_opy_(*args):
    global bstack11l11111l_opy_
    bstack1ll11llll_opy_.bstack111l1ll1l1_opy_()
    for driver in bstack11l11111l_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1l11111ll_opy_, stage=STAGE.bstack1111lll11_opy_, bstack1l11lll11l_opy_=bstack1ll1ll111_opy_)
def bstack1ll1l11l_opy_(self, *args, **kwargs):
    bstack1l11l111ll_opy_ = bstack1ll11111_opy_(self, *args, **kwargs)
    bstack11l1l11lll_opy_ = getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡕࡧࡶࡸࡒ࡫ࡴࡢࠩ↸"), None)
    if bstack11l1l11lll_opy_ and bstack11l1l11lll_opy_.get(bstack1l1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩ↹"), bstack1l1_opy_ (u"ࠪࠫ↺")) == bstack1l1_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬ↻"):
        bstack1ll11llll_opy_.bstack1111l1l1_opy_(self)
    return bstack1l11l111ll_opy_
@measure(event_name=EVENTS.bstack11ll1lll_opy_, stage=STAGE.bstack11llll1l_opy_, bstack1l11lll11l_opy_=bstack1ll1ll111_opy_)
def bstack1lllll1ll_opy_(framework_name):
    from bstack_utils.config import Config
    bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
    if bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡳ࡯ࡥࡡࡦࡥࡱࡲࡥࡥࠩ↼")):
        return
    bstack1ll11l111l_opy_.bstack1l1l11l1l_opy_(bstack1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ↽"), True)
    global bstack1ll1lll11_opy_
    global bstack1l11lll11_opy_
    bstack1ll1lll11_opy_ = framework_name
    logger.info(bstack1lll11l1_opy_.format(bstack1ll1lll11_opy_.split(bstack1l1_opy_ (u"ࠧ࠮ࠩ↾"))[0]))
    try:
        from selenium import webdriver
        from selenium.webdriver.common.service import Service
        from selenium.webdriver.remote.webdriver import WebDriver
        if bstack1ll111l1111_opy_():
            Service.start = bstack11llll111l_opy_
            Service.stop = bstack1ll111lll_opy_
            webdriver.Remote.get = bstack11l1111l1_opy_
            webdriver.Remote.__init__ = bstack11l1l11ll_opy_
            if not isinstance(os.getenv(bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑ࡛ࡗࡉࡘ࡚࡟ࡑࡃࡕࡅࡑࡒࡅࡍࠩ↿")), str):
                return
            WebDriver.quit = bstack1l1ll11lll_opy_
            WebDriver.getAccessibilityResults = getAccessibilityResults
            WebDriver.get_accessibility_results = getAccessibilityResults
            WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
            WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
        elif bstack1ll11llll_opy_.on():
            webdriver.Remote.__init__ = bstack1ll1l11l_opy_
        bstack1l11lll11_opy_ = True
    except Exception as e:
        pass
    if os.environ.get(bstack1l1_opy_ (u"ࠩࡖࡉࡑࡋࡎࡊࡗࡐࡣࡔࡘ࡟ࡑࡎࡄ࡝࡜ࡘࡉࡈࡊࡗࡣࡎࡔࡓࡕࡃࡏࡐࡊࡊࠧ⇀")):
        bstack1l11lll11_opy_ = eval(os.environ.get(bstack1l1_opy_ (u"ࠪࡗࡊࡒࡅࡏࡋࡘࡑࡤࡕࡒࡠࡒࡏࡅ࡞࡝ࡒࡊࡉࡋࡘࡤࡏࡎࡔࡖࡄࡐࡑࡋࡄࠨ⇁")))
    if not bstack1l11lll11_opy_:
        bstack1ll1l1l11l_opy_(bstack1l1_opy_ (u"ࠦࡕࡧࡣ࡬ࡣࡪࡩࡸࠦ࡮ࡰࡶࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠨ⇂"), bstack1llll1l1ll_opy_)
    if bstack1l1lll111l_opy_():
        try:
            from selenium.webdriver.remote.remote_connection import RemoteConnection
            if hasattr(RemoteConnection, bstack1l1_opy_ (u"ࠬࡥࡧࡦࡶࡢࡴࡷࡵࡸࡺࡡࡸࡶࡱ࠭⇃")) and callable(getattr(RemoteConnection, bstack1l1_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ⇄"))):
                RemoteConnection._get_proxy_url = bstack1llll11l11_opy_
            else:
                from selenium.webdriver.remote.client_config import ClientConfig
                ClientConfig.get_proxy_url = bstack1llll11l11_opy_
        except Exception as e:
            logger.error(bstack1l1l11l1_opy_.format(str(e)))
    if bstack1l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ⇅") in str(framework_name).lower():
        if not bstack1ll111l1111_opy_():
            return
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            pytest_selenium.pytest_report_header = bstack1llll1l11_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack11llll111_opy_
            Config.getoption = bstack111lllll1_opy_
        except Exception as e:
            pass
        try:
            from pytest_bdd import reporting
            reporting.runtest_makereport = bstack1l11l1ll1_opy_
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack11l11l11l_opy_, stage=STAGE.bstack1111lll11_opy_, bstack1l11lll11l_opy_=bstack1ll1ll111_opy_)
def bstack1l1ll11lll_opy_(self):
    global bstack1ll1lll11_opy_
    global bstack1llll111l1_opy_
    global bstack11lllll11l_opy_
    try:
        if bstack1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ⇆") in bstack1ll1lll11_opy_ and self.session_id != None and bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡓࡵࡣࡷࡹࡸ࠭⇇"), bstack1l1_opy_ (u"ࠪࠫ⇈")) != bstack1l1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ⇉"):
            bstack11111llll_opy_ = bstack1l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ⇊") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭⇋")
            bstack1llll1l1l_opy_(logger, True)
            if os.environ.get(bstack1l1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࡟ࡕࡇࡖࡘࡤࡔࡁࡎࡇࠪ⇌"), None):
                self.execute_script(
                    bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭⇍") + json.dumps(
                        os.environ.get(bstack1l1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ⇎"))) + bstack1l1_opy_ (u"ࠪࢁࢂ࠭⇏"))
            if self != None:
                bstack1l111llll1_opy_(self, bstack11111llll_opy_, bstack1l1_opy_ (u"ࠫ࠱ࠦࠧ⇐").join(threading.current_thread().bstackTestErrorMessages))
        if not cli.bstack1ll1llll1ll_opy_(bstack1llll1l11ll_opy_):
            item = store.get(bstack1l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩ⇑"), None)
            if item is not None and bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ⇒"), None):
                bstack1l1l1lll11_opy_.bstack11ll1l111_opy_(self, bstack11lll11111_opy_, logger, item)
        threading.current_thread().testStatus = bstack1l1_opy_ (u"ࠧࠨ⇓")
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࠤ⇔") + str(e))
    bstack11lllll11l_opy_(self)
    self.session_id = None
@measure(event_name=EVENTS.bstack1l1l11l11l_opy_, stage=STAGE.bstack1111lll11_opy_, bstack1l11lll11l_opy_=bstack1ll1ll111_opy_)
def bstack11l1l11ll_opy_(self, command_executor,
             desired_capabilities=None, bstack1ll1l1ll1_opy_=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
    global CONFIG
    global bstack1llll111l1_opy_
    global bstack1ll1ll111_opy_
    global bstack11lllll1l_opy_
    global bstack1ll1lll11_opy_
    global bstack1ll11111_opy_
    global bstack11l11111l_opy_
    global bstack1l111l11_opy_
    global bstack1l11ll1111_opy_
    global bstack11lll11111_opy_
    CONFIG[bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ⇕")] = str(bstack1ll1lll11_opy_) + str(__version__)
    command_executor = bstack1ll1l1ll11_opy_(bstack1l111l11_opy_, CONFIG)
    logger.debug(bstack1ll1l1lll1_opy_.format(command_executor))
    proxy = bstack1ll11lll1_opy_(CONFIG, proxy)
    bstack11l111l1l1_opy_ = 0
    try:
        if bstack11lllll1l_opy_ is True:
            bstack11l111l1l1_opy_ = int(os.environ.get(bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ⇖")))
    except:
        bstack11l111l1l1_opy_ = 0
    bstack1ll1l111l_opy_ = bstack1lll1l1l1_opy_(CONFIG, bstack11l111l1l1_opy_)
    logger.debug(bstack11lllll1ll_opy_.format(str(bstack1ll1l111l_opy_)))
    bstack11lll11111_opy_ = CONFIG.get(bstack1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⇗"))[bstack11l111l1l1_opy_]
    if bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ⇘") in CONFIG and CONFIG[bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ⇙")]:
        bstack11l11llll1_opy_(bstack1ll1l111l_opy_, bstack1l11ll1111_opy_)
    if bstack1111111l1_opy_.bstack1lllllll1l_opy_(CONFIG, bstack11l111l1l1_opy_) and bstack1111111l1_opy_.bstack1l1l1ll111_opy_(bstack1ll1l111l_opy_, options, desired_capabilities):
        threading.current_thread().a11yPlatform = True
        if not cli.bstack1ll1llll1ll_opy_(bstack1llll1l11ll_opy_):
            bstack1111111l1_opy_.set_capabilities(bstack1ll1l111l_opy_, CONFIG)
    if desired_capabilities:
        bstack1l11ll11ll_opy_ = bstack11ll111ll1_opy_(desired_capabilities)
        bstack1l11ll11ll_opy_[bstack1l1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧ⇚")] = bstack11llll1l1_opy_(CONFIG)
        bstack1lll111l1l_opy_ = bstack1lll1l1l1_opy_(bstack1l11ll11ll_opy_)
        if bstack1lll111l1l_opy_:
            bstack1ll1l111l_opy_ = update(bstack1lll111l1l_opy_, bstack1ll1l111l_opy_)
        desired_capabilities = None
    if options:
        bstack1ll11l11ll_opy_(options, bstack1ll1l111l_opy_)
    if not options:
        options = bstack111l1111l_opy_(bstack1ll1l111l_opy_)
    if proxy and bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠨ࠶࠱࠵࠵࠴࠰ࠨ⇛")):
        options.proxy(proxy)
    if options and bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨ⇜")):
        desired_capabilities = None
    if (
            not options and not desired_capabilities
    ) or (
            bstack1l1lll11_opy_() < version.parse(bstack1l1_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩ⇝")) and not desired_capabilities
    ):
        desired_capabilities = {}
        desired_capabilities.update(bstack1ll1l111l_opy_)
    logger.info(bstack1l1l1l1l1_opy_)
    bstack11l11l111l_opy_.end(EVENTS.bstack11ll1lll_opy_.value, EVENTS.bstack11ll1lll_opy_.value + bstack1l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦ⇞"),
                               EVENTS.bstack11ll1lll_opy_.value + bstack1l1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥ⇟"), True, None)
    if bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"࠭࠴࠯࠳࠳࠲࠵࠭⇠")):
        bstack1ll11111_opy_(self, command_executor=command_executor,
                  options=options, keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭⇡")):
        bstack1ll11111_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities, options=options,
                  bstack1ll1l1ll1_opy_=bstack1ll1l1ll1_opy_, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    elif bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠨ࠴࠱࠹࠸࠴࠰ࠨ⇢")):
        bstack1ll11111_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  bstack1ll1l1ll1_opy_=bstack1ll1l1ll1_opy_, proxy=proxy,
                  keep_alive=keep_alive, file_detector=file_detector)
    else:
        bstack1ll11111_opy_(self, command_executor=command_executor,
                  desired_capabilities=desired_capabilities,
                  bstack1ll1l1ll1_opy_=bstack1ll1l1ll1_opy_, proxy=proxy,
                  keep_alive=keep_alive)
    try:
        bstack111l1ll1_opy_ = bstack1l1_opy_ (u"ࠩࠪ⇣")
        if bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠪ࠸࠳࠶࠮࠱ࡤ࠴ࠫ⇤")):
            bstack111l1ll1_opy_ = self.caps.get(bstack1l1_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦ⇥"))
        else:
            bstack111l1ll1_opy_ = self.capabilities.get(bstack1l1_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧ⇦"))
        if bstack111l1ll1_opy_:
            bstack1l11ll11l1_opy_(bstack111l1ll1_opy_)
            if bstack1l1lll11_opy_() <= version.parse(bstack1l1_opy_ (u"࠭࠳࠯࠳࠶࠲࠵࠭⇧")):
                self.command_executor._url = bstack1l1_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣ⇨") + bstack1l111l11_opy_ + bstack1l1_opy_ (u"ࠣ࠼࠻࠴࠴ࡽࡤ࠰ࡪࡸࡦࠧ⇩")
            else:
                self.command_executor._url = bstack1l1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ⇪") + bstack111l1ll1_opy_ + bstack1l1_opy_ (u"ࠥ࠳ࡼࡪ࠯ࡩࡷࡥࠦ⇫")
            logger.debug(bstack1lllll1l1l_opy_.format(bstack111l1ll1_opy_))
        else:
            logger.debug(bstack1l1l11ll11_opy_.format(bstack1l1_opy_ (u"ࠦࡔࡶࡴࡪ࡯ࡤࡰࠥࡎࡵࡣࠢࡱࡳࡹࠦࡦࡰࡷࡱࡨࠧ⇬")))
    except Exception as e:
        logger.debug(bstack1l1l11ll11_opy_.format(e))
    bstack1llll111l1_opy_ = self.session_id
    if bstack1l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ⇭") in bstack1ll1lll11_opy_:
        threading.current_thread().bstackSessionId = self.session_id
        threading.current_thread().bstackSessionDriver = self
        threading.current_thread().bstackTestErrorMessages = []
        item = store.get(bstack1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤ࡯ࡴࡦ࡯ࠪ⇮"), None)
        if item:
            bstack11111l11ll1_opy_ = getattr(item, bstack1l1_opy_ (u"ࠧࡠࡶࡨࡷࡹࡥࡣࡢࡵࡨࡣࡸࡺࡡࡳࡶࡨࡨࠬ⇯"), False)
            if not getattr(item, bstack1l1_opy_ (u"ࠨࡡࡧࡶ࡮ࡼࡥࡳࠩ⇰"), None) and bstack11111l11ll1_opy_:
                setattr(store[bstack1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠ࡫ࡷࡩࡲ࠭⇱")], bstack1l1_opy_ (u"ࠪࡣࡩࡸࡩࡷࡧࡵࠫ⇲"), self)
        bstack11l1l11lll_opy_ = getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡘࡪࡹࡴࡎࡧࡷࡥࠬ⇳"), None)
        if bstack11l1l11lll_opy_ and bstack11l1l11lll_opy_.get(bstack1l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ⇴"), bstack1l1_opy_ (u"࠭ࠧ⇵")) == bstack1l1_opy_ (u"ࠧࡱࡧࡱࡨ࡮ࡴࡧࠨ⇶"):
            bstack1ll11llll_opy_.bstack1111l1l1_opy_(self)
    bstack11l11111l_opy_.append(self)
    if bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ⇷") in CONFIG and bstack1l1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ⇸") in CONFIG[bstack1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭⇹")][bstack11l111l1l1_opy_]:
        bstack1ll1ll111_opy_ = CONFIG[bstack1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ⇺")][bstack11l111l1l1_opy_][bstack1l1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⇻")]
    logger.debug(bstack1lll111l_opy_.format(bstack1llll111l1_opy_))
@measure(event_name=EVENTS.bstack1l11ll1ll1_opy_, stage=STAGE.bstack1111lll11_opy_, bstack1l11lll11l_opy_=bstack1ll1ll111_opy_)
def bstack11l1111l1_opy_(self, url):
    global bstack1ll1111l1_opy_
    global CONFIG
    try:
        bstack1l1l1llll_opy_(url, CONFIG, logger)
    except Exception as err:
        logger.debug(bstack11l11lll1_opy_.format(str(err)))
    try:
        bstack1ll1111l1_opy_(self, url)
    except Exception as e:
        try:
            bstack1ll1l11l1l_opy_ = str(e)
            if any(err_msg in bstack1ll1l11l1l_opy_ for err_msg in bstack11llll11_opy_):
                bstack1l1l1llll_opy_(url, CONFIG, logger, True)
        except Exception as err:
            logger.debug(bstack11l11lll1_opy_.format(str(err)))
        raise e
def bstack111l1111_opy_(item, when):
    global bstack1lll111lll_opy_
    try:
        bstack1lll111lll_opy_(item, when)
    except Exception as e:
        pass
def bstack1l11l1ll1_opy_(item, call, rep):
    global bstack1l111111ll_opy_
    global bstack11l11111l_opy_
    name = bstack1l1_opy_ (u"࠭ࠧ⇼")
    try:
        if rep.when == bstack1l1_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ⇽"):
            bstack1llll111l1_opy_ = threading.current_thread().bstackSessionId
            skipSessionName = item.config.getoption(bstack1l1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ⇾"))
            try:
                if (str(skipSessionName).lower() != bstack1l1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ⇿")):
                    name = str(rep.nodeid)
                    bstack1l1l1ll11_opy_ = bstack1l11l1l1l_opy_(bstack1l1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ∀"), name, bstack1l1_opy_ (u"ࠫࠬ∁"), bstack1l1_opy_ (u"ࠬ࠭∂"), bstack1l1_opy_ (u"࠭ࠧ∃"), bstack1l1_opy_ (u"ࠧࠨ∄"))
                    os.environ[bstack1l1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫ∅")] = name
                    for driver in bstack11l11111l_opy_:
                        if bstack1llll111l1_opy_ == driver.session_id:
                            driver.execute_script(bstack1l1l1ll11_opy_)
            except Exception as e:
                logger.debug(bstack1l1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ∆").format(str(e)))
            try:
                bstack1l1l1l1ll_opy_(rep.outcome.lower())
                if rep.outcome.lower() != bstack1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫ∇"):
                    status = bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ∈") if rep.outcome.lower() == bstack1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ∉") else bstack1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭∊")
                    reason = bstack1l1_opy_ (u"ࠧࠨ∋")
                    if status == bstack1l1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ∌"):
                        reason = rep.longrepr.reprcrash.message
                        if (not threading.current_thread().bstackTestErrorMessages):
                            threading.current_thread().bstackTestErrorMessages = []
                        threading.current_thread().bstackTestErrorMessages.append(reason)
                    level = bstack1l1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ∍") if status == bstack1l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ∎") else bstack1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ∏")
                    data = name + bstack1l1_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧ∐") if status == bstack1l1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭∑") else name + bstack1l1_opy_ (u"ࠧࠡࡨࡤ࡭ࡱ࡫ࡤࠢࠢࠪ−") + reason
                    bstack1lll1lll1_opy_ = bstack1l11l1l1l_opy_(bstack1l1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪ∓"), bstack1l1_opy_ (u"ࠩࠪ∔"), bstack1l1_opy_ (u"ࠪࠫ∕"), bstack1l1_opy_ (u"ࠫࠬ∖"), level, data)
                    for driver in bstack11l11111l_opy_:
                        if bstack1llll111l1_opy_ == driver.session_id:
                            driver.execute_script(bstack1lll1lll1_opy_)
            except Exception as e:
                logger.debug(bstack1l1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡦࡳࡳࡺࡥࡹࡶࠣࡪࡴࡸࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠿ࠦࡻࡾࠩ∗").format(str(e)))
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡶࡸࡦࡺࡥࠡ࡫ࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࠦࡳࡵࡣࡷࡹࡸࡀࠠࡼࡿࠪ∘").format(str(e)))
    bstack1l111111ll_opy_(item, call, rep)
notset = Notset()
def bstack111lllll1_opy_(self, name: str, default=notset, skip: bool = False):
    global bstack11ll1l1111_opy_
    if str(name).lower() == bstack1l1_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸࠧ∙"):
        return bstack1l1_opy_ (u"ࠣࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠢ√")
    else:
        return bstack11ll1l1111_opy_(self, name, default, skip)
def bstack1llll11l11_opy_(self):
    global CONFIG
    global bstack111ll11l1_opy_
    try:
        proxy = bstack11l1l1lll1_opy_(CONFIG)
        if proxy:
            if proxy.endswith(bstack1l1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ∛")):
                proxies = bstack1l1l111ll_opy_(proxy, bstack1ll1l1ll11_opy_())
                if len(proxies) > 0:
                    protocol, bstack1l111l1l11_opy_ = proxies.popitem()
                    if bstack1l1_opy_ (u"ࠥ࠾࠴࠵ࠢ∜") in bstack1l111l1l11_opy_:
                        return bstack1l111l1l11_opy_
                    else:
                        return bstack1l1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧ∝") + bstack1l111l1l11_opy_
            else:
                return proxy
    except Exception as e:
        logger.error(bstack1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡲࡵࡳࡽࡿࠠࡶࡴ࡯ࠤ࠿ࠦࡻࡾࠤ∞").format(str(e)))
    return bstack111ll11l1_opy_(self)
def bstack1l1lll111l_opy_():
    return (bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩ∟") in CONFIG or bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ∠") in CONFIG) and bstack1111111ll_opy_() and bstack1l1lll11_opy_() >= version.parse(
        bstack11lll1l11_opy_)
def bstack1l11111ll1_opy_(self,
               executablePath=None,
               channel=None,
               args=None,
               ignoreDefaultArgs=None,
               handleSIGINT=None,
               handleSIGTERM=None,
               handleSIGHUP=None,
               timeout=None,
               env=None,
               headless=None,
               devtools=None,
               proxy=None,
               downloadsPath=None,
               slowMo=None,
               tracesDir=None,
               chromiumSandbox=None,
               firefoxUserPrefs=None
               ):
    global CONFIG
    global bstack1ll1ll111_opy_
    global bstack11lllll1l_opy_
    global bstack1ll1lll11_opy_
    CONFIG[bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪ∡")] = str(bstack1ll1lll11_opy_) + str(__version__)
    bstack11l111l1l1_opy_ = 0
    try:
        if bstack11lllll1l_opy_ is True:
            bstack11l111l1l1_opy_ = int(os.environ.get(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩ∢")))
    except:
        bstack11l111l1l1_opy_ = 0
    CONFIG[bstack1l1_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤ∣")] = True
    bstack1ll1l111l_opy_ = bstack1lll1l1l1_opy_(CONFIG, bstack11l111l1l1_opy_)
    logger.debug(bstack11lllll1ll_opy_.format(str(bstack1ll1l111l_opy_)))
    if CONFIG.get(bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ∤")):
        bstack11l11llll1_opy_(bstack1ll1l111l_opy_, bstack1l11ll1111_opy_)
    if bstack1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ∥") in CONFIG and bstack1l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ∦") in CONFIG[bstack1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ∧")][bstack11l111l1l1_opy_]:
        bstack1ll1ll111_opy_ = CONFIG[bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ∨")][bstack11l111l1l1_opy_][bstack1l1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ∩")]
    import urllib
    import json
    if bstack1l1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ∪") in CONFIG and str(CONFIG[bstack1l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ∫")]).lower() != bstack1l1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ∬"):
        bstack1111l11ll_opy_ = bstack1l1l111ll1_opy_()
        bstack111llll1_opy_ = bstack1111l11ll_opy_ + urllib.parse.quote(json.dumps(bstack1ll1l111l_opy_))
    else:
        bstack111llll1_opy_ = bstack1l1_opy_ (u"࠭ࡷࡴࡵ࠽࠳࠴ࡩࡤࡱ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࡁࡦࡥࡵࡹ࠽ࠨ∭") + urllib.parse.quote(json.dumps(bstack1ll1l111l_opy_))
    browser = self.connect(bstack111llll1_opy_)
    return browser
def bstack1l1ll111ll_opy_():
    global bstack1l11lll11_opy_
    global bstack1ll1lll11_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1111l1l1l_opy_
        if not bstack1ll111l1111_opy_():
            global bstack11l1111l_opy_
            if not bstack11l1111l_opy_:
                from bstack_utils.helper import bstack1l1l1lll_opy_, bstack1ll1l1111l_opy_
                bstack11l1111l_opy_ = bstack1l1l1lll_opy_()
                bstack1ll1l1111l_opy_(bstack1ll1lll11_opy_)
            BrowserType.connect = bstack1111l1l1l_opy_
            return
        BrowserType.launch = bstack1l11111ll1_opy_
        bstack1l11lll11_opy_ = True
    except Exception as e:
        pass
def bstack111111l1ll1_opy_():
    global CONFIG
    global bstack11ll1llll_opy_
    global bstack1l111l11_opy_
    global bstack1l11ll1111_opy_
    global bstack11lllll1l_opy_
    global bstack1lllllll11_opy_
    CONFIG = json.loads(os.environ.get(bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌ࠭∮")))
    bstack11ll1llll_opy_ = eval(os.environ.get(bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩ∯")))
    bstack1l111l11_opy_ = os.environ.get(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡊࡘࡆࡤ࡛ࡒࡍࠩ∰"))
    bstack111llll1l_opy_(CONFIG, bstack11ll1llll_opy_)
    bstack1lllllll11_opy_ = bstack1l11lllll_opy_.bstack1ll1111l_opy_(CONFIG, bstack1lllllll11_opy_)
    if cli.bstack1lll1llll_opy_():
        bstack1l11111lll_opy_.invoke(bstack1ll111ll1_opy_.CONNECT, bstack11l11lllll_opy_())
        cli_context.platform_index = int(os.environ.get(bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ∱"), bstack1l1_opy_ (u"ࠫ࠵࠭∲")))
        cli.bstack1ll1lll111l_opy_(cli_context.platform_index)
        cli.bstack1ll1lll11ll_opy_(bstack1ll1l1ll11_opy_(bstack1l111l11_opy_, CONFIG), cli_context.platform_index, bstack111l1111l_opy_)
        cli.bstack1ll1lll1l1l_opy_()
        logger.debug(bstack1l1_opy_ (u"ࠧࡉࡌࡊࠢ࡬ࡷࠥࡧࡣࡵ࡫ࡹࡩࠥ࡬࡯ࡳࠢࡳࡰࡦࡺࡦࡰࡴࡰࡣ࡮ࡴࡤࡦࡺࡀࠦ∳") + str(cli_context.platform_index) + bstack1l1_opy_ (u"ࠨࠢ∴"))
        return # skip all existing bstack1111111lll1_opy_
    global bstack1ll11111_opy_
    global bstack11lllll11l_opy_
    global bstack1lll1ll1_opy_
    global bstack11llllllll_opy_
    global bstack11l1ll1l1_opy_
    global bstack11111111l_opy_
    global bstack11lll1l111_opy_
    global bstack1ll1111l1_opy_
    global bstack111ll11l1_opy_
    global bstack11ll1l1111_opy_
    global bstack1lll111lll_opy_
    global bstack1l111111ll_opy_
    try:
        from selenium import webdriver
        from selenium.webdriver.remote.webdriver import WebDriver
        bstack1ll11111_opy_ = webdriver.Remote.__init__
        bstack11lllll11l_opy_ = WebDriver.quit
        bstack11lll1l111_opy_ = WebDriver.close
        bstack1ll1111l1_opy_ = WebDriver.get
    except Exception as e:
        pass
    if (bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ∵") in CONFIG or bstack1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ∶") in CONFIG) and bstack1111111ll_opy_():
        if bstack1l1lll11_opy_() < version.parse(bstack11lll1l11_opy_):
            logger.error(bstack11lll111ll_opy_.format(bstack1l1lll11_opy_()))
        else:
            try:
                from selenium.webdriver.remote.remote_connection import RemoteConnection
                if hasattr(RemoteConnection, bstack1l1_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪ∷")) and callable(getattr(RemoteConnection, bstack1l1_opy_ (u"ࠪࡣ࡬࡫ࡴࡠࡲࡵࡳࡽࡿ࡟ࡶࡴ࡯ࠫ∸"))):
                    bstack111ll11l1_opy_ = RemoteConnection._get_proxy_url
                else:
                    from selenium.webdriver.remote.client_config import ClientConfig
                    bstack111ll11l1_opy_ = ClientConfig.get_proxy_url
            except Exception as e:
                logger.error(bstack1l1l11l1_opy_.format(str(e)))
    try:
        from _pytest.config import Config
        bstack11ll1l1111_opy_ = Config.getoption
        from _pytest import runner
        bstack1lll111lll_opy_ = runner._update_current_test_var
    except Exception as e:
        logger.warn(e, bstack11l1ll11l1_opy_)
    try:
        from pytest_bdd import reporting
        bstack1l111111ll_opy_ = reporting.runtest_makereport
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡳࠥࡸࡵ࡯ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡦࡵࡷࡷࠬ∹"))
    bstack1l11ll1111_opy_ = CONFIG.get(bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ∺"), {}).get(bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ∻"))
    bstack11lllll1l_opy_ = True
    bstack1lllll1ll_opy_(bstack1lll111l11_opy_)
if (bstack11ll1ll111l_opy_()):
    bstack111111l1ll1_opy_()
@bstack111l11l111_opy_(class_method=False)
def bstack111111l111l_opy_(hook_name, event, bstack1l111lll1l1_opy_=None):
    if hook_name not in [bstack1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨ∼"), bstack1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࠬ∽"), bstack1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨ∾"), bstack1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬ∿"), bstack1l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠩ≀"), bstack1l1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸ࠭≁"), bstack1l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳࡥࡵࡪࡲࡨࠬ≂"), bstack1l1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡰࡩࡹ࡮࡯ࡥࠩ≃")]:
        return
    node = store[bstack1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ≄")]
    if hook_name in [bstack1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨ≅"), bstack1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬ≆")]:
        node = store[bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡯ࡴࡦ࡯ࠪ≇")]
    elif hook_name in [bstack1l1_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪ≈"), bstack1l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧ≉")]:
        node = store[bstack1l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡥ࡯ࡥࡸࡹ࡟ࡪࡶࡨࡱࠬ≊")]
    hook_type = bstack111l111ll11_opy_(hook_name)
    if event == bstack1l1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࠨ≋"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_[hook_type], bstack1lllll1111l_opy_.PRE, node, hook_name)
            return
        uuid = uuid4().__str__()
        bstack111l11111l_opy_ = {
            bstack1l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ≌"): uuid,
            bstack1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ≍"): bstack11111l1l1_opy_(),
            bstack1l1_opy_ (u"ࠫࡹࡿࡰࡦࠩ≎"): bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ≏"),
            bstack1l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩ≐"): hook_type,
            bstack1l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡴࡡ࡮ࡧࠪ≑"): hook_name
        }
        store[bstack1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡ࡫ࡳࡴࡱ࡟ࡶࡷ࡬ࡨࠬ≒")].append(uuid)
        bstack111111l11ll_opy_ = node.nodeid
        if hook_type == bstack1l1_opy_ (u"ࠩࡅࡉࡋࡕࡒࡆࡡࡈࡅࡈࡎࠧ≓"):
            if not _111ll111l1_opy_.get(bstack111111l11ll_opy_, None):
                _111ll111l1_opy_[bstack111111l11ll_opy_] = {bstack1l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡴࠩ≔"): []}
            _111ll111l1_opy_[bstack111111l11ll_opy_][bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪ≕")].append(bstack111l11111l_opy_[bstack1l1_opy_ (u"ࠬࡻࡵࡪࡦࠪ≖")])
        _111ll111l1_opy_[bstack111111l11ll_opy_ + bstack1l1_opy_ (u"࠭࠭ࠨ≗") + hook_name] = bstack111l11111l_opy_
        bstack11111l111l1_opy_(node, bstack111l11111l_opy_, bstack1l1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨ≘"))
    elif event == bstack1l1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧ≙"):
        if cli.is_running():
            cli.test_framework.track_event(cli_context, bstack1llll1ll1ll_opy_[hook_type], bstack1lllll1111l_opy_.POST, node, None, bstack1l111lll1l1_opy_)
            return
        bstack111llll1l1_opy_ = node.nodeid + bstack1l1_opy_ (u"ࠩ࠰ࠫ≚") + hook_name
        _111ll111l1_opy_[bstack111llll1l1_opy_][bstack1l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ≛")] = bstack11111l1l1_opy_()
        bstack111111lll1l_opy_(_111ll111l1_opy_[bstack111llll1l1_opy_][bstack1l1_opy_ (u"ࠫࡺࡻࡩࡥࠩ≜")])
        bstack11111l111l1_opy_(node, _111ll111l1_opy_[bstack111llll1l1_opy_], bstack1l1_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳࡌࡩ࡯࡫ࡶ࡬ࡪࡪࠧ≝"), bstack11111l11111_opy_=bstack1l111lll1l1_opy_)
def bstack1111111llll_opy_():
    global bstack111111lll11_opy_
    if bstack1ll11ll1_opy_():
        bstack111111lll11_opy_ = bstack1l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪ≞")
    else:
        bstack111111lll11_opy_ = bstack1l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ≟")
@bstack1ll11llll_opy_.bstack1111l11ll1l_opy_
def bstack1111111ll1l_opy_():
    bstack1111111llll_opy_()
    if cli.is_running():
        try:
            bstack11l111l1l11_opy_(bstack111111l111l_opy_)
        except Exception as e:
            logger.debug(bstack1l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࡸࠦࡰࡢࡶࡦ࡬࠿ࠦࡻࡾࠤ≠").format(e))
        return
    if bstack1111111ll_opy_():
        bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
        bstack1l1_opy_ (u"ࠩࠪࠫࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡊࡴࡸࠠࡱࡲࡳࠤࡂࠦ࠱࠭ࠢࡰࡳࡩࡥࡥࡹࡧࡦࡹࡹ࡫ࠠࡨࡧࡷࡷࠥࡻࡳࡦࡦࠣࡪࡴࡸࠠࡢ࠳࠴ࡽࠥࡩ࡯࡮࡯ࡤࡲࡩࡹ࠭ࡸࡴࡤࡴࡵ࡯࡮ࡨࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡇࡱࡵࠤࡵࡶࡰࠡࡀࠣ࠵࠱ࠦ࡭ࡰࡦࡢࡩࡽ࡫ࡣࡶࡶࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡲࡶࡰࠣࡦࡪࡩࡡࡶࡵࡨࠤ࡮ࡺࠠࡪࡵࠣࡴࡦࡺࡣࡩࡧࡧࠤ࡮ࡴࠠࡢࠢࡧ࡭࡫࡬ࡥࡳࡧࡱࡸࠥࡶࡲࡰࡥࡨࡷࡸࠦࡩࡥࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡕࡪࡸࡷࠥࡽࡥࠡࡰࡨࡩࡩࠦࡴࡰࠢࡸࡷࡪࠦࡓࡦ࡮ࡨࡲ࡮ࡻ࡭ࡑࡣࡷࡧ࡭࠮ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡠࡪࡤࡲࡩࡲࡥࡳࠫࠣࡪࡴࡸࠠࡱࡲࡳࠤࡃࠦ࠱ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠪࠫࠬ≡")
        if bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡱࡴࡪ࡟ࡤࡣ࡯ࡰࡪࡪࠧ≢")):
            if CONFIG.get(bstack1l1_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ≣")) is not None and int(CONFIG[bstack1l1_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ≤")]) > 1:
                bstack1l1111l11l_opy_(bstack1l1ll11l11_opy_)
            return
        bstack1l1111l11l_opy_(bstack1l1ll11l11_opy_)
    try:
        bstack11l111l1l11_opy_(bstack111111l111l_opy_)
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࡶࠤࡵࡧࡴࡤࡪ࠽ࠤࢀࢃࠢ≥").format(e))
bstack1111111ll1l_opy_()