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
import atexit
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from browserstack_sdk.bstack1lll1ll1l_opy_ import bstack1llllll11l_opy_
from browserstack_sdk.bstack1lll1lll_opy_ import *
import time
import requests
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.measure import measure
def bstack11ll1l1ll_opy_():
  global CONFIG
  headers = {
        bstack1ll_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack1ll_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1ll1l111l1_opy_(CONFIG, bstack11111l1l1_opy_)
  try:
    response = requests.get(bstack11111l1l1_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack1llll111ll_opy_ = response.json()[bstack1ll_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1ll1lll1ll_opy_.format(response.json()))
      return bstack1llll111ll_opy_
    else:
      logger.debug(bstack11l111ll_opy_.format(bstack1ll_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack11l111ll_opy_.format(e))
def bstack11llllll11_opy_(hub_url):
  global CONFIG
  url = bstack1ll_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack1ll_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack1ll_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack1ll_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1ll1l111l1_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1lll111l1l_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1ll11lllll_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack1ll1ll1l11_opy_, stage=STAGE.bstack1llll11lll_opy_)
def bstack1lllllll1l_opy_():
  try:
    global bstack11llll1l1_opy_
    bstack1llll111ll_opy_ = bstack11ll1l1ll_opy_()
    bstack1lll11ll1l_opy_ = []
    results = []
    for bstack1l1lll1l1_opy_ in bstack1llll111ll_opy_:
      bstack1lll11ll1l_opy_.append(bstack11l11l11l1_opy_(target=bstack11llllll11_opy_,args=(bstack1l1lll1l1_opy_,)))
    for t in bstack1lll11ll1l_opy_:
      t.start()
    for t in bstack1lll11ll1l_opy_:
      results.append(t.join())
    bstack1lll11l1ll_opy_ = {}
    for item in results:
      hub_url = item[bstack1ll_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬࡾ")]
      latency = item[bstack1ll_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭ࡿ")]
      bstack1lll11l1ll_opy_[hub_url] = latency
    bstack1ll1l1ll_opy_ = min(bstack1lll11l1ll_opy_, key= lambda x: bstack1lll11l1ll_opy_[x])
    bstack11llll1l1_opy_ = bstack1ll1l1ll_opy_
    logger.debug(bstack11l1lll11l_opy_.format(bstack1ll1l1ll_opy_))
  except Exception as e:
    logger.debug(bstack1l111111l_opy_.format(e))
from browserstack_sdk.bstack1l111lll_opy_ import *
from browserstack_sdk.bstack11ll1111l_opy_ import *
from browserstack_sdk.bstack11l11111l_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack111ll11ll_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack1l111l1l_opy_, stage=STAGE.bstack1llll11lll_opy_)
def bstack1l11llll1_opy_():
    global bstack11llll1l1_opy_
    try:
        bstack11l1ll11_opy_ = bstack111l11111_opy_()
        bstack111llllll_opy_(bstack11l1ll11_opy_)
        hub_url = bstack11l1ll11_opy_.get(bstack1ll_opy_ (u"ࠨࡵࡳ࡮ࠥࢀ"), bstack1ll_opy_ (u"ࠢࠣࢁ"))
        if hub_url.endswith(bstack1ll_opy_ (u"ࠨ࠱ࡺࡨ࠴࡮ࡵࡣࠩࢂ")):
            hub_url = hub_url.rsplit(bstack1ll_opy_ (u"ࠩ࠲ࡻࡩ࠵ࡨࡶࡤࠪࢃ"), 1)[0]
        if hub_url.startswith(bstack1ll_opy_ (u"ࠪ࡬ࡹࡺࡰ࠻࠱࠲ࠫࢄ")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack1ll_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴࠭ࢅ")):
            hub_url = hub_url[8:]
        bstack11llll1l1_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack111l11111_opy_():
    global CONFIG
    bstack11l1l1l1l_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢆ"), {}).get(bstack1ll_opy_ (u"࠭ࡧࡳ࡫ࡧࡒࡦࡳࡥࠨࢇ"), bstack1ll_opy_ (u"ࠧࡏࡑࡢࡋࡗࡏࡄࡠࡐࡄࡑࡊࡥࡐࡂࡕࡖࡉࡉ࠭࢈"))
    if not isinstance(bstack11l1l1l1l_opy_, str):
        raise ValueError(bstack1ll_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡈࡴ࡬ࡨࠥࡴࡡ࡮ࡧࠣࡱࡺࡹࡴࠡࡤࡨࠤࡦࠦࡶࡢ࡮࡬ࡨࠥࡹࡴࡳ࡫ࡱ࡫ࠧࢉ"))
    try:
        bstack11l1ll11_opy_ = bstack1111l1l1l_opy_(bstack11l1l1l1l_opy_)
        return bstack11l1ll11_opy_
    except Exception as e:
        logger.error(bstack1ll_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤ࡬ࡸࡩࡥࠢࡧࡩࡹࡧࡩ࡭ࡵࠣ࠾ࠥࢁࡽࠣࢊ").format(str(e)))
        return {}
def bstack1111l1l1l_opy_(bstack11l1l1l1l_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack1ll_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࢋ")] or not CONFIG[bstack1ll_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧࢌ")]:
            raise ValueError(bstack1ll_opy_ (u"ࠧࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡻࡳࡦࡴࡱࡥࡲ࡫ࠠࡰࡴࠣࡥࡨࡩࡥࡴࡵࠣ࡯ࡪࡿࠢࢍ"))
        url = bstack1ll111111l_opy_ + bstack11l1l1l1l_opy_
        auth = (CONFIG[bstack1ll_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࢎ")], CONFIG[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ࢏")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack111111l1l_opy_ = json.loads(response.text)
            return bstack111111l1l_opy_
    except ValueError as ve:
        logger.error(bstack1ll_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤ࡬ࡸࡩࡥࠢࡧࡩࡹࡧࡩ࡭ࡵࠣ࠾ࠥࢁࡽࠣ࢐").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack1ll_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥ࡭ࡲࡪࡦࠣࡨࡪࡺࡡࡪ࡮ࡶࠤ࠿ࠦࡻࡾࠤ࢑").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack111llllll_opy_(bstack11l1ll1l11_opy_):
    global CONFIG
    if bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ࢒") not in CONFIG or str(CONFIG[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ࢓")]).lower() == bstack1ll_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ࢔"):
        CONFIG[bstack1ll_opy_ (u"࠭࡬ࡰࡥࡤࡰࠬ࢕")] = False
    elif bstack1ll_opy_ (u"ࠧࡪࡵࡗࡶ࡮ࡧ࡬ࡈࡴ࡬ࡨࠬ࢖") in bstack11l1ll1l11_opy_:
        bstack111ll1ll_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࢗ"), {})
        logger.debug(bstack1ll_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴࡩࡡ࡭ࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࠪࡹࠢ࢘"), bstack111ll1ll_opy_)
        bstack1lllll11ll_opy_ = bstack11l1ll1l11_opy_.get(bstack1ll_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯ࡕࡩࡵ࡫ࡡࡵࡧࡵࡷ࢙ࠧ"), [])
        bstack1ll1ll11l_opy_ = bstack1ll_opy_ (u"ࠦ࠱ࠨ࢚").join(bstack1lllll11ll_opy_)
        logger.debug(bstack1ll_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡈࡻࡳࡵࡱࡰࠤࡷ࡫ࡰࡦࡣࡷࡩࡷࠦࡳࡵࡴ࡬ࡲ࡬ࡀࠠࠦࡵ࢛ࠥ"), bstack1ll1ll11l_opy_)
        bstack11ll1l11l_opy_ = {
            bstack1ll_opy_ (u"ࠨ࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣ࢜"): bstack1ll_opy_ (u"ࠢࡢࡶࡶ࠱ࡷ࡫ࡰࡦࡣࡷࡩࡷࠨ࢝"),
            bstack1ll_opy_ (u"ࠣࡨࡲࡶࡨ࡫ࡌࡰࡥࡤࡰࠧ࢞"): bstack1ll_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ࢟"),
            bstack1ll_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯࠰ࡶࡪࡶࡥࡢࡶࡨࡶࠧࢠ"): bstack1ll1ll11l_opy_
        }
        bstack111ll1ll_opy_.update(bstack11ll1l11l_opy_)
        logger.debug(bstack1ll_opy_ (u"ࠦࡆ࡚ࡓࠡ࠼࡙ࠣࡵࡪࡡࡵࡧࡧࠤࡱࡵࡣࡢ࡮ࠣࡳࡵࡺࡩࡰࡰࡶ࠾ࠥࠫࡳࠣࢡ"), bstack111ll1ll_opy_)
        CONFIG[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢢ")] = bstack111ll1ll_opy_
        logger.debug(bstack1ll_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡌࡩ࡯ࡣ࡯ࠤࡈࡕࡎࡇࡋࡊ࠾ࠥࠫࡳࠣࢣ"), CONFIG)
def bstack111l11ll_opy_():
    bstack11l1ll11_opy_ = bstack111l11111_opy_()
    if not bstack11l1ll11_opy_[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࡙ࡷࡲࠧࢤ")]:
      raise ValueError(bstack1ll_opy_ (u"ࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ࡚ࡸ࡬ࠡ࡫ࡶࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࡬ࡲࡰ࡯ࠣ࡫ࡷ࡯ࡤࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠥࢥ"))
    return bstack11l1ll11_opy_[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࡛ࡲ࡭ࠩࢦ")] + bstack1ll_opy_ (u"ࠪࡃࡨࡧࡰࡴ࠿ࠪࢧ")
@measure(event_name=EVENTS.bstack1ll11l11l1_opy_, stage=STAGE.bstack1llll11lll_opy_)
def bstack1l1lll1l_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack1ll_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ࢨ")], CONFIG[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࢩ")])
        url = bstack1ll111l1l_opy_
        logger.debug(bstack1ll_opy_ (u"ࠨࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷࠥ࡬ࡲࡰ࡯ࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡗࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࠦࡁࡑࡋࠥࢪ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack1ll_opy_ (u"ࠢࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪࠨࢫ"): bstack1ll_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠦࢬ")})
            if response.status_code == 200:
                bstack1l11l1lll1_opy_ = json.loads(response.text)
                bstack11lllll111_opy_ = bstack1l11l1lll1_opy_.get(bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡴࠩࢭ"), [])
                if bstack11lllll111_opy_:
                    bstack1l1l1l111l_opy_ = bstack11lllll111_opy_[0]
                    build_hashed_id = bstack1l1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ࢮ"))
                    bstack1ll11ll111_opy_ = bstack1l1ll1llll_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack1ll11ll111_opy_])
                    logger.info(bstack1lllll11l1_opy_.format(bstack1ll11ll111_opy_))
                    bstack1ll11lll1l_opy_ = CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧࢯ")]
                    if bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࢰ") in CONFIG:
                      bstack1ll11lll1l_opy_ += bstack1ll_opy_ (u"࠭ࠠࠨࢱ") + CONFIG[bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࢲ")]
                    if bstack1ll11lll1l_opy_ != bstack1l1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠨࡰࡤࡱࡪ࠭ࢳ")):
                      logger.debug(bstack1l111l1lll_opy_.format(bstack1l1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧࢴ")), bstack1ll11lll1l_opy_))
                    return result
                else:
                    logger.debug(bstack1ll_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡑࡳࠥࡨࡵࡪ࡮ࡧࡷࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡵࡪࡨࠤࡷ࡫ࡳࡱࡱࡱࡷࡪ࠴ࠢࢵ"))
            else:
                logger.debug(bstack1ll_opy_ (u"ࠦࡆ࡚ࡓࠡ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷ࠳ࠨࢶ"))
        except Exception as e:
            logger.error(bstack1ll_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡣࡷ࡬ࡰࡩࡹࠠ࠻ࠢࡾࢁࠧࢷ").format(str(e)))
    else:
        logger.debug(bstack1ll_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡉࡏࡏࡈࡌࡋࠥ࡯ࡳࠡࡰࡲࡸࠥࡹࡥࡵ࠰࡙ࠣࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷ࠳ࠨࢸ"))
    return [None, None]
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.bstack1lll1l1l11_opy_ import bstack1lll1l1l11_opy_, bstack1l1lll11l1_opy_, bstack11l111ll11_opy_, bstack1l1l1ll1l_opy_
from bstack_utils.measure import bstack1ll1lll1l_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack1l1ll11l1_opy_ import bstack1llll1l111_opy_
from bstack_utils.messages import *
from bstack_utils import bstack111ll11ll_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack11lllll1_opy_, bstack11ll1l1ll1_opy_, bstack11llll1111_opy_, bstack11ll11l1_opy_, \
  bstack11ll11l1l1_opy_, \
  Notset, bstack11111l1l_opy_, \
  bstack1ll1l1ll1_opy_, bstack1l111lllll_opy_, bstack1l1ll1ll1l_opy_, bstack11l1lll1_opy_, bstack1l11l1ll_opy_, bstack1l1111l111_opy_, \
  bstack11l1l11ll1_opy_, \
  bstack11ll11l111_opy_, bstack1l1ll11l11_opy_, bstack1l1l11ll11_opy_, bstack1l1l1l1l11_opy_, \
  bstack11lll1l1l_opy_, bstack1l1l111ll1_opy_, bstack11ll1lllll_opy_, bstack1lll1ll111_opy_
from bstack_utils.bstack11l1llllll_opy_ import bstack1lll1l1ll1_opy_, bstack11lll1ll11_opy_
from bstack_utils.bstack1llll11ll_opy_ import bstack111l11l11_opy_
from bstack_utils.bstack1ll11l111_opy_ import bstack11llll111_opy_, bstack11l11ll111_opy_
from bstack_utils.bstack1l11l1l1l_opy_ import bstack1l11l1l1l_opy_
from bstack_utils.bstack1lll1l111_opy_ import bstack1l1lll1l11_opy_
from bstack_utils.proxy import bstack1l1ll1lll_opy_, bstack1ll1l111l1_opy_, bstack1l1111l11_opy_, bstack11lll1lll_opy_
from bstack_utils.bstack1lll1l1l1l_opy_ import bstack1111ll111_opy_
import bstack_utils.bstack11l1ll111l_opy_ as bstack11l1lllll1_opy_
import bstack_utils.bstack111l11lll_opy_ as bstack1111111l_opy_
from browserstack_sdk.sdk_cli.cli import cli
from browserstack_sdk.sdk_cli.utils.bstack1l11ll111_opy_ import bstack1ll11l1111_opy_
from bstack_utils.bstack1llll11l1l_opy_ import bstack1ll1ll1ll_opy_
if os.getenv(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡌࡔࡕࡋࡔࠩࢹ")):
  cli.bstack1l111ll1l1_opy_()
else:
  os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡍࡕࡏࡌࡕࠪࢺ")] = bstack1ll_opy_ (u"ࠩࡷࡶࡺ࡫ࠧࢻ")
bstack1l1ll1l1l1_opy_ = bstack1ll_opy_ (u"ࠪࠤࠥ࠵ࠪࠡ࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࠥ࠰࠯࡝ࡰࠣࠤ࡮࡬ࠨࡱࡣࡪࡩࠥࡃ࠽࠾ࠢࡹࡳ࡮ࡪࠠ࠱ࠫࠣࡿࡡࡴࠠࠡࠢࡷࡶࡾࢁ࡜࡯ࠢࡦࡳࡳࡹࡴࠡࡨࡶࠤࡂࠦࡲࡦࡳࡸ࡭ࡷ࡫ࠨ࡝ࠩࡩࡷࡡ࠭ࠩ࠼࡞ࡱࠤࠥࠦࠠࠡࡨࡶ࠲ࡦࡶࡰࡦࡰࡧࡊ࡮ࡲࡥࡔࡻࡱࡧ࠭ࡨࡳࡵࡣࡦ࡯ࡤࡶࡡࡵࡪ࠯ࠤࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡶ࡟ࡪࡰࡧࡩࡽ࠯ࠠࠬࠢࠥ࠾ࠧࠦࠫࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡍࡗࡔࡔ࠮ࡱࡣࡵࡷࡪ࠮ࠨࡢࡹࡤ࡭ࡹࠦ࡮ࡦࡹࡓࡥ࡬࡫࠲࠯ࡧࡹࡥࡱࡻࡡࡵࡧࠫࠦ࠭࠯ࠠ࠾ࡀࠣࡿࢂࠨࠬࠡ࡞ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥ࡫ࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡄࡦࡶࡤ࡭ࡱࡹࠢࡾ࡞ࠪ࠭࠮࠯࡛ࠣࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠦࡢ࠯ࠠࠬࠢࠥ࠰ࡡࡢ࡮ࠣࠫ࡟ࡲࠥࠦࠠࠡࡿࡦࡥࡹࡩࡨࠩࡧࡻ࠭ࢀࡢ࡮ࠡࠢࠣࠤࢂࡢ࡮ࠡࠢࢀࡠࡳࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠪࢼ")
bstack11llll1l_opy_ = bstack1ll_opy_ (u"ࠫࡡࡴ࠯ࠫࠢࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࠦࠪ࠰࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠷࡝࡝ࡰࡦࡳࡳࡹࡴࠡࡲࡢ࡭ࡳࡪࡥࡹࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠷ࡣ࡜࡯ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯ࡵ࡯࡭ࡨ࡫ࠨ࠱࠮ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸࠯࡜࡯ࡥࡲࡲࡸࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯ࠥࡃࠠࡳࡧࡴࡹ࡮ࡸࡥࠩࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨࠩ࠼࡞ࡱ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫࠯ࡥ࡫ࡶࡴࡳࡩࡶ࡯࠱ࡰࡦࡻ࡮ࡤࡪࠣࡁࠥࡧࡳࡺࡰࡦࠤ࠭ࡲࡡࡶࡰࡦ࡬ࡔࡶࡴࡪࡱࡱࡷ࠮ࠦ࠽࠿ࠢࡾࡠࡳࡲࡥࡵࠢࡦࡥࡵࡹ࠻࡝ࡰࡷࡶࡾࠦࡻ࡝ࡰࡦࡥࡵࡹࠠ࠾ࠢࡍࡗࡔࡔ࠮ࡱࡣࡵࡷࡪ࠮ࡢࡴࡶࡤࡧࡰࡥࡣࡢࡲࡶ࠭ࡡࡴࠠࠡࡿࠣࡧࡦࡺࡣࡩࠪࡨࡼ࠮ࠦࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࡷ࡫ࡴࡶࡴࡱࠤࡦࡽࡡࡪࡶࠣ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫࠯ࡥ࡫ࡶࡴࡳࡩࡶ࡯࠱ࡧࡴࡴ࡮ࡦࡥࡷࠬࢀࡢ࡮ࠡࠢࠣࠤࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴ࠻ࠢࡣࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠩࢁࡥ࡯ࡥࡲࡨࡪ࡛ࡒࡊࡅࡲࡱࡵࡵ࡮ࡦࡰࡷࠬࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡩࡡࡱࡵࠬ࠭ࢂࡦࠬ࡝ࡰࠣࠤࠥࠦ࠮࠯࠰࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴ࡞ࡱࠤࠥࢃࠩ࡝ࡰࢀࡠࡳ࠵ࠪࠡ࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࠥ࠰࠯࡝ࡰࠪࢽ")
from ._version import __version__
bstack1ll1111l11_opy_ = None
CONFIG = {}
bstack1llll1l1_opy_ = {}
bstack11lll11ll1_opy_ = {}
bstack1l1111l11l_opy_ = None
bstack1l1lll11_opy_ = None
bstack1lll1lllll_opy_ = None
bstack1l1111ll_opy_ = -1
bstack1ll1111ll1_opy_ = 0
bstack11lll1lll1_opy_ = bstack11l1l11l11_opy_
bstack11l11l1lll_opy_ = 1
bstack11l11llll1_opy_ = False
bstack1l1lll1111_opy_ = False
bstack11ll1l1lll_opy_ = bstack1ll_opy_ (u"ࠬ࠭ࢾ")
bstack1lll11llll_opy_ = bstack1ll_opy_ (u"࠭ࠧࢿ")
bstack1l11lll1_opy_ = False
bstack1lllll11_opy_ = True
bstack1l111lll1l_opy_ = bstack1ll_opy_ (u"ࠧࠨࣀ")
bstack1llll1lll_opy_ = []
bstack11llll1l1_opy_ = bstack1ll_opy_ (u"ࠨࠩࣁ")
bstack1l111lll11_opy_ = False
bstack1111111l1_opy_ = None
bstack1l111lll1_opy_ = None
bstack1l11l1l1l1_opy_ = None
bstack1l111ll11_opy_ = -1
bstack1l11111l_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠩࢁࠫࣂ")), bstack1ll_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪࣃ"), bstack1ll_opy_ (u"ࠫ࠳ࡸ࡯ࡣࡱࡷ࠱ࡷ࡫ࡰࡰࡴࡷ࠱࡭࡫࡬ࡱࡧࡵ࠲࡯ࡹ࡯࡯ࠩࣄ"))
bstack1l11l1l111_opy_ = 0
bstack1l111l1l1_opy_ = 0
bstack1l11ll11_opy_ = []
bstack1111l11l_opy_ = []
bstack1l1l11ll1l_opy_ = []
bstack11l11l11l_opy_ = []
bstack11ll11ll1_opy_ = bstack1ll_opy_ (u"ࠬ࠭ࣅ")
bstack1l11ll1l11_opy_ = bstack1ll_opy_ (u"࠭ࠧࣆ")
bstack11l111l1l1_opy_ = False
bstack1llll1ll1l_opy_ = False
bstack1l1llll111_opy_ = {}
bstack1ll111ll11_opy_ = None
bstack1lll11111l_opy_ = None
bstack1lllllll11_opy_ = None
bstack1l1ll11lll_opy_ = None
bstack1lllll111_opy_ = None
bstack1lll1l11l_opy_ = None
bstack111l11l1_opy_ = None
bstack1l1111llll_opy_ = None
bstack11l1l111l_opy_ = None
bstack111l1lll1_opy_ = None
bstack1l111l11l_opy_ = None
bstack1l11l1ll11_opy_ = None
bstack11l11ll11l_opy_ = None
bstack11llll11l1_opy_ = None
bstack111lllll_opy_ = None
bstack11l1111l1_opy_ = None
bstack1l1l11l11_opy_ = None
bstack1lll1lll1_opy_ = None
bstack1lll1l1l_opy_ = None
bstack11l11ll1ll_opy_ = None
bstack1l1ll111_opy_ = None
bstack1l111l11ll_opy_ = None
bstack1111llll_opy_ = None
thread_local = threading.local()
bstack11lllllll_opy_ = False
bstack1llllll1l1_opy_ = bstack1ll_opy_ (u"ࠢࠣࣇ")
logger = bstack111ll11ll_opy_.get_logger(__name__, bstack11lll1lll1_opy_)
bstack1lll1111ll_opy_ = Config.bstack11ll1l1l_opy_()
percy = bstack1l11l1llll_opy_()
bstack1l1ll1l1ll_opy_ = bstack1llll1l111_opy_()
bstack1llllllll_opy_ = bstack11l11111l_opy_()
def bstack1lll1l111l_opy_():
  global CONFIG
  global bstack11l111l1l1_opy_
  global bstack1lll1111ll_opy_
  testContextOptions = bstack1111l111_opy_(CONFIG)
  if bstack11ll11l1l1_opy_(CONFIG):
    if (bstack1ll_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪࣈ") in testContextOptions and str(testContextOptions[bstack1ll_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫࣉ")]).lower() == bstack1ll_opy_ (u"ࠪࡸࡷࡻࡥࠨ࣊")):
      bstack11l111l1l1_opy_ = True
    bstack1lll1111ll_opy_.bstack11l1l11l1_opy_(testContextOptions.get(bstack1ll_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ࣋"), False))
  else:
    bstack11l111l1l1_opy_ = True
    bstack1lll1111ll_opy_.bstack11l1l11l1_opy_(True)
def bstack11l1l11ll_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack11l111ll1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1111l1l_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack1ll_opy_ (u"ࠧ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡩ࡯࡯ࡨ࡬࡫࡫࡯࡬ࡦࠤ࣌") == args[i].lower() or bstack1ll_opy_ (u"ࠨ࠭࠮ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡱࡪ࡮࡭ࠢ࣍") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack1l111lll1l_opy_
      bstack1l111lll1l_opy_ += bstack1ll_opy_ (u"ࠧ࠮࠯ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡄࡱࡱࡪ࡮࡭ࡆࡪ࡮ࡨࠤࠬ࣎") + path
      return path
  return None
bstack1ll1ll1ll1_opy_ = re.compile(bstack1ll_opy_ (u"ࡳࠤ࠱࠮ࡄࡢࠤࡼࠪ࠱࠮ࡄ࠯ࡽ࠯ࠬࡂ࣏ࠦ"))
def bstack11l1l1l1_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1ll1ll1ll1_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack1ll_opy_ (u"ࠤࠧࡿ࣐ࠧ") + group + bstack1ll_opy_ (u"ࠥࢁ࣑ࠧ"), os.environ.get(group))
  return value
def bstack11llllllll_opy_():
  global bstack1111llll_opy_
  if bstack1111llll_opy_ is None:
        bstack1111llll_opy_ = bstack1ll1111l1l_opy_()
  bstack1l1l11l1_opy_ = bstack1111llll_opy_
  if bstack1l1l11l1_opy_ and os.path.exists(os.path.abspath(bstack1l1l11l1_opy_)):
    fileName = bstack1l1l11l1_opy_
  if bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡕࡎࡇࡋࡊࡣࡋࡏࡌࡆ࣓ࠩ")])) and not bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡒࡦࡳࡥࠨࣔ") in locals():
    fileName = os.environ[bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫࣕ")]
  if bstack1ll_opy_ (u"ࠨࡨ࡬ࡰࡪࡔࡡ࡮ࡧࠪࣖ") in locals():
    bstack1ll1111_opy_ = os.path.abspath(fileName)
  else:
    bstack1ll1111_opy_ = bstack1ll_opy_ (u"ࠩࠪࣗ")
  bstack1lll111lll_opy_ = os.getcwd()
  bstack11ll1l1l11_opy_ = bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱ࠭ࣘ")
  bstack1ll111ll1l_opy_ = bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡦࡳ࡬ࠨࣙ")
  while (not os.path.exists(bstack1ll1111_opy_)) and bstack1lll111lll_opy_ != bstack1ll_opy_ (u"ࠧࠨࣚ"):
    bstack1ll1111_opy_ = os.path.join(bstack1lll111lll_opy_, bstack11ll1l1l11_opy_)
    if not os.path.exists(bstack1ll1111_opy_):
      bstack1ll1111_opy_ = os.path.join(bstack1lll111lll_opy_, bstack1ll111ll1l_opy_)
    if bstack1lll111lll_opy_ != os.path.dirname(bstack1lll111lll_opy_):
      bstack1lll111lll_opy_ = os.path.dirname(bstack1lll111lll_opy_)
    else:
      bstack1lll111lll_opy_ = bstack1ll_opy_ (u"ࠨࠢࣛ")
  bstack1111llll_opy_ = bstack1ll1111_opy_ if os.path.exists(bstack1ll1111_opy_) else None
  return bstack1111llll_opy_
def bstack1l11ll1l1_opy_():
  bstack1ll1111_opy_ = bstack11llllllll_opy_()
  if not os.path.exists(bstack1ll1111_opy_):
    bstack1l11l11l1l_opy_(
      bstack1l1l1ll1l1_opy_.format(os.getcwd()))
  try:
    with open(bstack1ll1111_opy_, bstack1ll_opy_ (u"ࠧࡳࠩࣜ")) as stream:
      yaml.add_implicit_resolver(bstack1ll_opy_ (u"ࠣࠣࡳࡥࡹ࡮ࡥࡹࠤࣝ"), bstack1ll1ll1ll1_opy_)
      yaml.add_constructor(bstack1ll_opy_ (u"ࠤࠤࡴࡦࡺࡨࡦࡺࠥࣞ"), bstack11l1l1l1_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      return config
  except:
    with open(bstack1ll1111_opy_, bstack1ll_opy_ (u"ࠪࡶࠬࣟ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1l11l11l1l_opy_(bstack1ll1l11l1l_opy_.format(str(exc)))
def bstack1l1l1111l_opy_(config):
  bstack1l1lllll_opy_ = bstack11l1l1l11_opy_(config)
  for option in list(bstack1l1lllll_opy_):
    if option.lower() in bstack1lll1lll11_opy_ and option != bstack1lll1lll11_opy_[option.lower()]:
      bstack1l1lllll_opy_[bstack1lll1lll11_opy_[option.lower()]] = bstack1l1lllll_opy_[option]
      del bstack1l1lllll_opy_[option]
  return config
def bstack11l1l1ll11_opy_():
  global bstack11lll11ll1_opy_
  for key, bstack1ll1lll11l_opy_ in bstack1l1llll11_opy_.items():
    if isinstance(bstack1ll1lll11l_opy_, list):
      for var in bstack1ll1lll11l_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack11lll11ll1_opy_[key] = os.environ[var]
          break
    elif bstack1ll1lll11l_opy_ in os.environ and os.environ[bstack1ll1lll11l_opy_] and str(os.environ[bstack1ll1lll11l_opy_]).strip():
      bstack11lll11ll1_opy_[key] = os.environ[bstack1ll1lll11l_opy_]
  if bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭࣠") in os.environ:
    bstack11lll11ll1_opy_[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ࣡")] = {}
    bstack11lll11ll1_opy_[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ࣢")][bstack1ll_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࣣࠩ")] = os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪࣤ")]
def bstack1ll111ll_opy_():
  global bstack1llll1l1_opy_
  global bstack1l111lll1l_opy_
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) and bstack1ll_opy_ (u"ࠩ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࣥ").lower() == val.lower():
      bstack1llll1l1_opy_[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࣦࠧ")] = {}
      bstack1llll1l1_opy_[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨࣧ")][bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣨ")] = sys.argv[idx + 1]
      del sys.argv[idx:idx + 2]
      break
  for key, bstack11ll11lll1_opy_ in bstack1l1ll1l111_opy_.items():
    if isinstance(bstack11ll11lll1_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack11ll11lll1_opy_:
          if idx < len(sys.argv) and bstack1ll_opy_ (u"࠭࠭࠮ࣩࠩ") + var.lower() == val.lower() and not key in bstack1llll1l1_opy_:
            bstack1llll1l1_opy_[key] = sys.argv[idx + 1]
            bstack1l111lll1l_opy_ += bstack1ll_opy_ (u"ࠧࠡ࠯࠰ࠫ࣪") + var + bstack1ll_opy_ (u"ࠨࠢࠪ࣫") + sys.argv[idx + 1]
            del sys.argv[idx:idx + 2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx < len(sys.argv) and bstack1ll_opy_ (u"ࠩ࠰࠱ࠬ࣬") + bstack11ll11lll1_opy_.lower() == val.lower() and not key in bstack1llll1l1_opy_:
          bstack1llll1l1_opy_[key] = sys.argv[idx + 1]
          bstack1l111lll1l_opy_ += bstack1ll_opy_ (u"ࠪࠤ࠲࠳࣭ࠧ") + bstack11ll11lll1_opy_ + bstack1ll_opy_ (u"࣮ࠫࠥ࠭") + sys.argv[idx + 1]
          del sys.argv[idx:idx + 2]
def bstack111l1111_opy_(config):
  bstack11l1llll1_opy_ = config.keys()
  for bstack1l1l1l1l1l_opy_, bstack111l1ll11_opy_ in bstack1ll11llll1_opy_.items():
    if bstack111l1ll11_opy_ in bstack11l1llll1_opy_:
      config[bstack1l1l1l1l1l_opy_] = config[bstack111l1ll11_opy_]
      del config[bstack111l1ll11_opy_]
  for bstack1l1l1l1l1l_opy_, bstack111l1ll11_opy_ in bstack1lll1ll1l1_opy_.items():
    if isinstance(bstack111l1ll11_opy_, list):
      for bstack1lll11l11l_opy_ in bstack111l1ll11_opy_:
        if bstack1lll11l11l_opy_ in bstack11l1llll1_opy_:
          config[bstack1l1l1l1l1l_opy_] = config[bstack1lll11l11l_opy_]
          del config[bstack1lll11l11l_opy_]
          break
    elif bstack111l1ll11_opy_ in bstack11l1llll1_opy_:
      config[bstack1l1l1l1l1l_opy_] = config[bstack111l1ll11_opy_]
      del config[bstack111l1ll11_opy_]
  for bstack1lll11l11l_opy_ in list(config):
    for bstack1l11lll1ll_opy_ in bstack111ll111_opy_:
      if bstack1lll11l11l_opy_.lower() == bstack1l11lll1ll_opy_.lower() and bstack1lll11l11l_opy_ != bstack1l11lll1ll_opy_:
        config[bstack1l11lll1ll_opy_] = config[bstack1lll11l11l_opy_]
        del config[bstack1lll11l11l_opy_]
  bstack111111lll_opy_ = [{}]
  if not config.get(bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ࣯")):
    config[bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࣰࠩ")] = [{}]
  bstack111111lll_opy_ = config[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࣱࠪ")]
  for platform in bstack111111lll_opy_:
    for bstack1lll11l11l_opy_ in list(platform):
      for bstack1l11lll1ll_opy_ in bstack111ll111_opy_:
        if bstack1lll11l11l_opy_.lower() == bstack1l11lll1ll_opy_.lower() and bstack1lll11l11l_opy_ != bstack1l11lll1ll_opy_:
          platform[bstack1l11lll1ll_opy_] = platform[bstack1lll11l11l_opy_]
          del platform[bstack1lll11l11l_opy_]
  for bstack1l1l1l1l1l_opy_, bstack111l1ll11_opy_ in bstack1lll1ll1l1_opy_.items():
    for platform in bstack111111lll_opy_:
      if isinstance(bstack111l1ll11_opy_, list):
        for bstack1lll11l11l_opy_ in bstack111l1ll11_opy_:
          if bstack1lll11l11l_opy_ in platform:
            platform[bstack1l1l1l1l1l_opy_] = platform[bstack1lll11l11l_opy_]
            del platform[bstack1lll11l11l_opy_]
            break
      elif bstack111l1ll11_opy_ in platform:
        platform[bstack1l1l1l1l1l_opy_] = platform[bstack111l1ll11_opy_]
        del platform[bstack111l1ll11_opy_]
  for bstack11l11l111l_opy_ in bstack11l1l111ll_opy_:
    if bstack11l11l111l_opy_ in config:
      if not bstack11l1l111ll_opy_[bstack11l11l111l_opy_] in config:
        config[bstack11l1l111ll_opy_[bstack11l11l111l_opy_]] = {}
      config[bstack11l1l111ll_opy_[bstack11l11l111l_opy_]].update(config[bstack11l11l111l_opy_])
      del config[bstack11l11l111l_opy_]
  for platform in bstack111111lll_opy_:
    for bstack11l11l111l_opy_ in bstack11l1l111ll_opy_:
      if bstack11l11l111l_opy_ in list(platform):
        if not bstack11l1l111ll_opy_[bstack11l11l111l_opy_] in platform:
          platform[bstack11l1l111ll_opy_[bstack11l11l111l_opy_]] = {}
        platform[bstack11l1l111ll_opy_[bstack11l11l111l_opy_]].update(platform[bstack11l11l111l_opy_])
        del platform[bstack11l11l111l_opy_]
  config = bstack1l1l1111l_opy_(config)
  return config
def bstack1l111ll1_opy_(config):
  global bstack1lll11llll_opy_
  bstack1llll1ll_opy_ = False
  if bstack1ll_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࣲࠬ") in config and str(config[bstack1ll_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ࣳ")]).lower() != bstack1ll_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩࣴ"):
    if bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨࣵ") not in config or str(config[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࣶࠩ")]).lower() == bstack1ll_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣷ"):
      config[bstack1ll_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ࣸ")] = False
    else:
      bstack11l1ll11_opy_ = bstack111l11111_opy_()
      if bstack1ll_opy_ (u"ࠨ࡫ࡶࡘࡷ࡯ࡡ࡭ࡉࡵ࡭ࡩࣹ࠭") in bstack11l1ll11_opy_:
        if not bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸࣺ࠭") in config:
          config[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧࣻ")] = {}
        config[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨࣼ")][bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣽ")] = bstack1ll_opy_ (u"࠭ࡡࡵࡵ࠰ࡶࡪࡶࡥࡢࡶࡨࡶࠬࣾ")
        bstack1llll1ll_opy_ = True
        bstack1lll11llll_opy_ = config[bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࣿ")].get(bstack1ll_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪऀ"))
  if bstack11ll11l1l1_opy_(config) and bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ँ") in config and str(config[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧं")]).lower() != bstack1ll_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪः") and not bstack1llll1ll_opy_:
    if not bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
      config[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
    if not config[bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")].get(bstack1ll_opy_ (u"ࠨࡵ࡮࡭ࡵࡈࡩ࡯ࡣࡵࡽࡎࡴࡩࡵ࡫ࡤࡰ࡮ࡹࡡࡵ࡫ࡲࡲࠬइ")) and not bstack1ll_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫई") in config[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")]:
      bstack11ll111lll_opy_ = datetime.datetime.now()
      bstack111111l1_opy_ = bstack11ll111lll_opy_.strftime(bstack1ll_opy_ (u"ࠫࠪࡪ࡟ࠦࡤࡢࠩࡍࠫࡍࠨऊ"))
      hostname = socket.gethostname()
      bstack11lll1l11_opy_ = bstack1ll_opy_ (u"ࠬ࠭ऋ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1ll_opy_ (u"࠭ࡻࡾࡡࡾࢁࡤࢁࡽࠨऌ").format(bstack111111l1_opy_, hostname, bstack11lll1l11_opy_)
      config[bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫऍ")][bstack1ll_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪऎ")] = identifier
    bstack1lll11llll_opy_ = config[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")].get(bstack1ll_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬऐ"))
  return config
def bstack1ll1ll1lll_opy_():
  bstack1l11l111l_opy_ =  bstack11l1lll1_opy_()[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠪऑ")]
  return bstack1l11l111l_opy_ if bstack1l11l111l_opy_ else -1
def bstack11l11l11ll_opy_(bstack1l11l111l_opy_):
  global CONFIG
  if not bstack1ll_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧऒ") in CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨओ")]:
    return
  CONFIG[bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऔ")] = CONFIG[bstack1ll_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪक")].replace(
    bstack1ll_opy_ (u"ࠩࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫख"),
    str(bstack1l11l111l_opy_)
  )
def bstack1l1lllll1_opy_():
  global CONFIG
  if not bstack1ll_opy_ (u"ࠪࠨࢀࡊࡁࡕࡇࡢࡘࡎࡓࡅࡾࠩग") in CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")]:
    return
  bstack11ll111lll_opy_ = datetime.datetime.now()
  bstack111111l1_opy_ = bstack11ll111lll_opy_.strftime(bstack1ll_opy_ (u"ࠬࠫࡤ࠮ࠧࡥ࠱ࠪࡎ࠺ࠦࡏࠪङ"))
  CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच")] = CONFIG[bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩछ")].replace(
    bstack1ll_opy_ (u"ࠨࠦࡾࡈࡆ࡚ࡅࡠࡖࡌࡑࡊࢃࠧज"),
    bstack111111l1_opy_
  )
def bstack11lllll1ll_opy_():
  global CONFIG
  if bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ") in CONFIG and not bool(CONFIG[bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")]):
    del CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")]
    return
  if not bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧठ") in CONFIG:
    CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨड")] = bstack1ll_opy_ (u"ࠧࠤࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪढ")
  if bstack1ll_opy_ (u"ࠨࠦࡾࡈࡆ࡚ࡅࡠࡖࡌࡑࡊࢃࠧण") in CONFIG[bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")]:
    bstack1l1lllll1_opy_()
    os.environ[bstack1ll_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧथ")] = CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭द")]
  if not bstack1ll_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧध") in CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]:
    return
  bstack1l11l111l_opy_ = bstack1ll_opy_ (u"ࠧࠨऩ")
  bstack1l11ll111l_opy_ = bstack1ll1ll1lll_opy_()
  if bstack1l11ll111l_opy_ != -1:
    bstack1l11l111l_opy_ = bstack1ll_opy_ (u"ࠨࡅࡌࠤࠬप") + str(bstack1l11ll111l_opy_)
  if bstack1l11l111l_opy_ == bstack1ll_opy_ (u"ࠩࠪफ"):
    bstack1l11l11l11_opy_ = bstack11l1lll1ll_opy_(CONFIG[bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ब")])
    if bstack1l11l11l11_opy_ != -1:
      bstack1l11l111l_opy_ = str(bstack1l11l11l11_opy_)
  if bstack1l11l111l_opy_:
    bstack11l11l11ll_opy_(bstack1l11l111l_opy_)
    os.environ[bstack1ll_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨभ")] = CONFIG[bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]
def bstack11l11ll1l1_opy_(bstack1llll1l1l1_opy_, bstack11l1lll111_opy_, path):
  bstack1l1ll11ll1_opy_ = {
    bstack1ll_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪय"): bstack11l1lll111_opy_
  }
  if os.path.exists(path):
    bstack111lllll1_opy_ = json.load(open(path, bstack1ll_opy_ (u"ࠧࡳࡤࠪर")))
  else:
    bstack111lllll1_opy_ = {}
  bstack111lllll1_opy_[bstack1llll1l1l1_opy_] = bstack1l1ll11ll1_opy_
  with open(path, bstack1ll_opy_ (u"ࠣࡹ࠮ࠦऱ")) as outfile:
    json.dump(bstack111lllll1_opy_, outfile)
def bstack11l1lll1ll_opy_(bstack1llll1l1l1_opy_):
  bstack1llll1l1l1_opy_ = str(bstack1llll1l1l1_opy_)
  bstack1llll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠩࢁࠫल")), bstack1ll_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪळ"))
  try:
    if not os.path.exists(bstack1llll1ll1_opy_):
      os.makedirs(bstack1llll1ll1_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠫࢃ࠭ऴ")), bstack1ll_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬव"), bstack1ll_opy_ (u"࠭࠮ࡣࡷ࡬ࡰࡩ࠳࡮ࡢ࡯ࡨ࠱ࡨࡧࡣࡩࡧ࠱࡮ࡸࡵ࡮ࠨश"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1ll_opy_ (u"ࠧࡸࠩष")):
        pass
      with open(file_path, bstack1ll_opy_ (u"ࠣࡹ࠮ࠦस")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1ll_opy_ (u"ࠩࡵࠫह")) as bstack11l11l1111_opy_:
      bstack111ll1lll_opy_ = json.load(bstack11l11l1111_opy_)
    if bstack1llll1l1l1_opy_ in bstack111ll1lll_opy_:
      bstack1l11lllll1_opy_ = bstack111ll1lll_opy_[bstack1llll1l1l1_opy_][bstack1ll_opy_ (u"ࠪ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऺ")]
      bstack11lll11l1_opy_ = int(bstack1l11lllll1_opy_) + 1
      bstack11l11ll1l1_opy_(bstack1llll1l1l1_opy_, bstack11lll11l1_opy_, file_path)
      return bstack11lll11l1_opy_
    else:
      bstack11l11ll1l1_opy_(bstack1llll1l1l1_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack11llll11ll_opy_.format(str(e)))
    return -1
def bstack11lll1ll_opy_(config):
  if not config[bstack1ll_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ऻ")] or not config[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ़")]:
    return True
  else:
    return False
