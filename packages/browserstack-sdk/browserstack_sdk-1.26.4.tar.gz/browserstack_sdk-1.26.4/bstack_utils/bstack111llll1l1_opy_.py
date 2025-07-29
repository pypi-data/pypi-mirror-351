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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11l1ll1l11l_opy_, bstack11ll111111l_opy_, bstack11ll1l1ll1_opy_, bstack111l11ll11_opy_, bstack111ll1l1l11_opy_, bstack111llllll11_opy_, bstack11l11l1l111_opy_, bstack11ll111lll_opy_, bstack11ll11l1_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1111lllll11_opy_ import bstack1111llll1ll_opy_
import bstack_utils.bstack11l1ll111l_opy_ as bstack11l1lllll1_opy_
from bstack_utils.bstack111lll1ll1_opy_ import bstack11llllll1l_opy_
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from bstack_utils.bstack1l11l1l1l_opy_ import bstack1l11l1l1l_opy_
from bstack_utils.bstack111llllll1_opy_ import bstack111l1l111l_opy_
bstack1111l11l1l1_opy_ = bstack1ll_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡣࡰ࡮࡯ࡩࡨࡺ࡯ࡳ࠯ࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠬẳ")
logger = logging.getLogger(__name__)
class bstack1l111111_opy_:
    bstack1111lllll11_opy_ = None
    bs_config = None
    bstack1l11111111_opy_ = None
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    @measure(event_name=EVENTS.bstack11l11ll1ll1_opy_, stage=STAGE.bstack1llll11lll_opy_)
    def launch(cls, bs_config, bstack1l11111111_opy_):
        cls.bs_config = bs_config
        cls.bstack1l11111111_opy_ = bstack1l11111111_opy_
        try:
            cls.bstack1111l1111l1_opy_()
            bstack11ll111ll11_opy_ = bstack11l1ll1l11l_opy_(bs_config)
            bstack11l1ll1llll_opy_ = bstack11ll111111l_opy_(bs_config)
            data = bstack11l1lllll1_opy_.bstack1111l11111l_opy_(bs_config, bstack1l11111111_opy_)
            config = {
                bstack1ll_opy_ (u"࠭ࡡࡶࡶ࡫ࠫẴ"): (bstack11ll111ll11_opy_, bstack11l1ll1llll_opy_),
                bstack1ll_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨẵ"): cls.default_headers()
            }
            response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠨࡒࡒࡗ࡙࠭Ặ"), cls.request_url(bstack1ll_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠳࠱ࡥࡹ࡮ࡲࡤࡴࠩặ")), data, config)
            if response.status_code != 200:
                bstack1l1l111l_opy_ = response.json()
                if bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫẸ")] == False:
                    cls.bstack1111l1l1l11_opy_(bstack1l1l111l_opy_)
                    return
                cls.bstack11111lll1l1_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫẹ")])
                cls.bstack1111l111l1l_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬẺ")])
                return None
            bstack1111l11lll1_opy_ = cls.bstack1111l111ll1_opy_(response)
            return bstack1111l11lll1_opy_, response.json()
        except Exception as error:
            logger.error(bstack1ll_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡩࡳࡷࠦࡔࡦࡵࡷࡌࡺࡨ࠺ࠡࡽࢀࠦẻ").format(str(error)))
            return None
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def stop(cls, bstack1111l11l11l_opy_=None):
        if not bstack11llllll1l_opy_.on() and not bstack1l11llll1l_opy_.on():
            return
        if os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫẼ")) == bstack1ll_opy_ (u"ࠣࡰࡸࡰࡱࠨẽ") or os.environ.get(bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧẾ")) == bstack1ll_opy_ (u"ࠥࡲࡺࡲ࡬ࠣế"):
            logger.error(bstack1ll_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࡍࡪࡵࡶ࡭ࡳ࡭ࠠࡢࡷࡷ࡬ࡪࡴࡴࡪࡥࡤࡸ࡮ࡵ࡮ࠡࡶࡲ࡯ࡪࡴࠧỀ"))
            return {
                bstack1ll_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬề"): bstack1ll_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬỂ"),
                bstack1ll_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨể"): bstack1ll_opy_ (u"ࠨࡖࡲ࡯ࡪࡴ࠯ࡣࡷ࡬ࡰࡩࡏࡄࠡ࡫ࡶࠤࡺࡴࡤࡦࡨ࡬ࡲࡪࡪࠬࠡࡤࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢࡰ࡭࡬࡮ࡴࠡࡪࡤࡺࡪࠦࡦࡢ࡫࡯ࡩࡩ࠭Ễ")
            }
        try:
            cls.bstack1111lllll11_opy_.shutdown()
            data = {
                bstack1ll_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡦࡺࠧễ"): bstack11ll111lll_opy_()
            }
            if not bstack1111l11l11l_opy_ is None:
                data[bstack1ll_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡳࡥࡵࡣࡧࡥࡹࡧࠧỆ")] = [{
                    bstack1ll_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫệ"): bstack1ll_opy_ (u"ࠬࡻࡳࡦࡴࡢ࡯࡮ࡲ࡬ࡦࡦࠪỈ"),
                    bstack1ll_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱ࠭ỉ"): bstack1111l11l11l_opy_
                }]
            config = {
                bstack1ll_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨỊ"): cls.default_headers()
            }
            bstack11lll1lll1l_opy_ = bstack1ll_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡸࡺ࡯ࡱࠩị").format(os.environ[bstack1ll_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢỌ")])
            bstack1111l111l11_opy_ = cls.request_url(bstack11lll1lll1l_opy_)
            response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠪࡔ࡚࡚ࠧọ"), bstack1111l111l11_opy_, data, config)
            if not response.ok:
                raise Exception(bstack1ll_opy_ (u"ࠦࡘࡺ࡯ࡱࠢࡵࡩࡶࡻࡥࡴࡶࠣࡲࡴࡺࠠࡰ࡭ࠥỎ"))
        except Exception as error:
            logger.error(bstack1ll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺ࡯ࡱࠢࡥࡹ࡮ࡲࡤࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳ࡚ࠥࡥࡴࡶࡋࡹࡧࡀ࠺ࠡࠤỏ") + str(error))
            return {
                bstack1ll_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭Ố"): bstack1ll_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ố"),
                bstack1ll_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩỒ"): str(error)
            }
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def bstack1111l111ll1_opy_(cls, response):
        bstack1l1l111l_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1111l11lll1_opy_ = {}
        if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠩ࡭ࡻࡹ࠭ồ")) is None:
            os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧỔ")] = bstack1ll_opy_ (u"ࠫࡳࡻ࡬࡭ࠩổ")
        else:
            os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩỖ")] = bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"࠭ࡪࡸࡶࠪỗ"), bstack1ll_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬỘ"))
        os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ộ")] = bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫỚ"), bstack1ll_opy_ (u"ࠪࡲࡺࡲ࡬ࠨớ"))
        logger.info(bstack1ll_opy_ (u"࡙ࠫ࡫ࡳࡵࡪࡸࡦࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࠩỜ") + os.getenv(bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪờ")));
        if bstack11llllll1l_opy_.bstack1111l11l111_opy_(cls.bs_config, cls.bstack1l11111111_opy_.get(bstack1ll_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡸࡷࡪࡪࠧỞ"), bstack1ll_opy_ (u"ࠧࠨở"))) is True:
            bstack1111lll11l1_opy_, build_hashed_id, bstack11111llllll_opy_ = cls.bstack1111l1l11l1_opy_(bstack1l1l111l_opy_)
            if bstack1111lll11l1_opy_ != None and build_hashed_id != None:
                bstack1111l11lll1_opy_[bstack1ll_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨỠ")] = {
                    bstack1ll_opy_ (u"ࠩ࡭ࡻࡹࡥࡴࡰ࡭ࡨࡲࠬỡ"): bstack1111lll11l1_opy_,
                    bstack1ll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬỢ"): build_hashed_id,
                    bstack1ll_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨợ"): bstack11111llllll_opy_
                }
            else:
                bstack1111l11lll1_opy_[bstack1ll_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬỤ")] = {}
        else:
            bstack1111l11lll1_opy_[bstack1ll_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ụ")] = {}
        bstack1111l1l11ll_opy_, build_hashed_id = cls.bstack1111l11llll_opy_(bstack1l1l111l_opy_)
        if bstack1111l1l11ll_opy_ != None and build_hashed_id != None:
            bstack1111l11lll1_opy_[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧỦ")] = {
                bstack1ll_opy_ (u"ࠨࡣࡸࡸ࡭ࡥࡴࡰ࡭ࡨࡲࠬủ"): bstack1111l1l11ll_opy_,
                bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫỨ"): build_hashed_id,
            }
        else:
            bstack1111l11lll1_opy_[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪứ")] = {}
        if bstack1111l11lll1_opy_[bstack1ll_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫỪ")].get(bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧừ")) != None or bstack1111l11lll1_opy_[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭Ử")].get(bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩử")) != None:
            cls.bstack1111l11l1ll_opy_(bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠨ࡬ࡺࡸࠬỮ")), bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫữ")))
        return bstack1111l11lll1_opy_
    @classmethod
    def bstack1111l1l11l1_opy_(cls, bstack1l1l111l_opy_):
        if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪỰ")) == None:
            cls.bstack11111lll1l1_opy_()
            return [None, None, None]
        if bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫự")][bstack1ll_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭Ỳ")] != True:
            cls.bstack11111lll1l1_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ỳ")])
            return [None, None, None]
        logger.debug(bstack1ll_opy_ (u"ࠧࡕࡧࡶࡸࠥࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫỴ"))
        os.environ[bstack1ll_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧỵ")] = bstack1ll_opy_ (u"ࠩࡷࡶࡺ࡫ࠧỶ")
        if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠪ࡮ࡼࡺࠧỷ")):
            os.environ[bstack1ll_opy_ (u"ࠫࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࡡࡉࡓࡗࡥࡃࡓࡃࡖࡌࡤࡘࡅࡑࡑࡕࡘࡎࡔࡇࠨỸ")] = json.dumps({
                bstack1ll_opy_ (u"ࠬࡻࡳࡦࡴࡱࡥࡲ࡫ࠧỹ"): bstack11l1ll1l11l_opy_(cls.bs_config),
                bstack1ll_opy_ (u"࠭ࡰࡢࡵࡶࡻࡴࡸࡤࠨỺ"): bstack11ll111111l_opy_(cls.bs_config)
            })
        if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩỻ")):
            os.environ[bstack1ll_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧỼ")] = bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫỽ")]
        if bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪỾ")].get(bstack1ll_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬỿ"), {}).get(bstack1ll_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩἀ")):
            os.environ[bstack1ll_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧἁ")] = str(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧἂ")][bstack1ll_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩἃ")][bstack1ll_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭ἄ")])
        else:
            os.environ[bstack1ll_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫἅ")] = bstack1ll_opy_ (u"ࠦࡳࡻ࡬࡭ࠤἆ")
        return [bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠬࡰࡷࡵࠩἇ")], bstack1l1l111l_opy_[bstack1ll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨἈ")], os.environ[bstack1ll_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡆࡒࡌࡐ࡙ࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࡓࠨἉ")]]
    @classmethod
    def bstack1111l11llll_opy_(cls, bstack1l1l111l_opy_):
        if bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨἊ")) == None:
            cls.bstack1111l111l1l_opy_()
            return [None, None]
        if bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩἋ")][bstack1ll_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫἌ")] != True:
            cls.bstack1111l111l1l_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫἍ")])
            return [None, None]
        if bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬἎ")].get(bstack1ll_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧἏ")):
            logger.debug(bstack1ll_opy_ (u"ࠧࡕࡧࡶࡸࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫἐ"))
            parsed = json.loads(os.getenv(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩἑ"), bstack1ll_opy_ (u"ࠩࡾࢁࠬἒ")))
            capabilities = bstack11l1lllll1_opy_.bstack1111l11ll11_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪἓ")][bstack1ll_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬἔ")][bstack1ll_opy_ (u"ࠬࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫἕ")], bstack1ll_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ἖"), bstack1ll_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭἗"))
            bstack1111l1l11ll_opy_ = capabilities[bstack1ll_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭Ἐ")]
            os.environ[bstack1ll_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧἙ")] = bstack1111l1l11ll_opy_
            if bstack1ll_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧἚ") in bstack1l1l111l_opy_ and bstack1l1l111l_opy_.get(bstack1ll_opy_ (u"ࠦࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠥἛ")) is None:
                parsed[bstack1ll_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭Ἔ")] = capabilities[bstack1ll_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧἝ")]
            os.environ[bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ἞")] = json.dumps(parsed)
            scripts = bstack11l1lllll1_opy_.bstack1111l11ll11_opy_(bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ἟")][bstack1ll_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪἠ")][bstack1ll_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫἡ")], bstack1ll_opy_ (u"ࠫࡳࡧ࡭ࡦࠩἢ"), bstack1ll_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩ࠭ἣ"))
            bstack1l11l1l1l_opy_.bstack1l1111ll11_opy_(scripts)
            commands = bstack1l1l111l_opy_[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ἤ")][bstack1ll_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨἥ")][bstack1ll_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࡗࡳ࡜ࡸࡡࡱࠩἦ")].get(bstack1ll_opy_ (u"ࠩࡦࡳࡲࡳࡡ࡯ࡦࡶࠫἧ"))
            bstack1l11l1l1l_opy_.bstack11l1ll11ll1_opy_(commands)
            bstack11l1lllllll_opy_ = capabilities.get(bstack1ll_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨἨ"))
            bstack1l11l1l1l_opy_.bstack11l1ll1111l_opy_(bstack11l1lllllll_opy_)
            bstack1l11l1l1l_opy_.store()
        return [bstack1111l1l11ll_opy_, bstack1l1l111l_opy_[bstack1ll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭Ἡ")]]
    @classmethod
    def bstack11111lll1l1_opy_(cls, response=None):
        os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪἪ")] = bstack1ll_opy_ (u"࠭࡮ࡶ࡮࡯ࠫἫ")
        os.environ[bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫἬ")] = bstack1ll_opy_ (u"ࠨࡰࡸࡰࡱ࠭Ἥ")
        os.environ[bstack1ll_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡉࡏࡎࡒࡏࡉ࡙ࡋࡄࠨἮ")] = bstack1ll_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩἯ")
        os.environ[bstack1ll_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪἰ")] = bstack1ll_opy_ (u"ࠧࡴࡵ࡭࡮ࠥἱ")
        os.environ[bstack1ll_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧἲ")] = bstack1ll_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧἳ")
        cls.bstack1111l1l1l11_opy_(response, bstack1ll_opy_ (u"ࠣࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠣἴ"))
        return [None, None, None]
    @classmethod
    def bstack1111l111l1l_opy_(cls, response=None):
        os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧἵ")] = bstack1ll_opy_ (u"ࠪࡲࡺࡲ࡬ࠨἶ")
        os.environ[bstack1ll_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩἷ")] = bstack1ll_opy_ (u"ࠬࡴࡵ࡭࡮ࠪἸ")
        os.environ[bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪἹ")] = bstack1ll_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬἺ")
        cls.bstack1111l1l1l11_opy_(response, bstack1ll_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣἻ"))
        return [None, None, None]
    @classmethod
    def bstack1111l11l1ll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭Ἴ")] = jwt
        os.environ[bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨἽ")] = build_hashed_id
    @classmethod
    def bstack1111l1l1l11_opy_(cls, response=None, product=bstack1ll_opy_ (u"ࠦࠧἾ")):
        if response == None or response.get(bstack1ll_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࡷࠬἿ")) == None:
            logger.error(product + bstack1ll_opy_ (u"ࠨࠠࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡨࡤ࡭ࡱ࡫ࡤࠣὀ"))
            return
        for error in response[bstack1ll_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧὁ")]:
            bstack111lll1l1ll_opy_ = error[bstack1ll_opy_ (u"ࠨ࡭ࡨࡽࠬὂ")]
            error_message = error[bstack1ll_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪὃ")]
            if error_message:
                if bstack111lll1l1ll_opy_ == bstack1ll_opy_ (u"ࠥࡉࡗࡘࡏࡓࡡࡄࡇࡈࡋࡓࡔࡡࡇࡉࡓࡏࡅࡅࠤὄ"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack1ll_opy_ (u"ࠦࡉࡧࡴࡢࠢࡸࡴࡱࡵࡡࡥࠢࡷࡳࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࠧὅ") + product + bstack1ll_opy_ (u"ࠧࠦࡦࡢ࡫࡯ࡩࡩࠦࡤࡶࡧࠣࡸࡴࠦࡳࡰ࡯ࡨࠤࡪࡸࡲࡰࡴࠥ὆"))
    @classmethod
    def bstack1111l1111l1_opy_(cls):
        if cls.bstack1111lllll11_opy_ is not None:
            return
        cls.bstack1111lllll11_opy_ = bstack1111llll1ll_opy_(cls.bstack11111llll11_opy_)
        cls.bstack1111lllll11_opy_.start()
    @classmethod
    def bstack111l11l111_opy_(cls):
        if cls.bstack1111lllll11_opy_ is None:
            return
        cls.bstack1111lllll11_opy_.shutdown()
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def bstack11111llll11_opy_(cls, bstack111ll1ll11_opy_, event_url=bstack1ll_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬ࠬ὇")):
        config = {
            bstack1ll_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨὈ"): cls.default_headers()
        }
        logger.debug(bstack1ll_opy_ (u"ࠣࡲࡲࡷࡹࡥࡤࡢࡶࡤ࠾࡙ࠥࡥ࡯ࡦ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤࡹࡵࠠࡵࡧࡶࡸ࡭ࡻࡢࠡࡨࡲࡶࠥ࡫ࡶࡦࡰࡷࡷࠥࢁࡽࠣὉ").format(bstack1ll_opy_ (u"ࠩ࠯ࠤࠬὊ").join([event[bstack1ll_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧὋ")] for event in bstack111ll1ll11_opy_])))
        response = bstack11ll1l1ll1_opy_(bstack1ll_opy_ (u"ࠫࡕࡕࡓࡕࠩὌ"), cls.request_url(event_url), bstack111ll1ll11_opy_, config)
        bstack11l1ll11lll_opy_ = response.json()
    @classmethod
    def bstack11l11l1ll1_opy_(cls, bstack111ll1ll11_opy_, event_url=bstack1ll_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫὍ")):
        logger.debug(bstack1ll_opy_ (u"ࠨࡳࡦࡰࡧࡣࡩࡧࡴࡢ࠼ࠣࡅࡹࡺࡥ࡮ࡲࡷ࡭ࡳ࡭ࠠࡵࡱࠣࡥࡩࡪࠠࡥࡣࡷࡥࠥࡺ࡯ࠡࡤࡤࡸࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ὎").format(bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ὏")]))
        if not bstack11l1lllll1_opy_.bstack1111l1111ll_opy_(bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬὐ")]):
            logger.debug(bstack1ll_opy_ (u"ࠤࡶࡩࡳࡪ࡟ࡥࡣࡷࡥ࠿ࠦࡎࡰࡶࠣࡥࡩࡪࡩ࡯ࡩࠣࡨࡦࡺࡡࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢὑ").format(bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧὒ")]))
            return
        bstack1ll1111l_opy_ = bstack11l1lllll1_opy_.bstack1111l1l1111_opy_(bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨὓ")], bstack111ll1ll11_opy_.get(bstack1ll_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧὔ")))
        if bstack1ll1111l_opy_ != None:
            if bstack111ll1ll11_opy_.get(bstack1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨὕ")) != None:
                bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩὖ")][bstack1ll_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭ὗ")] = bstack1ll1111l_opy_
            else:
                bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࡢࡱࡦࡶࠧ὘")] = bstack1ll1111l_opy_
        if event_url == bstack1ll_opy_ (u"ࠪࡥࡵ࡯࠯ࡷ࠳࠲ࡦࡦࡺࡣࡩࠩὙ"):
            cls.bstack1111l1111l1_opy_()
            logger.debug(bstack1ll_opy_ (u"ࠦࡸ࡫࡮ࡥࡡࡧࡥࡹࡧ࠺ࠡࡃࡧࡨ࡮ࡴࡧࠡࡦࡤࡸࡦࠦࡴࡰࠢࡥࡥࡹࡩࡨࠡࡹ࡬ࡸ࡭ࠦࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ࠽ࠤࢀࢃࠢ὚").format(bstack111ll1ll11_opy_[bstack1ll_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩὛ")]))
            cls.bstack1111lllll11_opy_.add(bstack111ll1ll11_opy_)
        elif event_url == bstack1ll_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫ὜"):
            cls.bstack11111llll11_opy_([bstack111ll1ll11_opy_], event_url)
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def bstack11l111lll1_opy_(cls, logs):
        bstack1111l11ll1l_opy_ = []
        for log in logs:
            bstack1111l111lll_opy_ = {
                bstack1ll_opy_ (u"ࠧ࡬࡫ࡱࡨࠬὝ"): bstack1ll_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡌࡐࡉࠪ὞"),
                bstack1ll_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨὟ"): log[bstack1ll_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩὠ")],
                bstack1ll_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧὡ"): log[bstack1ll_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨὢ")],
                bstack1ll_opy_ (u"࠭ࡨࡵࡶࡳࡣࡷ࡫ࡳࡱࡱࡱࡷࡪ࠭ὣ"): {},
                bstack1ll_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨὤ"): log[bstack1ll_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩὥ")],
            }
            if bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩὦ") in log:
                bstack1111l111lll_opy_[bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪὧ")] = log[bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫὨ")]
            elif bstack1ll_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬὩ") in log:
                bstack1111l111lll_opy_[bstack1ll_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭Ὢ")] = log[bstack1ll_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧὫ")]
            bstack1111l11ll1l_opy_.append(bstack1111l111lll_opy_)
        cls.bstack11l11l1ll1_opy_({
            bstack1ll_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬὬ"): bstack1ll_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭Ὥ"),
            bstack1ll_opy_ (u"ࠪࡰࡴ࡭ࡳࠨὮ"): bstack1111l11ll1l_opy_
        })
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def bstack1111l111111_opy_(cls, steps):
        bstack11111lll1ll_opy_ = []
        for step in steps:
            bstack1111l1l111l_opy_ = {
                bstack1ll_opy_ (u"ࠫࡰ࡯࡮ࡥࠩὯ"): bstack1ll_opy_ (u"࡚ࠬࡅࡔࡖࡢࡗ࡙ࡋࡐࠨὰ"),
                bstack1ll_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬά"): step[bstack1ll_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ὲ")],
                bstack1ll_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫέ"): step[bstack1ll_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬὴ")],
                bstack1ll_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫή"): step[bstack1ll_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬὶ")],
                bstack1ll_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧί"): step[bstack1ll_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨὸ")]
            }
            if bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧό") in step:
                bstack1111l1l111l_opy_[bstack1ll_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨὺ")] = step[bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩύ")]
            elif bstack1ll_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪὼ") in step:
                bstack1111l1l111l_opy_[bstack1ll_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫώ")] = step[bstack1ll_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ὾")]
            bstack11111lll1ll_opy_.append(bstack1111l1l111l_opy_)
        cls.bstack11l11l1ll1_opy_({
            bstack1ll_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ὿"): bstack1ll_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫᾀ"),
            bstack1ll_opy_ (u"ࠨ࡮ࡲ࡫ࡸ࠭ᾁ"): bstack11111lll1ll_opy_
        })
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    @measure(event_name=EVENTS.bstack1llll11111_opy_, stage=STAGE.bstack1llll11lll_opy_)
    def bstack1111llll1_opy_(cls, screenshot):
        cls.bstack11l11l1ll1_opy_({
            bstack1ll_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ᾂ"): bstack1ll_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧᾃ"),
            bstack1ll_opy_ (u"ࠫࡱࡵࡧࡴࠩᾄ"): [{
                bstack1ll_opy_ (u"ࠬࡱࡩ࡯ࡦࠪᾅ"): bstack1ll_opy_ (u"࠭ࡔࡆࡕࡗࡣࡘࡉࡒࡆࡇࡑࡗࡍࡕࡔࠨᾆ"),
                bstack1ll_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪᾇ"): datetime.datetime.utcnow().isoformat() + bstack1ll_opy_ (u"ࠨ࡜ࠪᾈ"),
                bstack1ll_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᾉ"): screenshot[bstack1ll_opy_ (u"ࠪ࡭ࡲࡧࡧࡦࠩᾊ")],
                bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᾋ"): screenshot[bstack1ll_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᾌ")]
            }]
        }, event_url=bstack1ll_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࡶࠫᾍ"))
    @classmethod
    @bstack111l11ll11_opy_(class_method=True)
    def bstack11lll11ll_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack11l11l1ll1_opy_({
            bstack1ll_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫᾎ"): bstack1ll_opy_ (u"ࠨࡅࡅࡘࡘ࡫ࡳࡴ࡫ࡲࡲࡈࡸࡥࡢࡶࡨࡨࠬᾏ"),
            bstack1ll_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫᾐ"): {
                bstack1ll_opy_ (u"ࠥࡹࡺ࡯ࡤࠣᾑ"): cls.current_test_uuid(),
                bstack1ll_opy_ (u"ࠦ࡮ࡴࡴࡦࡩࡵࡥࡹ࡯࡯࡯ࡵࠥᾒ"): cls.bstack111lll11l1_opy_(driver)
            }
        })
    @classmethod
    def bstack11l111111l_opy_(cls, event: str, bstack111ll1ll11_opy_: bstack111l1l111l_opy_):
        bstack111l111lll_opy_ = {
            bstack1ll_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩᾓ"): event,
            bstack111ll1ll11_opy_.bstack111l11111l_opy_(): bstack111ll1ll11_opy_.bstack111ll1l1ll_opy_(event)
        }
        cls.bstack11l11l1ll1_opy_(bstack111l111lll_opy_)
        result = getattr(bstack111ll1ll11_opy_, bstack1ll_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᾔ"), None)
        if event == bstack1ll_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤࠨᾕ"):
            threading.current_thread().bstackTestMeta = {bstack1ll_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨᾖ"): bstack1ll_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪᾗ")}
        elif event == bstack1ll_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡊ࡮ࡴࡩࡴࡪࡨࡨࠬᾘ"):
            threading.current_thread().bstackTestMeta = {bstack1ll_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᾙ"): getattr(result, bstack1ll_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᾚ"), bstack1ll_opy_ (u"࠭ࠧᾛ"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫᾜ"), None) is None or os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬᾝ")] == bstack1ll_opy_ (u"ࠤࡱࡹࡱࡲࠢᾞ")) and (os.environ.get(bstack1ll_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᾟ"), None) is None or os.environ[bstack1ll_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᾠ")] == bstack1ll_opy_ (u"ࠧࡴࡵ࡭࡮ࠥᾡ")):
            return False
        return True
    @staticmethod
    def bstack11111llll1l_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1l111111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack1ll_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬᾢ"): bstack1ll_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪᾣ"),
            bstack1ll_opy_ (u"ࠨ࡚࠰ࡆࡘ࡚ࡁࡄࡍ࠰ࡘࡊ࡙ࡔࡐࡒࡖࠫᾤ"): bstack1ll_opy_ (u"ࠩࡷࡶࡺ࡫ࠧᾥ")
        }
        if os.environ.get(bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧᾦ"), None):
            headers[bstack1ll_opy_ (u"ࠫࡆࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫᾧ")] = bstack1ll_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨᾨ").format(os.environ[bstack1ll_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠥᾩ")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack1ll_opy_ (u"ࠧࡼࡿ࠲ࡿࢂ࠭ᾪ").format(bstack1111l11l1l1_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬᾫ"), None)
    @staticmethod
    def bstack111lll11l1_opy_(driver):
        return {
            bstack111ll1l1l11_opy_(): bstack111llllll11_opy_(driver)
        }
    @staticmethod
    def bstack11111lllll1_opy_(exception_info, report):
        return [{bstack1ll_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᾬ"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack1111l11ll1_opy_(typename):
        if bstack1ll_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᾭ") in typename:
            return bstack1ll_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᾮ")
        return bstack1ll_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᾯ")