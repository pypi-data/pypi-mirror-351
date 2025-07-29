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
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111llllll1_opy_ import bstack11l1111111_opy_, bstack111lll111l_opy_
from bstack_utils.bstack111lll1ll1_opy_ import bstack11llllll1l_opy_
from bstack_utils.helper import bstack11ll11l1_opy_, bstack11ll111lll_opy_, Result
from bstack_utils.bstack111llll1l1_opy_ import bstack1l111111_opy_
from bstack_utils.capture import bstack111lll1111_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack11l11111l_opy_:
    def __init__(self):
        self.bstack111llll1ll_opy_ = bstack111lll1111_opy_(self.bstack11l1111l11_opy_)
        self.tests = {}
    @staticmethod
    def bstack11l1111l11_opy_(log):
        if not (log[bstack1ll_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭໥")] and log[bstack1ll_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ໦")].strip()):
            return
        active = bstack11llllll1l_opy_.bstack111lll1lll_opy_()
        log = {
            bstack1ll_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭໧"): log[bstack1ll_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ໨")],
            bstack1ll_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ໩"): bstack11ll111lll_opy_(),
            bstack1ll_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ໪"): log[bstack1ll_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ໫")],
        }
        if active:
            if active[bstack1ll_opy_ (u"ࠬࡺࡹࡱࡧࠪ໬")] == bstack1ll_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ໭"):
                log[bstack1ll_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ໮")] = active[bstack1ll_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ໯")]
            elif active[bstack1ll_opy_ (u"ࠩࡷࡽࡵ࡫ࠧ໰")] == bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࠨ໱"):
                log[bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ໲")] = active[bstack1ll_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ໳")]
        bstack1l111111_opy_.bstack11l111lll1_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111llll1ll_opy_.start()
        driver = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬ໴"), None)
        bstack111llllll1_opy_ = bstack111lll111l_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack11ll111lll_opy_(),
            file_path=attrs.feature.filename,
            result=bstack1ll_opy_ (u"ࠢࡱࡧࡱࡨ࡮ࡴࡧࠣ໵"),
            framework=bstack1ll_opy_ (u"ࠨࡄࡨ࡬ࡦࡼࡥࠨ໶"),
            scope=[attrs.feature.name],
            bstack11l1111l1l_opy_=bstack1l111111_opy_.bstack111lll11l1_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬ໷")] = bstack111llllll1_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack1l111111_opy_.bstack11l111111l_opy_(bstack1ll_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫ໸"), bstack111llllll1_opy_)
    def end_test(self, attrs):
        bstack11l1111lll_opy_ = {
            bstack1ll_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ໹"): attrs.feature.name,
            bstack1ll_opy_ (u"ࠧࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥ໺"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111llllll1_opy_ = self.tests[current_test_uuid][bstack1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ໻")]
        meta = {
            bstack1ll_opy_ (u"ࠢࡧࡧࡤࡸࡺࡸࡥࠣ໼"): bstack11l1111lll_opy_,
            bstack1ll_opy_ (u"ࠣࡵࡷࡩࡵࡹࠢ໽"): bstack111llllll1_opy_.meta.get(bstack1ll_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ໾"), []),
            bstack1ll_opy_ (u"ࠥࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ໿"): {
                bstack1ll_opy_ (u"ࠦࡳࡧ࡭ࡦࠤༀ"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111llllll1_opy_.bstack111lllllll_opy_(meta)
        bstack111llllll1_opy_.bstack11l11111ll_opy_(bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪ༁"), []))
        bstack111lll11ll_opy_, exception = self._111ll1llll_opy_(attrs)
        bstack11l1111ll1_opy_ = Result(result=attrs.status.name, exception=exception, bstack111lllll1l_opy_=[bstack111lll11ll_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩ༂")].stop(time=bstack11ll111lll_opy_(), duration=int(attrs.duration)*1000, result=bstack11l1111ll1_opy_)
        bstack1l111111_opy_.bstack11l111111l_opy_(bstack1ll_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩ༃"), self.tests[threading.current_thread().current_test_uuid][bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ༄")])
    def bstack11l1l11l1l_opy_(self, attrs):
        bstack11l11111l1_opy_ = {
            bstack1ll_opy_ (u"ࠩ࡬ࡨࠬ༅"): uuid4().__str__(),
            bstack1ll_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫ༆"): attrs.keyword,
            bstack1ll_opy_ (u"ࠫࡸࡺࡥࡱࡡࡤࡶ࡬ࡻ࡭ࡦࡰࡷࠫ༇"): [],
            bstack1ll_opy_ (u"ࠬࡺࡥࡹࡶࠪ༈"): attrs.name,
            bstack1ll_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ༉"): bstack11ll111lll_opy_(),
            bstack1ll_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ༊"): bstack1ll_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ་"),
            bstack1ll_opy_ (u"ࠩࡧࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧ༌"): bstack1ll_opy_ (u"ࠪࠫ།")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧ༎")].add_step(bstack11l11111l1_opy_)
        threading.current_thread().current_step_uuid = bstack11l11111l1_opy_[bstack1ll_opy_ (u"ࠬ࡯ࡤࠨ༏")]
    def bstack1l1ll111l_opy_(self, attrs):
        current_test_id = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪ༐"), None)
        current_step_uuid = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡷࡩࡵࡥࡵࡶ࡫ࡧࠫ༑"), None)
        bstack111lll11ll_opy_, exception = self._111ll1llll_opy_(attrs)
        bstack11l1111ll1_opy_ = Result(result=attrs.status.name, exception=exception, bstack111lllll1l_opy_=[bstack111lll11ll_opy_])
        self.tests[current_test_id][bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ༒")].bstack111llll11l_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack11l1111ll1_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack11l1ll1l1l_opy_(self, name, attrs):
        try:
            bstack111llll111_opy_ = uuid4().__str__()
            self.tests[bstack111llll111_opy_] = {}
            self.bstack111llll1ll_opy_.start()
            scopes = []
            driver = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ༓"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack1ll_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࠨ༔")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111llll111_opy_)
            if name in [bstack1ll_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣ༕"), bstack1ll_opy_ (u"ࠧࡧࡦࡵࡧࡵࡣࡦࡲ࡬ࠣ༖")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡦࡦࡣࡷࡹࡷ࡫ࠢ༗"), bstack1ll_opy_ (u"ࠢࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫༘ࠢ")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack1ll_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦ༙ࠩ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack11l1111111_opy_(
                name=name,
                uuid=bstack111llll111_opy_,
                started_at=bstack11ll111lll_opy_(),
                file_path=file_path,
                framework=bstack1ll_opy_ (u"ࠤࡅࡩ࡭ࡧࡶࡦࠤ༚"),
                bstack11l1111l1l_opy_=bstack1l111111_opy_.bstack111lll11l1_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack1ll_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦ༛"),
                hook_type=name
            )
            self.tests[bstack111llll111_opy_][bstack1ll_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠢ༜")] = hook_data
            current_test_id = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠧࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠤ༝"), None)
            if current_test_id:
                hook_data.bstack111lll1l11_opy_(current_test_id)
            if name == bstack1ll_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥ༞"):
                threading.current_thread().before_all_hook_uuid = bstack111llll111_opy_
            threading.current_thread().current_hook_uuid = bstack111llll111_opy_
            bstack1l111111_opy_.bstack11l111111l_opy_(bstack1ll_opy_ (u"ࠢࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠣ༟"), hook_data)
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡰࡥࡦࡹࡷࡸࡥࡥࠢ࡬ࡲࠥࡹࡴࡢࡴࡷࠤ࡭ࡵ࡯࡬ࠢࡨࡺࡪࡴࡴࡴ࠮ࠣ࡬ࡴࡵ࡫ࠡࡰࡤࡱࡪࡀࠠࠦࡵ࠯ࠤࡪࡸࡲࡰࡴ࠽ࠤࠪࡹࠢ༠"), name, e)
    def bstack1lll1llll1_opy_(self, attrs):
        bstack111lll1l1l_opy_ = bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭༡"), None)
        hook_data = self.tests[bstack111lll1l1l_opy_][bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭༢")]
        status = bstack1ll_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ༣")
        exception = None
        bstack111lll11ll_opy_ = None
        if hook_data.name == bstack1ll_opy_ (u"ࠧࡧࡦࡵࡧࡵࡣࡦࡲ࡬ࠣ༤"):
            self.bstack111llll1ll_opy_.reset()
            bstack111lllll11_opy_ = self.tests[bstack11ll11l1_opy_(threading.current_thread(), bstack1ll_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭༥"), None)][bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣࠪ༦")].result.result
            if bstack111lllll11_opy_ == bstack1ll_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ༧"):
                if attrs.hook_failures == 1:
                    status = bstack1ll_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ༨")
                elif attrs.hook_failures == 2:
                    status = bstack1ll_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥ༩")
            elif attrs.aborted:
                status = bstack1ll_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ༪")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack1ll_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠩ༫") and attrs.hook_failures == 1:
                status = bstack1ll_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ༬")
            elif hasattr(attrs, bstack1ll_opy_ (u"ࠧࡦࡴࡵࡳࡷࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠧ༭")) and attrs.error_message:
                status = bstack1ll_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ༮")
            bstack111lll11ll_opy_, exception = self._111ll1llll_opy_(attrs)
        bstack11l1111ll1_opy_ = Result(result=status, exception=exception, bstack111lllll1l_opy_=[bstack111lll11ll_opy_])
        hook_data.stop(time=bstack11ll111lll_opy_(), duration=0, result=bstack11l1111ll1_opy_)
        bstack1l111111_opy_.bstack11l111111l_opy_(bstack1ll_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ༯"), self.tests[bstack111lll1l1l_opy_][bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭༰")])
        threading.current_thread().current_hook_uuid = None
    def _111ll1llll_opy_(self, attrs):
        try:
            import traceback
            bstack11lllll1l_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111lll11ll_opy_ = bstack11lllll1l_opy_[-1] if bstack11lllll1l_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack1ll_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡴࡨࡨࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡩࡵࡴࡶࡲࡱࠥࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࠣ༱"))
            bstack111lll11ll_opy_ = None
            exception = None
        return bstack111lll11ll_opy_, exception