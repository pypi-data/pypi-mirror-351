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
from browserstack_sdk.sdk_cli.bstack1llll1lll1l_opy_ import bstack1ll1llllll1_opy_
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import (
    bstack11111l11l1_opy_,
    bstack1llllll1lll_opy_,
    bstack11111ll1l1_opy_,
    bstack1llllllllll_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1ll1_opy_ import bstack1lll111l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1llll1ll111_opy_
from browserstack_sdk.sdk_cli.bstack111111lll1_opy_ import bstack1llllll11ll_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1llll1lll1l_opy_ import bstack1ll1llllll1_opy_
import weakref
class bstack1ll111l1lll_opy_(bstack1ll1llllll1_opy_):
    bstack1ll111ll1ll_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack1llllllllll_opy_]]
    pages: Dict[str, Tuple[Callable, bstack1llllllllll_opy_]]
    def __init__(self, bstack1ll111ll1ll_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1ll111lllll_opy_ = dict()
        self.bstack1ll111ll1ll_opy_ = bstack1ll111ll1ll_opy_
        self.frameworks = frameworks
        bstack1llll1ll111_opy_.bstack1ll1l1l1ll1_opy_((bstack11111l11l1_opy_.bstack111111l11l_opy_, bstack1llllll1lll_opy_.POST), self.__1ll111lll11_opy_)
        if any(bstack1lll111l11l_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1lll111l11l_opy_.bstack1ll1l1l1ll1_opy_(
                (bstack11111l11l1_opy_.bstack1111111ll1_opy_, bstack1llllll1lll_opy_.PRE), self.__1ll111ll11l_opy_
            )
            bstack1lll111l11l_opy_.bstack1ll1l1l1ll1_opy_(
                (bstack11111l11l1_opy_.QUIT, bstack1llllll1lll_opy_.POST), self.__1ll111ll111_opy_
            )
    def __1ll111lll11_opy_(
        self,
        f: bstack1llll1ll111_opy_,
        bstack1ll111l1l1l_opy_: object,
        exec: Tuple[bstack1llllllllll_opy_, str],
        bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack1ll_opy_ (u"ࠧࡴࡥࡸࡡࡳࡥ࡬࡫ࠢᇄ"):
                return
            contexts = bstack1ll111l1l1l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1ll_opy_ (u"ࠨࡡࡣࡱࡸࡸ࠿ࡨ࡬ࡢࡰ࡮ࠦᇅ") in page.url:
                                self.logger.debug(bstack1ll_opy_ (u"ࠢࡔࡶࡲࡶ࡮ࡴࡧࠡࡶ࡫ࡩࠥࡴࡥࡸࠢࡳࡥ࡬࡫ࠠࡪࡰࡶࡸࡦࡴࡣࡦࠤᇆ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack11111ll1l1_opy_.bstack111111l1l1_opy_(instance, self.bstack1ll111ll1ll_opy_, True)
                                self.logger.debug(bstack1ll_opy_ (u"ࠣࡡࡢࡳࡳࡥࡰࡢࡩࡨࡣ࡮ࡴࡩࡵ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࠨᇇ") + str(instance.ref()) + bstack1ll_opy_ (u"ࠤࠥᇈ"))
        except Exception as e:
            self.logger.debug(bstack1ll_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡴࡸࡩ࡯ࡩࠣࡲࡪࡽࠠࡱࡣࡪࡩࠥࡀࠢᇉ"),e)
    def __1ll111ll11l_opy_(
        self,
        f: bstack1lll111l11l_opy_,
        driver: object,
        exec: Tuple[bstack1llllllllll_opy_, str],
        bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack11111ll1l1_opy_.bstack1111111lll_opy_(instance, self.bstack1ll111ll1ll_opy_, False):
            return
        if not f.bstack1ll11l1l111_opy_(f.hub_url(driver)):
            self.bstack1ll111lllll_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack11111ll1l1_opy_.bstack111111l1l1_opy_(instance, self.bstack1ll111ll1ll_opy_, True)
            self.logger.debug(bstack1ll_opy_ (u"ࠦࡤࡥ࡯࡯ࡡࡶࡩࡱ࡫࡮ࡪࡷࡰࡣ࡮ࡴࡩࡵ࠼ࠣࡲࡴࡴ࡟ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡤࡳ࡫ࡹࡩࡷࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᇊ") + str(instance.ref()) + bstack1ll_opy_ (u"ࠧࠨᇋ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack11111ll1l1_opy_.bstack111111l1l1_opy_(instance, self.bstack1ll111ll1ll_opy_, True)
        self.logger.debug(bstack1ll_opy_ (u"ࠨ࡟ࡠࡱࡱࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡩ࡯࡫ࡷ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᇌ") + str(instance.ref()) + bstack1ll_opy_ (u"ࠢࠣᇍ"))
    def __1ll111ll111_opy_(
        self,
        f: bstack1lll111l11l_opy_,
        driver: object,
        exec: Tuple[bstack1llllllllll_opy_, str],
        bstack111111ll1l_opy_: Tuple[bstack11111l11l1_opy_, bstack1llllll1lll_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1ll111l1ll1_opy_(instance)
        self.logger.debug(bstack1ll_opy_ (u"ࠣࡡࡢࡳࡳࡥࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡠࡳࡸ࡭ࡹࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥᇎ") + str(instance.ref()) + bstack1ll_opy_ (u"ࠤࠥᇏ"))
    def bstack1ll11l1111l_opy_(self, context: bstack1llllll11ll_opy_, reverse=True) -> List[Tuple[Callable, bstack1llllllllll_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1ll11l11111_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1lll111l11l_opy_.bstack1ll111lll1l_opy_(data[1])
                    and data[1].bstack1ll11l11111_opy_(context)
                    and getattr(data[0](), bstack1ll_opy_ (u"ࠥࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᇐ"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack11111l1lll_opy_, reverse=reverse)
    def bstack1ll111l1l11_opy_(self, context: bstack1llllll11ll_opy_, reverse=True) -> List[Tuple[Callable, bstack1llllllllll_opy_]]:
        matches = []
        for data in self.bstack1ll111lllll_opy_.values():
            if (
                data[1].bstack1ll11l11111_opy_(context)
                and getattr(data[0](), bstack1ll_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠣᇑ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack11111l1lll_opy_, reverse=reverse)
    def bstack1ll111llll1_opy_(self, instance: bstack1llllllllll_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1ll111l1ll1_opy_(self, instance: bstack1llllllllll_opy_) -> bool:
        if self.bstack1ll111llll1_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack11111ll1l1_opy_.bstack111111l1l1_opy_(instance, self.bstack1ll111ll1ll_opy_, False)
            return True
        return False