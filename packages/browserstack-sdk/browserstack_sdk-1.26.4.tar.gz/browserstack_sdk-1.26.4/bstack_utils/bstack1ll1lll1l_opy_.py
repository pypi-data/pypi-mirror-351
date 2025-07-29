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
from filelock import FileLock
import json
import os
import time
import uuid
import logging
from typing import Dict, List, Optional
from bstack_utils.bstack111ll11ll_opy_ import get_logger
logger = get_logger(__name__)
bstack111l11ll111_opy_: Dict[str, float] = {}
bstack111l11l1lll_opy_: List = []
bstack111l11l1ll1_opy_ = 5
bstack11ll1l111l_opy_ = os.path.join(os.getcwd(), bstack1ll_opy_ (u"ࠫࡱࡵࡧࠨᶶ"), bstack1ll_opy_ (u"ࠬࡱࡥࡺ࠯ࡰࡩࡹࡸࡩࡤࡵ࠱࡮ࡸࡵ࡮ࠨᶷ"))
logging.getLogger(bstack1ll_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠨᶸ")).setLevel(logging.WARNING)
lock = FileLock(bstack11ll1l111l_opy_+bstack1ll_opy_ (u"ࠢ࠯࡮ࡲࡧࡰࠨᶹ"))
class bstack111l11l1l11_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    cli: Optional[bool]
    def __init__(self, duration: float, name: str, start_time: float, bstack111l11ll1ll_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None, cli: Optional[bool] = False) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack111l11ll1ll_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack1ll_opy_ (u"ࠣ࡯ࡨࡥࡸࡻࡲࡦࠤᶺ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
        self.cli = cli
class bstack1lll11l1lll_opy_:
    global bstack111l11ll111_opy_
    @staticmethod
    def bstack1ll1ll11111_opy_(key: str):
        bstack1ll11lll1ll_opy_ = bstack1lll11l1lll_opy_.bstack11ll11l111l_opy_(key)
        bstack1lll11l1lll_opy_.mark(bstack1ll11lll1ll_opy_+bstack1ll_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᶻ"))
        return bstack1ll11lll1ll_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack111l11ll111_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠥࡉࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᶼ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str] = None, hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack1lll11l1lll_opy_.mark(end)
            bstack1lll11l1lll_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦ࡫ࡦࡻࠣࡱࡪࡺࡲࡪࡥࡶ࠾ࠥࢁࡽࠣᶽ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack111l11ll111_opy_ or end not in bstack111l11ll111_opy_:
                logger.debug(bstack1ll_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡶࡤࡶࡹࠦ࡫ࡦࡻࠣࡻ࡮ࡺࡨࠡࡸࡤࡰࡺ࡫ࠠࡼࡿࠣࡳࡷࠦࡥ࡯ࡦࠣ࡯ࡪࡿࠠࡸ࡫ࡷ࡬ࠥࡼࡡ࡭ࡷࡨࠤࢀࢃࠢᶾ").format(start,end))
                return
            duration: float = bstack111l11ll111_opy_[end] - bstack111l11ll111_opy_[start]
            bstack111l11lll11_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡉࡏࡃࡕ࡝ࡤࡏࡓࡠࡔࡘࡒࡓࡏࡎࡈࠤᶿ"), bstack1ll_opy_ (u"ࠢࡧࡣ࡯ࡷࡪࠨ᷀")).lower() == bstack1ll_opy_ (u"ࠣࡶࡵࡹࡪࠨ᷁")
            bstack111l11lll1l_opy_: bstack111l11l1l11_opy_ = bstack111l11l1l11_opy_(duration, label, bstack111l11ll111_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack1ll_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤ᷂"), 0), command, test_name, hook_type, bstack111l11lll11_opy_)
            del bstack111l11ll111_opy_[start]
            del bstack111l11ll111_opy_[end]
            bstack1lll11l1lll_opy_.bstack111l11l1l1l_opy_(bstack111l11lll1l_opy_)
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡨࡥࡸࡻࡲࡪࡰࡪࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴ࠼ࠣࡿࢂࠨ᷃").format(e))
    @staticmethod
    def bstack111l11l1l1l_opy_(bstack111l11lll1l_opy_):
        os.makedirs(os.path.dirname(bstack11ll1l111l_opy_)) if not os.path.exists(os.path.dirname(bstack11ll1l111l_opy_)) else None
        bstack1lll11l1lll_opy_.bstack111l11ll11l_opy_()
        try:
            with lock:
                with open(bstack11ll1l111l_opy_, bstack1ll_opy_ (u"ࠦࡷ࠱ࠢ᷄"), encoding=bstack1ll_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦ᷅")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack111l11lll1l_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError as bstack111l11ll1l1_opy_:
            logger.debug(bstack1ll_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࡳࡵࡴࠡࡨࡲࡹࡳࡪࠠࡼࡿࠥ᷆").format(bstack111l11ll1l1_opy_))
            with lock:
                with open(bstack11ll1l111l_opy_, bstack1ll_opy_ (u"ࠢࡸࠤ᷇"), encoding=bstack1ll_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢ᷈")) as file:
                    data = [bstack111l11lll1l_opy_.__dict__]
                    json.dump(data, file, indent=4)
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡰ࡫ࡹࠡ࡯ࡨࡸࡷ࡯ࡣࡴࠢࡤࡴࡵ࡫࡮ࡥࠢࡾࢁࠧ᷉").format(str(e)))
        finally:
            if os.path.exists(bstack11ll1l111l_opy_+bstack1ll_opy_ (u"ࠥ࠲ࡱࡵࡣ࡬ࠤ᷊")):
                os.remove(bstack11ll1l111l_opy_+bstack1ll_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥ᷋"))
    @staticmethod
    def bstack111l11ll11l_opy_():
        attempt = 0
        while (attempt < bstack111l11l1ll1_opy_):
            attempt += 1
            if os.path.exists(bstack11ll1l111l_opy_+bstack1ll_opy_ (u"ࠧ࠴࡬ࡰࡥ࡮ࠦ᷌")):
                time.sleep(0.5)
            else:
                break
    @staticmethod
    def bstack11ll11l111l_opy_(label: str) -> str:
        try:
            return bstack1ll_opy_ (u"ࠨࡻࡾ࠼ࡾࢁࠧ᷍").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠢࡆࡴࡵࡳࡷࡀࠠࡼࡿ᷎ࠥ").format(e))