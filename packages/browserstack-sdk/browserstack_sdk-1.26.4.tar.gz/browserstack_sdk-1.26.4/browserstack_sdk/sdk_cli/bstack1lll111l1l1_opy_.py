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
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import bstack1llllllllll_opy_, bstack11111l11l1_opy_, bstack1llllll1lll_opy_
from browserstack_sdk.sdk_cli.bstack1llll1lll1l_opy_ import bstack1ll1llllll1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1llll1ll_opy_ import bstack1lll1llllll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1111l1l_opy_, bstack1lll1l11lll_opy_, bstack1lllll1l1ll_opy_, bstack1lll1l1ll1l_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1llllllll_opy_, bstack1ll111l1111_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1ll1111l1ll_opy_ = [bstack1ll_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᇒ"), bstack1ll_opy_ (u"ࠨࡰࡢࡴࡨࡲࡹࠨᇓ"), bstack1ll_opy_ (u"ࠢࡤࡱࡱࡪ࡮࡭ࠢᇔ"), bstack1ll_opy_ (u"ࠣࡵࡨࡷࡸ࡯࡯࡯ࠤᇕ"), bstack1ll_opy_ (u"ࠤࡳࡥࡹ࡮ࠢᇖ")]
bstack1l1ll1llll1_opy_ = bstack1ll111l1111_opy_()
bstack1l1ll1ll11l_opy_ = bstack1ll_opy_ (u"࡙ࠥࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠯ࠥᇗ")
bstack1l1lll1lll1_opy_ = {
    bstack1ll_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡵࡿࡴࡩࡱࡱ࠲ࡎࡺࡥ࡮ࠤᇘ"): bstack1ll1111l1ll_opy_,
    bstack1ll_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡖࡡࡤ࡭ࡤ࡫ࡪࠨᇙ"): bstack1ll1111l1ll_opy_,
    bstack1ll_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡍࡰࡦࡸࡰࡪࠨᇚ"): bstack1ll1111l1ll_opy_,
    bstack1ll_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡄ࡮ࡤࡷࡸࠨᇛ"): bstack1ll1111l1ll_opy_,
    bstack1ll_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯ࡲࡼࡸ࡭ࡵ࡮࠯ࡈࡸࡲࡨࡺࡩࡰࡰࠥᇜ"): bstack1ll1111l1ll_opy_
    + [
        bstack1ll_opy_ (u"ࠤࡲࡶ࡮࡭ࡩ࡯ࡣ࡯ࡲࡦࡳࡥࠣᇝ"),
        bstack1ll_opy_ (u"ࠥ࡯ࡪࡿࡷࡰࡴࡧࡷࠧᇞ"),
        bstack1ll_opy_ (u"ࠦ࡫࡯ࡸࡵࡷࡵࡩ࡮ࡴࡦࡰࠤᇟ"),
        bstack1ll_opy_ (u"ࠧࡱࡥࡺࡹࡲࡶࡩࡹࠢᇠ"),
        bstack1ll_opy_ (u"ࠨࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠣᇡ"),
        bstack1ll_opy_ (u"ࠢࡤࡣ࡯ࡰࡴࡨࡪࠣᇢ"),
        bstack1ll_opy_ (u"ࠣࡵࡷࡥࡷࡺࠢᇣ"),
        bstack1ll_opy_ (u"ࠤࡶࡸࡴࡶࠢᇤ"),
        bstack1ll_opy_ (u"ࠥࡨࡺࡸࡡࡵ࡫ࡲࡲࠧᇥ"),
        bstack1ll_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤᇦ"),
    ],
    bstack1ll_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡳࡡࡪࡰ࠱ࡗࡪࡹࡳࡪࡱࡱࠦᇧ"): [bstack1ll_opy_ (u"ࠨࡳࡵࡣࡵࡸࡵࡧࡴࡩࠤᇨ"), bstack1ll_opy_ (u"ࠢࡵࡧࡶࡸࡸ࡬ࡡࡪ࡮ࡨࡨࠧᇩ"), bstack1ll_opy_ (u"ࠣࡶࡨࡷࡹࡹࡣࡰ࡮࡯ࡩࡨࡺࡥࡥࠤᇪ"), bstack1ll_opy_ (u"ࠤ࡬ࡸࡪࡳࡳࠣᇫ")],
    bstack1ll_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡧࡴࡴࡦࡪࡩ࠱ࡇࡴࡴࡦࡪࡩࠥᇬ"): [bstack1ll_opy_ (u"ࠦ࡮ࡴࡶࡰࡥࡤࡸ࡮ࡵ࡮ࡠࡲࡤࡶࡦࡳࡳࠣᇭ"), bstack1ll_opy_ (u"ࠧࡧࡲࡨࡵࠥᇮ")],
    bstack1ll_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡦࡪࡺࡷࡹࡷ࡫ࡳ࠯ࡈ࡬ࡼࡹࡻࡲࡦࡆࡨࡪࠧᇯ"): [bstack1ll_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᇰ"), bstack1ll_opy_ (u"ࠣࡣࡵ࡫ࡳࡧ࡭ࡦࠤᇱ"), bstack1ll_opy_ (u"ࠤࡩࡹࡳࡩࠢᇲ"), bstack1ll_opy_ (u"ࠥࡴࡦࡸࡡ࡮ࡵࠥᇳ"), bstack1ll_opy_ (u"ࠦࡺࡴࡩࡵࡶࡨࡷࡹࠨᇴ"), bstack1ll_opy_ (u"ࠧ࡯ࡤࡴࠤᇵ")],
    bstack1ll_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡦࡪࡺࡷࡹࡷ࡫ࡳ࠯ࡕࡸࡦࡗ࡫ࡱࡶࡧࡶࡸࠧᇶ"): [bstack1ll_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᇷ"), bstack1ll_opy_ (u"ࠣࡲࡤࡶࡦࡳࠢᇸ"), bstack1ll_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡠ࡫ࡱࡨࡪࡾࠢᇹ")],
    bstack1ll_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡶࡺࡴ࡮ࡦࡴ࠱ࡇࡦࡲ࡬ࡊࡰࡩࡳࠧᇺ"): [bstack1ll_opy_ (u"ࠦࡼ࡮ࡥ࡯ࠤᇻ"), bstack1ll_opy_ (u"ࠧࡸࡥࡴࡷ࡯ࡸࠧᇼ")],
    bstack1ll_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴࡭ࡢࡴ࡮࠲ࡸࡺࡲࡶࡥࡷࡹࡷ࡫ࡳ࠯ࡐࡲࡨࡪࡑࡥࡺࡹࡲࡶࡩࡹࠢᇽ"): [bstack1ll_opy_ (u"ࠢ࡯ࡱࡧࡩࠧᇾ"), bstack1ll_opy_ (u"ࠣࡲࡤࡶࡪࡴࡴࠣᇿ")],
    bstack1ll_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡰࡥࡷࡱ࠮ࡴࡶࡵࡹࡨࡺࡵࡳࡧࡶ࠲ࡒࡧࡲ࡬ࠤሀ"): [bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣሁ"), bstack1ll_opy_ (u"ࠦࡦࡸࡧࡴࠤሂ"), bstack1ll_opy_ (u"ࠧࡱࡷࡢࡴࡪࡷࠧሃ")],
}
_1l1lll1llll_opy_ = set()
class bstack1lll11l11l1_opy_(bstack1ll1llllll1_opy_):
    bstack1l1llll11l1_opy_ = bstack1ll_opy_ (u"ࠨࡴࡦࡵࡷࡣࡩ࡫ࡦࡦࡴࡵࡩࡩࠨሄ")
    bstack1ll1111l111_opy_ = bstack1ll_opy_ (u"ࠢࡊࡐࡉࡓࠧህ")
    bstack1ll11111ll1_opy_ = bstack1ll_opy_ (u"ࠣࡇࡕࡖࡔࡘࠢሆ")
    bstack1l1ll1l1l11_opy_: Callable
    bstack1l1lllll11l_opy_: Callable
    def __init__(self, bstack1ll1ll1lll1_opy_, bstack1lll1l1l11l_opy_):
        super().__init__()
        self.bstack1ll1l111lll_opy_ = bstack1lll1l1l11l_opy_
        if os.getenv(bstack1ll_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡑ࠴࠵࡞ࠨሇ"), bstack1ll_opy_ (u"ࠥ࠵ࠧለ")) != bstack1ll_opy_ (u"ࠦ࠶ࠨሉ") or not self.is_enabled():
            self.logger.warning(bstack1ll_opy_ (u"ࠧࠨሊ") + str(self.__class__.__name__) + bstack1ll_opy_ (u"ࠨࠠࡥ࡫ࡶࡥࡧࡲࡥࡥࠤላ"))
            return
        TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.PRE), self.bstack1ll1ll111l1_opy_)
        TestFramework.bstack1ll1l1l1ll1_opy_((bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.POST), self.bstack1ll11llllll_opy_)
        for event in bstack1lll1111l1l_opy_:
            for state in bstack1lllll1l1ll_opy_:
                TestFramework.bstack1ll1l1l1ll1_opy_((event, state), self.bstack1l1lllll1ll_opy_)
        bstack1ll1ll1lll1_opy_.bstack1ll1l1l1ll1_opy_((bstack11111l11l1_opy_.bstack1111111ll1_opy_, bstack1llllll1lll_opy_.POST), self.bstack1l1lll1l11l_opy_)
        self.bstack1l1ll1l1l11_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1llll1lll_opy_(bstack1lll11l11l1_opy_.bstack1ll1111l111_opy_, self.bstack1l1ll1l1l11_opy_)
        self.bstack1l1lllll11l_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1llll1lll_opy_(bstack1lll11l11l1_opy_.bstack1ll11111ll1_opy_, self.bstack1l1lllll11l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1lllll1ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1lll11ll1_opy_() and instance:
            bstack1l1lllll1l1_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack111111ll1l_opy_
            if test_framework_state == bstack1lll1111l1l_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1lll1111l1l_opy_.LOG:
                bstack1lll1ll11_opy_ = datetime.now()
                entries = f.bstack1l1ll1l1111_opy_(instance, bstack111111ll1l_opy_)
                if entries:
                    self.bstack1l1llllll11_opy_(instance, entries)
                    instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡹࡥ࡯ࡦࡢࡰࡴ࡭࡟ࡤࡴࡨࡥࡹ࡫ࡤࡠࡧࡹࡩࡳࡺࠢሌ"), datetime.now() - bstack1lll1ll11_opy_)
                    f.bstack1l1ll1l1lll_opy_(instance, bstack111111ll1l_opy_)
                instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠣࡱ࠴࠵ࡾࡀ࡯࡯ࡡࡤࡰࡱࡥࡴࡦࡵࡷࡣࡪࡼࡥ࡯ࡶࡶࠦል"), datetime.now() - bstack1l1lllll1l1_opy_)
                return # bstack1l1ll1lll11_opy_ not send this event with the bstack1ll1111lll1_opy_ bstack1ll1111ll11_opy_
            elif (
                test_framework_state == bstack1lll1111l1l_opy_.TEST
                and test_hook_state == bstack1lllll1l1ll_opy_.POST
                and not f.bstack11111l1ll1_opy_(instance, TestFramework.bstack1ll11111111_opy_)
            ):
                self.logger.warning(bstack1ll_opy_ (u"ࠤࡧࡶࡴࡶࡰࡪࡰࡪࠤࡩࡻࡥࠡࡶࡲࠤࡱࡧࡣ࡬ࠢࡲࡪࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࠢሎ") + str(TestFramework.bstack11111l1ll1_opy_(instance, TestFramework.bstack1ll11111111_opy_)) + bstack1ll_opy_ (u"ࠥࠦሏ"))
                f.bstack111111l1l1_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1llll11l1_opy_, True)
                return # bstack1l1ll1lll11_opy_ not send this event bstack1l1ll1ll1l1_opy_ bstack1ll111l11l1_opy_
            elif (
                f.bstack1111111lll_opy_(instance, bstack1lll11l11l1_opy_.bstack1l1llll11l1_opy_, False)
                and test_framework_state == bstack1lll1111l1l_opy_.LOG_REPORT
                and test_hook_state == bstack1lllll1l1ll_opy_.POST
                and f.bstack11111l1ll1_opy_(instance, TestFramework.bstack1ll11111111_opy_)
            ):
                self.logger.warning(bstack1ll_opy_ (u"ࠦ࡮ࡴࡪࡦࡥࡷ࡭ࡳ࡭ࠠࡕࡧࡶࡸࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࡓࡵࡣࡷࡩ࠳࡚ࡅࡔࡖ࠯ࠤ࡙࡫ࡳࡵࡊࡲࡳࡰ࡙ࡴࡢࡶࡨ࠲ࡕࡕࡓࡕࠢࠥሐ") + str(TestFramework.bstack11111l1ll1_opy_(instance, TestFramework.bstack1ll11111111_opy_)) + bstack1ll_opy_ (u"ࠧࠨሑ"))
                self.bstack1l1lllll1ll_opy_(f, instance, (bstack1lll1111l1l_opy_.TEST, bstack1lllll1l1ll_opy_.POST), *args, **kwargs)
            bstack1lll1ll11_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1llll111l_opy_ = sorted(
                filter(lambda x: x.get(bstack1ll_opy_ (u"ࠨࡥࡷࡧࡱࡸࡤࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠤሒ"), None), data.pop(bstack1ll_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢሓ"), {}).values()),
                key=lambda x: x[bstack1ll_opy_ (u"ࠣࡧࡹࡩࡳࡺ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠦሔ")],
            )
            if bstack1lll1llllll_opy_.bstack1l1lll1ll1l_opy_ in data:
                data.pop(bstack1lll1llllll_opy_.bstack1l1lll1ll1l_opy_)
            data.update({bstack1ll_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠤሕ"): bstack1l1llll111l_opy_})
            instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠥ࡮ࡸࡵ࡮࠻ࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣሖ"), datetime.now() - bstack1lll1ll11_opy_)
            bstack1lll1ll11_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1ll1ll111_opy_)
            instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠦ࡯ࡹ࡯࡯࠼ࡲࡲࡤࡧ࡬࡭ࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡹࠢሗ"), datetime.now() - bstack1lll1ll11_opy_)
            self.bstack1ll1111ll11_opy_(instance, bstack111111ll1l_opy_, event_json=event_json)
            instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠧࡵ࠱࠲ࡻ࠽ࡳࡳࡥࡡ࡭࡮ࡢࡸࡪࡹࡴࡠࡧࡹࡩࡳࡺࡳࠣመ"), datetime.now() - bstack1l1lllll1l1_opy_)
    def bstack1ll1ll111l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1ll1lll1l_opy_ import bstack1lll11l1lll_opy_
        bstack1ll11lll1ll_opy_ = bstack1lll11l1lll_opy_.bstack1ll1ll11111_opy_(EVENTS.bstack11l11lll1_opy_.value)
        self.bstack1ll1l111lll_opy_.bstack1l1llll1l11_opy_(instance, f, bstack111111ll1l_opy_, *args, **kwargs)
        bstack1lll11l1lll_opy_.end(EVENTS.bstack11l11lll1_opy_.value, bstack1ll11lll1ll_opy_ + bstack1ll_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨሙ"), bstack1ll11lll1ll_opy_ + bstack1ll_opy_ (u"ࠢ࠻ࡧࡱࡨࠧሚ"), status=True, failure=None, test_name=None)
    def bstack1ll11llllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        *args,
        **kwargs,
    ):
        req = self.bstack1ll1l111lll_opy_.bstack1ll1111llll_opy_(instance, f, bstack111111ll1l_opy_, *args, **kwargs)
        self.bstack1l1lll1ll11_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1lll1111l_opy_, stage=STAGE.bstack1llll11lll_opy_)
    def bstack1l1lll1ll11_opy_(
        self,
        f: TestFramework,
        instance: bstack1lll1l11lll_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack1ll_opy_ (u"ࠣࡕ࡮࡭ࡵࡶࡩ࡯ࡩࠣࡘࡪࡹࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡆࡸࡨࡲࡹࠦࡧࡓࡒࡆࠤࡨࡧ࡬࡭࠼ࠣࡒࡴࠦࡶࡢ࡮࡬ࡨࠥࡸࡥࡲࡷࡨࡷࡹࠦࡤࡢࡶࡤࠦማ"))
            return
        bstack1lll1ll11_opy_ = datetime.now()
        try:
            r = self.bstack1ll1lll1ll1_opy_.TestSessionEvent(req)
            instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡺࡥࡴࡶࡢࡷࡪࡹࡳࡪࡱࡱࡣࡪࡼࡥ࡯ࡶࠥሜ"), datetime.now() - bstack1lll1ll11_opy_)
            f.bstack111111l1l1_opy_(instance, self.bstack1ll1l111lll_opy_.bstack1l1llll1l1l_opy_, r.success)
            if not r.success:
                self.logger.info(bstack1ll_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࠧም") + str(r) + bstack1ll_opy_ (u"ࠦࠧሞ"))
        except grpc.RpcError as e:
            self.logger.error(bstack1ll_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥሟ") + str(e) + bstack1ll_opy_ (u"ࠨࠢሠ"))
            traceback.print_exc()
            raise e
    def bstack1l1lll1l11l_opy_(
        self,
        f: bstack1lll111l11l_opy_,
        _driver: object,
        exec: Tuple[bstack1llllllllll_opy_, str],
        _1l1lll111ll_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1lll111l11l_opy_.bstack1ll1l11l1ll_opy_(method_name):
            return
        if f.bstack1ll11llll11_opy_(*args) == bstack1lll111l11l_opy_.bstack1l1ll1l1l1l_opy_:
            bstack1l1lllll1l1_opy_ = datetime.now()
            screenshot = result.get(bstack1ll_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨሡ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack1ll_opy_ (u"ࠣ࡫ࡱࡺࡦࡲࡩࡥࠢࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠦࡩ࡮ࡣࡪࡩࠥࡨࡡࡴࡧ࠹࠸ࠥࡹࡴࡳࠤሢ"))
                return
            bstack1l1lllllll1_opy_ = self.bstack1l1lll1l1l1_opy_(instance)
            if bstack1l1lllllll1_opy_:
                entry = bstack1lll1l1ll1l_opy_(TestFramework.bstack1l1ll1l11ll_opy_, screenshot)
                self.bstack1l1llllll11_opy_(bstack1l1lllllll1_opy_, [entry])
                instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠤࡲ࠵࠶ࡿ࠺ࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡨࡼࡪࡩࡵࡵࡧࠥሣ"), datetime.now() - bstack1l1lllll1l1_opy_)
            else:
                self.logger.warning(bstack1ll_opy_ (u"ࠥࡹࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡷࡩࡸࡺࠠࡧࡱࡵࠤࡼ࡮ࡩࡤࡪࠣࡸ࡭࡯ࡳࠡࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠥࡽࡡࡴࠢࡷࡥࡰ࡫࡮ࠡࡤࡼࠤࡩࡸࡩࡷࡧࡵࡁࠥࢁࡽࠣሤ").format(instance.ref()))
        event = {}
        bstack1l1lllllll1_opy_ = self.bstack1l1lll1l1l1_opy_(instance)
        if bstack1l1lllllll1_opy_:
            self.bstack1l1lll11111_opy_(event, bstack1l1lllllll1_opy_)
            if event.get(bstack1ll_opy_ (u"ࠦࡱࡵࡧࡴࠤሥ")):
                self.bstack1l1llllll11_opy_(bstack1l1lllllll1_opy_, event[bstack1ll_opy_ (u"ࠧࡲ࡯ࡨࡵࠥሦ")])
            else:
                self.logger.debug(bstack1ll_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥࡲ࡯ࡨࡵࠣࡪࡴࡸࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡪࡼࡥ࡯ࡶࠥሧ"))
    @measure(event_name=EVENTS.bstack1ll1111l1l1_opy_, stage=STAGE.bstack1llll11lll_opy_)
    def bstack1l1llllll11_opy_(
        self,
        bstack1l1lllllll1_opy_: bstack1lll1l11lll_opy_,
        entries: List[bstack1lll1l1ll1l_opy_],
    ):
        self.bstack1ll1l1l1lll_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1111111lll_opy_(bstack1l1lllllll1_opy_, TestFramework.bstack1ll1l1l111l_opy_)
        req.execution_context.hash = str(bstack1l1lllllll1_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1lllllll1_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1lllllll1_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1111111lll_opy_(bstack1l1lllllll1_opy_, TestFramework.bstack1ll1l1lll11_opy_)
            log_entry.test_framework_version = TestFramework.bstack1111111lll_opy_(bstack1l1lllllll1_opy_, TestFramework.bstack1ll1111l11l_opy_)
            log_entry.uuid = TestFramework.bstack1111111lll_opy_(bstack1l1lllllll1_opy_, TestFramework.bstack1ll1l11111l_opy_)
            log_entry.test_framework_state = bstack1l1lllllll1_opy_.state.name
            log_entry.message = entry.message.encode(bstack1ll_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨረ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1ll_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥሩ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll1l111l_opy_
                log_entry.file_path = entry.bstack1ll1111_opy_
        def bstack1l1ll1ll1ll_opy_():
            bstack1lll1ll11_opy_ = datetime.now()
            try:
                self.bstack1ll1lll1ll1_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1ll1l11ll_opy_:
                    bstack1l1lllllll1_opy_.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࠨሪ"), datetime.now() - bstack1lll1ll11_opy_)
                elif entry.kind == TestFramework.bstack1l1lll1l1ll_opy_:
                    bstack1l1lllllll1_opy_.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠢራ"), datetime.now() - bstack1lll1ll11_opy_)
                else:
                    bstack1l1lllllll1_opy_.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡱࡵࡧࠣሬ"), datetime.now() - bstack1lll1ll11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1ll_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥር") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1111l111ll_opy_.enqueue(bstack1l1ll1ll1ll_opy_)
    @measure(event_name=EVENTS.bstack1ll1111111l_opy_, stage=STAGE.bstack1llll11lll_opy_)
    def bstack1ll1111ll11_opy_(
        self,
        instance: bstack1lll1l11lll_opy_,
        bstack111111ll1l_opy_: Tuple[bstack1lll1111l1l_opy_, bstack1lllll1l1ll_opy_],
        event_json=None,
    ):
        self.bstack1ll1l1l1lll_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l1l111l_opy_)
        req.test_framework_name = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l1lll11_opy_)
        req.test_framework_version = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1111l11l_opy_)
        req.test_framework_state = bstack111111ll1l_opy_[0].name
        req.test_hook_state = bstack111111ll1l_opy_[1].name
        started_at = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1l1llll1111_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll11111l1l_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1ll1ll111_opy_)).encode(bstack1ll_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧሮ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1ll1ll1ll_opy_():
            bstack1lll1ll11_opy_ = datetime.now()
            try:
                self.bstack1ll1lll1ll1_opy_.TestFrameworkEvent(req)
                instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡹࡥ࡯ࡦࡢࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡪࡼࡥ࡯ࡶࠥሯ"), datetime.now() - bstack1lll1ll11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1ll_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨሰ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1111l111ll_opy_.enqueue(bstack1l1ll1ll1ll_opy_)
    def bstack1l1lll1l1l1_opy_(self, instance: bstack1llllllllll_opy_):
        bstack1l1llllll1l_opy_ = TestFramework.bstack1lllllll1ll_opy_(instance.context)
        for t in bstack1l1llllll1l_opy_:
            bstack1ll111111ll_opy_ = TestFramework.bstack1111111lll_opy_(t, bstack1lll1llllll_opy_.bstack1l1lll1ll1l_opy_, [])
            if any(instance is d[1] for d in bstack1ll111111ll_opy_):
                return t
    def bstack1l1lll1l111_opy_(self, message):
        self.bstack1l1ll1l1l11_opy_(message + bstack1ll_opy_ (u"ࠤ࡟ࡲࠧሱ"))
    def log_error(self, message):
        self.bstack1l1lllll11l_opy_(message + bstack1ll_opy_ (u"ࠥࡠࡳࠨሲ"))
    def bstack1l1llll1lll_opy_(self, level, original_func):
        def bstack1ll11111lll_opy_(*args):
            return_value = original_func(*args)
            if not args or not isinstance(args[0], str) or not args[0].strip():
                return return_value
            message = args[0].strip()
            bstack1l1llllll1l_opy_ = TestFramework.bstack1ll11111l11_opy_()
            if not bstack1l1llllll1l_opy_:
                return return_value
            bstack1l1lllllll1_opy_ = next(
                (
                    instance
                    for instance in bstack1l1llllll1l_opy_
                    if TestFramework.bstack11111l1ll1_opy_(instance, TestFramework.bstack1ll1l11111l_opy_)
                ),
                None,
            )
            if not bstack1l1lllllll1_opy_:
                return
            entry = bstack1lll1l1ll1l_opy_(TestFramework.bstack1l1ll1lll1l_opy_, message, level)
            self.bstack1l1llllll11_opy_(bstack1l1lllllll1_opy_, [entry])
            return return_value
        return bstack1ll11111lll_opy_
    def bstack1l1lll11111_opy_(self, event: dict, instance=None) -> None:
        global _1l1lll1llll_opy_
        levels = [bstack1ll_opy_ (u"࡙ࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢሳ"), bstack1ll_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤሴ")]
        bstack1l1ll1l1ll1_opy_ = bstack1ll_opy_ (u"ࠨࠢስ")
        if instance is not None:
            try:
                bstack1l1ll1l1ll1_opy_ = TestFramework.bstack1111111lll_opy_(instance, TestFramework.bstack1ll1l11111l_opy_)
            except Exception as e:
                self.logger.warning(bstack1ll_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡷ࡬ࡨࠥ࡬ࡲࡰ࡯ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠧሶ").format(e))
        bstack1l1lll11lll_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨሷ")]
                bstack1l1ll1l11l1_opy_ = os.path.join(bstack1l1ll1llll1_opy_, (bstack1l1ll1ll11l_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1ll1l11l1_opy_):
                    self.logger.debug(bstack1ll_opy_ (u"ࠤࡇ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡴ࡯ࡵࠢࡳࡶࡪࡹࡥ࡯ࡶࠣࡪࡴࡸࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤ࡙࡫ࡳࡵࠢࡤࡲࡩࠦࡂࡶ࡫࡯ࡨࠥࡲࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡾࢁࠧሸ").format(bstack1l1ll1l11l1_opy_))
                    continue
                file_names = os.listdir(bstack1l1ll1l11l1_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1ll1l11l1_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1lll1llll_opy_:
                        self.logger.info(bstack1ll_opy_ (u"ࠥࡔࡦࡺࡨࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡳࡶࡴࡩࡥࡴࡵࡨࡨࠥࢁࡽࠣሹ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1ll1111ll1l_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1ll1111ll1l_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack1ll_opy_ (u"࡙ࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢሺ"):
                                entry = bstack1lll1l1ll1l_opy_(
                                    kind=bstack1ll_opy_ (u"࡚ࠧࡅࡔࡖࡢࡅ࡙࡚ࡁࡄࡊࡐࡉࡓ࡚ࠢሻ"),
                                    message=bstack1ll_opy_ (u"ࠨࠢሼ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll1l111l_opy_=file_size,
                                    bstack1l1llll11ll_opy_=bstack1ll_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢሽ"),
                                    bstack1ll1111_opy_=os.path.abspath(file_path),
                                    bstack1l1l1ll111_opy_=bstack1l1ll1l1ll1_opy_
                                )
                            elif level == bstack1ll_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧሾ"):
                                entry = bstack1lll1l1ll1l_opy_(
                                    kind=bstack1ll_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦሿ"),
                                    message=bstack1ll_opy_ (u"ࠥࠦቀ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1ll1l111l_opy_=file_size,
                                    bstack1l1llll11ll_opy_=bstack1ll_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦቁ"),
                                    bstack1ll1111_opy_=os.path.abspath(file_path),
                                    bstack1l1lllll111_opy_=bstack1l1ll1l1ll1_opy_
                                )
                            bstack1l1lll11lll_opy_.append(entry)
                            _1l1lll1llll_opy_.add(abs_path)
                        except Exception as bstack1ll111111l1_opy_:
                            self.logger.error(bstack1ll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡴࡤ࡭ࡸ࡫ࡤࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡽࢀࠦቂ").format(bstack1ll111111l1_opy_))
        except Exception as e:
            self.logger.error(bstack1ll_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡵࡥ࡮ࡹࡥࡥࠢࡺ࡬ࡪࡴࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡾࢁࠧቃ").format(e))
        event[bstack1ll_opy_ (u"ࠢ࡭ࡱࡪࡷࠧቄ")] = bstack1l1lll11lll_opy_
class bstack1l1ll1ll111_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1ll1lllll_opy_ = set()
        kwargs[bstack1ll_opy_ (u"ࠣࡵ࡮࡭ࡵࡱࡥࡺࡵࠥቅ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1lll11l11_opy_(obj, self.bstack1l1ll1lllll_opy_)
def bstack1l1lll111l1_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1lll11l11_opy_(obj, bstack1l1ll1lllll_opy_=None, max_depth=3):
    if bstack1l1ll1lllll_opy_ is None:
        bstack1l1ll1lllll_opy_ = set()
    if id(obj) in bstack1l1ll1lllll_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1ll1lllll_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1lll11l1l_opy_ = TestFramework.bstack1ll111l111l_opy_(obj)
    bstack1l1llll1ll1_opy_ = next((k.lower() in bstack1l1lll11l1l_opy_.lower() for k in bstack1l1lll1lll1_opy_.keys()), None)
    if bstack1l1llll1ll1_opy_:
        obj = TestFramework.bstack1ll111l11ll_opy_(obj, bstack1l1lll1lll1_opy_[bstack1l1llll1ll1_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack1ll_opy_ (u"ࠤࡢࡣࡸࡲ࡯ࡵࡵࡢࡣࠧቆ")):
            keys = getattr(obj, bstack1ll_opy_ (u"ࠥࡣࡤࡹ࡬ࡰࡶࡶࡣࡤࠨቇ"), [])
        elif hasattr(obj, bstack1ll_opy_ (u"ࠦࡤࡥࡤࡪࡥࡷࡣࡤࠨቈ")):
            keys = getattr(obj, bstack1ll_opy_ (u"ࠧࡥ࡟ࡥ࡫ࡦࡸࡤࡥࠢ቉"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack1ll_opy_ (u"ࠨ࡟ࠣቊ"))}
        if not obj and bstack1l1lll11l1l_opy_ == bstack1ll_opy_ (u"ࠢࡱࡣࡷ࡬ࡱ࡯ࡢ࠯ࡒࡲࡷ࡮ࡾࡐࡢࡶ࡫ࠦቋ"):
            obj = {bstack1ll_opy_ (u"ࠣࡲࡤࡸ࡭ࠨቌ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1lll111l1_opy_(key) or str(key).startswith(bstack1ll_opy_ (u"ࠤࡢࠦቍ")):
            continue
        if value is not None and bstack1l1lll111l1_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1lll11l11_opy_(value, bstack1l1ll1lllll_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1lll11l11_opy_(o, bstack1l1ll1lllll_opy_, max_depth) for o in value]))
    return result or None