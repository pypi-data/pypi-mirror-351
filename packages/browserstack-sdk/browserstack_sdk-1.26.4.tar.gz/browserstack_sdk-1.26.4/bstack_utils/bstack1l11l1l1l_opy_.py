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
import json
from bstack_utils.bstack111ll11ll_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1ll11l11_opy_(object):
  bstack1llll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"࠭ࡾࠨᝄ")), bstack1ll_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᝅ"))
  bstack11l1ll111ll_opy_ = os.path.join(bstack1llll1ll1_opy_, bstack1ll_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵ࠱࡮ࡸࡵ࡮ࠨᝆ"))
  commands_to_wrap = None
  perform_scan = None
  bstack11l111l1_opy_ = None
  bstack11ll11ll1l_opy_ = None
  bstack11l1lll11ll_opy_ = None
  bstack11l1lllllll_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1ll_opy_ (u"ࠩ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠫᝇ")):
      cls.instance = super(bstack11l1ll11l11_opy_, cls).__new__(cls)
      cls.instance.bstack11l1ll111l1_opy_()
    return cls.instance
  def bstack11l1ll111l1_opy_(self):
    try:
      with open(self.bstack11l1ll111ll_opy_, bstack1ll_opy_ (u"ࠪࡶࠬᝈ")) as bstack11l11l1111_opy_:
        bstack11l1ll11111_opy_ = bstack11l11l1111_opy_.read()
        data = json.loads(bstack11l1ll11111_opy_)
        if bstack1ll_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭ᝉ") in data:
          self.bstack11l1ll11ll1_opy_(data[bstack1ll_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧᝊ")])
        if bstack1ll_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧᝋ") in data:
          self.bstack1l1111ll11_opy_(data[bstack1ll_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨᝌ")])
        if bstack1ll_opy_ (u"ࠨࡰࡲࡲࡇ࡙ࡴࡢࡥ࡮ࡍࡳ࡬ࡲࡢࡃ࠴࠵ࡾࡉࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᝍ") in data:
          self.bstack11l1ll1111l_opy_(data[bstack1ll_opy_ (u"ࠩࡱࡳࡳࡈࡓࡵࡣࡦ࡯ࡎࡴࡦࡳࡣࡄ࠵࠶ࡿࡃࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝎ")])
    except:
      pass
  def bstack11l1ll1111l_opy_(self, bstack11l1lllllll_opy_):
    if bstack11l1lllllll_opy_ != None:
      self.bstack11l1lllllll_opy_ = bstack11l1lllllll_opy_
  def bstack1l1111ll11_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack1ll_opy_ (u"ࠪࡷࡨࡧ࡮ࠨᝏ"),bstack1ll_opy_ (u"ࠫࠬᝐ"))
      self.bstack11l111l1_opy_ = scripts.get(bstack1ll_opy_ (u"ࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠩᝑ"),bstack1ll_opy_ (u"࠭ࠧᝒ"))
      self.bstack11ll11ll1l_opy_ = scripts.get(bstack1ll_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠫᝓ"),bstack1ll_opy_ (u"ࠨࠩ᝔"))
      self.bstack11l1lll11ll_opy_ = scripts.get(bstack1ll_opy_ (u"ࠩࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠧ᝕"),bstack1ll_opy_ (u"ࠪࠫ᝖"))
  def bstack11l1ll11ll1_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1ll111ll_opy_, bstack1ll_opy_ (u"ࠫࡼ࠭᝗")) as file:
        json.dump({
          bstack1ll_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࠢ᝘"): self.commands_to_wrap,
          bstack1ll_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࡹࠢ᝙"): {
            bstack1ll_opy_ (u"ࠢࡴࡥࡤࡲࠧ᝚"): self.perform_scan,
            bstack1ll_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧ᝛"): self.bstack11l111l1_opy_,
            bstack1ll_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾࠨ᝜"): self.bstack11ll11ll1l_opy_,
            bstack1ll_opy_ (u"ࠥࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠣ᝝"): self.bstack11l1lll11ll_opy_
          },
          bstack1ll_opy_ (u"ࠦࡳࡵ࡮ࡃࡕࡷࡥࡨࡱࡉ࡯ࡨࡵࡥࡆ࠷࠱ࡺࡅ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠣ᝞"): self.bstack11l1lllllll_opy_
        }, file)
    except Exception as e:
      logger.error(bstack1ll_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡹࡵࡲࡪࡰࡪࠤࡨࡵ࡭࡮ࡣࡱࡨࡸࡀࠠࡼࡿࠥ᝟").format(e))
      pass
  def bstack11l1111l_opy_(self, bstack1ll1l11ll1l_opy_):
    try:
      return any(command.get(bstack1ll_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᝠ")) == bstack1ll1l11ll1l_opy_ for command in self.commands_to_wrap)
    except:
      return False
bstack1l11l1l1l_opy_ = bstack11l1ll11l11_opy_()