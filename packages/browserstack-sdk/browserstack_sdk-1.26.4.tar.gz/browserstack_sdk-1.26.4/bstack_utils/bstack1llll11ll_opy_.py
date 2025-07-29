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
class bstack111l11l11_opy_:
    def __init__(self, handler):
        self._1111ll1ll11_opy_ = None
        self.handler = handler
        self._1111ll1l1ll_opy_ = self.bstack1111ll1ll1l_opy_()
        self.patch()
    def patch(self):
        self._1111ll1ll11_opy_ = self._1111ll1l1ll_opy_.execute
        self._1111ll1l1ll_opy_.execute = self.bstack1111ll1lll1_opy_()
    def bstack1111ll1lll1_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࠢḾ"), driver_command, None, this, args)
            response = self._1111ll1ll11_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1ll_opy_ (u"ࠣࡣࡩࡸࡪࡸࠢḿ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1111ll1l1ll_opy_.execute = self._1111ll1ll11_opy_
    @staticmethod
    def bstack1111ll1ll1l_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver