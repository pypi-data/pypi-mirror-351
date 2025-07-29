# coding: UTF-8
import sys
bstack1l11_opy_ = sys.version_info [0] == 2
bstack111l1ll_opy_ = 2048
bstack11lll1l_opy_ = 7
def bstack1ll_opy_ (bstack11111ll_opy_):
    global bstack1lll1l_opy_
    bstack1ll11_opy_ = ord (bstack11111ll_opy_ [-1])
    bstack1l1llll_opy_ = bstack11111ll_opy_ [:-1]
    bstack1l111l1_opy_ = bstack1ll11_opy_ % len (bstack1l1llll_opy_)
    bstack1l11ll_opy_ = bstack1l1llll_opy_ [:bstack1l111l1_opy_] + bstack1l1llll_opy_ [bstack1l111l1_opy_:]
    if bstack1l11_opy_:
        bstack111l1_opy_ = unicode () .join ([unichr (ord (char) - bstack111l1ll_opy_ - (bstack1ll1l11_opy_ + bstack1ll11_opy_) % bstack11lll1l_opy_) for bstack1ll1l11_opy_, char in enumerate (bstack1l11ll_opy_)])
    else:
        bstack111l1_opy_ = str () .join ([chr (ord (char) - bstack111l1ll_opy_ - (bstack1ll1l11_opy_ + bstack1ll11_opy_) % bstack11lll1l_opy_) for bstack1ll1l11_opy_, char in enumerate (bstack1l11ll_opy_)])
    return eval (bstack111l1_opy_)
import os
import threading
from bstack_utils.helper import bstack11ll1lllll_opy_
from bstack_utils.constants import bstack11l11ll1lll_opy_, EVENTS, STAGE
from bstack_utils.bstack111ll11ll_opy_ import get_logger
logger = get_logger(__name__)
class bstack11llllll1l_opy_:
    bstack1111lllll11_opy_ = None
    @classmethod
    def bstack1lllllll1_opy_(cls):
        if cls.on() and os.getenv(bstack1ll_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢΌ")):
            logger.info(
                bstack1ll_opy_ (u"࡚ࠪ࡮ࡹࡩࡵࠢ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳ࠭Ὼ").format(os.getenv(bstack1ll_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤΏ"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩῼ"), None) is None or os.environ[bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ´")] == bstack1ll_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ῾"):
            return False
        return True
    @classmethod
    def bstack11111ll1111_opy_(cls, bs_config, framework=bstack1ll_opy_ (u"ࠣࠤ῿")):
        bstack11l1l11lll1_opy_ = False
        for fw in bstack11l11ll1lll_opy_:
            if fw in framework:
                bstack11l1l11lll1_opy_ = True
        return bstack11ll1lllll_opy_(bs_config.get(bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ "), bstack11l1l11lll1_opy_))
    @classmethod
    def bstack11111l1ll11_opy_(cls, framework):
        return framework in bstack11l11ll1lll_opy_
    @classmethod
    def bstack1111l11l111_opy_(cls, bs_config, framework):
        return cls.bstack11111ll1111_opy_(bs_config, framework) is True and cls.bstack11111l1ll11_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ "), None)
    @staticmethod
    def bstack111lll1lll_opy_():
        if getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ "), None):
            return {
                bstack1ll_opy_ (u"ࠬࡺࡹࡱࡧࠪ "): bstack1ll_opy_ (u"࠭ࡴࡦࡵࡷࠫ "),
                bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ "): getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ "), None)
            }
        if getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭ "), None):
            return {
                bstack1ll_opy_ (u"ࠪࡸࡾࡶࡥࠨ "): bstack1ll_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ "),
                bstack1ll_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ "): getattr(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ​"), None)
            }
        return None
    @staticmethod
    def bstack11111l1l1l1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11llllll1l_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack111l1111ll_opy_(test, hook_name=None):
        bstack11111l1l11l_opy_ = test.parent
        if hook_name in [bstack1ll_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠬ‌"), bstack1ll_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠩ‍"), bstack1ll_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨ‎"), bstack1ll_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬ‏")]:
            bstack11111l1l11l_opy_ = test
        scope = []
        while bstack11111l1l11l_opy_ is not None:
            scope.append(bstack11111l1l11l_opy_.name)
            bstack11111l1l11l_opy_ = bstack11111l1l11l_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack11111l1l111_opy_(hook_type):
        if hook_type == bstack1ll_opy_ (u"ࠦࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠤ‐"):
            return bstack1ll_opy_ (u"࡙ࠧࡥࡵࡷࡳࠤ࡭ࡵ࡯࡬ࠤ‑")
        elif hook_type == bstack1ll_opy_ (u"ࠨࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠥ‒"):
            return bstack1ll_opy_ (u"ࠢࡕࡧࡤࡶࡩࡵࡷ࡯ࠢ࡫ࡳࡴࡱࠢ–")
    @staticmethod
    def bstack11111l1l1ll_opy_(bstack1l1ll1l1_opy_):
        try:
            if not bstack11llllll1l_opy_.on():
                return bstack1l1ll1l1_opy_
            if os.environ.get(bstack1ll_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࠨ—"), None) == bstack1ll_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ―"):
                tests = os.environ.get(bstack1ll_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࡠࡖࡈࡗ࡙࡙ࠢ‖"), None)
                if tests is None or tests == bstack1ll_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ‗"):
                    return bstack1l1ll1l1_opy_
                bstack1l1ll1l1_opy_ = tests.split(bstack1ll_opy_ (u"ࠬ࠲ࠧ‘"))
                return bstack1l1ll1l1_opy_
        except Exception as exc:
            logger.debug(bstack1ll_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡸࡥࡳࡷࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡶ࠿ࠦࠢ’") + str(str(exc)) + bstack1ll_opy_ (u"ࠢࠣ‚"))
        return bstack1l1ll1l1_opy_