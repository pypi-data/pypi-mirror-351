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
from collections import deque
from bstack_utils.constants import *
class bstack1llll1l111_opy_:
    def __init__(self):
        self._11ll11l1lll_opy_ = deque()
        self._11ll11l1l11_opy_ = {}
        self._11ll11ll111_opy_ = False
    def bstack11ll11lll11_opy_(self, test_name, bstack11ll11llll1_opy_):
        bstack11ll11ll1ll_opy_ = self._11ll11l1l11_opy_.get(test_name, {})
        return bstack11ll11ll1ll_opy_.get(bstack11ll11llll1_opy_, 0)
    def bstack11ll11l11ll_opy_(self, test_name, bstack11ll11llll1_opy_):
        bstack11ll11lll1l_opy_ = self.bstack11ll11lll11_opy_(test_name, bstack11ll11llll1_opy_)
        self.bstack11ll11l1ll1_opy_(test_name, bstack11ll11llll1_opy_)
        return bstack11ll11lll1l_opy_
    def bstack11ll11l1ll1_opy_(self, test_name, bstack11ll11llll1_opy_):
        if test_name not in self._11ll11l1l11_opy_:
            self._11ll11l1l11_opy_[test_name] = {}
        bstack11ll11ll1ll_opy_ = self._11ll11l1l11_opy_[test_name]
        bstack11ll11lll1l_opy_ = bstack11ll11ll1ll_opy_.get(bstack11ll11llll1_opy_, 0)
        bstack11ll11ll1ll_opy_[bstack11ll11llll1_opy_] = bstack11ll11lll1l_opy_ + 1
    def bstack11lll1llll_opy_(self, bstack11ll11l1l1l_opy_, bstack11ll11ll1l1_opy_):
        bstack11ll11lllll_opy_ = self.bstack11ll11l11ll_opy_(bstack11ll11l1l1l_opy_, bstack11ll11ll1l1_opy_)
        event_name = bstack11ll11ll11l_opy_[bstack11ll11ll1l1_opy_]
        bstack1l1ll111l1l_opy_ = bstack1ll_opy_ (u"ࠥࡿࢂ࠳ࡻࡾ࠯ࡾࢁࠧᘍ").format(bstack11ll11l1l1l_opy_, event_name, bstack11ll11lllll_opy_)
        self._11ll11l1lll_opy_.append(bstack1l1ll111l1l_opy_)
    def bstack11l1llll11_opy_(self):
        return len(self._11ll11l1lll_opy_) == 0
    def bstack1lll1l1111_opy_(self):
        bstack11ll11l11l1_opy_ = self._11ll11l1lll_opy_.popleft()
        return bstack11ll11l11l1_opy_
    def capturing(self):
        return self._11ll11ll111_opy_
    def bstack11l11l1l11_opy_(self):
        self._11ll11ll111_opy_ = True
    def bstack111lll1ll_opy_(self):
        self._11ll11ll111_opy_ = False