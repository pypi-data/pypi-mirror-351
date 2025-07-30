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
import requests
import logging
import threading
import bstack_utils.constants as bstack11l1lll1111_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11l1l1ll11l_opy_ as bstack11l1ll11ll1_opy_, EVENTS
from bstack_utils.bstack11l11l1lll_opy_ import bstack11l11l1lll_opy_
from bstack_utils.helper import bstack11111l1l1_opy_, bstack111l1111l1_opy_, bstack11l1l1ll1l_opy_, bstack11ll1111l1l_opy_, \
  bstack11lll11ll1l_opy_, bstack1lll1lll1l_opy_, get_host_info, bstack11ll11l1lll_opy_, bstack11lll11ll_opy_, bstack111l11l111_opy_, bstack11llll111ll_opy_, bstack11ll11l1111_opy_, bstack1l11l1l1_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1l11lllll_opy_ import get_logger
from bstack_utils.bstack11l11l111l_opy_ import bstack1ll1llll111_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack11l11l111l_opy_ = bstack1ll1llll111_opy_()
@bstack111l11l111_opy_(class_method=False)
def _11l1l1ll111_opy_(driver, bstack1111l1ll11_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack1l1_opy_ (u"ࠫࡴࡹ࡟࡯ࡣࡰࡩࠬៀ"): caps.get(bstack1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠫេ"), None),
        bstack1l1_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪែ"): bstack1111l1ll11_opy_.get(bstack1l1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪៃ"), None),
        bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡱࡥࡲ࡫ࠧោ"): caps.get(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧៅ"), None),
        bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬំ"): caps.get(bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬះ"), None)
    }
  except Exception as error:
    logger.debug(bstack1l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫࡫ࡴࡤࡪ࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࠦ࠺ࠡࠩៈ") + str(error))
  return response
def on():
    if os.environ.get(bstack1l1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫ៉"), None) is None or os.environ[bstack1l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ៊")] == bstack1l1_opy_ (u"ࠣࡰࡸࡰࡱࠨ់"):
        return False
    return True
def bstack1l1l111l11_opy_(config):
  return config.get(bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ៌"), False) or any([p.get(bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ៍"), False) == True for p in config.get(bstack1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ៎"), [])])
def bstack1lllllll1l_opy_(config, bstack11l111l1l1_opy_):
  try:
    bstack11l1l1l1111_opy_ = config.get(bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ៏"), False)
    if int(bstack11l111l1l1_opy_) < len(config.get(bstack1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ័"), [])) and config[bstack1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ៑")][bstack11l111l1l1_opy_]:
      bstack11l1lll1ll1_opy_ = config[bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶ្ࠫ")][bstack11l111l1l1_opy_].get(bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ៓"), None)
    else:
      bstack11l1lll1ll1_opy_ = config.get(bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ។"), None)
    if bstack11l1lll1ll1_opy_ != None:
      bstack11l1l1l1111_opy_ = bstack11l1lll1ll1_opy_
    bstack11l1l1l11l1_opy_ = os.getenv(bstack1l1_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩ៕")) is not None and len(os.getenv(bstack1l1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ៖"))) > 0 and os.getenv(bstack1l1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫៗ")) != bstack1l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ៘")
    return bstack11l1l1l1111_opy_ and bstack11l1l1l11l1_opy_
  except Exception as error:
    logger.debug(bstack1l1_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡷࡧࡵ࡭࡫ࡿࡩ࡯ࡩࠣࡸ࡭࡫ࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡹ࡬ࡸ࡭ࠦࡥࡳࡴࡲࡶࠥࡀࠠࠨ៙") + str(error))
  return False
def bstack11l1l1111l_opy_(test_tags):
  bstack1ll1l1111ll_opy_ = os.getenv(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪ៚"))
  if bstack1ll1l1111ll_opy_ is None:
    return True
  bstack1ll1l1111ll_opy_ = json.loads(bstack1ll1l1111ll_opy_)
  try:
    include_tags = bstack1ll1l1111ll_opy_[bstack1l1_opy_ (u"ࠪ࡭ࡳࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨ៛")] if bstack1l1_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩៜ") in bstack1ll1l1111ll_opy_ and isinstance(bstack1ll1l1111ll_opy_[bstack1l1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪ៝")], list) else []
    exclude_tags = bstack1ll1l1111ll_opy_[bstack1l1_opy_ (u"࠭ࡥࡹࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ៞")] if bstack1l1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ៟") in bstack1ll1l1111ll_opy_ and isinstance(bstack1ll1l1111ll_opy_[bstack1l1_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭០")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack1l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡷࡣ࡯࡭ࡩࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡧࡱࡵࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡧ࡫ࡦࡰࡴࡨࠤࡸࡩࡡ࡯ࡰ࡬ࡲ࡬࠴ࠠࡆࡴࡵࡳࡷࠦ࠺ࠡࠤ១") + str(error))
  return False
