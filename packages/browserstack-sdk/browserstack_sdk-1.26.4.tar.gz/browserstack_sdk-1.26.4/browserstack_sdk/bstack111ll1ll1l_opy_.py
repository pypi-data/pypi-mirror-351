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
class RobotHandler():
    def __init__(self, args, logger, bstack1111lll1ll_opy_, bstack1111lll11l_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111lll1ll_opy_ = bstack1111lll1ll_opy_
        self.bstack1111lll11l_opy_ = bstack1111lll11l_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111l1111ll_opy_(bstack1111l11lll_opy_):
        bstack1111l11l1l_opy_ = []
        if bstack1111l11lll_opy_:
            tokens = str(os.path.basename(bstack1111l11lll_opy_)).split(bstack1ll_opy_ (u"ࠤࡢࠦါ"))
            camelcase_name = bstack1ll_opy_ (u"ࠥࠤࠧာ").join(t.title() for t in tokens)
            suite_name, bstack1111l1l111_opy_ = os.path.splitext(camelcase_name)
            bstack1111l11l1l_opy_.append(suite_name)
        return bstack1111l11l1l_opy_
    @staticmethod
    def bstack1111l11ll1_opy_(typename):
        if bstack1ll_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢိ") in typename:
            return bstack1ll_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨီ")
        return bstack1ll_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢု")