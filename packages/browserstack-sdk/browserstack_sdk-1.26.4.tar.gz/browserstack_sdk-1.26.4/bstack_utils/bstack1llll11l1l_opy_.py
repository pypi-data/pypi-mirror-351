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
bstack111l11llll1_opy_ = {bstack1ll_opy_ (u"ࠪࡶࡪࡺࡲࡺࡖࡨࡷࡹࡹࡏ࡯ࡈࡤ࡭ࡱࡻࡲࡦࠩᶮ")}
class bstack1ll1ll1ll_opy_:
    @staticmethod
    def bstack1l1ll11111_opy_(config: dict) -> bool:
        bstack111l1l11111_opy_ = config.get(bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨᶯ"), {}).get(bstack1ll_opy_ (u"ࠬࡸࡥࡵࡴࡼࡘࡪࡹࡴࡴࡑࡱࡊࡦ࡯࡬ࡶࡴࡨࠫᶰ"), {})
        return bstack111l1l11111_opy_.get(bstack1ll_opy_ (u"࠭ࡥ࡯ࡣࡥࡰࡪࡪࠧᶱ"), False)
    @staticmethod
    def bstack1ll1l1l11_opy_(config: dict) -> int:
        bstack111l1l11111_opy_ = config.get(bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫᶲ"), {}).get(bstack1ll_opy_ (u"ࠨࡴࡨࡸࡷࡿࡔࡦࡵࡷࡷࡔࡴࡆࡢ࡫࡯ࡹࡷ࡫ࠧᶳ"), {})
        retries = 0
        if bstack1ll1ll1ll_opy_.bstack1l1ll11111_opy_(config):
            retries = bstack111l1l11111_opy_.get(bstack1ll_opy_ (u"ࠩࡰࡥࡽࡘࡥࡵࡴ࡬ࡩࡸ࠭ᶴ"), 1)
        return retries
    @staticmethod
    def bstack1l11111l1_opy_(config: dict) -> dict:
        bstack111l11lllll_opy_ = config.get(bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧᶵ"), {})
        return {
            key: value for key, value in bstack111l11lllll_opy_.items() if key in bstack111l11llll1_opy_
        }