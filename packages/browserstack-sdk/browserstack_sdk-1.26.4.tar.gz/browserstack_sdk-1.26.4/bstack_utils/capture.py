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
import builtins
import logging
class bstack111lll1111_opy_:
    def __init__(self, handler):
        self._11l1l1l1l1l_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11l1l1l1ll1_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack1ll_opy_ (u"ࠬ࡯࡮ࡧࡱࠪ᝴"), bstack1ll_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬ᝵"), bstack1ll_opy_ (u"ࠧࡸࡣࡵࡲ࡮ࡴࡧࠨ᝶"), bstack1ll_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ᝷")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11l1l1l1l11_opy_
        self._11l1l1l11l1_opy_()
    def _11l1l1l1l11_opy_(self, *args, **kwargs):
        self._11l1l1l1l1l_opy_(*args, **kwargs)
        message = bstack1ll_opy_ (u"ࠩࠣࠫ᝸").join(map(str, args)) + bstack1ll_opy_ (u"ࠪࡠࡳ࠭᝹")
        self._log_message(bstack1ll_opy_ (u"ࠫࡎࡔࡆࡐࠩ᝺"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack1ll_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ᝻"): level, bstack1ll_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ᝼"): msg})
    def _11l1l1l11l1_opy_(self):
        for level, bstack11l1l1l111l_opy_ in self._11l1l1l1ll1_opy_.items():
            setattr(logging, level, self._11l1l1l11ll_opy_(level, bstack11l1l1l111l_opy_))
    def _11l1l1l11ll_opy_(self, level, bstack11l1l1l111l_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11l1l1l111l_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11l1l1l1l1l_opy_
        for level, bstack11l1l1l111l_opy_ in self._11l1l1l1ll1_opy_.items():
            setattr(logging, level, bstack11l1l1l111l_opy_)