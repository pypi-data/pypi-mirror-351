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
from time import sleep
from datetime import datetime
from urllib.parse import urlencode
from bstack_utils.bstack11l1l111ll1_opy_ import bstack11l1l111lll_opy_
from bstack_utils.constants import *
import json
class bstack11111l111_opy_:
    def __init__(self, bstack1111ll1ll_opy_, bstack11l1l1111l1_opy_):
        self.bstack1111ll1ll_opy_ = bstack1111ll1ll_opy_
        self.bstack11l1l1111l1_opy_ = bstack11l1l1111l1_opy_
        self.bstack11l1l111l11_opy_ = None
    def __call__(self):
        bstack11l1l1111ll_opy_ = {}
        while True:
            self.bstack11l1l111l11_opy_ = bstack11l1l1111ll_opy_.get(
                bstack1l1_opy_ (u"ࠧ࡯ࡧࡻࡸࡤࡶ࡯࡭࡮ࡢࡸ࡮ࡳࡥࠨᤓ"),
                int(datetime.now().timestamp() * 1000)
            )
            bstack11l1l111l1l_opy_ = self.bstack11l1l111l11_opy_ - int(datetime.now().timestamp() * 1000)
            if bstack11l1l111l1l_opy_ > 0:
                sleep(bstack11l1l111l1l_opy_ / 1000)
            params = {
                bstack1l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᤔ"): self.bstack1111ll1ll_opy_,
                bstack1l1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬᤕ"): int(datetime.now().timestamp() * 1000)
            }
            bstack11l1l11l111_opy_ = bstack1l1_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳ࠧᤖ") + bstack11l1l11l1l1_opy_ + bstack1l1_opy_ (u"ࠦ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡢࡲ࡬࠳ࡻ࠷࠯ࠣᤗ")
            if self.bstack11l1l1111l1_opy_.lower() == bstack1l1_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸࡸࠨᤘ"):
                bstack11l1l1111ll_opy_ = bstack11l1l111lll_opy_.results(bstack11l1l11l111_opy_, params)
            else:
                bstack11l1l1111ll_opy_ = bstack11l1l111lll_opy_.bstack11l1l11l11l_opy_(bstack11l1l11l111_opy_, params)
            if str(bstack11l1l1111ll_opy_.get(bstack1l1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ᤙ"), bstack1l1_opy_ (u"ࠧ࠳࠲࠳ࠫᤚ"))) != bstack1l1_opy_ (u"ࠨ࠶࠳࠸ࠬᤛ"):
                break
        return bstack11l1l1111ll_opy_.get(bstack1l1_opy_ (u"ࠩࡧࡥࡹࡧࠧᤜ"), bstack11l1l1111ll_opy_)