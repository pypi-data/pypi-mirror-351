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
import re
from enum import Enum
bstack11ll1ll11l_opy_ = {
  bstack1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᤴ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦࡴࠪᤵ"),
  bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᤶ"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡬ࡧࡼࠫᤷ"),
  bstack1l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᤸ"): bstack1l1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴ᤹ࠧ"),
  bstack1l1_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫ᤺"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡠࡹ࠶ࡧ᤻ࠬ"),
  bstack1l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ᤼"): bstack1l1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࠨ᤽"),
  bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ᤾"): bstack1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࠨ᤿"),
  bstack1l1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ᥀"): bstack1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ᥁"),
  bstack1l1_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫ᥂"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡥࡣࡷࡪࠫ᥃"),
  bstack1l1_opy_ (u"ࠧࡤࡱࡱࡷࡴࡲࡥࡍࡱࡪࡷࠬ᥄"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡱࡷࡴࡲࡥࠨ᥅"),
  bstack1l1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࠧ᥆"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࠧ᥇"),
  bstack1l1_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰࡐࡴ࡭ࡳࠨ᥈"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡐࡴ࡭ࡳࠨ᥉"),
  bstack1l1_opy_ (u"࠭ࡶࡪࡦࡨࡳࠬ᥊"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡶࡪࡦࡨࡳࠬ᥋"),
  bstack1l1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡏࡳ࡬ࡹࠧ᥌"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡏࡳ࡬ࡹࠧ᥍"),
  bstack1l1_opy_ (u"ࠪࡸࡪࡲࡥ࡮ࡧࡷࡶࡾࡒ࡯ࡨࡵࠪ᥎"): bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡸࡪࡲࡥ࡮ࡧࡷࡶࡾࡒ࡯ࡨࡵࠪ᥏"),
  bstack1l1_opy_ (u"ࠬ࡭ࡥࡰࡎࡲࡧࡦࡺࡩࡰࡰࠪᥐ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡭ࡥࡰࡎࡲࡧࡦࡺࡩࡰࡰࠪᥑ"),
  bstack1l1_opy_ (u"ࠧࡵ࡫ࡰࡩࡿࡵ࡮ࡦࠩᥒ"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡵ࡫ࡰࡩࡿࡵ࡮ࡦࠩᥓ"),
  bstack1l1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᥔ"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡱ࡫࡮ࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᥕ"),
  bstack1l1_opy_ (u"ࠫࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪᥖ"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪᥗ"),
  bstack1l1_opy_ (u"࠭ࡩࡥ࡮ࡨࡘ࡮ࡳࡥࡰࡷࡷࠫᥘ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡩࡥ࡮ࡨࡘ࡮ࡳࡥࡰࡷࡷࠫᥙ"),
  bstack1l1_opy_ (u"ࠨ࡯ࡤࡷࡰࡈࡡࡴ࡫ࡦࡅࡺࡺࡨࠨᥚ"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡯ࡤࡷࡰࡈࡡࡴ࡫ࡦࡅࡺࡺࡨࠨᥛ"),
  bstack1l1_opy_ (u"ࠪࡷࡪࡴࡤࡌࡧࡼࡷࠬᥜ"): bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡷࡪࡴࡤࡌࡧࡼࡷࠬᥝ"),
  bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱ࡚ࡥ࡮ࡺࠧᥞ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡵࡵࡱ࡚ࡥ࡮ࡺࠧᥟ"),
  bstack1l1_opy_ (u"ࠧࡩࡱࡶࡸࡸ࠭ᥠ"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡩࡱࡶࡸࡸ࠭ᥡ"),
  bstack1l1_opy_ (u"ࠩࡥࡪࡨࡧࡣࡩࡧࠪᥢ"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡪࡨࡧࡣࡩࡧࠪᥣ"),
  bstack1l1_opy_ (u"ࠫࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸࠬᥤ"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸࠬᥥ"),
  bstack1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡃࡰࡴࡶࡖࡪࡹࡴࡳ࡫ࡦࡸ࡮ࡵ࡮ࡴࠩᥦ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡤࡪࡵࡤࡦࡱ࡫ࡃࡰࡴࡶࡖࡪࡹࡴࡳ࡫ࡦࡸ࡮ࡵ࡮ࡴࠩᥧ"),
  bstack1l1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬᥨ"): bstack1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩᥩ"),
  bstack1l1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧᥪ"): bstack1l1_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡡࡰࡳࡧ࡯࡬ࡦࠩᥫ"),
  bstack1l1_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᥬ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡰࡱ࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᥭ"),
  bstack1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧ᥮"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧ᥯"),
  bstack1l1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡓࡶࡴ࡬ࡩ࡭ࡧࠪᥰ"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡱࡩࡹࡽ࡯ࡳ࡭ࡓࡶࡴ࡬ࡩ࡭ࡧࠪᥱ"),
  bstack1l1_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪᥲ"): bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭ᥳ"),
  bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨᥴ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨ᥵"),
  bstack1l1_opy_ (u"ࠨࡵࡲࡹࡷࡩࡥࠨ᥶"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡲࡹࡷࡩࡥࠨ᥷"),
  bstack1l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ᥸"): bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ᥹"),
  bstack1l1_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧ᥺"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧ᥻"),
  bstack1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡓࡪ࡯ࠪ᥼"): bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡦࡰࡤࡦࡱ࡫ࡓࡪ࡯ࠪ᥽"),
  bstack1l1_opy_ (u"ࠩࡶ࡭ࡲࡕࡰࡵ࡫ࡲࡲࡸ࠭᥾"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶ࡭ࡲࡕࡰࡵ࡫ࡲࡲࡸ࠭᥿"),
  bstack1l1_opy_ (u"ࠫࡺࡶ࡬ࡰࡣࡧࡑࡪࡪࡩࡢࠩᦀ"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡶ࡬ࡰࡣࡧࡑࡪࡪࡩࡢࠩᦁ"),
  bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᦂ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩᦃ"),
  bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᦄ"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᦅ")
}
bstack11l11ll1lll_opy_ = [
  bstack1l1_opy_ (u"ࠪࡳࡸ࠭ᦆ"),
  bstack1l1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧᦇ"),
  bstack1l1_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡖࡦࡴࡶ࡭ࡴࡴࠧᦈ"),
  bstack1l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫᦉ"),
  bstack1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫᦊ"),
  bstack1l1_opy_ (u"ࠨࡴࡨࡥࡱࡓ࡯ࡣ࡫࡯ࡩࠬᦋ"),
  bstack1l1_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩᦌ"),
]
bstack1l1111111_opy_ = {
  bstack1l1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬᦍ"): [bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠬᦎ"), bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡡࡑࡅࡒࡋࠧᦏ")],
  bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᦐ"): bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪᦑ"),
  bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᦒ"): bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡏࡃࡐࡉࠬᦓ"),
  bstack1l1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᦔ"): bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡗࡕࡊࡆࡅࡗࡣࡓࡇࡍࡆࠩᦕ"),
  bstack1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧᦖ"): bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨᦗ"),
  bstack1l1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧᦘ"): bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡃࡕࡅࡑࡒࡅࡍࡕࡢࡔࡊࡘ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࠩᦙ"),
  bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ᦚ"): bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡏࡓࡈࡇࡌࠨᦛ"),
  bstack1l1_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࡗࡩࡸࡺࡳࠨᦜ"): bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࡢࡘࡊ࡙ࡔࡔࠩᦝ"),
  bstack1l1_opy_ (u"࠭ࡡࡱࡲࠪᦞ"): [bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡑࡒࡢࡍࡉ࠭ᦟ"), bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡒࡓࠫᦠ")],
  bstack1l1_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫᦡ"): bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡖࡈࡐࡥࡌࡐࡉࡏࡉ࡛ࡋࡌࠨᦢ"),
  bstack1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᦣ"): bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨᦤ"),
  bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᦥ"): bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡔࡈࡓࡆࡔ࡙ࡅࡇࡏࡌࡊࡖ࡜ࠫᦦ"),
  bstack1l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᦧ"): bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡘࡖࡇࡕࡓࡄࡃࡏࡉࠬᦨ")
}
bstack1l1ll111_opy_ = {
  bstack1l1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬᦩ"): [bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡲࡠࡰࡤࡱࡪ࠭ᦪ"), bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᦫ")],
  bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ᦬"): [bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡥ࡫ࡦࡻࠪ᦭"), bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ᦮")],
  bstack1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ᦯"): bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᦰ"),
  bstack1l1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᦱ"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᦲ"),
  bstack1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᦳ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᦴ"),
  bstack1l1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᦵ"): [bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡳࡴࠬᦶ"), bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩᦷ")],
  bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨᦸ"): bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࠪᦹ"),
  bstack1l1_opy_ (u"࠭ࡲࡦࡴࡸࡲ࡙࡫ࡳࡵࡵࠪᦺ"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡲࡦࡴࡸࡲ࡙࡫ࡳࡵࡵࠪᦻ"),
  bstack1l1_opy_ (u"ࠨࡣࡳࡴࠬᦼ"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴࠬᦽ"),
  bstack1l1_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᦾ"): bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴ࡭ࡌࡦࡸࡨࡰࠬᦿ"),
  bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᧀ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᧁ")
}
bstack11ll1l1ll_opy_ = {
  bstack1l1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪᧂ"): bstack1l1_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᧃ"),
  bstack1l1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫᧄ"): [bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡱ࡫࡮ࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᧅ"), bstack1l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᧆ")],
  bstack1l1_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪᧇ"): bstack1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᧈ"),
  bstack1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫᧉ"): bstack1l1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ᧊"),
  bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ᧋"): [bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫ᧌"), bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧࠪ᧍")],
  bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᧎"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᧏"),
  bstack1l1_opy_ (u"ࠧࡳࡧࡤࡰࡒࡵࡢࡪ࡮ࡨࠫ᧐"): bstack1l1_opy_ (u"ࠨࡴࡨࡥࡱࡥ࡭ࡰࡤ࡬ࡰࡪ࠭᧑"),
  bstack1l1_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩ᧒"): [bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡴࡵ࡯ࡵ࡮ࡡࡹࡩࡷࡹࡩࡰࡰࠪ᧓"), bstack1l1_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᧔")],
  bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡎࡴࡳࡦࡥࡸࡶࡪࡉࡥࡳࡶࡶࠫ᧕"): [bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹࡹࠧ᧖"), bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡓࡴ࡮ࡆࡩࡷࡺࠧ᧗")]
}
bstack111l1l111_opy_ = [
  bstack1l1_opy_ (u"ࠨࡣࡦࡧࡪࡶࡴࡊࡰࡶࡩࡨࡻࡲࡦࡅࡨࡶࡹࡹࠧ᧘"),
  bstack1l1_opy_ (u"ࠩࡳࡥ࡬࡫ࡌࡰࡣࡧࡗࡹࡸࡡࡵࡧࡪࡽࠬ᧙"),
  bstack1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩ᧚"),
  bstack1l1_opy_ (u"ࠫࡸ࡫ࡴࡘ࡫ࡱࡨࡴࡽࡒࡦࡥࡷࠫ᧛"),
  bstack1l1_opy_ (u"ࠬࡺࡩ࡮ࡧࡲࡹࡹࡹࠧ᧜"),
  bstack1l1_opy_ (u"࠭ࡳࡵࡴ࡬ࡧࡹࡌࡩ࡭ࡧࡌࡲࡹ࡫ࡲࡢࡥࡷࡥࡧ࡯࡬ࡪࡶࡼࠫ᧝"),
  bstack1l1_opy_ (u"ࠧࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡓࡶࡴࡳࡰࡵࡄࡨ࡬ࡦࡼࡩࡰࡴࠪ᧞"),
  bstack1l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᧟"),
  bstack1l1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ᧠"),
  bstack1l1_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ᧡"),
  bstack1l1_opy_ (u"ࠫࡸ࡫࠺ࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᧢"),
  bstack1l1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭᧣"),
]
bstack1l11l1ll_opy_ = [
  bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ᧤"),
  bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ᧥"),
  bstack1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ᧦"),
  bstack1l1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ᧧"),
  bstack1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭᧨"),
  bstack1l1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭᧩"),
  bstack1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ᧪"),
  bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ᧫"),
  bstack1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ᧬"),
  bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸ࠭᧭"),
  bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭᧮"),
  bstack1l1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠬ᧯"),
  bstack1l1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰࡘࡦ࡭ࠧ᧰"),
  bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩ᧱"),
  bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᧲"),
  bstack1l1_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ᧳"),
  bstack1l1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠷ࠧ᧴"),
  bstack1l1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠲ࠨ᧵"),
  bstack1l1_opy_ (u"ࠪࡇ࡚࡙ࡔࡐࡏࡢࡘࡆࡍ࡟࠴ࠩ᧶"),
  bstack1l1_opy_ (u"ࠫࡈ࡛ࡓࡕࡑࡐࡣ࡙ࡇࡇࡠ࠶ࠪ᧷"),
  bstack1l1_opy_ (u"ࠬࡉࡕࡔࡖࡒࡑࡤ࡚ࡁࡈࡡ࠸ࠫ᧸"),
  bstack1l1_opy_ (u"࠭ࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢ࠺ࠬ᧹"),
  bstack1l1_opy_ (u"ࠧࡄࡗࡖࡘࡔࡓ࡟ࡕࡃࡊࡣ࠼࠭᧺"),
  bstack1l1_opy_ (u"ࠨࡅࡘࡗ࡙ࡕࡍࡠࡖࡄࡋࡤ࠾ࠧ᧻"),
  bstack1l1_opy_ (u"ࠩࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࠹ࠨ᧼"),
  bstack1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᧽"),
  bstack1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᧾"),
  bstack1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨ᧿"),
  bstack1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁࡶࡶࡲࡇࡦࡶࡴࡶࡴࡨࡐࡴ࡭ࡳࠨᨀ"),
  bstack1l1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᨁ"),
  bstack1l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬᨂ"),
  bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࡕࡰࡵ࡫ࡲࡲࡸ࠭ᨃ")
]
bstack11l11l11l1l_opy_ = [
  bstack1l1_opy_ (u"ࠪࡹࡵࡲ࡯ࡢࡦࡐࡩࡩ࡯ࡡࠨᨄ"),
  bstack1l1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᨅ"),
  bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᨆ"),
  bstack1l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫᨇ"),
  bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡕࡸࡩࡰࡴ࡬ࡸࡾ࠭ᨈ"),
  bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᨉ"),
  bstack1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡕࡣࡪࠫᨊ"),
  bstack1l1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᨋ"),
  bstack1l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᨌ"),
  bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪᨍ"),
  bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᨎ"),
  bstack1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ᨏ"),
  bstack1l1_opy_ (u"ࠨࡱࡶࠫᨐ"),
  bstack1l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᨑ"),
  bstack1l1_opy_ (u"ࠪ࡬ࡴࡹࡴࡴࠩᨒ"),
  bstack1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ᨓ"),
  bstack1l1_opy_ (u"ࠬࡸࡥࡨ࡫ࡲࡲࠬᨔ"),
  bstack1l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨᨕ"),
  bstack1l1_opy_ (u"ࠧ࡮ࡣࡦ࡬࡮ࡴࡥࠨᨖ"),
  bstack1l1_opy_ (u"ࠨࡴࡨࡷࡴࡲࡵࡵ࡫ࡲࡲࠬᨗ"),
  bstack1l1_opy_ (u"ࠩ࡬ࡨࡱ࡫ࡔࡪ࡯ࡨࡳࡺࡺᨘࠧ"),
  bstack1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧᨙ"),
  bstack1l1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱࠪᨚ"),
  bstack1l1_opy_ (u"ࠬࡴ࡯ࡑࡣࡪࡩࡑࡵࡡࡥࡖ࡬ࡱࡪࡵࡵࡵࠩᨛ"),
  bstack1l1_opy_ (u"࠭ࡢࡧࡥࡤࡧ࡭࡫ࠧ᨜"),
  bstack1l1_opy_ (u"ࠧࡥࡧࡥࡹ࡬࠭᨝"),
  bstack1l1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡔࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬ᨞"),
  bstack1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡕࡨࡲࡩࡑࡥࡺࡵࠪ᨟"),
  bstack1l1_opy_ (u"ࠪࡶࡪࡧ࡬ࡎࡱࡥ࡭ࡱ࡫ࠧᨠ"),
  bstack1l1_opy_ (u"ࠫࡳࡵࡐࡪࡲࡨࡰ࡮ࡴࡥࠨᨡ"),
  bstack1l1_opy_ (u"ࠬࡩࡨࡦࡥ࡮࡙ࡗࡒࠧᨢ"),
  bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᨣ"),
  bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡃࡰࡱ࡮࡭ࡪࡹࠧᨤ"),
  bstack1l1_opy_ (u"ࠨࡥࡤࡴࡹࡻࡲࡦࡅࡵࡥࡸ࡮ࠧᨥ"),
  bstack1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭ᨦ"),
  bstack1l1_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᨧ"),
  bstack1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᨨ"),
  bstack1l1_opy_ (u"ࠬࡴ࡯ࡃ࡮ࡤࡲࡰࡖ࡯࡭࡮࡬ࡲ࡬࠭ᨩ"),
  bstack1l1_opy_ (u"࠭࡭ࡢࡵ࡮ࡗࡪࡴࡤࡌࡧࡼࡷࠬᨪ"),
  bstack1l1_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡌࡰࡩࡶࠫᨫ"),
  bstack1l1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡊࡦࠪᨬ"),
  bstack1l1_opy_ (u"ࠩࡧࡩࡩ࡯ࡣࡢࡶࡨࡨࡉ࡫ࡶࡪࡥࡨࠫᨭ"),
  bstack1l1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡓࡥࡷࡧ࡭ࡴࠩᨮ"),
  bstack1l1_opy_ (u"ࠫࡵ࡮࡯࡯ࡧࡑࡹࡲࡨࡥࡳࠩᨯ"),
  bstack1l1_opy_ (u"ࠬࡴࡥࡵࡹࡲࡶࡰࡒ࡯ࡨࡵࠪᨰ"),
  bstack1l1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡓࡵࡺࡩࡰࡰࡶࠫᨱ"),
  bstack1l1_opy_ (u"ࠧࡤࡱࡱࡷࡴࡲࡥࡍࡱࡪࡷࠬᨲ"),
  bstack1l1_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨᨳ"),
  bstack1l1_opy_ (u"ࠩࡤࡴࡵ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭ᨴ"),
  bstack1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡅ࡭ࡴࡳࡥࡵࡴ࡬ࡧࠬᨵ"),
  bstack1l1_opy_ (u"ࠫࡻ࡯ࡤࡦࡱ࡙࠶ࠬᨶ"),
  bstack1l1_opy_ (u"ࠬࡳࡩࡥࡕࡨࡷࡸ࡯࡯࡯ࡋࡱࡷࡹࡧ࡬࡭ࡃࡳࡴࡸ࠭ᨷ"),
  bstack1l1_opy_ (u"࠭ࡥࡴࡲࡵࡩࡸࡹ࡯ࡔࡧࡵࡺࡪࡸࠧᨸ"),
  bstack1l1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭ᨹ"),
  bstack1l1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࡆࡨࡵ࠭ᨺ"),
  bstack1l1_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩᨻ"),
  bstack1l1_opy_ (u"ࠪࡷࡾࡴࡣࡕ࡫ࡰࡩ࡜࡯ࡴࡩࡐࡗࡔࠬᨼ"),
  bstack1l1_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩᨽ"),
  bstack1l1_opy_ (u"ࠬ࡭ࡰࡴࡎࡲࡧࡦࡺࡩࡰࡰࠪᨾ"),
  bstack1l1_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡐࡳࡱࡩ࡭ࡱ࡫ࠧᨿ"),
  bstack1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡎࡦࡶࡺࡳࡷࡱࠧᩀ"),
  bstack1l1_opy_ (u"ࠨࡨࡲࡶࡨ࡫ࡃࡩࡣࡱ࡫ࡪࡐࡡࡳࠩᩁ"),
  bstack1l1_opy_ (u"ࠩࡻࡱࡸࡐࡡࡳࠩᩂ"),
  bstack1l1_opy_ (u"ࠪࡼࡲࡾࡊࡢࡴࠪᩃ"),
  bstack1l1_opy_ (u"ࠫࡲࡧࡳ࡬ࡅࡲࡱࡲࡧ࡮ࡥࡵࠪᩄ"),
  bstack1l1_opy_ (u"ࠬࡳࡡࡴ࡭ࡅࡥࡸ࡯ࡣࡂࡷࡷ࡬ࠬᩅ"),
  bstack1l1_opy_ (u"࠭ࡷࡴࡎࡲࡧࡦࡲࡓࡶࡲࡳࡳࡷࡺࠧᩆ"),
  bstack1l1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡄࡱࡵࡷࡗ࡫ࡳࡵࡴ࡬ࡧࡹ࡯࡯࡯ࡵࠪᩇ"),
  bstack1l1_opy_ (u"ࠨࡣࡳࡴ࡛࡫ࡲࡴ࡫ࡲࡲࠬᩈ"),
  bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡰࡵࡋࡱࡷࡪࡩࡵࡳࡧࡆࡩࡷࡺࡳࠨᩉ"),
  bstack1l1_opy_ (u"ࠪࡶࡪࡹࡩࡨࡰࡄࡴࡵ࠭ᩊ"),
  bstack1l1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡩ࡮ࡣࡷ࡭ࡴࡴࡳࠨᩋ"),
  bstack1l1_opy_ (u"ࠬࡩࡡ࡯ࡣࡵࡽࠬᩌ"),
  bstack1l1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧᩍ"),
  bstack1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧᩎ"),
  bstack1l1_opy_ (u"ࠨ࡫ࡨࠫᩏ"),
  bstack1l1_opy_ (u"ࠩࡨࡨ࡬࡫ࠧᩐ"),
  bstack1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪᩑ"),
  bstack1l1_opy_ (u"ࠫࡶࡻࡥࡶࡧࠪᩒ"),
  bstack1l1_opy_ (u"ࠬ࡯࡮ࡵࡧࡵࡲࡦࡲࠧᩓ"),
  bstack1l1_opy_ (u"࠭ࡡࡱࡲࡖࡸࡴࡸࡥࡄࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠧᩔ"),
  bstack1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡃࡢ࡯ࡨࡶࡦࡏ࡭ࡢࡩࡨࡍࡳࡰࡥࡤࡶ࡬ࡳࡳ࠭ᩕ"),
  bstack1l1_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸࡋࡸࡤ࡮ࡸࡨࡪࡎ࡯ࡴࡶࡶࠫᩖ"),
  bstack1l1_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡏࡳ࡬ࡹࡉ࡯ࡥ࡯ࡹࡩ࡫ࡈࡰࡵࡷࡷࠬᩗ"),
  bstack1l1_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡄࡴࡵ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧᩘ"),
  bstack1l1_opy_ (u"ࠫࡷ࡫ࡳࡦࡴࡹࡩࡉ࡫ࡶࡪࡥࡨࠫᩙ"),
  bstack1l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬᩚ"),
  bstack1l1_opy_ (u"࠭ࡳࡦࡰࡧࡏࡪࡿࡳࠨᩛ"),
  bstack1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡐࡢࡵࡶࡧࡴࡪࡥࠨᩜ"),
  bstack1l1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡊࡱࡶࡈࡪࡼࡩࡤࡧࡖࡩࡹࡺࡩ࡯ࡩࡶࠫᩝ"),
  bstack1l1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡃࡸࡨ࡮ࡵࡉ࡯࡬ࡨࡧࡹ࡯࡯࡯ࠩᩞ"),
  bstack1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡄࡴࡵࡲࡥࡑࡣࡼࠫ᩟"),
  bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ᩠ࠬ"),
  bstack1l1_opy_ (u"ࠬࡽࡤࡪࡱࡖࡩࡷࡼࡩࡤࡧࠪᩡ"),
  bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨᩢ"),
  bstack1l1_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡄࡴࡲࡷࡸ࡙ࡩࡵࡧࡗࡶࡦࡩ࡫ࡪࡰࡪࠫᩣ"),
  bstack1l1_opy_ (u"ࠨࡪ࡬࡫࡭ࡉ࡯࡯ࡶࡵࡥࡸࡺࠧᩤ"),
  bstack1l1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡒࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࡸ࠭ᩥ"),
  bstack1l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡖ࡭ࡲ࠭ᩦ"),
  bstack1l1_opy_ (u"ࠫࡸ࡯࡭ࡐࡲࡷ࡭ࡴࡴࡳࠨᩧ"),
  bstack1l1_opy_ (u"ࠬࡸࡥ࡮ࡱࡹࡩࡎࡕࡓࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࡑࡵࡣࡢ࡮࡬ࡾࡦࡺࡩࡰࡰࠪᩨ"),
  bstack1l1_opy_ (u"࠭ࡨࡰࡵࡷࡒࡦࡳࡥࠨᩩ"),
  bstack1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᩪ"),
  bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᩫ"),
  bstack1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨᩬ"),
  bstack1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᩭ"),
  bstack1l1_opy_ (u"ࠫࡵࡧࡧࡦࡎࡲࡥࡩ࡙ࡴࡳࡣࡷࡩ࡬ࡿࠧᩮ"),
  bstack1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫᩯ"),
  bstack1l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡳࡺࡺࡳࠨᩰ"),
  bstack1l1_opy_ (u"ࠧࡶࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡓࡶࡴࡳࡰࡵࡄࡨ࡬ࡦࡼࡩࡰࡴࠪᩱ")
]
bstack1ll11l111_opy_ = {
  bstack1l1_opy_ (u"ࠨࡸࠪᩲ"): bstack1l1_opy_ (u"ࠩࡹࠫᩳ"),
  bstack1l1_opy_ (u"ࠪࡪࠬᩴ"): bstack1l1_opy_ (u"ࠫ࡫࠭᩵"),
  bstack1l1_opy_ (u"ࠬ࡬࡯ࡳࡥࡨࠫ᩶"): bstack1l1_opy_ (u"࠭ࡦࡰࡴࡦࡩࠬ᩷"),
  bstack1l1_opy_ (u"ࠧࡰࡰ࡯ࡽࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭᩸"): bstack1l1_opy_ (u"ࠨࡱࡱࡰࡾࡇࡵࡵࡱࡰࡥࡹ࡫ࠧ᩹"),
  bstack1l1_opy_ (u"ࠩࡩࡳࡷࡩࡥ࡭ࡱࡦࡥࡱ࠭᩺"): bstack1l1_opy_ (u"ࠪࡪࡴࡸࡣࡦ࡮ࡲࡧࡦࡲࠧ᩻"),
  bstack1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻ࡫ࡳࡸࡺࠧ᩼"): bstack1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡌࡴࡹࡴࠨ᩽"),
  bstack1l1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡵࡵࡲࡵࠩ᩾"): bstack1l1_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶ᩿ࠪ"),
  bstack1l1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫ᪀"): bstack1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡖࡵࡨࡶࠬ᪁"),
  bstack1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡲࡤࡷࡸ࠭᪂"): bstack1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡥࡸࡹࠧ᪃"),
  bstack1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡪࡲࡷࡹ࠭᪄"): bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡋࡳࡸࡺࠧ᪅"),
  bstack1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡴࡸࡴࠨ᪆"): bstack1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡵࡲࡵࠩ᪇"),
  bstack1l1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡻࡳࡦࡴࠪ᪈"): bstack1l1_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬ᪉"),
  bstack1l1_opy_ (u"ࠫ࠲ࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡷࡶࡩࡷ࠭᪊"): bstack1l1_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡘࡷࡪࡸࠧ᪋"),
  bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡵࡸ࡯ࡹࡻࡳࡥࡸࡹࠧ᪌"): bstack1l1_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩ᪍"),
  bstack1l1_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡱࡴࡲࡼࡾࡶࡡࡴࡵࠪ᪎"): bstack1l1_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡐࡢࡵࡶࠫ᪏"),
  bstack1l1_opy_ (u"ࠪࡦ࡮ࡴࡡࡳࡻࡳࡥࡹ࡮ࠧ᪐"): bstack1l1_opy_ (u"ࠫࡧ࡯࡮ࡢࡴࡼࡴࡦࡺࡨࠨ᪑"),
  bstack1l1_opy_ (u"ࠬࡶࡡࡤࡨ࡬ࡰࡪ࠭᪒"): bstack1l1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩ᪓"),
  bstack1l1_opy_ (u"ࠧࡱࡣࡦ࠱࡫࡯࡬ࡦࠩ᪔"): bstack1l1_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫ᪕"),
  bstack1l1_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬ᪖"): bstack1l1_opy_ (u"ࠪ࠱ࡵࡧࡣ࠮ࡨ࡬ࡰࡪ࠭᪗"),
  bstack1l1_opy_ (u"ࠫࡱࡵࡧࡧ࡫࡯ࡩࠬ᪘"): bstack1l1_opy_ (u"ࠬࡲ࡯ࡨࡨ࡬ࡰࡪ࠭᪙"),
  bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ᪚"): bstack1l1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ᪛"),
  bstack1l1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭࠮ࡴࡨࡴࡪࡧࡴࡦࡴࠪ᪜"): bstack1l1_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡔࡨࡴࡪࡧࡴࡦࡴࠪ᪝")
}
bstack11l11ll111l_opy_ = bstack1l1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳࡬࡯ࡴࡩࡷࡥ࠲ࡨࡵ࡭࠰ࡲࡨࡶࡨࡿ࠯ࡤ࡮࡬࠳ࡷ࡫࡬ࡦࡣࡶࡩࡸ࠵࡬ࡢࡶࡨࡷࡹ࠵ࡤࡰࡹࡱࡰࡴࡧࡤࠣ᪞")
bstack11l111lll11_opy_ = bstack1l1_opy_ (u"ࠦ࠴ࡶࡥࡳࡥࡼ࠳࡭࡫ࡡ࡭ࡶ࡫ࡧ࡭࡫ࡣ࡬ࠤ᪟")
bstack11l111ll1_opy_ = bstack1l1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡥࡥࡵ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡳࡦࡰࡧࡣࡸࡪ࡫ࡠࡧࡹࡩࡳࡺࡳࠣ᪠")
bstack1l11lll1l1_opy_ = bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡸࡦ࠲࡬ࡺࡨࠧ᪡")
bstack1l1llll111_opy_ = bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠪ᪢")
bstack1ll11l1ll1_opy_ = bstack1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠬ᪣")
bstack11l11l111l1_opy_ = {
  bstack1l1_opy_ (u"ࠩࡦࡶ࡮ࡺࡩࡤࡣ࡯ࠫ᪤"): 50,
  bstack1l1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ᪥"): 40,
  bstack1l1_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬ᪦"): 30,
  bstack1l1_opy_ (u"ࠬ࡯࡮ࡧࡱࠪᪧ"): 20,
  bstack1l1_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬ᪨"): 10
}
bstack1l1ll11l1l_opy_ = bstack11l11l111l1_opy_[bstack1l1_opy_ (u"ࠧࡪࡰࡩࡳࠬ᪩")]
bstack1l1l11l1ll_opy_ = bstack1l1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧ᪪")
bstack1ll1ll1l1_opy_ = bstack1l1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧ᪫")
bstack11lllll111_opy_ = bstack1l1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩ᪬")
bstack1lll111l11_opy_ = bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࠪ᪭")
bstack11l1ll11l1_opy_ = bstack1l1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹࠦࡡ࡯ࡦࠣࡴࡾࡺࡥࡴࡶ࠰ࡷࡪࡲࡥ࡯࡫ࡸࡱࠥࡶࡡࡤ࡭ࡤ࡫ࡪࡹ࠮ࠡࡢࡳ࡭ࡵࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺࠠࡱࡻࡷࡩࡸࡺ࠭ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡢࠪ᪮")
bstack11l11ll1l1l_opy_ = [bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧ᪯"), bstack1l1_opy_ (u"࡚ࠧࡑࡘࡖࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧ᪰")]
bstack11l11ll1ll1_opy_ = [bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ᪱"), bstack1l1_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫ᪲")]
bstack1ll1111l11_opy_ = re.compile(bstack1l1_opy_ (u"ࠪࡢࡠࡢ࡜ࡸ࠯ࡠ࠯࠿࠴ࠪࠥࠩ᪳"))
bstack1ll1lll1l1_opy_ = [
  bstack1l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡏࡣࡰࡩࠬ᪴"),
  bstack1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴ᪵ࠧ"),
  bstack1l1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧ᪶ࠪ"),
  bstack1l1_opy_ (u"ࠧ࡯ࡧࡺࡇࡴࡳ࡭ࡢࡰࡧࡘ࡮ࡳࡥࡰࡷࡷ᪷ࠫ"),
  bstack1l1_opy_ (u"ࠨࡣࡳࡴ᪸ࠬ"),
  bstack1l1_opy_ (u"ࠩࡸࡨ࡮ࡪ᪹ࠧ"),
  bstack1l1_opy_ (u"ࠪࡰࡦࡴࡧࡶࡣࡪࡩ᪺ࠬ"),
  bstack1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡨࠫ᪻"),
  bstack1l1_opy_ (u"ࠬࡵࡲࡪࡧࡱࡸࡦࡺࡩࡰࡰࠪ᪼"),
  bstack1l1_opy_ (u"࠭ࡡࡶࡶࡲ࡛ࡪࡨࡶࡪࡧࡺ᪽ࠫ"),
  bstack1l1_opy_ (u"ࠧ࡯ࡱࡕࡩࡸ࡫ࡴࠨ᪾"), bstack1l1_opy_ (u"ࠨࡨࡸࡰࡱࡘࡥࡴࡧࡷᪿࠫ"),
  bstack1l1_opy_ (u"ࠩࡦࡰࡪࡧࡲࡔࡻࡶࡸࡪࡳࡆࡪ࡮ࡨࡷᫀࠬ"),
  bstack1l1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡖ࡬ࡱ࡮ࡴࡧࡴࠩ᫁"),
  bstack1l1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡔࡪࡸࡦࡰࡴࡰࡥࡳࡩࡥࡍࡱࡪ࡫࡮ࡴࡧࠨ᫂"),
  bstack1l1_opy_ (u"ࠬࡵࡴࡩࡧࡵࡅࡵࡶࡳࠨ᫃"),
  bstack1l1_opy_ (u"࠭ࡰࡳ࡫ࡱࡸࡕࡧࡧࡦࡕࡲࡹࡷࡩࡥࡐࡰࡉ࡭ࡳࡪࡆࡢ࡫࡯ࡹࡷ࡫᫄ࠧ"),
  bstack1l1_opy_ (u"ࠧࡢࡲࡳࡅࡨࡺࡩࡷ࡫ࡷࡽࠬ᫅"), bstack1l1_opy_ (u"ࠨࡣࡳࡴࡕࡧࡣ࡬ࡣࡪࡩࠬ᫆"), bstack1l1_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡄࡧࡹ࡯ࡶࡪࡶࡼࠫ᫇"), bstack1l1_opy_ (u"ࠪࡥࡵࡶࡗࡢ࡫ࡷࡔࡦࡩ࡫ࡢࡩࡨࠫ᫈"), bstack1l1_opy_ (u"ࠫࡦࡶࡰࡘࡣ࡬ࡸࡉࡻࡲࡢࡶ࡬ࡳࡳ࠭᫉"),
  bstack1l1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡗ࡫ࡡࡥࡻࡗ࡭ࡲ࡫࡯ࡶࡶ᫊ࠪ"),
  bstack1l1_opy_ (u"࠭ࡡ࡭࡮ࡲࡻ࡙࡫ࡳࡵࡒࡤࡧࡰࡧࡧࡦࡵࠪ᫋"),
  bstack1l1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡄࡱࡹࡩࡷࡧࡧࡦࠩᫌ"), bstack1l1_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡅࡲࡺࡪࡸࡡࡨࡧࡈࡲࡩࡏ࡮ࡵࡧࡱࡸࠬᫍ"),
  bstack1l1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡇࡩࡻ࡯ࡣࡦࡔࡨࡥࡩࡿࡔࡪ࡯ࡨࡳࡺࡺࠧᫎ"),
  bstack1l1_opy_ (u"ࠪࡥࡩࡨࡐࡰࡴࡷࠫ᫏"),
  bstack1l1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡉ࡫ࡶࡪࡥࡨࡗࡴࡩ࡫ࡦࡶࠪ᫐"),
  bstack1l1_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡏ࡮ࡴࡶࡤࡰࡱ࡚ࡩ࡮ࡧࡲࡹࡹ࠭᫑"),
  bstack1l1_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡉ࡯ࡵࡷࡥࡱࡲࡐࡢࡶ࡫ࠫ᫒"),
  bstack1l1_opy_ (u"ࠧࡢࡸࡧࠫ᫓"), bstack1l1_opy_ (u"ࠨࡣࡹࡨࡑࡧࡵ࡯ࡥ࡫ࡘ࡮ࡳࡥࡰࡷࡷࠫ᫔"), bstack1l1_opy_ (u"ࠩࡤࡺࡩࡘࡥࡢࡦࡼࡘ࡮ࡳࡥࡰࡷࡷࠫ᫕"), bstack1l1_opy_ (u"ࠪࡥࡻࡪࡁࡳࡩࡶࠫ᫖"),
  bstack1l1_opy_ (u"ࠫࡺࡹࡥࡌࡧࡼࡷࡹࡵࡲࡦࠩ᫗"), bstack1l1_opy_ (u"ࠬࡱࡥࡺࡵࡷࡳࡷ࡫ࡐࡢࡶ࡫ࠫ᫘"), bstack1l1_opy_ (u"࠭࡫ࡦࡻࡶࡸࡴࡸࡥࡑࡣࡶࡷࡼࡵࡲࡥࠩ᫙"),
  bstack1l1_opy_ (u"ࠧ࡬ࡧࡼࡅࡱ࡯ࡡࡴࠩ᫚"), bstack1l1_opy_ (u"ࠨ࡭ࡨࡽࡕࡧࡳࡴࡹࡲࡶࡩ࠭᫛"),
  bstack1l1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࠫ᫜"), bstack1l1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡃࡵ࡫ࡸ࠭᫝"), bstack1l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡈࡼࡪࡩࡵࡵࡣࡥࡰࡪࡊࡩࡳࠩ᫞"), bstack1l1_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡇ࡭ࡸ࡯࡮ࡧࡐࡥࡵࡶࡩ࡯ࡩࡉ࡭ࡱ࡫ࠧ᫟"), bstack1l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶ࡚ࡹࡥࡔࡻࡶࡸࡪࡳࡅࡹࡧࡦࡹࡹࡧࡢ࡭ࡧࠪ᫠"),
  bstack1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡖ࡯ࡳࡶࠪ᫡"), bstack1l1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡐࡰࡴࡷࡷࠬ᫢"),
  bstack1l1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡅ࡫ࡶࡥࡧࡲࡥࡃࡷ࡬ࡰࡩࡉࡨࡦࡥ࡮ࠫ᫣"),
  bstack1l1_opy_ (u"ࠪࡥࡺࡺ࡯ࡘࡧࡥࡺ࡮࡫ࡷࡕ࡫ࡰࡩࡴࡻࡴࠨ᫤"),
  bstack1l1_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡅࡨࡺࡩࡰࡰࠪ᫥"), bstack1l1_opy_ (u"ࠬ࡯࡮ࡵࡧࡱࡸࡈࡧࡴࡦࡩࡲࡶࡾ࠭᫦"), bstack1l1_opy_ (u"࠭ࡩ࡯ࡶࡨࡲࡹࡌ࡬ࡢࡩࡶࠫ᫧"), bstack1l1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡡ࡭ࡋࡱࡸࡪࡴࡴࡂࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ᫨"),
  bstack1l1_opy_ (u"ࠨࡦࡲࡲࡹ࡙ࡴࡰࡲࡄࡴࡵࡕ࡮ࡓࡧࡶࡩࡹ࠭᫩"),
  bstack1l1_opy_ (u"ࠩࡸࡲ࡮ࡩ࡯ࡥࡧࡎࡩࡾࡨ࡯ࡢࡴࡧࠫ᫪"), bstack1l1_opy_ (u"ࠪࡶࡪࡹࡥࡵࡍࡨࡽࡧࡵࡡࡳࡦࠪ᫫"),
  bstack1l1_opy_ (u"ࠫࡳࡵࡓࡪࡩࡱࠫ᫬"),
  bstack1l1_opy_ (u"ࠬ࡯ࡧ࡯ࡱࡵࡩ࡚ࡴࡩ࡮ࡲࡲࡶࡹࡧ࡮ࡵࡘ࡬ࡩࡼࡹࠧ᫭"),
  bstack1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡁ࡯ࡦࡵࡳ࡮ࡪࡗࡢࡶࡦ࡬ࡪࡸࡳࠨ᫮"),
  bstack1l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᫯"),
  bstack1l1_opy_ (u"ࠨࡴࡨࡧࡷ࡫ࡡࡵࡧࡆ࡬ࡷࡵ࡭ࡦࡆࡵ࡭ࡻ࡫ࡲࡔࡧࡶࡷ࡮ࡵ࡮ࡴࠩ᫰"),
  bstack1l1_opy_ (u"ࠩࡱࡥࡹ࡯ࡶࡦ࡙ࡨࡦࡘࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠨ᫱"),
  bstack1l1_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡗࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡐࡢࡶ࡫ࠫ᫲"),
  bstack1l1_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡘࡶࡥࡦࡦࠪ᫳"),
  bstack1l1_opy_ (u"ࠬ࡭ࡰࡴࡇࡱࡥࡧࡲࡥࡥࠩ᫴"),
  bstack1l1_opy_ (u"࠭ࡩࡴࡊࡨࡥࡩࡲࡥࡴࡵࠪ᫵"),
  bstack1l1_opy_ (u"ࠧࡢࡦࡥࡉࡽ࡫ࡣࡕ࡫ࡰࡩࡴࡻࡴࠨ᫶"),
  bstack1l1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡥࡔࡥࡵ࡭ࡵࡺࠧ᫷"),
  bstack1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡄࡦࡸ࡬ࡧࡪࡏ࡮ࡪࡶ࡬ࡥࡱ࡯ࡺࡢࡶ࡬ࡳࡳ࠭᫸"),
  bstack1l1_opy_ (u"ࠪࡥࡺࡺ࡯ࡈࡴࡤࡲࡹࡖࡥࡳ࡯࡬ࡷࡸ࡯࡯࡯ࡵࠪ᫹"),
  bstack1l1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡓࡧࡴࡶࡴࡤࡰࡔࡸࡩࡦࡰࡷࡥࡹ࡯࡯࡯ࠩ᫺"),
  bstack1l1_opy_ (u"ࠬࡹࡹࡴࡶࡨࡱࡕࡵࡲࡵࠩ᫻"),
  bstack1l1_opy_ (u"࠭ࡲࡦ࡯ࡲࡸࡪࡇࡤࡣࡊࡲࡷࡹ࠭᫼"),
  bstack1l1_opy_ (u"ࠧࡴ࡭࡬ࡴ࡚ࡴ࡬ࡰࡥ࡮ࠫ᫽"), bstack1l1_opy_ (u"ࠨࡷࡱࡰࡴࡩ࡫ࡕࡻࡳࡩࠬ᫾"), bstack1l1_opy_ (u"ࠩࡸࡲࡱࡵࡣ࡬ࡍࡨࡽࠬ᫿"),
  bstack1l1_opy_ (u"ࠪࡥࡺࡺ࡯ࡍࡣࡸࡲࡨ࡮ࠧᬀ"),
  bstack1l1_opy_ (u"ࠫࡸࡱࡩࡱࡎࡲ࡫ࡨࡧࡴࡄࡣࡳࡸࡺࡸࡥࠨᬁ"),
  bstack1l1_opy_ (u"ࠬࡻ࡮ࡪࡰࡶࡸࡦࡲ࡬ࡐࡶ࡫ࡩࡷࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠧᬂ"),
  bstack1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡗࡪࡰࡧࡳࡼࡇ࡮ࡪ࡯ࡤࡸ࡮ࡵ࡮ࠨᬃ"),
  bstack1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࡚࡯ࡰ࡮ࡶ࡚ࡪࡸࡳࡪࡱࡱࠫᬄ"),
  bstack1l1_opy_ (u"ࠨࡧࡱࡪࡴࡸࡣࡦࡃࡳࡴࡎࡴࡳࡵࡣ࡯ࡰࠬᬅ"),
  bstack1l1_opy_ (u"ࠩࡨࡲࡸࡻࡲࡦ࡙ࡨࡦࡻ࡯ࡥࡸࡵࡋࡥࡻ࡫ࡐࡢࡩࡨࡷࠬᬆ"), bstack1l1_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࡈࡪࡼࡴࡰࡱ࡯ࡷࡕࡵࡲࡵࠩᬇ"), bstack1l1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨ࡛ࡪࡨࡶࡪࡧࡺࡈࡪࡺࡡࡪ࡮ࡶࡇࡴࡲ࡬ࡦࡥࡷ࡭ࡴࡴࠧᬈ"),
  bstack1l1_opy_ (u"ࠬࡸࡥ࡮ࡱࡷࡩࡆࡶࡰࡴࡅࡤࡧ࡭࡫ࡌࡪ࡯࡬ࡸࠬᬉ"),
  bstack1l1_opy_ (u"࠭ࡣࡢ࡮ࡨࡲࡩࡧࡲࡇࡱࡵࡱࡦࡺࠧᬊ"),
  bstack1l1_opy_ (u"ࠧࡣࡷࡱࡨࡱ࡫ࡉࡥࠩᬋ"),
  bstack1l1_opy_ (u"ࠨ࡮ࡤࡹࡳࡩࡨࡕ࡫ࡰࡩࡴࡻࡴࠨᬌ"),
  bstack1l1_opy_ (u"ࠩ࡯ࡳࡨࡧࡴࡪࡱࡱࡗࡪࡸࡶࡪࡥࡨࡷࡊࡴࡡࡣ࡮ࡨࡨࠬᬍ"), bstack1l1_opy_ (u"ࠪࡰࡴࡩࡡࡵ࡫ࡲࡲࡘ࡫ࡲࡷ࡫ࡦࡩࡸࡇࡵࡵࡪࡲࡶ࡮ࢀࡥࡥࠩᬎ"),
  bstack1l1_opy_ (u"ࠫࡦࡻࡴࡰࡃࡦࡧࡪࡶࡴࡂ࡮ࡨࡶࡹࡹࠧᬏ"), bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱࡇ࡭ࡸࡳࡩࡴࡵࡄࡰࡪࡸࡴࡴࠩᬐ"),
  bstack1l1_opy_ (u"࠭࡮ࡢࡶ࡬ࡺࡪࡏ࡮ࡴࡶࡵࡹࡲ࡫࡮ࡵࡵࡏ࡭ࡧ࠭ᬑ"),
  bstack1l1_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡗࡦࡤࡗࡥࡵ࠭ᬒ"),
  bstack1l1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡊࡰ࡬ࡸ࡮ࡧ࡬ࡖࡴ࡯ࠫᬓ"), bstack1l1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡃ࡯ࡰࡴࡽࡐࡰࡲࡸࡴࡸ࠭ᬔ"), bstack1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࡌ࡫ࡳࡵࡲࡦࡈࡵࡥࡺࡪࡗࡢࡴࡱ࡭ࡳ࡭ࠧᬕ"), bstack1l1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬ࡓࡵ࡫࡮ࡍ࡫ࡱ࡯ࡸࡏ࡮ࡃࡣࡦ࡯࡬ࡸ࡯ࡶࡰࡧࠫᬖ"),
  bstack1l1_opy_ (u"ࠬࡱࡥࡦࡲࡎࡩࡾࡉࡨࡢ࡫ࡱࡷࠬᬗ"),
  bstack1l1_opy_ (u"࠭࡬ࡰࡥࡤࡰ࡮ࢀࡡࡣ࡮ࡨࡗࡹࡸࡩ࡯ࡩࡶࡈ࡮ࡸࠧᬘ"),
  bstack1l1_opy_ (u"ࠧࡱࡴࡲࡧࡪࡹࡳࡂࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᬙ"),
  bstack1l1_opy_ (u"ࠨ࡫ࡱࡸࡪࡸࡋࡦࡻࡇࡩࡱࡧࡹࠨᬚ"),
  bstack1l1_opy_ (u"ࠩࡶ࡬ࡴࡽࡉࡐࡕࡏࡳ࡬࠭ᬛ"),
  bstack1l1_opy_ (u"ࠪࡷࡪࡴࡤࡌࡧࡼࡗࡹࡸࡡࡵࡧࡪࡽࠬᬜ"),
  bstack1l1_opy_ (u"ࠫࡼ࡫ࡢ࡬࡫ࡷࡖࡪࡹࡰࡰࡰࡶࡩ࡙࡯࡭ࡦࡱࡸࡸࠬᬝ"), bstack1l1_opy_ (u"ࠬࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵ࡙ࡤ࡭ࡹ࡚ࡩ࡮ࡧࡲࡹࡹ࠭ᬞ"),
  bstack1l1_opy_ (u"࠭ࡲࡦ࡯ࡲࡸࡪࡊࡥࡣࡷࡪࡔࡷࡵࡸࡺࠩᬟ"),
  bstack1l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡴࡻࡱࡧࡊࡾࡥࡤࡷࡷࡩࡋࡸ࡯࡮ࡊࡷࡸࡵࡹࠧᬠ"),
  bstack1l1_opy_ (u"ࠨࡵ࡮࡭ࡵࡒ࡯ࡨࡅࡤࡴࡹࡻࡲࡦࠩᬡ"),
  bstack1l1_opy_ (u"ࠩࡺࡩࡧࡱࡩࡵࡆࡨࡦࡺ࡭ࡐࡳࡱࡻࡽࡕࡵࡲࡵࠩᬢ"),
  bstack1l1_opy_ (u"ࠪࡪࡺࡲ࡬ࡄࡱࡱࡸࡪࡾࡴࡍ࡫ࡶࡸࠬᬣ"),
  bstack1l1_opy_ (u"ࠫࡼࡧࡩࡵࡈࡲࡶࡆࡶࡰࡔࡥࡵ࡭ࡵࡺࠧᬤ"),
  bstack1l1_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼࡉ࡯࡯ࡰࡨࡧࡹࡘࡥࡵࡴ࡬ࡩࡸ࠭ᬥ"),
  bstack1l1_opy_ (u"࠭ࡡࡱࡲࡑࡥࡲ࡫ࠧᬦ"),
  bstack1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡔࡎࡆࡩࡷࡺࠧᬧ"),
  bstack1l1_opy_ (u"ࠨࡶࡤࡴ࡜࡯ࡴࡩࡕ࡫ࡳࡷࡺࡐࡳࡧࡶࡷࡉࡻࡲࡢࡶ࡬ࡳࡳ࠭ᬨ"),
  bstack1l1_opy_ (u"ࠩࡶࡧࡦࡲࡥࡇࡣࡦࡸࡴࡸࠧᬩ"),
  bstack1l1_opy_ (u"ࠪࡻࡩࡧࡌࡰࡥࡤࡰࡕࡵࡲࡵࠩᬪ"),
  bstack1l1_opy_ (u"ࠫࡸ࡮࡯ࡸ࡚ࡦࡳࡩ࡫ࡌࡰࡩࠪᬫ"),
  bstack1l1_opy_ (u"ࠬ࡯࡯ࡴࡋࡱࡷࡹࡧ࡬࡭ࡒࡤࡹࡸ࡫ࠧᬬ"),
  bstack1l1_opy_ (u"࠭ࡸࡤࡱࡧࡩࡈࡵ࡮ࡧ࡫ࡪࡊ࡮ࡲࡥࠨᬭ"),
  bstack1l1_opy_ (u"ࠧ࡬ࡧࡼࡧ࡭ࡧࡩ࡯ࡒࡤࡷࡸࡽ࡯ࡳࡦࠪᬮ"),
  bstack1l1_opy_ (u"ࠨࡷࡶࡩࡕࡸࡥࡣࡷ࡬ࡰࡹ࡝ࡄࡂࠩᬯ"),
  bstack1l1_opy_ (u"ࠩࡳࡶࡪࡼࡥ࡯ࡶ࡚ࡈࡆࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠪᬰ"),
  bstack1l1_opy_ (u"ࠪࡻࡪࡨࡄࡳ࡫ࡹࡩࡷࡇࡧࡦࡰࡷ࡙ࡷࡲࠧᬱ"),
  bstack1l1_opy_ (u"ࠫࡰ࡫ࡹࡤࡪࡤ࡭ࡳࡖࡡࡵࡪࠪᬲ"),
  bstack1l1_opy_ (u"ࠬࡻࡳࡦࡐࡨࡻ࡜ࡊࡁࠨᬳ"),
  bstack1l1_opy_ (u"࠭ࡷࡥࡣࡏࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵ᬴ࠩ"), bstack1l1_opy_ (u"ࠧࡸࡦࡤࡇࡴࡴ࡮ࡦࡥࡷ࡭ࡴࡴࡔࡪ࡯ࡨࡳࡺࡺࠧᬵ"),
  bstack1l1_opy_ (u"ࠨࡺࡦࡳࡩ࡫ࡏࡳࡩࡌࡨࠬᬶ"), bstack1l1_opy_ (u"ࠩࡻࡧࡴࡪࡥࡔ࡫ࡪࡲ࡮ࡴࡧࡊࡦࠪᬷ"),
  bstack1l1_opy_ (u"ࠪࡹࡵࡪࡡࡵࡧࡧ࡛ࡉࡇࡂࡶࡰࡧࡰࡪࡏࡤࠨᬸ"),
  bstack1l1_opy_ (u"ࠫࡷ࡫ࡳࡦࡶࡒࡲࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡳࡶࡒࡲࡱࡿࠧᬹ"),
  bstack1l1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩ࡚ࡩ࡮ࡧࡲࡹࡹࡹࠧᬺ"),
  bstack1l1_opy_ (u"࠭ࡷࡥࡣࡖࡸࡦࡸࡴࡶࡲࡕࡩࡹࡸࡩࡦࡵࠪᬻ"), bstack1l1_opy_ (u"ࠧࡸࡦࡤࡗࡹࡧࡲࡵࡷࡳࡖࡪࡺࡲࡺࡋࡱࡸࡪࡸࡶࡢ࡮ࠪᬼ"),
  bstack1l1_opy_ (u"ࠨࡥࡲࡲࡳ࡫ࡣࡵࡊࡤࡶࡩࡽࡡࡳࡧࡎࡩࡾࡨ࡯ࡢࡴࡧࠫᬽ"),
  bstack1l1_opy_ (u"ࠩࡰࡥࡽ࡚ࡹࡱ࡫ࡱ࡫ࡋࡸࡥࡲࡷࡨࡲࡨࡿࠧᬾ"),
  bstack1l1_opy_ (u"ࠪࡷ࡮ࡳࡰ࡭ࡧࡌࡷ࡛࡯ࡳࡪࡤ࡯ࡩࡈ࡮ࡥࡤ࡭ࠪᬿ"),
  bstack1l1_opy_ (u"ࠫࡺࡹࡥࡄࡣࡵࡸ࡭ࡧࡧࡦࡕࡶࡰࠬᭀ"),
  bstack1l1_opy_ (u"ࠬࡹࡨࡰࡷ࡯ࡨ࡚ࡹࡥࡔ࡫ࡱ࡫ࡱ࡫ࡴࡰࡰࡗࡩࡸࡺࡍࡢࡰࡤ࡫ࡪࡸࠧᭁ"),
  bstack1l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡎ࡝ࡄࡑࠩᭂ"),
  bstack1l1_opy_ (u"ࠧࡢ࡮࡯ࡳࡼ࡚࡯ࡶࡥ࡫ࡍࡩࡋ࡮ࡳࡱ࡯ࡰࠬᭃ"),
  bstack1l1_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࡉ࡫ࡧࡨࡪࡴࡁࡱ࡫ࡓࡳࡱ࡯ࡣࡺࡇࡵࡶࡴࡸ᭄ࠧ"),
  bstack1l1_opy_ (u"ࠩࡰࡳࡨࡱࡌࡰࡥࡤࡸ࡮ࡵ࡮ࡂࡲࡳࠫᭅ"),
  bstack1l1_opy_ (u"ࠪࡰࡴ࡭ࡣࡢࡶࡉࡳࡷࡳࡡࡵࠩᭆ"), bstack1l1_opy_ (u"ࠫࡱࡵࡧࡤࡣࡷࡊ࡮ࡲࡴࡦࡴࡖࡴࡪࡩࡳࠨᭇ"),
  bstack1l1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡈࡪࡲࡡࡺࡃࡧࡦࠬᭈ"),
  bstack1l1_opy_ (u"࠭ࡤࡪࡵࡤࡦࡱ࡫ࡉࡥࡎࡲࡧࡦࡺ࡯ࡳࡃࡸࡸࡴࡩ࡯࡮ࡲ࡯ࡩࡹ࡯࡯࡯ࠩᭉ")
]
bstack1lllll11_opy_ = bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠲ࡩ࡬ࡰࡷࡧ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡵࡱ࡮ࡲࡥࡩ࠭ᭊ")
bstack1l11l1l111_opy_ = [bstack1l1_opy_ (u"ࠨ࠰ࡤࡴࡰ࠭ᭋ"), bstack1l1_opy_ (u"ࠩ࠱ࡥࡦࡨࠧᭌ"), bstack1l1_opy_ (u"ࠪ࠲࡮ࡶࡡࠨ᭍")]
bstack1lllll11l_opy_ = [bstack1l1_opy_ (u"ࠫ࡮ࡪࠧ᭎"), bstack1l1_opy_ (u"ࠬࡶࡡࡵࡪࠪ᭏"), bstack1l1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡥࡩࡥࠩ᭐"), bstack1l1_opy_ (u"ࠧࡴࡪࡤࡶࡪࡧࡢ࡭ࡧࡢ࡭ࡩ࠭᭑")]
bstack1l1111lll1_opy_ = {
  bstack1l1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ᭒"): bstack1l1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᭓"),
  bstack1l1_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࡓࡵࡺࡩࡰࡰࡶࠫ᭔"): bstack1l1_opy_ (u"ࠫࡲࡵࡺ࠻ࡨ࡬ࡶࡪ࡬࡯ࡹࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᭕"),
  bstack1l1_opy_ (u"ࠬ࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᭖"): bstack1l1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᭗"),
  bstack1l1_opy_ (u"ࠧࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᭘"): bstack1l1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᭙"),
  bstack1l1_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᭚"): bstack1l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ᭛")
}
bstack11lll11l1l_opy_ = [
  bstack1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᭜"),
  bstack1l1_opy_ (u"ࠬࡳ࡯ࡻ࠼ࡩ࡭ࡷ࡫ࡦࡰࡺࡒࡴࡹ࡯࡯࡯ࡵࠪ᭝"),
  bstack1l1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ᭞"),
  bstack1l1_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᭟"),
  bstack1l1_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ᭠"),
]
bstack1ll1llllll_opy_ = bstack1l11l1ll_opy_ + bstack11l11l11l1l_opy_ + bstack1ll1lll1l1_opy_
bstack1lllll1l1_opy_ = [
  bstack1l1_opy_ (u"ࠩࡡࡰࡴࡩࡡ࡭ࡪࡲࡷࡹࠪࠧ᭡"),
  bstack1l1_opy_ (u"ࠪࡢࡧࡹ࠭࡭ࡱࡦࡥࡱ࠴ࡣࡰ࡯ࠧࠫ᭢"),
  bstack1l1_opy_ (u"ࠫࡣ࠷࠲࠸࠰ࠪ᭣"),
  bstack1l1_opy_ (u"ࠬࡤ࠱࠱࠰ࠪ᭤"),
  bstack1l1_opy_ (u"࠭࡞࠲࠹࠵࠲࠶ࡡ࠶࠮࠻ࡠ࠲ࠬ᭥"),
  bstack1l1_opy_ (u"ࠧ࡟࠳࠺࠶࠳࠸࡛࠱࠯࠼ࡡ࠳࠭᭦"),
  bstack1l1_opy_ (u"ࠨࡠ࠴࠻࠷࠴࠳࡜࠲࠰࠵ࡢ࠴ࠧ᭧"),
  bstack1l1_opy_ (u"ࠩࡡ࠵࠾࠸࠮࠲࠸࠻࠲ࠬ᭨")
]
bstack11lll111l1l_opy_ = bstack1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡶࡩ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ᭩")
bstack1l1lllll11_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠰ࡸ࠴࠳ࡪࡼࡥ࡯ࡶࠪ᭪")
bstack11ll1l11_opy_ = [ bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ᭫") ]
bstack11ll1llll1_opy_ = [ bstack1l1_opy_ (u"࠭ࡡࡱࡲ࠰ࡥࡺࡺ࡯࡮ࡣࡷࡩ᭬ࠬ") ]
bstack11l111ll_opy_ = [bstack1l1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ᭭")]
bstack111lll111_opy_ = [ bstack1l1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ᭮") ]
bstack1l11l1l1l1_opy_ = bstack1l1_opy_ (u"ࠩࡖࡈࡐ࡙ࡥࡵࡷࡳࠫ᭯")
bstack111l1lll_opy_ = bstack1l1_opy_ (u"ࠪࡗࡉࡑࡔࡦࡵࡷࡅࡹࡺࡥ࡮ࡲࡷࡩࡩ࠭᭰")
bstack1l1l11l1l1_opy_ = bstack1l1_opy_ (u"ࠫࡘࡊࡋࡕࡧࡶࡸࡘࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬ࠨ᭱")
bstack11lll1l11_opy_ = bstack1l1_opy_ (u"ࠬ࠺࠮࠱࠰࠳ࠫ᭲")
bstack11llll11_opy_ = [
  bstack1l1_opy_ (u"࠭ࡅࡓࡔࡢࡊࡆࡏࡌࡆࡆࠪ᭳"),
  bstack1l1_opy_ (u"ࠧࡆࡔࡕࡣ࡙ࡏࡍࡆࡆࡢࡓ࡚࡚ࠧ᭴"),
  bstack1l1_opy_ (u"ࠨࡇࡕࡖࡤࡈࡌࡐࡅࡎࡉࡉࡥࡂ࡚ࡡࡆࡐࡎࡋࡎࡕࠩ᭵"),
  bstack1l1_opy_ (u"ࠩࡈࡖࡗࡥࡎࡆࡖ࡚ࡓࡗࡑ࡟ࡄࡊࡄࡒࡌࡋࡄࠨ᭶"),
  bstack1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡊ࡚࡟ࡏࡑࡗࡣࡈࡕࡎࡏࡇࡆࡘࡊࡊࠧ᭷"),
  bstack1l1_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡉࡌࡐࡕࡈࡈࠬ᭸"),
  bstack1l1_opy_ (u"ࠬࡋࡒࡓࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡒࡆࡕࡈࡘࠬ᭹"),
  bstack1l1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡓࡇࡉ࡙ࡘࡋࡄࠨ᭺"),
  bstack1l1_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡃࡅࡓࡗ࡚ࡅࡅࠩ᭻"),
  bstack1l1_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩ᭼"),
  bstack1l1_opy_ (u"ࠩࡈࡖࡗࡥࡎࡂࡏࡈࡣࡓࡕࡔࡠࡔࡈࡗࡔࡒࡖࡆࡆࠪ᭽"),
  bstack1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡂࡆࡇࡖࡊ࡙ࡓࡠࡋࡑ࡚ࡆࡒࡉࡅࠩ᭾"),
  bstack1l1_opy_ (u"ࠫࡊࡘࡒࡠࡃࡇࡈࡗࡋࡓࡔࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧ᭿"),
  bstack1l1_opy_ (u"ࠬࡋࡒࡓࡡࡗ࡙ࡓࡔࡅࡍࡡࡆࡓࡓࡔࡅࡄࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ᮀ"),
  bstack1l1_opy_ (u"࠭ࡅࡓࡔࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪᮁ"),
  bstack1l1_opy_ (u"ࠧࡆࡔࡕࡣࡘࡕࡃࡌࡕࡢࡇࡔࡔࡎࡆࡅࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧᮂ"),
  bstack1l1_opy_ (u"ࠨࡇࡕࡖࡤ࡙ࡏࡄࡍࡖࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡊࡒࡗ࡙ࡥࡕࡏࡔࡈࡅࡈࡎࡁࡃࡎࡈࠫᮃ"),
  bstack1l1_opy_ (u"ࠩࡈࡖࡗࡥࡐࡓࡑ࡛࡝ࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩᮄ"),
  bstack1l1_opy_ (u"ࠪࡉࡗࡘ࡟ࡏࡃࡐࡉࡤࡔࡏࡕࡡࡕࡉࡘࡕࡌࡗࡇࡇࠫᮅ"),
  bstack1l1_opy_ (u"ࠫࡊࡘࡒࡠࡐࡄࡑࡊࡥࡒࡆࡕࡒࡐ࡚࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪᮆ"),
  bstack1l1_opy_ (u"ࠬࡋࡒࡓࡡࡐࡅࡓࡊࡁࡕࡑࡕ࡝ࡤࡖࡒࡐ࡚࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣࡋࡇࡉࡍࡇࡇࠫᮇ"),
]
bstack111l11ll1_opy_ = bstack1l1_opy_ (u"࠭࠮࠰ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠭ࡢࡴࡷ࡭࡫ࡧࡣࡵࡵ࠲ࠫᮈ")
bstack1lllll1lll_opy_ = os.path.join(os.path.expanduser(bstack1l1_opy_ (u"ࠧࡿࠩᮉ")), bstack1l1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᮊ"), bstack1l1_opy_ (u"ࠩ࠱ࡦࡸࡺࡡࡤ࡭࠰ࡧࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠨᮋ"))
bstack11l1l1ll11l_opy_ = bstack1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡢࡲ࡬ࠫᮌ")
bstack11l11l11l11_opy_ = [ bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᮍ"), bstack1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᮎ"), bstack1l1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬᮏ"), bstack1l1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧᮐ")]
bstack11l11l11_opy_ = [ bstack1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨᮑ"), bstack1l1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨᮒ"), bstack1l1_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩᮓ"), bstack1l1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫᮔ") ]
bstack11ll1l1ll1_opy_ = [ bstack1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᮕ") ]
bstack1lll11l11_opy_ = 360
bstack11l1l11l1l1_opy_ = bstack1l1_opy_ (u"ࠨࡡࡱࡲ࠰ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲࠨᮖ")
bstack11l11lll111_opy_ = bstack1l1_opy_ (u"ࠢࡢࡷࡷࡳࡲࡧࡴࡦ࠱ࡤࡴ࡮࠵ࡶ࠲࠱࡬ࡷࡸࡻࡥࡴࠤᮗ")
bstack11l11l1ll11_opy_ = bstack1l1_opy_ (u"ࠣࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡥࡵ࡯࠯ࡷ࠳࠲࡭ࡸࡹࡵࡦࡵ࠰ࡷࡺࡳ࡭ࡢࡴࡼࠦᮘ")
bstack11l1l1l1l11_opy_ = bstack1l1_opy_ (u"ࠤࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡸࡪࡹࡴࡴࠢࡤࡶࡪࠦࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡲࡲࠥࡕࡓࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࠨࡷࠥࡧ࡮ࡥࠢࡤࡦࡴࡼࡥࠡࡨࡲࡶࠥࡇ࡮ࡥࡴࡲ࡭ࡩࠦࡤࡦࡸ࡬ࡧࡪࡹ࠮ࠣᮙ")
bstack11l1ll111l1_opy_ = bstack1l1_opy_ (u"ࠥ࠵࠶࠴࠰ࠣᮚ")
bstack111l111lll_opy_ = {
  bstack1l1_opy_ (u"ࠫࡕࡇࡓࡔࠩᮛ"): bstack1l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᮜ"),
  bstack1l1_opy_ (u"࠭ࡆࡂࡋࡏࠫᮝ"): bstack1l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᮞ"),
  bstack1l1_opy_ (u"ࠨࡕࡎࡍࡕ࠭ᮟ"): bstack1l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪᮠ")
}
bstack1l1ll1ll11_opy_ = [
  bstack1l1_opy_ (u"ࠥ࡫ࡪࡺࠢᮡ"),
  bstack1l1_opy_ (u"ࠦ࡬ࡵࡂࡢࡥ࡮ࠦᮢ"),
  bstack1l1_opy_ (u"ࠧ࡭࡯ࡇࡱࡵࡻࡦࡸࡤࠣᮣ"),
  bstack1l1_opy_ (u"ࠨࡲࡦࡨࡵࡩࡸ࡮ࠢᮤ"),
  bstack1l1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨᮥ"),
  bstack1l1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᮦ"),
  bstack1l1_opy_ (u"ࠤࡶࡹࡧࡳࡩࡵࡇ࡯ࡩࡲ࡫࡮ࡵࠤᮧ"),
  bstack1l1_opy_ (u"ࠥࡷࡪࡴࡤࡌࡧࡼࡷ࡙ࡵࡅ࡭ࡧࡰࡩࡳࡺࠢᮨ"),
  bstack1l1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡂࡥࡷ࡭ࡻ࡫ࡅ࡭ࡧࡰࡩࡳࡺࠢᮩ"),
  bstack1l1_opy_ (u"ࠧࡩ࡬ࡦࡣࡵࡉࡱ࡫࡭ࡦࡰࡷ᮪ࠦ"),
  bstack1l1_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࡹ᮫ࠢ"),
  bstack1l1_opy_ (u"ࠢࡦࡺࡨࡧࡺࡺࡥࡔࡥࡵ࡭ࡵࡺࠢᮬ"),
  bstack1l1_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࡃࡶࡽࡳࡩࡓࡤࡴ࡬ࡴࡹࠨᮭ"),
  bstack1l1_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣᮮ"),
  bstack1l1_opy_ (u"ࠥࡵࡺ࡯ࡴࠣᮯ"),
  bstack1l1_opy_ (u"ࠦࡵ࡫ࡲࡧࡱࡵࡱ࡙ࡵࡵࡤࡪࡄࡧࡹ࡯࡯࡯ࠤ᮰"),
  bstack1l1_opy_ (u"ࠧࡶࡥࡳࡨࡲࡶࡲࡓࡵ࡭ࡶ࡬ࡘࡴࡻࡣࡩࠤ᮱"),
  bstack1l1_opy_ (u"ࠨࡳࡩࡣ࡮ࡩࠧ᮲"),
  bstack1l1_opy_ (u"ࠢࡤ࡮ࡲࡷࡪࡇࡰࡱࠤ᮳")
]
bstack11l11l1lll1_opy_ = [
  bstack1l1_opy_ (u"ࠣࡥ࡯࡭ࡨࡱࠢ᮴"),
  bstack1l1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨ᮵"),
  bstack1l1_opy_ (u"ࠥࡥࡺࡺ࡯ࠣ᮶"),
  bstack1l1_opy_ (u"ࠦࡲࡧ࡮ࡶࡣ࡯ࠦ᮷"),
  bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢ᮸")
]
bstack1l1111lll_opy_ = {
  bstack1l1_opy_ (u"ࠨࡣ࡭࡫ࡦ࡯ࠧ᮹"): [bstack1l1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨᮺ")],
  bstack1l1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᮻ"): [bstack1l1_opy_ (u"ࠤࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨᮼ")],
  bstack1l1_opy_ (u"ࠥࡥࡺࡺ࡯ࠣᮽ"): [bstack1l1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡆ࡮ࡨࡱࡪࡴࡴࠣᮾ"), bstack1l1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࡔࡰࡃࡦࡸ࡮ࡼࡥࡆ࡮ࡨࡱࡪࡴࡴࠣᮿ"), bstack1l1_opy_ (u"ࠨࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠥᯀ"), bstack1l1_opy_ (u"ࠢࡤ࡮࡬ࡧࡰࡋ࡬ࡦ࡯ࡨࡲࡹࠨᯁ")],
  bstack1l1_opy_ (u"ࠣ࡯ࡤࡲࡺࡧ࡬ࠣᯂ"): [bstack1l1_opy_ (u"ࠤࡰࡥࡳࡻࡡ࡭ࠤᯃ")],
  bstack1l1_opy_ (u"ࠥࡸࡪࡹࡴࡤࡣࡶࡩࠧᯄ"): [bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨᯅ")],
}
bstack11l11l11lll_opy_ = {
  bstack1l1_opy_ (u"ࠧࡩ࡬ࡪࡥ࡮ࡉࡱ࡫࡭ࡦࡰࡷࠦᯆ"): bstack1l1_opy_ (u"ࠨࡣ࡭࡫ࡦ࡯ࠧᯇ"),
  bstack1l1_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦᯈ"): bstack1l1_opy_ (u"ࠣࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧᯉ"),
  bstack1l1_opy_ (u"ࠤࡶࡩࡳࡪࡋࡦࡻࡶࡘࡴࡋ࡬ࡦ࡯ࡨࡲࡹࠨᯊ"): bstack1l1_opy_ (u"ࠥࡷࡪࡴࡤࡌࡧࡼࡷࠧᯋ"),
  bstack1l1_opy_ (u"ࠦࡸ࡫࡮ࡥࡍࡨࡽࡸ࡚࡯ࡂࡥࡷ࡭ࡻ࡫ࡅ࡭ࡧࡰࡩࡳࡺࠢᯌ"): bstack1l1_opy_ (u"ࠧࡹࡥ࡯ࡦࡎࡩࡾࡹࠢᯍ"),
  bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡧࡦࡹࡥࠣᯎ"): bstack1l1_opy_ (u"ࠢࡵࡧࡶࡸࡨࡧࡳࡦࠤᯏ")
}
bstack111l11ll11_opy_ = {
  bstack1l1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡃࡏࡐࠬᯐ"): bstack1l1_opy_ (u"ࠩࡖࡹ࡮ࡺࡥࠡࡕࡨࡸࡺࡶࠧᯑ"),
  bstack1l1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭ᯒ"): bstack1l1_opy_ (u"ࠫࡘࡻࡩࡵࡧࠣࡘࡪࡧࡲࡥࡱࡺࡲࠬᯓ"),
  bstack1l1_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪᯔ"): bstack1l1_opy_ (u"࠭ࡔࡦࡵࡷࠤࡘ࡫ࡴࡶࡲࠪᯕ"),
  bstack1l1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫᯖ"): bstack1l1_opy_ (u"ࠨࡖࡨࡷࡹࠦࡔࡦࡣࡵࡨࡴࡽ࡮ࠨᯗ")
}
bstack11lll11lll1_opy_ = 65536
bstack11l1llllll1_opy_ = bstack1l1_opy_ (u"ࠩ࠱࠲࠳ࡡࡔࡓࡗࡑࡇࡆ࡚ࡅࡅ࡟ࠪᯘ")
bstack11ll11111ll_opy_ = [
      bstack1l1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬᯙ"), bstack1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧᯚ"), bstack1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨᯛ"), bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪᯜ"), bstack1l1_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡖࡢࡴ࡬ࡥࡧࡲࡥࡴࠩᯝ"),
      bstack1l1_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫᯞ"), bstack1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬᯟ"), bstack1l1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡒࡵࡳࡽࡿࡕࡴࡧࡵࠫᯠ"), bstack1l1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡑࡣࡶࡷࠬᯡ"),
      bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᯢ"), bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᯣ"), bstack1l1_opy_ (u"ࠧࡢࡷࡷ࡬࡙ࡵ࡫ࡦࡰࠪᯤ")
    ]
