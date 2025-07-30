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
class RobotHandler():
    def __init__(self, args, logger, bstack1111l1lll1_opy_, bstack1111ll1l1l_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111l1lll1_opy_ = bstack1111l1lll1_opy_
        self.bstack1111ll1l1l_opy_ = bstack1111ll1l1l_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111ll1l1l1_opy_(bstack1111l11lll_opy_):
        bstack1111l1l111_opy_ = []
        if bstack1111l11lll_opy_:
            tokens = str(os.path.basename(bstack1111l11lll_opy_)).split(bstack1l1_opy_ (u"ࠤࡢࠦါ"))
            camelcase_name = bstack1l1_opy_ (u"ࠥࠤࠧာ").join(t.title() for t in tokens)
            suite_name, bstack1111l11ll1_opy_ = os.path.splitext(camelcase_name)
            bstack1111l1l111_opy_.append(suite_name)
        return bstack1111l1l111_opy_
    @staticmethod
    def bstack1111l11l1l_opy_(typename):
        if bstack1l1_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢိ") in typename:
            return bstack1l1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨီ")
        return bstack1l1_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢု")