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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1llllll11l_opy_():
  def __init__(self, args, logger, bstack1111lll1ll_opy_, bstack1111lll11l_opy_, bstack1111l1l1l1_opy_):
    self.args = args
    self.logger = logger
    self.bstack1111lll1ll_opy_ = bstack1111lll1ll_opy_
    self.bstack1111lll11l_opy_ = bstack1111lll11l_opy_
    self.bstack1111l1l1l1_opy_ = bstack1111l1l1l1_opy_
  def bstack1l1l1ll11_opy_(self, bstack1111l1llll_opy_, bstack1llllll1ll_opy_, bstack1111l1l11l_opy_=False):
    bstack11111l11l_opy_ = []
    manager = multiprocessing.Manager()
    bstack1111l1ll1l_opy_ = manager.list()
    bstack1lll1111ll_opy_ = Config.bstack11ll1l1l_opy_()
    if bstack1111l1l11l_opy_:
      for index, platform in enumerate(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬဤ")]):
        if index == 0:
          bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ဥ")] = self.args
        bstack11111l11l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111l1llll_opy_,
                                                    args=(bstack1llllll1ll_opy_, bstack1111l1ll1l_opy_)))
    else:
      for index, platform in enumerate(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧဦ")]):
        bstack11111l11l_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111l1llll_opy_,
                                                    args=(bstack1llllll1ll_opy_, bstack1111l1ll1l_opy_)))
    i = 0
    for t in bstack11111l11l_opy_:
      try:
        if bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ဧ")):
          os.environ[bstack1ll_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧဨ")] = json.dumps(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪဩ")][i % self.bstack1111l1l1l1_opy_])
      except Exception as e:
        self.logger.debug(bstack1ll_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡵࡱࡵ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶ࠾ࠥࢁࡽࠣဪ").format(str(e)))
      i += 1
      t.start()
    for t in bstack11111l11l_opy_:
      t.join()
    return list(bstack1111l1ll1l_opy_)