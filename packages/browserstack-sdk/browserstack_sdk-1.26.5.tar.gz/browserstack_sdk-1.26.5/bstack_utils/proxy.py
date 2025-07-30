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
import os
from urllib.parse import urlparse
from bstack_utils.config import Config
from bstack_utils.messages import bstack111llll11ll_opy_
bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
def bstack111l11l11l1_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack111l111llll_opy_(bstack111l111lll1_opy_, bstack111l11l1111_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack111l111lll1_opy_):
        with open(bstack111l111lll1_opy_) as f:
            pac = PACFile(f.read())
    elif bstack111l11l11l1_opy_(bstack111l111lll1_opy_):
        pac = get_pac(url=bstack111l111lll1_opy_)
    else:
        raise Exception(bstack1l1_opy_ (u"ࠨࡒࡤࡧࠥ࡬ࡩ࡭ࡧࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠾ࠥࢁࡽࠨ᷏").format(bstack111l111lll1_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack1l1_opy_ (u"ࠤ࠻࠲࠽࠴࠸࠯࠺᷐ࠥ"), 80))
        bstack111l111ll1l_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack111l111ll1l_opy_ = bstack1l1_opy_ (u"ࠪ࠴࠳࠶࠮࠱࠰࠳ࠫ᷑")
    proxy_url = session.get_pac().find_proxy_for_url(bstack111l11l1111_opy_, bstack111l111ll1l_opy_)
    return proxy_url
def bstack1ll1lll1_opy_(config):
    return bstack1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ᷒") in config or bstack1l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩᷓ") in config
def bstack11l1l1lll1_opy_(config):
    if not bstack1ll1lll1_opy_(config):
        return
    if config.get(bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩᷔ")):
        return config.get(bstack1l1_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪᷕ"))
    if config.get(bstack1l1_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬᷖ")):
        return config.get(bstack1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ᷗ"))
def bstack1lll1l11ll_opy_(config, bstack111l11l1111_opy_):
    proxy = bstack11l1l1lll1_opy_(config)
    proxies = {}
    if config.get(bstack1l1_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭ᷘ")) or config.get(bstack1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨᷙ")):
        if proxy.endswith(bstack1l1_opy_ (u"ࠬ࠴ࡰࡢࡥࠪᷚ")):
            proxies = bstack1l1l111ll_opy_(proxy, bstack111l11l1111_opy_)
        else:
            proxies = {
                bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᷛ"): proxy
            }
    bstack1ll11l111l_opy_.bstack1l1l11l1l_opy_(bstack1l1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠧᷜ"), proxies)
    return proxies
def bstack1l1l111ll_opy_(bstack111l111lll1_opy_, bstack111l11l1111_opy_):
    proxies = {}
    global bstack111l11l11ll_opy_
    if bstack1l1_opy_ (u"ࠨࡒࡄࡇࡤࡖࡒࡐ࡚࡜ࠫᷝ") in globals():
        return bstack111l11l11ll_opy_
    try:
        proxy = bstack111l111llll_opy_(bstack111l111lll1_opy_, bstack111l11l1111_opy_)
        if bstack1l1_opy_ (u"ࠤࡇࡍࡗࡋࡃࡕࠤᷞ") in proxy:
            proxies = {}
        elif bstack1l1_opy_ (u"ࠥࡌ࡙࡚ࡐࠣᷟ") in proxy or bstack1l1_opy_ (u"ࠦࡍ࡚ࡔࡑࡕࠥᷠ") in proxy or bstack1l1_opy_ (u"࡙ࠧࡏࡄࡍࡖࠦᷡ") in proxy:
            bstack111l11l111l_opy_ = proxy.split(bstack1l1_opy_ (u"ࠨࠠࠣᷢ"))
            if bstack1l1_opy_ (u"ࠢ࠻࠱࠲ࠦᷣ") in bstack1l1_opy_ (u"ࠣࠤᷤ").join(bstack111l11l111l_opy_[1:]):
                proxies = {
                    bstack1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨᷥ"): bstack1l1_opy_ (u"ࠥࠦᷦ").join(bstack111l11l111l_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᷧ"): str(bstack111l11l111l_opy_[0]).lower() + bstack1l1_opy_ (u"ࠧࡀ࠯࠰ࠤᷨ") + bstack1l1_opy_ (u"ࠨࠢᷩ").join(bstack111l11l111l_opy_[1:])
                }
        elif bstack1l1_opy_ (u"ࠢࡑࡔࡒ࡜࡞ࠨᷪ") in proxy:
            bstack111l11l111l_opy_ = proxy.split(bstack1l1_opy_ (u"ࠣࠢࠥᷫ"))
            if bstack1l1_opy_ (u"ࠤ࠽࠳࠴ࠨᷬ") in bstack1l1_opy_ (u"ࠥࠦᷭ").join(bstack111l11l111l_opy_[1:]):
                proxies = {
                    bstack1l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪᷮ"): bstack1l1_opy_ (u"ࠧࠨᷯ").join(bstack111l11l111l_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬᷰ"): bstack1l1_opy_ (u"ࠢࡩࡶࡷࡴ࠿࠵࠯ࠣᷱ") + bstack1l1_opy_ (u"ࠣࠤᷲ").join(bstack111l11l111l_opy_[1:])
                }
        else:
            proxies = {
                bstack1l1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࠨᷳ"): proxy
            }
    except Exception as e:
        print(bstack1l1_opy_ (u"ࠥࡷࡴࡳࡥࠡࡧࡵࡶࡴࡸࠢᷴ"), bstack111llll11ll_opy_.format(bstack111l111lll1_opy_, str(e)))
    bstack111l11l11ll_opy_ = proxies
    return proxies