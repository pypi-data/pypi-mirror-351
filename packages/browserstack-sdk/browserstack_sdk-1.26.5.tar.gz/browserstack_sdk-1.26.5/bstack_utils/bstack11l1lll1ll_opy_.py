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
class bstack1l1111l11l_opy_:
    def __init__(self, handler):
        self._1111ll1l1ll_opy_ = None
        self.handler = handler
        self._1111ll1ll1l_opy_ = self.bstack1111ll1lll1_opy_()
        self.patch()
    def patch(self):
        self._1111ll1l1ll_opy_ = self._1111ll1ll1l_opy_.execute
        self._1111ll1ll1l_opy_.execute = self.bstack1111ll1ll11_opy_()
    def bstack1111ll1ll11_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack1l1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࠢḾ"), driver_command, None, this, args)
            response = self._1111ll1l1ll_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack1l1_opy_ (u"ࠣࡣࡩࡸࡪࡸࠢḿ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1111ll1ll1l_opy_.execute = self._1111ll1l1ll_opy_
    @staticmethod
    def bstack1111ll1lll1_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver