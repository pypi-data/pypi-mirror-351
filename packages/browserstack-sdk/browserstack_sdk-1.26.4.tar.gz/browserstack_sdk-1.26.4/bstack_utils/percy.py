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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack11llll1111_opy_, bstack11ll1l1ll1_opy_
from bstack_utils.measure import measure
class bstack1l11l1llll_opy_:
  working_dir = os.getcwd()
  bstack11l1ll1ll1_opy_ = False
  config = {}
  bstack11ll1l1llll_opy_ = bstack1ll_opy_ (u"ࠬ࠭ᖊ")
  binary_path = bstack1ll_opy_ (u"࠭ࠧᖋ")
  bstack11lll1llll1_opy_ = bstack1ll_opy_ (u"ࠧࠨᖌ")
  bstack1l1ll1l1ll_opy_ = False
  bstack11ll1l1ll1l_opy_ = None
  bstack11lll1l1l11_opy_ = {}
  bstack11lll11lll1_opy_ = 300
  bstack11lll1l1l1l_opy_ = False
  logger = None
  bstack11llll1l111_opy_ = False
  bstack1l11111l1l_opy_ = False
  percy_build_id = None
  bstack11lll11llll_opy_ = bstack1ll_opy_ (u"ࠨࠩᖍ")
  bstack11ll1l1ll11_opy_ = {
    bstack1ll_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩᖎ") : 1,
    bstack1ll_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫᖏ") : 2,
    bstack1ll_opy_ (u"ࠫࡪࡪࡧࡦࠩᖐ") : 3,
    bstack1ll_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࠬᖑ") : 4
  }
  def __init__(self) -> None: pass
  def bstack11lll111l1l_opy_(self):
    bstack11lll1111ll_opy_ = bstack1ll_opy_ (u"࠭ࠧᖒ")
    bstack11lll1lll11_opy_ = sys.platform
    bstack11lll111l11_opy_ = bstack1ll_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭ᖓ")
    if re.match(bstack1ll_opy_ (u"ࠣࡦࡤࡶࡼ࡯࡮ࡽ࡯ࡤࡧࠥࡵࡳࠣᖔ"), bstack11lll1lll11_opy_) != None:
      bstack11lll1111ll_opy_ = bstack11lll1l111l_opy_ + bstack1ll_opy_ (u"ࠤ࠲ࡴࡪࡸࡣࡺ࠯ࡲࡷࡽ࠴ࡺࡪࡲࠥᖕ")
      self.bstack11lll11llll_opy_ = bstack1ll_opy_ (u"ࠪࡱࡦࡩࠧᖖ")
    elif re.match(bstack1ll_opy_ (u"ࠦࡲࡹࡷࡪࡰࡿࡱࡸࡿࡳࡽ࡯࡬ࡲ࡬ࡽࡼࡤࡻࡪࡻ࡮ࡴࡼࡣࡥࡦࡻ࡮ࡴࡼࡸ࡫ࡱࡧࡪࢂࡥ࡮ࡥࡿࡻ࡮ࡴ࠳࠳ࠤᖗ"), bstack11lll1lll11_opy_) != None:
      bstack11lll1111ll_opy_ = bstack11lll1l111l_opy_ + bstack1ll_opy_ (u"ࠧ࠵ࡰࡦࡴࡦࡽ࠲ࡽࡩ࡯࠰ࡽ࡭ࡵࠨᖘ")
      bstack11lll111l11_opy_ = bstack1ll_opy_ (u"ࠨࡰࡦࡴࡦࡽ࠳࡫ࡸࡦࠤᖙ")
      self.bstack11lll11llll_opy_ = bstack1ll_opy_ (u"ࠧࡸ࡫ࡱࠫᖚ")
    else:
      bstack11lll1111ll_opy_ = bstack11lll1l111l_opy_ + bstack1ll_opy_ (u"ࠣ࠱ࡳࡩࡷࡩࡹ࠮࡮࡬ࡲࡺࡾ࠮ࡻ࡫ࡳࠦᖛ")
      self.bstack11lll11llll_opy_ = bstack1ll_opy_ (u"ࠩ࡯࡭ࡳࡻࡸࠨᖜ")
    return bstack11lll1111ll_opy_, bstack11lll111l11_opy_
  def bstack11ll1l11lll_opy_(self):
    try:
      bstack11lll11111l_opy_ = [os.path.join(expanduser(bstack1ll_opy_ (u"ࠥࢂࠧᖝ")), bstack1ll_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᖞ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack11lll11111l_opy_:
        if(self.bstack11llll11l1l_opy_(path)):
          return path
      raise bstack1ll_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡲࡻࡳࡲ࡯ࡢࡦࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠤᖟ")
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡩ࡭ࡳࡪࠠࡢࡸࡤ࡭ࡱࡧࡢ࡭ࡧࠣࡴࡦࡺࡨࠡࡨࡲࡶࠥࡶࡥࡳࡥࡼࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࠱ࠥࢁࡽࠣᖠ").format(e))
  def bstack11llll11l1l_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack11ll1lll1l1_opy_(self, bstack11lll11ll1l_opy_):
    return os.path.join(bstack11lll11ll1l_opy_, self.bstack11ll1l1llll_opy_ + bstack1ll_opy_ (u"ࠢ࠯ࡧࡷࡥ࡬ࠨᖡ"))
  def bstack11lll1l1lll_opy_(self, bstack11lll11ll1l_opy_, bstack11lll11l1ll_opy_):
    if not bstack11lll11l1ll_opy_: return
    try:
      bstack11ll1llll1l_opy_ = self.bstack11ll1lll1l1_opy_(bstack11lll11ll1l_opy_)
      with open(bstack11ll1llll1l_opy_, bstack1ll_opy_ (u"ࠣࡹࠥᖢ")) as f:
        f.write(bstack11lll11l1ll_opy_)
        self.logger.debug(bstack1ll_opy_ (u"ࠤࡖࡥࡻ࡫ࡤࠡࡰࡨࡻࠥࡋࡔࡢࡩࠣࡪࡴࡸࠠࡱࡧࡵࡧࡾࠨᖣ"))
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡢࡸࡨࠤࡹ࡮ࡥࠡࡧࡷࡥ࡬࠲ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥᖤ").format(e))
  def bstack11llll1111l_opy_(self, bstack11lll11ll1l_opy_):
    try:
      bstack11ll1llll1l_opy_ = self.bstack11ll1lll1l1_opy_(bstack11lll11ll1l_opy_)
      if os.path.exists(bstack11ll1llll1l_opy_):
        with open(bstack11ll1llll1l_opy_, bstack1ll_opy_ (u"ࠦࡷࠨᖥ")) as f:
          bstack11lll11l1ll_opy_ = f.read().strip()
          return bstack11lll11l1ll_opy_ if bstack11lll11l1ll_opy_ else None
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡅࡕࡣࡪ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣᖦ").format(e))
  def bstack11llll11lll_opy_(self, bstack11lll11ll1l_opy_, bstack11lll1111ll_opy_):
    bstack11lll1ll111_opy_ = self.bstack11llll1111l_opy_(bstack11lll11ll1l_opy_)
    if bstack11lll1ll111_opy_:
      try:
        bstack11ll1l1lll1_opy_ = self.bstack11ll1ll111l_opy_(bstack11lll1ll111_opy_, bstack11lll1111ll_opy_)
        if not bstack11ll1l1lll1_opy_:
          self.logger.debug(bstack1ll_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࡨࡩ࡯ࡣࡵࡽࠥ࡯ࡳࠡࡷࡳࠤࡹࡵࠠࡥࡣࡷࡩࠥ࠮ࡅࡕࡣࡪࠤࡺࡴࡣࡩࡣࡱ࡫ࡪࡪࠩࠣᖧ"))
          return True
        self.logger.debug(bstack1ll_opy_ (u"ࠢࡏࡧࡺࠤࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡺࡪࡸࡳࡪࡱࡱࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠬࠡࡦࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡵࡱࡦࡤࡸࡪࠨᖨ"))
        return False
      except Exception as e:
        self.logger.warn(bstack1ll_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡨ࡮ࡥࡤ࡭ࠣࡪࡴࡸࠠࡣ࡫ࡱࡥࡷࡿࠠࡶࡲࡧࡥࡹ࡫ࡳ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡦ࡮ࡴࡡࡳࡻ࠽ࠤࢀࢃࠢᖩ").format(e))
    return False
  def bstack11ll1ll111l_opy_(self, bstack11lll1ll111_opy_, bstack11lll1111ll_opy_):
    try:
      headers = {
        bstack1ll_opy_ (u"ࠤࡌࡪ࠲ࡔ࡯࡯ࡧ࠰ࡑࡦࡺࡣࡩࠤᖪ"): bstack11lll1ll111_opy_
      }
      response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠪࡋࡊ࡚ࠧᖫ"), bstack11lll1111ll_opy_, {}, {bstack1ll_opy_ (u"ࠦ࡭࡫ࡡࡥࡧࡵࡷࠧᖬ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack1ll_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡨ࡮ࡥࡤ࡭࡬ࡲ࡬ࠦࡦࡰࡴࠣࡔࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡸࡴࡩࡧࡴࡦࡵ࠽ࠤࢀࢃࠢᖭ").format(e))
  @measure(event_name=EVENTS.bstack11llll1l1l1_opy_, stage=STAGE.bstack1llll11lll_opy_)
  def bstack11llll111l1_opy_(self, bstack11lll1111ll_opy_, bstack11lll111l11_opy_):
    try:
      bstack11lll111ll1_opy_ = self.bstack11ll1l11lll_opy_()
      bstack11ll1l1l1l1_opy_ = os.path.join(bstack11lll111ll1_opy_, bstack1ll_opy_ (u"࠭ࡰࡦࡴࡦࡽ࠳ࢀࡩࡱࠩᖮ"))
      bstack11ll1ll11ll_opy_ = os.path.join(bstack11lll111ll1_opy_, bstack11lll111l11_opy_)
      if self.bstack11llll11lll_opy_(bstack11lll111ll1_opy_, bstack11lll1111ll_opy_): # if bstack11ll1lll111_opy_, bstack1l1ll11111l_opy_ bstack11lll11l1ll_opy_ is bstack11lll1lllll_opy_ to bstack11lll1l11ll_opy_ version available (response 304)
        if os.path.exists(bstack11ll1ll11ll_opy_):
          self.logger.info(bstack1ll_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡦࡰࡷࡱࡨࠥ࡯࡮ࠡࡽࢀ࠰ࠥࡹ࡫ࡪࡲࡳ࡭ࡳ࡭ࠠࡥࡱࡺࡲࡱࡵࡡࡥࠤᖯ").format(bstack11ll1ll11ll_opy_))
          return bstack11ll1ll11ll_opy_
        if os.path.exists(bstack11ll1l1l1l1_opy_):
          self.logger.info(bstack1ll_opy_ (u"ࠣࡒࡨࡶࡨࡿࠠࡻ࡫ࡳࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡻࡾ࠮ࠣࡹࡳࢀࡩࡱࡲ࡬ࡲ࡬ࠨᖰ").format(bstack11ll1l1l1l1_opy_))
          return self.bstack11lll111lll_opy_(bstack11ll1l1l1l1_opy_, bstack11lll111l11_opy_)
      self.logger.info(bstack1ll_opy_ (u"ࠤࡇࡳࡼࡴ࡬ࡰࡣࡧ࡭ࡳ࡭ࠠࡱࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࠦࡦࡳࡱࡰࠤࢀࢃࠢᖱ").format(bstack11lll1111ll_opy_))
      response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠪࡋࡊ࡚ࠧᖲ"), bstack11lll1111ll_opy_, {}, {})
      if response.status_code == 200:
        bstack11ll1lll11l_opy_ = response.headers.get(bstack1ll_opy_ (u"ࠦࡊ࡚ࡡࡨࠤᖳ"), bstack1ll_opy_ (u"ࠧࠨᖴ"))
        if bstack11ll1lll11l_opy_:
          self.bstack11lll1l1lll_opy_(bstack11lll111ll1_opy_, bstack11ll1lll11l_opy_)
        with open(bstack11ll1l1l1l1_opy_, bstack1ll_opy_ (u"࠭ࡷࡣࠩᖵ")) as file:
          file.write(response.content)
        self.logger.info(bstack1ll_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥࡧࡧࠤࡵ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣࡥࡳࡪࠠࡴࡣࡹࡩࡩࠦࡡࡵࠢࡾࢁࠧᖶ").format(bstack11ll1l1l1l1_opy_))
        return self.bstack11lll111lll_opy_(bstack11ll1l1l1l1_opy_, bstack11lll111l11_opy_)
      else:
        raise(bstack1ll_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡴࡩࡧࠣࡪ࡮ࡲࡥ࠯ࠢࡖࡸࡦࡺࡵࡴࠢࡦࡳࡩ࡫࠺ࠡࡽࢀࠦᖷ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠠࡱࡧࡵࡧࡾࠦࡢࡪࡰࡤࡶࡾࡀࠠࡼࡿࠥᖸ").format(e))
  def bstack11ll1l11ll1_opy_(self, bstack11lll1111ll_opy_, bstack11lll111l11_opy_):
    try:
      retry = 2
      bstack11ll1ll11ll_opy_ = None
      bstack11lll1ll1ll_opy_ = False
      while retry > 0:
        bstack11ll1ll11ll_opy_ = self.bstack11llll111l1_opy_(bstack11lll1111ll_opy_, bstack11lll111l11_opy_)
        bstack11lll1ll1ll_opy_ = self.bstack11ll1l1l11l_opy_(bstack11lll1111ll_opy_, bstack11lll111l11_opy_, bstack11ll1ll11ll_opy_)
        if bstack11lll1ll1ll_opy_:
          break
        retry -= 1
      return bstack11ll1ll11ll_opy_, bstack11lll1ll1ll_opy_
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡧࡦࡶࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠢࡳࡥࡹ࡮ࠢᖹ").format(e))
    return bstack11ll1ll11ll_opy_, False
  def bstack11ll1l1l11l_opy_(self, bstack11lll1111ll_opy_, bstack11lll111l11_opy_, bstack11ll1ll11ll_opy_, bstack11lll1l1ll1_opy_ = 0):
    if bstack11lll1l1ll1_opy_ > 1:
      return False
    if bstack11ll1ll11ll_opy_ == None or os.path.exists(bstack11ll1ll11ll_opy_) == False:
      self.logger.warn(bstack1ll_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡴࡦࡺࡨࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧ࠰ࠥࡸࡥࡵࡴࡼ࡭ࡳ࡭ࠠࡥࡱࡺࡲࡱࡵࡡࡥࠤᖺ"))
      return False
    bstack11ll1ll11l1_opy_ = bstack1ll_opy_ (u"ࡷࠨ࡞࠯ࠬࡃࡴࡪࡸࡣࡺ࠱ࡦࡰ࡮ࠦ࡜ࡥ࠭࡟࠲ࡡࡪࠫ࡝࠰࡟ࡨ࠰ࠨᖻ")
    command = bstack1ll_opy_ (u"࠭ࡻࡾࠢ࠰࠱ࡻ࡫ࡲࡴ࡫ࡲࡲࠬᖼ").format(bstack11ll1ll11ll_opy_)
    bstack11lll1111l1_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack11ll1ll11l1_opy_, bstack11lll1111l1_opy_) != None:
      return True
    else:
      self.logger.error(bstack1ll_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡤࡪࡨࡧࡰࠦࡦࡢ࡫࡯ࡩࡩࠨᖽ"))
      return False
  def bstack11lll111lll_opy_(self, bstack11ll1l1l1l1_opy_, bstack11lll111l11_opy_):
    try:
      working_dir = os.path.dirname(bstack11ll1l1l1l1_opy_)
      shutil.unpack_archive(bstack11ll1l1l1l1_opy_, working_dir)
      bstack11ll1ll11ll_opy_ = os.path.join(working_dir, bstack11lll111l11_opy_)
      os.chmod(bstack11ll1ll11ll_opy_, 0o755)
      return bstack11ll1ll11ll_opy_
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡺࡴࡺࡪࡲࠣࡴࡪࡸࡣࡺࠢࡥ࡭ࡳࡧࡲࡺࠤᖾ"))
  def bstack11llll11l11_opy_(self):
    try:
      bstack11lll11l11l_opy_ = self.config.get(bstack1ll_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨᖿ"))
      bstack11llll11l11_opy_ = bstack11lll11l11l_opy_ or (bstack11lll11l11l_opy_ is None and self.bstack11l1ll1ll1_opy_)
      if not bstack11llll11l11_opy_ or self.config.get(bstack1ll_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ᗀ"), None) not in bstack11llll1l11l_opy_:
        return False
      self.bstack1l1ll1l1ll_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡥࡧࡷࡩࡨࡺࠠࡱࡧࡵࡧࡾ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨᗁ").format(e))
  def bstack11lll11ll11_opy_(self):
    try:
      bstack11lll11ll11_opy_ = self.percy_capture_mode
      return bstack11lll11ll11_opy_
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡩࡴࠡࡲࡨࡶࡨࡿࠠࡤࡣࡳࡸࡺࡸࡥࠡ࡯ࡲࡨࡪ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨᗂ").format(e))
  def init(self, bstack11l1ll1ll1_opy_, config, logger):
    self.bstack11l1ll1ll1_opy_ = bstack11l1ll1ll1_opy_
    self.config = config
    self.logger = logger
    if not self.bstack11llll11l11_opy_():
      return
    self.bstack11lll1l1l11_opy_ = config.get(bstack1ll_opy_ (u"࠭ࡰࡦࡴࡦࡽࡔࡶࡴࡪࡱࡱࡷࠬᗃ"), {})
    self.percy_capture_mode = config.get(bstack1ll_opy_ (u"ࠧࡱࡧࡵࡧࡾࡉࡡࡱࡶࡸࡶࡪࡓ࡯ࡥࡧࠪᗄ"))
    try:
      bstack11lll1111ll_opy_, bstack11lll111l11_opy_ = self.bstack11lll111l1l_opy_()
      self.bstack11ll1l1llll_opy_ = bstack11lll111l11_opy_
      bstack11ll1ll11ll_opy_, bstack11lll1ll1ll_opy_ = self.bstack11ll1l11ll1_opy_(bstack11lll1111ll_opy_, bstack11lll111l11_opy_)
      if bstack11lll1ll1ll_opy_:
        self.binary_path = bstack11ll1ll11ll_opy_
        thread = Thread(target=self.bstack11ll1llllll_opy_)
        thread.start()
      else:
        self.bstack11llll1l111_opy_ = True
        self.logger.error(bstack1ll_opy_ (u"ࠣࡋࡱࡺࡦࡲࡩࡥࠢࡳࡩࡷࡩࡹࠡࡲࡤࡸ࡭ࠦࡦࡰࡷࡱࡨࠥ࠳ࠠࡼࡿ࠯ࠤ࡚ࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡐࡦࡴࡦࡽࠧᗅ").format(bstack11ll1ll11ll_opy_))
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡼࡿࠥᗆ").format(e))
  def bstack11lll11l111_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack1ll_opy_ (u"ࠪࡰࡴ࡭ࠧᗇ"), bstack1ll_opy_ (u"ࠫࡵ࡫ࡲࡤࡻ࠱ࡰࡴ࡭ࠧᗈ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack1ll_opy_ (u"ࠧࡖࡵࡴࡪ࡬ࡲ࡬ࠦࡰࡦࡴࡦࡽࠥࡲ࡯ࡨࡵࠣࡥࡹࠦࡻࡾࠤᗉ").format(logfile))
      self.bstack11lll1llll1_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡩࡹࠦࡰࡦࡴࡦࡽࠥࡲ࡯ࡨࠢࡳࡥࡹ࡮ࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢᗊ").format(e))
  @measure(event_name=EVENTS.bstack11ll1l1l1ll_opy_, stage=STAGE.bstack1llll11lll_opy_)
  def bstack11ll1llllll_opy_(self):
    bstack11lll1ll1l1_opy_ = self.bstack11ll1lll1ll_opy_()
    if bstack11lll1ll1l1_opy_ == None:
      self.bstack11llll1l111_opy_ = True
      self.logger.error(bstack1ll_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡴࡰ࡭ࡨࡲࠥࡴ࡯ࡵࠢࡩࡳࡺࡴࡤ࠭ࠢࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻࠥᗋ"))
      return False
    command_args = [bstack1ll_opy_ (u"ࠣࡣࡳࡴ࠿࡫ࡸࡦࡥ࠽ࡷࡹࡧࡲࡵࠤᗌ") if self.bstack11l1ll1ll1_opy_ else bstack1ll_opy_ (u"ࠩࡨࡼࡪࡩ࠺ࡴࡶࡤࡶࡹ࠭ᗍ")]
    bstack11llll11ll1_opy_ = self.bstack11ll1ll1lll_opy_()
    if bstack11llll11ll1_opy_ != None:
      command_args.append(bstack1ll_opy_ (u"ࠥ࠱ࡨࠦࡻࡾࠤᗎ").format(bstack11llll11ll1_opy_))
    env = os.environ.copy()
    env[bstack1ll_opy_ (u"ࠦࡕࡋࡒࡄ࡛ࡢࡘࡔࡑࡅࡏࠤᗏ")] = bstack11lll1ll1l1_opy_
    env[bstack1ll_opy_ (u"࡚ࠧࡈࡠࡄࡘࡍࡑࡊ࡟ࡖࡗࡌࡈࠧᗐ")] = os.environ.get(bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᗑ"), bstack1ll_opy_ (u"ࠧࠨᗒ"))
    bstack11lll111111_opy_ = [self.binary_path]
    self.bstack11lll11l111_opy_()
    self.bstack11ll1l1ll1l_opy_ = self.bstack11lll1ll11l_opy_(bstack11lll111111_opy_ + command_args, env)
    self.logger.debug(bstack1ll_opy_ (u"ࠣࡕࡷࡥࡷࡺࡩ࡯ࡩࠣࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠤᗓ"))
    bstack11lll1l1ll1_opy_ = 0
    while self.bstack11ll1l1ll1l_opy_.poll() == None:
      bstack11ll1ll1l1l_opy_ = self.bstack11llll11111_opy_()
      if bstack11ll1ll1l1l_opy_:
        self.logger.debug(bstack1ll_opy_ (u"ࠤࡋࡩࡦࡲࡴࡩࠢࡆ࡬ࡪࡩ࡫ࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࠧᗔ"))
        self.bstack11lll1l1l1l_opy_ = True
        return True
      bstack11lll1l1ll1_opy_ += 1
      self.logger.debug(bstack1ll_opy_ (u"ࠥࡌࡪࡧ࡬ࡵࡪࠣࡇ࡭࡫ࡣ࡬ࠢࡕࡩࡹࡸࡹࠡ࠯ࠣࡿࢂࠨᗕ").format(bstack11lll1l1ll1_opy_))
      time.sleep(2)
    self.logger.error(bstack1ll_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡤࡶࡹࠦࡰࡦࡴࡦࡽ࠱ࠦࡈࡦࡣ࡯ࡸ࡭ࠦࡃࡩࡧࡦ࡯ࠥࡌࡡࡪ࡮ࡨࡨࠥࡧࡦࡵࡧࡵࠤࢀࢃࠠࡢࡶࡷࡩࡲࡶࡴࡴࠤᗖ").format(bstack11lll1l1ll1_opy_))
    self.bstack11llll1l111_opy_ = True
    return False
  def bstack11llll11111_opy_(self, bstack11lll1l1ll1_opy_ = 0):
    if bstack11lll1l1ll1_opy_ > 10:
      return False
    try:
      bstack11ll1l11l1l_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠬࡖࡅࡓࡅ࡜ࡣࡘࡋࡒࡗࡇࡕࡣࡆࡊࡄࡓࡇࡖࡗࠬᗗ"), bstack1ll_opy_ (u"࠭ࡨࡵࡶࡳ࠾࠴࠵࡬ࡰࡥࡤࡰ࡭ࡵࡳࡵ࠼࠸࠷࠸࠾ࠧᗘ"))
      bstack11ll1l1111l_opy_ = bstack11ll1l11l1l_opy_ + bstack11lll1l11l1_opy_
      response = requests.get(bstack11ll1l1111l_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࠭ᗙ"), {}).get(bstack1ll_opy_ (u"ࠨ࡫ࡧࠫᗚ"), None)
      return True
    except:
      self.logger.debug(bstack1ll_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡱࡦࡧࡺࡸࡲࡦࡦࠣࡻ࡭࡯࡬ࡦࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡨࡦࡣ࡯ࡸ࡭ࠦࡣࡩࡧࡦ࡯ࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠢᗛ"))
      return False
  def bstack11ll1lll1ll_opy_(self):
    bstack11ll1ll1111_opy_ = bstack1ll_opy_ (u"ࠪࡥࡵࡶࠧᗜ") if self.bstack11l1ll1ll1_opy_ else bstack1ll_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ᗝ")
    bstack11ll1lllll1_opy_ = bstack1ll_opy_ (u"ࠧࡻ࡮ࡥࡧࡩ࡭ࡳ࡫ࡤࠣᗞ") if self.config.get(bstack1ll_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬᗟ")) is None else True
    bstack11lll1lll1l_opy_ = bstack1ll_opy_ (u"ࠢࡢࡲ࡬࠳ࡦࡶࡰࡠࡲࡨࡶࡨࡿ࠯ࡨࡧࡷࡣࡵࡸ࡯࡫ࡧࡦࡸࡤࡺ࡯࡬ࡧࡱࡃࡳࡧ࡭ࡦ࠿ࡾࢁࠫࡺࡹࡱࡧࡀࡿࢂࠬࡰࡦࡴࡦࡽࡂࢁࡽࠣᗠ").format(self.config[bstack1ll_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᗡ")], bstack11ll1ll1111_opy_, bstack11ll1lllll1_opy_)
    if self.percy_capture_mode:
      bstack11lll1lll1l_opy_ += bstack1ll_opy_ (u"ࠤࠩࡴࡪࡸࡣࡺࡡࡦࡥࡵࡺࡵࡳࡧࡢࡱࡴࡪࡥ࠾ࡽࢀࠦᗢ").format(self.percy_capture_mode)
    uri = bstack11llll1111_opy_(bstack11lll1lll1l_opy_)
    try:
      response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠪࡋࡊ࡚ࠧᗣ"), uri, {}, {bstack1ll_opy_ (u"ࠫࡦࡻࡴࡩࠩᗤ"): (self.config[bstack1ll_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᗥ")], self.config[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᗦ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack1l1ll1l1ll_opy_ = data.get(bstack1ll_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨᗧ"))
        self.percy_capture_mode = data.get(bstack1ll_opy_ (u"ࠨࡲࡨࡶࡨࡿ࡟ࡤࡣࡳࡸࡺࡸࡥࡠ࡯ࡲࡨࡪ࠭ᗨ"))
        os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡈࡖࡈ࡟ࠧᗩ")] = str(self.bstack1l1ll1l1ll_opy_)
        os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࡠࡅࡄࡔ࡙࡛ࡒࡆࡡࡐࡓࡉࡋࠧᗪ")] = str(self.percy_capture_mode)
        if bstack11ll1lllll1_opy_ == bstack1ll_opy_ (u"ࠦࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠢᗫ") and str(self.bstack1l1ll1l1ll_opy_).lower() == bstack1ll_opy_ (u"ࠧࡺࡲࡶࡧࠥᗬ"):
          self.bstack1l11111l1l_opy_ = True
        if bstack1ll_opy_ (u"ࠨࡴࡰ࡭ࡨࡲࠧᗭ") in data:
          return data[bstack1ll_opy_ (u"ࠢࡵࡱ࡮ࡩࡳࠨᗮ")]
        else:
          raise bstack1ll_opy_ (u"ࠨࡖࡲ࡯ࡪࡴࠠࡏࡱࡷࠤࡋࡵࡵ࡯ࡦࠣ࠱ࠥࢁࡽࠨᗯ").format(data)
      else:
        raise bstack1ll_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡵ࡫ࡲࡤࡻࠣࡸࡴࡱࡥ࡯࠮ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥࡹࡴࡢࡶࡸࡷࠥ࠳ࠠࡼࡿ࠯ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡂࡰࡦࡼࠤ࠲ࠦࡻࡾࠤᗰ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡴࡷࡵࡪࡦࡥࡷࠦᗱ").format(e))
  def bstack11ll1ll1lll_opy_(self):
    bstack11lll11l1l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠦࡵ࡫ࡲࡤࡻࡆࡳࡳ࡬ࡩࡨ࠰࡭ࡷࡴࡴࠢᗲ"))
    try:
      if bstack1ll_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳ࠭ᗳ") not in self.bstack11lll1l1l11_opy_:
        self.bstack11lll1l1l11_opy_[bstack1ll_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧᗴ")] = 2
      with open(bstack11lll11l1l1_opy_, bstack1ll_opy_ (u"ࠧࡸࠩᗵ")) as fp:
        json.dump(self.bstack11lll1l1l11_opy_, fp)
      return bstack11lll11l1l1_opy_
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡨࡸࡥࡢࡶࡨࠤࡵ࡫ࡲࡤࡻࠣࡧࡴࡴࡦ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣᗶ").format(e))
  def bstack11lll1ll11l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack11lll11llll_opy_ == bstack1ll_opy_ (u"ࠩࡺ࡭ࡳ࠭ᗷ"):
        bstack11ll1l111ll_opy_ = [bstack1ll_opy_ (u"ࠪࡧࡲࡪ࠮ࡦࡺࡨࠫᗸ"), bstack1ll_opy_ (u"ࠫ࠴ࡩࠧᗹ")]
        cmd = bstack11ll1l111ll_opy_ + cmd
      cmd = bstack1ll_opy_ (u"ࠬࠦࠧᗺ").join(cmd)
      self.logger.debug(bstack1ll_opy_ (u"ࠨࡒࡶࡰࡱ࡭ࡳ࡭ࠠࡼࡿࠥᗻ").format(cmd))
      with open(self.bstack11lll1llll1_opy_, bstack1ll_opy_ (u"ࠢࡢࠤᗼ")) as bstack11ll1l1l111_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack11ll1l1l111_opy_, text=True, stderr=bstack11ll1l1l111_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack11llll1l111_opy_ = True
      self.logger.error(bstack1ll_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸࡺࡡࡳࡶࠣࡴࡪࡸࡣࡺࠢࡺ࡭ࡹ࡮ࠠࡤ࡯ࡧࠤ࠲ࠦࡻࡾ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠥᗽ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack11lll1l1l1l_opy_:
        self.logger.info(bstack1ll_opy_ (u"ࠤࡖࡸࡴࡶࡰࡪࡰࡪࠤࡕ࡫ࡲࡤࡻࠥᗾ"))
        cmd = [self.binary_path, bstack1ll_opy_ (u"ࠥࡩࡽ࡫ࡣ࠻ࡵࡷࡳࡵࠨᗿ")]
        self.bstack11lll1ll11l_opy_(cmd)
        self.bstack11lll1l1l1l_opy_ = False
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡶࡲࡴࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡨࡵ࡭࡮ࡣࡱࡨࠥ࠳ࠠࡼࡿ࠯ࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴ࠺ࠡࡽࢀࠦᘀ").format(cmd, e))
  def bstack11l1ll11l1_opy_(self):
    if not self.bstack1l1ll1l1ll_opy_:
      return
    try:
      bstack11llll111ll_opy_ = 0
      while not self.bstack11lll1l1l1l_opy_ and bstack11llll111ll_opy_ < self.bstack11lll11lll1_opy_:
        if self.bstack11llll1l111_opy_:
          self.logger.info(bstack1ll_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡸ࡫ࡴࡶࡲࠣࡪࡦ࡯࡬ࡦࡦࠥᘁ"))
          return
        time.sleep(1)
        bstack11llll111ll_opy_ += 1
      os.environ[bstack1ll_opy_ (u"࠭ࡐࡆࡔࡆ࡝ࡤࡈࡅࡔࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࠬᘂ")] = str(self.bstack11ll1ll1l11_opy_())
      self.logger.info(bstack1ll_opy_ (u"ࠢࡑࡧࡵࡧࡾࠦࡳࡦࡶࡸࡴࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤࠣᘃ"))
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡪࡸࡣࡺ࠮ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡻࡾࠤᘄ").format(e))
  def bstack11ll1ll1l11_opy_(self):
    if self.bstack11l1ll1ll1_opy_:
      return
    try:
      bstack11ll1l111l1_opy_ = [platform[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᘅ")].lower() for platform in self.config.get(bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᘆ"), [])]
      bstack11ll1llll11_opy_ = sys.maxsize
      bstack11ll1l11l11_opy_ = bstack1ll_opy_ (u"ࠫࠬᘇ")
      for browser in bstack11ll1l111l1_opy_:
        if browser in self.bstack11ll1l1ll11_opy_:
          bstack11ll1ll1ll1_opy_ = self.bstack11ll1l1ll11_opy_[browser]
        if bstack11ll1ll1ll1_opy_ < bstack11ll1llll11_opy_:
          bstack11ll1llll11_opy_ = bstack11ll1ll1ll1_opy_
          bstack11ll1l11l11_opy_ = browser
      return bstack11ll1l11l11_opy_
    except Exception as e:
      self.logger.error(bstack1ll_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡢࡦࡵࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲ࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨᘈ").format(e))
  @classmethod
  def bstack1ll1ll11l1_opy_(self):
    return os.getenv(bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡅࡓࡅ࡜ࠫᘉ"), bstack1ll_opy_ (u"ࠧࡇࡣ࡯ࡷࡪ࠭ᘊ")).lower()
  @classmethod
  def bstack1l1l1111_opy_(self):
    return os.getenv(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞ࡥࡃࡂࡒࡗ࡙ࡗࡋ࡟ࡎࡑࡇࡉࠬᘋ"), bstack1ll_opy_ (u"ࠩࠪᘌ"))
  @classmethod
  def bstack1l1ll11ll11_opy_(cls, value):
    cls.bstack1l11111l1l_opy_ = value
  @classmethod
  def bstack11ll1l11111_opy_(cls):
    return cls.bstack1l11111l1l_opy_
  @classmethod
  def bstack1l1ll111lll_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11lll1l1111_opy_(cls):
    return cls.percy_build_id