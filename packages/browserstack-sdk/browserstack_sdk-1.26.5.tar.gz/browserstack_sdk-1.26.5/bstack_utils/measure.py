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
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1l11lllll_opy_ import get_logger
from bstack_utils.bstack11l11l111l_opy_ import bstack1ll1llll111_opy_
bstack11l11l111l_opy_ = bstack1ll1llll111_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack1l11lll11l_opy_: Optional[str] = None):
    bstack1l1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡉ࡫ࡣࡰࡴࡤࡸࡴࡸࠠࡵࡱࠣࡰࡴ࡭ࠠࡵࡪࡨࠤࡸࡺࡡࡳࡶࠣࡸ࡮ࡳࡥࠡࡱࡩࠤࡦࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡧࡻࡩࡨࡻࡴࡪࡱࡱࠎࠥࠦࠠࠡࡣ࡯ࡳࡳ࡭ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࠤࡳࡧ࡭ࡦࠢࡤࡲࡩࠦࡳࡵࡣࡪࡩ࠳ࠐࠠࠡࠢࠣࠦࠧࠨ᳝")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll11lll111_opy_: str = bstack11l11l111l_opy_.bstack11l1ll11111_opy_(label)
            start_mark: str = label + bstack1l1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸ᳞ࠧ")
            end_mark: str = label + bstack1l1_opy_ (u"ࠨ࠺ࡦࡰࡧ᳟ࠦ")
            result = None
            try:
                if stage.value == STAGE.bstack11llll1l_opy_.value:
                    bstack11l11l111l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack11l11l111l_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack1l11lll11l_opy_)
                elif stage.value == STAGE.bstack1111lll11_opy_.value:
                    start_mark: str = bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢ᳠")
                    end_mark: str = bstack1ll11lll111_opy_ + bstack1l1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨ᳡")
                    bstack11l11l111l_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack11l11l111l_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack1l11lll11l_opy_)
            except Exception as e:
                bstack11l11l111l_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack1l11lll11l_opy_)
            return result
        return wrapper
    return decorator