def bstack11ll1llll1_opy_(config, index=0):
  global bstack1l11lll1_opy_
  bstack1ll1l111l_opy_ = {}
  caps = bstack1l1l11llll_opy_ + bstack111llll11_opy_
  if config.get(bstack1ll_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪऽ"), False):
    bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫा")] = True
    bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬि")] = config.get(bstack1ll_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ी"), {})
  if bstack1l11lll1_opy_:
    caps += bstack1l1l111l1_opy_
  for key in config:
    if key in caps + [bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ु")]:
      continue
    bstack1ll1l111l_opy_[key] = config[key]
  if bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧू") in config:
    for bstack1ll1ll1111_opy_ in config[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨृ")][index]:
      if bstack1ll1ll1111_opy_ in caps:
        continue
      bstack1ll1l111l_opy_[bstack1ll1ll1111_opy_] = config[bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॄ")][index][bstack1ll1ll1111_opy_]
  bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠧࡩࡱࡶࡸࡓࡧ࡭ࡦࠩॅ")] = socket.gethostname()
  if bstack1ll_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩॆ") in bstack1ll1l111l_opy_:
    del (bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪे")])
  return bstack1ll1l111l_opy_
def bstack11lll1ll1_opy_(config):
  global bstack1l11lll1_opy_
  bstack1lll11lll_opy_ = {}
  caps = bstack111llll11_opy_
  if bstack1l11lll1_opy_:
    caps += bstack1l1l111l1_opy_
  for key in caps:
    if key in config:
      bstack1lll11lll_opy_[key] = config[key]
  return bstack1lll11lll_opy_
def bstack111l1l1l1_opy_(bstack1ll1l111l_opy_, bstack1lll11lll_opy_):
  bstack111l111l1_opy_ = {}
  for key in bstack1ll1l111l_opy_.keys():
    if key in bstack1ll11llll1_opy_:
      bstack111l111l1_opy_[bstack1ll11llll1_opy_[key]] = bstack1ll1l111l_opy_[key]
    else:
      bstack111l111l1_opy_[key] = bstack1ll1l111l_opy_[key]
  for key in bstack1lll11lll_opy_:
    if key in bstack1ll11llll1_opy_:
      bstack111l111l1_opy_[bstack1ll11llll1_opy_[key]] = bstack1lll11lll_opy_[key]
    else:
      bstack111l111l1_opy_[key] = bstack1lll11lll_opy_[key]
  return bstack111l111l1_opy_
def bstack1lll1llll_opy_(config, index=0):
  global bstack1l11lll1_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack1l1lllllll_opy_ = bstack11lllll1_opy_(bstack1l1lll111l_opy_, config, logger)
  bstack1lll11lll_opy_ = bstack11lll1ll1_opy_(config)
  bstack1l1llll1_opy_ = bstack111llll11_opy_
  bstack1l1llll1_opy_ += bstack1l111l1ll1_opy_
  bstack1lll11lll_opy_ = update(bstack1lll11lll_opy_, bstack1l1lllllll_opy_)
  if bstack1l11lll1_opy_:
    bstack1l1llll1_opy_ += bstack1l1l111l1_opy_
  if bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ै") in config:
    if bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॉ") in config[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨॊ")][index]:
      caps[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫो")] = config[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ")][index][bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ्࠭")]
    if bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪॎ") in config[bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॏ")][index]:
      caps[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬॐ")] = str(config[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ॑")][index][bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴ॒ࠧ")])
    bstack1l111111ll_opy_ = bstack11lllll1_opy_(bstack1l1lll111l_opy_, config[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ॓")][index], logger)
    bstack1l1llll1_opy_ += list(bstack1l111111ll_opy_.keys())
    for bstack1l1ll11ll_opy_ in bstack1l1llll1_opy_:
      if bstack1l1ll11ll_opy_ in config[bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
        if bstack1l1ll11ll_opy_ == bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫॕ"):
          try:
            bstack1l111111ll_opy_[bstack1l1ll11ll_opy_] = str(config[bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack1l1ll11ll_opy_] * 1.0)
          except:
            bstack1l111111ll_opy_[bstack1l1ll11ll_opy_] = str(config[bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧॗ")][index][bstack1l1ll11ll_opy_])
        else:
          bstack1l111111ll_opy_[bstack1l1ll11ll_opy_] = config[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨक़")][index][bstack1l1ll11ll_opy_]
        del (config[bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index][bstack1l1ll11ll_opy_])
    bstack1lll11lll_opy_ = update(bstack1lll11lll_opy_, bstack1l111111ll_opy_)
  bstack1ll1l111l_opy_ = bstack11ll1llll1_opy_(config, index)
  for bstack1lll11l11l_opy_ in bstack111llll11_opy_ + list(bstack1l1lllllll_opy_.keys()):
    if bstack1lll11l11l_opy_ in bstack1ll1l111l_opy_:
      bstack1lll11lll_opy_[bstack1lll11l11l_opy_] = bstack1ll1l111l_opy_[bstack1lll11l11l_opy_]
      del (bstack1ll1l111l_opy_[bstack1lll11l11l_opy_])
  if bstack11111l1l_opy_(config):
    bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧग़")] = True
    caps.update(bstack1lll11lll_opy_)
    caps[bstack1ll_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩज़")] = bstack1ll1l111l_opy_
  else:
    bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩड़")] = False
    caps.update(bstack111l1l1l1_opy_(bstack1ll1l111l_opy_, bstack1lll11lll_opy_))
    if bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨढ़") in caps:
      caps[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬफ़")] = caps[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪय़")]
      del (caps[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫॠ")])
    if bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨॡ") in caps:
      caps[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪॢ")] = caps[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪॣ")]
      del (caps[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ।")])
  return caps
def bstack11l11ll11_opy_():
  global bstack11llll1l1_opy_
  global CONFIG
  if bstack11l111ll1_opy_() <= version.parse(bstack1ll_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫ॥")):
    if bstack11llll1l1_opy_ != bstack1ll_opy_ (u"ࠬ࠭०"):
      return bstack1ll_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ१") + bstack11llll1l1_opy_ + bstack1ll_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦ२")
    return bstack111l1l111_opy_
  if bstack11llll1l1_opy_ != bstack1ll_opy_ (u"ࠨࠩ३"):
    return bstack1ll_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ४") + bstack11llll1l1_opy_ + bstack1ll_opy_ (u"ࠥ࠳ࡼࡪ࠯ࡩࡷࡥࠦ५")
  return bstack1l111l11_opy_
def bstack1l11ll1111_opy_(options):
  return hasattr(options, bstack1ll_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬ६"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack11llll1lll_opy_(options, bstack1l11l11l1_opy_):
  for bstack111llll1l_opy_ in bstack1l11l11l1_opy_:
    if bstack111llll1l_opy_ in [bstack1ll_opy_ (u"ࠬࡧࡲࡨࡵࠪ७"), bstack1ll_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ८")]:
      continue
    if bstack111llll1l_opy_ in options._experimental_options:
      options._experimental_options[bstack111llll1l_opy_] = update(options._experimental_options[bstack111llll1l_opy_],
                                                         bstack1l11l11l1_opy_[bstack111llll1l_opy_])
    else:
      options.add_experimental_option(bstack111llll1l_opy_, bstack1l11l11l1_opy_[bstack111llll1l_opy_])
  if bstack1ll_opy_ (u"ࠧࡢࡴࡪࡷࠬ९") in bstack1l11l11l1_opy_:
    for arg in bstack1l11l11l1_opy_[bstack1ll_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭॰")]:
      options.add_argument(arg)
    del (bstack1l11l11l1_opy_[bstack1ll_opy_ (u"ࠩࡤࡶ࡬ࡹࠧॱ")])
  if bstack1ll_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧॲ") in bstack1l11l11l1_opy_:
    for ext in bstack1l11l11l1_opy_[bstack1ll_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨॳ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack1l11l11l1_opy_[bstack1ll_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩॴ")])
def bstack1111ll1l1_opy_(options, bstack11l1ll11l_opy_):
  if bstack1ll_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬॵ") in bstack11l1ll11l_opy_:
    for bstack1ll1l1l1ll_opy_ in bstack11l1ll11l_opy_[bstack1ll_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ॶ")]:
      if bstack1ll1l1l1ll_opy_ in options._preferences:
        options._preferences[bstack1ll1l1l1ll_opy_] = update(options._preferences[bstack1ll1l1l1ll_opy_], bstack11l1ll11l_opy_[bstack1ll_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧॷ")][bstack1ll1l1l1ll_opy_])
      else:
        options.set_preference(bstack1ll1l1l1ll_opy_, bstack11l1ll11l_opy_[bstack1ll_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॸ")][bstack1ll1l1l1ll_opy_])
  if bstack1ll_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack11l1ll11l_opy_:
    for arg in bstack11l1ll11l_opy_[bstack1ll_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
def bstack11111l1ll_opy_(options, bstack1ll1ll1l1_opy_):
  if bstack1ll_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ॻ") in bstack1ll1ll1l1_opy_:
    options.use_webview(bool(bstack1ll1ll1l1_opy_[bstack1ll_opy_ (u"࠭ࡷࡦࡤࡹ࡭ࡪࡽࠧॼ")]))
  bstack11llll1lll_opy_(options, bstack1ll1ll1l1_opy_)
def bstack11l11l1l1_opy_(options, bstack11ll1l1l1_opy_):
  for bstack1l1ll11l_opy_ in bstack11ll1l1l1_opy_:
    if bstack1l1ll11l_opy_ in [bstack1ll_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫॽ"), bstack1ll_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॾ")]:
      continue
    options.set_capability(bstack1l1ll11l_opy_, bstack11ll1l1l1_opy_[bstack1l1ll11l_opy_])
  if bstack1ll_opy_ (u"ࠩࡤࡶ࡬ࡹࠧॿ") in bstack11ll1l1l1_opy_:
    for arg in bstack11ll1l1l1_opy_[bstack1ll_opy_ (u"ࠪࡥࡷ࡭ࡳࠨঀ")]:
      options.add_argument(arg)
  if bstack1ll_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨঁ") in bstack11ll1l1l1_opy_:
    options.bstack1l111l111l_opy_(bool(bstack11ll1l1l1_opy_[bstack1ll_opy_ (u"ࠬࡺࡥࡤࡪࡱࡳࡱࡵࡧࡺࡒࡵࡩࡻ࡯ࡥࡸࠩং")]))
def bstack1l1llll1l_opy_(options, bstack1l1l11ll1_opy_):
  for bstack11lll1l1ll_opy_ in bstack1l1l11ll1_opy_:
    if bstack11lll1l1ll_opy_ in [bstack1ll_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪঃ"), bstack1ll_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      continue
    options._options[bstack11lll1l1ll_opy_] = bstack1l1l11ll1_opy_[bstack11lll1l1ll_opy_]
  if bstack1ll_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬঅ") in bstack1l1l11ll1_opy_:
    for bstack1lll111ll1_opy_ in bstack1l1l11ll1_opy_[bstack1ll_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭আ")]:
      options.bstack1l1l11l1l_opy_(
        bstack1lll111ll1_opy_, bstack1l1l11ll1_opy_[bstack1ll_opy_ (u"ࠪࡥࡩࡪࡩࡵ࡫ࡲࡲࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧই")][bstack1lll111ll1_opy_])
  if bstack1ll_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ") in bstack1l1l11ll1_opy_:
    for arg in bstack1l1l11ll1_opy_[bstack1ll_opy_ (u"ࠬࡧࡲࡨࡵࠪউ")]:
      options.add_argument(arg)
def bstack1ll1ll111_opy_(options, caps):
  if not hasattr(options, bstack1ll_opy_ (u"࠭ࡋࡆ࡛ࠪঊ")):
    return
  if options.KEY == bstack1ll_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬঋ"):
    options = bstack1l11llll1l_opy_.bstack1l1ll1111_opy_(bstack1ll1llll_opy_=options, config=CONFIG)
  if options.KEY == bstack1ll_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ঌ") and options.KEY in caps:
    bstack11llll1lll_opy_(options, caps[bstack1ll_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ঍")])
  elif options.KEY == bstack1ll_opy_ (u"ࠪࡱࡴࢀ࠺ࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨ঎") and options.KEY in caps:
    bstack1111ll1l1_opy_(options, caps[bstack1ll_opy_ (u"ࠫࡲࡵࡺ࠻ࡨ࡬ࡶࡪ࡬࡯ࡹࡑࡳࡸ࡮ࡵ࡮ࡴࠩএ")])
  elif options.KEY == bstack1ll_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ঐ") and options.KEY in caps:
    bstack11l11l1l1_opy_(options, caps[bstack1ll_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠴࡯ࡱࡶ࡬ࡳࡳࡹࠧ঑")])
  elif options.KEY == bstack1ll_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ঒") and options.KEY in caps:
    bstack11111l1ll_opy_(options, caps[bstack1ll_opy_ (u"ࠨ࡯ࡶ࠾ࡪࡪࡧࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩও")])
  elif options.KEY == bstack1ll_opy_ (u"ࠩࡶࡩ࠿࡯ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨঔ") and options.KEY in caps:
    bstack1l1llll1l_opy_(options, caps[bstack1ll_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩক")])
def bstack1l1l111ll_opy_(caps):
  global bstack1l11lll1_opy_
  if isinstance(os.environ.get(bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬখ")), str):
    bstack1l11lll1_opy_ = eval(os.getenv(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭গ")))
  if bstack1l11lll1_opy_:
    if bstack11l1l11ll_opy_() < version.parse(bstack1ll_opy_ (u"࠭࠲࠯࠵࠱࠴ࠬঘ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1ll_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧঙ")
    if bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭চ") in caps:
      browser = caps[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧছ")]
    elif bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫজ") in caps:
      browser = caps[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬঝ")]
    browser = str(browser).lower()
    if browser == bstack1ll_opy_ (u"ࠬ࡯ࡰࡩࡱࡱࡩࠬঞ") or browser == bstack1ll_opy_ (u"࠭ࡩࡱࡣࡧࠫট"):
      browser = bstack1ll_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࠧঠ")
    if browser == bstack1ll_opy_ (u"ࠨࡵࡤࡱࡸࡻ࡮ࡨࠩড"):
      browser = bstack1ll_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩঢ")
    if browser not in [bstack1ll_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪণ"), bstack1ll_opy_ (u"ࠫࡪࡪࡧࡦࠩত"), bstack1ll_opy_ (u"ࠬ࡯ࡥࠨথ"), bstack1ll_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠭দ"), bstack1ll_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࠨধ")]:
      return None
    try:
      package = bstack1ll_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࠱ࡻࡪࡨࡤࡳ࡫ࡹࡩࡷ࠴ࡻࡾ࠰ࡲࡴࡹ࡯࡯࡯ࡵࠪন").format(browser)
      name = bstack1ll_opy_ (u"ࠩࡒࡴࡹ࡯࡯࡯ࡵࠪ঩")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1l11ll1111_opy_(options):
        return None
      for bstack1lll11l11l_opy_ in caps.keys():
        options.set_capability(bstack1lll11l11l_opy_, caps[bstack1lll11l11l_opy_])
      bstack1ll1ll111_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1ll1l1l111_opy_(options, bstack1lll11ll1_opy_):
  if not bstack1l11ll1111_opy_(options):
    return
  for bstack1lll11l11l_opy_ in bstack1lll11ll1_opy_.keys():
    if bstack1lll11l11l_opy_ in bstack1l111l1ll1_opy_:
      continue
    if bstack1lll11l11l_opy_ in options._caps and type(options._caps[bstack1lll11l11l_opy_]) in [dict, list]:
      options._caps[bstack1lll11l11l_opy_] = update(options._caps[bstack1lll11l11l_opy_], bstack1lll11ll1_opy_[bstack1lll11l11l_opy_])
    else:
      options.set_capability(bstack1lll11l11l_opy_, bstack1lll11ll1_opy_[bstack1lll11l11l_opy_])
  bstack1ll1ll111_opy_(options, bstack1lll11ll1_opy_)
  if bstack1ll_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩপ") in options._caps:
    if options._caps[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩফ")] and options._caps[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪব")].lower() != bstack1ll_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧভ"):
      del options._caps[bstack1ll_opy_ (u"ࠧ࡮ࡱࡽ࠾ࡩ࡫ࡢࡶࡩࡪࡩࡷࡇࡤࡥࡴࡨࡷࡸ࠭ম")]
def bstack1l1llll1ll_opy_(proxy_config):
  if bstack1ll_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬয") in proxy_config:
    proxy_config[bstack1ll_opy_ (u"ࠩࡶࡷࡱࡖࡲࡰࡺࡼࠫর")] = proxy_config[bstack1ll_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ঱")]
    del (proxy_config[bstack1ll_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨল")])
  if bstack1ll_opy_ (u"ࠬࡶࡲࡰࡺࡼࡘࡾࡶࡥࠨ঳") in proxy_config and proxy_config[bstack1ll_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡙ࡿࡰࡦࠩ঴")].lower() != bstack1ll_opy_ (u"ࠧࡥ࡫ࡵࡩࡨࡺࠧ঵"):
    proxy_config[bstack1ll_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫশ")] = bstack1ll_opy_ (u"ࠩࡰࡥࡳࡻࡡ࡭ࠩষ")
  if bstack1ll_opy_ (u"ࠪࡴࡷࡵࡸࡺࡃࡸࡸࡴࡩ࡯࡯ࡨ࡬࡫࡚ࡸ࡬ࠨস") in proxy_config:
    proxy_config[bstack1ll_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧহ")] = bstack1ll_opy_ (u"ࠬࡶࡡࡤࠩ঺")
  return proxy_config
def bstack111111l11_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1ll_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬ঻") in config:
    return proxy
  config[bstack1ll_opy_ (u"ࠧࡱࡴࡲࡼࡾ়࠭")] = bstack1l1llll1ll_opy_(config[bstack1ll_opy_ (u"ࠨࡲࡵࡳࡽࡿࠧঽ")])
  if proxy == None:
    proxy = Proxy(config[bstack1ll_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨা")])
  return proxy
def bstack11l1llll_opy_(self):
  global CONFIG
  global bstack1l11l1ll11_opy_
  try:
    proxy = bstack1l1111l11_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1ll_opy_ (u"ࠪ࠲ࡵࡧࡣࠨি")):
        proxies = bstack1l1ll1lll_opy_(proxy, bstack11l11ll11_opy_())
        if len(proxies) > 0:
          protocol, bstack1lll11111_opy_ = proxies.popitem()
          if bstack1ll_opy_ (u"ࠦ࠿࠵࠯ࠣী") in bstack1lll11111_opy_:
            return bstack1lll11111_opy_
          else:
            return bstack1ll_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨু") + bstack1lll11111_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡳࡶࡴࡾࡹࠡࡷࡵࡰࠥࡀࠠࡼࡿࠥূ").format(str(e)))
  return bstack1l11l1ll11_opy_(self)
def bstack1ll1l1llll_opy_():
  global CONFIG
  return bstack11lll1lll_opy_(CONFIG) and bstack1l1111l111_opy_() and bstack11l111ll1_opy_() >= version.parse(bstack1l1lll111_opy_)
def bstack1l111l11l1_opy_():
  global CONFIG
  return (bstack1ll_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪৃ") in CONFIG or bstack1ll_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬৄ") in CONFIG) and bstack11l1l11ll1_opy_()
def bstack11l1l1l11_opy_(config):
  bstack1l1lllll_opy_ = {}
  if bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৅") in config:
    bstack1l1lllll_opy_ = config[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ৆")]
  if bstack1ll_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪে") in config:
    bstack1l1lllll_opy_ = config[bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫৈ")]
  proxy = bstack1l1111l11_opy_(config)
  if proxy:
    if proxy.endswith(bstack1ll_opy_ (u"࠭࠮ࡱࡣࡦࠫ৉")) and os.path.isfile(proxy):
      bstack1l1lllll_opy_[bstack1ll_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪ৊")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1ll_opy_ (u"ࠨ࠰ࡳࡥࡨ࠭ো")):
        proxies = bstack1ll1l111l1_opy_(config, bstack11l11ll11_opy_())
        if len(proxies) > 0:
          protocol, bstack1lll11111_opy_ = proxies.popitem()
          if bstack1ll_opy_ (u"ࠤ࠽࠳࠴ࠨৌ") in bstack1lll11111_opy_:
            parsed_url = urlparse(bstack1lll11111_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1ll_opy_ (u"ࠥ࠾࠴࠵্ࠢ") + bstack1lll11111_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1l1lllll_opy_[bstack1ll_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡋࡳࡸࡺࠧৎ")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1l1lllll_opy_[bstack1ll_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨ৏")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1l1lllll_opy_[bstack1ll_opy_ (u"࠭ࡰࡳࡱࡻࡽ࡚ࡹࡥࡳࠩ৐")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1l1lllll_opy_[bstack1ll_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖࡡࡴࡵࠪ৑")] = str(parsed_url.password)
  return bstack1l1lllll_opy_
def bstack1111l111_opy_(config):
  if bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸ࠭৒") in config:
    return config[bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺࡃࡰࡰࡷࡩࡽࡺࡏࡱࡶ࡬ࡳࡳࡹࠧ৓")]
  return {}
def bstack1l1ll1l11l_opy_(caps):
  global bstack1lll11llll_opy_
  if bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ৔") in caps:
    caps[bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬ৕")][bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࠫ৖")] = True
    if bstack1lll11llll_opy_:
      caps[bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧৗ")][bstack1ll_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ৘")] = bstack1lll11llll_opy_
  else:
    caps[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱ࠭৙")] = True
    if bstack1lll11llll_opy_:
      caps[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ৚")] = bstack1lll11llll_opy_
@measure(event_name=EVENTS.bstack1l11ll1ll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1lll1lll1l_opy_():
  global CONFIG
  if not bstack11ll11l1l1_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ৛") in CONFIG and bstack11ll1lllll_opy_(CONFIG[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨড়")]):
    if (
      bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঢ়") in CONFIG
      and bstack11ll1lllll_opy_(CONFIG[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ৞")].get(bstack1ll_opy_ (u"ࠧࡴ࡭࡬ࡴࡇ࡯࡮ࡢࡴࡼࡍࡳ࡯ࡴࡪࡣ࡯࡭ࡸࡧࡴࡪࡱࡱࠫয়")))
    ):
      logger.debug(bstack1ll_opy_ (u"ࠣࡎࡲࡧࡦࡲࠠࡣ࡫ࡱࡥࡷࡿࠠ࡯ࡱࡷࠤࡸࡺࡡࡳࡶࡨࡨࠥࡧࡳࠡࡵ࡮࡭ࡵࡈࡩ࡯ࡣࡵࡽࡎࡴࡩࡵ࡫ࡤࡰ࡮ࡹࡡࡵ࡫ࡲࡲࠥ࡯ࡳࠡࡧࡱࡥࡧࡲࡥࡥࠤৠ"))
      return
    bstack1l1lllll_opy_ = bstack11l1l1l11_opy_(CONFIG)
    bstack1llll1111l_opy_(CONFIG[bstack1ll_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬৡ")], bstack1l1lllll_opy_)
def bstack1llll1111l_opy_(key, bstack1l1lllll_opy_):
  global bstack1ll1111l11_opy_
  logger.info(bstack1llllll1l_opy_)
  try:
    bstack1ll1111l11_opy_ = Local()
    bstack1ll1ll11ll_opy_ = {bstack1ll_opy_ (u"ࠪ࡯ࡪࡿࠧৢ"): key}
    bstack1ll1ll11ll_opy_.update(bstack1l1lllll_opy_)
    logger.debug(bstack1l1l11l11l_opy_.format(str(bstack1ll1ll11ll_opy_)).replace(key, bstack1ll_opy_ (u"ࠫࡠࡘࡅࡅࡃࡆࡘࡊࡊ࡝ࠨৣ")))
    bstack1ll1111l11_opy_.start(**bstack1ll1ll11ll_opy_)
    if bstack1ll1111l11_opy_.isRunning():
      logger.info(bstack1l1l1111ll_opy_)
  except Exception as e:
    bstack1l11l11l1l_opy_(bstack11ll1l11_opy_.format(str(e)))
def bstack1l1l1l1lll_opy_():
  global bstack1ll1111l11_opy_
  if bstack1ll1111l11_opy_.isRunning():
    logger.info(bstack11l111l11_opy_)
    bstack1ll1111l11_opy_.stop()
  bstack1ll1111l11_opy_ = None
def bstack1l1ll11l1l_opy_(bstack1l1llll1l1_opy_=[]):
  global CONFIG
  bstack11111111_opy_ = []
  bstack1ll1ll11_opy_ = [bstack1ll_opy_ (u"ࠬࡵࡳࠨ৤"), bstack1ll_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩ৥"), bstack1ll_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ০"), bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪ১"), bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧ২"), bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ৩")]
  try:
    for err in bstack1l1llll1l1_opy_:
      bstack11l1lll1l_opy_ = {}
      for k in bstack1ll1ll11_opy_:
        val = CONFIG[bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ৪")][int(err[bstack1ll_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ৫")])].get(k)
        if val:
          bstack11l1lll1l_opy_[k] = val
      if(err[bstack1ll_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ৬")] != bstack1ll_opy_ (u"ࠧࠨ৭")):
        bstack11l1lll1l_opy_[bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡹࠧ৮")] = {
          err[bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ৯")]: err[bstack1ll_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩৰ")]
        }
        bstack11111111_opy_.append(bstack11l1lll1l_opy_)
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡦࡰࡴࡰࡥࡹࡺࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡨࡲࡶࠥ࡫ࡶࡦࡰࡷ࠾ࠥ࠭ৱ") + str(e))
  finally:
    return bstack11111111_opy_
def bstack1ll11lll_opy_(file_name):
  bstack1111111ll_opy_ = []
  try:
    bstack11111lll_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack11111lll_opy_):
      with open(bstack11111lll_opy_) as f:
        bstack111111ll_opy_ = json.load(f)
        bstack1111111ll_opy_ = bstack111111ll_opy_
      os.remove(bstack11111lll_opy_)
    return bstack1111111ll_opy_
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧ࡫ࡱࡨ࡮ࡴࡧࠡࡧࡵࡶࡴࡸࠠ࡭࡫ࡶࡸ࠿ࠦࠧ৲") + str(e))
    return bstack1111111ll_opy_
def bstack11ll11l11_opy_():
  try:
      from bstack_utils.constants import bstack1l1l111lll_opy_, EVENTS
      from bstack_utils.helper import bstack11ll1l1ll1_opy_, get_host_info, bstack1lll1111ll_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack11ll1l111l_opy_ = os.path.join(os.getcwd(), bstack1ll_opy_ (u"࠭࡬ࡰࡩࠪ৳"), bstack1ll_opy_ (u"ࠧ࡬ࡧࡼ࠱ࡲ࡫ࡴࡳ࡫ࡦࡷ࠳ࡰࡳࡰࡰࠪ৴"))
      lock = FileLock(bstack11ll1l111l_opy_+bstack1ll_opy_ (u"ࠣ࠰࡯ࡳࡨࡱࠢ৵"))
      def bstack11l11l1ll1_opy_():
          try:
              with lock:
                  with open(bstack11ll1l111l_opy_, bstack1ll_opy_ (u"ࠤࡵࠦ৶"), encoding=bstack1ll_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤ৷")) as file:
                      data = json.load(file)
                      config = {
                          bstack1ll_opy_ (u"ࠦ࡭࡫ࡡࡥࡧࡵࡷࠧ৸"): {
                              bstack1ll_opy_ (u"ࠧࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠦ৹"): bstack1ll_opy_ (u"ࠨࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠤ৺"),
                          }
                      }
                      bstack1ll1l11lll_opy_ = datetime.utcnow()
                      bstack11ll111lll_opy_ = bstack1ll1l11lll_opy_.strftime(bstack1ll_opy_ (u"࡛ࠢࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࠲ࠪ࡬ࠠࡖࡖࡆࠦ৻"))
                      bstack1lll1l11ll_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ৼ")) if os.environ.get(bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ৽")) else bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠥࡷࡩࡱࡒࡶࡰࡌࡨࠧ৾"))
                      payload = {
                          bstack1ll_opy_ (u"ࠦࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠣ৿"): bstack1ll_opy_ (u"ࠧࡹࡤ࡬ࡡࡨࡺࡪࡴࡴࡴࠤ਀"),
                          bstack1ll_opy_ (u"ࠨࡤࡢࡶࡤࠦਁ"): {
                              bstack1ll_opy_ (u"ࠢࡵࡧࡶࡸ࡭ࡻࡢࡠࡷࡸ࡭ࡩࠨਂ"): bstack1lll1l11ll_opy_,
                              bstack1ll_opy_ (u"ࠣࡥࡵࡩࡦࡺࡥࡥࡡࡧࡥࡾࠨਃ"): bstack11ll111lll_opy_,
                              bstack1ll_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠࡰࡤࡱࡪࠨ਄"): bstack1ll_opy_ (u"ࠥࡗࡉࡑࡆࡦࡣࡷࡹࡷ࡫ࡐࡦࡴࡩࡳࡷࡳࡡ࡯ࡥࡨࠦਅ"),
                              bstack1ll_opy_ (u"ࠦࡪࡼࡥ࡯ࡶࡢ࡮ࡸࡵ࡮ࠣਆ"): {
                                  bstack1ll_opy_ (u"ࠧࡳࡥࡢࡵࡸࡶࡪࡹࠢਇ"): data,
                                  bstack1ll_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣਈ"): bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠢࡴࡦ࡮ࡖࡺࡴࡉࡥࠤਉ"))
                              },
                              bstack1ll_opy_ (u"ࠣࡷࡶࡩࡷࡥࡤࡢࡶࡤࠦਊ"): bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠤࡸࡷࡪࡸࡎࡢ࡯ࡨࠦ਋")),
                              bstack1ll_opy_ (u"ࠥ࡬ࡴࡹࡴࡠ࡫ࡱࡪࡴࠨ਌"): get_host_info()
                          }
                      }
                      response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠦࡕࡕࡓࡕࠤ਍"), bstack1l1l111lll_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack1ll_opy_ (u"ࠧࡊࡡࡵࡣࠣࡷࡪࡴࡴࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡵࡱࠣࡿࢂࠦࡷࡪࡶ࡫ࠤࡩࡧࡴࡢࠢࡾࢁࠧ਎").format(bstack1l1l111lll_opy_, payload))
                      else:
                          logger.debug(bstack1ll_opy_ (u"ࠨࡒࡦࡳࡸࡩࡸࡺࠠࡧࡣ࡬ࡰࡪࡪࠠࡧࡱࡵࠤࢀࢃࠠࡸ࡫ࡷ࡬ࠥࡪࡡࡵࡣࠣࡿࢂࠨਏ").format(bstack1l1l111lll_opy_, payload))
          except Exception as e:
              logger.debug(bstack1ll_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡴࡤࠡ࡭ࡨࡽࠥࡳࡥࡵࡴ࡬ࡧࡸࠦࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡࡽࢀࠦਐ").format(e))
      bstack11l11l1ll1_opy_()
      bstack1l111lllll_opy_(bstack11ll1l111l_opy_, logger)
  except:
    pass
def bstack11l1ll111_opy_():
  global bstack1llllll1l1_opy_
  global bstack1llll1lll_opy_
  global bstack1l11ll11_opy_
  global bstack1111l11l_opy_
  global bstack1l1l11ll1l_opy_
  global bstack1l11ll1l11_opy_
  global CONFIG
  bstack11111l111_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠨࡈࡕࡅࡒࡋࡗࡐࡔࡎࡣ࡚࡙ࡅࡅࠩ਑"))
  if bstack11111l111_opy_ in [bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ਒"), bstack1ll_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩਓ")]:
    bstack1l1111lll_opy_()
  percy.shutdown()
  if bstack1llllll1l1_opy_:
    logger.warning(bstack1ll1ll1l_opy_.format(str(bstack1llllll1l1_opy_)))
  else:
    try:
      bstack111lllll1_opy_ = bstack1ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪਔ"), logger)
      if bstack111lllll1_opy_.get(bstack1ll_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪਕ")) and bstack111lllll1_opy_.get(bstack1ll_opy_ (u"࠭࡮ࡶࡦࡪࡩࡤࡲ࡯ࡤࡣ࡯ࠫਖ")).get(bstack1ll_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩਗ")):
        logger.warning(bstack1ll1ll1l_opy_.format(str(bstack111lllll1_opy_[bstack1ll_opy_ (u"ࠨࡰࡸࡨ࡬࡫࡟࡭ࡱࡦࡥࡱ࠭ਘ")][bstack1ll_opy_ (u"ࠩ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨࠫਙ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.bstack1l1l1llll_opy_)
  logger.info(bstack11l1l1ll1_opy_)
  global bstack1ll1111l11_opy_
  if bstack1ll1111l11_opy_:
    bstack1l1l1l1lll_opy_()
  try:
    for driver in bstack1llll1lll_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1ll1lllll1_opy_)
  if bstack1l11ll1l11_opy_ == bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩਚ"):
    bstack1l1l11ll1l_opy_ = bstack1ll11lll_opy_(bstack1ll_opy_ (u"ࠫࡷࡵࡢࡰࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬਛ"))
  if bstack1l11ll1l11_opy_ == bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬਜ") and len(bstack1111l11l_opy_) == 0:
    bstack1111l11l_opy_ = bstack1ll11lll_opy_(bstack1ll_opy_ (u"࠭ࡰࡸࡡࡳࡽࡹ࡫ࡳࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਝ"))
    if len(bstack1111l11l_opy_) == 0:
      bstack1111l11l_opy_ = bstack1ll11lll_opy_(bstack1ll_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡱࡲࡳࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴ࠯࡬ࡶࡳࡳ࠭ਞ"))
  bstack1l1111l1_opy_ = bstack1ll_opy_ (u"ࠨࠩਟ")
  if len(bstack1l11ll11_opy_) > 0:
    bstack1l1111l1_opy_ = bstack1l1ll11l1l_opy_(bstack1l11ll11_opy_)
  elif len(bstack1111l11l_opy_) > 0:
    bstack1l1111l1_opy_ = bstack1l1ll11l1l_opy_(bstack1111l11l_opy_)
  elif len(bstack1l1l11ll1l_opy_) > 0:
    bstack1l1111l1_opy_ = bstack1l1ll11l1l_opy_(bstack1l1l11ll1l_opy_)
  elif len(bstack11l11l11l_opy_) > 0:
    bstack1l1111l1_opy_ = bstack1l1ll11l1l_opy_(bstack11l11l11l_opy_)
  if bool(bstack1l1111l1_opy_):
    bstack1llll11l11_opy_(bstack1l1111l1_opy_)
  else:
    bstack1llll11l11_opy_()
  bstack1l111lllll_opy_(bstack11lll111l1_opy_, logger)
  if bstack11111l111_opy_ not in [bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪਠ")]:
    bstack11ll11l11_opy_()
  bstack111ll11ll_opy_.bstack11l111lll1_opy_(CONFIG)
  if len(bstack1l1l11ll1l_opy_) > 0:
    sys.exit(len(bstack1l1l11ll1l_opy_))
def bstack1lll111l1_opy_(bstack111111111_opy_, frame):
  global bstack1lll1111ll_opy_
  logger.error(bstack1ll111llll_opy_)
  bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡒࡴ࠭ਡ"), bstack111111111_opy_)
  if hasattr(signal, bstack1ll_opy_ (u"ࠫࡘ࡯ࡧ࡯ࡣ࡯ࡷࠬਢ")):
    bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬਣ"), signal.Signals(bstack111111111_opy_).name)
  else:
    bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"࠭ࡳࡥ࡭ࡎ࡭ࡱࡲࡓࡪࡩࡱࡥࡱ࠭ਤ"), bstack1ll_opy_ (u"ࠧࡔࡋࡊ࡙ࡓࡑࡎࡐ࡙ࡑࠫਥ"))
  if cli.is_running():
    bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.bstack1l1l1llll_opy_)
  bstack11111l111_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠨࡈࡕࡅࡒࡋࡗࡐࡔࡎࡣ࡚࡙ࡅࡅࠩਦ"))
  if bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩਧ") and not cli.is_enabled(CONFIG):
    bstack1l111111_opy_.stop(bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪਨ")))
  bstack11l1ll111_opy_()
  sys.exit(1)
def bstack1l11l11l1l_opy_(err):
  logger.critical(bstack1ll11l111l_opy_.format(str(err)))
  bstack1llll11l11_opy_(bstack1ll11l111l_opy_.format(str(err)), True)
  atexit.unregister(bstack11l1ll111_opy_)
  bstack1l1111lll_opy_()
  sys.exit(1)
def bstack11l1l111l1_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1llll11l11_opy_(message, True)
  atexit.unregister(bstack11l1ll111_opy_)
  bstack1l1111lll_opy_()
  sys.exit(1)
def bstack1lll11ll11_opy_():
  global CONFIG
  global bstack1llll1l1_opy_
  global bstack11lll11ll1_opy_
  global bstack1lllll11_opy_
  CONFIG = bstack1l11ll1l1_opy_()
  load_dotenv(CONFIG.get(bstack1ll_opy_ (u"ࠫࡪࡴࡶࡇ࡫࡯ࡩࠬ਩")))
  bstack11l1l1ll11_opy_()
  bstack1ll111ll_opy_()
  CONFIG = bstack111l1111_opy_(CONFIG)
  update(CONFIG, bstack11lll11ll1_opy_)
  update(CONFIG, bstack1llll1l1_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack1l111ll1_opy_(CONFIG)
  bstack1lllll11_opy_ = bstack11ll11l1l1_opy_(CONFIG)
  os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨਪ")] = bstack1lllll11_opy_.__str__().lower()
  bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧਫ"), bstack1lllll11_opy_)
  if (bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪਬ") in CONFIG and bstack1ll_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫਭ") in bstack1llll1l1_opy_) or (
          bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬਮ") in CONFIG and bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ਯ") not in bstack11lll11ll1_opy_):
    if os.getenv(bstack1ll_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨਰ")):
      CONFIG[bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ਱")] = os.getenv(bstack1ll_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪਲ"))
    else:
      if not CONFIG.get(bstack1ll_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠥਲ਼"), bstack1ll_opy_ (u"ࠣࠤ਴")) in bstack1l1ll111ll_opy_:
        bstack11lllll1ll_opy_()
  elif (bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬਵ") not in CONFIG and bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬਸ਼") in CONFIG) or (
          bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ਷") in bstack11lll11ll1_opy_ and bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨਸ") not in bstack1llll1l1_opy_):
    del (CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨਹ")])
  if bstack11lll1ll_opy_(CONFIG):
    bstack1l11l11l1l_opy_(bstack11ll1lll_opy_)
  Config.bstack11ll1l1l_opy_().bstack11111l11_opy_(bstack1ll_opy_ (u"ࠢࡶࡵࡨࡶࡓࡧ࡭ࡦࠤ਺"), CONFIG[bstack1ll_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ਻")])
  bstack111lll1l1_opy_()
  bstack11ll1111l1_opy_()
  if bstack1l11lll1_opy_ and not CONFIG.get(bstack1ll_opy_ (u"ࠤࡩࡶࡦࡳࡥࡸࡱࡵ࡯਼ࠧ"), bstack1ll_opy_ (u"ࠥࠦ਽")) in bstack1l1ll111ll_opy_:
    CONFIG[bstack1ll_opy_ (u"ࠫࡦࡶࡰࠨਾ")] = bstack1lllll111l_opy_(CONFIG)
    logger.info(bstack1l1lll1lll_opy_.format(CONFIG[bstack1ll_opy_ (u"ࠬࡧࡰࡱࠩਿ")]))
  if not bstack1lllll11_opy_:
    CONFIG[bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩੀ")] = [{}]
def bstack1l1l1l1ll_opy_(config, bstack11l1ll1ll1_opy_):
  global CONFIG
  global bstack1l11lll1_opy_
  CONFIG = config
  bstack1l11lll1_opy_ = bstack11l1ll1ll1_opy_
def bstack11ll1111l1_opy_():
  global CONFIG
  global bstack1l11lll1_opy_
  if bstack1ll_opy_ (u"ࠧࡢࡲࡳࠫੁ") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack11llll1ll_opy_)
    bstack1l11lll1_opy_ = True
    bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧੂ"), True)
def bstack1lllll111l_opy_(config):
  bstack1l1l111l11_opy_ = bstack1ll_opy_ (u"ࠩࠪ੃")
  app = config[bstack1ll_opy_ (u"ࠪࡥࡵࡶࠧ੄")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1l1llll11l_opy_:
      if os.path.exists(app):
        bstack1l1l111l11_opy_ = bstack1l1l11l111_opy_(config, app)
      elif bstack1lll1ll11l_opy_(app):
        bstack1l1l111l11_opy_ = app
      else:
        bstack1l11l11l1l_opy_(bstack11ll1111ll_opy_.format(app))
    else:
      if bstack1lll1ll11l_opy_(app):
        bstack1l1l111l11_opy_ = app
      elif os.path.exists(app):
        bstack1l1l111l11_opy_ = bstack1l1l11l111_opy_(app)
      else:
        bstack1l11l11l1l_opy_(bstack11l111lll_opy_)
  else:
    if len(app) > 2:
      bstack1l11l11l1l_opy_(bstack1lll1111l1_opy_)
    elif len(app) == 2:
      if bstack1ll_opy_ (u"ࠫࡵࡧࡴࡩࠩ੅") in app and bstack1ll_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨ੆") in app:
        if os.path.exists(app[bstack1ll_opy_ (u"࠭ࡰࡢࡶ࡫ࠫੇ")]):
          bstack1l1l111l11_opy_ = bstack1l1l11l111_opy_(config, app[bstack1ll_opy_ (u"ࠧࡱࡣࡷ࡬ࠬੈ")], app[bstack1ll_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠫ੉")])
        else:
          bstack1l11l11l1l_opy_(bstack11ll1111ll_opy_.format(app))
      else:
        bstack1l11l11l1l_opy_(bstack1lll1111l1_opy_)
    else:
      for key in app:
        if key in bstack1l11l1ll1_opy_:
          if key == bstack1ll_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ੊"):
            if os.path.exists(app[key]):
              bstack1l1l111l11_opy_ = bstack1l1l11l111_opy_(config, app[key])
            else:
              bstack1l11l11l1l_opy_(bstack11ll1111ll_opy_.format(app))
          else:
            bstack1l1l111l11_opy_ = app[key]
        else:
          bstack1l11l11l1l_opy_(bstack1ll1lll111_opy_)
  return bstack1l1l111l11_opy_
def bstack1lll1ll11l_opy_(bstack1l1l111l11_opy_):
  import re
  bstack1ll11ll1ll_opy_ = re.compile(bstack1ll_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫࠦࠥੋ"))
  bstack111111ll1_opy_ = re.compile(bstack1ll_opy_ (u"ࡶࠧࡤ࡛ࡢ࠯ࡽࡅ࠲ࡠ࠰࠮࠻࡟ࡣ࠳ࡢ࠭࡞ࠬ࠲࡟ࡦ࠳ࡺࡂ࠯࡝࠴࠲࠿࡜ࡠ࠰࡟࠱ࡢ࠰ࠤࠣੌ"))
  if bstack1ll_opy_ (u"ࠬࡨࡳ࠻࠱࠲੍ࠫ") in bstack1l1l111l11_opy_ or re.fullmatch(bstack1ll11ll1ll_opy_, bstack1l1l111l11_opy_) or re.fullmatch(bstack111111ll1_opy_, bstack1l1l111l11_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1llll111l1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1l1l11l111_opy_(config, path, bstack1l11l1l11_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1ll_opy_ (u"࠭ࡲࡣࠩ੎")).read()).hexdigest()
  bstack11ll1ll1l1_opy_ = bstack11l1ll1111_opy_(md5_hash)
  bstack1l1l111l11_opy_ = None
  if bstack11ll1ll1l1_opy_:
    logger.info(bstack11111ll1l_opy_.format(bstack11ll1ll1l1_opy_, md5_hash))
    return bstack11ll1ll1l1_opy_
  bstack1lll1ll11_opy_ = datetime.datetime.now()
  bstack11ll1lll11_opy_ = MultipartEncoder(
    fields={
      bstack1ll_opy_ (u"ࠧࡧ࡫࡯ࡩࠬ੏"): (os.path.basename(path), open(os.path.abspath(path), bstack1ll_opy_ (u"ࠨࡴࡥࠫ੐")), bstack1ll_opy_ (u"ࠩࡷࡩࡽࡺ࠯ࡱ࡮ࡤ࡭ࡳ࠭ੑ")),
      bstack1ll_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭੒"): bstack1l11l1l11_opy_
    }
  )
  response = requests.post(bstack1ll1l1ll1l_opy_, data=bstack11ll1lll11_opy_,
                           headers={bstack1ll_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ੓"): bstack11ll1lll11_opy_.content_type},
                           auth=(config[bstack1ll_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ੔")], config[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ੕")]))
  try:
    res = json.loads(response.text)
    bstack1l1l111l11_opy_ = res[bstack1ll_opy_ (u"ࠧࡢࡲࡳࡣࡺࡸ࡬ࠨ੖")]
    logger.info(bstack11l1ll1lll_opy_.format(bstack1l1l111l11_opy_))
    bstack1l11ll1l_opy_(md5_hash, bstack1l1l111l11_opy_)
    cli.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠣࡪࡷࡸࡵࡀࡵࡱ࡮ࡲࡥࡩࡥࡡࡱࡲࠥ੗"), datetime.datetime.now() - bstack1lll1ll11_opy_)
  except ValueError as err:
    bstack1l11l11l1l_opy_(bstack11lllll11_opy_.format(str(err)))
  return bstack1l1l111l11_opy_
def bstack111lll1l1_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack11l11l1lll_opy_
  bstack1ll1lllll_opy_ = 1
  bstack1l1l1l1l1_opy_ = 1
  if bstack1ll_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ੘") in CONFIG:
    bstack1l1l1l1l1_opy_ = CONFIG[bstack1ll_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪਖ਼")]
  else:
    bstack1l1l1l1l1_opy_ = bstack111l111ll_opy_(framework_name, args) or 1
  if bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧਗ਼") in CONFIG:
    bstack1ll1lllll_opy_ = len(CONFIG[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨਜ਼")])
  bstack11l11l1lll_opy_ = int(bstack1l1l1l1l1_opy_) * int(bstack1ll1lllll_opy_)
def bstack111l111ll_opy_(framework_name, args):
  if framework_name == bstack11111ll11_opy_ and args and bstack1ll_opy_ (u"࠭࠭࠮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫੜ") in args:
      bstack1l11lll111_opy_ = args.index(bstack1ll_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬ੝"))
      return int(args[bstack1l11lll111_opy_ + 1]) or 1
  return 1
def bstack11l1ll1111_opy_(md5_hash):
  bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠨࢀࠪਫ਼")), bstack1ll_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ੟"), bstack1ll_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ੠"))
  if os.path.exists(bstack1l11l1111_opy_):
    bstack1l11l1l1_opy_ = json.load(open(bstack1l11l1111_opy_, bstack1ll_opy_ (u"ࠫࡷࡨࠧ੡")))
    if md5_hash in bstack1l11l1l1_opy_:
      bstack11ll11l11l_opy_ = bstack1l11l1l1_opy_[md5_hash]
      bstack11lll11l11_opy_ = datetime.datetime.now()
      bstack11l11l1ll_opy_ = datetime.datetime.strptime(bstack11ll11l11l_opy_[bstack1ll_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ੢")], bstack1ll_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪ੣"))
      if (bstack11lll11l11_opy_ - bstack11l11l1ll_opy_).days > 30:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack11ll11l11l_opy_[bstack1ll_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ੤")]):
        return None
      return bstack11ll11l11l_opy_[bstack1ll_opy_ (u"ࠨ࡫ࡧࠫ੥")]
  else:
    return None
def bstack1l11ll1l_opy_(md5_hash, bstack1l1l111l11_opy_):
  bstack1llll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠩࢁࠫ੦")), bstack1ll_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ੧"))
  if not os.path.exists(bstack1llll1ll1_opy_):
    os.makedirs(bstack1llll1ll1_opy_)
  bstack1l11l1111_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠫࢃ࠭੨")), bstack1ll_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ੩"), bstack1ll_opy_ (u"࠭ࡡࡱࡲࡘࡴࡱࡵࡡࡥࡏࡇ࠹ࡍࡧࡳࡩ࠰࡭ࡷࡴࡴࠧ੪"))
  bstack1l11llllll_opy_ = {
    bstack1ll_opy_ (u"ࠧࡪࡦࠪ੫"): bstack1l1l111l11_opy_,
    bstack1ll_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ੬"): datetime.datetime.strftime(datetime.datetime.now(), bstack1ll_opy_ (u"ࠩࠨࡨ࠴ࠫ࡭࠰ࠧ࡜ࠤࠪࡎ࠺ࠦࡏ࠽ࠩࡘ࠭੭")),
    bstack1ll_opy_ (u"ࠪࡷࡩࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ੮"): str(__version__)
  }
  if os.path.exists(bstack1l11l1111_opy_):
    bstack1l11l1l1_opy_ = json.load(open(bstack1l11l1111_opy_, bstack1ll_opy_ (u"ࠫࡷࡨࠧ੯")))
  else:
    bstack1l11l1l1_opy_ = {}
  bstack1l11l1l1_opy_[md5_hash] = bstack1l11llllll_opy_
  with open(bstack1l11l1111_opy_, bstack1ll_opy_ (u"ࠧࡽࠫࠣੰ")) as outfile:
    json.dump(bstack1l11l1l1_opy_, outfile)
def bstack1l11l11111_opy_(self):
  return
def bstack1lll111l_opy_(self):
  return
def bstack11ll1ll1l_opy_():
  global bstack1l11l1l1l1_opy_
  bstack1l11l1l1l1_opy_ = True
@measure(event_name=EVENTS.bstack1ll1l1lll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1l1l1l11ll_opy_(self):
  global bstack11ll1l1lll_opy_
  global bstack1l1111l11l_opy_
  global bstack1lll11111l_opy_
  try:
    if bstack1ll_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ੱ") in bstack11ll1l1lll_opy_ and self.session_id != None and bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡘࡺࡡࡵࡷࡶࠫੲ"), bstack1ll_opy_ (u"ࠨࠩੳ")) != bstack1ll_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪੴ"):
      bstack1l11l1l1ll_opy_ = bstack1ll_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪੵ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1ll_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫ੶")
      if bstack1l11l1l1ll_opy_ == bstack1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ੷"):
        bstack11lll1l1l_opy_(logger)
      if self != None:
        bstack11llll111_opy_(self, bstack1l11l1l1ll_opy_, bstack1ll_opy_ (u"࠭ࠬࠡࠩ੸").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack1ll_opy_ (u"ࠧࠨ੹")
    if bstack1ll_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ੺") in bstack11ll1l1lll_opy_ and getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੻"), None):
      bstack11l1l11111_opy_.bstack1111l1111_opy_(self, bstack1l1llll111_opy_, logger, wait=True)
    if bstack1ll_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ੼") in bstack11ll1l1lll_opy_:
      if not threading.currentThread().behave_test_status:
        bstack11llll111_opy_(self, bstack1ll_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ੽"))
      bstack1111111l_opy_.bstack1lllll1ll1_opy_(self)
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࠨ੾") + str(e))
  bstack1lll11111l_opy_(self)
  self.session_id = None
def bstack11l11111_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1llll1l1ll_opy_
    global bstack11ll1l1lll_opy_
    command_executor = kwargs.get(bstack1ll_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠩ੿"), bstack1ll_opy_ (u"ࠧࠨ઀"))
    bstack11l11lllll_opy_ = False
    if type(command_executor) == str and bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫઁ") in command_executor:
      bstack11l11lllll_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬં") in str(getattr(command_executor, bstack1ll_opy_ (u"ࠪࡣࡺࡸ࡬ࠨઃ"), bstack1ll_opy_ (u"ࠫࠬ઄"))):
      bstack11l11lllll_opy_ = True
    else:
      kwargs = bstack1l11llll1l_opy_.bstack1l1ll1111_opy_(bstack1ll1llll_opy_=kwargs, config=CONFIG)
      return bstack1ll111ll11_opy_(self, *args, **kwargs)
    if bstack11l11lllll_opy_:
      bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(CONFIG, bstack11ll1l1lll_opy_)
      if kwargs.get(bstack1ll_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭અ")):
        kwargs[bstack1ll_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧઆ")] = bstack1llll1l1ll_opy_(kwargs[bstack1ll_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨઇ")], bstack11ll1l1lll_opy_, CONFIG, bstack1ll1111l_opy_)
      elif kwargs.get(bstack1ll_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨઈ")):
        kwargs[bstack1ll_opy_ (u"ࠩࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩઉ")] = bstack1llll1l1ll_opy_(kwargs[bstack1ll_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪઊ")], bstack11ll1l1lll_opy_, CONFIG, bstack1ll1111l_opy_)
  except Exception as e:
    logger.error(bstack1ll_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡫࡮ࠡࡲࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫࡙ࠥࡄࡌࠢࡦࡥࡵࡹ࠺ࠡࡽࢀࠦઋ").format(str(e)))
  return bstack1ll111ll11_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack11ll111ll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1ll111l1l1_opy_(self, command_executor=bstack1ll_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴࠷࠲࠸࠰࠳࠲࠵࠴࠱࠻࠶࠷࠸࠹ࠨઌ"), *args, **kwargs):
  global bstack1l1111l11l_opy_
  global bstack1llll1lll_opy_
  bstack1ll1llllll_opy_ = bstack11l11111_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack11llllll1l_opy_.on():
    return bstack1ll1llllll_opy_
  try:
    logger.debug(bstack1ll_opy_ (u"࠭ࡃࡰ࡯ࡰࡥࡳࡪࠠࡆࡺࡨࡧࡺࡺ࡯ࡳࠢࡺ࡬ࡪࡴࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣ࡭ࡸࠦࡦࡢ࡮ࡶࡩࠥ࠳ࠠࡼࡿࠪઍ").format(str(command_executor)))
    logger.debug(bstack1ll_opy_ (u"ࠧࡉࡷࡥࠤ࡚ࡘࡌࠡ࡫ࡶࠤ࠲ࠦࡻࡾࠩ઎").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫએ") in command_executor._url:
      bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪઐ"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠭ઑ") in command_executor):
    bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ઒"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack1l11ll11l1_opy_ = getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࡙࡫ࡳࡵࡏࡨࡸࡦ࠭ઓ"), None)
  bstack1l11111lll_opy_ = {}
  if self.capabilities is not None:
    bstack1l11111lll_opy_[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟࡯ࡣࡰࡩࠬઔ")] = self.capabilities.get(bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬક"))
    bstack1l11111lll_opy_[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪખ")] = self.capabilities.get(bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪગ"))
    bstack1l11111lll_opy_[bstack1ll_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡢࡳࡵࡺࡩࡰࡰࡶࠫઘ")] = self.capabilities.get(bstack1ll_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩઙ"))
  if CONFIG.get(bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬચ"), False) and bstack1l11llll1l_opy_.bstack1ll111lll_opy_(bstack1l11111lll_opy_):
    threading.current_thread().a11yPlatform = True
  if bstack1ll_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭છ") in bstack11ll1l1lll_opy_ or bstack1ll_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭જ") in bstack11ll1l1lll_opy_:
    bstack1l111111_opy_.bstack11lll11ll_opy_(self)
  if bstack1ll_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨઝ") in bstack11ll1l1lll_opy_ and bstack1l11ll11l1_opy_ and bstack1l11ll11l1_opy_.get(bstack1ll_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩઞ"), bstack1ll_opy_ (u"ࠪࠫટ")) == bstack1ll_opy_ (u"ࠫࡵ࡫࡮ࡥ࡫ࡱ࡫ࠬઠ"):
    bstack1l111111_opy_.bstack11lll11ll_opy_(self)
  bstack1l1111l11l_opy_ = self.session_id
  bstack1llll1lll_opy_.append(self)
  return bstack1ll1llllll_opy_
def bstack111ll11l_opy_(args):
  return bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷ࠭ડ") in str(args)
def bstack1ll11llll_opy_(self, driver_command, *args, **kwargs):
  global bstack11l11ll1ll_opy_
  global bstack11lllllll_opy_
  bstack11l11lll1l_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪઢ"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ણ"), None)
  bstack11l11ll1_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨત"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫથ"), None)
  bstack1ll1111ll_opy_ = getattr(self, bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪદ"), None) != None and getattr(self, bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫધ"), None) == True
  if not bstack11lllllll_opy_ and bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬન") in CONFIG and CONFIG[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭઩")] == True and bstack1l11l1l1l_opy_.bstack11l1111l_opy_(driver_command) and (bstack1ll1111ll_opy_ or bstack11l11lll1l_opy_) and not bstack111ll11l_opy_(args):
    try:
      bstack11lllllll_opy_ = True
      logger.debug(bstack1ll_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡻࡾࠩપ").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack1ll_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵ࡫ࡲࡧࡱࡵࡱࠥࡹࡣࡢࡰࠣࡿࢂ࠭ફ").format(str(err)))
    bstack11lllllll_opy_ = False
  response = bstack11l11ll1ll_opy_(self, driver_command, *args, **kwargs)
  if (bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨબ") in str(bstack11ll1l1lll_opy_).lower() or bstack1ll_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪભ") in str(bstack11ll1l1lll_opy_).lower()) and bstack11llllll1l_opy_.on():
    try:
      if driver_command == bstack1ll_opy_ (u"ࠫࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࠨમ"):
        bstack1l111111_opy_.bstack1111llll1_opy_({
            bstack1ll_opy_ (u"ࠬ࡯࡭ࡢࡩࡨࠫય"): response[bstack1ll_opy_ (u"࠭ࡶࡢ࡮ࡸࡩࠬર")],
            bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ઱"): bstack1l111111_opy_.current_test_uuid() if bstack1l111111_opy_.current_test_uuid() else bstack11llllll1l_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack1l1ll1lll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack11l111ll1l_opy_(self, command_executor,
             desired_capabilities=None, bstack1ll11l1l1_opy_=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1l1111l11l_opy_
  global bstack1l1111ll_opy_
  global bstack1lll1lllll_opy_
  global bstack11l11llll1_opy_
  global bstack1l1lll1111_opy_
  global bstack11ll1l1lll_opy_
  global bstack1ll111ll11_opy_
  global bstack1llll1lll_opy_
  global bstack1l111ll11_opy_
  global bstack1l1llll111_opy_
  CONFIG[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪલ")] = str(bstack11ll1l1lll_opy_) + str(__version__)
  bstack1l1llllll1_opy_ = os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧળ")]
  bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(CONFIG, bstack11ll1l1lll_opy_)
  CONFIG[bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭઴")] = bstack1l1llllll1_opy_
  CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭વ")] = bstack1ll1111l_opy_
  if CONFIG.get(bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬશ"),bstack1ll_opy_ (u"࠭ࠧષ")) and bstack1ll_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭સ") in bstack11ll1l1lll_opy_:
    CONFIG[bstack1ll_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨહ")].pop(bstack1ll_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ઺"), None)
    CONFIG[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ઻")].pop(bstack1ll_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦ઼ࠩ"), None)
  command_executor = bstack11l11ll11_opy_()
  logger.debug(bstack111l1111l_opy_.format(command_executor))
  proxy = bstack111111l11_opy_(CONFIG, proxy)
  bstack1l1ll1ll11_opy_ = 0 if bstack1l1111ll_opy_ < 0 else bstack1l1111ll_opy_
  try:
    if bstack11l11llll1_opy_ is True:
      bstack1l1ll1ll11_opy_ = int(multiprocessing.current_process().name)
    elif bstack1l1lll1111_opy_ is True:
      bstack1l1ll1ll11_opy_ = int(threading.current_thread().name)
  except:
    bstack1l1ll1ll11_opy_ = 0
  bstack1lll11ll1_opy_ = bstack1lll1llll_opy_(CONFIG, bstack1l1ll1ll11_opy_)
  logger.debug(bstack111l1llll_opy_.format(str(bstack1lll11ll1_opy_)))
  if bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩઽ") in CONFIG and bstack11ll1lllll_opy_(CONFIG[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪા")]):
    bstack1l1ll1l11l_opy_(bstack1lll11ll1_opy_)
  if bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1ll1ll11_opy_) and bstack1l11llll1l_opy_.bstack11l11l1l1l_opy_(bstack1lll11ll1_opy_, options, desired_capabilities, CONFIG):
    threading.current_thread().a11yPlatform = True
    if (cli.accessibility is None or not cli.accessibility.is_enabled()):
      bstack1l11llll1l_opy_.set_capabilities(bstack1lll11ll1_opy_, CONFIG)
  if desired_capabilities:
    bstack1ll1ll111l_opy_ = bstack111l1111_opy_(desired_capabilities)
    bstack1ll1ll111l_opy_[bstack1ll_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧિ")] = bstack11111l1l_opy_(CONFIG)
    bstack1111ll11l_opy_ = bstack1lll1llll_opy_(bstack1ll1ll111l_opy_)
    if bstack1111ll11l_opy_:
      bstack1lll11ll1_opy_ = update(bstack1111ll11l_opy_, bstack1lll11ll1_opy_)
    desired_capabilities = None
  if options:
    bstack1ll1l1l111_opy_(options, bstack1lll11ll1_opy_)
  if not options:
    options = bstack1l1l111ll_opy_(bstack1lll11ll1_opy_)
  bstack1l1llll111_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫી"))[bstack1l1ll1ll11_opy_]
  if proxy and bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩુ")):
    options.proxy(proxy)
  if options and bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩૂ")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack11l111ll1_opy_() < version.parse(bstack1ll_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪૃ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack1lll11ll1_opy_)
  logger.info(bstack11ll1llll_opy_)
  bstack1ll1lll1l_opy_.end(EVENTS.bstack1l11l1ll1l_opy_.value, EVENTS.bstack1l11l1ll1l_opy_.value + bstack1ll_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧૄ"), EVENTS.bstack1l11l1ll1l_opy_.value + bstack1ll_opy_ (u"ࠨ࠺ࡦࡰࡧࠦૅ"), status=True, failure=None, test_name=bstack1lll1lllll_opy_)
  if bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡲࡵࡳ࡫࡯࡬ࡦࠩ૆") in kwargs:
    del kwargs[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡳࡶࡴ࡬ࡩ࡭ࡧࠪે")]
  if bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩૈ")):
    bstack1ll111ll11_opy_(self, command_executor=command_executor,
              options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
  elif bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩૉ")):
    bstack1ll111ll11_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities, options=options,
              bstack1ll11l1l1_opy_=bstack1ll11l1l1_opy_, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  elif bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠫ࠷࠴࠵࠴࠰࠳ࠫ૊")):
    bstack1ll111ll11_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              bstack1ll11l1l1_opy_=bstack1ll11l1l1_opy_, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack1ll111ll11_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              bstack1ll11l1l1_opy_=bstack1ll11l1l1_opy_, proxy=proxy,
              keep_alive=keep_alive)
  if bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1ll1ll11_opy_) and bstack1l11llll1l_opy_.bstack11l11l1l1l_opy_(self.caps, options, desired_capabilities):
    if CONFIG[bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧો")][bstack1ll_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬૌ")] == True:
      threading.current_thread().appA11yPlatform = True
      if cli.accessibility is None or not cli.accessibility.is_enabled():
        bstack1l11llll1l_opy_.set_capabilities(bstack1lll11ll1_opy_, CONFIG)
  try:
    bstack1lllll1ll_opy_ = bstack1ll_opy_ (u"ࠧࠨ્")
    if bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࡢ࠲ࠩ૎")):
      if self.caps is not None:
        bstack1lllll1ll_opy_ = self.caps.get(bstack1ll_opy_ (u"ࠤࡲࡴࡹ࡯࡭ࡢ࡮ࡋࡹࡧ࡛ࡲ࡭ࠤ૏"))
    else:
      if self.capabilities is not None:
        bstack1lllll1ll_opy_ = self.capabilities.get(bstack1ll_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥૐ"))
    if bstack1lllll1ll_opy_:
      bstack1l1l11ll11_opy_(bstack1lllll1ll_opy_)
      if bstack11l111ll1_opy_() <= version.parse(bstack1ll_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫ૑")):
        self.command_executor._url = bstack1ll_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨ૒") + bstack11llll1l1_opy_ + bstack1ll_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥ૓")
      else:
        self.command_executor._url = bstack1ll_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤ૔") + bstack1lllll1ll_opy_ + bstack1ll_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤ૕")
      logger.debug(bstack1l11ll11l_opy_.format(bstack1lllll1ll_opy_))
    else:
      logger.debug(bstack111lll1l_opy_.format(bstack1ll_opy_ (u"ࠤࡒࡴࡹ࡯࡭ࡢ࡮ࠣࡌࡺࡨࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦࠥ૖")))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_.format(e))
  if bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ૗") in bstack11ll1l1lll_opy_:
    bstack1ll1l1lll_opy_(bstack1l1111ll_opy_, bstack1l111ll11_opy_)
  bstack1l1111l11l_opy_ = self.session_id
  if bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ૘") in bstack11ll1l1lll_opy_ or bstack1ll_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ૙") in bstack11ll1l1lll_opy_ or bstack1ll_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ૚") in bstack11ll1l1lll_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1l11ll11l1_opy_ = getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡔࡦࡵࡷࡑࡪࡺࡡࠨ૛"), None)
  if bstack1ll_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ૜") in bstack11ll1l1lll_opy_ or bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ૝") in bstack11ll1l1lll_opy_:
    bstack1l111111_opy_.bstack11lll11ll_opy_(self)
  if bstack1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ૞") in bstack11ll1l1lll_opy_ and bstack1l11ll11l1_opy_ and bstack1l11ll11l1_opy_.get(bstack1ll_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ૟"), bstack1ll_opy_ (u"ࠬ࠭ૠ")) == bstack1ll_opy_ (u"࠭ࡰࡦࡰࡧ࡭ࡳ࡭ࠧૡ"):
    bstack1l111111_opy_.bstack11lll11ll_opy_(self)
  bstack1llll1lll_opy_.append(self)
  if bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪૢ") in CONFIG and bstack1ll_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ૣ") in CONFIG[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ૤")][bstack1l1ll1ll11_opy_]:
    bstack1lll1lllll_opy_ = CONFIG[bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭૥")][bstack1l1ll1ll11_opy_][bstack1ll_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ૦")]
  logger.debug(bstack1l111l1ll_opy_.format(bstack1l1111l11l_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack111l11ll_opy_
    def bstack1l1l1l11_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l111lll11_opy_
      if(bstack1ll_opy_ (u"ࠧ࡯࡮ࡥࡧࡻ࠲࡯ࡹࠢ૧") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1ll_opy_ (u"࠭ࡾࠨ૨")), bstack1ll_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ૩"), bstack1ll_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ૪")), bstack1ll_opy_ (u"ࠩࡺࠫ૫")) as fp:
          fp.write(bstack1ll_opy_ (u"ࠥࠦ૬"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1ll_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨ૭")))):
          with open(args[1], bstack1ll_opy_ (u"ࠬࡸࠧ૮")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1ll_opy_ (u"࠭ࡡࡴࡻࡱࡧࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡠࡰࡨࡻࡕࡧࡧࡦࠪࡦࡳࡳࡺࡥࡹࡶ࠯ࠤࡵࡧࡧࡦࠢࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠬ૯") in line), None)
            if index is not None:
                lines.insert(index+2, bstack1l1ll1l1l1_opy_)
            if bstack1ll_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ૰") in CONFIG and str(CONFIG[bstack1ll_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ૱")]).lower() != bstack1ll_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ૲"):
                bstack11l11llll_opy_ = bstack111l11ll_opy_()
                bstack11llll1l_opy_ = bstack1ll_opy_ (u"ࠪࠫࠬࠐ࠯ࠫࠢࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࠦࠪ࠰ࠌࡦࡳࡳࡹࡴࠡࡤࡶࡸࡦࡩ࡫ࡠࡲࡤࡸ࡭ࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࡛ࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴࡬ࡦࡰࡪࡸ࡭ࠦ࠭ࠡ࠵ࡠ࠿ࠏࡩ࡯࡯ࡵࡷࠤࡧࡹࡴࡢࡥ࡮ࡣࡨࡧࡰࡴࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠶ࡣ࠻ࠋࡥࡲࡲࡸࡺࠠࡱࡡ࡬ࡲࡩ࡫ࡸࠡ࠿ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࡝ࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯࡮ࡨࡲ࡬ࡺࡨࠡ࠯ࠣ࠶ࡢࡁࠊࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࠦ࠽ࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮ࡴ࡮࡬ࡧࡪ࠮࠰࠭ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯࡮ࡨࡲ࡬ࡺࡨࠡ࠯ࠣ࠷࠮ࡁࠊࡤࡱࡱࡷࡹࠦࡩ࡮ࡲࡲࡶࡹࡥࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶ࠷ࡣࡧࡹࡴࡢࡥ࡮ࠤࡂࠦࡲࡦࡳࡸ࡭ࡷ࡫ࠨࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧ࠯࠻ࠋ࡫ࡰࡴࡴࡸࡴࡠࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ࠹ࡥࡢࡴࡶࡤࡧࡰ࠴ࡣࡩࡴࡲࡱ࡮ࡻ࡭࠯࡮ࡤࡹࡳࡩࡨࠡ࠿ࠣࡥࡸࡿ࡮ࡤࠢࠫࡰࡦࡻ࡮ࡤࡪࡒࡴࡹ࡯࡯࡯ࡵࠬࠤࡂࡄࠠࡼࡽࠍࠤࠥࡲࡥࡵࠢࡦࡥࡵࡹ࠻ࠋࠢࠣࡸࡷࡿࠠࡼࡽࠍࠤࠥࠦࠠࡤࡣࡳࡷࠥࡃࠠࡋࡕࡒࡒ࠳ࡶࡡࡳࡵࡨࠬࡧࡹࡴࡢࡥ࡮ࡣࡨࡧࡰࡴࠫ࠾ࠎࠥࠦࡽࡾࠢࡦࡥࡹࡩࡨࠡࠪࡨࡼ࠮ࠦࡻࡼࠌࠣࠤࠥࠦࡣࡰࡰࡶࡳࡱ࡫࠮ࡦࡴࡵࡳࡷ࠮ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳ࠻ࠤ࠯ࠤࡪࡾࠩ࠼ࠌࠣࠤࢂࢃࠊࠡࠢࡵࡩࡹࡻࡲ࡯ࠢࡤࡻࡦ࡯ࡴࠡ࡫ࡰࡴࡴࡸࡴࡠࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ࠹ࡥࡢࡴࡶࡤࡧࡰ࠴ࡣࡩࡴࡲࡱ࡮ࡻ࡭࠯ࡥࡲࡲࡳ࡫ࡣࡵࠪࡾࡿࠏࠦࠠࠡࠢࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹࡀࠠࠨࡽࡦࡨࡵ࡛ࡲ࡭ࡿࠪࠤ࠰ࠦࡥ࡯ࡥࡲࡨࡪ࡛ࡒࡊࡅࡲࡱࡵࡵ࡮ࡦࡰࡷࠬࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡩࡡࡱࡵࠬ࠭࠱ࠐࠠࠡࠢࠣ࠲࠳࠴࡬ࡢࡷࡱࡧ࡭ࡕࡰࡵ࡫ࡲࡲࡸࠐࠠࠡࡿࢀ࠭ࡀࠐࡽࡾ࠽ࠍ࠳࠯ࠦ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࠣ࠮࠴ࠐࠧࠨࠩ૳").format(bstack11l11llll_opy_=bstack11l11llll_opy_)
            lines.insert(1, bstack11llll1l_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1ll_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨ૴")), bstack1ll_opy_ (u"ࠬࡽࠧ૵")) as bstack11lll111_opy_:
              bstack11lll111_opy_.writelines(lines)
        CONFIG[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨ૶")] = str(bstack11ll1l1lll_opy_) + str(__version__)
        bstack1l1llllll1_opy_ = os.environ[bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ૷")]
        bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(CONFIG, bstack11ll1l1lll_opy_)
        CONFIG[bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹ࡮ࡵࡣࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫ૸")] = bstack1l1llllll1_opy_
        CONFIG[bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫૹ")] = bstack1ll1111l_opy_
        bstack1l1ll1ll11_opy_ = 0 if bstack1l1111ll_opy_ < 0 else bstack1l1111ll_opy_
        try:
          if bstack11l11llll1_opy_ is True:
            bstack1l1ll1ll11_opy_ = int(multiprocessing.current_process().name)
          elif bstack1l1lll1111_opy_ is True:
            bstack1l1ll1ll11_opy_ = int(threading.current_thread().name)
        except:
          bstack1l1ll1ll11_opy_ = 0
        CONFIG[bstack1ll_opy_ (u"ࠥࡹࡸ࡫ࡗ࠴ࡅࠥૺ")] = False
        CONFIG[bstack1ll_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥૻ")] = True
        bstack1lll11ll1_opy_ = bstack1lll1llll_opy_(CONFIG, bstack1l1ll1ll11_opy_)
        logger.debug(bstack111l1llll_opy_.format(str(bstack1lll11ll1_opy_)))
        if CONFIG.get(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩૼ")):
          bstack1l1ll1l11l_opy_(bstack1lll11ll1_opy_)
        if bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ૽") in CONFIG and bstack1ll_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ૾") in CONFIG[bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૿")][bstack1l1ll1ll11_opy_]:
          bstack1lll1lllll_opy_ = CONFIG[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଀")][bstack1l1ll1ll11_opy_][bstack1ll_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨଁ")]
        args.append(os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠫࢃ࠭ଂ")), bstack1ll_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬଃ"), bstack1ll_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨ଄")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack1lll11ll1_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1ll_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤଅ"))
      bstack1l111lll11_opy_ = True
      return bstack111lllll_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1lllll1111_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1l1111ll_opy_
    global bstack1lll1lllll_opy_
    global bstack11l11llll1_opy_
    global bstack1l1lll1111_opy_
    global bstack11ll1l1lll_opy_
    CONFIG[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪଆ")] = str(bstack11ll1l1lll_opy_) + str(__version__)
    bstack1l1llllll1_opy_ = os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧଇ")]
    bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(CONFIG, bstack11ll1l1lll_opy_)
    CONFIG[bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ଈ")] = bstack1l1llllll1_opy_
    CONFIG[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡓࡶࡴࡪࡵࡤࡶࡐࡥࡵ࠭ଉ")] = bstack1ll1111l_opy_
    bstack1l1ll1ll11_opy_ = 0 if bstack1l1111ll_opy_ < 0 else bstack1l1111ll_opy_
    try:
      if bstack11l11llll1_opy_ is True:
        bstack1l1ll1ll11_opy_ = int(multiprocessing.current_process().name)
      elif bstack1l1lll1111_opy_ is True:
        bstack1l1ll1ll11_opy_ = int(threading.current_thread().name)
    except:
      bstack1l1ll1ll11_opy_ = 0
    CONFIG[bstack1ll_opy_ (u"ࠧ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦଊ")] = True
    bstack1lll11ll1_opy_ = bstack1lll1llll_opy_(CONFIG, bstack1l1ll1ll11_opy_)
    logger.debug(bstack111l1llll_opy_.format(str(bstack1lll11ll1_opy_)))
    if CONFIG.get(bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪଋ")):
      bstack1l1ll1l11l_opy_(bstack1lll11ll1_opy_)
    if bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଌ") in CONFIG and bstack1ll_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭଍") in CONFIG[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଎")][bstack1l1ll1ll11_opy_]:
      bstack1lll1lllll_opy_ = CONFIG[bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଏ")][bstack1l1ll1ll11_opy_][bstack1ll_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩଐ")]
    import urllib
    import json
    if bstack1ll_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ଑") in CONFIG and str(CONFIG[bstack1ll_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ଒")]).lower() != bstack1ll_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ଓ"):
        bstack1ll1l1l1l1_opy_ = bstack111l11ll_opy_()
        bstack11l11llll_opy_ = bstack1ll1l1l1l1_opy_ + urllib.parse.quote(json.dumps(bstack1lll11ll1_opy_))
    else:
        bstack11l11llll_opy_ = bstack1ll_opy_ (u"ࠨࡹࡶࡷ࠿࠵࠯ࡤࡦࡳ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࡃࡨࡧࡰࡴ࠿ࠪଔ") + urllib.parse.quote(json.dumps(bstack1lll11ll1_opy_))
    browser = self.connect(bstack11l11llll_opy_)
    return browser
except Exception as e:
    pass
def bstack1l1l1lll11_opy_():
    global bstack1l111lll11_opy_
    global bstack11ll1l1lll_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack1lll1l1lll_opy_
        global bstack1lll1111ll_opy_
        if not bstack1lllll11_opy_:
          global bstack1l111l11ll_opy_
          if not bstack1l111l11ll_opy_:
            from bstack_utils.helper import bstack11llll111l_opy_, bstack11l11l11_opy_, bstack1l11lll11l_opy_
            bstack1l111l11ll_opy_ = bstack11llll111l_opy_()
            bstack11l11l11_opy_(bstack11ll1l1lll_opy_)
            bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(CONFIG, bstack11ll1l1lll_opy_)
            bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠤࡓࡐࡆ࡟ࡗࡓࡋࡊࡌ࡙ࡥࡐࡓࡑࡇ࡙ࡈ࡚࡟ࡎࡃࡓࠦକ"), bstack1ll1111l_opy_)
          BrowserType.connect = bstack1lll1l1lll_opy_
          return
        BrowserType.launch = bstack1lllll1111_opy_
        bstack1l111lll11_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1l1l1l11_opy_
      bstack1l111lll11_opy_ = True
    except Exception as e:
      pass
def bstack11llll11_opy_(context, bstack11ll11l1l_opy_):
  try:
    context.page.evaluate(bstack1ll_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦଖ"), bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨଗ")+ json.dumps(bstack11ll11l1l_opy_) + bstack1ll_opy_ (u"ࠧࢃࡽࠣଘ"))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀ࠾ࠥࢁࡽࠣଙ").format(str(e), traceback.format_exc()))
def bstack11l1l1111_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1ll_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣଚ"), bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ଛ") + json.dumps(message) + bstack1ll_opy_ (u"ࠩ࠯ࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠬଜ") + json.dumps(level) + bstack1ll_opy_ (u"ࠪࢁࢂ࠭ଝ"))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࢀࢃ࠺ࠡࡽࢀࠦଞ").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack111l11ll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack11l1l1ll1l_opy_(self, url):
  global bstack11llll11l1_opy_
  try:
    bstack11lll111ll_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1l1l1l_opy_.format(str(err)))
  try:
    bstack11llll11l1_opy_(self, url)
  except Exception as e:
    try:
      bstack1l11l11l_opy_ = str(e)
      if any(err_msg in bstack1l11l11l_opy_ for err_msg in bstack1l1l11111_opy_):
        bstack11lll111ll_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1l1l1l_opy_.format(str(err)))
    raise e
def bstack1lll11ll_opy_(self):
  global bstack1l111lll1_opy_
  bstack1l111lll1_opy_ = self
  return
def bstack1ll1l11l11_opy_(self):
  global bstack1111111l1_opy_
  bstack1111111l1_opy_ = self
  return
def bstack1lll11l1l_opy_(test_name, bstack111l111l_opy_):
  global CONFIG
  if percy.bstack1ll1ll11l1_opy_() == bstack1ll_opy_ (u"ࠧࡺࡲࡶࡧࠥଟ"):
    bstack11lll11l1l_opy_ = os.path.relpath(bstack111l111l_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack11lll11l1l_opy_)
    bstack1lll11l11_opy_ = suite_name + bstack1ll_opy_ (u"ࠨ࠭ࠣଠ") + test_name
    threading.current_thread().percySessionName = bstack1lll11l11_opy_
def bstack11ll1l1111_opy_(self, test, *args, **kwargs):
  global bstack1lllllll11_opy_
  test_name = None
  bstack111l111l_opy_ = None
  if test:
    test_name = str(test.name)
    bstack111l111l_opy_ = str(test.source)
  bstack1lll11l1l_opy_(test_name, bstack111l111l_opy_)
  bstack1lllllll11_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack11l11lll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack11ll111l1l_opy_(driver, bstack1lll11l11_opy_):
  if not bstack11l111l1l1_opy_ and bstack1lll11l11_opy_:
      bstack1l11l11lll_opy_ = {
          bstack1ll_opy_ (u"ࠧࡢࡥࡷ࡭ࡴࡴࠧଡ"): bstack1ll_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩଢ"),
          bstack1ll_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬଣ"): {
              bstack1ll_opy_ (u"ࠪࡲࡦࡳࡥࠨତ"): bstack1lll11l11_opy_
          }
      }
      bstack1lllll11l_opy_ = bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠩଥ").format(json.dumps(bstack1l11l11lll_opy_))
      driver.execute_script(bstack1lllll11l_opy_)
  if bstack1l1lll11_opy_:
      bstack11l1l1l1ll_opy_ = {
          bstack1ll_opy_ (u"ࠬࡧࡣࡵ࡫ࡲࡲࠬଦ"): bstack1ll_opy_ (u"࠭ࡡ࡯ࡰࡲࡸࡦࡺࡥࠨଧ"),
          bstack1ll_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪନ"): {
              bstack1ll_opy_ (u"ࠨࡦࡤࡸࡦ࠭଩"): bstack1lll11l11_opy_ + bstack1ll_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫପ"),
              bstack1ll_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩଫ"): bstack1ll_opy_ (u"ࠫ࡮ࡴࡦࡰࠩବ")
          }
      }
      if bstack1l1lll11_opy_.status == bstack1ll_opy_ (u"ࠬࡖࡁࡔࡕࠪଭ"):
          bstack111l1ll1_opy_ = bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫମ").format(json.dumps(bstack11l1l1l1ll_opy_))
          driver.execute_script(bstack111l1ll1_opy_)
          bstack11llll111_opy_(driver, bstack1ll_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧଯ"))
      elif bstack1l1lll11_opy_.status == bstack1ll_opy_ (u"ࠨࡈࡄࡍࡑ࠭ର"):
          reason = bstack1ll_opy_ (u"ࠤࠥ଱")
          bstack1ll111l1ll_opy_ = bstack1lll11l11_opy_ + bstack1ll_opy_ (u"ࠪࠤ࡫ࡧࡩ࡭ࡧࡧࠫଲ")
          if bstack1l1lll11_opy_.message:
              reason = str(bstack1l1lll11_opy_.message)
              bstack1ll111l1ll_opy_ = bstack1ll111l1ll_opy_ + bstack1ll_opy_ (u"ࠫࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠫଳ") + reason
          bstack11l1l1l1ll_opy_[bstack1ll_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ଴")] = {
              bstack1ll_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬଵ"): bstack1ll_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ଶ"),
              bstack1ll_opy_ (u"ࠨࡦࡤࡸࡦ࠭ଷ"): bstack1ll111l1ll_opy_
          }
          bstack111l1ll1_opy_ = bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧସ").format(json.dumps(bstack11l1l1l1ll_opy_))
          driver.execute_script(bstack111l1ll1_opy_)
          bstack11llll111_opy_(driver, bstack1ll_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪହ"), reason)
          bstack1l1l111ll1_opy_(reason, str(bstack1l1lll11_opy_), str(bstack1l1111ll_opy_), logger)
@measure(event_name=EVENTS.bstack1llll11111_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1lll1l1l1_opy_(driver, test):
  if percy.bstack1ll1ll11l1_opy_() == bstack1ll_opy_ (u"ࠦࡹࡸࡵࡦࠤ଺") and percy.bstack1l1l1111_opy_() == bstack1ll_opy_ (u"ࠧࡺࡥࡴࡶࡦࡥࡸ࡫ࠢ଻"):
      bstack11l1ll1l1_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡰࡦࡴࡦࡽࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦ଼ࠩ"), None)
      bstack1l1ll111l1_opy_(driver, bstack11l1ll1l1_opy_, test)
  if (bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫଽ"), None) and
      bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧା"), None)) or (
      bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩି"), None) and
      bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬୀ"), None)):
      logger.info(bstack1ll_opy_ (u"ࠦࡆࡻࡴࡰ࡯ࡤࡸࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡨࡼࡪࡩࡵࡵ࡫ࡲࡲࠥ࡮ࡡࡴࠢࡨࡲࡩ࡫ࡤ࠯ࠢࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡮ࡹࠠࡶࡰࡧࡩࡷࡽࡡࡺ࠰ࠣࠦୁ"))
      bstack1l11llll1l_opy_.bstack1ll11111l_opy_(driver, name=test.name, path=test.source)
def bstack1llll11l1_opy_(test, bstack1lll11l11_opy_):
    try:
      bstack1lll1ll11_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪୂ")] = bstack1lll11l11_opy_
      if bstack1l1lll11_opy_:
        if bstack1l1lll11_opy_.status == bstack1ll_opy_ (u"࠭ࡐࡂࡕࡖࠫୃ"):
          data[bstack1ll_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧୄ")] = bstack1ll_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ୅")
        elif bstack1l1lll11_opy_.status == bstack1ll_opy_ (u"ࠩࡉࡅࡎࡒࠧ୆"):
          data[bstack1ll_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪେ")] = bstack1ll_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫୈ")
          if bstack1l1lll11_opy_.message:
            data[bstack1ll_opy_ (u"ࠬࡸࡥࡢࡵࡲࡲࠬ୉")] = str(bstack1l1lll11_opy_.message)
      user = CONFIG[bstack1ll_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨ୊")]
      key = CONFIG[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪୋ")]
      url = bstack1ll_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠴ࢁࡽ࠯࡬ࡶࡳࡳ࠭ୌ").format(user, key, bstack1l1111l11l_opy_)
      headers = {
        bstack1ll_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨ୍"): bstack1ll_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭୎"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
        cli.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼ࡸࡴࡩࡧࡴࡦࡡࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡷࡥࡹࡻࡳࠣ୏"), datetime.datetime.now() - bstack1lll1ll11_opy_)
    except Exception as e:
      logger.error(bstack1ll1l1l1l_opy_.format(str(e)))
def bstack1llll1lll1_opy_(test, bstack1lll11l11_opy_):
  global CONFIG
  global bstack1111111l1_opy_
  global bstack1l111lll1_opy_
  global bstack1l1111l11l_opy_
  global bstack1l1lll11_opy_
  global bstack1lll1lllll_opy_
  global bstack1l1ll11lll_opy_
  global bstack1lllll111_opy_
  global bstack1lll1l11l_opy_
  global bstack1l1ll111_opy_
  global bstack1llll1lll_opy_
  global bstack1l1llll111_opy_
  try:
    if not bstack1l1111l11l_opy_:
      with open(os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠬࢄࠧ୐")), bstack1ll_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭୑"), bstack1ll_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩ୒"))) as f:
        bstack11llll11l_opy_ = json.loads(bstack1ll_opy_ (u"ࠣࡽࠥ୓") + f.read().strip() + bstack1ll_opy_ (u"ࠩࠥࡼࠧࡀࠠࠣࡻࠥࠫ୔") + bstack1ll_opy_ (u"ࠥࢁࠧ୕"))
        bstack1l1111l11l_opy_ = bstack11llll11l_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1llll1lll_opy_:
    for driver in bstack1llll1lll_opy_:
      if bstack1l1111l11l_opy_ == driver.session_id:
        if test:
          bstack1lll1l1l1_opy_(driver, test)
        bstack11ll111l1l_opy_(driver, bstack1lll11l11_opy_)
  elif bstack1l1111l11l_opy_:
    bstack1llll11l1_opy_(test, bstack1lll11l11_opy_)
  if bstack1111111l1_opy_:
    bstack1lllll111_opy_(bstack1111111l1_opy_)
  if bstack1l111lll1_opy_:
    bstack1lll1l11l_opy_(bstack1l111lll1_opy_)
  if bstack1l11l1l1l1_opy_:
    bstack1l1ll111_opy_()
def bstack1llllllll1_opy_(self, test, *args, **kwargs):
  bstack1lll11l11_opy_ = None
  if test:
    bstack1lll11l11_opy_ = str(test.name)
  bstack1llll1lll1_opy_(test, bstack1lll11l11_opy_)
  bstack1l1ll11lll_opy_(self, test, *args, **kwargs)
def bstack111lll111_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack111l11l1_opy_
  global CONFIG
  global bstack1llll1lll_opy_
  global bstack1l1111l11l_opy_
  bstack1ll1l11111_opy_ = None
  try:
    if bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪୖ"), None) or bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠬࡧࡰࡱࡃ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧୗ"), None):
      try:
        if not bstack1l1111l11l_opy_:
          with open(os.path.join(os.path.expanduser(bstack1ll_opy_ (u"࠭ࡾࠨ୘")), bstack1ll_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ୙"), bstack1ll_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪ୚"))) as f:
            bstack11llll11l_opy_ = json.loads(bstack1ll_opy_ (u"ࠤࡾࠦ୛") + f.read().strip() + bstack1ll_opy_ (u"ࠪࠦࡽࠨ࠺ࠡࠤࡼࠦࠬଡ଼") + bstack1ll_opy_ (u"ࠦࢂࠨଢ଼"))
            bstack1l1111l11l_opy_ = bstack11llll11l_opy_[str(threading.get_ident())]
      except:
        pass
      if bstack1llll1lll_opy_:
        for driver in bstack1llll1lll_opy_:
          if bstack1l1111l11l_opy_ == driver.session_id:
            bstack1ll1l11111_opy_ = driver
    bstack11ll111111_opy_ = bstack1l11llll1l_opy_.bstack11l11lll_opy_(test.tags)
    if bstack1ll1l11111_opy_:
      threading.current_thread().isA11yTest = bstack1l11llll1l_opy_.bstack11ll11llll_opy_(bstack1ll1l11111_opy_, bstack11ll111111_opy_)
      threading.current_thread().isAppA11yTest = bstack1l11llll1l_opy_.bstack11ll11llll_opy_(bstack1ll1l11111_opy_, bstack11ll111111_opy_)
    else:
      threading.current_thread().isA11yTest = bstack11ll111111_opy_
      threading.current_thread().isAppA11yTest = bstack11ll111111_opy_
  except:
    pass
  bstack111l11l1_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1l1lll11_opy_
  try:
    bstack1l1lll11_opy_ = self._test
  except:
    bstack1l1lll11_opy_ = self.test
def bstack11lll1111_opy_():
  global bstack1l11111l_opy_
  try:
    if os.path.exists(bstack1l11111l_opy_):
      os.remove(bstack1l11111l_opy_)
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡵࡳࡧࡵࡴࠡࡴࡨࡴࡴࡸࡴࠡࡨ࡬ࡰࡪࡀࠠࠨ୞") + str(e))
def bstack11ll1ll111_opy_():
  global bstack1l11111l_opy_
  bstack111lllll1_opy_ = {}
  try:
    if not os.path.isfile(bstack1l11111l_opy_):
      with open(bstack1l11111l_opy_, bstack1ll_opy_ (u"࠭ࡷࠨୟ")):
        pass
      with open(bstack1l11111l_opy_, bstack1ll_opy_ (u"ࠢࡸ࠭ࠥୠ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1l11111l_opy_):
      bstack111lllll1_opy_ = json.load(open(bstack1l11111l_opy_, bstack1ll_opy_ (u"ࠨࡴࡥࠫୡ")))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡷ࡫ࡡࡥ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫୢ") + str(e))
  finally:
    return bstack111lllll1_opy_
def bstack1ll1l1lll_opy_(platform_index, item_index):
  global bstack1l11111l_opy_
  try:
    bstack111lllll1_opy_ = bstack11ll1ll111_opy_()
    bstack111lllll1_opy_[item_index] = platform_index
    with open(bstack1l11111l_opy_, bstack1ll_opy_ (u"ࠥࡻ࠰ࠨୣ")) as outfile:
      json.dump(bstack111lllll1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡷࡳ࡫ࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠢࡩ࡭ࡱ࡫࠺ࠡࠩ୤") + str(e))
def bstack1111ll11_opy_(bstack1l1lll1ll1_opy_):
  global CONFIG
  bstack1lll1ll1ll_opy_ = bstack1ll_opy_ (u"ࠬ࠭୥")
  if not bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ୦") in CONFIG:
    logger.info(bstack1ll_opy_ (u"ࠧࡏࡱࠣࡴࡱࡧࡴࡧࡱࡵࡱࡸࠦࡰࡢࡵࡶࡩࡩࠦࡵ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡪࡩࡳ࡫ࡲࡢࡶࡨࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫ࡵࡲࠡࡔࡲࡦࡴࡺࠠࡳࡷࡱࠫ୧"))
  try:
    platform = CONFIG[bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ୨")][bstack1l1lll1ll1_opy_]
    if bstack1ll_opy_ (u"ࠩࡲࡷࠬ୩") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"ࠪࡳࡸ࠭୪")]) + bstack1ll_opy_ (u"ࠫ࠱ࠦࠧ୫")
    if bstack1ll_opy_ (u"ࠬࡵࡳࡗࡧࡵࡷ࡮ࡵ࡮ࠨ୬") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩ୭")]) + bstack1ll_opy_ (u"ࠧ࠭ࠢࠪ୮")
    if bstack1ll_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬ୯") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭୰")]) + bstack1ll_opy_ (u"ࠪ࠰ࠥ࠭ୱ")
    if bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭୲") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ୳")]) + bstack1ll_opy_ (u"࠭ࠬࠡࠩ୴")
    if bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ୵") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭୶")]) + bstack1ll_opy_ (u"ࠩ࠯ࠤࠬ୷")
    if bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ୸") in platform:
      bstack1lll1ll1ll_opy_ += str(platform[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬ୹")]) + bstack1ll_opy_ (u"ࠬ࠲ࠠࠨ୺")
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"࠭ࡓࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠣ࡭ࡳࠦࡧࡦࡰࡨࡶࡦࡺࡩ࡯ࡩࠣࡴࡱࡧࡴࡧࡱࡵࡱࠥࡹࡴࡳ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡵࡩࡵࡵࡲࡵࠢࡪࡩࡳ࡫ࡲࡢࡶ࡬ࡳࡳ࠭୻") + str(e))
  finally:
    if bstack1lll1ll1ll_opy_[len(bstack1lll1ll1ll_opy_) - 2:] == bstack1ll_opy_ (u"ࠧ࠭ࠢࠪ୼"):
      bstack1lll1ll1ll_opy_ = bstack1lll1ll1ll_opy_[:-2]
    return bstack1lll1ll1ll_opy_
def bstack1l1llllll_opy_(path, bstack1lll1ll1ll_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1lll1111_opy_ = ET.parse(path)
    bstack11ll1ll11l_opy_ = bstack1lll1111_opy_.getroot()
    bstack1ll1l11ll_opy_ = None
    for suite in bstack11ll1ll11l_opy_.iter(bstack1ll_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ୽")):
      if bstack1ll_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ୾") in suite.attrib:
        suite.attrib[bstack1ll_opy_ (u"ࠪࡲࡦࡳࡥࠨ୿")] += bstack1ll_opy_ (u"ࠫࠥ࠭஀") + bstack1lll1ll1ll_opy_
        bstack1ll1l11ll_opy_ = suite
    bstack11ll1l11ll_opy_ = None
    for robot in bstack11ll1ll11l_opy_.iter(bstack1ll_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ஁")):
      bstack11ll1l11ll_opy_ = robot
    bstack11ll11ll_opy_ = len(bstack11ll1l11ll_opy_.findall(bstack1ll_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬஂ")))
    if bstack11ll11ll_opy_ == 1:
      bstack11ll1l11ll_opy_.remove(bstack11ll1l11ll_opy_.findall(bstack1ll_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭ஃ"))[0])
      bstack111l1l11_opy_ = ET.Element(bstack1ll_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧ஄"), attrib={bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧஅ"): bstack1ll_opy_ (u"ࠪࡗࡺ࡯ࡴࡦࡵࠪஆ"), bstack1ll_opy_ (u"ࠫ࡮ࡪࠧஇ"): bstack1ll_opy_ (u"ࠬࡹ࠰ࠨஈ")})
      bstack11ll1l11ll_opy_.insert(1, bstack111l1l11_opy_)
      bstack1ll1l11l1_opy_ = None
      for suite in bstack11ll1l11ll_opy_.iter(bstack1ll_opy_ (u"࠭ࡳࡶ࡫ࡷࡩࠬஉ")):
        bstack1ll1l11l1_opy_ = suite
      bstack1ll1l11l1_opy_.append(bstack1ll1l11ll_opy_)
      bstack1l1l11l1l1_opy_ = None
      for status in bstack1ll1l11ll_opy_.iter(bstack1ll_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧஊ")):
        bstack1l1l11l1l1_opy_ = status
      bstack1ll1l11l1_opy_.append(bstack1l1l11l1l1_opy_)
    bstack1lll1111_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡴࡦࡸࡳࡪࡰࡪࠤࡼ࡮ࡩ࡭ࡧࠣ࡫ࡪࡴࡥࡳࡣࡷ࡭ࡳ࡭ࠠࡳࡱࡥࡳࡹࠦࡲࡦࡲࡲࡶࡹ࠭஋") + str(e))
def bstack1l1l1l11l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1lll1lll1_opy_
  global CONFIG
  if bstack1ll_opy_ (u"ࠤࡳࡽࡹ࡮࡯࡯ࡲࡤࡸ࡭ࠨ஌") in options:
    del options[bstack1ll_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡳࡥࡹ࡮ࠢ஍")]
  bstack1l1ll11ll1_opy_ = bstack11ll1ll111_opy_()
  for bstack1111lll11_opy_ in bstack1l1ll11ll1_opy_.keys():
    path = os.path.join(os.getcwd(), bstack1ll_opy_ (u"ࠫࡵࡧࡢࡰࡶࡢࡶࡪࡹࡵ࡭ࡶࡶࠫஎ"), str(bstack1111lll11_opy_), bstack1ll_opy_ (u"ࠬࡵࡵࡵࡲࡸࡸ࠳ࡾ࡭࡭ࠩஏ"))
    bstack1l1llllll_opy_(path, bstack1111ll11_opy_(bstack1l1ll11ll1_opy_[bstack1111lll11_opy_]))
  bstack11lll1111_opy_()
  return bstack1lll1lll1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1l1111111l_opy_(self, ff_profile_dir):
  global bstack1l1111llll_opy_
  if not ff_profile_dir:
    return None
  return bstack1l1111llll_opy_(self, ff_profile_dir)
def bstack1ll11ll1l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1lll11llll_opy_
  bstack11ll111ll1_opy_ = []
  if bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩஐ") in CONFIG:
    bstack11ll111ll1_opy_ = CONFIG[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ஑")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1ll_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࠤஒ")],
      pabot_args[bstack1ll_opy_ (u"ࠤࡹࡩࡷࡨ࡯ࡴࡧࠥஓ")],
      argfile,
      pabot_args.get(bstack1ll_opy_ (u"ࠥ࡬࡮ࡼࡥࠣஔ")),
      pabot_args[bstack1ll_opy_ (u"ࠦࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠢக")],
      platform[0],
      bstack1lll11llll_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1ll_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡦࡪ࡮ࡨࡷࠧ஖")] or [(bstack1ll_opy_ (u"ࠨࠢ஗"), None)]
    for platform in enumerate(bstack11ll111ll1_opy_)
  ]
def bstack11l111l1ll_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1l11l111ll_opy_=bstack1ll_opy_ (u"ࠧࠨ஘")):
  global bstack111l1lll1_opy_
  self.platform_index = platform_index
  self.bstack1lllllllll_opy_ = bstack1l11l111ll_opy_
  bstack111l1lll1_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1l111llll_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1l111l11l_opy_
  global bstack1l111lll1l_opy_
  bstack1ll11l11l_opy_ = copy.deepcopy(item)
  if not bstack1ll_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪங") in item.options:
    bstack1ll11l11l_opy_.options[bstack1ll_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫச")] = []
  bstack1ll11l1ll1_opy_ = bstack1ll11l11l_opy_.options[bstack1ll_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ஛")].copy()
  for v in bstack1ll11l11l_opy_.options[bstack1ll_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭ஜ")]:
    if bstack1ll_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫ஝") in v:
      bstack1ll11l1ll1_opy_.remove(v)
    if bstack1ll_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡉࡌࡊࡃࡕࡋࡘ࠭ஞ") in v:
      bstack1ll11l1ll1_opy_.remove(v)
    if bstack1ll_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫட") in v:
      bstack1ll11l1ll1_opy_.remove(v)
  bstack1ll11l1ll1_opy_.insert(0, bstack1ll_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞࠺ࡼࡿࠪ஠").format(bstack1ll11l11l_opy_.platform_index))
  bstack1ll11l1ll1_opy_.insert(0, bstack1ll_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡆࡈࡊࡑࡕࡃࡂࡎࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࡀࡻࡾࠩ஡").format(bstack1ll11l11l_opy_.bstack1lllllllll_opy_))
  bstack1ll11l11l_opy_.options[bstack1ll_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬ஢")] = bstack1ll11l1ll1_opy_
  if bstack1l111lll1l_opy_:
    bstack1ll11l11l_opy_.options[bstack1ll_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭ண")].insert(0, bstack1ll_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡈࡒࡉࡂࡔࡊࡗ࠿ࢁࡽࠨத").format(bstack1l111lll1l_opy_))
  return bstack1l111l11l_opy_(caller_id, datasources, is_last, bstack1ll11l11l_opy_, outs_dir)
def bstack111ll1l1_opy_(command, item_index):
  if bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ஥")):
    os.environ[bstack1ll_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨ஦")] = json.dumps(CONFIG[bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ஧")][item_index % bstack1ll1111ll1_opy_])
  global bstack1l111lll1l_opy_
  if bstack1l111lll1l_opy_:
    command[0] = command[0].replace(bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨந"), bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠯ࡶࡨࡰࠦࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠠ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽࠦࠧன") + str(
      item_index) + bstack1ll_opy_ (u"ࠫࠥ࠭ப") + bstack1l111lll1l_opy_, 1)
  else:
    command[0] = command[0].replace(bstack1ll_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫ஫"),
                                    bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡹࡤ࡬ࠢࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠣ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠢࠪ஬") + str(item_index), 1)
def bstack11111lll1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack11l1l111l_opy_
  bstack111ll1l1_opy_(command, item_index)
  return bstack11l1l111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack11lll1l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack11l1l111l_opy_
  bstack111ll1l1_opy_(command, item_index)
  return bstack11l1l111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1llll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack11l1l111l_opy_
  bstack111ll1l1_opy_(command, item_index)
  return bstack11l1l111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack1l11l1lll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start):
  global bstack11l1l111l_opy_
  bstack111ll1l1_opy_(command, item_index)
  return bstack11l1l111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout, sleep_before_start)
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack1l1111lll1_opy_(self, runner, quiet=False, capture=True):
  global bstack1llll1l1l_opy_
  bstack1l1l1ll11l_opy_ = bstack1llll1l1l_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack1ll_opy_ (u"ࠧࡦࡺࡦࡩࡵࡺࡩࡰࡰࡢࡥࡷࡸࠧ஭")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1ll_opy_ (u"ࠨࡧࡻࡧࡤࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࡠࡣࡵࡶࠬம")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack1l1l1ll11l_opy_
def bstack1ll1l1111l_opy_(runner, hook_name, context, element, bstack11lll1l11l_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack1llllllll_opy_.bstack11l1ll1l1l_opy_(hook_name, element)
    bstack11lll1l11l_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack1llllllll_opy_.bstack1lll1llll1_opy_(element)
      if hook_name not in [bstack1ll_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱ࠭ய"), bstack1ll_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡤࡰࡱ࠭ர")] and args and hasattr(args[0], bstack1ll_opy_ (u"ࠫࡪࡸࡲࡰࡴࡢࡱࡪࡹࡳࡢࡩࡨࠫற")):
        args[0].error_message = bstack1ll_opy_ (u"ࠬ࠭ல")
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢ࡫ࡥࡳࡪ࡬ࡦࠢ࡫ࡳࡴࡱࡳࠡ࡫ࡱࠤࡧ࡫ࡨࡢࡸࡨ࠾ࠥࢁࡽࠨள").format(str(e)))
@measure(event_name=EVENTS.bstack1l1l1l11l1_opy_, stage=STAGE.bstack1llll11lll_opy_, hook_type=bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࡁ࡭࡮ࠥழ"), bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1l1ll1l11_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    if runner.hooks.get(bstack1ll_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠧவ")).__name__ != bstack1ll_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࡥࡤࡦࡨࡤࡹࡱࡺ࡟ࡩࡱࡲ࡯ࠧஶ"):
      bstack1ll1l1111l_opy_(runner, name, context, runner, bstack11lll1l11l_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack11ll11111_opy_(bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩஷ")) else context.browser
      runner.driver_initialised = bstack1ll_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣஸ")
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡪࡲࡪࡸࡨࡶࠥ࡯࡮ࡪࡶ࡬ࡥࡱ࡯ࡳࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩ࠿ࠦࡻࡾࠩஹ").format(str(e)))
def bstack1ll1111111_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    bstack1ll1l1111l_opy_(runner, name, context, context.feature, bstack11lll1l11l_opy_, *args)
    try:
      if not bstack11l111l1l1_opy_:
        bstack1ll1l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11111_opy_(bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬ஺")) else context.browser
        if is_driver_active(bstack1ll1l11111_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣ஻")
          bstack11ll11l1l_opy_ = str(runner.feature.name)
          bstack11llll11_opy_(context, bstack11ll11l1l_opy_)
          bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭஼") + json.dumps(bstack11ll11l1l_opy_) + bstack1ll_opy_ (u"ࠩࢀࢁࠬ஽"))
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪா").format(str(e)))
def bstack1l11ll1ll1_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    if hasattr(context, bstack1ll_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ி")):
        bstack1llllllll_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack1ll_opy_ (u"ࠬࡹࡣࡦࡰࡤࡶ࡮ࡵࠧீ")) else context.feature
    bstack1ll1l1111l_opy_(runner, name, context, target, bstack11lll1l11l_opy_, *args)
@measure(event_name=EVENTS.bstack1l11ll11ll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1llll1111_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    if len(context.scenario.tags) == 0: bstack1llllllll_opy_.start_test(context)
    bstack1ll1l1111l_opy_(runner, name, context, context.scenario, bstack11lll1l11l_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack1111111l_opy_.bstack11l11lll11_opy_(context, *args)
    try:
      bstack1ll1l11111_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬு"), context.browser)
      if is_driver_active(bstack1ll1l11111_opy_):
        bstack1l111111_opy_.bstack11lll11ll_opy_(bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ூ"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack1ll_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠥ௃")
        if (not bstack11l111l1l1_opy_):
          scenario_name = args[0].name
          feature_name = bstack11ll11l1l_opy_ = str(runner.feature.name)
          bstack11ll11l1l_opy_ = feature_name + bstack1ll_opy_ (u"ࠩࠣ࠱ࠥ࠭௄") + scenario_name
          if runner.driver_initialised == bstack1ll_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ௅"):
            bstack11llll11_opy_(context, bstack11ll11l1l_opy_)
            bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩெ") + json.dumps(bstack11ll11l1l_opy_) + bstack1ll_opy_ (u"ࠬࢃࡽࠨே"))
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡩࡳࡧࡲࡪࡱ࠽ࠤࢀࢃࠧை").format(str(e)))
@measure(event_name=EVENTS.bstack1l1l1l11l1_opy_, stage=STAGE.bstack1llll11lll_opy_, hook_type=bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫ࡓࡵࡧࡳࠦ௉"), bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack111ll11l1_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    bstack1ll1l1111l_opy_(runner, name, context, args[0], bstack11lll1l11l_opy_, *args)
    try:
      bstack1ll1l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11111_opy_(bstack1ll_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧொ")) else context.browser
      if is_driver_active(bstack1ll1l11111_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack1ll_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢோ")
        bstack1llllllll_opy_.bstack11l1l11l1l_opy_(args[0])
        if runner.driver_initialised == bstack1ll_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣௌ"):
          feature_name = bstack11ll11l1l_opy_ = str(runner.feature.name)
          bstack11ll11l1l_opy_ = feature_name + bstack1ll_opy_ (u"ࠫࠥ࠳ࠠࠨ்") + context.scenario.name
          bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪ௎") + json.dumps(bstack11ll11l1l_opy_) + bstack1ll_opy_ (u"࠭ࡽࡾࠩ௏"))
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡸࡪࡶ࠺ࠡࡽࢀࠫௐ").format(str(e)))
@measure(event_name=EVENTS.bstack1l1l1l11l1_opy_, stage=STAGE.bstack1llll11lll_opy_, hook_type=bstack1ll_opy_ (u"ࠣࡣࡩࡸࡪࡸࡓࡵࡧࡳࠦ௑"), bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1lll111111_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
  bstack1llllllll_opy_.bstack1l1ll111l_opy_(args[0])
  try:
    bstack1l11llll11_opy_ = args[0].status.name
    bstack1ll1l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ௒") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack1ll1l11111_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack1ll_opy_ (u"ࠪ࡭ࡳࡹࡴࡦࡲࠪ௓")
        feature_name = bstack11ll11l1l_opy_ = str(runner.feature.name)
        bstack11ll11l1l_opy_ = feature_name + bstack1ll_opy_ (u"ࠫࠥ࠳ࠠࠨ௔") + context.scenario.name
        bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪ௕") + json.dumps(bstack11ll11l1l_opy_) + bstack1ll_opy_ (u"࠭ࡽࡾࠩ௖"))
    if str(bstack1l11llll11_opy_).lower() == bstack1ll_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧௗ"):
      bstack1l1l1lll1l_opy_ = bstack1ll_opy_ (u"ࠨࠩ௘")
      bstack11lllllll1_opy_ = bstack1ll_opy_ (u"ࠩࠪ௙")
      bstack111lll11_opy_ = bstack1ll_opy_ (u"ࠪࠫ௚")
      try:
        import traceback
        bstack1l1l1lll1l_opy_ = runner.exception.__class__.__name__
        bstack11lllll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11lllllll1_opy_ = bstack1ll_opy_ (u"ࠫࠥ࠭௛").join(bstack11lllll1l_opy_)
        bstack111lll11_opy_ = bstack11lllll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l111ll11l_opy_.format(str(e)))
      bstack1l1l1lll1l_opy_ += bstack111lll11_opy_
      bstack11l1l1111_opy_(context, json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦ௜") + str(bstack11lllllll1_opy_)),
                          bstack1ll_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ௝"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧ௞"):
        bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭௟"), None), bstack1ll_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤ௠"), bstack1l1l1lll1l_opy_)
        bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ௡") + json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠦࠥ࠳ࠠࡇࡣ࡬ࡰࡪࡪࠡ࡝ࡰࠥ௢") + str(bstack11lllllll1_opy_)) + bstack1ll_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬ௣"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦ௤"):
        bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ௥"), bstack1ll_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧ௦") + str(bstack1l1l1lll1l_opy_))
    else:
      bstack11l1l1111_opy_(context, bstack1ll_opy_ (u"ࠤࡓࡥࡸࡹࡥࡥࠣࠥ௧"), bstack1ll_opy_ (u"ࠥ࡭ࡳ࡬࡯ࠣ௨"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡺࡥࡱࠤ௩"):
        bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"ࠬࡶࡡࡨࡧࠪ௪"), None), bstack1ll_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨ௫"))
      bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬ௬") + json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠣࠢ࠰ࠤࡕࡧࡳࡴࡧࡧࠥࠧ௭")) + bstack1ll_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨ௮"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣ௯"):
        bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ௰"))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡ࡯ࡤࡶࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡴࡶࡤࡸࡺࡹࠠࡪࡰࠣࡥ࡫ࡺࡥࡳࠢࡶࡸࡪࡶ࠺ࠡࡽࢀࠫ௱").format(str(e)))
  bstack1ll1l1111l_opy_(runner, name, context, args[0], bstack11lll1l11l_opy_, *args)
@measure(event_name=EVENTS.bstack1l1111l1ll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack111l1ll1l_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
  bstack1llllllll_opy_.end_test(args[0])
  try:
    bstack1l111ll111_opy_ = args[0].status.name
    bstack1ll1l11111_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬ௲"), context.browser)
    bstack1111111l_opy_.bstack1lllll1ll1_opy_(bstack1ll1l11111_opy_)
    if str(bstack1l111ll111_opy_).lower() == bstack1ll_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ௳"):
      bstack1l1l1lll1l_opy_ = bstack1ll_opy_ (u"ࠨࠩ௴")
      bstack11lllllll1_opy_ = bstack1ll_opy_ (u"ࠩࠪ௵")
      bstack111lll11_opy_ = bstack1ll_opy_ (u"ࠪࠫ௶")
      try:
        import traceback
        bstack1l1l1lll1l_opy_ = runner.exception.__class__.__name__
        bstack11lllll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack11lllllll1_opy_ = bstack1ll_opy_ (u"ࠫࠥ࠭௷").join(bstack11lllll1l_opy_)
        bstack111lll11_opy_ = bstack11lllll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1l111ll11l_opy_.format(str(e)))
      bstack1l1l1lll1l_opy_ += bstack111lll11_opy_
      bstack11l1l1111_opy_(context, json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦ௸") + str(bstack11lllllll1_opy_)),
                          bstack1ll_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧ௹"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤ௺") or runner.driver_initialised == bstack1ll_opy_ (u"ࠨ࡫ࡱࡷࡹ࡫ࡰࠨ௻"):
        bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"ࠩࡳࡥ࡬࡫ࠧ௼"), None), bstack1ll_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ௽"), bstack1l1l1lll1l_opy_)
        bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩ௾") + json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦ௿") + str(bstack11lllllll1_opy_)) + bstack1ll_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭ఀ"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠤఁ") or runner.driver_initialised == bstack1ll_opy_ (u"ࠨ࡫ࡱࡷࡹ࡫ࡰࠨం"):
        bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩః"), bstack1ll_opy_ (u"ࠥࡗࡨ࡫࡮ࡢࡴ࡬ࡳࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡽࡩࡵࡪ࠽ࠤࡡࡴࠢఄ") + str(bstack1l1l1lll1l_opy_))
    else:
      bstack11l1l1111_opy_(context, bstack1ll_opy_ (u"ࠦࡕࡧࡳࡴࡧࡧࠥࠧఅ"), bstack1ll_opy_ (u"ࠧ࡯࡮ࡧࡱࠥఆ"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣఇ") or runner.driver_initialised == bstack1ll_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧఈ"):
        bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭ఉ"), None), bstack1ll_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤఊ"))
      bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨఋ") + json.dumps(str(args[0].name) + bstack1ll_opy_ (u"ࠦࠥ࠳ࠠࡑࡣࡶࡷࡪࡪࠡࠣఌ")) + bstack1ll_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ఍"))
      if runner.driver_initialised == bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣఎ") or runner.driver_initialised == bstack1ll_opy_ (u"ࠧࡪࡰࡶࡸࡪࡶࠧఏ"):
        bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠣࡲࡤࡷࡸ࡫ࡤࠣఐ"))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡳࡡࡳ࡭ࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤ࡮ࡴࠠࡢࡨࡷࡩࡷࠦࡦࡦࡣࡷࡹࡷ࡫࠺ࠡࡽࢀࠫ఑").format(str(e)))
  bstack1ll1l1111l_opy_(runner, name, context, context.scenario, bstack11lll1l11l_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1l11ll1lll_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    target = context.scenario if hasattr(context, bstack1ll_opy_ (u"ࠪࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠬఒ")) else context.feature
    bstack1ll1l1111l_opy_(runner, name, context, target, bstack11lll1l11l_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack1ll11l1l11_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    try:
      bstack1ll1l11111_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪఓ"), context.browser)
      bstack1l1l11l1ll_opy_ = bstack1ll_opy_ (u"ࠬ࠭ఔ")
      if context.failed is True:
        bstack1l11lll1l1_opy_ = []
        bstack11l111111_opy_ = []
        bstack11ll1l1l1l_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack1l11lll1l1_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack11lllll1l_opy_ = traceback.format_tb(exc_tb)
            bstack1ll11111_opy_ = bstack1ll_opy_ (u"࠭ࠠࠨక").join(bstack11lllll1l_opy_)
            bstack11l111111_opy_.append(bstack1ll11111_opy_)
            bstack11ll1l1l1l_opy_.append(bstack11lllll1l_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l111ll11l_opy_.format(str(e)))
        bstack1l1l1lll1l_opy_ = bstack1ll_opy_ (u"ࠧࠨఖ")
        for i in range(len(bstack1l11lll1l1_opy_)):
          bstack1l1l1lll1l_opy_ += bstack1l11lll1l1_opy_[i] + bstack11ll1l1l1l_opy_[i] + bstack1ll_opy_ (u"ࠨ࡞ࡱࠫగ")
        bstack1l1l11l1ll_opy_ = bstack1ll_opy_ (u"ࠩࠣࠫఘ").join(bstack11l111111_opy_)
        if runner.driver_initialised in [bstack1ll_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠦఙ"), bstack1ll_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣచ")]:
          bstack11l1l1111_opy_(context, bstack1l1l11l1ll_opy_, bstack1ll_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦఛ"))
          bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"࠭ࡰࡢࡩࡨࠫజ"), None), bstack1ll_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢఝ"), bstack1l1l1lll1l_opy_)
          bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ఞ") + json.dumps(bstack1l1l11l1ll_opy_) + bstack1ll_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࡽࡾࠩట"))
          bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥఠ"), bstack1ll_opy_ (u"ࠦࡘࡵ࡭ࡦࠢࡶࡧࡪࡴࡡࡳ࡫ࡲࡷࠥ࡬ࡡࡪ࡮ࡨࡨ࠿ࠦ࡜࡯ࠤడ") + str(bstack1l1l1lll1l_opy_))
          bstack1l1l1l1111_opy_ = bstack1l1l1l1l11_opy_(bstack1l1l11l1ll_opy_, runner.feature.name, logger)
          if (bstack1l1l1l1111_opy_ != None):
            bstack11l11l11l_opy_.append(bstack1l1l1l1111_opy_)
      else:
        if runner.driver_initialised in [bstack1ll_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪࠨఢ"), bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥణ")]:
          bstack11l1l1111_opy_(context, bstack1ll_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥ࠻ࠢࠥత") + str(runner.feature.name) + bstack1ll_opy_ (u"ࠣࠢࡳࡥࡸࡹࡥࡥࠣࠥథ"), bstack1ll_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢద"))
          bstack11l11ll111_opy_(getattr(context, bstack1ll_opy_ (u"ࠪࡴࡦ࡭ࡥࠨధ"), None), bstack1ll_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦన"))
          bstack1ll1l11111_opy_.execute_script(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡨࡦࡺࡡࠣ࠼ࠪ఩") + json.dumps(bstack1ll_opy_ (u"ࠨࡆࡦࡣࡷࡹࡷ࡫࠺ࠡࠤప") + str(runner.feature.name) + bstack1ll_opy_ (u"ࠢࠡࡲࡤࡷࡸ࡫ࡤࠢࠤఫ")) + bstack1ll_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧబ"))
          bstack11llll111_opy_(bstack1ll1l11111_opy_, bstack1ll_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩభ"))
          bstack1l1l1l1111_opy_ = bstack1l1l1l1l11_opy_(bstack1l1l11l1ll_opy_, runner.feature.name, logger)
          if (bstack1l1l1l1111_opy_ != None):
            bstack11l11l11l_opy_.append(bstack1l1l1l1111_opy_)
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬమ").format(str(e)))
    bstack1ll1l1111l_opy_(runner, name, context, context.feature, bstack11lll1l11l_opy_, *args)
@measure(event_name=EVENTS.bstack1l1l1l11l1_opy_, stage=STAGE.bstack1llll11lll_opy_, hook_type=bstack1ll_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࡄࡰࡱࠨయ"), bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack11ll1ll11_opy_(runner, name, context, bstack11lll1l11l_opy_, *args):
    bstack1ll1l1111l_opy_(runner, name, context, runner, bstack11lll1l11l_opy_, *args)
def bstack1llll1llll_opy_(self, name, context, *args):
  if bstack1lllll11_opy_:
    platform_index = int(threading.current_thread()._name) % bstack1ll1111ll1_opy_
    bstack1l1lllll11_opy_ = CONFIG[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨర")][platform_index]
    os.environ[bstack1ll_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧఱ")] = json.dumps(bstack1l1lllll11_opy_)
  global bstack11lll1l11l_opy_
  if not hasattr(self, bstack1ll_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡵࡨࡨࠬల")):
    self.driver_initialised = None
  bstack1ll11l1lll_opy_ = {
      bstack1ll_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡣ࡯ࡰࠬళ"): bstack1l1ll1l11_opy_,
      bstack1ll_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࡡࡩࡩࡦࡺࡵࡳࡧࠪఴ"): bstack1ll1111111_opy_,
      bstack1ll_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡸࡦ࡭ࠧవ"): bstack1l11ll1ll1_opy_,
      bstack1ll_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭శ"): bstack1llll1111_opy_,
      bstack1ll_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠪష"): bstack111ll11l1_opy_,
      bstack1ll_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡴࡦࡲࠪస"): bstack1lll111111_opy_,
      bstack1ll_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨహ"): bstack111l1ll1l_opy_,
      bstack1ll_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡵࡣࡪࠫ఺"): bstack1l11ll1lll_opy_,
      bstack1ll_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩ఻"): bstack1ll11l1l11_opy_,
      bstack1ll_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡤࡰࡱ఼࠭"): bstack11ll1ll11_opy_
  }
  handler = bstack1ll11l1lll_opy_.get(name, bstack11lll1l11l_opy_)
  handler(self, name, context, bstack11lll1l11l_opy_, *args)
  if name in [bstack1ll_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫఽ"), bstack1ll_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ా"), bstack1ll_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩి")]:
    try:
      bstack1ll1l11111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11111_opy_(bstack1ll_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭ీ")) else context.browser
      bstack1ll11l1ll_opy_ = (
        (name == bstack1ll_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡢ࡮࡯ࠫు") and self.driver_initialised == bstack1ll_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨూ")) or
        (name == bstack1ll_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪృ") and self.driver_initialised == bstack1ll_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣ࡫࡫ࡡࡵࡷࡵࡩࠧౄ")) or
        (name == bstack1ll_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭౅") and self.driver_initialised in [bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣె"), bstack1ll_opy_ (u"ࠢࡪࡰࡶࡸࡪࡶࠢే")]) or
        (name == bstack1ll_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡶࡨࡴࠬై") and self.driver_initialised == bstack1ll_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢ౉"))
      )
      if bstack1ll11l1ll_opy_:
        self.driver_initialised = None
        bstack1ll1l11111_opy_.quit()
    except Exception:
      pass
def bstack11lllll11l_opy_(config, startdir):
  return bstack1ll_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀ࠶ࡽࠣొ").format(bstack1ll_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥో"))
notset = Notset()
def bstack111llll1_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack11l1111l1_opy_
  if str(name).lower() == bstack1ll_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࠬౌ"):
    return bstack1ll_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯్ࠧ")
  else:
    return bstack11l1111l1_opy_(self, name, default, skip)
def bstack1llll11l_opy_(item, when):
  global bstack1l1l11l11_opy_
  try:
    bstack1l1l11l11_opy_(item, when)
  except Exception as e:
    pass
def bstack1lll11l111_opy_():
  return
def bstack11ll11l1ll_opy_(type, name, status, reason, bstack1lll11l1l1_opy_, bstack1111l1ll_opy_):
  bstack1l11l11lll_opy_ = {
    bstack1ll_opy_ (u"ࠧࡢࡥࡷ࡭ࡴࡴࠧ౎"): type,
    bstack1ll_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ౏"): {}
  }
  if type == bstack1ll_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫ౐"):
    bstack1l11l11lll_opy_[bstack1ll_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭౑")][bstack1ll_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ౒")] = bstack1lll11l1l1_opy_
    bstack1l11l11lll_opy_[bstack1ll_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ౓")][bstack1ll_opy_ (u"࠭ࡤࡢࡶࡤࠫ౔")] = json.dumps(str(bstack1111l1ll_opy_))
  if type == bstack1ll_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨౕ"):
    bstack1l11l11lll_opy_[bstack1ll_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶౖࠫ")][bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ౗")] = name
  if type == bstack1ll_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ࠭ౘ"):
    bstack1l11l11lll_opy_[bstack1ll_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧౙ")][bstack1ll_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬౚ")] = status
    if status == bstack1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭౛"):
      bstack1l11l11lll_opy_[bstack1ll_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ౜")][bstack1ll_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨౝ")] = json.dumps(str(reason))
  bstack1lllll11l_opy_ = bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧ౞").format(json.dumps(bstack1l11l11lll_opy_))
  return bstack1lllll11l_opy_
