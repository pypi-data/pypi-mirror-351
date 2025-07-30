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
import logging
from enum import Enum
from typing import Dict, Tuple, Callable, Type, List, Any
import abc
from datetime import datetime, timezone, timedelta
from browserstack_sdk.sdk_cli.bstack1lllllll1ll_opy_ import bstack11111lll11_opy_, bstack111111llll_opy_
import os
import threading
class bstack111111ll1l_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1l1_opy_ (u"ࠣࡊࡲࡳࡰ࡙ࡴࡢࡶࡨ࠲ࢀࢃࠢေ").format(self.name)
class bstack11111l11ll_opy_(Enum):
    NONE = 0
    bstack1llllll11ll_opy_ = 1
    bstack11111l1lll_opy_ = 3
    bstack1llllll1111_opy_ = 4
    bstack11111llll1_opy_ = 5
    QUIT = 6
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1l1_opy_ (u"ࠤࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡔࡶࡤࡸࡪ࠴ࡻࡾࠤဲ").format(self.name)
class bstack11111l1l1l_opy_(bstack11111lll11_opy_):
    framework_name: str
    framework_version: str
    state: bstack11111l11ll_opy_
    previous_state: bstack11111l11ll_opy_
    bstack1llllllll1l_opy_: datetime
    bstack11111111l1_opy_: datetime
    def __init__(
        self,
        context: bstack111111llll_opy_,
        framework_name: str,
        framework_version: str,
        state=bstack11111l11ll_opy_.NONE,
    ):
        super().__init__(context)
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.state = state
        self.previous_state = bstack11111l11ll_opy_.NONE
        self.bstack1llllllll1l_opy_ = datetime.now(tz=timezone.utc)
        self.bstack11111111l1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llllllll11_opy_(self, bstack111111l111_opy_: bstack11111l11ll_opy_):
        bstack1llllll1l11_opy_ = bstack11111l11ll_opy_(bstack111111l111_opy_).name
        if not bstack1llllll1l11_opy_:
            return False
        if bstack111111l111_opy_ == self.state:
            return False
        if self.state == bstack11111l11ll_opy_.bstack11111l1lll_opy_: # bstack1111111lll_opy_ bstack11111ll1ll_opy_ for bstack111111l1ll_opy_ in bstack1lllllllll1_opy_, it bstack11111ll1l1_opy_ bstack11111l11l1_opy_ bstack11111l1l11_opy_ times bstack11111ll111_opy_ a new state
            return True
        if (
            bstack111111l111_opy_ == bstack11111l11ll_opy_.NONE
            or (self.state != bstack11111l11ll_opy_.NONE and bstack111111l111_opy_ == bstack11111l11ll_opy_.bstack1llllll11ll_opy_)
            or (self.state < bstack11111l11ll_opy_.bstack1llllll11ll_opy_ and bstack111111l111_opy_ == bstack11111l11ll_opy_.bstack1llllll1111_opy_)
            or (self.state < bstack11111l11ll_opy_.bstack1llllll11ll_opy_ and bstack111111l111_opy_ == bstack11111l11ll_opy_.QUIT)
        ):
            raise ValueError(bstack1l1_opy_ (u"ࠥ࡭ࡳࡼࡡ࡭࡫ࡧࠤࡸࡺࡡࡵࡧࠣࡸࡷࡧ࡮ࡴ࡫ࡷ࡭ࡴࡴ࠺ࠡࠤဳ") + str(self.state) + bstack1l1_opy_ (u"ࠦࠥࡃ࠾ࠡࠤဴ") + str(bstack111111l111_opy_))
        self.previous_state = self.state
        self.state = bstack111111l111_opy_
        self.bstack11111111l1_opy_ = datetime.now(tz=timezone.utc)
        return True
