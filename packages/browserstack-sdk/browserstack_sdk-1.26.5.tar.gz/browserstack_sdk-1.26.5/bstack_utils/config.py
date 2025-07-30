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
conf = {
    bstack1l1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭᤯"): False,
    bstack1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࠩᤰ"): True,
    bstack1l1_opy_ (u"ࠩࡶ࡯࡮ࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡵࡷࡥࡹࡻࡳࠨᤱ"): False
}
class Config(object):
    instance = None
    def __init__(self):
        self._11l11lll1ll_opy_ = conf
    @classmethod
    def bstack1l1l11ll1_opy_(cls):
        if cls.instance:
            return cls.instance
        return Config()
    def get_property(self, property_name, bstack11l11lll11l_opy_=None):
        return self._11l11lll1ll_opy_.get(property_name, bstack11l11lll11l_opy_)
    def bstack1l1l11l1l_opy_(self, property_name, bstack11l11lll1l1_opy_):
        self._11l11lll1ll_opy_[property_name] = bstack11l11lll1l1_opy_
    def bstack1ll11lll11_opy_(self, val):
        self._11l11lll1ll_opy_[bstack1l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡶࡸࡦࡺࡵࡴࠩᤲ")] = bool(val)
    def bstack1111l1l1ll_opy_(self):
        return self._11l11lll1ll_opy_.get(bstack1l1_opy_ (u"ࠫࡸࡱࡩࡱࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠪᤳ"), False)