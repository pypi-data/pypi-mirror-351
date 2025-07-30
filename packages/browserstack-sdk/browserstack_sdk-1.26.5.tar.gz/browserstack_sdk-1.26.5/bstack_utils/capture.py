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
import builtins
import logging
class bstack111lllllll_opy_:
    def __init__(self, handler):
        self._11l11llll1l_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l11llll11_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack1l1_opy_ (u"ࠬ࡯࡮ࡧࡱࠪᤦ"), bstack1l1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬᤧ"), bstack1l1_opy_ (u"ࠧࡸࡣࡵࡲ࡮ࡴࡧࠨᤨ"), bstack1l1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᤩ")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l11llllll_opy_
        self._11l1l111111_opy_()
    def _11l11llllll_opy_(self, *args, **kwargs):
        self._11l11llll1l_opy_(*args, **kwargs)
        message = bstack1l1_opy_ (u"ࠩࠣࠫᤪ").join(map(str, args)) + bstack1l1_opy_ (u"ࠪࡠࡳ࠭ᤫ")
        self._log_message(bstack1l1_opy_ (u"ࠫࡎࡔࡆࡐࠩ᤬"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack1l1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ᤭"): level, bstack1l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ᤮"): msg})
    def _11l1l111111_opy_(self):
        for level, bstack11l1l11111l_opy_ in self._11l11llll11_opy_.items():
            setattr(logging, level, self._11l11lllll1_opy_(level, bstack11l1l11111l_opy_))
    def _11l11lllll1_opy_(self, level, bstack11l1l11111l_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1l11111l_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l11llll1l_opy_
        for level, bstack11l1l11111l_opy_ in self._11l11llll11_opy_.items():
            setattr(logging, level, bstack11l1l11111l_opy_)