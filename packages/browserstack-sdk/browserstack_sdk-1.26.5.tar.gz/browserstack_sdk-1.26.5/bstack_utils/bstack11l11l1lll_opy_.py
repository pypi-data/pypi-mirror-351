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
from bstack_utils.bstack1l11lllll_opy_ import get_logger
logger = get_logger(__name__)
class bstack11l1l11ll1l_opy_(object):
  bstack1l1l1l11_opy_ = os.path.join(os.path.expanduser(bstack1l1_opy_ (u"࠭ࡾࠨ᣶")), bstack1l1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ᣷"))
  bstack11l1l11ll11_opy_ = os.path.join(bstack1l1l1l11_opy_, bstack1l1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵ࠱࡮ࡸࡵ࡮ࠨ᣸"))
  commands_to_wrap = None
  perform_scan = None
  bstack1l1l111l_opy_ = None
  bstack11l111ll11_opy_ = None
  bstack11l1l1llll1_opy_ = None
  bstack11l1ll1l11l_opy_ = None
  def __new__(cls):
    if not hasattr(cls, bstack1l1_opy_ (u"ࠩ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠫ᣹")):
      cls.instance = super(bstack11l1l11ll1l_opy_, cls).__new__(cls)
      cls.instance.bstack11l1l11lll1_opy_()
    return cls.instance
  def bstack11l1l11lll1_opy_(self):
    try:
      with open(self.bstack11l1l11ll11_opy_, bstack1l1_opy_ (u"ࠪࡶࠬ᣺")) as bstack11l1l1l1l_opy_:
        bstack11l1l11l1ll_opy_ = bstack11l1l1l1l_opy_.read()
        data = json.loads(bstack11l1l11l1ll_opy_)
        if bstack1l1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭᣻") in data:
          self.bstack11l1lll1l11_opy_(data[bstack1l1_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧ᣼")])
        if bstack1l1_opy_ (u"࠭ࡳࡤࡴ࡬ࡴࡹࡹࠧ᣽") in data:
          self.bstack111111ll1_opy_(data[bstack1l1_opy_ (u"ࠧࡴࡥࡵ࡭ࡵࡺࡳࠨ᣾")])
        if bstack1l1_opy_ (u"ࠨࡰࡲࡲࡇ࡙ࡴࡢࡥ࡮ࡍࡳ࡬ࡲࡢࡃ࠴࠵ࡾࡉࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ᣿") in data:
          self.bstack11l1l11llll_opy_(data[bstack1l1_opy_ (u"ࠩࡱࡳࡳࡈࡓࡵࡣࡦ࡯ࡎࡴࡦࡳࡣࡄ࠵࠶ࡿࡃࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᤀ")])
    except:
      pass
  def bstack11l1l11llll_opy_(self, bstack11l1ll1l11l_opy_):
    if bstack11l1ll1l11l_opy_ != None:
      self.bstack11l1ll1l11l_opy_ = bstack11l1ll1l11l_opy_
  def bstack111111ll1_opy_(self, scripts):
    if scripts != None:
      self.perform_scan = scripts.get(bstack1l1_opy_ (u"ࠪࡷࡨࡧ࡮ࠨᤁ"),bstack1l1_opy_ (u"ࠫࠬᤂ"))
      self.bstack1l1l111l_opy_ = scripts.get(bstack1l1_opy_ (u"ࠬ࡭ࡥࡵࡔࡨࡷࡺࡲࡴࡴࠩᤃ"),bstack1l1_opy_ (u"࠭ࠧᤄ"))
      self.bstack11l111ll11_opy_ = scripts.get(bstack1l1_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠫᤅ"),bstack1l1_opy_ (u"ࠨࠩᤆ"))
      self.bstack11l1l1llll1_opy_ = scripts.get(bstack1l1_opy_ (u"ࠩࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠧᤇ"),bstack1l1_opy_ (u"ࠪࠫᤈ"))
  def bstack11l1lll1l11_opy_(self, commands_to_wrap):
    if commands_to_wrap != None and len(commands_to_wrap) != 0:
      self.commands_to_wrap = commands_to_wrap
  def store(self):
    try:
      with open(self.bstack11l1l11ll11_opy_, bstack1l1_opy_ (u"ࠫࡼ࠭ᤉ")) as file:
        json.dump({
          bstack1l1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡹࠢᤊ"): self.commands_to_wrap,
          bstack1l1_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࡹࠢᤋ"): {
            bstack1l1_opy_ (u"ࠢࡴࡥࡤࡲࠧᤌ"): self.perform_scan,
            bstack1l1_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧᤍ"): self.bstack1l1l111l_opy_,
            bstack1l1_opy_ (u"ࠤࡪࡩࡹࡘࡥࡴࡷ࡯ࡸࡸ࡙ࡵ࡮࡯ࡤࡶࡾࠨᤎ"): self.bstack11l111ll11_opy_,
            bstack1l1_opy_ (u"ࠥࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠣᤏ"): self.bstack11l1l1llll1_opy_
          },
          bstack1l1_opy_ (u"ࠦࡳࡵ࡮ࡃࡕࡷࡥࡨࡱࡉ࡯ࡨࡵࡥࡆ࠷࠱ࡺࡅ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠣᤐ"): self.bstack11l1ll1l11l_opy_
        }, file)
    except Exception as e:
      logger.error(bstack1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡹࡵࡲࡪࡰࡪࠤࡨࡵ࡭࡮ࡣࡱࡨࡸࡀࠠࡼࡿࠥᤑ").format(e))
      pass
  def bstack11ll111l1l_opy_(self, bstack1ll11lll11l_opy_):
    try:
      return any(command.get(bstack1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᤒ")) == bstack1ll11lll11l_opy_ for command in self.commands_to_wrap)
    except:
      return False
bstack11l11l1lll_opy_ = bstack11l1l11ll1l_opy_()