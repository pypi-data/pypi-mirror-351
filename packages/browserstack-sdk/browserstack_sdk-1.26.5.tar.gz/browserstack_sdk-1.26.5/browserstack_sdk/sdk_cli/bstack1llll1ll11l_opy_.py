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
import time
import os
import threading
import asyncio
from browserstack_sdk.sdk_cli.bstack1111111l11_opy_ import (
    bstack11111l11ll_opy_,
    bstack111111ll1l_opy_,
    bstack11111l1l1l_opy_,
    bstack111111llll_opy_,
)
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1ll111l1111_opy_, bstack1ll11ll1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1l11_opy_ import bstack1lll1l1ll11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_, bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11lll11_opy_ import bstack1llll1ll111_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l11111_opy_ import bstack1ll111lllll_opy_
from typing import Tuple, List, Any
from bstack_utils.bstack1ll11l1ll_opy_ import bstack1l11l1l1l_opy_, bstack1l111llll1_opy_, bstack11lll1111_opy_
from browserstack_sdk import sdk_pb2 as structs
class bstack1lll1l111l1_opy_(bstack1ll111lllll_opy_):
    bstack1l1l1l111l1_opy_ = bstack1l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡤࡳ࡫ࡹࡩࡷࡹࠢኄ")
    bstack1l1ll1lll11_opy_ = bstack1l1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣኅ")
    bstack1l1l1l1l11l_opy_ = bstack1l1_opy_ (u"ࠥࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧኆ")
    bstack1l1l11lllll_opy_ = bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡶࠦኇ")
    bstack1l1l1l1111l_opy_ = bstack1l1_opy_ (u"ࠧࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡣࡷ࡫ࡦࡴࠤኈ")
    bstack1l1llllll11_opy_ = bstack1l1_opy_ (u"ࠨࡣࡣࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡨࡸࡥࡢࡶࡨࡨࠧ኉")
    bstack1l1l1l11l11_opy_ = bstack1l1_opy_ (u"ࠢࡤࡤࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡴࡡ࡮ࡧࠥኊ")
    bstack1l1l1l1l1l1_opy_ = bstack1l1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡳࡵࡣࡷࡹࡸࠨኋ")
    def __init__(self):
        super().__init__(bstack1ll111ll1l1_opy_=self.bstack1l1l1l111l1_opy_, frameworks=[bstack1lll1l1ll11_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.BEFORE_EACH, bstack1lllll1111l_opy_.POST), self.bstack1l1l1l11ll1_opy_)
        if bstack1ll11ll1_opy_():
            TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.POST), self.bstack1ll11l1llll_opy_)
        else:
            TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.PRE), self.bstack1ll11l1llll_opy_)
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.POST), self.bstack1ll1l11lll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l1l11ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1l11llll1_opy_ = self.bstack1l1l1l11111_opy_(instance.context)
        if not bstack1l1l11llll1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡰࡢࡩࡨ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࠢኌ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠥࠦኍ"))
            return
        f.bstack1llllllll11_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1ll1lll11_opy_, bstack1l1l11llll1_opy_)
    def bstack1l1l1l11111_opy_(self, context: bstack111111llll_opy_, bstack1l1l1l111ll_opy_= True):
        if bstack1l1l1l111ll_opy_:
            bstack1l1l11llll1_opy_ = self.bstack1ll111ll111_opy_(context, reverse=True)
        else:
            bstack1l1l11llll1_opy_ = self.bstack1ll11l1111l_opy_(context, reverse=True)
        return [f for f in bstack1l1l11llll1_opy_ if f[1].state != bstack11111l11ll_opy_.QUIT]
    def bstack1ll11l1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l11ll1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ኎") + str(kwargs) + bstack1l1_opy_ (u"ࠧࠨ኏"))
            return
        bstack1l1l11llll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1l1l11llll1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤነ") + str(kwargs) + bstack1l1_opy_ (u"ࠢࠣኑ"))
            return
        if len(bstack1l1l11llll1_opy_) > 1:
            self.logger.debug(
                bstack1ll1llllll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥኒ"))
        bstack1l1l1l1lll1_opy_, bstack1l1ll11lll1_opy_ = bstack1l1l11llll1_opy_[0]
        page = bstack1l1l1l1lll1_opy_()
        if not page:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤና") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦኔ"))
            return
        bstack1l11lll11l_opy_ = getattr(args[0], bstack1l1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦን"), None)
        try:
            page.evaluate(bstack1l1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨኖ"),
                        bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪኗ") + json.dumps(
                            bstack1l11lll11l_opy_) + bstack1l1_opy_ (u"ࠢࡾࡿࠥኘ"))
        except Exception as e:
            self.logger.debug(bstack1l1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨኙ"), e)
    def bstack1ll1l11lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l11ll1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if not bstack1ll111l1111_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧኚ") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦኛ"))
            return
        bstack1l1l11llll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1l1l11llll1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠦࡴࡴ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢኜ") + str(kwargs) + bstack1l1_opy_ (u"ࠧࠨኝ"))
            return
        if len(bstack1l1l11llll1_opy_) > 1:
            self.logger.debug(
                bstack1ll1llllll1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡰࡢࡩࡨࡣ࡮ࡴࡳࡵࡣࡱࡧࡪࡹࠩࡾࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣኞ"))
        bstack1l1l1l1lll1_opy_, bstack1l1ll11lll1_opy_ = bstack1l1l11llll1_opy_[0]
        page = bstack1l1l1l1lll1_opy_()
        if not page:
            self.logger.debug(bstack1l1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡶࡡࡨࡧࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢኟ") + str(kwargs) + bstack1l1_opy_ (u"ࠣࠤአ"))
            return
        status = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_, None)
        if not status:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧኡ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠥࠦኢ"))
            return
        bstack1l1l1l11lll_opy_ = {bstack1l1_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦኣ"): status.lower()}
        bstack1l1l1l1l111_opy_ = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_, None)
        if status.lower() == bstack1l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬኤ") and bstack1l1l1l1l111_opy_ is not None:
            bstack1l1l1l11lll_opy_[bstack1l1_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭እ")] = bstack1l1l1l1l111_opy_[0][bstack1l1_opy_ (u"ࠧࡣࡣࡦ࡯ࡹࡸࡡࡤࡧࠪኦ")][0] if isinstance(bstack1l1l1l1l111_opy_, list) else str(bstack1l1l1l1l111_opy_)
        try:
              page.evaluate(
                    bstack1l1_opy_ (u"ࠣࡡࠣࡁࡃࠦࡻࡾࠤኧ"),
                    bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࠧከ")
                    + json.dumps(bstack1l1l1l11lll_opy_)
                    + bstack1l1_opy_ (u"ࠥࢁࠧኩ")
                )
        except Exception as e:
            self.logger.debug(bstack1l1_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀࠦኪ"), e)
    def bstack1l1llll111l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l11ll1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if not bstack1ll111l1111_opy_:
            self.logger.debug(
                bstack1ll1llllll1_opy_ (u"ࠧࡳࡡࡳ࡭ࡢࡳ࠶࠷ࡹࡠࡵࡼࡲࡨࡀࠠ࡯ࡱࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࡽ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࢂࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨካ"))
            return
        bstack1l1l11llll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1l1l11llll1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠨ࡯࡯ࡡࡥࡩ࡫ࡵࡲࡦࡡࡷࡩࡸࡺ࠺ࠡࡰࡲࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤኬ") + str(kwargs) + bstack1l1_opy_ (u"ࠢࠣክ"))
            return
        if len(bstack1l1l11llll1_opy_) > 1:
            self.logger.debug(
                bstack1ll1llllll1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࡽ࡮ࡻࡦࡸࡧࡴࡿࠥኮ"))
        bstack1l1l1l1lll1_opy_, bstack1l1ll11lll1_opy_ = bstack1l1l11llll1_opy_[0]
        page = bstack1l1l1l1lll1_opy_()
        if not page:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡰࡥࡷࡱ࡟ࡰ࠳࠴ࡽࡤࡹࡹ࡯ࡥ࠽ࠤࡳࡵࠠࡱࡣࡪࡩࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤኯ") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦኰ"))
            return
        timestamp = int(time.time() * 1000)
        data = bstack1l1_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤ኱") + str(timestamp)
        try:
            page.evaluate(
                bstack1l1_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨኲ"),
                bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫኳ").format(
                    json.dumps(
                        {
                            bstack1l1_opy_ (u"ࠢࡢࡥࡷ࡭ࡴࡴࠢኴ"): bstack1l1_opy_ (u"ࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥኵ"),
                            bstack1l1_opy_ (u"ࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧ኶"): {
                                bstack1l1_opy_ (u"ࠥࡸࡾࡶࡥࠣ኷"): bstack1l1_opy_ (u"ࠦࡆࡴ࡮ࡰࡶࡤࡸ࡮ࡵ࡮ࠣኸ"),
                                bstack1l1_opy_ (u"ࠧࡪࡡࡵࡣࠥኹ"): data,
                                bstack1l1_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࠧኺ"): bstack1l1_opy_ (u"ࠢࡥࡧࡥࡹ࡬ࠨኻ")
                            }
                        }
                    )
                )
            )
        except Exception as e:
            self.logger.debug(bstack1l1_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡴ࠷࠱ࡺࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦ࡭ࡢࡴ࡮࡭ࡳ࡭ࠠࡼࡿࠥኼ"), e)
    def bstack1l1lll1l11l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l1l1l11ll1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if f.bstack1llllll1lll_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1llllll11_opy_, False):
            return
        self.bstack1ll1l111111_opy_()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll1l11ll1l_opy_)
        req.test_framework_name = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll11llll11_opy_)
        req.test_framework_version = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1llll1111_opy_)
        req.test_framework_state = bstack1llllll1l1l_opy_[0].name
        req.test_hook_state = bstack1llllll1l1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll1l11l11l_opy_)
        for bstack1l1l1l1ll11_opy_ in bstack1llll1ll111_opy_.bstack1111111111_opy_.values():
            session = req.automation_sessions.add()
            session.provider = (
                bstack1l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠣኽ")
                if bstack1ll111l1111_opy_
                else bstack1l1_opy_ (u"ࠥࡹࡳࡱ࡮ࡰࡹࡱࡣ࡬ࡸࡩࡥࠤኾ")
            )
            session.ref = bstack1l1l1l1ll11_opy_.ref()
            session.hub_url = bstack1llll1ll111_opy_.bstack1llllll1lll_opy_(bstack1l1l1l1ll11_opy_, bstack1llll1ll111_opy_.bstack1l1l1llllll_opy_, bstack1l1_opy_ (u"ࠦࠧ኿"))
            session.framework_name = bstack1l1l1l1ll11_opy_.framework_name
            session.framework_version = bstack1l1l1l1ll11_opy_.framework_version
            session.framework_session_id = bstack1llll1ll111_opy_.bstack1llllll1lll_opy_(bstack1l1l1l1ll11_opy_, bstack1llll1ll111_opy_.bstack1l1l1ll11l1_opy_, bstack1l1_opy_ (u"ࠧࠨዀ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll1l111lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1l11llll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1l111l1_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1l1l11llll1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠨࡧࡦࡶࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡰࡲࠤࡵࡧࡧࡦࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢ዁") + str(kwargs) + bstack1l1_opy_ (u"ࠢࠣዂ"))
            return
        if len(bstack1l1l11llll1_opy_) > 1:
            self.logger.debug(bstack1l1_opy_ (u"ࠣࡩࡨࡸࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࡱ࡫࡮ࠩࡲࡤ࡫ࡪࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤዃ") + str(kwargs) + bstack1l1_opy_ (u"ࠤࠥዄ"))
        bstack1l1l1l1lll1_opy_, bstack1l1ll11lll1_opy_ = bstack1l1l11llll1_opy_[0]
        page = bstack1l1l1l1lll1_opy_()
        if not page:
            self.logger.debug(bstack1l1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡩࡸࡩࡷࡧࡵ࠾ࠥࡴ࡯ࠡࡲࡤ࡫ࡪࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥዅ") + str(kwargs) + bstack1l1_opy_ (u"ࠦࠧ዆"))
            return
        return page
    def bstack1ll11ll11l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs
    ):
        caps = {}
        bstack1l1l1l11l1l_opy_ = {}
        for bstack1l1l1l1ll11_opy_ in bstack1llll1ll111_opy_.bstack1111111111_opy_.values():
            caps = bstack1llll1ll111_opy_.bstack1llllll1lll_opy_(bstack1l1l1l1ll11_opy_, bstack1llll1ll111_opy_.bstack1l1l1ll1lll_opy_, bstack1l1_opy_ (u"ࠧࠨ዇"))
        bstack1l1l1l11l1l_opy_[bstack1l1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠦወ")] = caps.get(bstack1l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣዉ"), bstack1l1_opy_ (u"ࠣࠤዊ"))
        bstack1l1l1l11l1l_opy_[bstack1l1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣዋ")] = caps.get(bstack1l1_opy_ (u"ࠥࡳࡸࠨዌ"), bstack1l1_opy_ (u"ࠦࠧው"))
        bstack1l1l1l11l1l_opy_[bstack1l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠢዎ")] = caps.get(bstack1l1_opy_ (u"ࠨ࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠥዏ"), bstack1l1_opy_ (u"ࠢࠣዐ"))
        bstack1l1l1l11l1l_opy_[bstack1l1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠤዑ")] = caps.get(bstack1l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠦዒ"), bstack1l1_opy_ (u"ࠥࠦዓ"))
        return bstack1l1l1l11l1l_opy_
    def bstack1ll1l1l11ll_opy_(self, page: object, bstack1ll1ll11l1l_opy_, args={}):
        try:
            bstack1l1l1l1ll1l_opy_ = bstack1l1_opy_ (u"ࠦࠧࠨࠨࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࠫ࠲࠳࠴ࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸ࠯ࠠࡼࡽࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡸࡥࡵࡷࡵࡲࠥࡴࡥࡸࠢࡓࡶࡴࡳࡩࡴࡧࠫࠬࡷ࡫ࡳࡰ࡮ࡹࡩ࠱ࠦࡲࡦ࡬ࡨࡧࡹ࠯ࠠ࠾ࡀࠣࡿࢀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡳࡵࡣࡦ࡯ࡘࡪ࡫ࡂࡴࡪࡷ࠳ࡶࡵࡴࡪࠫࡶࡪࡹ࡯࡭ࡸࡨ࠭ࡀࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࢁࡦ࡯ࡡࡥࡳࡩࡿࡽࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࢁࢂ࠯࠻ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽࡾࠫࠫࡿࡦࡸࡧࡠ࡬ࡶࡳࡳࢃࠩࠣࠤࠥዔ")
            bstack1ll1ll11l1l_opy_ = bstack1ll1ll11l1l_opy_.replace(bstack1l1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣዕ"), bstack1l1_opy_ (u"ࠨࡢࡴࡶࡤࡧࡰ࡙ࡤ࡬ࡃࡵ࡫ࡸࠨዖ"))
            script = bstack1l1l1l1ll1l_opy_.format(fn_body=bstack1ll1ll11l1l_opy_, arg_json=json.dumps(args))
            return page.evaluate(script)
        except Exception as e:
            self.logger.error(bstack1l1_opy_ (u"ࠢࡢ࠳࠴ࡽࡤࡹࡣࡳ࡫ࡳࡸࡤ࡫ࡸࡦࡥࡸࡸࡪࡀࠠࡆࡴࡵࡳࡷࠦࡥࡹࡧࡦࡹࡹ࡯࡮ࡨࠢࡷ࡬ࡪࠦࡡ࠲࠳ࡼࠤࡸࡩࡲࡪࡲࡷ࠰ࠥࠨ዗") + str(e) + bstack1l1_opy_ (u"ࠣࠤዘ"))