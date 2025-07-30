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
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1111l11111_opy_ import bstack1111l111ll_opy_
from browserstack_sdk.sdk_cli.bstack1lllllll1ll_opy_ import bstack11111lll11_opy_, bstack111111llll_opy_
class bstack1lllll1111l_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1l1_opy_ (u"ࠤࡗࡩࡸࡺࡈࡰࡱ࡮ࡗࡹࡧࡴࡦ࠰ࡾࢁࠧᔥ").format(self.name)
class bstack1llll1ll1ll_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1l1_opy_ (u"ࠥࡘࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡖࡸࡦࡺࡥ࠯ࡽࢀࠦᔦ").format(self.name)
class bstack1lll111l1ll_opy_(bstack11111lll11_opy_):
    bstack1ll11ll1lll_opy_: List[str]
    bstack1l11l111ll1_opy_: Dict[str, str]
    state: bstack1llll1ll1ll_opy_
    bstack1llllllll1l_opy_: datetime
    bstack11111111l1_opy_: datetime
    def __init__(
        self,
        context: bstack111111llll_opy_,
        bstack1ll11ll1lll_opy_: List[str],
        bstack1l11l111ll1_opy_: Dict[str, str],
        state=bstack1llll1ll1ll_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1ll11ll1lll_opy_ = bstack1ll11ll1lll_opy_
        self.bstack1l11l111ll1_opy_ = bstack1l11l111ll1_opy_
        self.state = state
        self.bstack1llllllll1l_opy_ = datetime.now(tz=timezone.utc)
        self.bstack11111111l1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1llllllll11_opy_(self, bstack111111l111_opy_: bstack1llll1ll1ll_opy_):
        bstack1llllll1l11_opy_ = bstack1llll1ll1ll_opy_(bstack111111l111_opy_).name
        if not bstack1llllll1l11_opy_:
            return False
        if bstack111111l111_opy_ == self.state:
            return False
        self.state = bstack111111l111_opy_
        self.bstack11111111l1_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack1l11ll1l1l1_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1lllll1l11l_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1ll11111l11_opy_: int = None
    bstack1l1ll1ll11l_opy_: str = None
    bstack1l11l1l_opy_: str = None
    bstack1111ll1ll_opy_: str = None
    bstack1l1lll1ll11_opy_: str = None
    bstack1l11l111l1l_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll1l11l11l_opy_ = bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡸࡹ࡮ࡪࠢᔧ")
    bstack1l11l1l1l11_opy_ = bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࡢ࡭ࡩࠨᔨ")
    bstack1ll1l1l1111_opy_ = bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡳࡧ࡭ࡦࠤᔩ")
    bstack1l11ll1111l_opy_ = bstack1l1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡢࡴࡦࡺࡨࠣᔪ")
    bstack1l11l1ll1l1_opy_ = bstack1l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡴࡢࡩࡶࠦᔫ")
    bstack1l1l1l1l1ll_opy_ = bstack1l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡳࡧࡶࡹࡱࡺࠢᔬ")
    bstack1ll1111l1ll_opy_ = bstack1l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡷࡺࡲࡴࡠࡣࡷࠦᔭ")
    bstack1l1lll1llll_opy_ = bstack1l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨᔮ")
    bstack1l1lll1111l_opy_ = bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡩࡳࡪࡥࡥࡡࡤࡸࠧᔯ")
    bstack1l1111lllll_opy_ = bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡱࡵࡣࡢࡶ࡬ࡳࡳࠨᔰ")
    bstack1ll11llll11_opy_ = bstack1l1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡰࡤࡱࡪࠨᔱ")
    bstack1l1llll1111_opy_ = bstack1l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠥᔲ")
    bstack1l111l1l1ll_opy_ = bstack1l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡤࡱࡧࡩࠧᔳ")
    bstack1l1ll111lll_opy_ = bstack1l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡶࡺࡴ࡟࡯ࡣࡰࡩࠧᔴ")
    bstack1ll1l11ll1l_opy_ = bstack1l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠧᔵ")
    bstack1l1l1l1llll_opy_ = bstack1l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪࡦ࡯࡬ࡶࡴࡨࠦᔶ")
    bstack1l11l111l11_opy_ = bstack1l1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠥᔷ")
    bstack1l111ll1lll_opy_ = bstack1l1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡲ࡯ࡨࡵࠥᔸ")
    bstack1l11l1lllll_opy_ = bstack1l1_opy_ (u"ࠣࡶࡨࡷࡹࡥ࡭ࡦࡶࡤࠦᔹ")
    bstack1l1111l1l1l_opy_ = bstack1l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡴࡥࡲࡴࡪࡹࠧᔺ")
    bstack1l11llll11l_opy_ = bstack1l1_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࡤࡹࡥࡴࡵ࡬ࡳࡳࡥ࡮ࡢ࡯ࡨࠦᔻ")
    bstack1l111l1llll_opy_ = bstack1l1_opy_ (u"ࠦࡪࡼࡥ࡯ࡶࡢࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠢᔼ")
    bstack1l1111ll1l1_opy_ = bstack1l1_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡪࡴࡤࡦࡦࡢࡥࡹࠨᔽ")
    bstack1l111ll1l11_opy_ = bstack1l1_opy_ (u"ࠨࡨࡰࡱ࡮ࡣ࡮ࡪࠢᔾ")
    bstack1l11l11lll1_opy_ = bstack1l1_opy_ (u"ࠢࡩࡱࡲ࡯ࡤࡸࡥࡴࡷ࡯ࡸࠧᔿ")
    bstack1l11l1llll1_opy_ = bstack1l1_opy_ (u"ࠣࡪࡲࡳࡰࡥ࡬ࡰࡩࡶࠦᕀ")
    bstack1l1111ll1ll_opy_ = bstack1l1_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟࡯ࡣࡰࡩࠧᕁ")
    bstack1l111l1ll1l_opy_ = bstack1l1_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᕂ")
    bstack1l1111lll1l_opy_ = bstack1l1_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨᕃ")
    bstack1l111lllll1_opy_ = bstack1l1_opy_ (u"ࠧࡶࡥ࡯ࡦ࡬ࡲ࡬ࠨᕄ")
    bstack1l111l11lll_opy_ = bstack1l1_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢᕅ")
    bstack1ll1111l111_opy_ = bstack1l1_opy_ (u"ࠢࡕࡇࡖࡘࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࠤᕆ")
    bstack1ll1111lll1_opy_ = bstack1l1_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡌࡐࡉࠥᕇ")
    bstack1ll1111111l_opy_ = bstack1l1_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡂࡖࡗࡅࡈࡎࡍࡆࡐࡗࠦᕈ")
    bstack1111111111_opy_: Dict[str, bstack1lll111l1ll_opy_] = dict()
    bstack1l1111l1111_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11ll1lll_opy_: List[str]
    bstack1l11l111ll1_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1ll11ll1lll_opy_: List[str],
        bstack1l11l111ll1_opy_: Dict[str, str],
        bstack1111l11111_opy_: bstack1111l111ll_opy_
    ):
        self.bstack1ll11ll1lll_opy_ = bstack1ll11ll1lll_opy_
        self.bstack1l11l111ll1_opy_ = bstack1l11l111ll1_opy_
        self.bstack1111l11111_opy_ = bstack1111l11111_opy_
    def track_event(
        self,
        context: bstack1l11ll1l1l1_opy_,
        test_framework_state: bstack1llll1ll1ll_opy_,
        test_hook_state: bstack1lllll1111l_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack1l1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࡼࡿࠣࡥࡷ࡭ࡳ࠾ࡽࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࢃࠢᕉ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack1l11l11l111_opy_(
        self,
        instance: bstack1lll111l1ll_opy_,
        bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_],
        *args,
        **kwargs,
    ):
        bstack1l11lll111l_opy_ = TestFramework.bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_)
        if not bstack1l11lll111l_opy_ in TestFramework.bstack1l1111l1111_opy_:
            return
        self.logger.debug(bstack1l1_opy_ (u"ࠦ࡮ࡴࡶࡰ࡭࡬ࡲ࡬ࠦࡻࡾࠢࡦࡥࡱࡲࡢࡢࡥ࡮ࡷࠧᕊ").format(len(TestFramework.bstack1l1111l1111_opy_[bstack1l11lll111l_opy_])))
        for callback in TestFramework.bstack1l1111l1111_opy_[bstack1l11lll111l_opy_]:
            try:
                callback(self, instance, bstack1llllll1l1l_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack1l1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠤ࡮ࡴࡶࡰ࡭࡬ࡲ࡬ࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢࡾࢁࠧᕋ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1ll1l1l11_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1ll1l1111_opy_(self, instance, bstack1llllll1l1l_opy_):
        return
    @abc.abstractmethod
    def bstack1l1lll1ll1l_opy_(self, instance, bstack1llllll1l1l_opy_):
        return
    @staticmethod
    def bstack11111l111l_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack11111lll11_opy_.create_context(target)
        instance = TestFramework.bstack1111111111_opy_.get(ctx.id, None)
        if instance and instance.bstack1llllll1ll1_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1ll1lll1l_opy_(reverse=True) -> List[bstack1lll111l1ll_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1111111111_opy_.values(),
            ),
            key=lambda t: t.bstack1llllllll1l_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack11111ll11l_opy_(ctx: bstack111111llll_opy_, reverse=True) -> List[bstack1lll111l1ll_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1111111111_opy_.values(),
            ),
            key=lambda t: t.bstack1llllllll1l_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1111111ll1_opy_(instance: bstack1lll111l1ll_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1llllll1lll_opy_(instance: bstack1lll111l1ll_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1llllllll11_opy_(instance: bstack1lll111l1ll_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1l1_opy_ (u"ࠨࡳࡦࡶࡢࡷࡹࡧࡴࡦ࠼ࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡ࡭ࡨࡽࡂࢁࡽࠡࡸࡤࡰࡺ࡫࠽ࡼࡿࠥᕌ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l11ll11l1l_opy_(instance: bstack1lll111l1ll_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack1l1_opy_ (u"ࠢࡴࡧࡷࡣࡸࡺࡡࡵࡧࡢࡩࡳࡺࡲࡪࡧࡶ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࡼࡿࠣࡩࡳࡺࡲࡪࡧࡶࡁࢀࢃࠢᕍ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack1l11111l111_opy_(instance: bstack1llll1ll1ll_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1l1_opy_ (u"ࠣࡷࡳࡨࡦࡺࡥࡠࡵࡷࡥࡹ࡫࠺ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿࢂࠦ࡫ࡦࡻࡀࡿࢂࠦࡶࡢ࡮ࡸࡩࡂࢁࡽࠣᕎ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack11111l111l_opy_(target, strict)
        return TestFramework.bstack1llllll1lll_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack11111l111l_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l11l11ll11_opy_(instance: bstack1lll111l1ll_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l111l1l1l1_opy_(instance: bstack1lll111l1ll_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_]):
        return bstack1l1_opy_ (u"ࠤ࠽ࠦᕏ").join((bstack1llll1ll1ll_opy_(bstack1llllll1l1l_opy_[0]).name, bstack1lllll1111l_opy_(bstack1llllll1l1l_opy_[1]).name))
    @staticmethod
    def bstack1ll11ll1l1l_opy_(bstack1llllll1l1l_opy_: Tuple[bstack1llll1ll1ll_opy_, bstack1lllll1111l_opy_], callback: Callable):
        bstack1l11lll111l_opy_ = TestFramework.bstack1l11lll1l11_opy_(bstack1llllll1l1l_opy_)
        TestFramework.logger.debug(bstack1l1_opy_ (u"ࠥࡷࡪࡺ࡟ࡩࡱࡲ࡯ࡤࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࡪࡲࡳࡰࡥࡲࡦࡩ࡬ࡷࡹࡸࡹࡠ࡭ࡨࡽࡂࢁࡽࠣᕐ").format(bstack1l11lll111l_opy_))
        if not bstack1l11lll111l_opy_ in TestFramework.bstack1l1111l1111_opy_:
            TestFramework.bstack1l1111l1111_opy_[bstack1l11lll111l_opy_] = []
        TestFramework.bstack1l1111l1111_opy_[bstack1l11lll111l_opy_].append(callback)
    @staticmethod
    def bstack1l1ll1lllll_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡶ࡬ࡲࡸࠨᕑ"):
            return klass.__qualname__
        return module + bstack1l1_opy_ (u"ࠧ࠴ࠢᕒ") + klass.__qualname__
    @staticmethod
    def bstack1l1llll1l1l_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}