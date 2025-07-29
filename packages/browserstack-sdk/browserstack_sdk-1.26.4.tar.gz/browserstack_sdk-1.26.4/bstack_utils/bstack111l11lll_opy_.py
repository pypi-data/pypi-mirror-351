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
import threading
import logging
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from bstack_utils.helper import bstack11ll11l1_opy_
logger = logging.getLogger(__name__)
def bstack11ll11111_opy_(bstack1111l111l_opy_):
  return True if bstack1111l111l_opy_ in threading.current_thread().__dict__.keys() else False
def bstack11l11lll11_opy_(context, *args):
    tags = getattr(args[0], bstack1ll_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᝫ"), [])
    bstack11ll111111_opy_ = bstack1l11llll1l_opy_.bstack11l11lll_opy_(tags)
    threading.current_thread().isA11yTest = bstack11ll111111_opy_
    try:
      bstack1ll1l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11111_opy_(bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪᝬ")) else context.browser
      if bstack1ll1l11111_opy_ and bstack1ll1l11111_opy_.session_id and bstack11ll111111_opy_ and bstack11ll11l1_opy_(
              threading.current_thread(), bstack1ll_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ᝭"), None):
          threading.current_thread().isA11yTest = bstack1l11llll1l_opy_.bstack11ll11llll_opy_(bstack1ll1l11111_opy_, bstack11ll111111_opy_)
    except Exception as e:
       logger.debug(bstack1ll_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡣ࠴࠵ࡾࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦ࠼ࠣࡿࢂ࠭ᝮ").format(str(e)))
def bstack1lllll1ll1_opy_(bstack1ll1l11111_opy_):
    if bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫᝯ"), None) and bstack11ll11l1_opy_(
      threading.current_thread(), bstack1ll_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧᝰ"), None) and not bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡤ࠵࠶ࡿ࡟ࡴࡶࡲࡴࠬ᝱"), False):
      threading.current_thread().a11y_stop = True
      bstack1l11llll1l_opy_.bstack1ll11111l_opy_(bstack1ll1l11111_opy_, name=bstack1ll_opy_ (u"ࠥࠦᝲ"), path=bstack1ll_opy_ (u"ࠦࠧᝳ"))