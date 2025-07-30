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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1111111l11_opy_ import (
    bstack111111111l_opy_,
    bstack11111l1l1l_opy_,
    bstack11111l11ll_opy_,
    bstack111111ll1l_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1llll1ll111_opy_(bstack111111111l_opy_):
    bstack1l11lll11ll_opy_ = bstack1l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦᎃ")
    bstack1l1l1ll11l1_opy_ = bstack1l1_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧᎄ")
    bstack1l1l1llllll_opy_ = bstack1l1_opy_ (u"ࠨࡨࡶࡤࡢࡹࡷࡲࠢᎅ")
    bstack1l1l1ll1lll_opy_ = bstack1l1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᎆ")
    bstack1l11lll1111_opy_ = bstack1l1_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࠦᎇ")
    bstack1l11ll1ll11_opy_ = bstack1l1_opy_ (u"ࠤࡺ࠷ࡨ࡫ࡸࡦࡥࡸࡸࡪࡹࡣࡳ࡫ࡳࡸࡦࡹࡹ࡯ࡥࠥᎈ")
    NAME = bstack1l1_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᎉ")
    bstack1l11lll11l1_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lllll11l11_opy_: Any
    bstack1l11ll1l1ll_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack1l1_opy_ (u"ࠦࡱࡧࡵ࡯ࡥ࡫ࠦᎊ"), bstack1l1_opy_ (u"ࠧࡩ࡯࡯ࡰࡨࡧࡹࠨᎋ"), bstack1l1_opy_ (u"ࠨ࡮ࡦࡹࡢࡴࡦ࡭ࡥࠣᎌ"), bstack1l1_opy_ (u"ࠢࡤ࡮ࡲࡷࡪࠨᎍ"), bstack1l1_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥᎎ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack111111lll1_opy_(methods)
    def bstack1llllllllll_opy_(self, instance: bstack11111l1l1l_opy_, method_name: str, bstack1llllll111l_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1lllllll11l_opy_(
        self,
        target: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack11111l1ll1_opy_, bstack1l11ll1llll_opy_ = bstack1llllll1l1l_opy_
        bstack1l11lll111l_opy_ = bstack1llll1ll111_opy_.bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_)
        if bstack1l11lll111l_opy_ in bstack1llll1ll111_opy_.bstack1l11lll11l1_opy_:
            bstack1l11ll1ll1l_opy_ = None
            for callback in bstack1llll1ll111_opy_.bstack1l11lll11l1_opy_[bstack1l11lll111l_opy_]:
                try:
                    bstack1l11ll1lll1_opy_ = callback(self, target, exec, bstack1llllll1l1l_opy_, result, *args, **kwargs)
                    if bstack1l11ll1ll1l_opy_ == None:
                        bstack1l11ll1ll1l_opy_ = bstack1l11ll1lll1_opy_
                except Exception as e:
                    self.logger.error(bstack1l1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࠢᎏ") + str(e) + bstack1l1_opy_ (u"ࠥࠦ᎐"))
                    traceback.print_exc()
            if bstack1l11ll1llll_opy_ == bstack111111ll1l_opy_.PRE and callable(bstack1l11ll1ll1l_opy_):
                return bstack1l11ll1ll1l_opy_
            elif bstack1l11ll1llll_opy_ == bstack111111ll1l_opy_.POST and bstack1l11ll1ll1l_opy_:
                return bstack1l11ll1ll1l_opy_
    def bstack111111ll11_opy_(
        self, method_name, previous_state: bstack11111l11ll_opy_, *args, **kwargs
    ) -> bstack11111l11ll_opy_:
        if method_name == bstack1l1_opy_ (u"ࠫࡱࡧࡵ࡯ࡥ࡫ࠫ᎑") or method_name == bstack1l1_opy_ (u"ࠬࡩ࡯࡯ࡰࡨࡧࡹ࠭᎒") or method_name == bstack1l1_opy_ (u"࠭࡮ࡦࡹࡢࡴࡦ࡭ࡥࠨ᎓"):
            return bstack11111l11ll_opy_.bstack1llllll11ll_opy_
        if method_name == bstack1l1_opy_ (u"ࠧࡥ࡫ࡶࡴࡦࡺࡣࡩࠩ᎔"):
            return bstack11111l11ll_opy_.bstack11111l1lll_opy_
        if method_name == bstack1l1_opy_ (u"ࠨࡥ࡯ࡳࡸ࡫ࠧ᎕"):
            return bstack11111l11ll_opy_.QUIT
        return bstack11111l11ll_opy_.NONE
    @staticmethod
    def bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_]):
        return bstack1l1_opy_ (u"ࠤ࠽ࠦ᎖").join((bstack11111l11ll_opy_(bstack1llllll1l1l_opy_[0]).name, bstack111111ll1l_opy_(bstack1llllll1l1l_opy_[1]).name))
    @staticmethod
    def bstack1ll11ll1l1l_opy_(bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_], callback: Callable):
        bstack1l11lll111l_opy_ = bstack1llll1ll111_opy_.bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_)
        if not bstack1l11lll111l_opy_ in bstack1llll1ll111_opy_.bstack1l11lll11l1_opy_:
            bstack1llll1ll111_opy_.bstack1l11lll11l1_opy_[bstack1l11lll111l_opy_] = []
        bstack1llll1ll111_opy_.bstack1l11lll11l1_opy_[bstack1l11lll111l_opy_].append(callback)
    @staticmethod
    def bstack1ll1l1l1l11_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll1l1lllll_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll11ll1l11_opy_(instance: bstack11111l1l1l_opy_, default_value=None):
        return bstack111111111l_opy_.bstack1llllll1lll_opy_(instance, bstack1llll1ll111_opy_.bstack1l1l1ll1lll_opy_, default_value)
    @staticmethod
    def bstack1ll111ll1ll_opy_(instance: bstack11111l1l1l_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll1ll1111l_opy_(instance: bstack11111l1l1l_opy_, default_value=None):
        return bstack111111111l_opy_.bstack1llllll1lll_opy_(instance, bstack1llll1ll111_opy_.bstack1l1l1llllll_opy_, default_value)
    @staticmethod
    def bstack1ll1l111l1l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll11llll1l_opy_(method_name: str, *args):
        if not bstack1llll1ll111_opy_.bstack1ll1l1l1l11_opy_(method_name):
            return False
        if not bstack1llll1ll111_opy_.bstack1l11lll1111_opy_ in bstack1llll1ll111_opy_.bstack1l1l11111l1_opy_(*args):
            return False
        bstack1ll11l1l1ll_opy_ = bstack1llll1ll111_opy_.bstack1ll11l1l11l_opy_(*args)
        return bstack1ll11l1l1ll_opy_ and bstack1l1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥ᎗") in bstack1ll11l1l1ll_opy_ and bstack1l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧ᎘") in bstack1ll11l1l1ll_opy_[bstack1l1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧ᎙")]
    @staticmethod
    def bstack1ll1l1l1lll_opy_(method_name: str, *args):
        if not bstack1llll1ll111_opy_.bstack1ll1l1l1l11_opy_(method_name):
            return False
        if not bstack1llll1ll111_opy_.bstack1l11lll1111_opy_ in bstack1llll1ll111_opy_.bstack1l1l11111l1_opy_(*args):
            return False
        bstack1ll11l1l1ll_opy_ = bstack1llll1ll111_opy_.bstack1ll11l1l11l_opy_(*args)
        return (
            bstack1ll11l1l1ll_opy_
            and bstack1l1_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨ᎚") in bstack1ll11l1l1ll_opy_
            and bstack1l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡨࡸࡩࡱࡶࠥ᎛") in bstack1ll11l1l1ll_opy_[bstack1l1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣ᎜")]
        )
    @staticmethod
    def bstack1l1l11111l1_opy_(*args):
        return str(bstack1llll1ll111_opy_.bstack1ll1l111l1l_opy_(*args)).lower()