def bstack1l11l111_opy_(driver_command, response):
    if driver_command == bstack1ll_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࠧ౟"):
        bstack1l111111_opy_.bstack1111llll1_opy_({
            bstack1ll_opy_ (u"ࠫ࡮ࡳࡡࡨࡧࠪౠ"): response[bstack1ll_opy_ (u"ࠬࡼࡡ࡭ࡷࡨࠫౡ")],
            bstack1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ౢ"): bstack1l111111_opy_.current_test_uuid()
        })
def bstack1l1lll11l_opy_(item, call, rep):
  global bstack1lll1l1l_opy_
  global bstack1llll1lll_opy_
  global bstack11l111l1l1_opy_
  name = bstack1ll_opy_ (u"ࠧࠨౣ")
  try:
    if rep.when == bstack1ll_opy_ (u"ࠨࡥࡤࡰࡱ࠭౤"):
      bstack1l1111l11l_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack11l111l1l1_opy_:
          name = str(rep.nodeid)
          bstack1l1l111l1l_opy_ = bstack11ll11l1ll_opy_(bstack1ll_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ౥"), name, bstack1ll_opy_ (u"ࠪࠫ౦"), bstack1ll_opy_ (u"ࠫࠬ౧"), bstack1ll_opy_ (u"ࠬ࠭౨"), bstack1ll_opy_ (u"࠭ࠧ౩"))
          threading.current_thread().bstack1l11l11ll1_opy_ = name
          for driver in bstack1llll1lll_opy_:
            if bstack1l1111l11l_opy_ == driver.session_id:
              driver.execute_script(bstack1l1l111l1l_opy_)
      except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠡࡨࡲࡶࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡶࡩࡸࡹࡩࡰࡰ࠽ࠤࢀࢃࠧ౪").format(str(e)))
      try:
        bstack1111ll111_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack1ll_opy_ (u"ࠨࡵ࡮࡭ࡵࡶࡥࡥࠩ౫"):
          status = bstack1ll_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ౬") if rep.outcome.lower() == bstack1ll_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ౭") else bstack1ll_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ౮")
          reason = bstack1ll_opy_ (u"ࠬ࠭౯")
          if status == bstack1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭౰"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack1ll_opy_ (u"ࠧࡪࡰࡩࡳࠬ౱") if status == bstack1ll_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨ౲") else bstack1ll_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ౳")
          data = name + bstack1ll_opy_ (u"ࠪࠤࡵࡧࡳࡴࡧࡧࠥࠬ౴") if status == bstack1ll_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ౵") else name + bstack1ll_opy_ (u"ࠬࠦࡦࡢ࡫࡯ࡩࡩࠧࠠࠨ౶") + reason
          bstack1l1ll1ll1_opy_ = bstack11ll11l1ll_opy_(bstack1ll_opy_ (u"࠭ࡡ࡯ࡰࡲࡸࡦࡺࡥࠨ౷"), bstack1ll_opy_ (u"ࠧࠨ౸"), bstack1ll_opy_ (u"ࠨࠩ౹"), bstack1ll_opy_ (u"ࠩࠪ౺"), level, data)
          for driver in bstack1llll1lll_opy_:
            if bstack1l1111l11l_opy_ == driver.session_id:
              driver.execute_script(bstack1l1ll1ll1_opy_)
      except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡤࡱࡱࡸࡪࡾࡴࠡࡨࡲࡶࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡶࡩࡸࡹࡩࡰࡰ࠽ࠤࢀࢃࠧ౻").format(str(e)))
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡴࡶࡤࡸࡪࠦࡩ࡯ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡦࡵࡷࠤࡸࡺࡡࡵࡷࡶ࠾ࠥࢁࡽࠨ౼").format(str(e)))
  bstack1lll1l1l_opy_(item, call, rep)