def bstack11l1ll1l1l1_opy_(config, bstack11l1l1ll1l1_opy_, bstack11l1ll11l11_opy_, bstack11l1lll11l1_opy_):
  bstack11l1l1l1lll_opy_ = bstack11ll1111l1l_opy_(config)
  bstack11l1ll111ll_opy_ = bstack11lll11ll1l_opy_(config)
  if bstack11l1l1l1lll_opy_ is None or bstack11l1ll111ll_opy_ is None:
    logger.error(bstack1l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡸࡵ࡯ࠢࡩࡳࡷࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠼ࠣࡑ࡮ࡹࡳࡪࡰࡪࠤࡦࡻࡴࡩࡧࡱࡸ࡮ࡩࡡࡵ࡫ࡲࡲࠥࡺ࡯࡬ࡧࡱࠫ២"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ៣"), bstack1l1_opy_ (u"ࠬࢁࡽࠨ៤")))
    data = {
        bstack1l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ៥"): config[bstack1l1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬ៦")],
        bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ៧"): config.get(bstack1l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ៨"), os.path.basename(os.getcwd())),
        bstack1l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡖ࡬ࡱࡪ࠭៩"): bstack11111l1l1_opy_(),
        bstack1l1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩ៪"): config.get(bstack1l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨ៫"), bstack1l1_opy_ (u"࠭ࠧ៬")),
        bstack1l1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧ៭"): {
            bstack1l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡒࡦࡳࡥࠨ៮"): bstack11l1l1ll1l1_opy_,
            bstack1l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ៯"): bstack11l1ll11l11_opy_,
            bstack1l1_opy_ (u"ࠪࡷࡩࡱࡖࡦࡴࡶ࡭ࡴࡴࠧ៰"): __version__,
            bstack1l1_opy_ (u"ࠫࡱࡧ࡮ࡨࡷࡤ࡫ࡪ࠭៱"): bstack1l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ៲"),
            bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭៳"): bstack1l1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩ៴"),
            bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ៵"): bstack11l1lll11l1_opy_
        },
        bstack1l1_opy_ (u"ࠩࡶࡩࡹࡺࡩ࡯ࡩࡶࠫ៶"): settings,
        bstack1l1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࡇࡴࡴࡴࡳࡱ࡯ࠫ៷"): bstack11ll11l1lll_opy_(),
        bstack1l1_opy_ (u"ࠫࡨ࡯ࡉ࡯ࡨࡲࠫ៸"): bstack1lll1lll1l_opy_(),
        bstack1l1_opy_ (u"ࠬ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠧ៹"): get_host_info(),
        bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ៺"): bstack11l1l1ll1l_opy_(config)
    }
    headers = {
        bstack1l1_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭៻"): bstack1l1_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫ៼"),
    }
    config = {
        bstack1l1_opy_ (u"ࠩࡤࡹࡹ࡮ࠧ៽"): (bstack11l1l1l1lll_opy_, bstack11l1ll111ll_opy_),
        bstack1l1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫ៾"): headers
    }
    response = bstack11lll11ll_opy_(bstack1l1_opy_ (u"ࠫࡕࡕࡓࡕࠩ៿"), bstack11l1ll11ll1_opy_ + bstack1l1_opy_ (u"ࠬ࠵ࡶ࠳࠱ࡷࡩࡸࡺ࡟ࡳࡷࡱࡷࠬ᠀"), data, config)
    bstack11l1lll1l1l_opy_ = response.json()
    if bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹࠧ᠁")]:
      parsed = json.loads(os.getenv(bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ᠂"), bstack1l1_opy_ (u"ࠨࡽࢀࠫ᠃")))
      parsed[bstack1l1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪ᠄")] = bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠪࡨࡦࡺࡡࠨ᠅")][bstack1l1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ᠆")]
      os.environ[bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭᠇")] = json.dumps(parsed)
      bstack11l11l1lll_opy_.bstack111111ll1_opy_(bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"࠭ࡤࡢࡶࡤࠫ᠈")][bstack1l1_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨ᠉")])
      bstack11l11l1lll_opy_.bstack11l1lll1l11_opy_(bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭᠊")][bstack1l1_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫ᠋")])
      bstack11l11l1lll_opy_.store()
      return bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠪࡨࡦࡺࡡࠨ᠌")][bstack1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡘࡴࡱࡥ࡯ࠩ᠍")], bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠬࡪࡡࡵࡣࠪ᠎")][bstack1l1_opy_ (u"࠭ࡩࡥࠩ᠏")]
    else:
      logger.error(bstack1l1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡵࡹࡳࡴࡩ࡯ࡩࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡀࠠࠨ᠐") + bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ᠑")])
      if bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ᠒")] == bstack1l1_opy_ (u"ࠪࡍࡳࡼࡡ࡭࡫ࡧࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡵࡧࡳࡴࡧࡧ࠲ࠬ᠓"):
        for bstack11l1l1l111l_opy_ in bstack11l1lll1l1l_opy_[bstack1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫ᠔")]:
          logger.error(bstack11l1l1l111l_opy_[bstack1l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭᠕")])
      return None, None
  except Exception as error:
    logger.error(bstack1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡴࡸࡲࠥ࡬࡯ࡳࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࠿ࠦࠢ᠖") +  str(error))
    return None, None
def bstack11l1ll11l1l_opy_():
  if os.getenv(bstack1l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ᠗")) is None:
    return {
        bstack1l1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ᠘"): bstack1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ᠙"),
        bstack1l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ᠚"): bstack1l1_opy_ (u"ࠫࡇࡻࡩ࡭ࡦࠣࡧࡷ࡫ࡡࡵ࡫ࡲࡲࠥ࡮ࡡࡥࠢࡩࡥ࡮ࡲࡥࡥ࠰ࠪ᠛")
    }
  data = {bstack1l1_opy_ (u"ࠬ࡫࡮ࡥࡖ࡬ࡱࡪ࠭᠜"): bstack11111l1l1_opy_()}
  headers = {
      bstack1l1_opy_ (u"࠭ࡁࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭᠝"): bstack1l1_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࠨ᠞") + os.getenv(bstack1l1_opy_ (u"ࠣࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙ࠨ᠟")),
      bstack1l1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨᠠ"): bstack1l1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ᠡ")
  }
  response = bstack11lll11ll_opy_(bstack1l1_opy_ (u"ࠫࡕ࡛ࡔࠨᠢ"), bstack11l1ll11ll1_opy_ + bstack1l1_opy_ (u"ࠬ࠵ࡴࡦࡵࡷࡣࡷࡻ࡮ࡴ࠱ࡶࡸࡴࡶࠧᠣ"), data, { bstack1l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧᠤ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack1l1_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡘࡪࡹࡴࠡࡔࡸࡲࠥࡳࡡࡳ࡭ࡨࡨࠥࡧࡳࠡࡥࡲࡱࡵࡲࡥࡵࡧࡧࠤࡦࡺࠠࠣᠥ") + bstack111l1111l1_opy_().isoformat() + bstack1l1_opy_ (u"ࠨ࡜ࠪᠦ"))
      return {bstack1l1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩᠧ"): bstack1l1_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫᠨ"), bstack1l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᠩ"): bstack1l1_opy_ (u"ࠬ࠭ᠪ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡦࡳࡲࡶ࡬ࡦࡶ࡬ࡳࡳࠦ࡯ࡧࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࡚ࠥࡥࡴࡶࠣࡖࡺࡴ࠺ࠡࠤᠫ") + str(error))
    return {
        bstack1l1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧᠬ"): bstack1l1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᠭ"),
        bstack1l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᠮ"): str(error)
    }
def bstack11l1ll1ll1l_opy_(bstack11l1l1l1ll1_opy_):
    return re.match(bstack1l1_opy_ (u"ࡵࠫࡣࡢࡤࠬࠪ࡟࠲ࡡࡪࠫࠪࡁࠧࠫᠯ"), bstack11l1l1l1ll1_opy_.strip()) is not None
def bstack1l1l1ll111_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11l1ll1ll11_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11l1ll1ll11_opy_ = desired_capabilities
        else:
          bstack11l1ll1ll11_opy_ = {}
        bstack11l1l1l11ll_opy_ = (bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠪᠰ"), bstack1l1_opy_ (u"ࠬ࠭ᠱ")).lower() or caps.get(bstack1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᠲ"), bstack1l1_opy_ (u"ࠧࠨᠳ")).lower())
        if bstack11l1l1l11ll_opy_ == bstack1l1_opy_ (u"ࠨ࡫ࡲࡷࠬᠴ"):
            return True
        if bstack11l1l1l11ll_opy_ == bstack1l1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࠪᠵ"):
            bstack11l1ll11lll_opy_ = str(float(caps.get(bstack1l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬᠶ")) or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᠷ"), {}).get(bstack1l1_opy_ (u"ࠬࡵࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨᠸ"),bstack1l1_opy_ (u"࠭ࠧᠹ"))))
            if bstack11l1l1l11ll_opy_ == bstack1l1_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࠨᠺ") and int(bstack11l1ll11lll_opy_.split(bstack1l1_opy_ (u"ࠨ࠰ࠪᠻ"))[0]) < float(bstack11l1ll111l1_opy_):
                logger.warning(str(bstack11l1l1l1l11_opy_))
                return False
            return True
        bstack1ll11llllll_opy_ = caps.get(bstack1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᠼ"), {}).get(bstack1l1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧᠽ"), caps.get(bstack1l1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫᠾ"), bstack1l1_opy_ (u"ࠬ࠭ᠿ")))
        if bstack1ll11llllll_opy_:
            logger.warning(bstack1l1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡄࡦࡵ࡮ࡸࡴࡶࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥᡀ"))
            return False
        browser = caps.get(bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬᡁ"), bstack1l1_opy_ (u"ࠨࠩᡂ")).lower() or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᡃ"), bstack1l1_opy_ (u"ࠪࠫᡄ")).lower()
        if browser != bstack1l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫᡅ"):
            logger.warning(bstack1l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣᡆ"))
            return False
        browser_version = caps.get(bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᡇ")) or caps.get(bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᡈ")) or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᡉ")) or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᡊ"), {}).get(bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᡋ")) or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᡌ"), {}).get(bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᡍ"))
        bstack1ll1l1ll1l1_opy_ = bstack11l1lll1111_opy_.bstack1ll1l1l111l_opy_
        bstack11l1ll1111l_opy_ = False
        if config is not None:
          bstack11l1ll1111l_opy_ = bstack1l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᡎ") in config and str(config[bstack1l1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫᡏ")]).lower() != bstack1l1_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧᡐ")
        if os.environ.get(bstack1l1_opy_ (u"ࠩࡌࡗࡤࡔࡏࡏࡡࡅࡗ࡙ࡇࡃࡌࡡࡌࡒࡋࡘࡁࡠࡃ࠴࠵࡞ࡥࡓࡆࡕࡖࡍࡔࡔࠧᡑ"), bstack1l1_opy_ (u"ࠪࠫᡒ")).lower() == bstack1l1_opy_ (u"ࠫࡹࡸࡵࡦࠩᡓ") or bstack11l1ll1111l_opy_:
          bstack1ll1l1ll1l1_opy_ = bstack11l1lll1111_opy_.bstack1ll1l1l11l1_opy_
        if browser_version and browser_version != bstack1l1_opy_ (u"ࠬࡲࡡࡵࡧࡶࡸࠬᡔ") and int(browser_version.split(bstack1l1_opy_ (u"࠭࠮ࠨᡕ"))[0]) <= bstack1ll1l1ll1l1_opy_:
          logger.warning(bstack1ll1llllll1_opy_ (u"ࠧࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡪࡶࡪࡧࡴࡦࡴࠣࡸ࡭ࡧ࡮ࠡࡽࡰ࡭ࡳࡥࡡ࠲࠳ࡼࡣࡸࡻࡰࡱࡱࡵࡸࡪࡪ࡟ࡤࡪࡵࡳࡲ࡫࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࡾ࠰ࠪᡖ"))
          return False
        if not options:
          bstack1ll1l11l111_opy_ = caps.get(bstack1l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᡗ")) or bstack11l1ll1ll11_opy_.get(bstack1l1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᡘ"), {})
          if bstack1l1_opy_ (u"ࠪ࠱࠲࡮ࡥࡢࡦ࡯ࡩࡸࡹࠧᡙ") in bstack1ll1l11l111_opy_.get(bstack1l1_opy_ (u"ࠫࡦࡸࡧࡴࠩᡚ"), []):
              logger.warning(bstack1l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠ࡯ࡱࡷࠤࡷࡻ࡮ࠡࡱࡱࠤࡱ࡫ࡧࡢࡥࡼࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲࡙ࠥࡷࡪࡶࡦ࡬ࠥࡺ࡯ࠡࡰࡨࡻࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩࠥࡵࡲࠡࡣࡹࡳ࡮ࡪࠠࡶࡵ࡬ࡲ࡬ࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠢᡛ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack1l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡼࡡ࡭࡫ࡧࡥࡹ࡫ࠠࡢ࠳࠴ࡽࠥࡹࡵࡱࡲࡲࡶࡹࠦ࠺ࠣᡜ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1lll111ll11_opy_ = config.get(bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᡝ"), {})
    bstack1lll111ll11_opy_[bstack1l1_opy_ (u"ࠨࡣࡸࡸ࡭࡚࡯࡬ࡧࡱࠫᡞ")] = os.getenv(bstack1l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᡟ"))
    bstack11llll1111l_opy_ = json.loads(os.getenv(bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᡠ"), bstack1l1_opy_ (u"ࠫࢀࢃࠧᡡ"))).get(bstack1l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᡢ"))
    if not config[bstack1l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡕࡸ࡯ࡥࡷࡦࡸࡒࡧࡰࠨᡣ")].get(bstack1l1_opy_ (u"ࠢࡢࡲࡳࡣࡦࡻࡴࡰ࡯ࡤࡸࡪࠨᡤ")):
      if bstack1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᡥ") in caps:
        caps[bstack1l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᡦ")][bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᡧ")] = bstack1lll111ll11_opy_
        caps[bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᡨ")][bstack1l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᡩ")][bstack1l1_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᡪ")] = bstack11llll1111l_opy_
      else:
        caps[bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᡫ")] = bstack1lll111ll11_opy_
        caps[bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᡬ")][bstack1l1_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᡭ")] = bstack11llll1111l_opy_
  except Exception as error:
    logger.debug(bstack1l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠰ࠣࡉࡷࡸ࡯ࡳ࠼ࠣࠦᡮ") +  str(error))
def bstack1lll11111l_opy_(driver, bstack11l1l1lllll_opy_):
  try:
    setattr(driver, bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫᡯ"), True)
    session = driver.session_id
    if session:
      bstack11l1l1l1l1l_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11l1l1l1l1l_opy_ = False
      bstack11l1l1l1l1l_opy_ = url.scheme in [bstack1l1_opy_ (u"ࠧ࡮ࡴࡵࡲࠥᡰ"), bstack1l1_opy_ (u"ࠨࡨࡵࡶࡳࡷࠧᡱ")]
      if bstack11l1l1l1l1l_opy_:
        if bstack11l1l1lllll_opy_:
          logger.info(bstack1l1_opy_ (u"ࠢࡔࡧࡷࡹࡵࠦࡦࡰࡴࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡭ࡧࡳࠡࡵࡷࡥࡷࡺࡥࡥ࠰ࠣࡅࡺࡺ࡯࡮ࡣࡷࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡧࡻࡩࡨࡻࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡥࡩ࡬࡯࡮ࠡ࡯ࡲࡱࡪࡴࡴࡢࡴ࡬ࡰࡾ࠴ࠢᡲ"))
      return bstack11l1l1lllll_opy_
  except Exception as e:
    logger.error(bstack1l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡴࡶࡤࡶࡹ࡯࡮ࡨࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡤࡣࡱࠤ࡫ࡵࡲࠡࡶ࡫࡭ࡸࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦ࠼ࠣࠦᡳ") + str(e))
    return False
def bstack1l111lll1l_opy_(driver, name, path):
  try:
    bstack1ll1l1ll111_opy_ = {
        bstack1l1_opy_ (u"ࠩࡷ࡬࡙࡫ࡳࡵࡔࡸࡲ࡚ࡻࡩࡥࠩᡴ"): threading.current_thread().current_test_uuid,
        bstack1l1_opy_ (u"ࠪࡸ࡭ࡈࡵࡪ࡮ࡧ࡙ࡺ࡯ࡤࠨᡵ"): os.environ.get(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᡶ"), bstack1l1_opy_ (u"ࠬ࠭ᡷ")),
        bstack1l1_opy_ (u"࠭ࡴࡩࡌࡺࡸ࡙ࡵ࡫ࡦࡰࠪᡸ"): os.environ.get(bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ᡹"), bstack1l1_opy_ (u"ࠨࠩ᡺"))
    }
    bstack1ll11lll111_opy_ = bstack11l11l111l_opy_.bstack1ll11lll1l1_opy_(EVENTS.bstack1l11111l11_opy_.value)
    logger.debug(bstack1l1_opy_ (u"ࠩࡓࡩࡷ࡬࡯ࡳ࡯࡬ࡲ࡬ࠦࡳࡤࡣࡱࠤࡧ࡫ࡦࡰࡴࡨࠤࡸࡧࡶࡪࡰࡪࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠬ᡻"))
    try:
      if (bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ᡼"), None) and bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭᡽"), None)):
        scripts = {bstack1l1_opy_ (u"ࠬࡹࡣࡢࡰࠪ᡾"): bstack11l11l1lll_opy_.perform_scan}
        bstack11l1ll1llll_opy_ = json.loads(scripts[bstack1l1_opy_ (u"ࠨࡳࡤࡣࡱࠦ᡿")].replace(bstack1l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥᢀ"), bstack1l1_opy_ (u"ࠣࠤᢁ")))
        bstack11l1ll1llll_opy_[bstack1l1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬᢂ")][bstack1l1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࠪᢃ")] = None
        scripts[bstack1l1_opy_ (u"ࠦࡸࡩࡡ࡯ࠤᢄ")] = bstack1l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࠣᢅ") + json.dumps(bstack11l1ll1llll_opy_)
        bstack11l11l1lll_opy_.bstack111111ll1_opy_(scripts)
        bstack11l11l1lll_opy_.store()
        logger.debug(driver.execute_script(bstack11l11l1lll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11l11l1lll_opy_.perform_scan, {bstack1l1_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࠨᢆ"): name}))
      bstack11l11l111l_opy_.end(EVENTS.bstack1l11111l11_opy_.value, bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᢇ"), bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᢈ"), True, None)
    except Exception as error:
      bstack11l11l111l_opy_.end(EVENTS.bstack1l11111l11_opy_.value, bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᢉ"), bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᢊ"), False, str(error))
    bstack1ll11lll111_opy_ = bstack11l11l111l_opy_.bstack11l1ll11111_opy_(EVENTS.bstack1ll1l1llll1_opy_.value)
    bstack11l11l111l_opy_.mark(bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᢋ"))
    try:
      if (bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"ࠬ࡯ࡳࡂࡲࡳࡅ࠶࠷ࡹࡕࡧࡶࡸࠬᢌ"), None) and bstack1l11l1l1_opy_(threading.current_thread(), bstack1l1_opy_ (u"࠭ࡡࡱࡲࡄ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᢍ"), None)):
        scripts = {bstack1l1_opy_ (u"ࠧࡴࡥࡤࡲࠬᢎ"): bstack11l11l1lll_opy_.perform_scan}
        bstack11l1ll1llll_opy_ = json.loads(scripts[bstack1l1_opy_ (u"ࠣࡵࡦࡥࡳࠨᢏ")].replace(bstack1l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧᢐ"), bstack1l1_opy_ (u"ࠥࠦᢑ")))
        bstack11l1ll1llll_opy_[bstack1l1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᢒ")][bstack1l1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬᢓ")] = None
        scripts[bstack1l1_opy_ (u"ࠨࡳࡤࡣࡱࠦᢔ")] = bstack1l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥᢕ") + json.dumps(bstack11l1ll1llll_opy_)
        bstack11l11l1lll_opy_.bstack111111ll1_opy_(scripts)
        bstack11l11l1lll_opy_.store()
        logger.debug(driver.execute_script(bstack11l11l1lll_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack11l11l1lll_opy_.bstack11l1l1llll1_opy_, bstack1ll1l1ll111_opy_))
      bstack11l11l111l_opy_.end(bstack1ll11lll111_opy_, bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣᢖ"), bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢᢗ"),True, None)
    except Exception as error:
      bstack11l11l111l_opy_.end(bstack1ll11lll111_opy_, bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᢘ"), bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᢙ"),False, str(error))
    logger.info(bstack1l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤ࡭ࡧࡳࠡࡧࡱࡨࡪࡪ࠮ࠣᢚ"))
  except Exception as bstack1ll1ll11l11_opy_:
    logger.error(bstack1l1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹࠠࡤࡱࡸࡰࡩࠦ࡮ࡰࡶࠣࡦࡪࠦࡰࡳࡱࡦࡩࡸࡹࡥࡥࠢࡩࡳࡷࠦࡴࡩࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࡀࠠࠣᢛ") + str(path) + bstack1l1_opy_ (u"ࠢࠡࡇࡵࡶࡴࡸࠠ࠻ࠤᢜ") + str(bstack1ll1ll11l11_opy_))
def bstack11l1ll1l111_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack1l1_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠢᢝ")) and str(caps.get(bstack1l1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣᢞ"))).lower() == bstack1l1_opy_ (u"ࠥࡥࡳࡪࡲࡰ࡫ࡧࠦᢟ"):
        bstack11l1ll11lll_opy_ = caps.get(bstack1l1_opy_ (u"ࠦࡦࡶࡰࡪࡷࡰ࠾ࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨᢠ")) or caps.get(bstack1l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢᢡ"))
        if bstack11l1ll11lll_opy_ and int(str(bstack11l1ll11lll_opy_)) < bstack11l1ll111l1_opy_:
            return False
    return True
def bstack11l1l1111_opy_(config):
  if bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᢢ") in config:
        return config[bstack1l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᢣ")]
  for platform in config.get(bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᢤ"), []):
      if bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᢥ") in platform:
          return platform[bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᢦ")]
  return None
def bstack1l111ll1_opy_(bstack1ll11llll1_opy_):
  try:
    browser_name = bstack1ll11llll1_opy_[bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧࠪᢧ")]
    browser_version = bstack1ll11llll1_opy_[bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᢨ")]
    chrome_options = bstack1ll11llll1_opy_[bstack1l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡥ࡯ࡱࡶ࡬ࡳࡳࡹᢩࠧ")]
    try:
        bstack11l1lll11ll_opy_ = int(browser_version.split(bstack1l1_opy_ (u"ࠧ࠯ࠩᢪ"))[0])
    except ValueError as e:
        logger.error(bstack1l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡣࡰࡰࡹࡩࡷࡺࡩ࡯ࡩࠣࡦࡷࡵࡷࡴࡧࡵࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠧ᢫") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack1l1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩ᢬")):
        logger.warning(bstack1l1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡇ࡭ࡸ࡯࡮ࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷ࠳ࠨ᢭"))
        return False
    if bstack11l1lll11ll_opy_ < bstack11l1lll1111_opy_.bstack1ll1l1l11l1_opy_:
        logger.warning(bstack1ll1llllll1_opy_ (u"ࠫࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡴࡨࡵࡺ࡯ࡲࡦࡵࠣࡇ࡭ࡸ࡯࡮ࡧࠣࡺࡪࡸࡳࡪࡱࡱࠤࢀࡉࡏࡏࡕࡗࡅࡓ࡚ࡓ࠯ࡏࡌࡒࡎࡓࡕࡎࡡࡑࡓࡓࡥࡂࡔࡖࡄࡇࡐࡥࡉࡏࡈࡕࡅࡤࡇ࠱࠲࡛ࡢࡗ࡚ࡖࡐࡐࡔࡗࡉࡉࡥࡃࡉࡔࡒࡑࡊࡥࡖࡆࡔࡖࡍࡔࡔࡽࠡࡱࡵࠤ࡭࡯ࡧࡩࡧࡵ࠲ࠬ᢮"))
        return False
    if chrome_options and any(bstack1l1_opy_ (u"ࠬ࠳࠭ࡩࡧࡤࡨࡱ࡫ࡳࡴࠩ᢯") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack1l1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡲࡲࠥࡲࡥࡨࡣࡦࡽࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠦࡓࡸ࡫ࡷࡧ࡭ࠦࡴࡰࠢࡱࡩࡼࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪࠦ࡯ࡳࠢࡤࡺࡴ࡯ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠣᢰ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack1l1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡦ࡬ࡪࡩ࡫ࡪࡰࡪࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡳࡶࡲࡳࡳࡷࡺࠠࡧࡱࡵࠤࡱࡵࡣࡢ࡮ࠣࡇ࡭ࡸ࡯࡮ࡧ࠽ࠤࠧᢱ") + str(e))
    return False
def bstack1llllll1l_opy_(bstack1l1ll1lll_opy_, config):
    try:
      bstack1ll11ll11ll_opy_ = bstack1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᢲ") in config and config[bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᢳ")] == True
      bstack11l1ll1111l_opy_ = bstack1l1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧᢴ") in config and str(config[bstack1l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨᢵ")]).lower() != bstack1l1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫᢶ")
      if not (bstack1ll11ll11ll_opy_ and (not bstack11l1l1ll1l_opy_(config) or bstack11l1ll1111l_opy_)):
        return bstack1l1ll1lll_opy_
      bstack11l1l1ll1ll_opy_ = bstack11l11l1lll_opy_.bstack11l1ll1l11l_opy_
      if bstack11l1l1ll1ll_opy_ is None:
        logger.debug(bstack1l1_opy_ (u"ࠨࡇࡰࡱࡪࡰࡪࠦࡣࡩࡴࡲࡱࡪࠦ࡯ࡱࡶ࡬ࡳࡳࡹࠠࡢࡴࡨࠤࡓࡵ࡮ࡦࠤᢷ"))
        return bstack1l1ll1lll_opy_
      bstack11l1l1lll1l_opy_ = int(str(bstack11ll11l1111_opy_()).split(bstack1l1_opy_ (u"ࠧ࠯ࠩᢸ"))[0])
      logger.debug(bstack1l1_opy_ (u"ࠣࡕࡨࡰࡪࡴࡩࡶ࡯ࠣࡺࡪࡸࡳࡪࡱࡱࠤࡩ࡫ࡴࡦࡥࡷࡩࡩࡀࠠࠣᢹ") + str(bstack11l1l1lll1l_opy_) + bstack1l1_opy_ (u"ࠤࠥᢺ"))
      if bstack11l1l1lll1l_opy_ == 3 and isinstance(bstack1l1ll1lll_opy_, dict) and bstack1l1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᢻ") in bstack1l1ll1lll_opy_ and bstack11l1l1ll1ll_opy_ is not None:
        if bstack1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᢼ") not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᢽ")]:
          bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭ᢾ")][bstack1l1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᢿ")] = {}
        if bstack1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ᣀ") in bstack11l1l1ll1ll_opy_:
          if bstack1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧᣁ") not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᣂ")][bstack1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᣃ")]:
            bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᣄ")][bstack1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᣅ")][bstack1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬᣆ")] = []
          for arg in bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ᣇ")]:
            if arg not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᣈ")][bstack1l1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᣉ")][bstack1l1_opy_ (u"ࠫࡦࡸࡧࡴࠩᣊ")]:
              bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᣋ")][bstack1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᣌ")][bstack1l1_opy_ (u"ࠧࡢࡴࡪࡷࠬᣍ")].append(arg)
        if bstack1l1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬᣎ") in bstack11l1l1ll1ll_opy_:
          if bstack1l1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ᣏ") not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᣐ")][bstack1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᣑ")]:
            bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᣒ")][bstack1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᣓ")][bstack1l1_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫᣔ")] = []
          for ext in bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠨࡧࡻࡸࡪࡴࡳࡪࡱࡱࡷࠬᣕ")]:
            if ext not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᣖ")][bstack1l1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᣗ")][bstack1l1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨᣘ")]:
              bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᣙ")][bstack1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᣚ")][bstack1l1_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫᣛ")].append(ext)
        if bstack1l1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧᣜ") in bstack11l1l1ll1ll_opy_:
          if bstack1l1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨᣝ") not in bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᣞ")][bstack1l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᣟ")]:
            bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᣠ")][bstack1l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᣡ")][bstack1l1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ᣢ")] = {}
          bstack11llll111ll_opy_(bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨᣣ")][bstack1l1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᣤ")][bstack1l1_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩᣥ")],
                    bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪᣦ")])
        os.environ[bstack1l1_opy_ (u"ࠬࡏࡓࡠࡐࡒࡒࡤࡈࡓࡕࡃࡆࡏࡤࡏࡎࡇࡔࡄࡣࡆ࠷࠱࡚ࡡࡖࡉࡘ࡙ࡉࡐࡐࠪᣧ")] = bstack1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫᣨ")
        return bstack1l1ll1lll_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l1ll1lll_opy_, ChromeOptions):
          chrome_options = bstack1l1ll1lll_opy_
        elif isinstance(bstack1l1ll1lll_opy_, dict):
          for value in bstack1l1ll1lll_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l1ll1lll_opy_, dict):
            bstack1l1ll1lll_opy_[bstack1l1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨᣩ")] = chrome_options
          else:
            bstack1l1ll1lll_opy_ = chrome_options
        if bstack11l1l1ll1ll_opy_ is not None:
          if bstack1l1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ᣪ") in bstack11l1l1ll1ll_opy_:
                bstack11l1l1lll11_opy_ = chrome_options.arguments or []
                new_args = bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧᣫ")]
                for arg in new_args:
                    if arg not in bstack11l1l1lll11_opy_:
                        chrome_options.add_argument(arg)
          if bstack1l1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧᣬ") in bstack11l1l1ll1ll_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack1l1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨᣭ"), [])
                bstack11l1lll111l_opy_ = bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩᣮ")]
                for extension in bstack11l1lll111l_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack1l1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬᣯ") in bstack11l1l1ll1ll_opy_:
                bstack11l1ll1lll1_opy_ = chrome_options.experimental_options.get(bstack1l1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ᣰ"), {})
                bstack11l1ll1l1ll_opy_ = bstack11l1l1ll1ll_opy_[bstack1l1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧᣱ")]
                bstack11llll111ll_opy_(bstack11l1ll1lll1_opy_, bstack11l1ll1l1ll_opy_)
                chrome_options.add_experimental_option(bstack1l1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨᣲ"), bstack11l1ll1lll1_opy_)
        os.environ[bstack1l1_opy_ (u"ࠪࡍࡘࡥࡎࡐࡐࡢࡆࡘ࡚ࡁࡄࡍࡢࡍࡓࡌࡒࡂࡡࡄ࠵࠶࡟࡟ࡔࡇࡖࡗࡎࡕࡎࠨᣳ")] = bstack1l1_opy_ (u"ࠫࡹࡸࡵࡦࠩᣴ")
        return bstack1l1ll1lll_opy_
    except Exception as e:
      logger.error(bstack1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡥࡩࡪࡩ࡯ࡩࠣࡲࡴࡴ࠭ࡃࡕࠣ࡭ࡳ࡬ࡲࡢࠢࡤ࠵࠶ࡿࠠࡤࡪࡵࡳࡲ࡫ࠠࡰࡲࡷ࡭ࡴࡴࡳ࠻ࠢࠥᣵ") + str(e))
      return bstack1l1ll1lll_opy_