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
import re
from bstack_utils.bstack1ll11l111_opy_ import bstack111l1111lll_opy_
def bstack111l1111l11_opy_(fixture_name):
    if fixture_name.startswith(bstack1ll_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭᷵")):
        return bstack1ll_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭᷶")
    elif fixture_name.startswith(bstack1ll_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ᷷࠭")):
        return bstack1ll_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳࡭ࡰࡦࡸࡰࡪ᷸࠭")
    elif fixture_name.startswith(bstack1ll_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ᷹࠭")):
        return bstack1ll_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ᷺࠭")
    elif fixture_name.startswith(bstack1ll_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᷻")):
        return bstack1ll_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭᷼")
def bstack111l111ll11_opy_(fixture_name):
    return bool(re.match(bstack1ll_opy_ (u"ࠬࡤ࡟ࡹࡷࡱ࡭ࡹࡥࠨࡴࡧࡷࡹࡵࢂࡴࡦࡣࡵࡨࡴࡽ࡮ࠪࡡࠫࡪࡺࡴࡣࡵ࡫ࡲࡲࢁࡳ࡯ࡥࡷ࡯ࡩ࠮ࡥࡦࡪࡺࡷࡹࡷ࡫࡟࠯᷽ࠬࠪ"), fixture_name))
def bstack111l1111ll1_opy_(fixture_name):
    return bool(re.match(bstack1ll_opy_ (u"࠭࡞ࡠࡺࡸࡲ࡮ࡺ࡟ࠩࡵࡨࡸࡺࡶࡼࡵࡧࡤࡶࡩࡵࡷ࡯ࠫࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰ࠧ᷾"), fixture_name))
def bstack111l1111111_opy_(fixture_name):
    return bool(re.match(bstack1ll_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࡣ࠳࠰᷿ࠧ"), fixture_name))
def bstack1111lllllll_opy_(fixture_name):
    if fixture_name.startswith(bstack1ll_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪḀ")):
        return bstack1ll_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪḁ"), bstack1ll_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨḂ")
    elif fixture_name.startswith(bstack1ll_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫḃ")):
        return bstack1ll_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱ࡲࡵࡤࡶ࡮ࡨࠫḄ"), bstack1ll_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪḅ")
    elif fixture_name.startswith(bstack1ll_opy_ (u"ࠧࡠࡺࡸࡲ࡮ࡺ࡟ࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬḆ")):
        return bstack1ll_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰ࠰ࡪࡺࡴࡣࡵ࡫ࡲࡲࠬḇ"), bstack1ll_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭Ḉ")
    elif fixture_name.startswith(bstack1ll_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ḉ")):
        return bstack1ll_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳࡭ࡰࡦࡸࡰࡪ࠭Ḋ"), bstack1ll_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨḋ")
    return None, None
def bstack111l111111l_opy_(hook_name):
    if hook_name in [bstack1ll_opy_ (u"࠭ࡳࡦࡶࡸࡴࠬḌ"), bstack1ll_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࠩḍ")]:
        return hook_name.capitalize()
    return hook_name
def bstack111l11111l1_opy_(hook_name):
    if hook_name in [bstack1ll_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩḎ"), bstack1ll_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨḏ")]:
        return bstack1ll_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨḐ")
    elif hook_name in [bstack1ll_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࠪḑ"), bstack1ll_opy_ (u"ࠬࡹࡥࡵࡷࡳࡣࡨࡲࡡࡴࡵࠪḒ")]:
        return bstack1ll_opy_ (u"࠭ࡂࡆࡈࡒࡖࡊࡥࡁࡍࡎࠪḓ")
    elif hook_name in [bstack1ll_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯ࡡࡩࡹࡳࡩࡴࡪࡱࡱࠫḔ"), bstack1ll_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪḕ")]:
        return bstack1ll_opy_ (u"ࠩࡄࡊ࡙ࡋࡒࡠࡇࡄࡇࡍ࠭Ḗ")
    elif hook_name in [bstack1ll_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬḗ"), bstack1ll_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥࡣ࡭ࡣࡶࡷࠬḘ")]:
        return bstack1ll_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡆࡒࡌࠨḙ")
    return hook_name
def bstack111l111l11l_opy_(node, scenario):
    if hasattr(node, bstack1ll_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨḚ")):
        parts = node.nodeid.rsplit(bstack1ll_opy_ (u"ࠢ࡜ࠤḛ"))
        params = parts[-1]
        return bstack1ll_opy_ (u"ࠣࡽࢀࠤࡠࢁࡽࠣḜ").format(scenario.name, params)
    return scenario.name
def bstack111l1111l1l_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack1ll_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫḝ")):
            examples = list(node.callspec.params[bstack1ll_opy_ (u"ࠪࡣࡵࡿࡴࡦࡵࡷࡣࡧࡪࡤࡠࡧࡻࡥࡲࡶ࡬ࡦࠩḞ")].values())
        return examples
    except:
        return []
def bstack111l111l111_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack111l111l1ll_opy_(report):
    try:
        status = bstack1ll_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫḟ")
        if report.passed or (report.failed and hasattr(report, bstack1ll_opy_ (u"ࠧࡽࡡࡴࡺࡩࡥ࡮ࡲࠢḠ"))):
            status = bstack1ll_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ḡ")
        elif report.skipped:
            status = bstack1ll_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨḢ")
        bstack111l1111lll_opy_(status)
    except:
        pass
def bstack1111ll111_opy_(status):
    try:
        bstack111l111l1l1_opy_ = bstack1ll_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨḣ")
        if status == bstack1ll_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩḤ"):
            bstack111l111l1l1_opy_ = bstack1ll_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪḥ")
        elif status == bstack1ll_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬḦ"):
            bstack111l111l1l1_opy_ = bstack1ll_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭ḧ")
        bstack111l1111lll_opy_(bstack111l111l1l1_opy_)
    except:
        pass
def bstack111l11111ll_opy_(item=None, report=None, summary=None, extra=None):
    return