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
from browserstack_sdk.bstack1l111lll_opy_ import bstack11l1l11111_opy_
from browserstack_sdk.bstack111ll1ll1l_opy_ import RobotHandler
def bstack1lll1l1ll1_opy_(framework):
    if framework.lower() == bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ᪴"):
        return bstack11l1l11111_opy_.version()
    elif framework.lower() == bstack1ll_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ᪵ࠫ"):
        return RobotHandler.version()
    elif framework.lower() == bstack1ll_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ᪶࠭"):
        import behave
        return behave.__version__
    else:
        return bstack1ll_opy_ (u"ࠧࡶࡰ࡮ࡲࡴࡽ࡮ࠨ᪷")
def bstack11lll1ll11_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack1ll_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯᪸ࠪ"))
        framework_version.append(importlib.metadata.version(bstack1ll_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰ᪹ࠦ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack1ll_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ᪺ࠧ"))
        framework_version.append(importlib.metadata.version(bstack1ll_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ᪻")))
    except:
        pass
    return {
        bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ᪼"): bstack1ll_opy_ (u"࠭࡟ࠨ᪽").join(framework_name),
        bstack1ll_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨ᪾"): bstack1ll_opy_ (u"ࠨࡡᪿࠪ").join(framework_version)
    }