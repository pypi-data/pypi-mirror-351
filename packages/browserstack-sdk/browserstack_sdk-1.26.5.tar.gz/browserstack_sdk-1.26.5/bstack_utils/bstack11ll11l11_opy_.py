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
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack11ll11l1lll_opy_, bstack1lll1lll1l_opy_, get_host_info, bstack11lll11l1ll_opy_, \
 bstack11l1l1ll1l_opy_, bstack1l11l1l1_opy_, bstack111l11l111_opy_, bstack11ll11lllll_opy_, bstack11111l1l1_opy_
import bstack_utils.accessibility as bstack1111111l1_opy_
from bstack_utils.bstack111lll1111_opy_ import bstack1l1111l1l1_opy_
from bstack_utils.percy import bstack11lll1l1_opy_
from bstack_utils.config import Config
bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
logger = logging.getLogger(__name__)
percy = bstack11lll1l1_opy_()
@bstack111l11l111_opy_(class_method=False)
def bstack1111l11l1ll_opy_(bs_config, bstack111lllll_opy_):
  try:
    data = {
        bstack1l1_opy_ (u"࠭ࡦࡰࡴࡰࡥࡹ࠭ᾰ"): bstack1l1_opy_ (u"ࠧ࡫ࡵࡲࡲࠬᾱ"),
        bstack1l1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡡࡱࡥࡲ࡫ࠧᾲ"): bs_config.get(bstack1l1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᾳ"), bstack1l1_opy_ (u"ࠪࠫᾴ")),
        bstack1l1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ᾵"): bs_config.get(bstack1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᾶ"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᾷ"): bs_config.get(bstack1l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩᾸ")),
        bstack1l1_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭Ᾱ"): bs_config.get(bstack1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬᾺ"), bstack1l1_opy_ (u"ࠪࠫΆ")),
        bstack1l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨᾼ"): bstack11111l1l1_opy_(),
        bstack1l1_opy_ (u"ࠬࡺࡡࡨࡵࠪ᾽"): bstack11lll11l1ll_opy_(bs_config),
        bstack1l1_opy_ (u"࠭ࡨࡰࡵࡷࡣ࡮ࡴࡦࡰࠩι"): get_host_info(),
        bstack1l1_opy_ (u"ࠧࡤ࡫ࡢ࡭ࡳ࡬࡯ࠨ᾿"): bstack1lll1lll1l_opy_(),
        bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡳࡷࡱࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ῀"): os.environ.get(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨ῁")),
        bstack1l1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࡢࡸࡪࡹࡴࡴࡡࡵࡩࡷࡻ࡮ࠨῂ"): os.environ.get(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࠩῃ"), False),
        bstack1l1_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳࡥࡣࡰࡰࡷࡶࡴࡲࠧῄ"): bstack11ll11l1lll_opy_(),
        bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭῅"): bstack11111ll111l_opy_(bs_config),
        bstack1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡨࡪࡺࡡࡪ࡮ࡶࠫῆ"): bstack11111ll1lll_opy_(bstack111lllll_opy_),
        bstack1l1_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭ῇ"): bstack11111ll1111_opy_(bs_config, bstack111lllll_opy_.get(bstack1l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡻࡳࡦࡦࠪῈ"), bstack1l1_opy_ (u"ࠪࠫΈ"))),
        bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭Ὴ"): bstack11l1l1ll1l_opy_(bs_config),
    }
    return data
  except Exception as error:
    logger.error(bstack1l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡥࡾࡲ࡯ࡢࡦࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨΉ").format(str(error)))
    return None
def bstack11111ll1lll_opy_(framework):
  return {
    bstack1l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡐࡤࡱࡪ࠭ῌ"): framework.get(bstack1l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࠨ῍"), bstack1l1_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨ῎")),
    bstack1l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ῏"): framework.get(bstack1l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧῐ")),
    bstack1l1_opy_ (u"ࠫࡸࡪ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨῑ"): framework.get(bstack1l1_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪῒ")),
    bstack1l1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨΐ"): bstack1l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ῔"),
    bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ῕"): framework.get(bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩῖ"))
  }
def bstack1l11l11111_opy_(bs_config, framework):
  bstack1l11l1lll1_opy_ = False
  bstack1ll1l1l1l1_opy_ = False
  bstack11111ll1l1l_opy_ = False
  if bstack1l1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧῗ") in bs_config:
    bstack11111ll1l1l_opy_ = True
  elif bstack1l1_opy_ (u"ࠫࡦࡶࡰࠨῘ") in bs_config:
    bstack1l11l1lll1_opy_ = True
  else:
    bstack1ll1l1l1l1_opy_ = True
  bstack1l11l1111_opy_ = {
    bstack1l1_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬῙ"): bstack1l1111l1l1_opy_.bstack11111ll1l11_opy_(bs_config, framework),
    bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭Ὶ"): bstack1111111l1_opy_.bstack1l1l111l11_opy_(bs_config),
    bstack1l1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭Ί"): bs_config.get(bstack1l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧ῜"), False),
    bstack1l1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ῝"): bstack1ll1l1l1l1_opy_,
    bstack1l1_opy_ (u"ࠪࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠩ῞"): bstack1l11l1lll1_opy_,
    bstack1l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡶࡧࡦࡲࡥࠨ῟"): bstack11111ll1l1l_opy_
  }
  return bstack1l11l1111_opy_
