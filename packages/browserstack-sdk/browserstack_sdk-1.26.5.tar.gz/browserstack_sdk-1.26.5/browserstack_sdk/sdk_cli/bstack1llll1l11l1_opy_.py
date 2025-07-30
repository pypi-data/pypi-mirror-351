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
import json
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1lll1lll111_opy_
from browserstack_sdk.sdk_cli.bstack1111111l11_opy_ import (
    bstack11111l11ll_opy_,
    bstack111111ll1l_opy_,
    bstack11111l1l1l_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1l11_opy_ import bstack1lll1l1ll11_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1l1l1l1l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack11l11l111l_opy_ import bstack1ll1llll111_opy_
class bstack1llll1lllll_opy_(bstack1lll1lll111_opy_):
    bstack1l1l11ll111_opy_ = bstack1l1_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣ࡮ࡴࡩࡵࠤዙ")
    bstack1l1l11l1111_opy_ = bstack1l1_opy_ (u"ࠥࡶࡪ࡭ࡩࡴࡶࡨࡶࡤࡹࡴࡢࡴࡷࠦዚ")
    bstack1l1l11lll1l_opy_ = bstack1l1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡳࡵࡱࡳࠦዛ")
    def __init__(self, bstack1lllll1llll_opy_):
        super().__init__()
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.bstack1llllll11ll_opy_, bstack111111ll1l_opy_.PRE), self.bstack1l1l111ll1l_opy_)
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.bstack1llllll1111_opy_, bstack111111ll1l_opy_.PRE), self.bstack1ll11l1l111_opy_)
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.bstack1llllll1111_opy_, bstack111111ll1l_opy_.POST), self.bstack1l1l111llll_opy_)
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.bstack1llllll1111_opy_, bstack111111ll1l_opy_.POST), self.bstack1l1l11l1l11_opy_)
        bstack1lll1l1ll11_opy_.bstack1ll11ll1l1l_opy_((bstack11111l11ll_opy_.QUIT, bstack111111ll1l_opy_.POST), self.bstack1l1l1111ll1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l111ll1l_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1l1_opy_ (u"ࠧࡥ࡟ࡪࡰ࡬ࡸࡤࡥࠢዜ"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack1l1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤዝ")), str):
                    url = kwargs.get(bstack1l1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥዞ"))
                elif hasattr(kwargs.get(bstack1l1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦዟ")), bstack1l1_opy_ (u"ࠩࡢࡧࡱ࡯ࡥ࡯ࡶࡢࡧࡴࡴࡦࡪࡩࠪዠ")):
                    url = kwargs.get(bstack1l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨዡ"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack1l1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢዢ"))._url
            except Exception as e:
                url = bstack1l1_opy_ (u"ࠬ࠭ዣ")
                self.logger.error(bstack1l1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡻࡲ࡭ࠢࡩࡶࡴࡳࠠࡥࡴ࡬ࡺࡪࡸ࠺ࠡࡽࢀࠦዤ").format(e))
            self.logger.info(bstack1l1_opy_ (u"ࠢࡓࡧࡰࡳࡹ࡫ࠠࡔࡧࡵࡺࡪࡸࠠࡂࡦࡧࡶࡪࡹࡳࠡࡤࡨ࡭ࡳ࡭ࠠࡱࡣࡶࡷࡪࡪࠠࡢࡵࠣ࠾ࠥࢁࡽࠣዥ").format(str(url)))
            self.bstack1l1l111l111_opy_(instance, url, f, kwargs)
            self.logger.info(bstack1l1_opy_ (u"ࠣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡢ࡭ࡳࡪࡥࡹ࠿ࡾࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࢁ࠿ࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࢀࡱࡷࡢࡴࡪࡷࢂࠨዦ").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1ll11l1l111_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1llllll1lll_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11ll111_opy_, False):
            return
        if not f.bstack1111111ll1_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_):
            return
        platform_index = f.bstack1llllll1lll_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_)
        if f.bstack1ll1l1lllll_opy_(method_name, *args) and len(args) > 1:
            bstack11111ll11_opy_ = datetime.now()
            hub_url = bstack1lll1l1ll11_opy_.hub_url(driver)
            self.logger.warning(bstack1l1_opy_ (u"ࠤ࡫ࡹࡧࡥࡵࡳ࡮ࡀࠦዧ") + str(hub_url) + bstack1l1_opy_ (u"ࠥࠦየ"))
            bstack1l1l111l1ll_opy_ = args[1][bstack1l1_opy_ (u"ࠦࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥዩ")] if isinstance(args[1], dict) and bstack1l1_opy_ (u"ࠧࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦዪ") in args[1] else None
            bstack1l1l11lll11_opy_ = bstack1l1_opy_ (u"ࠨࡡ࡭ࡹࡤࡽࡸࡓࡡࡵࡥ࡫ࠦያ")
            if isinstance(bstack1l1l111l1ll_opy_, dict):
                bstack11111ll11_opy_ = datetime.now()
                r = self.bstack1l1l1111l1l_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1ll1l1l1ll_opy_(bstack1l1_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡪࡰ࡬ࡸࠧዬ"), datetime.now() - bstack11111ll11_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack1l1_opy_ (u"ࠣࡵࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧ࠻ࠢࠥይ") + str(r) + bstack1l1_opy_ (u"ࠤࠥዮ"))
                        return
                    if r.hub_url:
                        f.bstack1l1l11111ll_opy_(instance, driver, r.hub_url)
                        f.bstack1llllllll11_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11ll111_opy_, True)
                except Exception as e:
                    self.logger.error(bstack1l1_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤዯ"), e)
    def bstack1l1l111llll_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1lll1l1ll11_opy_.session_id(driver)
            if session_id:
                bstack1l1l1111l11_opy_ = bstack1l1_opy_ (u"ࠦࢀࢃ࠺ࡴࡶࡤࡶࡹࠨደ").format(session_id)
                bstack1ll1llll111_opy_.mark(bstack1l1l1111l11_opy_)
    def bstack1l1l11l1l11_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llllll1lll_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11l1111_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1lll1l1ll11_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack1l1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡲࡤࡶࡸ࡫ࠠࡩࡷࡥࡣࡺࡸ࡬࠾ࠤዱ") + str(hub_url) + bstack1l1_opy_ (u"ࠨࠢዲ"))
            return
        framework_session_id = bstack1lll1l1ll11_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack1l1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥ࠿ࠥዳ") + str(framework_session_id) + bstack1l1_opy_ (u"ࠣࠤዴ"))
            return
        if bstack1lll1l1ll11_opy_.bstack1l1l11111l1_opy_(*args) == bstack1lll1l1ll11_opy_.bstack1l1l11l1ll1_opy_:
            bstack1l1l11l11l1_opy_ = bstack1l1_opy_ (u"ࠤࡾࢁ࠿࡫࡮ࡥࠤድ").format(framework_session_id)
            bstack1l1l1111l11_opy_ = bstack1l1_opy_ (u"ࠥࡿࢂࡀࡳࡵࡣࡵࡸࠧዶ").format(framework_session_id)
            bstack1ll1llll111_opy_.end(
                label=bstack1l1_opy_ (u"ࠦࡸࡪ࡫࠻ࡦࡵ࡭ࡻ࡫ࡲ࠻ࡲࡲࡷࡹ࠳ࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡣࡷ࡭ࡴࡴࠢዷ"),
                start=bstack1l1l1111l11_opy_,
                end=bstack1l1l11l11l1_opy_,
                status=True,
                failure=None
            )
            bstack11111ll11_opy_ = datetime.now()
            r = self.bstack1l1l111l1l1_opy_(
                ref,
                f.bstack1llllll1lll_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1ll1l1l1ll_opy_(bstack1l1_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡶࡪ࡭ࡩࡴࡶࡨࡶࡤࡹࡴࡢࡴࡷࠦዸ"), datetime.now() - bstack11111ll11_opy_)
            f.bstack1llllllll11_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11l1111_opy_, r.success)
    def bstack1l1l1111ll1_opy_(
        self,
        f: bstack1lll1l1ll11_opy_,
        driver: object,
        exec: Tuple[bstack11111l1l1l_opy_, str],
        bstack1llllll1l1l_opy_: Tuple[bstack11111l11ll_opy_, bstack111111ll1l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1llllll1lll_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11lll1l_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1lll1l1ll11_opy_.session_id(driver)
        hub_url = bstack1lll1l1ll11_opy_.hub_url(driver)
        bstack11111ll11_opy_ = datetime.now()
        r = self.bstack1l1l11l1lll_opy_(
            ref,
            f.bstack1llllll1lll_opy_(instance, bstack1lll1l1ll11_opy_.bstack1ll1l11ll1l_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1ll1l1l1ll_opy_(bstack1l1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡳࡵࡱࡳࠦዹ"), datetime.now() - bstack11111ll11_opy_)
        f.bstack1llllllll11_opy_(instance, bstack1llll1lllll_opy_.bstack1l1l11lll1l_opy_, r.success)
    @measure(event_name=EVENTS.bstack1l11ll1ll1_opy_, stage=STAGE.bstack1111lll11_opy_)
    def bstack1l1l1lll11l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack1l1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡺࡩࡧࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡪࡶ࠽ࠤࠧዺ") + str(req) + bstack1l1_opy_ (u"ࠣࠤዻ"))
        try:
            r = self.bstack1lll1l111ll_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1l1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࡷࡺࡩࡣࡦࡵࡶࡁࠧዼ") + str(r.success) + bstack1l1_opy_ (u"ࠥࠦዽ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤዾ") + str(e) + bstack1l1_opy_ (u"ࠧࠨዿ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1l111ll11_opy_, stage=STAGE.bstack1111lll11_opy_)
    def bstack1l1l1111l1l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll1l111111_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack1l1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠ࡫ࡱ࡭ࡹࡀࠠࠣጀ") + str(req) + bstack1l1_opy_ (u"ࠢࠣጁ"))
        try:
            r = self.bstack1lll1l111ll_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack1l1_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࡶࡹࡨࡩࡥࡴࡵࡀࠦጂ") + str(r.success) + bstack1l1_opy_ (u"ࠤࠥጃ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣጄ") + str(e) + bstack1l1_opy_ (u"ࠦࠧጅ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1l11ll11l_opy_, stage=STAGE.bstack1111lll11_opy_)
    def bstack1l1l111l1l1_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll1l111111_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1l1_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࡀࠠࠣጆ") + str(req) + bstack1l1_opy_ (u"ࠨࠢጇ"))
        try:
            r = self.bstack1lll1l111ll_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack1l1_opy_ (u"ࠢࡳࡧࡦࡩ࡮ࡼࡥࡥࠢࡩࡶࡴࡳࠠࡴࡧࡵࡺࡪࡸ࠺ࠡࠤገ") + str(r) + bstack1l1_opy_ (u"ࠣࠤጉ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢጊ") + str(e) + bstack1l1_opy_ (u"ࠥࠦጋ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1l11l11ll_opy_, stage=STAGE.bstack1111lll11_opy_)
    def bstack1l1l11l1lll_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll1l111111_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1l1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡳࡵࡱࡳ࠾ࠥࠨጌ") + str(req) + bstack1l1_opy_ (u"ࠧࠨግ"))
        try:
            r = self.bstack1lll1l111ll_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack1l1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣጎ") + str(r) + bstack1l1_opy_ (u"ࠢࠣጏ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1l1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨጐ") + str(e) + bstack1l1_opy_ (u"ࠤࠥ጑"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l1l11l11l_opy_, stage=STAGE.bstack1111lll11_opy_)
    def bstack1l1l111l111_opy_(self, instance: bstack11111l1l1l_opy_, url: str, f: bstack1lll1l1ll11_opy_, kwargs):
        bstack1l1l11l111l_opy_ = version.parse(f.framework_version)
        bstack1l1l111lll1_opy_ = kwargs.get(bstack1l1_opy_ (u"ࠥࡳࡵࡺࡩࡰࡰࡶࠦጒ"))
        bstack1l1l1111lll_opy_ = kwargs.get(bstack1l1_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦጓ"))
        bstack1l1l1ll1ll1_opy_ = {}
        bstack1l1l11l1l1l_opy_ = {}
        bstack1l1l11ll1l1_opy_ = None
        bstack1l1l111l11l_opy_ = {}
        if bstack1l1l1111lll_opy_ is not None or bstack1l1l111lll1_opy_ is not None: # check top level caps
            if bstack1l1l1111lll_opy_ is not None:
                bstack1l1l111l11l_opy_[bstack1l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬጔ")] = bstack1l1l1111lll_opy_
            if bstack1l1l111lll1_opy_ is not None and callable(getattr(bstack1l1l111lll1_opy_, bstack1l1_opy_ (u"ࠨࡴࡰࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣጕ"))):
                bstack1l1l111l11l_opy_[bstack1l1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࡠࡣࡶࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪ጖")] = bstack1l1l111lll1_opy_.to_capabilities()
        response = self.bstack1l1l1lll11l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l1l111l11l_opy_).encode(bstack1l1_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢ጗")))
        if response is not None and response.capabilities:
            bstack1l1l1ll1ll1_opy_ = json.loads(response.capabilities.decode(bstack1l1_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣጘ")))
            if not bstack1l1l1ll1ll1_opy_: # empty caps bstack1l1l1lll1ll_opy_ bstack1l1ll1111l1_opy_ bstack1l1l1ll111l_opy_ bstack1lll1llll1l_opy_ or error in processing
                return
            bstack1l1l11ll1l1_opy_ = f.bstack1lllll11l11_opy_[bstack1l1_opy_ (u"ࠥࡧࡷ࡫ࡡࡵࡧࡢࡳࡵࡺࡩࡰࡰࡶࡣ࡫ࡸ࡯࡮ࡡࡦࡥࡵࡹࠢጙ")](bstack1l1l1ll1ll1_opy_)
        if bstack1l1l111lll1_opy_ is not None and bstack1l1l11l111l_opy_ >= version.parse(bstack1l1_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪጚ")):
            bstack1l1l11l1l1l_opy_ = None
        if (
                not bstack1l1l111lll1_opy_ and not bstack1l1l1111lll_opy_
        ) or (
                bstack1l1l11l111l_opy_ < version.parse(bstack1l1_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫጛ"))
        ):
            bstack1l1l11l1l1l_opy_ = {}
            bstack1l1l11l1l1l_opy_.update(bstack1l1l1ll1ll1_opy_)
        self.logger.info(bstack1l1l1l1l1_opy_)
        if os.environ.get(bstack1l1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠤጜ")).lower().__eq__(bstack1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧጝ")):
            kwargs.update(
                {
                    bstack1l1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦጞ"): f.bstack1l1l11ll1ll_opy_,
                }
            )
        if bstack1l1l11l111l_opy_ >= version.parse(bstack1l1_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩጟ")):
            if bstack1l1l1111lll_opy_ is not None:
                del kwargs[bstack1l1_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥጠ")]
            kwargs.update(
                {
                    bstack1l1_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧጡ"): bstack1l1l11ll1l1_opy_,
                    bstack1l1_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤጢ"): True,
                    bstack1l1_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨጣ"): None,
                }
            )
        elif bstack1l1l11l111l_opy_ >= version.parse(bstack1l1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭ጤ")):
            kwargs.update(
                {
                    bstack1l1_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣጥ"): bstack1l1l11l1l1l_opy_,
                    bstack1l1_opy_ (u"ࠤࡲࡴࡹ࡯࡯࡯ࡵࠥጦ"): bstack1l1l11ll1l1_opy_,
                    bstack1l1_opy_ (u"ࠥ࡯ࡪ࡫ࡰࡠࡣ࡯࡭ࡻ࡫ࠢጧ"): True,
                    bstack1l1_opy_ (u"ࠦ࡫࡯࡬ࡦࡡࡧࡩࡹ࡫ࡣࡵࡱࡵࠦጨ"): None,
                }
            )
        elif bstack1l1l11l111l_opy_ >= version.parse(bstack1l1_opy_ (u"ࠬ࠸࠮࠶࠵࠱࠴ࠬጩ")):
            kwargs.update(
                {
                    bstack1l1_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨጪ"): bstack1l1l11l1l1l_opy_,
                    bstack1l1_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦጫ"): True,
                    bstack1l1_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣጬ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack1l1_opy_ (u"ࠤࡧࡩࡸ࡯ࡲࡦࡦࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠤጭ"): bstack1l1l11l1l1l_opy_,
                    bstack1l1_opy_ (u"ࠥ࡯ࡪ࡫ࡰࡠࡣ࡯࡭ࡻ࡫ࠢጮ"): True,
                    bstack1l1_opy_ (u"ࠦ࡫࡯࡬ࡦࡡࡧࡩࡹ࡫ࡣࡵࡱࡵࠦጯ"): None,
                }
            )