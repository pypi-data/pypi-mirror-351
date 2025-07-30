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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
logger = logging.getLogger(__name__)
class bstack11l1l111lll_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1111ll1llll_opy_ = urljoin(builder, bstack1l1_opy_ (u"ࠫ࡮ࡹࡳࡶࡧࡶࠫḭ"))
        if params:
            bstack1111ll1llll_opy_ += bstack1l1_opy_ (u"ࠧࡅࡻࡾࠤḮ").format(urlencode({bstack1l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ḯ"): params.get(bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧḰ"))}))
        return bstack11l1l111lll_opy_.bstack1111lll11l1_opy_(bstack1111ll1llll_opy_)
    @staticmethod
    def bstack11l1l11l11l_opy_(builder,params=None):
        bstack1111ll1llll_opy_ = urljoin(builder, bstack1l1_opy_ (u"ࠨ࡫ࡶࡷࡺ࡫ࡳ࠮ࡵࡸࡱࡲࡧࡲࡺࠩḱ"))
        if params:
            bstack1111ll1llll_opy_ += bstack1l1_opy_ (u"ࠤࡂࡿࢂࠨḲ").format(urlencode({bstack1l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪḳ"): params.get(bstack1l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫḴ"))}))
        return bstack11l1l111lll_opy_.bstack1111lll11l1_opy_(bstack1111ll1llll_opy_)
    @staticmethod
    def bstack1111lll11l1_opy_(bstack1111lll1111_opy_):
        bstack1111lll111l_opy_ = os.environ.get(bstack1l1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪḵ"), os.environ.get(bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪḶ"), bstack1l1_opy_ (u"ࠧࠨḷ")))
        headers = {bstack1l1_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨḸ"): bstack1l1_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬḹ").format(bstack1111lll111l_opy_)}
        response = requests.get(bstack1111lll1111_opy_, headers=headers)
        bstack1111lll11ll_opy_ = {}
        try:
            bstack1111lll11ll_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack1l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠤḺ").format(e))
            pass
        if bstack1111lll11ll_opy_ is not None:
            bstack1111lll11ll_opy_[bstack1l1_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬḻ")] = response.headers.get(bstack1l1_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭Ḽ"), str(int(datetime.now().timestamp() * 1000)))
            bstack1111lll11ll_opy_[bstack1l1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ḽ")] = response.status_code
        return bstack1111lll11ll_opy_