def bstack1l1ll111l1_opy_(driver, bstack1l1111111_opy_, test=None):
  global bstack1l1111ll_opy_
  if test != None:
    bstack1l1l1lll1_opy_ = getattr(test, bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ౽"), None)
    bstack1l111l1111_opy_ = getattr(test, bstack1ll_opy_ (u"࠭ࡵࡶ࡫ࡧࠫ౾"), None)
    PercySDK.screenshot(driver, bstack1l1111111_opy_, bstack1l1l1lll1_opy_=bstack1l1l1lll1_opy_, bstack1l111l1111_opy_=bstack1l111l1111_opy_, bstack11l1l111_opy_=bstack1l1111ll_opy_)
  else:
    PercySDK.screenshot(driver, bstack1l1111111_opy_)
@measure(event_name=EVENTS.bstack1111lll1l_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1l1ll1111l_opy_(driver):
  if bstack1l1ll1l1ll_opy_.bstack11l1llll11_opy_() is True or bstack1l1ll1l1ll_opy_.capturing() is True:
    return
  bstack1l1ll1l1ll_opy_.bstack11l11l1l11_opy_()
  while not bstack1l1ll1l1ll_opy_.bstack11l1llll11_opy_():
    bstack1lll1l11_opy_ = bstack1l1ll1l1ll_opy_.bstack1lll1l1111_opy_()
    bstack1l1ll111l1_opy_(driver, bstack1lll1l11_opy_)
  bstack1l1ll1l1ll_opy_.bstack111lll1ll_opy_()
def bstack1ll1lll1_opy_(sequence, driver_command, response = None, bstack1l11lll11_opy_ = None, args = None):
    try:
      if sequence != bstack1ll_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫ࠧ౿"):
        return
      if percy.bstack1ll1ll11l1_opy_() == bstack1ll_opy_ (u"ࠣࡨࡤࡰࡸ࡫ࠢಀ"):
        return
      bstack1lll1l11_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡳࡩࡷࡩࡹࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬಁ"), None)
      for command in bstack1l1111l1l_opy_:
        if command == driver_command:
          for driver in bstack1llll1lll_opy_:
            bstack1l1ll1111l_opy_(driver)
      bstack111l1l1l_opy_ = percy.bstack1l1l1111_opy_()
      if driver_command in bstack11lll11l_opy_[bstack111l1l1l_opy_]:
        bstack1l1ll1l1ll_opy_.bstack11lll1llll_opy_(bstack1lll1l11_opy_, driver_command)
    except Exception as e:
      pass
def bstack1ll11ll11_opy_(framework_name):
  if bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡱࡴࡪ࡟ࡤࡣ࡯ࡰࡪࡪࠧಂ")):
      return
  bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡲࡵࡤࡠࡥࡤࡰࡱ࡫ࡤࠨಃ"), True)
  global bstack11ll1l1lll_opy_
  global bstack1l111lll11_opy_
  global bstack1llll1ll1l_opy_
  bstack11ll1l1lll_opy_ = framework_name
  logger.info(bstack1l111l1l1l_opy_.format(bstack11ll1l1lll_opy_.split(bstack1ll_opy_ (u"ࠬ࠳ࠧ಄"))[0]))
  bstack1lll1l111l_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1lllll11_opy_:
      Service.start = bstack1l11l11111_opy_
      Service.stop = bstack1lll111l_opy_
      webdriver.Remote.get = bstack11l1l1ll1l_opy_
      WebDriver.quit = bstack1l1l1l11ll_opy_
      webdriver.Remote.__init__ = bstack11l111ll1l_opy_
    if not bstack1lllll11_opy_:
        webdriver.Remote.__init__ = bstack1ll111l1l1_opy_
    WebDriver.getAccessibilityResults = getAccessibilityResults
    WebDriver.get_accessibility_results = getAccessibilityResults
    WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
    WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
    WebDriver.performScan = perform_scan
    WebDriver.perform_scan = perform_scan
    WebDriver.execute = bstack1ll11llll_opy_
    bstack1l111lll11_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1lllll11_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack11ll1ll1l_opy_
  except Exception as e:
    pass
  bstack1l1l1lll11_opy_()
  if not bstack1l111lll11_opy_:
    bstack11l1l111l1_opy_(bstack1ll_opy_ (u"ࠨࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠡࡰࡲࡸࠥ࡯࡮ࡴࡶࡤࡰࡱ࡫ࡤࠣಅ"), bstack1lllll1l1_opy_)
  if bstack1ll1l1llll_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      if hasattr(RemoteConnection, bstack1ll_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨಆ")) and callable(getattr(RemoteConnection, bstack1ll_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩಇ"))):
        RemoteConnection._get_proxy_url = bstack11l1llll_opy_
      else:
        from selenium.webdriver.remote.client_config import ClientConfig
        ClientConfig.get_proxy_url = bstack11l1llll_opy_
    except Exception as e:
      logger.error(bstack11lll11111_opy_.format(str(e)))
  if bstack1l111l11l1_opy_():
    bstack11ll11l111_opy_(CONFIG, logger)
  if (bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨಈ") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1ll1ll11l1_opy_() == bstack1ll_opy_ (u"ࠥࡸࡷࡻࡥࠣಉ"):
          bstack111l11l11_opy_(bstack1ll1lll1_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1l1111111l_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack1ll1l11l11_opy_
      except Exception as e:
        logger.warn(bstack11l1ll11ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1lll11ll_opy_
      except Exception as e:
        logger.debug(bstack1l111ll1l_opy_ + str(e))
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack11l1ll11ll_opy_)
    Output.start_test = bstack11ll1l1111_opy_
    Output.end_test = bstack1llllllll1_opy_
    TestStatus.__init__ = bstack111lll111_opy_
    QueueItem.__init__ = bstack11l111l1ll_opy_
    pabot._create_items = bstack1ll11ll1l_opy_
    try:
      from pabot import __version__ as bstack1ll1ll1l1l_opy_
      if version.parse(bstack1ll1ll1l1l_opy_) >= version.parse(bstack1ll_opy_ (u"ࠫ࠹࠴࠲࠯࠲ࠪಊ")):
        pabot._run = bstack1l11l1lll_opy_
      elif version.parse(bstack1ll1ll1l1l_opy_) >= version.parse(bstack1ll_opy_ (u"ࠬ࠸࠮࠲࠷࠱࠴ࠬಋ")):
        pabot._run = bstack1llll111_opy_
      elif version.parse(bstack1ll1ll1l1l_opy_) >= version.parse(bstack1ll_opy_ (u"࠭࠲࠯࠳࠶࠲࠵࠭ಌ")):
        pabot._run = bstack11lll1l1_opy_
      else:
        pabot._run = bstack11111lll1_opy_
    except Exception as e:
      pabot._run = bstack11111lll1_opy_
    pabot._create_command_for_execution = bstack1l111llll_opy_
    pabot._report_results = bstack1l1l1l11l_opy_
  if bstack1ll_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ಍") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack1ll11lll1_opy_)
    Runner.run_hook = bstack1llll1llll_opy_
    Step.run = bstack1l1111lll1_opy_
  if bstack1ll_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨಎ") in str(framework_name).lower():
    if not bstack1lllll11_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack11lllll11l_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1lll11l111_opy_
      Config.getoption = bstack111llll1_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1l1lll11l_opy_
    except Exception as e:
      pass
def bstack111lll11l_opy_():
  global CONFIG
  if bstack1ll_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩಏ") in CONFIG and int(CONFIG[bstack1ll_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪಐ")]) > 1:
    logger.warn(bstack1l11lll1l_opy_)
