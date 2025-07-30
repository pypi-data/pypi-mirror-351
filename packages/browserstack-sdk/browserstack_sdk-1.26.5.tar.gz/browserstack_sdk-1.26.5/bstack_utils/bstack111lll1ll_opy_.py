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
from browserstack_sdk.bstack1ll111111_opy_ import bstack1l1l1lll11_opy_
from browserstack_sdk.bstack111l11ll1l_opy_ import RobotHandler
def bstack1ll11ll11l_opy_(framework):
    if framework.lower() == bstack1l1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫᱦ"):
        return bstack1l1l1lll11_opy_.version()
    elif framework.lower() == bstack1l1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫᱧ"):
        return RobotHandler.version()
    elif framework.lower() == bstack1l1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ᱨ"):
        import behave
        return behave.__version__
    else:
        return bstack1l1_opy_ (u"ࠧࡶࡰ࡮ࡲࡴࡽ࡮ࠨᱩ")
def bstack1llll1ll1l_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack1l1_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯ࠪᱪ"))
        framework_version.append(importlib.metadata.version(bstack1l1_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᱫ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack1l1_opy_ (u"ࠪࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᱬ"))
        framework_version.append(importlib.metadata.version(bstack1l1_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᱭ")))
    except:
        pass
    return {
        bstack1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᱮ"): bstack1l1_opy_ (u"࠭࡟ࠨᱯ").join(framework_name),
        bstack1l1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨᱰ"): bstack1l1_opy_ (u"ࠨࡡࠪᱱ").join(framework_version)
    }