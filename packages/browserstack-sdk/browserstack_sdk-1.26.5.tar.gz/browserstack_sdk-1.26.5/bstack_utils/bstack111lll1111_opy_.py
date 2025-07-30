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
import os
import threading
from bstack_utils.helper import bstack11l1l11l11_opy_
from bstack_utils.constants import bstack11l11l11l11_opy_, EVENTS, STAGE
from bstack_utils.bstack1l11lllll_opy_ import get_logger
logger = get_logger(__name__)
class bstack1l1111l1l1_opy_:
    bstack1111lll1ll1_opy_ = None
    @classmethod
    def bstack1lllllll1_opy_(cls):
        if cls.on() and os.getenv(bstack1l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢΌ")):
            logger.info(
                bstack1l1_opy_ (u"࡚ࠪ࡮ࡹࡩࡵࠢ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳ࠭Ὼ").format(os.getenv(bstack1l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤΏ"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩῼ"), None) is None or os.environ[bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ´")] == bstack1l1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ῾"):
            return False
        return True
    @classmethod
    def bstack11111ll1l11_opy_(cls, bs_config, framework=bstack1l1_opy_ (u"ࠣࠤ῿")):
        bstack11l11lll11l_opy_ = False
        for fw in bstack11l11l11l11_opy_:
            if fw in framework:
                bstack11l11lll11l_opy_ = True
        return bstack11l1l11l11_opy_(bs_config.get(bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ "), bstack11l11lll11l_opy_))
    @classmethod
    def bstack11111l1l1ll_opy_(cls, framework):
        return framework in bstack11l11l11l11_opy_
    @classmethod
    def bstack1111l1l11ll_opy_(cls, bs_config, framework):
        return cls.bstack11111ll1l11_opy_(bs_config, framework) is True and cls.bstack11111l1l1ll_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ "), None)
    @staticmethod
    def bstack111lll11l1_opy_():
        if getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨ "), None):
            return {
                bstack1l1_opy_ (u"ࠬࡺࡹࡱࡧࠪ "): bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࠫ "),
                bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ "): getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬ "), None)
            }
        if getattr(threading.current_thread(), bstack1l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭ "), None):
            return {
                bstack1l1_opy_ (u"ࠪࡸࡾࡶࡥࠨ "): bstack1l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ "),
                bstack1l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ "): getattr(threading.current_thread(), bstack1l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪ​"), None)
            }
        return None
    @staticmethod
    def bstack11111l1l1l1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1l1111l1l1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack111ll1l1l1_opy_(test, hook_name=None):
        bstack11111l1l111_opy_ = test.parent
        if hook_name in [bstack1l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠬ‌"), bstack1l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠩ‍"), bstack1l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨ‎"), bstack1l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬ‏")]:
            bstack11111l1l111_opy_ = test
        scope = []
        while bstack11111l1l111_opy_ is not None:
            scope.append(bstack11111l1l111_opy_.name)
            bstack11111l1l111_opy_ = bstack11111l1l111_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack11111l1l11l_opy_(hook_type):
        if hook_type == bstack1l1_opy_ (u"ࠦࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠤ‐"):
            return bstack1l1_opy_ (u"࡙ࠧࡥࡵࡷࡳࠤ࡭ࡵ࡯࡬ࠤ‑")
        elif hook_type == bstack1l1_opy_ (u"ࠨࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠥ‒"):
            return bstack1l1_opy_ (u"ࠢࡕࡧࡤࡶࡩࡵࡷ࡯ࠢ࡫ࡳࡴࡱࠢ–")
    @staticmethod
    def bstack11111l1ll11_opy_(bstack11ll1ll1l_opy_):
        try:
            if not bstack1l1111l1l1_opy_.on():
                return bstack11ll1ll1l_opy_
            if os.environ.get(bstack1l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࠨ—"), None) == bstack1l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ―"):
                tests = os.environ.get(bstack1l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࡠࡖࡈࡗ࡙࡙ࠢ‖"), None)
                if tests is None or tests == bstack1l1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ‗"):
                    return bstack11ll1ll1l_opy_
                bstack11ll1ll1l_opy_ = tests.split(bstack1l1_opy_ (u"ࠬ࠲ࠧ‘"))
                return bstack11ll1ll1l_opy_
        except Exception as exc:
            logger.debug(bstack1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡸࡥࡳࡷࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡶ࠿ࠦࠢ’") + str(str(exc)) + bstack1l1_opy_ (u"ࠢࠣ‚"))
        return bstack11ll1ll1l_opy_