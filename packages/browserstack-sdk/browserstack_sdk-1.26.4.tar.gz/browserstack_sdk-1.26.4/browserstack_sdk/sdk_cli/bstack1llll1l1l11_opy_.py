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
import time
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import (
    bstack11111l11l1_opy_,
    bstack1llllll1lll_opy_,
    bstack1llllllllll_opy_,
    bstack1llllll11ll_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1llllllll_opy_, bstack1l11l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_, bstack1lll1l11lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1llll1ll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll111ll1l1_opy_ import bstack1ll111l1lll_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1ll11l111_opy_ import bstack11ll11l1ll_opy_, bstack11llll111_opy_, bstack11l11ll111_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1llll111lll_opy_(bstack1ll111l1lll_opy_):
    bstack1l1l11llll1_opy_ = bstack1ll_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡳ࡫ࡹࡩࡷࡹࠢኄ")
    bstack1l1lll1ll1l_opy_ = bstack1ll_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣኅ")
    bstack1l1l1l1lll1_opy_ = bstack1ll_opy_ (u"ࠥࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧኆ")
    bstack1l1l1l1l111_opy_ = bstack1ll_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦኇ")
    bstack1l1l1l111ll_opy_ = bstack1ll_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡣࡷ࡫ࡦࡴࠤኈ")
    bstack1l1llll1l1l_opy_ = bstack1ll_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡨࡸࡥࡢࡶࡨࡨࠧ኉")
    bstack1l1l1l1ll1l_opy_ = bstack1ll_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡴࡡ࡮ࡧࠥኊ")
    bstack1l1l1l11l1l_opy_ = bstack1ll_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡳࡵࡣࡷࡹࡸࠨኋ")
    def __init__(self):
        super().__init__(bstack1ll111ll1ll_opy_=self.bstack1l1l11llll1_opy_, frameworks=[bstack1lll111l11l_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.BEFORE_EACH, bstack1lllll1l1ll_opy_.POST), self.bstack1l1l1l1l1ll_opy_)
        if bstack1l11l1ll_opy_():
            TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.POST), self.bstack1ll1ll111l1_opy_)
        else:
            TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.PRE), self.bstack1ll1ll111l1_opy_)
        TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.POST), self.bstack1ll11llllll_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1l1l1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l1l11l11_opy_ = self.bstack1l1l1l111l1_opy_(instance.context)
        if not bstack1l1l1l11l11_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡰࡢࡩࡨ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢኌ") + str(bstack111111ll1l_opy_) + bstack1ll_opy_ (u"ࠥࠦኍ"))
            return
        f.bstack111111l1l1_opy_(instance, bstack1llll111lll_opy_.bstack1l1lll1ll1l_opy_, bstack1l1l1l11l11_opy_)
    def bstack1l1l1l111l1_opy_(self, context: bstack1llllll11ll_opy_, bstack1l1l1l1llll_opy_= True):
        if bstack1l1l1l1llll_opy_:
            bstack1l1l1l11l11_opy_ = self.bstack1ll11l1111l_opy_(context, reverse=True)
        else:
            bstack1l1l1l11l11_opy_ = self.bstack1ll111l1l11_opy_(context, reverse=True)
        return [f for f in bstack1l1l1l11l11_opy_ if f[1].state != bstack11111l11l1_opy_.QUIT]
    def bstack1ll1ll111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l1l1ll_opy_(f, instance, bstack111111ll1l_opy_, *args, **kwargs)
        if not bstack1l1llllllll_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ኎") + str(kwargs) + bstack1ll_opy_ (u"ࠧࠨ኏"))
            return
        bstack1l1l1l11l11_opy_ = f.bstack1111111lll_opy_(instance, bstack1llll111lll_opy_.bstack1l1lll1ll1l_opy_, [])
        if not bstack1l1l1l11l11_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤነ") + str(kwargs) + bstack1ll_opy_ (u"ࠢࠣኑ"))
            return
        if len(bstack1l1l1l11l11_opy_) > 1:
            self.logger.debug(
                bstack1lllll1111l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥኒ"))
        bstack1l1l1l11ll1_opy_, bstack1l1ll11l1ll_opy_ = bstack1l1l1l11l11_opy_[0]
        page = bstack1l1l1l11ll1_opy_()
        if not page:
            self.logger.debug(bstack1ll_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤና") + str(kwargs) + bstack1ll_opy_ (u"ࠥࠦኔ"))
            return
        bstack1lll11l11_opy_ = getattr(args[0], bstack1ll_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦን"), None)
        try:
            page.evaluate(bstack1ll_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨኖ"),
                        bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪኗ") + json.dumps(
                            bstack1lll11l11_opy_) + bstack1ll_opy_ (u"ࠢࡾࡿࠥኘ"))
        except Exception as e:
            self.logger.debug(bstack1ll_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨኙ"), e)
    def bstack1ll11llllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l1l1ll_opy_(f, instance, bstack111111ll1l_opy_, *args, **kwargs)
        if not bstack1l1llllllll_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧኚ") + str(kwargs) + bstack1ll_opy_ (u"ࠥࠦኛ"))
            return
        bstack1l1l1l11l11_opy_ = f.bstack1111111lll_opy_(instance, bstack1llll111lll_opy_.bstack1l1lll1ll1l_opy_, [])
        if not bstack1l1l1l11l11_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢኜ") + str(kwargs) + bstack1ll_opy_ (u"ࠧࠨኝ"))
            return
        if len(bstack1l1l1l11l11_opy_) > 1:
            self.logger.debug(
                bstack1lllll1111l_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣኞ"))
        bstack1l1l1l11ll1_opy_, bstack1l1ll11l1ll_opy_ = bstack1l1l1l11l11_opy_[0]
        page = bstack1l1l1l11ll1_opy_()
        if not page:
            self.logger.debug(bstack1ll_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢኟ") + str(kwargs) + bstack1ll_opy_ (u"ࠣࠤአ"))
            return
        status = f.bstack1111111lll_opy_(instance, TestFramework.bstack1l1l1l1l11l_opy_, None)
        if not status:
            self.logger.debug(bstack1ll_opy_ (u"ࠤࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧኡ") + str(bstack111111ll1l_opy_) + bstack1ll_opy_ (u"ࠥࠦኢ"))
            return
        bstack1l1l1l11111_opy_ = {bstack1ll_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦኣ"): status.lower()}
        bstack1l1l1l1ll11_opy_ = f.bstack1111111lll_opy_(instance, TestFramework.bstack1l1l1l1l1l1_opy_, None)
        if status.lower() == bstack1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬኤ") and bstack1l1l1l1ll11_opy_ is not None:
            bstack1l1l1l11111_opy_[bstack1ll_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭እ")] = bstack1l1l1l1ll11_opy_[0][bstack1ll_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪኦ")][0] if isinstance(bstack1l1l1l1ll11_opy_, list) else str(bstack1l1l1l1ll11_opy_)
        try:
              page.evaluate(
                    bstack1ll_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤኧ"),
                    bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࠧከ")
                    + json.dumps(bstack1l1l1l11111_opy_)
                    + bstack1ll_opy_ (u"ࠥࢁࠧኩ")
                )
        except Exception as e:
            self.logger.debug(bstack1ll_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀࠦኪ"), e)
    def bstack1l1llll1l11_opy_(
        self,
        instance: bstack1lll1l11lll_opy_,
        f: TestFramework,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l1l1ll_opy_(f, instance, bstack111111ll1l_opy_, *args, **kwargs)
        if not bstack1l1llllllll_opy_:
            self.logger.debug(
                bstack1lllll1111l_opy_ (u"ࠧࡳࡡࡳ࡭ࡢࡳ࠶࠷ࡹࡠࡵࡼࡲࡨࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨካ"))
            return
        bstack1l1l1l11l11_opy_ = f.bstack1111111lll_opy_(instance, bstack1llll111lll_opy_.bstack1l1lll1ll1l_opy_, [])
        if not bstack1l1l1l11l11_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤኬ") + str(kwargs) + bstack1ll_opy_ (u"ࠢࠣክ"))
            return
        if len(bstack1l1l1l11l11_opy_) > 1:
            self.logger.debug(
                bstack1lllll1111l_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥኮ"))
        bstack1l1l1l11ll1_opy_, bstack1l1ll11l1ll_opy_ = bstack1l1l1l11l11_opy_[0]
        page = bstack1l1l1l11ll1_opy_()
        if not page:
            self.logger.debug(bstack1ll_opy_ (u"ࠤࡰࡥࡷࡱ࡟ࡰ࠳࠴ࡽࡤࡹࡹ࡯ࡥ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤኯ") + str(kwargs) + bstack1ll_opy_ (u"ࠥࠦኰ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack1ll_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤ኱") + str(timestamp)
        try:
            page.evaluate(
                bstack1ll_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨኲ"),
                bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫኳ").format(
                    json.dumps(
                        {
                            bstack1ll_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢኴ"): bstack1ll_opy_ (u"ࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥኵ"),
                            bstack1ll_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧ኶"): {
                                bstack1ll_opy_ (u"ࠥࡸࡾࡶࡥࠣ኷"): bstack1ll_opy_ (u"ࠦࡆࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠣኸ"),
                                bstack1ll_opy_ (u"ࠧࡪࡡࡵࡣࠥኹ"): data,
                                bstack1ll_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࠧኺ"): bstack1ll_opy_ (u"ࠢࡥࡧࡥࡹ࡬ࠨኻ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack1ll_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡴ࠷࠱ࡺࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡼࡿࠥኼ"), e)
    def bstack1ll1111llll_opy_(
        self,
        instance: bstack1lll1l11lll_opy_,
        f: TestFramework,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l1l1ll_opy_(f, instance, bstack111111ll1l_opy_, *args, **kwargs)
        if f.bstack1111111lll_opy_(instance, bstack1llll111lll_opy_.bstack1l1llll1l1l_opy_, False):
            return
        self.bstack1ll1l1l1lll_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l1l111l_opy_)
        req.test_framework_name = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l1lll11_opy_)
        req.test_framework_version = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1111l11l_opy_)
        req.test_framework_state = bstack111111ll1l_opy_[0].name
        req.test_hook_state = bstack111111ll1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l11111l_opy_)
        for bstack1l1l1l1111l_opy_ in bstack1llll1ll111_opy_.bstack11111l111l_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack1ll_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠣኽ")
                if bstack1l1llllllll_opy_
                else bstack1ll_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱࡣ࡬ࡸࡩࡥࠤኾ")
            )
            session.ref = bstack1l1l1l1111l_opy_.ref()
            session.hub_url = bstack1llll1ll111_opy_.bstack1111111lll_opy_(bstack1l1l1l1111l_opy_, bstack1llll1ll111_opy_.bstack1l1l1lll1l1_opy_, bstack1ll_opy_ (u"ࠦࠧ኿"))
            session.framework_name = bstack1l1l1l1111l_opy_.framework_name
            session.framework_version = bstack1l1l1l1111l_opy_.framework_version
            session.framework_session_id = bstack1llll1ll111_opy_.bstack1111111lll_opy_(bstack1l1l1l1111l_opy_, bstack1llll1ll111_opy_.bstack1l1l1ll111l_opy_, bstack1ll_opy_ (u"ࠧࠨዀ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11ll11ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l1l11l11_opy_ = f.bstack1111111lll_opy_(instance, bstack1llll111lll_opy_.bstack1l1lll1ll1l_opy_, [])
        if not bstack1l1l1l11l11_opy_:
            self.logger.debug(bstack1ll_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ዁") + str(kwargs) + bstack1ll_opy_ (u"ࠢࠣዂ"))
            return
        if len(bstack1l1l1l11l11_opy_) > 1:
            self.logger.debug(bstack1ll_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤዃ") + str(kwargs) + bstack1ll_opy_ (u"ࠤࠥዄ"))
        bstack1l1l1l11ll1_opy_, bstack1l1ll11l1ll_opy_ = bstack1l1l1l11l11_opy_[0]
        page = bstack1l1l1l11ll1_opy_()
        if not page:
            self.logger.debug(bstack1ll_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥዅ") + str(kwargs) + bstack1ll_opy_ (u"ࠦࠧ዆"))
            return
        return page
    def bstack1ll11lll11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l1l11lllll_opy_ = {}
        for bstack1l1l1l1111l_opy_ in bstack1llll1ll111_opy_.bstack11111l111l_opy_.values():
            caps = bstack1llll1ll111_opy_.bstack1111111lll_opy_(bstack1l1l1l1111l_opy_, bstack1llll1ll111_opy_.bstack1l1l1lllll1_opy_, bstack1ll_opy_ (u"ࠧࠨ዇"))
        bstack1l1l11lllll_opy_[bstack1ll_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠦወ")] = caps.get(bstack1ll_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣዉ"), bstack1ll_opy_ (u"ࠣࠤዊ"))
        bstack1l1l11lllll_opy_[bstack1ll_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣዋ")] = caps.get(bstack1ll_opy_ (u"ࠥࡳࡸࠨዌ"), bstack1ll_opy_ (u"ࠦࠧው"))
        bstack1l1l11lllll_opy_[bstack1ll_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢዎ")] = caps.get(bstack1ll_opy_ (u"ࠨ࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠥዏ"), bstack1ll_opy_ (u"ࠢࠣዐ"))
        bstack1l1l11lllll_opy_[bstack1ll_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠤዑ")] = caps.get(bstack1ll_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠦዒ"), bstack1ll_opy_ (u"ࠥࠦዓ"))
        return bstack1l1l11lllll_opy_
    def bstack1ll11ll1ll1_opy_(self, page: object, bstack1ll11lll1l1_opy_, args={}):
        try:
            bstack1l1l1l11lll_opy_ = bstack1ll_opy_ (u"ࠦࠧࠨࠨࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࠫ࠲࠳࠴ࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡸࡥࡵࡷࡵࡲࠥࡴࡥࡸࠢࡓࡶࡴࡳࡩࡴࡧࠫࠬࡷ࡫ࡳࡰ࡮ࡹࡩ࠱ࠦࡲࡦ࡬ࡨࡧࡹ࠯ࠠ࠾ࡀࠣࡿࢀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡳࡵࡣࡦ࡯ࡘࡪ࡫ࡂࡴࡪࡷ࠳ࡶࡵࡴࡪࠫࡶࡪࡹ࡯࡭ࡸࡨ࠭ࡀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢁࡦ࡯ࡡࡥࡳࡩࡿࡽࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࢂ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽࡾࠫࠫࡿࡦࡸࡧࡠ࡬ࡶࡳࡳࢃࠩࠣࠤࠥዔ")
            bstack1ll11lll1l1_opy_ = bstack1ll11lll1l1_opy_.replace(bstack1ll_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣዕ"), bstack1ll_opy_ (u"ࠨࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸࠨዖ"))
            script = bstack1l1l1l11lll_opy_.format(fn_body=bstack1ll11lll1l1_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack1ll_opy_ (u"ࠢࡢ࠳࠴ࡽࡤࡹࡣࡳ࡫ࡳࡸࡤ࡫ࡸࡦࡥࡸࡸࡪࡀࠠࡆࡴࡵࡳࡷࠦࡥࡹࡧࡦࡹࡹ࡯࡮ࡨࠢࡷ࡬ࡪࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷ࠰ࠥࠨ዗") + str(e) + bstack1ll_opy_ (u"ࠣࠤዘ"))