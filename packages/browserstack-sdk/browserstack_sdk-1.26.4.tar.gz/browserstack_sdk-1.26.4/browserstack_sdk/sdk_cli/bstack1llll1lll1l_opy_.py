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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1111l111ll_opy_ import bstack1111l11l11_opy_
class bstack1ll1llllll1_opy_(abc.ABC):
    bin_session_id: str
    bstack1111l111ll_opy_: bstack1111l11l11_opy_
    def __init__(self):
        self.bstack1ll1lll1ll1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1111l111ll_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1llll1l1l1l_opy_(self):
        return (self.bstack1ll1lll1ll1_opy_ != None and self.bin_session_id != None and self.bstack1111l111ll_opy_ != None)
    def configure(self, bstack1ll1lll1ll1_opy_, config, bin_session_id: str, bstack1111l111ll_opy_: bstack1111l11l11_opy_):
        self.bstack1ll1lll1ll1_opy_ = bstack1ll1lll1ll1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1111l111ll_opy_ = bstack1111l111ll_opy_
        if self.bin_session_id:
            self.logger.debug(bstack1ll_opy_ (u"ࠤ࡞ࡿ࡮ࡪࠨࡴࡧ࡯ࡪ࠮ࢃ࡝ࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡨࡨࠥࡳ࡯ࡥࡷ࡯ࡩࠥࢁࡳࡦ࡮ࡩ࠲ࡤࡥࡣ࡭ࡣࡶࡷࡤࡥ࠮ࡠࡡࡱࡥࡲ࡫࡟ࡠࡿ࠽ࠤࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࡂࠨᇁ") + str(self.bin_session_id) + bstack1ll_opy_ (u"ࠥࠦᇂ"))
    def bstack1ll1l1l1lll_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack1ll_opy_ (u"ࠦࡧ࡯࡮ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠥࡩࡡ࡯ࡰࡲࡸࠥࡨࡥࠡࡐࡲࡲࡪࠨᇃ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False