class bstack111111111l_opy_(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1111111111_opy_: Dict[str, bstack11111l1l1l_opy_] = dict()
    framework_name: str
    framework_version: str
    classes: List[Type]
    def __init__(
        self,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
    ):
        self.framework_name = framework_name
        self.framework_version = framework_version
        self.classes = classes
    @abc.abstractmethod
    def bstack1llllllllll_opy_(self, instance: bstack11111l1l1l_opy_, method_name: str, bstack1llllll111l_opy_: timedelta, *args, **kwargs):
        return
    @abc.abstractmethod
    def bstack111111ll11_opy_(
        self, method_name, previous_state: bstack11111l11ll_opy_, *args, **kwargs
    ) -> bstack11111l11ll_opy_:
        return
    @abc.abstractmethod
    def bstack1lllllll11l_opy_(
        self,
        target: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable:
        return
    def bstack111111lll1_opy_(self, bstack11111111ll_opy_: List[str]):
        for clazz in self.classes:
            for method_name in bstack11111111ll_opy_:
                bstack1llllll11l1_opy_ = getattr(clazz, method_name, None)
                if not callable(bstack1llllll11l1_opy_):
                    self.logger.warning(bstack1l1_opy_ (u"ࠧࡻ࡮ࡱࡣࡷࡧ࡭࡫ࡤࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠢࠥဵ") + str(method_name) + bstack1l1_opy_ (u"ࠨࠢံ"))
                    continue
                bstack11111l1ll1_opy_ = self.bstack111111ll11_opy_(
                    method_name, previous_state=bstack11111l11ll_opy_.NONE
                )
                bstack111111l1l1_opy_ = self.bstack111111l11l_opy_(
                    method_name,
                    (bstack11111l1ll1_opy_ if bstack11111l1ll1_opy_ else bstack11111l11ll_opy_.NONE),
                    bstack1llllll11l1_opy_,
                )
                if not callable(bstack111111l1l1_opy_):
                    self.logger.warning(bstack1l1_opy_ (u"ࠢ࡮ࡧࡷ࡬ࡴࡪࠠ࡯ࡱࡷࠤࡵࡧࡴࡤࡪࡨࡨ࠿ࠦࡻ࡮ࡧࡷ࡬ࡴࡪ࡟࡯ࡣࡰࡩࢂࠦࠨࡼࡵࡨࡰ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽ࠻့ࠢࠥ") + str(self.framework_version) + bstack1l1_opy_ (u"ࠣࠫࠥး"))
                    continue
                setattr(clazz, method_name, bstack111111l1l1_opy_)
    def bstack111111l11l_opy_(
        self,
        method_name: str,
        bstack11111l1ll1_opy_: bstack11111l11ll_opy_,
        bstack1llllll11l1_opy_: Callable,
    ):
        def wrapped(target, *args, **kwargs):
            bstack11111ll11_opy_ = datetime.now()
            (bstack11111l1ll1_opy_,) = wrapped.__vars__
            bstack11111l1ll1_opy_ = (
                bstack11111l1ll1_opy_
                if bstack11111l1ll1_opy_ and bstack11111l1ll1_opy_ != bstack11111l11ll_opy_.NONE
                else self.bstack111111ll11_opy_(method_name, previous_state=bstack11111l1ll1_opy_, *args, **kwargs)
            )
            if bstack11111l1ll1_opy_ == bstack11111l11ll_opy_.bstack1llllll11ll_opy_:
                ctx = bstack11111lll11_opy_.create_context(self.bstack1111111l1l_opy_(target))
                if not self.bstack1lllllll1l1_opy_() or ctx.id not in bstack111111111l_opy_.bstack1111111111_opy_:
                    bstack111111111l_opy_.bstack1111111111_opy_[ctx.id] = bstack11111l1l1l_opy_(
                        ctx, self.framework_name, self.framework_version, bstack11111l1ll1_opy_
                    )
                self.logger.debug(bstack1l1_opy_ (u"ࠤࡺࡶࡦࡶࡰࡦࡦࠣࡱࡪࡺࡨࡰࡦࠣࡧࡷ࡫ࡡࡵࡧࡧ࠾ࠥࢁࡴࡢࡴࡪࡩࡹ࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠࡿࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡤࡶࡻࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿္ࠥ") + str(bstack111111111l_opy_.bstack1111111111_opy_.keys()) + bstack1l1_opy_ (u"်ࠥࠦ"))
            else:
                self.logger.debug(bstack1l1_opy_ (u"ࠦࡼࡸࡡࡱࡲࡨࡨࠥࡳࡥࡵࡪࡲࡨࠥ࡯࡮ࡷࡱ࡮ࡩࡩࡀࠠࡼࡶࡤࡶ࡬࡫ࡴ࠯ࡡࡢࡧࡱࡧࡳࡴࡡࡢࢁࠥࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࡀࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡷࡂࠨျ") + str(bstack111111111l_opy_.bstack1111111111_opy_.keys()) + bstack1l1_opy_ (u"ࠧࠨြ"))
            instance = bstack111111111l_opy_.bstack11111l111l_opy_(self.bstack1111111l1l_opy_(target))
            if bstack11111l1ll1_opy_ == bstack11111l11ll_opy_.NONE or not instance:
                ctx = bstack11111lll11_opy_.create_context(self.bstack1111111l1l_opy_(target))
                self.logger.warning(bstack1l1_opy_ (u"ࠨࡷࡳࡣࡳࡴࡪࡪࠠ࡮ࡧࡷ࡬ࡴࡪࠠࡶࡰࡷࡶࡦࡩ࡫ࡦࡦ࠽ࠤࢀࡳࡥࡵࡪࡲࡨࡤࡴࡡ࡮ࡧࢀࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࡃࡻࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡧࡹࡾ࠽ࡼࡥࡷࡼࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥွ") + str(bstack111111111l_opy_.bstack1111111111_opy_.keys()) + bstack1l1_opy_ (u"ࠢࠣှ"))
                return bstack1llllll11l1_opy_(target, *args, **kwargs)
            bstack1lllllll111_opy_ = self.bstack1lllllll11l_opy_(
                target,
                (instance, method_name),
                (bstack11111l1ll1_opy_, bstack111111ll1l_opy_.PRE),
                None,
                *args,
                **kwargs,
            )
            if instance.bstack1llllllll11_opy_(bstack11111l1ll1_opy_):
                self.logger.debug(bstack1l1_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡥࡥࠢࡶࡸࡦࡺࡥ࠮ࡶࡵࡥࡳࡹࡩࡵ࡫ࡲࡲ࠿ࠦࡻࡪࡰࡶࡸࡦࡴࡣࡦ࠰ࡳࡶࡪࡼࡩࡰࡷࡶࡣࡸࡺࡡࡵࡧࢀࠤࡂࡄࠠࡼ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࡷࡹࡧࡴࡦࡿࠣࠬࢀࡺࡹࡱࡧࠫࡸࡦࡸࡧࡦࡶࠬࢁ࠳ࢁ࡭ࡦࡶ࡫ࡳࡩࡥ࡮ࡢ࡯ࡨࢁࠥࢁࡡࡳࡩࡶࢁ࠮࡛ࠦࠣဿ") + str(instance.ref()) + bstack1l1_opy_ (u"ࠤࡠࠦ၀"))
            result = (
                bstack1lllllll111_opy_(target, bstack1llllll11l1_opy_, *args, **kwargs)
                if callable(bstack1lllllll111_opy_)
                else bstack1llllll11l1_opy_(target, *args, **kwargs)
            )
            bstack11111lll1l_opy_ = self.bstack1lllllll11l_opy_(
                target,
                (instance, method_name),
                (bstack11111l1ll1_opy_, bstack111111ll1l_opy_.POST),
                result,
                *args,
                **kwargs,
            )
            self.bstack1llllllllll_opy_(instance, method_name, datetime.now() - bstack11111ll11_opy_, *args, **kwargs)
            return bstack11111lll1l_opy_ if bstack11111lll1l_opy_ else result
        wrapped.__name__ = method_name
        wrapped.__vars__ = (bstack11111l1ll1_opy_,)
        return wrapped
    @staticmethod
    def bstack11111l111l_opy_(target: object, strict=True):
        ctx = bstack11111lll11_opy_.create_context(target)
        instance = bstack111111111l_opy_.bstack1111111111_opy_.get(ctx.id, None)
        if instance and instance.bstack1llllll1ll1_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack11111ll11l_opy_(
        ctx: bstack111111llll_opy_, state: bstack11111l11ll_opy_, reverse=True
    ) -> List[bstack11111l1l1l_opy_]:
        return sorted(
            filter(
                lambda t: t.state == state
                and t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                bstack111111111l_opy_.bstack1111111111_opy_.values(),
            ),
            key=lambda t: t.bstack1llllllll1l_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1111111ll1_opy_(instance: bstack11111l1l1l_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llllll1lll_opy_(instance: bstack11111l1l1l_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llllllll11_opy_(instance: bstack11111l1l1l_opy_, key: str, value: Any) -> bool:
        instance.data[key] = value
        bstack111111111l_opy_.logger.debug(bstack1l1_opy_ (u"ࠥࡷࡪࡺ࡟ࡴࡶࡤࡸࡪࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࡾ࡭ࡳࡹࡴࡢࡰࡦࡩ࠳ࡸࡥࡧࠪࠬࢁࠥࡱࡥࡺ࠿ࡾ࡯ࡪࡿࡽࠡࡸࡤࡰࡺ࡫࠽ࠣ၁") + str(value) + bstack1l1_opy_ (u"ࠦࠧ၂"))
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = bstack111111111l_opy_.bstack11111l111l_opy_(target, strict)
        return bstack111111111l_opy_.bstack1llllll1lll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = bstack111111111l_opy_.bstack11111l111l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    def bstack1lllllll1l1_opy_(self):
        return self.framework_name == bstack1l1_opy_ (u"ࠬࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠩ၃")
    def bstack1111111l1l_opy_(self, target):
        return target if not self.bstack1lllllll1l1_opy_() else self.bstack11111l1111_opy_()
    @staticmethod
    def bstack11111l1111_opy_():
        return str(os.getpid()) + str(threading.get_ident())