def bstack11ll1ll1ll_opy_(arg, bstack1llllll1ll_opy_, bstack1111111ll_opy_=None):
  global CONFIG
  global bstack11llll1l1_opy_
  global bstack1l11lll1_opy_
  global bstack1lllll11_opy_
  global bstack1lll1111ll_opy_
  bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ಑")
  if bstack1llllll1ll_opy_ and isinstance(bstack1llllll1ll_opy_, str):
    bstack1llllll1ll_opy_ = eval(bstack1llllll1ll_opy_)
  CONFIG = bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬಒ")]
  bstack11llll1l1_opy_ = bstack1llllll1ll_opy_[bstack1ll_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧಓ")]
  bstack1l11lll1_opy_ = bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩಔ")]
  bstack1lllll11_opy_ = bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫಕ")]
  bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪಖ"), bstack1lllll11_opy_)
  os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬಗ")] = bstack11111l111_opy_
  os.environ[bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠪಘ")] = json.dumps(CONFIG)
  os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡍ࡛ࡂࡠࡗࡕࡐࠬಙ")] = bstack11llll1l1_opy_
  os.environ[bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧಚ")] = str(bstack1l11lll1_opy_)
  os.environ[bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ࠭ಛ")] = str(True)
  if bstack1l1ll1ll1l_opy_(arg, [bstack1ll_opy_ (u"ࠨ࠯ࡱࠫಜ"), bstack1ll_opy_ (u"ࠩ࠰࠱ࡳࡻ࡭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪಝ")]) != -1:
    os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡅࡗࡇࡌࡍࡇࡏࠫಞ")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1l1l11lll1_opy_)
    return
  bstack1ll1l11ll1_opy_()
  global bstack11l11l1lll_opy_
  global bstack1l1111ll_opy_
  global bstack1lll11llll_opy_
  global bstack1l111lll1l_opy_
  global bstack1111l11l_opy_
  global bstack1llll1ll1l_opy_
  global bstack11l11llll1_opy_
  arg.append(bstack1ll_opy_ (u"ࠦ࠲࡝ࠢಟ"))
  arg.append(bstack1ll_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩ࠿ࡓ࡯ࡥࡷ࡯ࡩࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡩ࡮ࡲࡲࡶࡹ࡫ࡤ࠻ࡲࡼࡸࡪࡹࡴ࠯ࡒࡼࡸࡪࡹࡴࡘࡣࡵࡲ࡮ࡴࡧࠣಠ"))
  arg.append(bstack1ll_opy_ (u"ࠨ࠭ࡘࠤಡ"))
  arg.append(bstack1ll_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫࠺ࡕࡪࡨࠤ࡭ࡵ࡯࡬࡫ࡰࡴࡱࠨಢ"))
  global bstack1ll111ll11_opy_
  global bstack1lll11111l_opy_
  global bstack11l11ll1ll_opy_
  global bstack111l11l1_opy_
  global bstack1l1111llll_opy_
  global bstack111l1lll1_opy_
  global bstack1l111l11l_opy_
  global bstack11l11ll11l_opy_
  global bstack11llll11l1_opy_
  global bstack1l11l1ll11_opy_
  global bstack11l1111l1_opy_
  global bstack1l1l11l11_opy_
  global bstack1lll1l1l_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1ll111ll11_opy_ = webdriver.Remote.__init__
    bstack1lll11111l_opy_ = WebDriver.quit
    bstack11l11ll11l_opy_ = WebDriver.close
    bstack11llll11l1_opy_ = WebDriver.get
    bstack11l11ll1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack11lll1lll_opy_(CONFIG) and bstack1l1111l111_opy_():
    if bstack11l111ll1_opy_() < version.parse(bstack1l1lll111_opy_):
      logger.error(bstack1l1ll1l1l_opy_.format(bstack11l111ll1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1ll_opy_ (u"ࠨࡡࡪࡩࡹࡥࡰࡳࡱࡻࡽࡤࡻࡲ࡭ࠩಣ")) and callable(getattr(RemoteConnection, bstack1ll_opy_ (u"ࠩࡢ࡫ࡪࡺ࡟ࡱࡴࡲࡼࡾࡥࡵࡳ࡮ࠪತ"))):
          bstack1l11l1ll11_opy_ = RemoteConnection._get_proxy_url
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          bstack1l11l1ll11_opy_ = ClientConfig.get_proxy_url
      except Exception as e:
        logger.error(bstack11lll11111_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack11l1111l1_opy_ = Config.getoption
    from _pytest import runner
    bstack1l1l11l11_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warn(e, bstack1l1l11ll_opy_)
  try:
    from pytest_bdd import reporting
    bstack1lll1l1l_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack1ll_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡲࠤࡷࡻ࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࡶࠫಥ"))
  bstack1lll11llll_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨದ"), {}).get(bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧಧ"))
  bstack11l11llll1_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack11l11l1l_opy_():
      bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.CONNECT, bstack1l1l1ll1l_opy_())
    platform_index = int(os.environ.get(bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ನ"), bstack1ll_opy_ (u"ࠧ࠱ࠩ಩")))
  else:
    bstack1ll11ll11_opy_(bstack11ll111l_opy_)
  os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡓࡇࡍࡆࠩಪ")] = CONFIG[bstack1ll_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫಫ")]
  os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ಬ")] = CONFIG[bstack1ll_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧಭ")]
  os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆ࡛ࡔࡐࡏࡄࡘࡎࡕࡎࠨಮ")] = bstack1lllll11_opy_.__str__()
  from _pytest.config import main as bstack1l1111l1l1_opy_
  bstack111ll1ll1_opy_ = []
  try:
    bstack1l11111ll1_opy_ = bstack1l1111l1l1_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack1ll1l111_opy_()
    if bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪಯ") in multiprocessing.current_process().__dict__.keys():
      for bstack11lll1111l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack111ll1ll1_opy_.append(bstack11lll1111l_opy_)
    try:
      bstack111ll111l_opy_ = (bstack111ll1ll1_opy_, int(bstack1l11111ll1_opy_))
      bstack1111111ll_opy_.append(bstack111ll111l_opy_)
    except:
      bstack1111111ll_opy_.append((bstack111ll1ll1_opy_, bstack1l11111ll1_opy_))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack111ll1ll1_opy_.append({bstack1ll_opy_ (u"ࠧ࡯ࡣࡰࡩࠬರ"): bstack1ll_opy_ (u"ࠨࡒࡵࡳࡨ࡫ࡳࡴࠢࠪಱ") + os.environ.get(bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩಲ")), bstack1ll_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩಳ"): traceback.format_exc(), bstack1ll_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ಴"): int(os.environ.get(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬವ")))})
    bstack1111111ll_opy_.append((bstack111ll1ll1_opy_, 1))
