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
from collections import deque
from bstack_utils.constants import *
class bstack1l11ll1l_opy_:
    def __init__(self):
        self._111l1l1l11l_opy_ = deque()
        self._111l11llll1_opy_ = {}
        self._111l1l11l1l_opy_ = False
    def bstack111l1l1111l_opy_(self, test_name, bstack111l1l1l111_opy_):
        bstack111l1l11lll_opy_ = self._111l11llll1_opy_.get(test_name, {})
        return bstack111l1l11lll_opy_.get(bstack111l1l1l111_opy_, 0)
    def bstack111l1l1l1l1_opy_(self, test_name, bstack111l1l1l111_opy_):
        bstack111l1l11111_opy_ = self.bstack111l1l1111l_opy_(test_name, bstack111l1l1l111_opy_)
        self.bstack111l1l111ll_opy_(test_name, bstack111l1l1l111_opy_)
        return bstack111l1l11111_opy_
    def bstack111l1l111ll_opy_(self, test_name, bstack111l1l1l111_opy_):
        if test_name not in self._111l11llll1_opy_:
            self._111l11llll1_opy_[test_name] = {}
        bstack111l1l11lll_opy_ = self._111l11llll1_opy_[test_name]
        bstack111l1l11111_opy_ = bstack111l1l11lll_opy_.get(bstack111l1l1l111_opy_, 0)
        bstack111l1l11lll_opy_[bstack111l1l1l111_opy_] = bstack111l1l11111_opy_ + 1
    def bstack1llll1lll1_opy_(self, bstack111l1l111l1_opy_, bstack111l1l11l11_opy_):
        bstack111l11lllll_opy_ = self.bstack111l1l1l1l1_opy_(bstack111l1l111l1_opy_, bstack111l1l11l11_opy_)
        event_name = bstack11l11l11lll_opy_[bstack111l1l11l11_opy_]
        bstack1l1ll1111ll_opy_ = bstack1l1_opy_ (u"ࠥࡿࢂ࠳ࡻࡾ࠯ࡾࢁࠧᶵ").format(bstack111l1l111l1_opy_, event_name, bstack111l11lllll_opy_)
        self._111l1l1l11l_opy_.append(bstack1l1ll1111ll_opy_)
    def bstack11lll1lll1_opy_(self):
        return len(self._111l1l1l11l_opy_) == 0
    def bstack1ll111l11_opy_(self):
        bstack111l1l11ll1_opy_ = self._111l1l1l11l_opy_.popleft()
        return bstack111l1l11ll1_opy_
    def capturing(self):
        return self._111l1l11l1l_opy_
    def bstack1l11l11l1_opy_(self):
        self._111l1l11l1l_opy_ = True
    def bstack1l1l11lll_opy_(self):
        self._111l1l11l1l_opy_ = False