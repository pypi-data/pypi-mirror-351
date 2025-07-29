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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1l1lll11_opy_ import bstack11l1l1l1lll_opy_
from bstack_utils.constants import *
import json
class bstack1l1lll1l11_opy_:
    def __init__(self, bstack1l1l1ll111_opy_, bstack11l1l1llll1_opy_):
        self.bstack1l1l1ll111_opy_ = bstack1l1l1ll111_opy_
        self.bstack11l1l1llll1_opy_ = bstack11l1l1llll1_opy_
        self.bstack11l1l1ll111_opy_ = None
    def __call__(self):
        bstack11l1l1ll11l_opy_ = {}
        while True:
            self.bstack11l1l1ll111_opy_ = bstack11l1l1ll11l_opy_.get(
                bstack1ll_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨᝡ"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1l1ll1ll_opy_ = self.bstack11l1l1ll111_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1l1ll1ll_opy_ > 0:
                sleep(bstack11l1l1ll1ll_opy_ / 1000)
            params = {
                bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᝢ"): self.bstack1l1l1ll111_opy_,
                bstack1ll_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬᝣ"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1l1lll1l_opy_ = bstack1ll_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧᝤ") + bstack11l1l1lllll_opy_ + bstack1ll_opy_ (u"ࠦ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡢࡲ࡬࠳ࡻ࠷࠯ࠣᝥ")
            if self.bstack11l1l1llll1_opy_.lower() == bstack1ll_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸࡸࠨᝦ"):
                bstack11l1l1ll11l_opy_ = bstack11l1l1l1lll_opy_.results(bstack11l1l1lll1l_opy_, params)
            else:
                bstack11l1l1ll11l_opy_ = bstack11l1l1l1lll_opy_.bstack11l1l1ll1l1_opy_(bstack11l1l1lll1l_opy_, params)
            if str(bstack11l1l1ll11l_opy_.get(bstack1ll_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ᝧ"), bstack1ll_opy_ (u"ࠧ࠳࠲࠳ࠫᝨ"))) != bstack1ll_opy_ (u"ࠨ࠶࠳࠸ࠬᝩ"):
                break
        return bstack11l1l1ll11l_opy_.get(bstack1ll_opy_ (u"ࠩࡧࡥࡹࡧࠧᝪ"), bstack11l1l1ll11l_opy_)