def mod_behave_main(args, retries):
  try:
    from behave.configuration import Configuration
    from behave.__main__ import run_behave
    from browserstack_sdk.bstack_behave_runner import BehaveRunner
    config = Configuration(args)
    config.update_userdata({bstack1ll_opy_ (u"ࠨࡲࡦࡶࡵ࡭ࡪࡹࠢಶ"): str(retries)})
    return run_behave(config, runner_class=BehaveRunner)
  except Exception as e:
    bstack1l111ll1ll_opy_ = e.__class__.__name__
    print(bstack1ll_opy_ (u"ࠢࠦࡵ࠽ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡶࡺࡴ࡮ࡪࡰࡪࠤࡧ࡫ࡨࡢࡸࡨࠤࡹ࡫ࡳࡵࠢࠨࡷࠧಷ") % (bstack1l111ll1ll_opy_, e))
    return 1
def bstack1ll1111l1_opy_(arg):
  global bstack1l111l1l1_opy_
  bstack1ll11ll11_opy_(bstack1lll1ll1_opy_)
  os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩಸ")] = str(bstack1l11lll1_opy_)
  retries = bstack1ll1ll1ll_opy_.bstack1ll1l1l11_opy_(CONFIG)
  status_code = 0
  if bstack1ll1ll1ll_opy_.bstack1l1ll11111_opy_(CONFIG):
    status_code = mod_behave_main(arg, retries)
  else:
    from behave.__main__ import main as bstack1llllll111_opy_
    status_code = bstack1llllll111_opy_(arg)
  if status_code != 0:
    bstack1l111l1l1_opy_ = status_code