@bstack111l11l111_opy_(class_method=False)
def bstack11111ll111l_opy_(bs_config):
  try:
    bstack11111ll11l1_opy_ = json.loads(os.getenv(bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ῠ"), bstack1l1_opy_ (u"࠭ࡻࡾࠩῡ")))
    bstack11111ll11l1_opy_ = bstack11111ll11ll_opy_(bs_config, bstack11111ll11l1_opy_)
    return {
        bstack1l1_opy_ (u"ࠧࡴࡧࡷࡸ࡮ࡴࡧࡴࠩῢ"): bstack11111ll11l1_opy_
    }
  except Exception as error:
    logger.error(bstack1l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥ࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡶࡩࡹࡺࡩ࡯ࡩࡶࠤ࡫ࡵࡲࠡࡖࡨࡷࡹࡎࡵࡣ࠼ࠣࠤࢀࢃࠢΰ").format(str(error)))
    return {}
def bstack11111ll11ll_opy_(bs_config, bstack11111ll11l1_opy_):
  if ((bstack1l1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ῤ") in bs_config or not bstack11l1l1ll1l_opy_(bs_config)) and bstack1111111l1_opy_.bstack1l1l111l11_opy_(bs_config)):
    bstack11111ll11l1_opy_[bstack1l1_opy_ (u"ࠥ࡭ࡳࡩ࡬ࡶࡦࡨࡉࡳࡩ࡯ࡥࡧࡧࡉࡽࡺࡥ࡯ࡵ࡬ࡳࡳࠨῥ")] = True
  return bstack11111ll11l1_opy_
def bstack1111l1l11l1_opy_(array, bstack11111ll1ll1_opy_, bstack11111lll111_opy_):
  result = {}
  for o in array:
    key = o[bstack11111ll1ll1_opy_]
    result[key] = o[bstack11111lll111_opy_]
  return result
def bstack1111l1l1111_opy_(bstack11lllllll1_opy_=bstack1l1_opy_ (u"ࠫࠬῦ")):
  bstack11111lll11l_opy_ = bstack1111111l1_opy_.on()
  bstack11111l1llll_opy_ = bstack1l1111l1l1_opy_.on()
  bstack11111l1lll1_opy_ = percy.bstack1111lllll_opy_()
  if bstack11111l1lll1_opy_ and not bstack11111l1llll_opy_ and not bstack11111lll11l_opy_:
    return bstack11lllllll1_opy_ not in [bstack1l1_opy_ (u"ࠬࡉࡂࡕࡕࡨࡷࡸ࡯࡯࡯ࡅࡵࡩࡦࡺࡥࡥࠩῧ"), bstack1l1_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪῨ")]
  elif bstack11111lll11l_opy_ and not bstack11111l1llll_opy_:
    return bstack11lllllll1_opy_ not in [bstack1l1_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨῩ"), bstack1l1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪῪ"), bstack1l1_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭Ύ")]
  return bstack11111lll11l_opy_ or bstack11111l1llll_opy_ or bstack11111l1lll1_opy_
@bstack111l11l111_opy_(class_method=False)
def bstack1111l1l111l_opy_(bstack11lllllll1_opy_, test=None):
  bstack11111l1ll1l_opy_ = bstack1111111l1_opy_.on()
  if not bstack11111l1ll1l_opy_ or bstack11lllllll1_opy_ not in [bstack1l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬῬ")] or test == None:
    return None
  return {
    bstack1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ῭"): bstack11111l1ll1l_opy_ and bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫ΅"), None) == True and bstack1111111l1_opy_.bstack11l1l1111l_opy_(test[bstack1l1_opy_ (u"࠭ࡴࡢࡩࡶࠫ`")])
  }
def bstack11111ll1111_opy_(bs_config, framework):
  bstack1l11l1lll1_opy_ = False
  bstack1ll1l1l1l1_opy_ = False
  bstack11111ll1l1l_opy_ = False
  if bstack1l1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ῰") in bs_config:
    bstack11111ll1l1l_opy_ = True
  elif bstack1l1_opy_ (u"ࠨࡣࡳࡴࠬ῱") in bs_config:
    bstack1l11l1lll1_opy_ = True
  else:
    bstack1ll1l1l1l1_opy_ = True
  bstack1l11l1111_opy_ = {
    bstack1l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩῲ"): bstack1l1111l1l1_opy_.bstack11111ll1l11_opy_(bs_config, framework),
    bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪῳ"): bstack1111111l1_opy_.bstack11l1l1111_opy_(bs_config),
    bstack1l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪῴ"): bs_config.get(bstack1l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ῵"), False),
    bstack1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡥࠨῶ"): bstack1ll1l1l1l1_opy_,
    bstack1l1_opy_ (u"ࠧࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ῷ"): bstack1l11l1lll1_opy_,
    bstack1l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬῸ"): bstack11111ll1l1l_opy_
  }
  return bstack1l11l1111_opy_