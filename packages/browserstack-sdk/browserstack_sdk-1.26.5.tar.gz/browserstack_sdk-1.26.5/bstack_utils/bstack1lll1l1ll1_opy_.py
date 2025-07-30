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
bstack111lll1llll_opy_ = {bstack1l1_opy_ (u"ࠫࡷ࡫ࡴࡳࡻࡗࡩࡸࡺࡳࡐࡰࡉࡥ࡮ࡲࡵࡳࡧࠪᴪ")}
class bstack1l1lll1ll1_opy_:
    @staticmethod
    def bstack1ll1111ll_opy_(config: dict) -> bool:
        bstack111lll1lll1_opy_ = config.get(bstack1l1_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡳࡸ࡮ࡵ࡮ࡴࠩᴫ"), {}).get(bstack1l1_opy_ (u"࠭ࡲࡦࡶࡵࡽ࡙࡫ࡳࡵࡵࡒࡲࡋࡧࡩ࡭ࡷࡵࡩࠬᴬ"), {})
        return bstack111lll1lll1_opy_.get(bstack1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨᴭ"), False)
    @staticmethod
    def bstack1ll1lll1l_opy_(config: dict) -> int:
        bstack111lll1lll1_opy_ = config.get(bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬᴮ"), {}).get(bstack1l1_opy_ (u"ࠩࡵࡩࡹࡸࡹࡕࡧࡶࡸࡸࡕ࡮ࡇࡣ࡬ࡰࡺࡸࡥࠨᴯ"), {})
        retries = 0
        if bstack1l1lll1ll1_opy_.bstack1ll1111ll_opy_(config):
            retries = bstack111lll1lll1_opy_.get(bstack1l1_opy_ (u"ࠪࡱࡦࡾࡒࡦࡶࡵ࡭ࡪࡹࠧᴰ"), 1)
        return retries
    @staticmethod
    def bstack11111l1l_opy_(config: dict) -> dict:
        bstack111lll1ll1l_opy_ = config.get(bstack1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨᴱ"), {})
        return {
            key: value for key, value in bstack111lll1ll1l_opy_.items() if key in bstack111lll1llll_opy_
        }