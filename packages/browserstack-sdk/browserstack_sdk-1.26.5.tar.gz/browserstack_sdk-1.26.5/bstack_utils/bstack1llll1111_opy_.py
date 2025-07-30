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
import threading
import logging
import bstack_utils.accessibility as bstack1111111l1_opy_
from bstack_utils.helper import bstack1l11l1l1_opy_
logger = logging.getLogger(__name__)
def bstack11ll1l1l11_opy_(bstack1lllll11ll_opy_):
  return True if bstack1lllll11ll_opy_ in threading.current_thread().__dict__.keys() else False
def bstack111l111l1_opy_(context, *args):
    tags = getattr(args[0], bstack1l1_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᤝ"), [])
    bstack11ll1ll11_opy_ = bstack1111111l1_opy_.bstack11l1l1111l_opy_(tags)
    threading.current_thread().isA11yTest = bstack11ll1ll11_opy_
    try:
      bstack1111lll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll1l1l11_opy_(bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪᤞ")) else context.browser
      if bstack1111lll1l_opy_ and bstack1111lll1l_opy_.session_id and bstack11ll1ll11_opy_ and bstack1l11l1l1_opy_(
              threading.current_thread(), bstack1l1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ᤟"), None):
          threading.current_thread().isA11yTest = bstack1111111l1_opy_.bstack1lll11111l_opy_(bstack1111lll1l_opy_, bstack11ll1ll11_opy_)
    except Exception as e:
       logger.debug(bstack1l1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡣ࠴࠵ࡾࠦࡩ࡯ࠢࡥࡩ࡭ࡧࡶࡦ࠼ࠣࡿࢂ࠭ᤠ").format(str(e)))
def bstack1l11llll11_opy_(bstack1111lll1l_opy_):
    if bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫᤡ"), None) and bstack1l11l1l1_opy_(
      threading.current_thread(), bstack1l1_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧᤢ"), None) and not bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠩࡤ࠵࠶ࡿ࡟ࡴࡶࡲࡴࠬᤣ"), False):
      threading.current_thread().a11y_stop = True
      bstack1111111l1_opy_.bstack1l111lll1l_opy_(bstack1111lll1l_opy_, name=bstack1l1_opy_ (u"ࠥࠦᤤ"), path=bstack1l1_opy_ (u"ࠦࠧᤥ"))