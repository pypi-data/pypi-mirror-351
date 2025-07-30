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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1l1ll1l1ll_opy_():
  def __init__(self, args, logger, bstack1111l1lll1_opy_, bstack1111ll1l1l_opy_, bstack1111l1l11l_opy_):
    self.args = args
    self.logger = logger
    self.bstack1111l1lll1_opy_ = bstack1111l1lll1_opy_
    self.bstack1111ll1l1l_opy_ = bstack1111ll1l1l_opy_
    self.bstack1111l1l11l_opy_ = bstack1111l1l11l_opy_
  def bstack111111l11_opy_(self, bstack1111llll1l_opy_, bstack1llll11l1_opy_, bstack1111l1l1l1_opy_=False):
    bstack1llll1ll_opy_ = []
    manager = multiprocessing.Manager()
    bstack1111ll1ll1_opy_ = manager.list()
    bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
    if bstack1111l1l1l1_opy_:
      for index, platform in enumerate(self.bstack1111l1lll1_opy_[bstack1l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬဤ")]):
        if index == 0:
          bstack1llll11l1_opy_[bstack1l1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ဥ")] = self.args
        bstack1llll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111llll1l_opy_,
                                                    args=(bstack1llll11l1_opy_, bstack1111ll1ll1_opy_)))
    else:
      for index, platform in enumerate(self.bstack1111l1lll1_opy_[bstack1l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧဦ")]):
        bstack1llll1ll_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack1111llll1l_opy_,
                                                    args=(bstack1llll11l1_opy_, bstack1111ll1ll1_opy_)))
    i = 0
    for t in bstack1llll1ll_opy_:
      try:
        if bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ဧ")):
          os.environ[bstack1l1_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧဨ")] = json.dumps(self.bstack1111l1lll1_opy_[bstack1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪဩ")][i % self.bstack1111l1l11l_opy_])
      except Exception as e:
        self.logger.debug(bstack1l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡵࡱࡵ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶ࠾ࠥࢁࡽࠣဪ").format(str(e)))
      i += 1
      t.start()
    for t in bstack1llll1ll_opy_:
      t.join()
    return list(bstack1111ll1ll1_opy_)