def bstack11ll1l111_opy_():
  logger.info(bstack1ll11ll11l_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1ll_opy_ (u"ࠩࡶࡩࡹࡻࡰࠨಹ"), help=bstack1ll_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࠫ಺"))
  parser.add_argument(bstack1ll_opy_ (u"ࠫ࠲ࡻࠧ಻"), bstack1ll_opy_ (u"ࠬ࠳࠭ࡶࡵࡨࡶࡳࡧ࡭ࡦ಼ࠩ"), help=bstack1ll_opy_ (u"࡙࠭ࡰࡷࡵࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡹࡸ࡫ࡲ࡯ࡣࡰࡩࠬಽ"))
  parser.add_argument(bstack1ll_opy_ (u"ࠧ࠮࡭ࠪಾ"), bstack1ll_opy_ (u"ࠨ࠯࠰࡯ࡪࡿࠧಿ"), help=bstack1ll_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡡࡤࡥࡨࡷࡸࠦ࡫ࡦࡻࠪೀ"))
  parser.add_argument(bstack1ll_opy_ (u"ࠪ࠱࡫࠭ು"), bstack1ll_opy_ (u"ࠫ࠲࠳ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩೂ"), help=bstack1ll_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡸࡪࡹࡴࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫೃ"))
  bstack1lll11l1_opy_ = parser.parse_args()
  try:
    bstack1l1l111111_opy_ = bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡭ࡥ࡯ࡧࡵ࡭ࡨ࠴ࡹ࡮࡮࠱ࡷࡦࡳࡰ࡭ࡧࠪೄ")
    if bstack1lll11l1_opy_.framework and bstack1lll11l1_opy_.framework not in (bstack1ll_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ೅"), bstack1ll_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠴ࠩೆ")):
      bstack1l1l111111_opy_ = bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࠲ࡾࡳ࡬࠯ࡵࡤࡱࡵࡲࡥࠨೇ")
    bstack1l1ll1ll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l111111_opy_)
    bstack1ll1l1111_opy_ = open(bstack1l1ll1ll_opy_, bstack1ll_opy_ (u"ࠪࡶࠬೈ"))
    bstack11l1l11lll_opy_ = bstack1ll1l1111_opy_.read()
    bstack1ll1l1111_opy_.close()
    if bstack1lll11l1_opy_.username:
      bstack11l1l11lll_opy_ = bstack11l1l11lll_opy_.replace(bstack1ll_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡘࡗࡊࡘࡎࡂࡏࡈࠫ೉"), bstack1lll11l1_opy_.username)
    if bstack1lll11l1_opy_.key:
      bstack11l1l11lll_opy_ = bstack11l1l11lll_opy_.replace(bstack1ll_opy_ (u"ࠬ࡟ࡏࡖࡔࡢࡅࡈࡉࡅࡔࡕࡢࡏࡊ࡟ࠧೊ"), bstack1lll11l1_opy_.key)
    if bstack1lll11l1_opy_.framework:
      bstack11l1l11lll_opy_ = bstack11l1l11lll_opy_.replace(bstack1ll_opy_ (u"࡙࠭ࡐࡗࡕࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧೋ"), bstack1lll11l1_opy_.framework)
    file_name = bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪೌ")
    file_path = os.path.abspath(file_name)
    bstack1ll1llll1l_opy_ = open(file_path, bstack1ll_opy_ (u"ࠨࡹ್ࠪ"))
    bstack1ll1llll1l_opy_.write(bstack11l1l11lll_opy_)
    bstack1ll1llll1l_opy_.close()
    logger.info(bstack1ll1l111ll_opy_)
    try:
      os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡕࡅࡒࡋࡗࡐࡔࡎࠫ೎")] = bstack1lll11l1_opy_.framework if bstack1lll11l1_opy_.framework != None else bstack1ll_opy_ (u"ࠥࠦ೏")
      config = yaml.safe_load(bstack11l1l11lll_opy_)
      config[bstack1ll_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫ೐")] = bstack1ll_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠲ࡹࡥࡵࡷࡳࠫ೑")
      bstack11l1l1l111_opy_(bstack11l1l1lll1_opy_, config)
    except Exception as e:
      logger.debug(bstack1lllll1l11_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack11l1llll1l_opy_.format(str(e)))
def bstack11l1l1l111_opy_(bstack1ll1lll1l1_opy_, config, bstack1llllll11_opy_={}):
  global bstack1lllll11_opy_
  global bstack1l11ll1l11_opy_
  global bstack1lll1111ll_opy_
  if not config:
    return
  bstack111l1l11l_opy_ = bstack1111l1l1_opy_ if not bstack1lllll11_opy_ else (
    bstack1111l1ll1_opy_ if bstack1ll_opy_ (u"࠭ࡡࡱࡲࠪ೒") in config else (
        bstack1ll11ll1l1_opy_ if config.get(bstack1ll_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ೓")) else bstack1l11111ll_opy_
    )
)
  bstack11llllll1_opy_ = False
  bstack1111ll1l_opy_ = False
  if bstack1lllll11_opy_ is True:
      if bstack1ll_opy_ (u"ࠨࡣࡳࡴࠬ೔") in config:
          bstack11llllll1_opy_ = True
      else:
          bstack1111ll1l_opy_ = True
  bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack11l1ll1ll_opy_(config, bstack1l11ll1l11_opy_)
  bstack11l1l1l1l1_opy_ = bstack11lll1ll11_opy_()
  data = {
    bstack1ll_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫೕ"): config[bstack1ll_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬೖ")],
    bstack1ll_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ೗"): config[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ೘")],
    bstack1ll_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ೙"): bstack1ll1lll1l1_opy_,
    bstack1ll_opy_ (u"ࠧࡥࡧࡷࡩࡨࡺࡥࡥࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ೚"): os.environ.get(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ೛"), bstack1l11ll1l11_opy_),
    bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ೜"): bstack11ll11ll1_opy_,
    bstack1ll_opy_ (u"ࠪࡳࡵࡺࡩ࡮ࡣ࡯ࡣ࡭ࡻࡢࡠࡷࡵࡰࠬೝ"): bstack1l1ll11l11_opy_(),
    bstack1ll_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧೞ"): {
      bstack1ll_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ೟"): str(config[bstack1ll_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ೠ")]) if bstack1ll_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧೡ") in config else bstack1ll_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤೢ"),
      bstack1ll_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨ࡚ࡪࡸࡳࡪࡱࡱࠫೣ"): sys.version,
      bstack1ll_opy_ (u"ࠪࡶࡪ࡬ࡥࡳࡴࡨࡶࠬ೤"): bstack1llll1l11l_opy_(os.environ.get(bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭೥"), bstack1l11ll1l11_opy_)),
      bstack1ll_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠧ೦"): bstack1ll_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭೧"),
      bstack1ll_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨ೨"): bstack111l1l11l_opy_,
      bstack1ll_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭೩"): bstack1ll1111l_opy_,
      bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡢࡹࡺ࡯ࡤࠨ೪"): os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨ೫")],
      bstack1ll_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ೬"): os.environ.get(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧ೭"), bstack1l11ll1l11_opy_),
      bstack1ll_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩ೮"): bstack1lll1l1ll1_opy_(os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ೯"), bstack1l11ll1l11_opy_)),
      bstack1ll_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ೰"): bstack11l1l1l1l1_opy_.get(bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧೱ")),
      bstack1ll_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩೲ"): bstack11l1l1l1l1_opy_.get(bstack1ll_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬೳ")),
      bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ೴"): config[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ೵")] if config[bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ೶")] else bstack1ll_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤ೷"),
      bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ೸"): str(config[bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ೹")]) if bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭೺") in config else bstack1ll_opy_ (u"ࠧࡻ࡮࡬ࡰࡲࡻࡳࠨ೻"),
      bstack1ll_opy_ (u"࠭࡯ࡴࠩ೼"): sys.platform,
      bstack1ll_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩ೽"): socket.gethostname(),
      bstack1ll_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪ೾"): bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫ೿"))
    }
  }
  if not bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪഀ")) is None:
    data[bstack1ll_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧഁ")][bstack1ll_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࡍࡦࡶࡤࡨࡦࡺࡡࠨം")] = {
      bstack1ll_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭ഃ"): bstack1ll_opy_ (u"ࠧࡶࡵࡨࡶࡤࡱࡩ࡭࡮ࡨࡨࠬഄ"),
      bstack1ll_opy_ (u"ࠨࡵ࡬࡫ࡳࡧ࡬ࠨഅ"): bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠩࡶࡨࡰࡑࡩ࡭࡮ࡖ࡭࡬ࡴࡡ࡭ࠩആ")),
      bstack1ll_opy_ (u"ࠪࡷ࡮࡭࡮ࡢ࡮ࡑࡹࡲࡨࡥࡳࠩഇ"): bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡓࡵࠧഈ"))
    }
  if bstack1ll1lll1l1_opy_ == bstack1l11llll_opy_:
    data[bstack1ll_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨഉ")][bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡈࡵ࡮ࡧ࡫ࡪࠫഊ")] = bstack1lll1ll111_opy_(config)
    data[bstack1ll_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪഋ")][bstack1ll_opy_ (u"ࠨ࡫ࡶࡔࡪࡸࡣࡺࡃࡸࡸࡴࡋ࡮ࡢࡤ࡯ࡩࡩ࠭ഌ")] = percy.bstack1l11111l1l_opy_
    data[bstack1ll_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡲࡵࡳࡵ࡫ࡲࡵ࡫ࡨࡷࠬ഍")][bstack1ll_opy_ (u"ࠪࡴࡪࡸࡣࡺࡄࡸ࡭ࡱࡪࡉࡥࠩഎ")] = percy.percy_build_id
  if not bstack1ll1ll1ll_opy_.bstack1l11111l1_opy_(CONFIG):
    data[bstack1ll_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧഏ")][bstack1ll_opy_ (u"ࠬࡺࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠩഐ")] = bstack1ll1ll1ll_opy_.bstack1l11111l1_opy_(CONFIG)
  update(data[bstack1ll_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡶࡲࡰࡲࡨࡶࡹ࡯ࡥࡴࠩ഑")], bstack1llllll11_opy_)
  try:
    response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠧࡑࡑࡖࡘࠬഒ"), bstack11llll1111_opy_(bstack1111l1lll_opy_), data, {
      bstack1ll_opy_ (u"ࠨࡣࡸࡸ࡭࠭ഓ"): (config[bstack1ll_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫഔ")], config[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ക")])
    })
    if response:
      logger.debug(bstack11lllll1l1_opy_.format(bstack1ll1lll1l1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1l1111ll1_opy_.format(str(e)))
def bstack1llll1l11l_opy_(framework):
  return bstack1ll_opy_ (u"ࠦࢀࢃ࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴ࢁࡽࠣഖ").format(str(framework), __version__) if framework else bstack1ll_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࡿࢂࠨഗ").format(
    __version__)
def bstack1ll1l11ll1_opy_():
  global CONFIG
  global bstack11lll1lll1_opy_
  if bool(CONFIG):
    return
  try:
    bstack1lll11ll11_opy_()
    logger.debug(bstack11l11ll1l_opy_.format(str(CONFIG)))
    bstack11lll1lll1_opy_ = bstack111ll11ll_opy_.bstack1l1l1ll1ll_opy_(CONFIG, bstack11lll1lll1_opy_)
    bstack1lll1l111l_opy_()
  except Exception as e:
    logger.error(bstack1ll_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࡻࡰ࠭ࠢࡨࡶࡷࡵࡲ࠻ࠢࠥഘ") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1ll11l11ll_opy_
  atexit.register(bstack11l1ll111_opy_)
  signal.signal(signal.SIGINT, bstack1lll111l1_opy_)
  signal.signal(signal.SIGTERM, bstack1lll111l1_opy_)
def bstack1ll11l11ll_opy_(exctype, value, traceback):
  global bstack1llll1lll_opy_
  try:
    for driver in bstack1llll1lll_opy_:
      bstack11llll111_opy_(driver, bstack1ll_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧങ"), bstack1ll_opy_ (u"ࠣࡕࡨࡷࡸ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦച") + str(value))
  except Exception:
    pass
  logger.info(bstack1l11l1l11l_opy_)
  bstack1llll11l11_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1llll11l11_opy_(message=bstack1ll_opy_ (u"ࠩࠪഛ"), bstack1l11l111l1_opy_ = False):
  global CONFIG
  bstack1111lll1_opy_ = bstack1ll_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮ࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠬജ") if bstack1l11l111l1_opy_ else bstack1ll_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪഝ")
  try:
    if message:
      bstack1llllll11_opy_ = {
        bstack1111lll1_opy_ : str(message)
      }
      bstack11l1l1l111_opy_(bstack1l11llll_opy_, CONFIG, bstack1llllll11_opy_)
    else:
      bstack11l1l1l111_opy_(bstack1l11llll_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack11l1lll1l1_opy_.format(str(e)))
def bstack1l1lll11ll_opy_(bstack11ll1lll1_opy_, size):
  bstack11l111llll_opy_ = []
  while len(bstack11ll1lll1_opy_) > size:
    bstack11llll1ll1_opy_ = bstack11ll1lll1_opy_[:size]
    bstack11l111llll_opy_.append(bstack11llll1ll1_opy_)
    bstack11ll1lll1_opy_ = bstack11ll1lll1_opy_[size:]
  bstack11l111llll_opy_.append(bstack11ll1lll1_opy_)
  return bstack11l111llll_opy_
def bstack11111llll_opy_(args):
  if bstack1ll_opy_ (u"ࠬ࠳࡭ࠨഞ") in args and bstack1ll_opy_ (u"࠭ࡰࡥࡤࠪട") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack1l11l1ll1l_opy_, stage=STAGE.bstack1ll11lll11_opy_)
def run_on_browserstack(bstack11l1111ll_opy_=None, bstack1111111ll_opy_=None, bstack1ll111l111_opy_=False):
  global CONFIG
  global bstack11llll1l1_opy_
  global bstack1l11lll1_opy_
  global bstack1l11ll1l11_opy_
  global bstack1lll1111ll_opy_
  bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠧࠨഠ")
  bstack1l111lllll_opy_(bstack11lll111l1_opy_, logger)
  if bstack11l1111ll_opy_ and isinstance(bstack11l1111ll_opy_, str):
    bstack11l1111ll_opy_ = eval(bstack11l1111ll_opy_)
  if bstack11l1111ll_opy_:
    CONFIG = bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨഡ")]
    bstack11llll1l1_opy_ = bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪഢ")]
    bstack1l11lll1_opy_ = bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬണ")]
    bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ത"), bstack1l11lll1_opy_)
    bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬഥ")
  bstack1lll1111ll_opy_.bstack11111l11_opy_(bstack1ll_opy_ (u"࠭ࡳࡥ࡭ࡕࡹࡳࡏࡤࠨദ"), uuid4().__str__())
  logger.info(bstack1ll_opy_ (u"ࠧࡔࡆࡎࠤࡷࡻ࡮ࠡࡵࡷࡥࡷࡺࡥࡥࠢࡺ࡭ࡹ࡮ࠠࡪࡦ࠽ࠤࠬധ") + bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠨࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠪന")));
  logger.debug(bstack1ll_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࡁࠬഩ") + bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࠬപ")))
  if not bstack1ll111l111_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1l1l11lll1_opy_)
      return
    if sys.argv[1] == bstack1ll_opy_ (u"ࠫ࠲࠳ࡶࡦࡴࡶ࡭ࡴࡴࠧഫ") or sys.argv[1] == bstack1ll_opy_ (u"ࠬ࠳ࡶࠨബ"):
      logger.info(bstack1ll_opy_ (u"࠭ࡂࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡖࡹࡵࡪࡲࡲ࡙ࠥࡄࡌࠢࡹࡿࢂ࠭ഭ").format(__version__))
      return
    if sys.argv[1] == bstack1ll_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭മ"):
      bstack11ll1l111_opy_()
      return
  args = sys.argv
  bstack1ll1l11ll1_opy_()
  global bstack11l11l1lll_opy_
  global bstack1ll1111ll1_opy_
  global bstack11l11llll1_opy_
  global bstack1l1lll1111_opy_
  global bstack1l1111ll_opy_
  global bstack1lll11llll_opy_
  global bstack1l111lll1l_opy_
  global bstack1l11ll11_opy_
  global bstack1111l11l_opy_
  global bstack1llll1ll1l_opy_
  global bstack1l11l1l111_opy_
  bstack1ll1111ll1_opy_ = len(CONFIG.get(bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫയ"), []))
  if not bstack11111l111_opy_:
    if args[1] == bstack1ll_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩര") or args[1] == bstack1ll_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫറ"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫല")
      args = args[2:]
    elif args[1] == bstack1ll_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫള"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬഴ")
      args = args[2:]
    elif args[1] == bstack1ll_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭വ"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧശ")
      args = args[2:]
    elif args[1] == bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪഷ"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫസ")
      args = args[2:]
    elif args[1] == bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫഹ"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬഺ")
      args = args[2:]
    elif args[1] == bstack1ll_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ഻࠭"):
      bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫഼ࠧ")
      args = args[2:]
    else:
      if not bstack1ll_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫഽ") in CONFIG or str(CONFIG[bstack1ll_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬാ")]).lower() in [bstack1ll_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪി"), bstack1ll_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬീ")]:
        bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬു")
        args = args[1:]
      elif str(CONFIG[bstack1ll_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩൂ")]).lower() == bstack1ll_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ൃ"):
        bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧൄ")
        args = args[1:]
      elif str(CONFIG[bstack1ll_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ൅")]).lower() == bstack1ll_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩെ"):
        bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪേ")
        args = args[1:]
      elif str(CONFIG[bstack1ll_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨൈ")]).lower() == bstack1ll_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭൉"):
        bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧൊ")
        args = args[1:]
      elif str(CONFIG[bstack1ll_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫോ")]).lower() == bstack1ll_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩൌ"):
        bstack11111l111_opy_ = bstack1ll_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ്ࠪ")
        args = args[1:]
      else:
        os.environ[bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭ൎ")] = bstack11111l111_opy_
        bstack1l11l11l1l_opy_(bstack11l1l1l11l_opy_)
  os.environ[bstack1ll_opy_ (u"ࠬࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࡠࡗࡖࡉࡉ࠭൏")] = bstack11111l111_opy_
  bstack1l11ll1l11_opy_ = bstack11111l111_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack11lll1ll1l_opy_ = bstack1lll1l11l1_opy_[bstack1ll_opy_ (u"࠭ࡐ࡚ࡖࡈࡗ࡙࠳ࡂࡅࡆࠪ൐")] if bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ൑") and bstack1l11l1ll_opy_() else bstack11111l111_opy_
      bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.bstack11ll111l11_opy_, bstack11l111ll11_opy_(
        sdk_version=__version__,
        path_config=bstack11llllllll_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack11lll1ll1l_opy_,
        frameworks=[bstack11lll1ll1l_opy_],
        framework_versions={
          bstack11lll1ll1l_opy_: bstack1lll1l1ll1_opy_(bstack1ll_opy_ (u"ࠨࡔࡲࡦࡴࡺࠧ൒") if bstack11111l111_opy_ in [bstack1ll_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ൓"), bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩൔ"), bstack1ll_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬൕ")] else bstack11111l111_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠢൖ"), None):
        CONFIG[bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣൗ")] = cli.config.get(bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠤ൘"), None)
    except Exception as e:
      bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.bstack11ll11111l_opy_, e.__traceback__, 1)
    if bstack1l11lll1_opy_:
      CONFIG[bstack1ll_opy_ (u"ࠣࡣࡳࡴࠧ൙")] = cli.config[bstack1ll_opy_ (u"ࠤࡤࡴࡵࠨ൚")]
      logger.info(bstack1l1lll1lll_opy_.format(CONFIG[bstack1ll_opy_ (u"ࠪࡥࡵࡶࠧ൛")]))
  else:
    bstack1lll1l1l11_opy_.clear()
  global bstack111lllll_opy_
  global bstack1l111l11ll_opy_
  if bstack11l1111ll_opy_:
    try:
      bstack1lll1ll11_opy_ = datetime.datetime.now()
      os.environ[bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭൜")] = bstack11111l111_opy_
      bstack11l1l1l111_opy_(bstack1l11111l11_opy_, CONFIG)
      cli.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽ࡷࡩࡱ࡟ࡵࡧࡶࡸࡤࡧࡴࡵࡧࡰࡴࡹ࡫ࡤࠣ൝"), datetime.datetime.now() - bstack1lll1ll11_opy_)
    except Exception as e:
      logger.debug(bstack111ll1l11_opy_.format(str(e)))
  global bstack1ll111ll11_opy_
  global bstack1lll11111l_opy_
  global bstack1lllllll11_opy_
  global bstack1l1ll11lll_opy_
  global bstack1lll1l11l_opy_
  global bstack1lllll111_opy_
  global bstack111l11l1_opy_
  global bstack1l1111llll_opy_
  global bstack11l1l111l_opy_
  global bstack111l1lll1_opy_
  global bstack1l111l11l_opy_
  global bstack11l11ll11l_opy_
  global bstack11lll1l11l_opy_
  global bstack1llll1l1l_opy_
  global bstack11llll11l1_opy_
  global bstack1l11l1ll11_opy_
  global bstack11l1111l1_opy_
  global bstack1l1l11l11_opy_
  global bstack1lll1lll1_opy_
  global bstack1lll1l1l_opy_
  global bstack11l11ll1ll_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1ll111ll11_opy_ = webdriver.Remote.__init__
    bstack1lll11111l_opy_ = WebDriver.quit
    bstack11l11ll11l_opy_ = WebDriver.close
    bstack11llll11l1_opy_ = WebDriver.get
    bstack11l11ll1ll_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack111lllll_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack11llll111l_opy_
    bstack1l111l11ll_opy_ = bstack11llll111l_opy_()
  except Exception as e:
    pass
  try:
    global bstack1l1ll111_opy_
    from QWeb.keywords import browser
    bstack1l1ll111_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack11lll1lll_opy_(CONFIG) and bstack1l1111l111_opy_():
    if bstack11l111ll1_opy_() < version.parse(bstack1l1lll111_opy_):
      logger.error(bstack1l1ll1l1l_opy_.format(bstack11l111ll1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        if hasattr(RemoteConnection, bstack1ll_opy_ (u"࠭࡟ࡨࡧࡷࡣࡵࡸ࡯ࡹࡻࡢࡹࡷࡲࠧ൞")) and callable(getattr(RemoteConnection, bstack1ll_opy_ (u"ࠧࡠࡩࡨࡸࡤࡶࡲࡰࡺࡼࡣࡺࡸ࡬ࠨൟ"))):
          RemoteConnection._get_proxy_url = bstack11l1llll_opy_
        else:
          from selenium.webdriver.remote.client_config import ClientConfig
          ClientConfig.get_proxy_url = bstack11l1llll_opy_
      except Exception as e:
        logger.error(bstack11lll11111_opy_.format(str(e)))
  if not CONFIG.get(bstack1ll_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡸࡸࡴࡉࡡࡱࡶࡸࡶࡪࡒ࡯ࡨࡵࠪൠ"), False) and not bstack11l1111ll_opy_:
    logger.info(bstack1111l11ll_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack1ll_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ൡ") in CONFIG and str(CONFIG[bstack1ll_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧൢ")]).lower() != bstack1ll_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪൣ"):
      bstack1l11llll1_opy_()
    elif bstack11111l111_opy_ != bstack1ll_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ൤") or (bstack11111l111_opy_ == bstack1ll_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭൥") and not bstack11l1111ll_opy_):
      bstack1lllllll1l_opy_()
  if (bstack11111l111_opy_ in [bstack1ll_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭൦"), bstack1ll_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ൧"), bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ൨")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1l1111111l_opy_
        bstack1lllll111_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack11l1ll11ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1lll1l11l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1l111ll1l_opy_ + str(e))
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack11l1ll11ll_opy_)
    if bstack11111l111_opy_ != bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ൩"):
      bstack11lll1111_opy_()
    bstack1lllllll11_opy_ = Output.start_test
    bstack1l1ll11lll_opy_ = Output.end_test
    bstack111l11l1_opy_ = TestStatus.__init__
    bstack11l1l111l_opy_ = pabot._run
    bstack111l1lll1_opy_ = QueueItem.__init__
    bstack1l111l11l_opy_ = pabot._create_command_for_execution
    bstack1lll1lll1_opy_ = pabot._report_results
  if bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ൪"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack1ll11lll1_opy_)
    bstack11lll1l11l_opy_ = Runner.run_hook
    bstack1llll1l1l_opy_ = Step.run
  if bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ൫"):
    try:
      from _pytest.config import Config
      bstack11l1111l1_opy_ = Config.getoption
      from _pytest import runner
      bstack1l1l11l11_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack1l1l11ll_opy_)
    try:
      from pytest_bdd import reporting
      bstack1lll1l1l_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹࡵࠠࡳࡷࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࡹࠧ൬"))
  try:
    framework_name = bstack1ll_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭൭") if bstack11111l111_opy_ in [bstack1ll_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ൮"), bstack1ll_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ൯"), bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ൰")] else bstack1llll1ll11_opy_(bstack11111l111_opy_)
    bstack1l11111111_opy_ = {
      bstack1ll_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࠬ൱"): bstack1ll_opy_ (u"ࠬࡖࡹࡵࡧࡶࡸ࠲ࡩࡵࡤࡷࡰࡦࡪࡸࠧ൲") if bstack11111l111_opy_ == bstack1ll_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭൳") and bstack1l11l1ll_opy_() else framework_name,
      bstack1ll_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫ൴"): bstack1lll1l1ll1_opy_(framework_name),
      bstack1ll_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭൵"): __version__,
      bstack1ll_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡻࡳࡦࡦࠪ൶"): bstack11111l111_opy_
    }
    if bstack11111l111_opy_ in bstack1ll111l1_opy_ + bstack1lllll1lll_opy_:
      if bstack1l11llll1l_opy_.bstack1ll111l11l_opy_(CONFIG):
        if bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ൷") in CONFIG:
          os.environ[bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬ൸")] = os.getenv(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭൹"), json.dumps(CONFIG[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ൺ")]))
          CONFIG[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧൻ")].pop(bstack1ll_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ർ"), None)
          CONFIG[bstack1ll_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩൽ")].pop(bstack1ll_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨൾ"), None)
        bstack1l11111111_opy_[bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫൿ")] = {
          bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ඀"): bstack1ll_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨඁ"),
          bstack1ll_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨං"): str(bstack11l111ll1_opy_())
        }
    if bstack11111l111_opy_ not in [bstack1ll_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩඃ")] and not cli.is_running():
      bstack1l111llll1_opy_, bstack1l1l111l_opy_ = bstack1l111111_opy_.launch(CONFIG, bstack1l11111111_opy_)
      if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ඄")) is not None and bstack1l11llll1l_opy_.bstack11lll111l_opy_(CONFIG) is None:
        value = bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪඅ")].get(bstack1ll_opy_ (u"ࠫࡸࡻࡣࡤࡧࡶࡷࠬආ"))
        if value is not None:
            CONFIG[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬඇ")] = value
        else:
          logger.debug(bstack1ll_opy_ (u"ࠨࡎࡰࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡧࡥࡹࡧࠠࡧࡱࡸࡲࡩࠦࡩ࡯ࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࠦඈ"))
  except Exception as e:
    logger.debug(bstack11ll1lll1l_opy_.format(bstack1ll_opy_ (u"ࠧࡕࡧࡶࡸࡍࡻࡢࠨඉ"), str(e)))
  if bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨඊ"):
    bstack11l11llll1_opy_ = True
    if bstack11l1111ll_opy_ and bstack1ll111l111_opy_:
      bstack1lll11llll_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭උ"), {}).get(bstack1ll_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬඌ"))
      bstack1ll11ll11_opy_(bstack1lll1l1ll_opy_)
    elif bstack11l1111ll_opy_:
      bstack1lll11llll_opy_ = CONFIG.get(bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨඍ"), {}).get(bstack1ll_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧඎ"))
      global bstack1llll1lll_opy_
      try:
        if bstack11111llll_opy_(bstack11l1111ll_opy_[bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩඏ")]) and multiprocessing.current_process().name == bstack1ll_opy_ (u"ࠧ࠱ࠩඐ"):
          bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫඑ")].remove(bstack1ll_opy_ (u"ࠩ࠰ࡱࠬඒ"))
          bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ඓ")].remove(bstack1ll_opy_ (u"ࠫࡵࡪࡢࠨඔ"))
          bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨඕ")] = bstack11l1111ll_opy_[bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩඖ")][0]
          with open(bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ඗")], bstack1ll_opy_ (u"ࠨࡴࠪ඘")) as f:
            bstack111l1l1ll_opy_ = f.read()
          bstack11111111l_opy_ = bstack1ll_opy_ (u"ࠤࠥࠦ࡫ࡸ࡯࡮ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡧ࡯ࠥ࡯࡭ࡱࡱࡵࡸࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥ࠼ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩ࠭ࢁࡽࠪ࠽ࠣࡪࡷࡵ࡭ࠡࡲࡧࡦࠥ࡯࡭ࡱࡱࡵࡸࠥࡖࡤࡣ࠽ࠣࡳ࡬ࡥࡤࡣࠢࡀࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࡸࡥࡢ࡭࠾ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡥࡧࡩࠤࡲࡵࡤࡠࡤࡵࡩࡦࡱࠨࡴࡧ࡯ࡪ࠱ࠦࡡࡳࡩ࠯ࠤࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠠ࠾ࠢ࠳࠭࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡹࡸࡹ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡤࡶ࡬ࠦ࠽ࠡࡵࡷࡶ࠭࡯࡮ࡵࠪࡤࡶ࡬࠯ࠫ࠲࠲ࠬࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡨࡼࡨ࡫ࡰࡵࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡧࡳࠡࡧ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡵࡧࡳࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡰࡩࡢࡨࡧ࠮ࡳࡦ࡮ࡩ࠰ࡦࡸࡧ࠭ࡶࡨࡱࡵࡵࡲࡢࡴࡼ࠭ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡒࡧࡦ࠳ࡪ࡯ࡠࡤࠣࡁࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࡸࡥࡢ࡭ࠣࡁࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡕࡪࡢࠩࠫ࠱ࡷࡪࡺ࡟ࡵࡴࡤࡧࡪ࠮ࠩ࡝ࡰࠥࠦࠧ඙").format(str(bstack11l1111ll_opy_))
          bstack1l11l11ll_opy_ = bstack11111111l_opy_ + bstack111l1l1ll_opy_
          bstack11lll1l111_opy_ = bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ක")] + bstack1ll_opy_ (u"ࠫࡤࡨࡳࡵࡣࡦ࡯ࡤࡺࡥ࡮ࡲ࠱ࡴࡾ࠭ඛ")
          with open(bstack11lll1l111_opy_, bstack1ll_opy_ (u"ࠬࡽࠧග")):
            pass
          with open(bstack11lll1l111_opy_, bstack1ll_opy_ (u"ࠨࡷࠬࠤඝ")) as f:
            f.write(bstack1l11l11ll_opy_)
          import subprocess
          bstack1ll1l1l11l_opy_ = subprocess.run([bstack1ll_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢඞ"), bstack11lll1l111_opy_])
          if os.path.exists(bstack11lll1l111_opy_):
            os.unlink(bstack11lll1l111_opy_)
          os._exit(bstack1ll1l1l11l_opy_.returncode)
        else:
          if bstack11111llll_opy_(bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫඟ")]):
            bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬච")].remove(bstack1ll_opy_ (u"ࠪ࠱ࡲ࠭ඡ"))
            bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧජ")].remove(bstack1ll_opy_ (u"ࠬࡶࡤࡣࠩඣ"))
            bstack11l1111ll_opy_[bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩඤ")] = bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪඥ")][0]
          bstack1ll11ll11_opy_(bstack1lll1l1ll_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫඦ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1ll_opy_ (u"ࠩࡢࡣࡳࡧ࡭ࡦࡡࡢࠫට")] = bstack1ll_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬඨ")
          mod_globals[bstack1ll_opy_ (u"ࠫࡤࡥࡦࡪ࡮ࡨࡣࡤ࠭ඩ")] = os.path.abspath(bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨඪ")])
          exec(open(bstack11l1111ll_opy_[bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩණ")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1ll_opy_ (u"ࠧࡄࡣࡸ࡫࡭ࡺࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰ࠽ࠤࢀࢃࠧඬ").format(str(e)))
          for driver in bstack1llll1lll_opy_:
            bstack1111111ll_opy_.append({
              bstack1ll_opy_ (u"ࠨࡰࡤࡱࡪ࠭ත"): bstack11l1111ll_opy_[bstack1ll_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬථ")],
              bstack1ll_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩද"): str(e),
              bstack1ll_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪධ"): multiprocessing.current_process().name
            })
            bstack11llll111_opy_(driver, bstack1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬන"), bstack1ll_opy_ (u"ࠨࡓࡦࡵࡶ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤ඲") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1llll1lll_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack1l11lll1_opy_, CONFIG, logger)
      bstack1lll1lll1l_opy_()
      bstack111lll11l_opy_()
      percy.bstack11l1ll11l1_opy_()
      bstack1llllll1ll_opy_ = {
        bstack1ll_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪඳ"): args[0],
        bstack1ll_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨප"): CONFIG,
        bstack1ll_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪඵ"): bstack11llll1l1_opy_,
        bstack1ll_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬබ"): bstack1l11lll1_opy_
      }
      if bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧභ") in CONFIG:
        bstack1l11ll1l1l_opy_ = bstack1llllll11l_opy_(args, logger, CONFIG, bstack1lllll11_opy_, bstack1ll1111ll1_opy_)
        bstack1l11ll11_opy_ = bstack1l11ll1l1l_opy_.bstack1l1l1ll11_opy_(run_on_browserstack, bstack1llllll1ll_opy_, bstack11111llll_opy_(args))
      else:
        if bstack11111llll_opy_(args):
          bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨම")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1llllll1ll_opy_,))
          test.start()
          test.join()
        else:
          bstack1ll11ll11_opy_(bstack1lll1l1ll_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1ll_opy_ (u"࠭࡟ࡠࡰࡤࡱࡪࡥ࡟ࠨඹ")] = bstack1ll_opy_ (u"ࠧࡠࡡࡰࡥ࡮ࡴ࡟ࡠࠩය")
          mod_globals[bstack1ll_opy_ (u"ࠨࡡࡢࡪ࡮ࡲࡥࡠࡡࠪර")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨ඼") or bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩල"):
    percy.init(bstack1l11lll1_opy_, CONFIG, logger)
    percy.bstack11l1ll11l1_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack11l1ll11ll_opy_)
    bstack1lll1lll1l_opy_()
    bstack1ll11ll11_opy_(bstack11111ll11_opy_)
    if bstack1lllll11_opy_:
      bstack111lll1l1_opy_(bstack11111ll11_opy_, args)
      if bstack1ll_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩ඾") in args:
        i = args.index(bstack1ll_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪ඿"))
        args.pop(i)
        args.pop(i)
      if bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩව") not in CONFIG:
        CONFIG[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪශ")] = [{}]
        bstack1ll1111ll1_opy_ = 1
      if bstack11l11l1lll_opy_ == 0:
        bstack11l11l1lll_opy_ = 1
      args.insert(0, str(bstack11l11l1lll_opy_))
      args.insert(0, str(bstack1ll_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ෂ")))
    if bstack1l111111_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack1ll1l1l1_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack1l1l1l111_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack1ll_opy_ (u"ࠤࡕࡓࡇࡕࡔࡠࡑࡓࡘࡎࡕࡎࡔࠤස"),
        ).parse_args(bstack1ll1l1l1_opy_)
        bstack11lll1l1l1_opy_ = args.index(bstack1ll1l1l1_opy_[0]) if len(bstack1ll1l1l1_opy_) > 0 else len(args)
        args.insert(bstack11lll1l1l1_opy_, str(bstack1ll_opy_ (u"ࠪ࠱࠲ࡲࡩࡴࡶࡨࡲࡪࡸࠧහ")))
        args.insert(bstack11lll1l1l1_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡷࡵࡢࡰࡶࡢࡰ࡮ࡹࡴࡦࡰࡨࡶ࠳ࡶࡹࠨළ"))))
        if bstack1ll1ll1ll_opy_.bstack1l1ll11111_opy_(CONFIG):
          args.insert(bstack11lll1l1l1_opy_, str(bstack1ll_opy_ (u"ࠬ࠳࠭࡭࡫ࡶࡸࡪࡴࡥࡳࠩෆ")))
          args.insert(bstack11lll1l1l1_opy_ + 1, str(bstack1ll_opy_ (u"࠭ࡒࡦࡶࡵࡽࡋࡧࡩ࡭ࡧࡧ࠾ࢀࢃࠧ෇").format(bstack1ll1ll1ll_opy_.bstack1ll1l1l11_opy_(CONFIG))))
        if bstack11ll1lllll_opy_(os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࠬ෈"))) and str(os.environ.get(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬ෉"), bstack1ll_opy_ (u"ࠩࡱࡹࡱࡲ්ࠧ"))) != bstack1ll_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ෋"):
          for bstack1ll1llll11_opy_ in bstack1l1l1l111_opy_:
            args.remove(bstack1ll1llll11_opy_)
          bstack1lll11lll1_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࡡࡗࡉࡘ࡚ࡓࠨ෌")).split(bstack1ll_opy_ (u"ࠬ࠲ࠧ෍"))
          for bstack11llll1l1l_opy_ in bstack1lll11lll1_opy_:
            args.append(bstack11llll1l1l_opy_)
      except Exception as e:
        logger.error(bstack1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡦࡺࡴࡢࡥ࡫࡭ࡳ࡭ࠠ࡭࡫ࡶࡸࡪࡴࡥࡳࠢࡩࡳࡷࠦࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠴ࠠࡆࡴࡵࡳࡷࠦ࠭ࠡࠤ෎").format(e))
    pabot.main(args)
  elif bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨා"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack11l1ll11ll_opy_)
    for a in args:
      if bstack1ll_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞ࠧැ") in a:
        bstack1l1111ll_opy_ = int(a.split(bstack1ll_opy_ (u"ࠩ࠽ࠫෑ"))[1])
      if bstack1ll_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡇࡉࡋࡒࡏࡄࡃࡏࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧි") in a:
        bstack1lll11llll_opy_ = str(a.split(bstack1ll_opy_ (u"ࠫ࠿࠭ී"))[1])
      if bstack1ll_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡈࡒࡉࡂࡔࡊࡗࠬු") in a:
        bstack1l111lll1l_opy_ = str(a.split(bstack1ll_opy_ (u"࠭࠺ࠨ෕"))[1])
    bstack1llll1l11_opy_ = None
    if bstack1ll_opy_ (u"ࠧ࠮࠯ࡥࡷࡹࡧࡣ࡬ࡡ࡬ࡸࡪࡳ࡟ࡪࡰࡧࡩࡽ࠭ූ") in args:
      i = args.index(bstack1ll_opy_ (u"ࠨ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾࠧ෗"))
      args.pop(i)
      bstack1llll1l11_opy_ = args.pop(i)
    if bstack1llll1l11_opy_ is not None:
      global bstack1l111ll11_opy_
      bstack1l111ll11_opy_ = bstack1llll1l11_opy_
    bstack1ll11ll11_opy_(bstack11111ll11_opy_)
    run_cli(args)
    if bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠭ෘ") in multiprocessing.current_process().__dict__.keys():
      for bstack11lll1111l_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1111111ll_opy_.append(bstack11lll1111l_opy_)
  elif bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪෙ"):
    bstack1ll11111ll_opy_ = bstack11l1l11111_opy_(args, logger, CONFIG, bstack1lllll11_opy_)
    bstack1ll11111ll_opy_.bstack1l1lll1ll_opy_()
    bstack1lll1lll1l_opy_()
    bstack1l1lll1111_opy_ = True
    bstack1llll1ll1l_opy_ = bstack1ll11111ll_opy_.bstack1ll11ll1_opy_()
    bstack1ll11111ll_opy_.bstack1llllll1ll_opy_(bstack11l111l1l1_opy_)
    bstack11ll1111_opy_ = bstack1ll11111ll_opy_.bstack1l1l1ll11_opy_(bstack11ll1ll1ll_opy_, {
      bstack1ll_opy_ (u"ࠫࡍ࡛ࡂࡠࡗࡕࡐࠬේ"): bstack11llll1l1_opy_,
      bstack1ll_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧෛ"): bstack1l11lll1_opy_,
      bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩො"): bstack1lllll11_opy_
    })
    try:
      bstack111ll1ll1_opy_, bstack11l1l1111l_opy_ = map(list, zip(*bstack11ll1111_opy_))
      bstack1111l11l_opy_ = bstack111ll1ll1_opy_[0]
      for status_code in bstack11l1l1111l_opy_:
        if status_code != 0:
          bstack1l11l1l111_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack1ll_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡦࡼࡥࠡࡧࡵࡶࡴࡸࡳࠡࡣࡱࡨࠥࡹࡴࡢࡶࡸࡷࠥࡩ࡯ࡥࡧ࠱ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠ࠻ࠢࡾࢁࠧෝ").format(str(e)))
  elif bstack11111l111_opy_ == bstack1ll_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨෞ"):
    try:
      from behave.__main__ import main as bstack1llllll111_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack11l1l111l1_opy_(e, bstack1ll11lll1_opy_)
    bstack1lll1lll1l_opy_()
    bstack1l1lll1111_opy_ = True
    bstack1ll111lll1_opy_ = 1
    if bstack1ll_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩෟ") in CONFIG:
      bstack1ll111lll1_opy_ = CONFIG[bstack1ll_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ෠")]
    if bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ෡") in CONFIG:
      bstack1l11l1111l_opy_ = int(bstack1ll111lll1_opy_) * int(len(CONFIG[bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ෢")]))
    else:
      bstack1l11l1111l_opy_ = int(bstack1ll111lll1_opy_)
    config = Configuration(args)
    bstack1l1lll1l1l_opy_ = config.paths
    if len(bstack1l1lll1l1l_opy_) == 0:
      import glob
      pattern = bstack1ll_opy_ (u"࠭ࠪࠫ࠱࠭࠲࡫࡫ࡡࡵࡷࡵࡩࠬ෣")
      bstack1ll1llll1_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1ll1llll1_opy_)
      config = Configuration(args)
      bstack1l1lll1l1l_opy_ = config.paths
    bstack1l1ll1l1_opy_ = [os.path.normpath(item) for item in bstack1l1lll1l1l_opy_]
    bstack1l111l111_opy_ = [os.path.normpath(item) for item in args]
    bstack1llll11ll1_opy_ = [item for item in bstack1l111l111_opy_ if item not in bstack1l1ll1l1_opy_]
    import platform as pf
    if pf.system().lower() == bstack1ll_opy_ (u"ࠧࡸ࡫ࡱࡨࡴࡽࡳࠨ෤"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l1ll1l1_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11lll11lll_opy_)))
                    for bstack11lll11lll_opy_ in bstack1l1ll1l1_opy_]
    bstack1ll111l11_opy_ = []
    for spec in bstack1l1ll1l1_opy_:
      bstack1ll111111_opy_ = []
      bstack1ll111111_opy_ += bstack1llll11ll1_opy_
      bstack1ll111111_opy_.append(spec)
      bstack1ll111l11_opy_.append(bstack1ll111111_opy_)
    execution_items = []
    for bstack1ll111111_opy_ in bstack1ll111l11_opy_:
      if bstack1ll_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ෥") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ෦")]):
          item = {}
          item[bstack1ll_opy_ (u"ࠪࡥࡷ࡭ࠧ෧")] = bstack1ll_opy_ (u"ࠫࠥ࠭෨").join(bstack1ll111111_opy_)
          item[bstack1ll_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ෩")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack1ll_opy_ (u"࠭ࡡࡳࡩࠪ෪")] = bstack1ll_opy_ (u"ࠧࠡࠩ෫").join(bstack1ll111111_opy_)
        item[bstack1ll_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧ෬")] = 0
        execution_items.append(item)
    bstack1lllll1l1l_opy_ = bstack1l1lll11ll_opy_(execution_items, bstack1l11l1111l_opy_)
    for execution_item in bstack1lllll1l1l_opy_:
      bstack11111l11l_opy_ = []
      for item in execution_item:
        bstack11111l11l_opy_.append(bstack11l11l11l1_opy_(name=str(item[bstack1ll_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ෭")]),
                                             target=bstack1ll1111l1_opy_,
                                             args=(item[bstack1ll_opy_ (u"ࠪࡥࡷ࡭ࠧ෮")],)))
      for t in bstack11111l11l_opy_:
        t.start()
      for t in bstack11111l11l_opy_:
        t.join()
  else:
    bstack1l11l11l1l_opy_(bstack11l1l1l11l_opy_)
  if not bstack11l1111ll_opy_:
    bstack1l1111lll_opy_()
    if(bstack11111l111_opy_ in [bstack1ll_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ෯"), bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ෰")]):
      bstack11ll11l11_opy_()
  bstack111ll11ll_opy_.bstack1l1lllll1l_opy_()
def browserstack_initialize(bstack1ll1111lll_opy_=None):
  logger.info(bstack1ll_opy_ (u"࠭ࡒࡶࡰࡱ࡭ࡳ࡭ࠠࡔࡆࡎࠤࡼ࡯ࡴࡩࠢࡤࡶ࡬ࡹ࠺ࠡࠩ෱") + str(bstack1ll1111lll_opy_))
  run_on_browserstack(bstack1ll1111lll_opy_, None, True)
@measure(event_name=EVENTS.bstack11ll1ll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1l1111lll_opy_():
  global CONFIG
  global bstack1l11ll1l11_opy_
  global bstack1l11l1l111_opy_
  global bstack1l111l1l1_opy_
  global bstack1lll1111ll_opy_
  bstack1ll11l1111_opy_.bstack1l1l1lll_opy_()
  if cli.is_running():
    bstack1lll1l1l11_opy_.invoke(bstack1l1lll11l1_opy_.bstack1l1l1llll_opy_)
  if bstack1l11ll1l11_opy_ == bstack1ll_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧෲ"):
    if not cli.is_enabled(CONFIG):
      bstack1l111111_opy_.stop()
  else:
    bstack1l111111_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack11llllll1l_opy_.bstack1lllllll1_opy_()
  if bstack1ll_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬෳ") in CONFIG and str(CONFIG[bstack1ll_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭෴")]).lower() != bstack1ll_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩ෵"):
    bstack1l11lllll_opy_, bstack1ll11ll111_opy_ = bstack1l1lll1l_opy_()
  else:
    bstack1l11lllll_opy_, bstack1ll11ll111_opy_ = get_build_link()
  bstack1ll1l1ll11_opy_(bstack1l11lllll_opy_)
  logger.info(bstack1ll_opy_ (u"ࠫࡘࡊࡋࠡࡴࡸࡲࠥ࡫࡮ࡥࡧࡧࠤ࡫ࡵࡲࠡ࡫ࡧ࠾ࠬ෶") + bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ෷"), bstack1ll_opy_ (u"࠭ࠧ෸")) + bstack1ll_opy_ (u"ࠧ࠭ࠢࡷࡩࡸࡺࡨࡶࡤࠣ࡭ࡩࡀࠠࠨ෹") + os.getenv(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭෺"), bstack1ll_opy_ (u"ࠩࠪ෻")))
  if bstack1l11lllll_opy_ is not None and bstack1ll1ll1lll_opy_() != -1:
    sessions = bstack1lll111ll_opy_(bstack1l11lllll_opy_)
    bstack111ll1111_opy_(sessions, bstack1ll11ll111_opy_)
  if bstack1l11ll1l11_opy_ == bstack1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ෼") and bstack1l11l1l111_opy_ != 0:
    sys.exit(bstack1l11l1l111_opy_)
  if bstack1l11ll1l11_opy_ == bstack1ll_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ෽") and bstack1l111l1l1_opy_ != 0:
    sys.exit(bstack1l111l1l1_opy_)
def bstack1ll1l1ll11_opy_(new_id):
    global bstack11ll11ll1_opy_
    bstack11ll11ll1_opy_ = new_id
def bstack1llll1ll11_opy_(bstack1l1l11lll_opy_):
  if bstack1l1l11lll_opy_:
    return bstack1l1l11lll_opy_.capitalize()
  else:
    return bstack1ll_opy_ (u"ࠬ࠭෾")
@measure(event_name=EVENTS.bstack11l11l111_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack11ll11lll_opy_(bstack11ll111l1_opy_):
  if bstack1ll_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ෿") in bstack11ll111l1_opy_ and bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ฀")] != bstack1ll_opy_ (u"ࠨࠩก"):
    return bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧข")]
  else:
    bstack1lll11l11_opy_ = bstack1ll_opy_ (u"ࠥࠦฃ")
    if bstack1ll_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫค") in bstack11ll111l1_opy_ and bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬฅ")] != None:
      bstack1lll11l11_opy_ += bstack11ll111l1_opy_[bstack1ll_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ฆ")] + bstack1ll_opy_ (u"ࠢ࠭ࠢࠥง")
      if bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠨࡱࡶࠫจ")] == bstack1ll_opy_ (u"ࠤ࡬ࡳࡸࠨฉ"):
        bstack1lll11l11_opy_ += bstack1ll_opy_ (u"ࠥ࡭ࡔ࡙ࠠࠣช")
      bstack1lll11l11_opy_ += (bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨซ")] or bstack1ll_opy_ (u"ࠬ࠭ฌ"))
      return bstack1lll11l11_opy_
    else:
      bstack1lll11l11_opy_ += bstack1llll1ll11_opy_(bstack11ll111l1_opy_[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧญ")]) + bstack1ll_opy_ (u"ࠢࠡࠤฎ") + (
              bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪฏ")] or bstack1ll_opy_ (u"ࠩࠪฐ")) + bstack1ll_opy_ (u"ࠥ࠰ࠥࠨฑ")
      if bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠫࡴࡹࠧฒ")] == bstack1ll_opy_ (u"ࠧ࡝ࡩ࡯ࡦࡲࡻࡸࠨณ"):
        bstack1lll11l11_opy_ += bstack1ll_opy_ (u"ࠨࡗࡪࡰࠣࠦด")
      bstack1lll11l11_opy_ += bstack11ll111l1_opy_[bstack1ll_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫต")] or bstack1ll_opy_ (u"ࠨࠩถ")
      return bstack1lll11l11_opy_
@measure(event_name=EVENTS.bstack1111lllll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack1ll111ll1_opy_(bstack1l111l1l11_opy_):
  if bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠤࡧࡳࡳ࡫ࠢท"):
    return bstack1ll_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿࡭ࡲࡦࡧࡱ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧ࡭ࡲࡦࡧࡱࠦࡃࡉ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ธ")
  elif bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦน"):
    return bstack1ll_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡳࡧࡧ࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࡸࡥࡥࠤࡁࡊࡦ࡯࡬ࡦࡦ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨบ")
  elif bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠨࡰࡢࡵࡶࡩࡩࠨป"):
    return bstack1ll_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡪࡶࡪ࡫࡮࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡪࡶࡪ࡫࡮ࠣࡀࡓࡥࡸࡹࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧผ")
  elif bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢฝ"):
    return bstack1ll_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࡷ࡫ࡤ࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡵࡩࡩࠨ࠾ࡆࡴࡵࡳࡷࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫพ")
  elif bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷࠦฟ"):
    return bstack1ll_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࠣࡦࡧࡤ࠷࠷࠼࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࠥࡨࡩࡦ࠹࠲࠷ࠤࡁࡘ࡮ࡳࡥࡰࡷࡷࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩภ")
  elif bstack1l111l1l11_opy_ == bstack1ll_opy_ (u"ࠧࡸࡵ࡯ࡰ࡬ࡲ࡬ࠨม"):
    return bstack1ll_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡤ࡯ࡥࡨࡱ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡤ࡯ࡥࡨࡱࠢ࠿ࡔࡸࡲࡳ࡯࡮ࡨ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧย")
  else:
    return bstack1ll_opy_ (u"ࠧ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡦࡱࡧࡣ࡬࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡦࡱࡧࡣ࡬ࠤࡁࠫร") + bstack1llll1ll11_opy_(
      bstack1l111l1l11_opy_) + bstack1ll_opy_ (u"ࠨ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧฤ")
def bstack11111ll1_opy_(session):
  return bstack1ll_opy_ (u"ࠩ࠿ࡸࡷࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡲࡰࡹࠥࡂࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠦࡳࡦࡵࡶ࡭ࡴࡴ࠭࡯ࡣࡰࡩࠧࡄ࠼ࡢࠢ࡫ࡶࡪ࡬࠽ࠣࡽࢀࠦࠥࡺࡡࡳࡩࡨࡸࡂࠨ࡟ࡣ࡮ࡤࡲࡰࠨ࠾ࡼࡿ࠿࠳ࡦࡄ࠼࠰ࡶࡧࡂࢀࢃࡻࡾ࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࡄࡻࡾ࠾࠲ࡸࡩࡄ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀ࠴ࡺࡲ࠿ࠩล").format(
    session[bstack1ll_opy_ (u"ࠪࡴࡺࡨ࡬ࡪࡥࡢࡹࡷࡲࠧฦ")], bstack11ll11lll_opy_(session), bstack1ll111ll1_opy_(session[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡷࡹࡧࡴࡶࡵࠪว")]),
    bstack1ll111ll1_opy_(session[bstack1ll_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬศ")]),
    bstack1llll1ll11_opy_(session[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧษ")] or session[bstack1ll_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧส")] or bstack1ll_opy_ (u"ࠨࠩห")) + bstack1ll_opy_ (u"ࠤࠣࠦฬ") + (session[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬอ")] or bstack1ll_opy_ (u"ࠫࠬฮ")),
    session[bstack1ll_opy_ (u"ࠬࡵࡳࠨฯ")] + bstack1ll_opy_ (u"ࠨࠠࠣะ") + session[bstack1ll_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫั")], session[bstack1ll_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪา")] or bstack1ll_opy_ (u"ࠩࠪำ"),
    session[bstack1ll_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧิ")] if session[bstack1ll_opy_ (u"ࠫࡨࡸࡥࡢࡶࡨࡨࡤࡧࡴࠨี")] else bstack1ll_opy_ (u"ࠬ࠭ึ"))
@measure(event_name=EVENTS.bstack1l1l1llll1_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def bstack111ll1111_opy_(sessions, bstack1ll11ll111_opy_):
  try:
    bstack1l1l1l1ll1_opy_ = bstack1ll_opy_ (u"ࠨࠢื")
    if not os.path.exists(bstack1l1l1lllll_opy_):
      os.mkdir(bstack1l1l1lllll_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1ll_opy_ (u"ࠧࡢࡵࡶࡩࡹࡹ࠯ࡳࡧࡳࡳࡷࡺ࠮ࡩࡶࡰࡰุࠬ")), bstack1ll_opy_ (u"ࠨࡴูࠪ")) as f:
      bstack1l1l1l1ll1_opy_ = f.read()
    bstack1l1l1l1ll1_opy_ = bstack1l1l1l1ll1_opy_.replace(bstack1ll_opy_ (u"ࠩࡾࠩࡗࡋࡓࡖࡎࡗࡗࡤࡉࡏࡖࡐࡗࠩࢂฺ࠭"), str(len(sessions)))
    bstack1l1l1l1ll1_opy_ = bstack1l1l1l1ll1_opy_.replace(bstack1ll_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠦࡿࠪ฻"), bstack1ll11ll111_opy_)
    bstack1l1l1l1ll1_opy_ = bstack1l1l1l1ll1_opy_.replace(bstack1ll_opy_ (u"ࠫࢀࠫࡂࡖࡋࡏࡈࡤࡔࡁࡎࡇࠨࢁࠬ฼"),
                                              sessions[0].get(bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣࡳࡧ࡭ࡦࠩ฽")) if sessions[0] else bstack1ll_opy_ (u"࠭ࠧ฾"))
    with open(os.path.join(bstack1l1l1lllll_opy_, bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫ฿")), bstack1ll_opy_ (u"ࠨࡹࠪเ")) as stream:
      stream.write(bstack1l1l1l1ll1_opy_.split(bstack1ll_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭แ"))[0])
      for session in sessions:
        stream.write(bstack11111ll1_opy_(session))
      stream.write(bstack1l1l1l1ll1_opy_.split(bstack1ll_opy_ (u"ࠪࡿ࡙ࠪࡅࡔࡕࡌࡓࡓ࡙࡟ࡅࡃࡗࡅࠪࢃࠧโ"))[1])
    logger.info(bstack1ll_opy_ (u"ࠫࡌ࡫࡮ࡦࡴࡤࡸࡪࡪࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡢࡶ࡫࡯ࡨࠥࡧࡲࡵ࡫ࡩࡥࡨࡺࡳࠡࡣࡷࠤࢀࢃࠧใ").format(bstack1l1l1lllll_opy_));
  except Exception as e:
    logger.debug(bstack1lll111l11_opy_.format(str(e)))
def bstack1lll111ll_opy_(bstack1l11lllll_opy_):
  global CONFIG
  try:
    bstack1lll1ll11_opy_ = datetime.datetime.now()
    host = bstack1ll_opy_ (u"ࠬࡧࡰࡪ࠯ࡦࡰࡴࡻࡤࠨไ") if bstack1ll_opy_ (u"࠭ࡡࡱࡲࠪๅ") in CONFIG else bstack1ll_opy_ (u"ࠧࡢࡲ࡬ࠫๆ")
    user = CONFIG[bstack1ll_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪ็")]
    key = CONFIG[bstack1ll_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽ่ࠬ")]
    bstack11l1l1llll_opy_ = bstack1ll_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦ้ࠩ") if bstack1ll_opy_ (u"ࠫࡦࡶࡰࠨ๊") in CONFIG else (bstack1ll_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦ๋ࠩ") if CONFIG.get(bstack1ll_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪ์")) else bstack1ll_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩํ"))
    url = bstack1ll_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡽࢀ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂ࠵ࡳࡦࡵࡶ࡭ࡴࡴࡳ࠯࡬ࡶࡳࡳ࠭๎").format(user, key, host, bstack11l1l1llll_opy_,
                                                                                bstack1l11lllll_opy_)
    headers = {
      bstack1ll_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨ๏"): bstack1ll_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭๐"),
    }
    proxies = bstack1ll1l111l1_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      cli.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼ࡪࡩࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࡠ࡮࡬ࡷࡹࠨ๑"), datetime.datetime.now() - bstack1lll1ll11_opy_)
      return list(map(lambda session: session[bstack1ll_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠪ๒")], response.json()))
  except Exception as e:
    logger.debug(bstack11l1ll1l_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack1llll111l_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def get_build_link():
  global CONFIG
  global bstack11ll11ll1_opy_
  try:
    if bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ๓") in CONFIG:
      bstack1lll1ll11_opy_ = datetime.datetime.now()
      host = bstack1ll_opy_ (u"ࠧࡢࡲ࡬࠱ࡨࡲ࡯ࡶࡦࠪ๔") if bstack1ll_opy_ (u"ࠨࡣࡳࡴࠬ๕") in CONFIG else bstack1ll_opy_ (u"ࠩࡤࡴ࡮࠭๖")
      user = CONFIG[bstack1ll_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ๗")]
      key = CONFIG[bstack1ll_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ๘")]
      bstack11l1l1llll_opy_ = bstack1ll_opy_ (u"ࠬࡧࡰࡱ࠯ࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ๙") if bstack1ll_opy_ (u"࠭ࡡࡱࡲࠪ๚") in CONFIG else bstack1ll_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩ๛")
      url = bstack1ll_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱ࡾࢁ࠿ࢁࡽࡁࡽࢀ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡼࡿ࠲ࡦࡺ࡯࡬ࡥࡵ࠱࡮ࡸࡵ࡮ࠨ๜").format(user, key, host, bstack11l1l1llll_opy_)
      if cli.is_enabled(CONFIG):
        bstack1ll11ll111_opy_, bstack1l11lllll_opy_ = cli.bstack1l111111l1_opy_()
        logger.info(bstack1lllll11l1_opy_.format(bstack1ll11ll111_opy_))
        return [bstack1l11lllll_opy_, bstack1ll11ll111_opy_]
      else:
        headers = {
          bstack1ll_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨ๝"): bstack1ll_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭๞"),
        }
        if bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭๟") in CONFIG:
          params = {bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๠"): CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ๡")], bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ๢"): CONFIG[bstack1ll_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ๣")]}
        else:
          params = {bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ๤"): CONFIG[bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭๥")]}
        proxies = bstack1ll1l111l1_opy_(CONFIG, url)
        response = requests.get(url, params=params, headers=headers, proxies=proxies)
        if response.json():
          bstack1ll1lll11_opy_ = response.json()[0][bstack1ll_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡤࡸ࡭ࡱࡪࠧ๦")]
          if bstack1ll1lll11_opy_:
            bstack1ll11ll111_opy_ = bstack1ll1lll11_opy_[bstack1ll_opy_ (u"ࠬࡶࡵࡣ࡮࡬ࡧࡤࡻࡲ࡭ࠩ๧")].split(bstack1ll_opy_ (u"࠭ࡰࡶࡤ࡯࡭ࡨ࠳ࡢࡶ࡫࡯ࡨࠬ๨"))[0] + bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡹ࠯ࠨ๩") + bstack1ll1lll11_opy_[
              bstack1ll_opy_ (u"ࠨࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫ๪")]
            logger.info(bstack1lllll11l1_opy_.format(bstack1ll11ll111_opy_))
            bstack11ll11ll1_opy_ = bstack1ll1lll11_opy_[bstack1ll_opy_ (u"ࠩ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬ๫")]
            bstack1ll11lll1l_opy_ = CONFIG[bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭๬")]
            if bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭๭") in CONFIG:
              bstack1ll11lll1l_opy_ += bstack1ll_opy_ (u"ࠬࠦࠧ๮") + CONFIG[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ๯")]
            if bstack1ll11lll1l_opy_ != bstack1ll1lll11_opy_[bstack1ll_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ๰")]:
              logger.debug(bstack1l111l1lll_opy_.format(bstack1ll1lll11_opy_[bstack1ll_opy_ (u"ࠨࡰࡤࡱࡪ࠭๱")], bstack1ll11lll1l_opy_))
            cli.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺ࡨࡧࡷࡣࡧࡻࡩ࡭ࡦࡢࡰ࡮ࡴ࡫ࠣ๲"), datetime.datetime.now() - bstack1lll1ll11_opy_)
            return [bstack1ll1lll11_opy_[bstack1ll_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭๳")], bstack1ll11ll111_opy_]
    else:
      logger.warn(bstack1l1l1111l1_opy_)
  except Exception as e:
    logger.debug(bstack11l1l11l_opy_.format(str(e)))
  return [None, None]
def bstack11lll111ll_opy_(url, bstack1111l1l11_opy_=False):
  global CONFIG
  global bstack1llllll1l1_opy_
  if not bstack1llllll1l1_opy_:
    hostname = bstack11l1lllll_opy_(url)
    is_private = bstack11ll11ll11_opy_(hostname)
    if (bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ๴") in CONFIG and not bstack11ll1lllll_opy_(CONFIG[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ๵")])) and (is_private or bstack1111l1l11_opy_):
      bstack1llllll1l1_opy_ = hostname
def bstack11l1lllll_opy_(url):
  return urlparse(url).hostname
def bstack11ll11ll11_opy_(hostname):
  for bstack1ll11l1l1l_opy_ in bstack1ll11l1l_opy_:
    regex = re.compile(bstack1ll11l1l1l_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack11ll11111_opy_(bstack1111l111l_opy_):
  return True if bstack1111l111l_opy_ in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack1lll1111l_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack1l1111ll_opy_
  bstack1ll11111l1_opy_ = not (bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪ๶"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭๷"), None))
  bstack111l1lll_opy_ = getattr(driver, bstack1ll_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ๸"), None) != True
  bstack11l11ll1_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩ࡬ࡷࡆࡶࡰࡂ࠳࠴ࡽ࡙࡫ࡳࡵࠩ๹"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠪࡥࡵࡶࡁ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ๺"), None)
  if bstack11l11ll1_opy_:
    if not bstack111ll1l1l_opy_():
      logger.warning(bstack1ll_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡶࡰࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡹࡥࡴࡵ࡬ࡳࡳ࠲ࠠࡤࡣࡱࡲࡴࡺࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࠢࡄࡴࡵࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹ࠮ࠣ๻"))
      return {}
    logger.debug(bstack1ll_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩ๼"))
    logger.debug(perform_scan(driver, driver_command=bstack1ll_opy_ (u"࠭ࡥࡹࡧࡦࡹࡹ࡫ࡓࡤࡴ࡬ࡴࡹ࠭๽")))
    results = bstack11l1l1lll_opy_(bstack1ll_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡳࠣ๾"))
    if results is not None and results.get(bstack1ll_opy_ (u"ࠣ࡫ࡶࡷࡺ࡫ࡳࠣ๿")) is not None:
        return results[bstack1ll_opy_ (u"ࠤ࡬ࡷࡸࡻࡥࡴࠤ຀")]
    logger.error(bstack1ll_opy_ (u"ࠥࡒࡴࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡒࡦࡵࡸࡰࡹࡹࠠࡸࡧࡵࡩࠥ࡬࡯ࡶࡰࡧ࠲ࠧກ"))
    return []
  if not bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1111ll_opy_) or (bstack111l1lll_opy_ and bstack1ll11111l1_opy_):
    logger.warning(bstack1ll_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡪࡺࡲࡪࡧࡹࡩࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸ࠴ࠢຂ"))
    return {}
  try:
    logger.debug(bstack1ll_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡴࡨࡷࡺࡲࡴࡴࠩ຃"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack1l11l1l1l_opy_.bstack11l111l1_opy_)
    return results
  except Exception:
    logger.error(bstack1ll_opy_ (u"ࠨࡎࡰࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡻࡪࡸࡥࠡࡨࡲࡹࡳࡪ࠮ࠣຄ"))
    return {}
@measure(event_name=EVENTS.bstack1l1111ll1l_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack1l1111ll_opy_
  bstack1ll11111l1_opy_ = not (bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡪࡵࡄ࠵࠶ࡿࡔࡦࡵࡷࠫ຅"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧຆ"), None))
  bstack111l1lll_opy_ = getattr(driver, bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩງ"), None) != True
  bstack11l11ll1_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠪ࡭ࡸࡇࡰࡱࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪຈ"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠫࡦࡶࡰࡂ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ຉ"), None)
  if bstack11l11ll1_opy_:
    if not bstack111ll1l1l_opy_():
      logger.warning(bstack1ll_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡰࡱࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡳࡦࡵࡶ࡭ࡴࡴࠬࠡࡥࡤࡲࡳࡵࡴࠡࡴࡨࡸࡷ࡯ࡥࡷࡧࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳࠡࡵࡸࡱࡲࡧࡲࡺ࠰ࠥຊ"))
      return {}
    logger.debug(bstack1ll_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼࠫ຋"))
    logger.debug(perform_scan(driver, driver_command=bstack1ll_opy_ (u"ࠧࡦࡺࡨࡧࡺࡺࡥࡔࡥࡵ࡭ࡵࡺࠧຌ")))
    results = bstack11l1l1lll_opy_(bstack1ll_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡔࡷࡰࡱࡦࡸࡹࠣຍ"))
    if results is not None and results.get(bstack1ll_opy_ (u"ࠤࡶࡹࡲࡳࡡࡳࡻࠥຎ")) is not None:
        return results[bstack1ll_opy_ (u"ࠥࡷࡺࡳ࡭ࡢࡴࡼࠦຏ")]
    logger.error(bstack1ll_opy_ (u"ࠦࡓࡵࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡓࡧࡶࡹࡱࡺࡳࠡࡕࡸࡱࡲࡧࡲࡺࠢࡺࡥࡸࠦࡦࡰࡷࡱࡨ࠳ࠨຐ"))
    return {}
  if not bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1111ll_opy_) or (bstack111l1lll_opy_ and bstack1ll11111l1_opy_):
    logger.warning(bstack1ll_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹࠠࡴࡷࡰࡱࡦࡸࡹ࠯ࠤຑ"))
    return {}
  try:
    logger.debug(bstack1ll_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼࠫຒ"))
    logger.debug(perform_scan(driver))
    bstack1111l11l1_opy_ = driver.execute_async_script(bstack1l11l1l1l_opy_.bstack11ll11ll1l_opy_)
    return bstack1111l11l1_opy_
  except Exception:
    logger.error(bstack1ll_opy_ (u"ࠢࡏࡱࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡺࡳ࡭ࡢࡴࡼࠤࡼࡧࡳࠡࡨࡲࡹࡳࡪ࠮ࠣຓ"))
    return {}
def bstack111ll1l1l_opy_():
  global CONFIG
  global bstack1l1111ll_opy_
  bstack1l1l11111l_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨດ"), None) and bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫຕ"), None)
  if not bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1111ll_opy_) or not bstack1l1l11111l_opy_:
        logger.warning(bstack1ll_opy_ (u"ࠥࡒࡴࡺࠠࡢࡰࠣࡅࡵࡶࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠱ࠦࡣࡢࡰࡱࡳࡹࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࠡࡴࡨࡷࡺࡲࡴࡴ࠰ࠥຖ"))
        return False
  return True
def bstack11l1l1lll_opy_(bstack11llllll_opy_):
    bstack1l1l1ll111_opy_ = bstack1l111111_opy_.current_test_uuid() if bstack1l111111_opy_.current_test_uuid() else bstack11llllll1l_opy_.current_hook_uuid()
    with ThreadPoolExecutor() as executor:
        future = executor.submit(bstack1l1lll1l11_opy_(bstack1l1l1ll111_opy_, bstack11llllll_opy_))
        try:
            return future.result(timeout=bstack1ll11l11_opy_)
        except TimeoutError:
            logger.error(bstack1ll_opy_ (u"࡙ࠦ࡯࡭ࡦࡱࡸࡸࠥࡧࡦࡵࡧࡵࠤࢀࢃࡳࠡࡹ࡫࡭ࡱ࡫ࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡕࡩࡸࡻ࡬ࡵࡵࠥທ").format(bstack1ll11l11_opy_))
        except Exception as ex:
            logger.debug(bstack1ll_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡷ࡫ࡴࡳ࡫ࡨࡺ࡮ࡴࡧࠡࡃࡳࡴࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡾࢁ࠳ࠦࡅࡳࡴࡲࡶࠥ࠳ࠠࡼࡿࠥຘ").format(bstack11llllll_opy_, str(ex)))
    return {}
@measure(event_name=EVENTS.bstack1111ll1ll_opy_, stage=STAGE.bstack1llll11lll_opy_, bstack1lll11l11_opy_=bstack1lll1lllll_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack1l1111ll_opy_
  bstack1ll11111l1_opy_ = not (bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪນ"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ບ"), None))
  bstack111l11l1l_opy_ = not (bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠨ࡫ࡶࡅࡵࡶࡁ࠲࠳ࡼࡘࡪࡹࡴࠨປ"), None) and bstack11ll11l1_opy_(
          threading.current_thread(), bstack1ll_opy_ (u"ࠩࡤࡴࡵࡇ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫຜ"), None))
  bstack111l1lll_opy_ = getattr(driver, bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪຝ"), None) != True
  if not bstack1l11llll1l_opy_.bstack1l1l1ll1_opy_(CONFIG, bstack1l1111ll_opy_) or (bstack111l1lll_opy_ and bstack1ll11111l1_opy_ and bstack111l11l1l_opy_):
    logger.warning(bstack1ll_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡺࡴࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲ࠳ࠨພ"))
    return {}
  try:
    bstack11llll1l11_opy_ = bstack1ll_opy_ (u"ࠬࡧࡰࡱࠩຟ") in CONFIG and CONFIG.get(bstack1ll_opy_ (u"࠭ࡡࡱࡲࠪຠ"), bstack1ll_opy_ (u"ࠧࠨມ"))
    session_id = getattr(driver, bstack1ll_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠬຢ"), None)
    if not session_id:
      logger.warning(bstack1ll_opy_ (u"ࠤࡑࡳࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡉࡅࠢࡩࡳࡺࡴࡤࠡࡨࡲࡶࠥࡪࡲࡪࡸࡨࡶࠧຣ"))
      return {bstack1ll_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤ຤"): bstack1ll_opy_ (u"ࠦࡓࡵࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡋࡇࠤ࡫ࡵࡵ࡯ࡦࠥລ")}
    if bstack11llll1l11_opy_:
      try:
        bstack11l1l1ll_opy_ = {
              bstack1ll_opy_ (u"ࠬࡺࡨࡋࡹࡷࡘࡴࡱࡥ࡯ࠩ຦"): os.environ.get(bstack1ll_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫວ"), os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫຨ"), bstack1ll_opy_ (u"ࠨࠩຩ"))),
              bstack1ll_opy_ (u"ࠩࡷ࡬࡙࡫ࡳࡵࡔࡸࡲ࡚ࡻࡩࡥࠩສ"): bstack1l111111_opy_.current_test_uuid() if bstack1l111111_opy_.current_test_uuid() else bstack11llllll1l_opy_.current_hook_uuid(),
              bstack1ll_opy_ (u"ࠪࡥࡺࡺࡨࡉࡧࡤࡨࡪࡸࠧຫ"): os.environ.get(bstack1ll_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩຬ")),
              bstack1ll_opy_ (u"ࠬࡹࡣࡢࡰࡗ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬອ"): str(int(datetime.datetime.now().timestamp() * 1000)),
              bstack1ll_opy_ (u"࠭ࡴࡩࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫຮ"): os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬຯ"), bstack1ll_opy_ (u"ࠨࠩະ")),
              bstack1ll_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࠩັ"): kwargs.get(bstack1ll_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࡢࡧࡴࡳ࡭ࡢࡰࡧࠫາ"), None) or bstack1ll_opy_ (u"ࠫࠬຳ")
          }
        if not hasattr(thread_local, bstack1ll_opy_ (u"ࠬࡨࡡࡴࡧࡢࡥࡵࡶ࡟ࡢ࠳࠴ࡽࡤࡹࡣࡳ࡫ࡳࡸࠬິ")):
            scripts = {bstack1ll_opy_ (u"࠭ࡳࡤࡣࡱࠫີ"): bstack1l11l1l1l_opy_.perform_scan}
            thread_local.base_app_a11y_script = scripts
        bstack1ll1l11l_opy_ = copy.deepcopy(thread_local.base_app_a11y_script)
        bstack1ll1l11l_opy_[bstack1ll_opy_ (u"ࠧࡴࡥࡤࡲࠬຶ")] = bstack1ll1l11l_opy_[bstack1ll_opy_ (u"ࠨࡵࡦࡥࡳ࠭ື")] % json.dumps(bstack11l1l1ll_opy_)
        bstack1l11l1l1l_opy_.bstack1l1111ll11_opy_(bstack1ll1l11l_opy_)
        bstack1l11l1l1l_opy_.store()
        bstack11l111l1l_opy_ = driver.execute_script(bstack1l11l1l1l_opy_.perform_scan)
      except Exception as bstack11l1lll11_opy_:
        logger.info(bstack1ll_opy_ (u"ࠤࡄࡴࡵ࡯ࡵ࡮ࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡧࡦࡴࠠࡧࡣ࡬ࡰࡪࡪ࠺ࠡࠤຸ") + str(bstack11l1lll11_opy_))
        bstack11l111l1l_opy_ = {bstack1ll_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤູ"): str(bstack11l1lll11_opy_)}
    else:
      bstack11l111l1l_opy_ = driver.execute_async_script(bstack1l11l1l1l_opy_.perform_scan, {bstack1ll_opy_ (u"ࠫࡲ࡫ࡴࡩࡱࡧ຺ࠫ"): kwargs.get(bstack1ll_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࡤࡩ࡯࡮࡯ࡤࡲࡩ࠭ົ"), None) or bstack1ll_opy_ (u"࠭ࠧຼ")})
    return bstack11l111l1l_opy_
  except Exception as err:
    logger.error(bstack1ll_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡶࡺࡴࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲ࠳ࠦࡻࡾࠤຽ").format(str(err)))
    return {}