bstack11ll1ll11l1_opy_= {
  bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬᯥ"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ᯦࠭"),
  bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧᯧ"): bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨᯨ"),
  bstack1l1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫᯩ"): bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪᯪ"),
  bstack1l1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧᯫ"): bstack1l1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᯬ"),
  bstack1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᯭ"): bstack1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᯮ"),
  bstack1l1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ᯯ"): bstack1l1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᯰ"),
  bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᯱ"): bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻ᯲ࠪ"),
  bstack1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽ᯳ࠬ"): bstack1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭᯴"),
  bstack1l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭᯵"): bstack1l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ᯶"),
  bstack1l1_opy_ (u"ࠬࡺࡥࡴࡶࡆࡳࡳࡺࡥࡹࡶࡒࡴࡹ࡯࡯࡯ࡵࠪ᯷"): bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠫ᯸"),
  bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ᯹"): bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬ᯺"),
  bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭᯻"): bstack1l1_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᯼"),
  bstack1l1_opy_ (u"ࠫࡨࡻࡳࡵࡱࡰ࡚ࡦࡸࡩࡢࡤ࡯ࡩࡸ࠭᯽"): bstack1l1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱ࡛ࡧࡲࡪࡣࡥࡰࡪࡹࠧ᯾"),
  bstack1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪ᯿"): bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᰀ"),
  bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᰁ"): bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫᰂ"),
  bstack1l1_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡖࡨࡷࡹࡹࠧᰃ"): bstack1l1_opy_ (u"ࠫࡷ࡫ࡲࡶࡰࡗࡩࡸࡺࡳࠨᰄ"),
  bstack1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫᰅ"): bstack1l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬᰆ"),
  bstack1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᰇ"): bstack1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᰈ"),
  bstack1l1_opy_ (u"ࠩࡳࡩࡷࡩࡹࡄࡣࡳࡸࡺࡸࡥࡎࡱࡧࡩࠬᰉ"): bstack1l1_opy_ (u"ࠪࡴࡪࡸࡣࡺࡅࡤࡴࡹࡻࡲࡦࡏࡲࡨࡪ࠭ᰊ"),
  bstack1l1_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡻࡴࡰࡅࡤࡴࡹࡻࡲࡦࡎࡲ࡫ࡸ࠭ᰋ"): bstack1l1_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡇࡵࡵࡱࡆࡥࡵࡺࡵࡳࡧࡏࡳ࡬ࡹࠧᰌ"),
  bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᰍ"): bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᰎ"),
  bstack1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᰏ"): bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᰐ"),
  bstack1l1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᰑ"): bstack1l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᰒ"),
  bstack1l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᰓ"): bstack1l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᰔ"),
  bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡓࡵࡺࡩࡰࡰࡶࠫᰕ"): bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬᰖ"),
  bstack1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡔࡧࡷࡸ࡮ࡴࡧࡴࠩᰗ"): bstack1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡕࡨࡸࡹ࡯࡮ࡨࡵࠪᰘ")
}
bstack11l11l111ll_opy_ = [bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᰙ"), bstack1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᰚ")]
bstack11ll11ll11_opy_ = (bstack1l1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᰛ"),)
bstack11ll11l1l1l_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠳ࡻ࠷࠯ࡶࡲࡧࡥࡹ࡫࡟ࡤ࡮࡬ࠫᰜ")
bstack11llll1lll_opy_ = bstack1l1_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࡤࡴ࡮࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠱ࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥ࠰ࡸ࠴࠳࡬ࡸࡩࡥࡵ࠲ࠦᰝ")
bstack1l11l11lll_opy_ = bstack1l1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲࡫ࡷ࡯ࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡩࡧࡳࡩࡤࡲࡥࡷࡪ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࠣᰞ")
bstack1ll111ll1l_opy_ = bstack1l1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡶࡩ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠳ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧ࠲ࡺ࠶࠵ࡢࡶ࡫࡯ࡨࡸ࠴ࡪࡴࡱࡱࠦᰟ")
class EVENTS(Enum):
  bstack11l11ll1111_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡱ࠴࠵ࡾࡀࡰࡳ࡫ࡱࡸ࠲ࡨࡵࡪ࡮ࡧࡰ࡮ࡴ࡫ࠨᰠ")
  bstack1l1l1l1l11_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰࡪࡧ࡮ࡶࡲࠪᰡ") # final bstack11l11l1l1l1_opy_
  bstack11l11l1l11l_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡷࡪࡴࡤ࡭ࡱࡪࡷࠬᰢ")
  bstack1llllllll_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥ࠻ࡲࡵ࡭ࡳࡺ࠭ࡣࡷ࡬ࡰࡩࡲࡩ࡯࡭ࠪᰣ") #shift post bstack11l11l11ll1_opy_
  bstack1lll111111_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡱࡴ࡬ࡲࡹ࠳ࡢࡶ࡫࡯ࡨࡱ࡯࡮࡬ࠩᰤ") #shift post bstack11l11l11ll1_opy_
  bstack11l11ll1l11_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡴࡦࡵࡷ࡬ࡺࡨࠧᰥ") #shift
  bstack11l11l1ll1l_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡱࡧࡵࡧࡾࡀࡤࡰࡹࡱࡰࡴࡧࡤࠨᰦ") #shift
  bstack1lll11l111_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩ࠿࡮ࡵࡣ࠯ࡰࡥࡳࡧࡧࡦ࡯ࡨࡲࡹ࠭ᰧ")
  bstack1ll1l1llll1_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤ࠵࠶ࡿ࠺ࡴࡣࡹࡩ࠲ࡸࡥࡴࡷ࡯ࡸࡸ࠭ᰨ")
  bstack1l11111l11_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡥ࠶࠷ࡹ࠻ࡦࡵ࡭ࡻ࡫ࡲ࠮ࡲࡨࡶ࡫ࡵࡲ࡮ࡵࡦࡥࡳ࠭ᰩ")
  bstack1l1111111l_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀ࡬ࡰࡥࡤࡰࠬᰪ") #shift
  bstack11l1l1l1ll_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨ࠾ࡦࡶࡰ࠮ࡷࡳࡰࡴࡧࡤࠨᰫ") #shift
  bstack11ll1l11l1_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡶࡶࡲࡱࡦࡺࡥ࠻ࡥ࡬࠱ࡦࡸࡴࡪࡨࡤࡧࡹࡹࠧᰬ")
  bstack1lll1lll11_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢ࠳࠴ࡽ࠿࡭ࡥࡵ࠯ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺ࠯ࡵࡩࡸࡻ࡬ࡵࡵ࠰ࡷࡺࡳ࡭ࡢࡴࡼࠫᰭ") #shift
  bstack1ll11l1l_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡣ࠴࠵ࡾࡀࡧࡦࡶ࠰ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻ࠰ࡶࡪࡹࡵ࡭ࡶࡶࠫᰮ") #shift
  bstack11l111llll1_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡳࡩࡷࡩࡹࠨᰯ") #shift
  bstack1l1ll111l11_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡴࡪࡸࡣࡺ࠼ࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭ᰰ")
  bstack1ll1l11l1_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸࡪࡀࡳࡦࡵࡶ࡭ࡴࡴ࠭ࡴࡶࡤࡸࡺࡹࠧᰱ") #shift
  bstack111l11l11_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡩࡷࡥ࠱ࡲࡧ࡮ࡢࡩࡨࡱࡪࡴࡴࠨᰲ")
  bstack11l11l1llll_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡰࡳࡱࡻࡽ࠲ࡹࡥࡵࡷࡳࠫᰳ") #shift
  bstack11ll1lll_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡴࡧࡷࡹࡵ࠭ᰴ")
  bstack11l11ll11l1_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡨࡶࡨࡿ࠺ࡴࡰࡤࡴࡸ࡮࡯ࡵࠩᰵ") # not bstack11lll11ll11_opy_ in python
  bstack11l11l11l_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳ࠼ࡴࡹ࡮ࡺࠧᰶ") # used in bstack11l11l1l111_opy_
  bstack1l11ll1ll1_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽࡫ࡪࡺ᰷ࠧ") # used in bstack11l11l1l111_opy_
  bstack1lll1111l1_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾࡭ࡵ࡯࡬ࠩ᰸")
  bstack1l111111l1_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡫࠺ࡴࡧࡶࡷ࡮ࡵ࡮࠮ࡰࡤࡱࡪ࠭᰹")
  bstack1llll11l_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡶࡶࡲࡱࡦࡺࡥ࠻ࡵࡨࡷࡸ࡯࡯࡯࠯ࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳ࠭᰺") #
  bstack1l11l1l11_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡰ࠳࠴ࡽ࠿ࡪࡲࡪࡸࡨࡶ࠲ࡺࡡ࡬ࡧࡖࡧࡷ࡫ࡥ࡯ࡕ࡫ࡳࡹ࠭᰻")
  bstack1lll1ll1ll_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡲࡨࡶࡨࡿ࠺ࡢࡷࡷࡳ࠲ࡩࡡࡱࡶࡸࡶࡪ࠭᰼")
  bstack111111l1_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡳࡶࡪ࠳ࡴࡦࡵࡷࠫ᰽")
  bstack1ll111111l_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡴࡴࡹࡴ࠮ࡶࡨࡷࡹ࠭᰾")
  bstack1l1l11l11l_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡩࡸࡩࡷࡧࡵ࠾ࡵࡸࡥ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠩ᰿") #shift
  bstack1l11111ll_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡪࡲࡪࡸࡨࡶ࠿ࡶ࡯ࡴࡶ࠰࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠫ᱀") #shift
  bstack11l11l1l1ll_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡶࡶࡲ࠱ࡨࡧࡰࡵࡷࡵࡩࠬ᱁")
  bstack11l11l1111l_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢࡷࡷࡳࡲࡧࡴࡦ࠼࡬ࡨࡱ࡫࠭ࡵ࡫ࡰࡩࡴࡻࡴࠨ᱂")
  bstack1lll1111l11_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡥ࡯࡭࠿ࡹࡴࡢࡴࡷࠫ᱃")
  bstack11ll1lll1l1_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡦࡰ࡮ࡀࡤࡰࡹࡱࡰࡴࡧࡤࠨ᱄")
  bstack11ll1l111l1_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡧࡱ࡯࠺ࡤࡪࡨࡧࡰ࠳ࡵࡱࡦࡤࡸࡪ࠭᱅")
  bstack1lll111l1l1_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡨࡲࡩ࠻ࡱࡱ࠱ࡧࡵ࡯ࡵࡵࡷࡶࡦࡶࠧ᱆")
  bstack1lllll1l1ll_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡬ࡪ࠼ࡲࡲ࠲ࡩ࡯࡯ࡰࡨࡧࡹ࠭᱇")
  bstack1lll1111ll1_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡣ࡭࡫࠽ࡳࡳ࠳ࡳࡵࡱࡳࠫ᱈")
  bstack1ll1lll1ll1_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡴࡶࡤࡶࡹࡈࡩ࡯ࡕࡨࡷࡸ࡯࡯࡯ࠩ᱉")
  bstack1lll1l1l11l_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡥࡲࡲࡳ࡫ࡣࡵࡄ࡬ࡲࡘ࡫ࡳࡴ࡫ࡲࡲࠬ᱊")
  bstack11l11l11111_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡧࡶ࡮ࡼࡥࡳࡋࡱ࡭ࡹ࠭᱋")
  bstack11l111lllll_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡪ࡮ࡴࡤࡏࡧࡤࡶࡪࡹࡴࡉࡷࡥࠫ᱌")
  bstack1l1l111ll11_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡌࡲ࡮ࡺࠧᱍ")
  bstack1l1l11ll11l_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡗࡹࡧࡲࡵࠩᱎ")
  bstack1ll11lllll1_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡉ࡯࡯ࡨ࡬࡫ࠬᱏ")
  bstack11l11ll11ll_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࡃࡰࡰࡩ࡭࡬࠭᱐")
  bstack1ll11l11l1l_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡣ࡬ࡗࡪࡲࡦࡉࡧࡤࡰࡘࡺࡥࡱࠩ᱑")
  bstack1ll11l11lll_opy_ = bstack1l1_opy_ (u"ࠬࡹࡤ࡬࠼ࡤ࡭ࡘ࡫࡬ࡧࡊࡨࡥࡱࡍࡥࡵࡔࡨࡷࡺࡲࡴࠨ᱒")
  bstack1l1lllll11l_opy_ = bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠽ࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡈࡺࡪࡴࡴࠨ᱓")
  bstack1l1lll111l1_opy_ = bstack1l1_opy_ (u"ࠧࡴࡦ࡮࠾ࡹ࡫ࡳࡵࡕࡨࡷࡸ࡯࡯࡯ࡇࡹࡩࡳࡺࠧ᱔")
  bstack1l1lll1l111_opy_ = bstack1l1_opy_ (u"ࠨࡵࡧ࡯࠿ࡩ࡬ࡪ࠼࡯ࡳ࡬ࡉࡲࡦࡣࡷࡩࡩࡋࡶࡦࡰࡷࠫ᱕")
  bstack11l111lll1l_opy_ = bstack1l1_opy_ (u"ࠩࡶࡨࡰࡀࡣ࡭࡫࠽ࡩࡳࡷࡵࡦࡷࡨࡘࡪࡹࡴࡆࡸࡨࡲࡹ࠭᱖")
  bstack1l1l11l11ll_opy_ = bstack1l1_opy_ (u"ࠪࡷࡩࡱ࠺ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡰࡲࠪ᱗")
  bstack1llll11l11l_opy_ = bstack1l1_opy_ (u"ࠫࡸࡪ࡫࠻ࡱࡱࡗࡹࡵࡰࠨ᱘")
class STAGE(Enum):
  bstack11llll1l_opy_ = bstack1l1_opy_ (u"ࠬࡹࡴࡢࡴࡷࠫ᱙")
  END = bstack1l1_opy_ (u"࠭ࡥ࡯ࡦࠪᱚ")
  bstack1111lll11_opy_ = bstack1l1_opy_ (u"ࠧࡴ࡫ࡱ࡫ࡱ࡫ࠧᱛ")
bstack1l1ll1l1l_opy_ = {
  bstack1l1_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࠨᱜ"): bstack1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩᱝ"),
  bstack1l1_opy_ (u"ࠪࡔ࡞࡚ࡅࡔࡖ࠰ࡆࡉࡊࠧᱞ"): bstack1l1_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷ࠱ࡨࡻࡣࡶ࡯ࡥࡩࡷ࠭ᱟ")
}
PLAYWRIGHT_HUB_URL = bstack1l1_opy_ (u"ࠧࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠢᱠ")
bstack1ll1l1l111l_opy_ = 98
bstack1ll1l1l11l1_opy_ = 100
bstack1111lll11l_opy_ = {
  bstack1l1_opy_ (u"࠭ࡲࡦࡴࡸࡲࠬᱡ"): bstack1l1_opy_ (u"ࠧ࠮࠯ࡵࡩࡷࡻ࡮ࡴࠩᱢ"),
  bstack1l1_opy_ (u"ࠨࡦࡨࡰࡦࡿࠧᱣ"): bstack1l1_opy_ (u"ࠩ࠰࠱ࡷ࡫ࡲࡶࡰࡶ࠱ࡩ࡫࡬ࡢࡻࠪᱤ"),
  bstack1l1_opy_ (u"ࠪࡶࡪࡸࡵ࡯࠯ࡧࡩࡱࡧࡹࠨᱥ"): 0
}