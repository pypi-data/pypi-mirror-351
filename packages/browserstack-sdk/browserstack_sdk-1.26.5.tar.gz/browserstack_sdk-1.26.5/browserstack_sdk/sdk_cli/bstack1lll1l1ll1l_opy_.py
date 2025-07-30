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
from typing import Dict, List, Any, Callable, Tuple, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1lll1lll111_opy_
from browserstack_sdk.sdk_cli.bstack1111111l11_opy_ import (
    bstack11111l11ll_opy_,
    bstack111111ll1l_opy_,
    bstack11111l1l1l_opy_,
)
from bstack_utils.helper import  bstack1l11l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1l11_opy_ import bstack1lll1l1ll11_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1ll1ll_opy_, bstack1lll111l1ll_opy_, bstack1lllll1111l_opy_, bstack1lllll1l11l_opy_
from typing import Tuple, Any
import threading
from bstack_utils.bstack1llll1ll1_opy_ import bstack1l11ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1ll1llll11l_opy_ import bstack1lll1llllll_opy_
from bstack_utils.percy import bstack11lll1l1_opy_
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.constants import *
import re
class bstack1llll1l1lll_opy_(bstack1lll1lll111_opy_):
    def __init__(self, bstack1l1ll11llll_opy_: Dict[str, str]):
        super().__init__()
        self.bstack1l1ll11llll_opy_ = bstack1l1ll11llll_opy_
        self.percy = bstack11lll1l1_opy_()
        self.bstack11l11l111_opy_ = bstack1l11ll1l_opy_()
        self.bstack1l1ll11l1l1_opy_()
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.bstack1llllll1111_opy_, bstack111111ll1l_opy_.PRE), self.bstack1l1ll11ll1l_opy_)
        TestFramework.bstack1ll11ll1l1l_opy_((bstack1llll1ll1ll_opy_.TEST, bstack1lllll1111l_opy_.POST), self.bstack1ll1l11lll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll1111llll_opy_(self, instance: bstack11111l1l1l_opy_, driver: object):
        bstack1l1ll1ll111_opy_ = TestFramework.bstack11111ll11l_opy_(instance.context)
        for t in bstack1l1ll1ll111_opy_:
            bstack1l1ll1l11l1_opy_ = TestFramework.bstack1llllll1lll_opy_(t, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
            if any(instance is d[1] for d in bstack1l1ll1l11l1_opy_) or instance == driver:
                return t
    def bstack1l1ll11ll1l_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if not bstack1lll1l1ll11_opy_.bstack1ll1l1l1l11_opy_(method_name):
                return
            platform_index = f.bstack1llllll1lll_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_, 0)
            bstack1ll111l111l_opy_ = self.bstack1ll1111llll_opy_(instance, driver)
            bstack1l1ll1111ll_opy_ = TestFramework.bstack1llllll1lll_opy_(bstack1ll111l111l_opy_, TestFramework.bstack1l1ll111lll_opy_, None)
            if not bstack1l1ll1111ll_opy_:
                self.logger.debug(bstack1l1_opy_ (u"ࠥࡳࡳࡥࡰࡳࡧࡢࡩࡽ࡫ࡣࡶࡶࡨ࠾ࠥࡸࡥࡵࡷࡵࡲ࡮ࡴࡧࠡࡣࡶࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥ࡯ࡳࠡࡰࡲࡸࠥࡿࡥࡵࠢࡶࡸࡦࡸࡴࡦࡦࠥ቎"))
                return
            driver_command = f.bstack1ll1l111l1l_opy_(*args)
            for command in bstack1l1ll1ll11_opy_:
                if command == driver_command:
                    self.bstack1lll1llll1_opy_(driver, platform_index)
            bstack1ll1ll11_opy_ = self.percy.bstack11ll1l1lll_opy_()
            if driver_command in bstack1l1111lll_opy_[bstack1ll1ll11_opy_]:
                self.bstack11l11l111_opy_.bstack1llll1lll1_opy_(bstack1l1ll1111ll_opy_, driver_command)
        except Exception as e:
            self.logger.error(bstack1l1_opy_ (u"ࠦࡴࡴ࡟ࡱࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩ࠿ࠦࡥࡳࡴࡲࡶࠧ቏"), e)
    def bstack1ll1l11lll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack11l11l111l_opy_ import bstack1ll1llll111_opy_
        bstack1l1ll1l11l1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1llllll_opy_.bstack1l1ll1lll11_opy_, [])
        if not bstack1l1ll1l11l1_opy_:
            self.logger.debug(bstack1l1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡮ࡰࠢࡧࡶ࡮ࡼࡥࡳࡵࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢቐ") + str(kwargs) + bstack1l1_opy_ (u"ࠨࠢቑ"))
            return
        if len(bstack1l1ll1l11l1_opy_) > 1:
            self.logger.debug(bstack1l1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡽ࡯ࡩࡳ࠮ࡤࡳ࡫ࡹࡩࡷࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡴࠫࢀࠤࡩࡸࡩࡷࡧࡵࡷࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤቒ") + str(kwargs) + bstack1l1_opy_ (u"ࠣࠤቓ"))
        bstack1l1ll111l1l_opy_, bstack1l1ll11lll1_opy_ = bstack1l1ll1l11l1_opy_[0]
        driver = bstack1l1ll111l1l_opy_()
        if not driver:
            self.logger.debug(bstack1l1_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡤࡳ࡫ࡹࡩࡷࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥቔ") + str(kwargs) + bstack1l1_opy_ (u"ࠥࠦቕ"))
            return
        bstack1l1ll11l1ll_opy_ = {
            TestFramework.bstack1ll1l1l1111_opy_: bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢቖ"),
            TestFramework.bstack1ll1l11l11l_opy_: bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࠣࡹࡺ࡯ࡤࠣ቗"),
            TestFramework.bstack1l1ll111lll_opy_: bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࠤࡷ࡫ࡲࡶࡰࠣࡲࡦࡳࡥࠣቘ")
        }
        bstack1l1ll111ll1_opy_ = { key: f.bstack1llllll1lll_opy_(instance, key) for key in bstack1l1ll11l1ll_opy_ }
        bstack1l1ll11l111_opy_ = [key for key, value in bstack1l1ll111ll1_opy_.items() if not value]
        if bstack1l1ll11l111_opy_:
            for key in bstack1l1ll11l111_opy_:
                self.logger.debug(bstack1l1_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡ࡯࡬ࡷࡸ࡯࡮ࡨࠢࠥ቙") + str(key) + bstack1l1_opy_ (u"ࠣࠤቚ"))
            return
        platform_index = f.bstack1llllll1lll_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_, 0)
        if self.bstack1l1ll11llll_opy_.percy_capture_mode == bstack1l1_opy_ (u"ࠤࡷࡩࡸࡺࡣࡢࡵࡨࠦቛ"):
            bstack11l1l1l1_opy_ = bstack1l1ll111ll1_opy_.get(TestFramework.bstack1l1ll111lll_opy_) + bstack1l1_opy_ (u"ࠥ࠱ࡹ࡫ࡳࡵࡥࡤࡷࡪࠨቜ")
            bstack1ll11lll111_opy_ = bstack1ll1llll111_opy_.bstack1ll11lll1l1_opy_(EVENTS.bstack1l1ll111l11_opy_.value)
            PercySDK.screenshot(
                driver,
                bstack11l1l1l1_opy_,
                bstack1l111ll11_opy_=bstack1l1ll111ll1_opy_[TestFramework.bstack1ll1l1l1111_opy_],
                bstack1l1l11llll_opy_=bstack1l1ll111ll1_opy_[TestFramework.bstack1ll1l11l11l_opy_],
                bstack1l111111l_opy_=platform_index
            )
            bstack1ll1llll111_opy_.end(EVENTS.bstack1l1ll111l11_opy_.value, bstack1ll11lll111_opy_+bstack1l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦቝ"), bstack1ll11lll111_opy_+bstack1l1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥ቞"), True, None, None, None, None, test_name=bstack11l1l1l1_opy_)
    def bstack1lll1llll1_opy_(self, driver, platform_index):
        if self.bstack11l11l111_opy_.bstack11lll1lll1_opy_() is True or self.bstack11l11l111_opy_.capturing() is True:
            return
        self.bstack11l11l111_opy_.bstack1l11l11l1_opy_()
        while not self.bstack11l11l111_opy_.bstack11lll1lll1_opy_():
            bstack1l1ll1111ll_opy_ = self.bstack11l11l111_opy_.bstack1ll111l11_opy_()
            self.bstack1l111ll1l_opy_(driver, bstack1l1ll1111ll_opy_, platform_index)
        self.bstack11l11l111_opy_.bstack1l1l11lll_opy_()
    def bstack1l111ll1l_opy_(self, driver, bstack1111ll1l1_opy_, platform_index, test=None):
        from bstack_utils.bstack11l11l111l_opy_ import bstack1ll1llll111_opy_
        bstack1ll11lll111_opy_ = bstack1ll1llll111_opy_.bstack1ll11lll1l1_opy_(EVENTS.bstack1lll1ll1ll_opy_.value)
        if test != None:
            bstack1l111ll11_opy_ = getattr(test, bstack1l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ቟"), None)
            bstack1l1l11llll_opy_ = getattr(test, bstack1l1_opy_ (u"ࠧࡶࡷ࡬ࡨࠬበ"), None)
            PercySDK.screenshot(driver, bstack1111ll1l1_opy_, bstack1l111ll11_opy_=bstack1l111ll11_opy_, bstack1l1l11llll_opy_=bstack1l1l11llll_opy_, bstack1l111111l_opy_=platform_index)
        else:
            PercySDK.screenshot(driver, bstack1111ll1l1_opy_)
        bstack1ll1llll111_opy_.end(EVENTS.bstack1lll1ll1ll_opy_.value, bstack1ll11lll111_opy_+bstack1l1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣቡ"), bstack1ll11lll111_opy_+bstack1l1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢቢ"), True, None, None, None, None, test_name=bstack1111ll1l1_opy_)
    def bstack1l1ll11l1l1_opy_(self):
        os.environ[bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡉࡗࡉ࡙ࠨባ")] = str(self.bstack1l1ll11llll_opy_.success)
        os.environ[bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࡡࡆࡅࡕ࡚ࡕࡓࡇࡢࡑࡔࡊࡅࠨቤ")] = str(self.bstack1l1ll11llll_opy_.percy_capture_mode)
        self.percy.bstack1l1ll11ll11_opy_(self.bstack1l1ll11llll_opy_.is_percy_auto_enabled)
        self.percy.bstack1l1ll11l11l_opy_(self.bstack1l1ll11llll_opy_.percy_build_id)