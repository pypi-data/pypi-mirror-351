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
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1111111l11_opy_ import (
    bstack11111l11ll_opy_,
    bstack111111ll1l_opy_,
    bstack111111111l_opy_,
    bstack11111l1l1l_opy_,
    bstack111111llll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1l11_opy_ import bstack1lll1l1ll11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_, bstack1lll111l1ll_opy_
from browserstack_sdk.sdk_cli.bstack1ll11l11111_opy_ import bstack1ll111lllll_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1ll111l1111_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1lll1llllll_opy_(bstack1ll111lllll_opy_):
    bstack1l1l1l111l1_opy_ = bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡷ࡯ࡶࡦࡴࡶࠦጰ")
    bstack1l1ll1lll11_opy_ = bstack1l1_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧጱ")
    bstack1l1l1l1l11l_opy_ = bstack1l1_opy_ (u"ࠢ࡯ࡱࡱࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤጲ")
    bstack1l1l11lllll_opy_ = bstack1l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣጳ")
    bstack1l1l1l1111l_opy_ = bstack1l1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡠࡴࡨࡪࡸࠨጴ")
    bstack1l1llllll11_opy_ = bstack1l1_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡥࡵࡩࡦࡺࡥࡥࠤጵ")
    bstack1l1l1l11l11_opy_ = bstack1l1_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢጶ")
    bstack1l1l1l1l1l1_opy_ = bstack1l1_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠥጷ")
    def __init__(self):
        super().__init__(bstack1ll111ll1l1_opy_=self.bstack1l1l1l111l1_opy_, frameworks=[bstack1lll1l1ll11_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.BEFORE_EACH, bstack1lllll1111l_opy_.POST), self.bstack1l11llll1l1_opy_)
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.PRE), self.bstack1ll11l1llll_opy_)
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.POST), self.bstack1ll1l11lll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11llll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1ll1l11l1_opy_ = self.bstack1l1l111111l_opy_(instance.context)
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤጸ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠢࠣጹ"))
        f.bstack1llllllll11_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, bstack1l1ll1l11l1_opy_)
        bstack1l1l1111111_opy_ = self.bstack1l1l111111l_opy_(instance.context, bstack1l11lllll11_opy_=False)
        f.bstack1llllllll11_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l11l_opy_, bstack1l1l1111111_opy_)
    def bstack1ll11l1llll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll1l1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l11l11_opy_, False):
            self.__1l11llllll1_opy_(f,instance,bstack1llllll1l1l_opy_)
    def bstack1ll1l11lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll1l1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l11l11_opy_, False):
            self.__1l11llllll1_opy_(f, instance, bstack1llllll1l1l_opy_)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l1l1_opy_, False):
            self.__1l11lll1lll_opy_(f, instance, bstack1llllll1l1l_opy_)
    def bstack1l11llll111_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1ll111ll1ll_opy_(instance):
            return
        if f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l1l1_opy_, False):
            return
        driver.execute_script(
            bstack1l1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂࠨጺ").format(
                json.dumps(
                    {
                        bstack1l1_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤጻ"): bstack1l1_opy_ (u"ࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨጼ"),
                        bstack1l1_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢጽ"): {bstack1l1_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧጾ"): result},
                    }
                )
            )
        )
        f.bstack1llllllll11_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l1l1_opy_, True)
    def bstack1l1l111111l_opy_(self, context: bstack111111llll_opy_, bstack1l11lllll11_opy_= True):
        if bstack1l11lllll11_opy_:
            bstack1l1ll1l11l1_opy_ = self.bstack1ll111ll111_opy_(context, reverse=True)
        else:
            bstack1l1ll1l11l1_opy_ = self.bstack1ll11l1111l_opy_(context, reverse=True)
        return [f for f in bstack1l1ll1l11l1_opy_ if f[1].state != bstack11111l11ll_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1ll1l11l1_opy_, stage=STAGE.bstack1111lll11_opy_)
    def __1l11lll1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦጿ")).get(bstack1l1_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦፀ")):
            bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
            if not bstack1l1ll1l11l1_opy_:
                self.logger.debug(bstack1l1_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦፁ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠤࠥፂ"))
                return
            driver = bstack1l1ll1l11l1_opy_[0][0]()
            status = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l1l1l1ll_opy_, None)
            if not status:
                self.logger.debug(bstack1l1_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧፃ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠦࠧፄ"))
                return
            bstack1l1l1l11lll_opy_ = {bstack1l1_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧፅ"): status.lower()}
            bstack1l1l1l1l111_opy_ = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_, None)
            if status.lower() == bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ፆ") and bstack1l1l1l1l111_opy_ is not None:
                bstack1l1l1l11lll_opy_[bstack1l1_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧፇ")] = bstack1l1l1l1l111_opy_[0][bstack1l1_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫፈ")][0] if isinstance(bstack1l1l1l1l111_opy_, list) else str(bstack1l1l1l1l111_opy_)
            driver.execute_script(
                bstack1l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢፉ").format(
                    json.dumps(
                        {
                            bstack1l1_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥፊ"): bstack1l1_opy_ (u"ࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢፋ"),
                            bstack1l1_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣፌ"): bstack1l1l1l11lll_opy_,
                        }
                    )
                )
            )
            f.bstack1llllllll11_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l1l1_opy_, True)
    @measure(event_name=EVENTS.bstack1l111111l1_opy_, stage=STAGE.bstack1111lll11_opy_)
    def __1l11llllll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦፍ")).get(bstack1l1_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤፎ")):
            test_name = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l11llll11l_opy_, None)
            if not test_name:
                self.logger.debug(bstack1l1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢፏ"))
                return
            bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
            if not bstack1l1ll1l11l1_opy_:
                self.logger.debug(bstack1l1_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡸࡺࡡࡵࡷࡶࠤ࡫ࡵࡲࠡࡶࡨࡷࡹ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦፐ") + str(bstack1llllll1l1l_opy_) + bstack1l1_opy_ (u"ࠥࠦፑ"))
                return
            for bstack1l1ll111l1l_opy_, bstack1l11lllll1l_opy_ in bstack1l1ll1l11l1_opy_:
                if not bstack1lll1l1ll11_opy_.bstack1ll111ll1ll_opy_(bstack1l11lllll1l_opy_):
                    continue
                driver = bstack1l1ll111l1l_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤፒ").format(
                        json.dumps(
                            {
                                bstack1l1_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧፓ"): bstack1l1_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢፔ"),
                                bstack1l1_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥፕ"): {bstack1l1_opy_ (u"ࠣࡰࡤࡱࡪࠨፖ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1llllllll11_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l11l11_opy_, True)
    def bstack1l1llll111l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll1l1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        bstack1l1ll1l11l1_opy_ = [d for d, _ in f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])]
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤፗ"))
            return
        if not bstack1ll111l1111_opy_():
            self.logger.debug(bstack1l1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣፘ"))
            return
        for bstack1l11llll1ll_opy_ in bstack1l1ll1l11l1_opy_:
            driver = bstack1l11llll1ll_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1l1_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤፙ") + str(timestamp)
            driver.execute_script(
                bstack1l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥፚ").format(
                    json.dumps(
                        {
                            bstack1l1_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨ፛"): bstack1l1_opy_ (u"ࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ፜"),
                            bstack1l1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ፝"): {
                                bstack1l1_opy_ (u"ࠤࡷࡽࡵ࡫ࠢ፞"): bstack1l1_opy_ (u"ࠥࡅࡳࡴ࡯ࡵࡣࡷ࡭ࡴࡴࠢ፟"),
                                bstack1l1_opy_ (u"ࠦࡩࡧࡴࡢࠤ፠"): data,
                                bstack1l1_opy_ (u"ࠧࡲࡥࡷࡧ࡯ࠦ፡"): bstack1l1_opy_ (u"ࠨࡤࡦࡤࡸ࡫ࠧ።")
                            }
                        }
                    )
                )
            )
    def bstack1l1lll1l11l_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        f: TestFramework,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11llll1l1_opy_(f, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
        keys = [
            bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_,
            bstack1lll1llllll_opy_.bstack1l1l1l1l11l_opy_,
        ]
        bstack1l1ll1l11l1_opy_ = []
        for key in keys:
            bstack1l1ll1l11l1_opy_.extend(f.bstack1llllll1lll_opy_(instance, key, []))
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡷࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡤࡲࡾࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤ፣"))
            return
        if f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1llllll11_opy_, False):
            self.logger.debug(bstack1l1_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡆࡆ࡙ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡤࡴࡨࡥࡹ࡫ࡤࠣ፤"))
            return
        self.bstack1ll1l111111_opy_()
        bstack11111ll11_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll1l11ll1l_opy_)
        req.test_framework_name = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll11llll11_opy_)
        req.test_framework_version = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1llll1111_opy_)
        req.test_framework_state = bstack1llllll1l1l_opy_[0].name
        req.test_hook_state = bstack1llllll1l1l_opy_[1].name
        req.test_uuid = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll1l11l11l_opy_)
        for bstack1l1ll111l1l_opy_, driver in bstack1l1ll1l11l1_opy_:
            try:
                webdriver = bstack1l1ll111l1l_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1l1_opy_ (u"ࠤ࡚ࡩࡧࡊࡲࡪࡸࡨࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡪࡵࠣࡒࡴࡴࡥࠡࠪࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࠥ࡫ࡸࡱ࡫ࡵࡩࡩ࠯ࠢ፥"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠤ፦")
                    if bstack1lll1l1ll11_opy_.bstack1llllll1lll_opy_(driver, bstack1lll1l1ll11_opy_.bstack1l11lllllll_opy_, False)
                    else bstack1l1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࡤ࡭ࡲࡪࡦࠥ፧")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1lll1l1ll11_opy_.bstack1llllll1lll_opy_(driver, bstack1lll1l1ll11_opy_.bstack1l1l1llllll_opy_, bstack1l1_opy_ (u"ࠧࠨ፨"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1lll1l1ll11_opy_.bstack1llllll1lll_opy_(driver, bstack1lll1l1ll11_opy_.bstack1l1l1ll11l1_opy_, bstack1l1_opy_ (u"ࠨࠢ፩"))
                caps = None
                if hasattr(webdriver, bstack1l1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨ፪")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1l1_opy_ (u"ࠣࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡧ࡭ࡷ࡫ࡣࡵ࡮ࡼࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠰ࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣ፫"))
                    except Exception as e:
                        self.logger.debug(bstack1l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡨࡵࡳࡲࠦࡤࡳ࡫ࡹࡩࡷ࠴ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠿ࠦࠢ፬") + str(e) + bstack1l1_opy_ (u"ࠥࠦ፭"))
                try:
                    bstack1l11lll1ll1_opy_ = json.dumps(caps).encode(bstack1l1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥ፮")) if caps else bstack1l11lll1l1l_opy_ (u"ࠧࢁࡽࠣ፯")
                    req.capabilities = bstack1l11lll1ll1_opy_
                except Exception as e:
                    self.logger.debug(bstack1l1_opy_ (u"ࠨࡧࡦࡶࡢࡧࡧࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡴࡤࠡࡵࡨࡶ࡮ࡧ࡬ࡪࡼࡨࠤࡨࡧࡰࡴࠢࡩࡳࡷࠦࡲࡦࡳࡸࡩࡸࡺ࠺ࠡࠤ፰") + str(e) + bstack1l1_opy_ (u"ࠢࠣ፱"))
            except Exception as e:
                self.logger.error(bstack1l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡩࡸࡩࡷࡧࡵࠤ࡮ࡺࡥ࡮࠼ࠣࠦ፲") + str(str(e)) + bstack1l1_opy_ (u"ࠤࠥ፳"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll11ll11l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1ll111l1111_opy_() and len(bstack1l1ll1l11l1_opy_) == 0:
            bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l11l_opy_, [])
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨ፴") + str(kwargs) + bstack1l1_opy_ (u"ࠦࠧ፵"))
            return {}
        if len(bstack1l1ll1l11l1_opy_) > 1:
            self.logger.debug(bstack1l1_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳࠪࡿࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣ፶") + str(kwargs) + bstack1l1_opy_ (u"ࠨࠢ፷"))
            return {}
        bstack1l1ll111l1l_opy_, bstack1l1ll11lll1_opy_ = bstack1l1ll1l11l1_opy_[0]
        driver = bstack1l1ll111l1l_opy_()
        if not driver:
            self.logger.debug(bstack1l1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤ፸") + str(kwargs) + bstack1l1_opy_ (u"ࠣࠤ፹"))
            return {}
        capabilities = f.bstack1llllll1lll_opy_(bstack1l1ll11lll1_opy_, bstack1lll1l1ll11_opy_.bstack1l1l1ll1lll_opy_)
        if not capabilities:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡦࡰࡷࡱࡨࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤ፺") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦ፻"))
            return {}
        return capabilities.get(bstack1l1_opy_ (u"ࠦࡦࡲࡷࡢࡻࡶࡑࡦࡺࡣࡩࠤ፼"), {})
    def bstack1ll1l111lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs
    ):
        bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1ll111l1111_opy_() and len(bstack1l1ll1l11l1_opy_) == 0:
            bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1l1l1l11l_opy_, [])
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣ፽") + str(kwargs) + bstack1l1_opy_ (u"ࠨࠢ፾"))
            return
        if len(bstack1l1ll1l11l1_opy_) > 1:
            self.logger.debug(bstack1l1_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥ፿") + str(kwargs) + bstack1l1_opy_ (u"ࠣࠤᎀ"))
        bstack1l1ll111l1l_opy_, bstack1l1ll11lll1_opy_ = bstack1l1ll1l11l1_opy_[0]
        driver = bstack1l1ll111l1l_opy_()
        if not driver:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᎁ") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦᎂ"))
            return
        return driver