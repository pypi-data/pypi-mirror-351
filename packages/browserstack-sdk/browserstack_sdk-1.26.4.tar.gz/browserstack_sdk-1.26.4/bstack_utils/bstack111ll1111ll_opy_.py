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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111lll11lll_opy_
from browserstack_sdk.bstack1l111lll_opy_ import bstack11l1l11111_opy_
def _111l1lllll1_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111ll11111l_opy_:
    def __init__(self, handler):
        self._111ll111l11_opy_ = {}
        self._111ll111ll1_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack11l1l11111_opy_.version()
        if bstack111lll11lll_opy_(pytest_version, bstack1ll_opy_ (u"ࠣ࠺࠱࠵࠳࠷ࠢᳶ")) >= 0:
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬ᳷")] = Module._register_setup_function_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᳸")] = Module._register_setup_module_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᳹")] = Class._register_setup_class_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᳺ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ᳻"))
            Module._register_setup_module_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᳼"))
            Class._register_setup_class_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᳽"))
            Class._register_setup_method_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ᳾"))
        else:
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭᳿")] = Module._inject_setup_function_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᴀ")] = Module._inject_setup_module_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᴁ")] = Class._inject_setup_class_fixture
            self._111ll111l11_opy_[bstack1ll_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᴂ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᴃ"))
            Module._inject_setup_module_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᴄ"))
            Class._inject_setup_class_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᴅ"))
            Class._inject_setup_method_fixture = self.bstack111ll1111l1_opy_(bstack1ll_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᴆ"))
    def bstack111ll111l1l_opy_(self, bstack111ll111111_opy_, hook_type):
        bstack111ll11l111_opy_ = id(bstack111ll111111_opy_.__class__)
        if (bstack111ll11l111_opy_, hook_type) in self._111ll111ll1_opy_:
            return
        meth = getattr(bstack111ll111111_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111ll111ll1_opy_[(bstack111ll11l111_opy_, hook_type)] = meth
            setattr(bstack111ll111111_opy_, hook_type, self.bstack111ll11l1l1_opy_(hook_type, bstack111ll11l111_opy_))
    def bstack111l1llll11_opy_(self, instance, bstack111ll111lll_opy_):
        if bstack111ll111lll_opy_ == bstack1ll_opy_ (u"ࠦ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠢᴇ"):
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨᴈ"))
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠥᴉ"))
        if bstack111ll111lll_opy_ == bstack1ll_opy_ (u"ࠢ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣᴊ"):
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠢᴋ"))
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲࡵࡤࡶ࡮ࡨࠦᴌ"))
        if bstack111ll111lll_opy_ == bstack1ll_opy_ (u"ࠥࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧࠥᴍ"):
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠤᴎ"))
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸࠨᴏ"))
        if bstack111ll111lll_opy_ == bstack1ll_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠢᴐ"):
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩࠨᴑ"))
            self.bstack111ll111l1l_opy_(instance.obj, bstack1ll_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠥᴒ"))
    @staticmethod
    def bstack111l1llll1l_opy_(hook_type, func, args):
        if hook_type in [bstack1ll_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨᴓ"), bstack1ll_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬᴔ")]:
            _111l1lllll1_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111ll11l1l1_opy_(self, hook_type, bstack111ll11l111_opy_):
        def bstack111ll11l1ll_opy_(arg=None):
            self.handler(hook_type, bstack1ll_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫᴕ"))
            result = None
            try:
                bstack1lllllllll1_opy_ = self._111ll111ll1_opy_[(bstack111ll11l111_opy_, hook_type)]
                self.bstack111l1llll1l_opy_(hook_type, bstack1lllllllll1_opy_, (arg,))
                result = Result(result=bstack1ll_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᴖ"))
            except Exception as e:
                result = Result(result=bstack1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᴗ"), exception=e)
                self.handler(hook_type, bstack1ll_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᴘ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1ll_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᴙ"), result)
        def bstack111l1llllll_opy_(this, arg=None):
            self.handler(hook_type, bstack1ll_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩᴚ"))
            result = None
            exception = None
            try:
                self.bstack111l1llll1l_opy_(hook_type, self._111ll111ll1_opy_[hook_type], (this, arg))
                result = Result(result=bstack1ll_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᴛ"))
            except Exception as e:
                result = Result(result=bstack1ll_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᴜ"), exception=e)
                self.handler(hook_type, bstack1ll_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫᴝ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1ll_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᴞ"), result)
        if hook_type in [bstack1ll_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ᴟ"), bstack1ll_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪᴠ")]:
            return bstack111l1llllll_opy_
        return bstack111ll11l1ll_opy_
    def bstack111ll1111l1_opy_(self, bstack111ll111lll_opy_):
        def bstack111ll11l11l_opy_(this, *args, **kwargs):
            self.bstack111l1llll11_opy_(this, bstack111ll111lll_opy_)
            self._111ll111l11_opy_[bstack111ll111lll_opy_](this, *args, **kwargs)
        return bstack111ll11l11l_opy_