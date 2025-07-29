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
import os
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import (
    bstack11111ll1l1_opy_,
    bstack1llllllllll_opy_,
    bstack11111l11l1_opy_,
    bstack1llllll1lll_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
from bstack_utils.bstack1ll1lll1l_opy_ import bstack1lll11l1lll_opy_
from bstack_utils.constants import EVENTS
class bstack1lll111l11l_opy_(bstack11111ll1l1_opy_):
    bstack1l11lll1111_opy_ = bstack1ll_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠣᓬ")
    NAME = bstack1ll_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᓭ")
    bstack1l1l1lll1l1_opy_ = bstack1ll_opy_ (u"ࠥ࡬ࡺࡨ࡟ࡶࡴ࡯ࠦᓮ")
    bstack1l1l1ll111l_opy_ = bstack1ll_opy_ (u"ࠦ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠦᓯ")
    bstack1l11111l1ll_opy_ = bstack1ll_opy_ (u"ࠧ࡯࡮ࡱࡷࡷࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᓰ")
    bstack1l1l1lllll1_opy_ = bstack1ll_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᓱ")
    bstack1l11lll1l1l_opy_ = bstack1ll_opy_ (u"ࠢࡪࡵࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡ࡫ࡹࡧࠨᓲ")
    bstack1l11111lll1_opy_ = bstack1ll_opy_ (u"ࠣࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠧᓳ")
    bstack1l11111l11l_opy_ = bstack1ll_opy_ (u"ࠤࡨࡲࡩ࡫ࡤࡠࡣࡷࠦᓴ")
    bstack1ll1l1l111l_opy_ = bstack1ll_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࠦᓵ")
    bstack1l1l11111ll_opy_ = bstack1ll_opy_ (u"ࠦࡳ࡫ࡷࡴࡧࡶࡷ࡮ࡵ࡮ࠣᓶ")
    bstack1l11111l1l1_opy_ = bstack1ll_opy_ (u"ࠧ࡭ࡥࡵࠤᓷ")
    bstack1l1ll1l1l1l_opy_ = bstack1ll_opy_ (u"ࠨࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠥᓸ")
    bstack1l11lll11ll_opy_ = bstack1ll_opy_ (u"ࠢࡸ࠵ࡦࡩࡽ࡫ࡣࡶࡶࡨࡷࡨࡸࡩࡱࡶࠥᓹ")
    bstack1l11ll1ll1l_opy_ = bstack1ll_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࡥࡸࡿ࡮ࡤࠤᓺ")
    bstack1l11111ll11_opy_ = bstack1ll_opy_ (u"ࠤࡴࡹ࡮ࡺࠢᓻ")
    bstack1l11111ll1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l1l111l1l1_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1llll111l11_opy_: Any
    bstack1l11ll1l1ll_opy_: Dict
    def __init__(
        self,
        bstack1l1l111l1l1_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1llll111l11_opy_: Dict[str, Any],
        methods=[bstack1ll_opy_ (u"ࠥࡣࡤ࡯࡮ࡪࡶࡢࡣࠧᓼ"), bstack1ll_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࠦᓽ"), bstack1ll_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᓾ"), bstack1ll_opy_ (u"ࠨࡱࡶ࡫ࡷࠦᓿ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l1l111l1l1_opy_ = bstack1l1l111l1l1_opy_
        self.platform_index = platform_index
        self.bstack1llllll11l1_opy_(methods)
        self.bstack1llll111l11_opy_ = bstack1llll111l11_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack11111ll1l1_opy_.get_data(bstack1lll111l11l_opy_.bstack1l1l1ll111l_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack11111ll1l1_opy_.get_data(bstack1lll111l11l_opy_.bstack1l1l1lll1l1_opy_, target, strict)
    @staticmethod
    def bstack1l11111llll_opy_(target: object, strict=True):
        return bstack11111ll1l1_opy_.get_data(bstack1lll111l11l_opy_.bstack1l11111l1ll_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack11111ll1l1_opy_.get_data(bstack1lll111l11l_opy_.bstack1l1l1lllll1_opy_, target, strict)
    @staticmethod
    def bstack1ll111lll1l_opy_(instance: bstack1llllllllll_opy_) -> bool:
        return bstack11111ll1l1_opy_.bstack1111111lll_opy_(instance, bstack1lll111l11l_opy_.bstack1l11lll1l1l_opy_, False)
    @staticmethod
    def bstack1ll1l111111_opy_(instance: bstack1llllllllll_opy_, default_value=None):
        return bstack11111ll1l1_opy_.bstack1111111lll_opy_(instance, bstack1lll111l11l_opy_.bstack1l1l1lll1l1_opy_, default_value)
    @staticmethod
    def bstack1ll11llll1l_opy_(instance: bstack1llllllllll_opy_, default_value=None):
        return bstack11111ll1l1_opy_.bstack1111111lll_opy_(instance, bstack1lll111l11l_opy_.bstack1l1l1lllll1_opy_, default_value)
    @staticmethod
    def bstack1ll11l1l111_opy_(hub_url: str, bstack1l1111l1111_opy_=bstack1ll_opy_ (u"ࠢ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠦᔀ")):
        try:
            bstack1l1111l111l_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack1l1111l111l_opy_.endswith(bstack1l1111l1111_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll1l11l1ll_opy_(method_name: str):
        return method_name == bstack1ll_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᔁ")
    @staticmethod
    def bstack1ll1l111l11_opy_(method_name: str, *args):
        return (
            bstack1lll111l11l_opy_.bstack1ll1l11l1ll_opy_(method_name)
            and bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args) == bstack1lll111l11l_opy_.bstack1l1l11111ll_opy_
        )
    @staticmethod
    def bstack1ll1l11lll1_opy_(method_name: str, *args):
        if not bstack1lll111l11l_opy_.bstack1ll1l11l1ll_opy_(method_name):
            return False
        if not bstack1lll111l11l_opy_.bstack1l11lll11ll_opy_ in bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args):
            return False
        bstack1ll11l111l1_opy_ = bstack1lll111l11l_opy_.bstack1ll11l111ll_opy_(*args)
        return bstack1ll11l111l1_opy_ and bstack1ll_opy_ (u"ࠤࡶࡧࡷ࡯ࡰࡵࠤᔂ") in bstack1ll11l111l1_opy_ and bstack1ll_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᔃ") in bstack1ll11l111l1_opy_[bstack1ll_opy_ (u"ࠦࡸࡩࡲࡪࡲࡷࠦᔄ")]
    @staticmethod
    def bstack1ll1l1l11l1_opy_(method_name: str, *args):
        if not bstack1lll111l11l_opy_.bstack1ll1l11l1ll_opy_(method_name):
            return False
        if not bstack1lll111l11l_opy_.bstack1l11lll11ll_opy_ in bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args):
            return False
        bstack1ll11l111l1_opy_ = bstack1lll111l11l_opy_.bstack1ll11l111ll_opy_(*args)
        return (
            bstack1ll11l111l1_opy_
            and bstack1ll_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᔅ") in bstack1ll11l111l1_opy_
            and bstack1ll_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࡡࡶࡧࡷ࡯ࡰࡵࠤᔆ") in bstack1ll11l111l1_opy_[bstack1ll_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᔇ")]
        )
    @staticmethod
    def bstack1l1l11ll111_opy_(*args):
        return str(bstack1lll111l11l_opy_.bstack1ll11llll11_opy_(*args)).lower()
    @staticmethod
    def bstack1ll11llll11_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1ll11l111ll_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack11l11ll11_opy_(driver):
        command_executor = getattr(driver, bstack1ll_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦᔈ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack1ll_opy_ (u"ࠤࡢࡹࡷࡲࠢᔉ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack1ll_opy_ (u"ࠥࡣࡨࡲࡩࡦࡰࡷࡣࡨࡵ࡮ࡧ࡫ࡪࠦᔊ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack1ll_opy_ (u"ࠦࡷ࡫࡭ࡰࡶࡨࡣࡸ࡫ࡲࡷࡧࡵࡣࡦࡪࡤࡳࠤᔋ"), None)
        return hub_url
    def bstack1l1l1111lll_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack1ll_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣᔌ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack1ll_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᔍ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack1ll_opy_ (u"ࠢࡠࡷࡵࡰࠧᔎ")):
                setattr(command_executor, bstack1ll_opy_ (u"ࠣࡡࡸࡶࡱࠨᔏ"), hub_url)
                result = True
        if result:
            self.bstack1l1l111l1l1_opy_ = hub_url
            bstack1lll111l11l_opy_.bstack111111l1l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l1l1lll1l1_opy_, hub_url)
            bstack1lll111l11l_opy_.bstack111111l1l1_opy_(
                instance, bstack1lll111l11l_opy_.bstack1l11lll1l1l_opy_, bstack1lll111l11l_opy_.bstack1ll11l1l111_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l11lll111l_opy_(bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_]):
        return bstack1ll_opy_ (u"ࠤ࠽ࠦᔐ").join((bstack11111l11l1_opy_(bstack111111ll1l_opy_[0]).name, bstack1llllll1lll_opy_(bstack111111ll1l_opy_[1]).name))
    @staticmethod
    def bstack1ll1l1l1ll1_opy_(bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_], callback: Callable):
        bstack1l11lll11l1_opy_ = bstack1lll111l11l_opy_.bstack1l11lll111l_opy_(bstack111111ll1l_opy_)
        if not bstack1l11lll11l1_opy_ in bstack1lll111l11l_opy_.bstack1l11111ll1l_opy_:
            bstack1lll111l11l_opy_.bstack1l11111ll1l_opy_[bstack1l11lll11l1_opy_] = []
        bstack1lll111l11l_opy_.bstack1l11111ll1l_opy_[bstack1l11lll11l1_opy_].append(callback)
    def bstack1llllll1ll1_opy_(self, instance: bstack1llllllllll_opy_, method_name: str, bstack1llllll1l1l_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack1ll_opy_ (u"ࠥࡷࡹࡧࡲࡵࡡࡶࡩࡸࡹࡩࡰࡰࠥᔑ")):
            return
        cmd = args[0] if method_name == bstack1ll_opy_ (u"ࠦࡪࡾࡥࡤࡷࡷࡩࠧᔒ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack1l1111l11l1_opy_ = bstack1ll_opy_ (u"ࠧࡀࠢᔓ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack11ll1l11l1_opy_(bstack1ll_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠢᔔ") + bstack1l1111l11l1_opy_, bstack1llllll1l1l_opy_)
    def bstack11111ll111_opy_(
        self,
        target: object,
        exec: Tuple[bstack1llllllllll_opy_, str],
        bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack11111llll1_opy_, bstack1l11ll1ll11_opy_ = bstack111111ll1l_opy_
        bstack1l11lll11l1_opy_ = bstack1lll111l11l_opy_.bstack1l11lll111l_opy_(bstack111111ll1l_opy_)
        self.logger.debug(bstack1ll_opy_ (u"ࠢࡰࡰࡢ࡬ࡴࡵ࡫࠻ࠢࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫࠽ࡼ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࢃࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᔕ") + str(kwargs) + bstack1ll_opy_ (u"ࠣࠤᔖ"))
        if bstack11111llll1_opy_ == bstack11111l11l1_opy_.QUIT:
            if bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.PRE:
                bstack1ll11lll1ll_opy_ = bstack1lll11l1lll_opy_.bstack1ll1ll11111_opy_(EVENTS.bstack1ll1l1lll1_opy_.value)
                bstack11111ll1l1_opy_.bstack111111l1l1_opy_(instance, EVENTS.bstack1ll1l1lll1_opy_.value, bstack1ll11lll1ll_opy_)
                self.logger.debug(bstack1ll_opy_ (u"ࠤ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀࢃࠠ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࡂࢁࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠨᔗ").format(instance, method_name, bstack11111llll1_opy_, bstack1l11ll1ll11_opy_))
        if bstack11111llll1_opy_ == bstack11111l11l1_opy_.bstack111111l11l_opy_:
            if bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.POST and not bstack1lll111l11l_opy_.bstack1l1l1ll111l_opy_ in instance.data:
                session_id = getattr(target, bstack1ll_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᔘ"), None)
                if session_id:
                    instance.data[bstack1lll111l11l_opy_.bstack1l1l1ll111l_opy_] = session_id
        elif (
            bstack11111llll1_opy_ == bstack11111l11l1_opy_.bstack1111111ll1_opy_
            and bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args) == bstack1lll111l11l_opy_.bstack1l1l11111ll_opy_
        ):
            if bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.PRE:
                hub_url = bstack1lll111l11l_opy_.bstack11l11ll11_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1lll111l11l_opy_.bstack1l1l1lll1l1_opy_: hub_url,
                            bstack1lll111l11l_opy_.bstack1l11lll1l1l_opy_: bstack1lll111l11l_opy_.bstack1ll11l1l111_opy_(hub_url),
                            bstack1lll111l11l_opy_.bstack1ll1l1l111l_opy_: int(
                                os.environ.get(bstack1ll_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠦᔙ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1ll11l111l1_opy_ = bstack1lll111l11l_opy_.bstack1ll11l111ll_opy_(*args)
                bstack1l11111llll_opy_ = bstack1ll11l111l1_opy_.get(bstack1ll_opy_ (u"ࠧࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᔚ"), None) if bstack1ll11l111l1_opy_ else None
                if isinstance(bstack1l11111llll_opy_, dict):
                    instance.data[bstack1lll111l11l_opy_.bstack1l11111l1ll_opy_] = copy.deepcopy(bstack1l11111llll_opy_)
                    instance.data[bstack1lll111l11l_opy_.bstack1l1l1lllll1_opy_] = bstack1l11111llll_opy_
            elif bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack1ll_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧᔛ"), dict()).get(bstack1ll_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥᔜ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1lll111l11l_opy_.bstack1l1l1ll111l_opy_: framework_session_id,
                                bstack1lll111l11l_opy_.bstack1l11111lll1_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack11111llll1_opy_ == bstack11111l11l1_opy_.bstack1111111ll1_opy_
            and bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args) == bstack1lll111l11l_opy_.bstack1l11111ll11_opy_
            and bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.POST
        ):
            instance.data[bstack1lll111l11l_opy_.bstack1l11111l11l_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l11lll11l1_opy_ in bstack1lll111l11l_opy_.bstack1l11111ll1l_opy_:
            bstack1l11lll1l11_opy_ = None
            for callback in bstack1lll111l11l_opy_.bstack1l11111ll1l_opy_[bstack1l11lll11l1_opy_]:
                try:
                    bstack1l11ll1llll_opy_ = callback(self, target, exec, bstack111111ll1l_opy_, result, *args, **kwargs)
                    if bstack1l11lll1l11_opy_ == None:
                        bstack1l11lll1l11_opy_ = bstack1l11ll1llll_opy_
                except Exception as e:
                    self.logger.error(bstack1ll_opy_ (u"ࠣࡧࡵࡶࡴࡸࠠࡪࡰࡹࡳࡰ࡯࡮ࡨࠢࡦࡥࡱࡲࡢࡢࡥ࡮࠾ࠥࠨᔝ") + str(e) + bstack1ll_opy_ (u"ࠤࠥᔞ"))
                    traceback.print_exc()
            if bstack11111llll1_opy_ == bstack11111l11l1_opy_.QUIT:
                if bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.POST:
                    bstack1ll11lll1ll_opy_ = bstack11111ll1l1_opy_.bstack1111111lll_opy_(instance, EVENTS.bstack1ll1l1lll1_opy_.value)
                    if bstack1ll11lll1ll_opy_!=None:
                        bstack1lll11l1lll_opy_.end(EVENTS.bstack1ll1l1lll1_opy_.value, bstack1ll11lll1ll_opy_+bstack1ll_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᔟ"), bstack1ll11lll1ll_opy_+bstack1ll_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᔠ"), True, None)
            if bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.PRE and callable(bstack1l11lll1l11_opy_):
                return bstack1l11lll1l11_opy_
            elif bstack1l11ll1ll11_opy_ == bstack1llllll1lll_opy_.POST and bstack1l11lll1l11_opy_:
                return bstack1l11lll1l11_opy_
    def bstack111111ll11_opy_(
        self, method_name, previous_state: bstack11111l11l1_opy_, *args, **kwargs
    ) -> bstack11111l11l1_opy_:
        if method_name == bstack1ll_opy_ (u"ࠧࡥ࡟ࡪࡰ࡬ࡸࡤࡥࠢᔡ") or method_name == bstack1ll_opy_ (u"ࠨࡳࡵࡣࡵࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࠨᔢ"):
            return bstack11111l11l1_opy_.bstack111111l11l_opy_
        if method_name == bstack1ll_opy_ (u"ࠢࡲࡷ࡬ࡸࠧᔣ"):
            return bstack11111l11l1_opy_.QUIT
        if method_name == bstack1ll_opy_ (u"ࠣࡧࡻࡩࡨࡻࡴࡦࠤᔤ"):
            if previous_state != bstack11111l11l1_opy_.NONE:
                bstack1ll1l11ll1l_opy_ = bstack1lll111l11l_opy_.bstack1l1l11ll111_opy_(*args)
                if bstack1ll1l11ll1l_opy_ == bstack1lll111l11l_opy_.bstack1l1l11111ll_opy_:
                    return bstack11111l11l1_opy_.bstack111111l11l_opy_
            return bstack11111l11l1_opy_.bstack1111111ll1_opy_
        return bstack11111l11l1_opy_.NONE