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
import multiprocessing
import os
import json
from time import sleep
import bstack_utils.accessibility as bstack1l11llll1l_opy_
from browserstack_sdk.bstack11ll1111l_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack1l1l11ll_opy_
from bstack_utils.bstack1llll11l1l_opy_ import bstack1ll1ll1ll_opy_
from bstack_utils.constants import bstack1111ll1l11_opy_
class bstack11l1l11111_opy_:
    def __init__(self, args, logger, bstack1111lll1ll_opy_, bstack1111lll11l_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111lll1ll_opy_ = bstack1111lll1ll_opy_
        self.bstack1111lll11l_opy_ = bstack1111lll11l_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1l1ll1l1_opy_ = []
        self.bstack1111ll1ll1_opy_ = None
        self.bstack1ll111l11_opy_ = []
        self.bstack1111llll1l_opy_ = self.bstack1ll11ll1_opy_()
        self.bstack1ll111lll1_opy_ = -1
    def bstack1llllll1ll_opy_(self, bstack1111lll1l1_opy_):
        self.parse_args()
        self.bstack1111l1l1ll_opy_()
        self.bstack1111ll1lll_opy_(bstack1111lll1l1_opy_)
        self.bstack1111l1ll11_opy_()
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack1111lllll1_opy_():
        import importlib
        if getattr(importlib, bstack1ll_opy_ (u"ࠩࡩ࡭ࡳࡪ࡟࡭ࡱࡤࡨࡪࡸࠧခ"), False):
            bstack1111ll1l1l_opy_ = importlib.find_loader(bstack1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࠬဂ"))
        else:
            bstack1111ll1l1l_opy_ = importlib.util.find_spec(bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ဃ"))
    def bstack1111lll111_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack1ll111lll1_opy_ = -1
        if self.bstack1111lll11l_opy_ and bstack1ll_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬင") in self.bstack1111lll1ll_opy_:
            self.bstack1ll111lll1_opy_ = int(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭စ")])
        try:
            bstack1111ll11l1_opy_ = [bstack1ll_opy_ (u"ࠧ࠮࠯ࡧࡶ࡮ࡼࡥࡳࠩဆ"), bstack1ll_opy_ (u"ࠨ࠯࠰ࡴࡱࡻࡧࡪࡰࡶࠫဇ"), bstack1ll_opy_ (u"ࠩ࠰ࡴࠬဈ")]
            if self.bstack1ll111lll1_opy_ >= 0:
                bstack1111ll11l1_opy_.extend([bstack1ll_opy_ (u"ࠪ࠱࠲ࡴࡵ࡮ࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠫဉ"), bstack1ll_opy_ (u"ࠫ࠲ࡴࠧည")])
            for arg in bstack1111ll11l1_opy_:
                self.bstack1111lll111_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack1111l1l1ll_opy_(self):
        bstack1111ll1ll1_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack1111ll1ll1_opy_ = bstack1111ll1ll1_opy_
        return bstack1111ll1ll1_opy_
    def bstack1l1lll1ll_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            self.bstack1111lllll1_opy_()
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warn(e, bstack1l1l11ll_opy_)
    def bstack1111ll1lll_opy_(self, bstack1111lll1l1_opy_):
        bstack1lll1111ll_opy_ = Config.bstack11ll1l1l_opy_()
        if bstack1111lll1l1_opy_:
            self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠬ࠳࠭ࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩဋ"))
            self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"࠭ࡔࡳࡷࡨࠫဌ"))
        if bstack1lll1111ll_opy_.bstack1111l1lll1_opy_():
            self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠧ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸ࠭ဍ"))
            self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠨࡖࡵࡹࡪ࠭ဎ"))
        self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠩ࠰ࡴࠬဏ"))
        self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡲ࡯ࡹ࡬࡯࡮ࠨတ"))
        self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭ထ"))
        self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬဒ"))
        if self.bstack1ll111lll1_opy_ > 1:
            self.bstack1111ll1ll1_opy_.append(bstack1ll_opy_ (u"࠭࠭࡯ࠩဓ"))
            self.bstack1111ll1ll1_opy_.append(str(self.bstack1ll111lll1_opy_))
    def bstack1111l1ll11_opy_(self):
        if bstack1ll1ll1ll_opy_.bstack1l1ll11111_opy_(self.bstack1111lll1ll_opy_):
             self.bstack1111ll1ll1_opy_ += [
                bstack1111ll1l11_opy_.get(bstack1ll_opy_ (u"ࠧࡳࡧࡵࡹࡳ࠭န")), str(bstack1ll1ll1ll_opy_.bstack1ll1l1l11_opy_(self.bstack1111lll1ll_opy_)),
                bstack1111ll1l11_opy_.get(bstack1ll_opy_ (u"ࠨࡦࡨࡰࡦࡿࠧပ")), str(bstack1111ll1l11_opy_.get(bstack1ll_opy_ (u"ࠩࡵࡩࡷࡻ࡮࠮ࡦࡨࡰࡦࡿࠧဖ")))
            ]
    def bstack1111ll11ll_opy_(self):
        bstack1ll111l11_opy_ = []
        for spec in self.bstack1l1ll1l1_opy_:
            bstack1ll111111_opy_ = [spec]
            bstack1ll111111_opy_ += self.bstack1111ll1ll1_opy_
            bstack1ll111l11_opy_.append(bstack1ll111111_opy_)
        self.bstack1ll111l11_opy_ = bstack1ll111l11_opy_
        return bstack1ll111l11_opy_
    def bstack1ll11ll1_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack1111llll1l_opy_ = True
            return True
        except Exception as e:
            self.bstack1111llll1l_opy_ = False
        return self.bstack1111llll1l_opy_
    def bstack1l1l1ll11_opy_(self, bstack1111l1llll_opy_, bstack1llllll1ll_opy_):
        bstack1llllll1ll_opy_[bstack1ll_opy_ (u"ࠪࡇࡔࡔࡆࡊࡉࠪဗ")] = self.bstack1111lll1ll_opy_
        multiprocessing.set_start_method(bstack1ll_opy_ (u"ࠫࡸࡶࡡࡸࡰࠪဘ"))
        bstack11111l11l_opy_ = []
        manager = multiprocessing.Manager()
        bstack1111l1ll1l_opy_ = manager.list()
        if bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨမ") in self.bstack1111lll1ll_opy_:
            for index, platform in enumerate(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩယ")]):
                bstack11111l11l_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack1111l1llll_opy_,
                                                            args=(self.bstack1111ll1ll1_opy_, bstack1llllll1ll_opy_, bstack1111l1ll1l_opy_)))
            bstack1111ll111l_opy_ = len(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪရ")])
        else:
            bstack11111l11l_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack1111l1llll_opy_,
                                                        args=(self.bstack1111ll1ll1_opy_, bstack1llllll1ll_opy_, bstack1111l1ll1l_opy_)))
            bstack1111ll111l_opy_ = 1
        i = 0
        for t in bstack11111l11l_opy_:
            os.environ[bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨလ")] = str(i)
            if bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬဝ") in self.bstack1111lll1ll_opy_:
                os.environ[bstack1ll_opy_ (u"ࠪࡇ࡚ࡘࡒࡆࡐࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡄࡂࡖࡄࠫသ")] = json.dumps(self.bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧဟ")][i % bstack1111ll111l_opy_])
            i += 1
            t.start()
        for t in bstack11111l11l_opy_:
            t.join()
        return list(bstack1111l1ll1l_opy_)
    @staticmethod
    def bstack1111l1111_opy_(driver, bstack1111llll11_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack1ll_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡮ࡺࡥ࡮ࠩဠ"), None)
        if item and getattr(item, bstack1ll_opy_ (u"࠭࡟ࡢ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡧࡦࡹࡥࠨအ"), None) and not getattr(item, bstack1ll_opy_ (u"ࠧࡠࡣ࠴࠵ࡾࡥࡳࡵࡱࡳࡣࡩࡵ࡮ࡦࠩဢ"), False):
            logger.info(
                bstack1ll_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠦࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡ࡫ࡶࠤࡺࡴࡤࡦࡴࡺࡥࡾ࠴ࠢဣ"))
            bstack1111ll1111_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1l11llll1l_opy_.bstack1ll11111l_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)