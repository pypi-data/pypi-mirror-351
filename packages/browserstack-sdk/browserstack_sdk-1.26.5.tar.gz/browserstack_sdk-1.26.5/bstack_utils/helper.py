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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack11lll111l1l_opy_, bstack1lllll1l1_opy_, bstack1l1llll111_opy_, bstack1l11lll1l1_opy_,
                                    bstack11lll11lll1_opy_, bstack11l1llllll1_opy_, bstack11ll11111ll_opy_, bstack11ll1ll11l1_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack1l1llll11_opy_, bstack1l1l11l1_opy_
from bstack_utils.proxy import bstack1lll1l11ll_opy_, bstack11l1l1lll1_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1l11lllll_opy_
from browserstack_sdk._version import __version__
bstack1ll11l111l_opy_ = Config.bstack1l1l11ll1_opy_()
logger = bstack1l11lllll_opy_.get_logger(__name__, bstack1l11lllll_opy_.bstack1lllll11l1l_opy_())
def bstack11ll1111l1l_opy_(config):
    return config[bstack1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᖊ")]
def bstack11lll11ll1l_opy_(config):
    return config[bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᖋ")]
def bstack11l11ll11_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack11lll1l1ll1_opy_(obj):
    values = []
    bstack11ll1l1ll11_opy_ = re.compile(bstack1l1_opy_ (u"ࡲࠣࡠࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࡜ࡥ࠭ࠧࠦᖌ"), re.I)
    for key in obj.keys():
        if bstack11ll1l1ll11_opy_.match(key):
            values.append(obj[key])
    return values
def bstack11lll11l1ll_opy_(config):
    tags = []
    tags.extend(bstack11lll1l1ll1_opy_(os.environ))
    tags.extend(bstack11lll1l1ll1_opy_(config))
    return tags
def bstack11ll11l111l_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack11ll111111l_opy_(bstack11ll1ll1ll1_opy_):
    if not bstack11ll1ll1ll1_opy_:
        return bstack1l1_opy_ (u"ࠨࠩᖍ")
    return bstack1l1_opy_ (u"ࠤࡾࢁࠥ࠮ࡻࡾࠫࠥᖎ").format(bstack11ll1ll1ll1_opy_.name, bstack11ll1ll1ll1_opy_.email)
def bstack11ll11l1lll_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack11ll1llllll_opy_ = repo.common_dir
        info = {
            bstack1l1_opy_ (u"ࠥࡷ࡭ࡧࠢᖏ"): repo.head.commit.hexsha,
            bstack1l1_opy_ (u"ࠦࡸ࡮࡯ࡳࡶࡢࡷ࡭ࡧࠢᖐ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1l1_opy_ (u"ࠧࡨࡲࡢࡰࡦ࡬ࠧᖑ"): repo.active_branch.name,
            bstack1l1_opy_ (u"ࠨࡴࡢࡩࠥᖒ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࠥᖓ"): bstack11ll111111l_opy_(repo.head.commit.committer),
            bstack1l1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡵࡧࡵࡣࡩࡧࡴࡦࠤᖔ"): repo.head.commit.committed_datetime.isoformat(),
            bstack1l1_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࠤᖕ"): bstack11ll111111l_opy_(repo.head.commit.author),
            bstack1l1_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡢࡨࡦࡺࡥࠣᖖ"): repo.head.commit.authored_datetime.isoformat(),
            bstack1l1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᖗ"): repo.head.commit.message,
            bstack1l1_opy_ (u"ࠧࡸ࡯ࡰࡶࠥᖘ"): repo.git.rev_parse(bstack1l1_opy_ (u"ࠨ࠭࠮ࡵ࡫ࡳࡼ࠳ࡴࡰࡲ࡯ࡩࡻ࡫࡬ࠣᖙ")),
            bstack1l1_opy_ (u"ࠢࡤࡱࡰࡱࡴࡴ࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣᖚ"): bstack11ll1llllll_opy_,
            bstack1l1_opy_ (u"ࠣࡹࡲࡶࡰࡺࡲࡦࡧࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦᖛ"): subprocess.check_output([bstack1l1_opy_ (u"ࠤࡪ࡭ࡹࠨᖜ"), bstack1l1_opy_ (u"ࠥࡶࡪࡼ࠭ࡱࡣࡵࡷࡪࠨᖝ"), bstack1l1_opy_ (u"ࠦ࠲࠳ࡧࡪࡶ࠰ࡧࡴࡳ࡭ࡰࡰ࠰ࡨ࡮ࡸࠢᖞ")]).strip().decode(
                bstack1l1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᖟ")),
            bstack1l1_opy_ (u"ࠨ࡬ࡢࡵࡷࡣࡹࡧࡧࠣᖠ"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡳࡠࡵ࡬ࡲࡨ࡫࡟࡭ࡣࡶࡸࡤࡺࡡࡨࠤᖡ"): repo.git.rev_list(
                bstack1l1_opy_ (u"ࠣࡽࢀ࠲࠳ࢁࡽࠣᖢ").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack11lll1l1l1l_opy_ = []
        for remote in remotes:
            bstack11l1llll111_opy_ = {
                bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᖣ"): remote.name,
                bstack1l1_opy_ (u"ࠥࡹࡷࡲࠢᖤ"): remote.url,
            }
            bstack11lll1l1l1l_opy_.append(bstack11l1llll111_opy_)
        bstack11ll1lllll1_opy_ = {
            bstack1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᖥ"): bstack1l1_opy_ (u"ࠧ࡭ࡩࡵࠤᖦ"),
            **info,
            bstack1l1_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪࡹࠢᖧ"): bstack11lll1l1l1l_opy_
        }
        bstack11ll1lllll1_opy_ = bstack11ll1l111ll_opy_(bstack11ll1lllll1_opy_)
        return bstack11ll1lllll1_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥᖨ").format(err))
        return {}
def bstack11ll1l111ll_opy_(bstack11ll1lllll1_opy_):
    bstack11ll1111111_opy_ = bstack11ll11ll1l1_opy_(bstack11ll1lllll1_opy_)
    if bstack11ll1111111_opy_ and bstack11ll1111111_opy_ > bstack11lll11lll1_opy_:
        bstack11ll1l1l1ll_opy_ = bstack11ll1111111_opy_ - bstack11lll11lll1_opy_
        bstack11ll11l11ll_opy_ = bstack11ll1111lll_opy_(bstack11ll1lllll1_opy_[bstack1l1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᖩ")], bstack11ll1l1l1ll_opy_)
        bstack11ll1lllll1_opy_[bstack1l1_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡡࡰࡩࡸࡹࡡࡨࡧࠥᖪ")] = bstack11ll11l11ll_opy_
        logger.info(bstack1l1_opy_ (u"ࠥࡘ࡭࡫ࠠࡤࡱࡰࡱ࡮ࡺࠠࡩࡣࡶࠤࡧ࡫ࡥ࡯ࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨ࠳ࠦࡓࡪࡼࡨࠤࡴ࡬ࠠࡤࡱࡰࡱ࡮ࡺࠠࡢࡨࡷࡩࡷࠦࡴࡳࡷࡱࡧࡦࡺࡩࡰࡰࠣ࡭ࡸࠦࡻࡾࠢࡎࡆࠧᖫ")
                    .format(bstack11ll11ll1l1_opy_(bstack11ll1lllll1_opy_) / 1024))
    return bstack11ll1lllll1_opy_
def bstack11ll11ll1l1_opy_(bstack11llll11l_opy_):
    try:
        if bstack11llll11l_opy_:
            bstack11lll11l1l1_opy_ = json.dumps(bstack11llll11l_opy_)
            bstack11lll1l1l11_opy_ = sys.getsizeof(bstack11lll11l1l1_opy_)
            return bstack11lll1l1l11_opy_
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠦࡘࡵ࡭ࡦࡶ࡫࡭ࡳ࡭ࠠࡸࡧࡱࡸࠥࡽࡲࡰࡰࡪࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡦࡲࡣࡶ࡮ࡤࡸ࡮ࡴࡧࠡࡵ࡬ࡾࡪࠦ࡯ࡧࠢࡍࡗࡔࡔࠠࡰࡤ࡭ࡩࡨࡺ࠺ࠡࡽࢀࠦᖬ").format(e))
    return -1
def bstack11ll1111lll_opy_(field, bstack11lll1ll11l_opy_):
    try:
        bstack11lll111lll_opy_ = len(bytes(bstack11l1llllll1_opy_, bstack1l1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᖭ")))
        bstack11lll1lll11_opy_ = bytes(field, bstack1l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᖮ"))
        bstack11ll1llll1l_opy_ = len(bstack11lll1lll11_opy_)
        bstack11ll11111l1_opy_ = ceil(bstack11ll1llll1l_opy_ - bstack11lll1ll11l_opy_ - bstack11lll111lll_opy_)
        if bstack11ll11111l1_opy_ > 0:
            bstack11ll111l1ll_opy_ = bstack11lll1lll11_opy_[:bstack11ll11111l1_opy_].decode(bstack1l1_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᖯ"), errors=bstack1l1_opy_ (u"ࠨ࡫ࡪࡲࡴࡸࡥࠨᖰ")) + bstack11l1llllll1_opy_
            return bstack11ll111l1ll_opy_
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡵࡴࡸࡲࡨࡧࡴࡪࡰࡪࠤ࡫࡯ࡥ࡭ࡦ࠯ࠤࡳࡵࡴࡩ࡫ࡱ࡫ࠥࡽࡡࡴࠢࡷࡶࡺࡴࡣࡢࡶࡨࡨࠥ࡮ࡥࡳࡧ࠽ࠤࢀࢃࠢᖱ").format(e))
    return field
def bstack1lll1lll1l_opy_():
    env = os.environ
    if (bstack1l1_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠣᖲ") in env and len(env[bstack1l1_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠤᖳ")]) > 0) or (
            bstack1l1_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠦᖴ") in env and len(env[bstack1l1_opy_ (u"ࠨࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠧᖵ")]) > 0):
        return {
            bstack1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᖶ"): bstack1l1_opy_ (u"ࠣࡌࡨࡲࡰ࡯࡮ࡴࠤᖷ"),
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᖸ"): env.get(bstack1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠨᖹ")),
            bstack1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᖺ"): env.get(bstack1l1_opy_ (u"ࠧࡐࡏࡃࡡࡑࡅࡒࡋࠢᖻ")),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᖼ"): env.get(bstack1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᖽ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠣࡅࡌࠦᖾ")) == bstack1l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᖿ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡆࡍࠧᗀ"))):
        return {
            bstack1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᗁ"): bstack1l1_opy_ (u"ࠧࡉࡩࡳࡥ࡯ࡩࡈࡏࠢᗂ"),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᗃ"): env.get(bstack1l1_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥᗄ")),
            bstack1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᗅ"): env.get(bstack1l1_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡡࡍࡓࡇࠨᗆ")),
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᗇ"): env.get(bstack1l1_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࠢᗈ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠧࡉࡉࠣᗉ")) == bstack1l1_opy_ (u"ࠨࡴࡳࡷࡨࠦᗊ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙ࠢᗋ"))):
        return {
            bstack1l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᗌ"): bstack1l1_opy_ (u"ࠤࡗࡶࡦࡼࡩࡴࠢࡆࡍࠧᗍ"),
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᗎ"): env.get(bstack1l1_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࡣࡇ࡛ࡉࡍࡆࡢ࡛ࡊࡈ࡟ࡖࡔࡏࠦᗏ")),
            bstack1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᗐ"): env.get(bstack1l1_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᗑ")),
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᗒ"): env.get(bstack1l1_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᗓ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠤࡆࡍࠧᗔ")) == bstack1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣᗕ") and env.get(bstack1l1_opy_ (u"ࠦࡈࡏ࡟ࡏࡃࡐࡉࠧᗖ")) == bstack1l1_opy_ (u"ࠧࡩ࡯ࡥࡧࡶ࡬࡮ࡶࠢᗗ"):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗘ"): bstack1l1_opy_ (u"ࠢࡄࡱࡧࡩࡸ࡮ࡩࡱࠤᗙ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᗚ"): None,
            bstack1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᗛ"): None,
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᗜ"): None
        }
    if env.get(bstack1l1_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡔࡄࡒࡈࡎࠢᗝ")) and env.get(bstack1l1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡅࡒࡑࡒࡏࡔࠣᗞ")):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᗟ"): bstack1l1_opy_ (u"ࠢࡃ࡫ࡷࡦࡺࡩ࡫ࡦࡶࠥᗠ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᗡ"): env.get(bstack1l1_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡍࡉࡕࡡࡋࡘ࡙ࡖ࡟ࡐࡔࡌࡋࡎࡔࠢᗢ")),
            bstack1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᗣ"): None,
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᗤ"): env.get(bstack1l1_opy_ (u"ࠧࡈࡉࡕࡄࡘࡇࡐࡋࡔࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᗥ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠨࡃࡊࠤᗦ")) == bstack1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧᗧ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠣࡆࡕࡓࡓࡋࠢᗨ"))):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᗩ"): bstack1l1_opy_ (u"ࠥࡈࡷࡵ࡮ࡦࠤᗪ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᗫ"): env.get(bstack1l1_opy_ (u"ࠧࡊࡒࡐࡐࡈࡣࡇ࡛ࡉࡍࡆࡢࡐࡎࡔࡋࠣᗬ")),
            bstack1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᗭ"): None,
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᗮ"): env.get(bstack1l1_opy_ (u"ࠣࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᗯ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠤࡆࡍࠧᗰ")) == bstack1l1_opy_ (u"ࠥࡸࡷࡻࡥࠣᗱ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋࠢᗲ"))):
        return {
            bstack1l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᗳ"): bstack1l1_opy_ (u"ࠨࡓࡦ࡯ࡤࡴ࡭ࡵࡲࡦࠤᗴ"),
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᗵ"): env.get(bstack1l1_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࡣࡔࡘࡇࡂࡐࡌ࡞ࡆ࡚ࡉࡐࡐࡢ࡙ࡗࡒࠢᗶ")),
            bstack1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᗷ"): env.get(bstack1l1_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᗸ")),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᗹ"): env.get(bstack1l1_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡌࡒࡆࡤࡏࡄࠣᗺ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠨࡃࡊࠤᗻ")) == bstack1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧᗼ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠣࡉࡌࡘࡑࡇࡂࡠࡅࡌࠦᗽ"))):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᗾ"): bstack1l1_opy_ (u"ࠥࡋ࡮ࡺࡌࡢࡤࠥᗿ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᘀ"): env.get(bstack1l1_opy_ (u"ࠧࡉࡉࡠࡌࡒࡆࡤ࡛ࡒࡍࠤᘁ")),
            bstack1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᘂ"): env.get(bstack1l1_opy_ (u"ࠢࡄࡋࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᘃ")),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᘄ"): env.get(bstack1l1_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡌࡈࠧᘅ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠥࡇࡎࠨᘆ")) == bstack1l1_opy_ (u"ࠦࡹࡸࡵࡦࠤᘇ") and bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࠣᘈ"))):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᘉ"): bstack1l1_opy_ (u"ࠢࡃࡷ࡬ࡰࡩࡱࡩࡵࡧࠥᘊ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᘋ"): env.get(bstack1l1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᘌ")),
            bstack1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᘍ"): env.get(bstack1l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡍࡃࡅࡉࡑࠨᘎ")) or env.get(bstack1l1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡏࡎ࡚ࡅࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡒࡆࡓࡅࠣᘏ")),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᘐ"): env.get(bstack1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡑࡉࡕࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᘑ"))
        }
    if bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠣࡖࡉࡣࡇ࡛ࡉࡍࡆࠥᘒ"))):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᘓ"): bstack1l1_opy_ (u"࡚ࠥ࡮ࡹࡵࡢ࡮ࠣࡗࡹࡻࡤࡪࡱࠣࡘࡪࡧ࡭ࠡࡕࡨࡶࡻ࡯ࡣࡦࡵࠥᘔ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᘕ"): bstack1l1_opy_ (u"ࠧࢁࡽࡼࡿࠥᘖ").format(env.get(bstack1l1_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡊࡔ࡛ࡎࡅࡃࡗࡍࡔࡔࡓࡆࡔ࡙ࡉࡗ࡛ࡒࡊࠩᘗ")), env.get(bstack1l1_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡕࡘࡏࡋࡇࡆࡘࡎࡊࠧᘘ"))),
            bstack1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᘙ"): env.get(bstack1l1_opy_ (u"ࠤࡖ࡝ࡘ࡚ࡅࡎࡡࡇࡉࡋࡏࡎࡊࡖࡌࡓࡓࡏࡄࠣᘚ")),
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᘛ"): env.get(bstack1l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦᘜ"))
        }
    if bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘࠢᘝ"))):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᘞ"): bstack1l1_opy_ (u"ࠢࡂࡲࡳࡺࡪࡿ࡯ࡳࠤᘟ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᘠ"): bstack1l1_opy_ (u"ࠤࡾࢁ࠴ࡶࡲࡰ࡬ࡨࡧࡹ࠵ࡻࡾ࠱ࡾࢁ࠴ࡨࡵࡪ࡮ࡧࡷ࠴ࢁࡽࠣᘡ").format(env.get(bstack1l1_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤ࡛ࡒࡍࠩᘢ")), env.get(bstack1l1_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡁࡄࡅࡒ࡙ࡓ࡚࡟ࡏࡃࡐࡉࠬᘣ")), env.get(bstack1l1_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡕࡏ࡙ࡌ࠭ᘤ")), env.get(bstack1l1_opy_ (u"࠭ࡁࡑࡒ࡙ࡉ࡞ࡕࡒࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪᘥ"))),
            bstack1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᘦ"): env.get(bstack1l1_opy_ (u"ࠣࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᘧ")),
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᘨ"): env.get(bstack1l1_opy_ (u"ࠥࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᘩ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠦࡆࡠࡕࡓࡇࡢࡌ࡙࡚ࡐࡠࡗࡖࡉࡗࡥࡁࡈࡇࡑࡘࠧᘪ")) and env.get(bstack1l1_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢᘫ")):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᘬ"): bstack1l1_opy_ (u"ࠢࡂࡼࡸࡶࡪࠦࡃࡊࠤᘭ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᘮ"): bstack1l1_opy_ (u"ࠤࡾࢁࢀࢃ࠯ࡠࡤࡸ࡭ࡱࡪ࠯ࡳࡧࡶࡹࡱࡺࡳࡀࡤࡸ࡭ࡱࡪࡉࡥ࠿ࡾࢁࠧᘯ").format(env.get(bstack1l1_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡇࡑࡘࡒࡉࡇࡔࡊࡑࡑࡗࡊࡘࡖࡆࡔࡘࡖࡎ࠭ᘰ")), env.get(bstack1l1_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡒࡕࡓࡏࡋࡃࡕࠩᘱ")), env.get(bstack1l1_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬᘲ"))),
            bstack1l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᘳ"): env.get(bstack1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡎࡊࠢᘴ")),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᘵ"): env.get(bstack1l1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠤᘶ"))
        }
    if any([env.get(bstack1l1_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᘷ")), env.get(bstack1l1_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡓࡇࡖࡓࡑ࡜ࡅࡅࡡࡖࡓ࡚ࡘࡃࡆࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᘸ")), env.get(bstack1l1_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡕࡒ࡙ࡗࡉࡅࡠࡘࡈࡖࡘࡏࡏࡏࠤᘹ"))]):
        return {
            bstack1l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᘺ"): bstack1l1_opy_ (u"ࠢࡂ࡙ࡖࠤࡈࡵࡤࡦࡄࡸ࡭ࡱࡪࠢᘻ"),
            bstack1l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᘼ"): env.get(bstack1l1_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡖࡕࡃࡎࡌࡇࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᘽ")),
            bstack1l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᘾ"): env.get(bstack1l1_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠤᘿ")),
            bstack1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᙀ"): env.get(bstack1l1_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᙁ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡔࡵ࡮ࡤࡨࡶࠧᙂ")):
        return {
            bstack1l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᙃ"): bstack1l1_opy_ (u"ࠤࡅࡥࡲࡨ࡯ࡰࠤᙄ"),
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᙅ"): env.get(bstack1l1_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡕࡩࡸࡻ࡬ࡵࡵࡘࡶࡱࠨᙆ")),
            bstack1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᙇ"): env.get(bstack1l1_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡳࡩࡱࡵࡸࡏࡵࡢࡏࡣࡰࡩࠧᙈ")),
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᙉ"): env.get(bstack1l1_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡎࡶ࡯ࡥࡩࡷࠨᙊ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࠥᙋ")) or env.get(bstack1l1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᙌ")):
        return {
            bstack1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᙍ"): bstack1l1_opy_ (u"ࠧ࡝ࡥࡳࡥ࡮ࡩࡷࠨᙎ"),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᙏ"): env.get(bstack1l1_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᙐ")),
            bstack1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᙑ"): bstack1l1_opy_ (u"ࠤࡐࡥ࡮ࡴࠠࡑ࡫ࡳࡩࡱ࡯࡮ࡦࠤᙒ") if env.get(bstack1l1_opy_ (u"࡛ࠥࡊࡘࡃࡌࡇࡕࡣࡒࡇࡉࡏࡡࡓࡍࡕࡋࡌࡊࡐࡈࡣࡘ࡚ࡁࡓࡖࡈࡈࠧᙓ")) else None,
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᙔ"): env.get(bstack1l1_opy_ (u"ࠧ࡝ࡅࡓࡅࡎࡉࡗࡥࡇࡊࡖࡢࡇࡔࡓࡍࡊࡖࠥᙕ"))
        }
    if any([env.get(bstack1l1_opy_ (u"ࠨࡇࡄࡒࡢࡔࡗࡕࡊࡆࡅࡗࠦᙖ")), env.get(bstack1l1_opy_ (u"ࠢࡈࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᙗ")), env.get(bstack1l1_opy_ (u"ࠣࡉࡒࡓࡌࡒࡅࡠࡅࡏࡓ࡚ࡊ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᙘ"))]):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᙙ"): bstack1l1_opy_ (u"ࠥࡋࡴࡵࡧ࡭ࡧࠣࡇࡱࡵࡵࡥࠤᙚ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᙛ"): None,
            bstack1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᙜ"): env.get(bstack1l1_opy_ (u"ࠨࡐࡓࡑࡍࡉࡈ࡚࡟ࡊࡆࠥᙝ")),
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᙞ"): env.get(bstack1l1_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᙟ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࠧᙠ")):
        return {
            bstack1l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᙡ"): bstack1l1_opy_ (u"ࠦࡘ࡮ࡩࡱࡲࡤࡦࡱ࡫ࠢᙢ"),
            bstack1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᙣ"): env.get(bstack1l1_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᙤ")),
            bstack1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᙥ"): bstack1l1_opy_ (u"ࠣࡌࡲࡦࠥࠩࡻࡾࠤᙦ").format(env.get(bstack1l1_opy_ (u"ࠩࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡐࡏࡃࡡࡌࡈࠬᙧ"))) if env.get(bstack1l1_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡊࡐࡄࡢࡍࡉࠨᙨ")) else None,
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᙩ"): env.get(bstack1l1_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࠢᙪ"))
        }
    if bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠨࡎࡆࡖࡏࡍࡋ࡟ࠢᙫ"))):
        return {
            bstack1l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᙬ"): bstack1l1_opy_ (u"ࠣࡐࡨࡸࡱ࡯ࡦࡺࠤ᙭"),
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᙮"): env.get(bstack1l1_opy_ (u"ࠥࡈࡊࡖࡌࡐ࡛ࡢ࡙ࡗࡒࠢᙯ")),
            bstack1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᙰ"): env.get(bstack1l1_opy_ (u"࡙ࠧࡉࡕࡇࡢࡒࡆࡓࡅࠣᙱ")),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᙲ"): env.get(bstack1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤᙳ"))
        }
    if bstack11l1l11l11_opy_(env.get(bstack1l1_opy_ (u"ࠣࡉࡌࡘࡍ࡛ࡂࡠࡃࡆࡘࡎࡕࡎࡔࠤᙴ"))):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᙵ"): bstack1l1_opy_ (u"ࠥࡋ࡮ࡺࡈࡶࡤࠣࡅࡨࡺࡩࡰࡰࡶࠦᙶ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᙷ"): bstack1l1_opy_ (u"ࠧࢁࡽ࠰ࡽࢀ࠳ࡦࡩࡴࡪࡱࡱࡷ࠴ࡸࡵ࡯ࡵ࠲ࡿࢂࠨᙸ").format(env.get(bstack1l1_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡓࡆࡔ࡙ࡉࡗࡥࡕࡓࡎࠪᙹ")), env.get(bstack1l1_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡓࡇࡓࡓࡘࡏࡔࡐࡔ࡜ࠫᙺ")), env.get(bstack1l1_opy_ (u"ࠨࡉࡌࡘࡍ࡛ࡂࡠࡔࡘࡒࡤࡏࡄࠨᙻ"))),
            bstack1l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᙼ"): env.get(bstack1l1_opy_ (u"ࠥࡋࡎ࡚ࡈࡖࡄࡢ࡛ࡔࡘࡋࡇࡎࡒ࡛ࠧᙽ")),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᙾ"): env.get(bstack1l1_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤࡘࡕࡏࡡࡌࡈࠧᙿ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠨࡃࡊࠤ ")) == bstack1l1_opy_ (u"ࠢࡵࡴࡸࡩࠧᚁ") and env.get(bstack1l1_opy_ (u"ࠣࡘࡈࡖࡈࡋࡌࠣᚂ")) == bstack1l1_opy_ (u"ࠤ࠴ࠦᚃ"):
        return {
            bstack1l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᚄ"): bstack1l1_opy_ (u"࡛ࠦ࡫ࡲࡤࡧ࡯ࠦᚅ"),
            bstack1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᚆ"): bstack1l1_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࡻࡾࠤᚇ").format(env.get(bstack1l1_opy_ (u"ࠧࡗࡇࡕࡇࡊࡒ࡟ࡖࡔࡏࠫᚈ"))),
            bstack1l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᚉ"): None,
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᚊ"): None,
        }
    if env.get(bstack1l1_opy_ (u"ࠥࡘࡊࡇࡍࡄࡋࡗ࡝ࡤ࡜ࡅࡓࡕࡌࡓࡓࠨᚋ")):
        return {
            bstack1l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᚌ"): bstack1l1_opy_ (u"࡚ࠧࡥࡢ࡯ࡦ࡭ࡹࡿࠢᚍ"),
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᚎ"): None,
            bstack1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᚏ"): env.get(bstack1l1_opy_ (u"ࠣࡖࡈࡅࡒࡉࡉࡕ࡛ࡢࡔࡗࡕࡊࡆࡅࡗࡣࡓࡇࡍࡆࠤᚐ")),
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᚑ"): env.get(bstack1l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠤᚒ"))
        }
    if any([env.get(bstack1l1_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋࠢᚓ")), env.get(bstack1l1_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡗࡕࡐࠧᚔ")), env.get(bstack1l1_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡘࡗࡊࡘࡎࡂࡏࡈࠦᚕ")), env.get(bstack1l1_opy_ (u"ࠢࡄࡑࡑࡇࡔ࡛ࡒࡔࡇࡢࡘࡊࡇࡍࠣᚖ"))]):
        return {
            bstack1l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᚗ"): bstack1l1_opy_ (u"ࠤࡆࡳࡳࡩ࡯ࡶࡴࡶࡩࠧᚘ"),
            bstack1l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᚙ"): None,
            bstack1l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᚚ"): env.get(bstack1l1_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨ᚛")) or None,
            bstack1l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᚜"): env.get(bstack1l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤ᚝"), 0)
        }
    if env.get(bstack1l1_opy_ (u"ࠣࡉࡒࡣࡏࡕࡂࡠࡐࡄࡑࡊࠨ᚞")):
        return {
            bstack1l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᚟"): bstack1l1_opy_ (u"ࠥࡋࡴࡉࡄࠣᚠ"),
            bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᚡ"): None,
            bstack1l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᚢ"): env.get(bstack1l1_opy_ (u"ࠨࡇࡐࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᚣ")),
            bstack1l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᚤ"): env.get(bstack1l1_opy_ (u"ࠣࡉࡒࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡃࡐࡗࡑࡘࡊࡘࠢᚥ"))
        }
    if env.get(bstack1l1_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᚦ")):
        return {
            bstack1l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᚧ"): bstack1l1_opy_ (u"ࠦࡈࡵࡤࡦࡈࡵࡩࡸ࡮ࠢᚨ"),
            bstack1l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᚩ"): env.get(bstack1l1_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᚪ")),
            bstack1l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᚫ"): env.get(bstack1l1_opy_ (u"ࠣࡅࡉࡣࡕࡏࡐࡆࡎࡌࡒࡊࡥࡎࡂࡏࡈࠦᚬ")),
            bstack1l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᚭ"): env.get(bstack1l1_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᚮ"))
        }
    return {bstack1l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᚯ"): None}
def get_host_info():
    return {
        bstack1l1_opy_ (u"ࠧ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠢᚰ"): platform.node(),
        bstack1l1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠣᚱ"): platform.system(),
        bstack1l1_opy_ (u"ࠢࡵࡻࡳࡩࠧᚲ"): platform.machine(),
        bstack1l1_opy_ (u"ࠣࡸࡨࡶࡸ࡯࡯࡯ࠤᚳ"): platform.version(),
        bstack1l1_opy_ (u"ࠤࡤࡶࡨ࡮ࠢᚴ"): platform.architecture()[0]
    }
def bstack1111111ll_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack11ll1l11ll1_opy_():
    if bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࠫᚵ")):
        return bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᚶ")
    return bstack1l1_opy_ (u"ࠬࡻ࡮࡬ࡰࡲࡻࡳࡥࡧࡳ࡫ࡧࠫᚷ")
def bstack11ll1ll1l1l_opy_(driver):
    info = {
        bstack1l1_opy_ (u"࠭ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᚸ"): driver.capabilities,
        bstack1l1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠫᚹ"): driver.session_id,
        bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࠩᚺ"): driver.capabilities.get(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᚻ"), None),
        bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᚼ"): driver.capabilities.get(bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᚽ"), None),
        bstack1l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࠧᚾ"): driver.capabilities.get(bstack1l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᚿ"), None),
        bstack1l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡡࡹࡩࡷࡹࡩࡰࡰࠪᛀ"):driver.capabilities.get(bstack1l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪᛁ"), None),
    }
    if bstack11ll1l11ll1_opy_() == bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᛂ"):
        if bstack1l1lllllll_opy_():
            info[bstack1l1_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫᛃ")] = bstack1l1_opy_ (u"ࠫࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧࠪᛄ")
        elif driver.capabilities.get(bstack1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᛅ"), {}).get(bstack1l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪᛆ"), False):
            info[bstack1l1_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨᛇ")] = bstack1l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡳࡤࡣ࡯ࡩࠬᛈ")
        else:
            info[bstack1l1_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࠪᛉ")] = bstack1l1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬᛊ")
    return info
def bstack1l1lllllll_opy_():
    if bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪᛋ")):
        return True
    if bstack11l1l11l11_opy_(os.environ.get(bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ᛌ"), None)):
        return True
    return False
def bstack11lll11ll_opy_(bstack11lll1lll1l_opy_, url, data, config):
    headers = config.get(bstack1l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧᛍ"), None)
    proxies = bstack1lll1l11ll_opy_(config, url)
    auth = config.get(bstack1l1_opy_ (u"ࠧࡢࡷࡷ࡬ࠬᛎ"), None)
    response = requests.request(
            bstack11lll1lll1l_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1l1l1l1l_opy_(bstack1l111lll1_opy_, size):
    bstack1ll1lll111_opy_ = []
    while len(bstack1l111lll1_opy_) > size:
        bstack1111l11l1_opy_ = bstack1l111lll1_opy_[:size]
        bstack1ll1lll111_opy_.append(bstack1111l11l1_opy_)
        bstack1l111lll1_opy_ = bstack1l111lll1_opy_[size:]
    bstack1ll1lll111_opy_.append(bstack1l111lll1_opy_)
    return bstack1ll1lll111_opy_
def bstack11ll11lllll_opy_(message, bstack11ll11l11l1_opy_=False):
    os.write(1, bytes(message, bstack1l1_opy_ (u"ࠨࡷࡷࡪ࠲࠾ࠧᛏ")))
    os.write(1, bytes(bstack1l1_opy_ (u"ࠩ࡟ࡲࠬᛐ"), bstack1l1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᛑ")))
    if bstack11ll11l11l1_opy_:
        with open(bstack1l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡴ࠷࠱ࡺ࠯ࠪᛒ") + os.environ[bstack1l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡅ࡙ࡎࡒࡄࡠࡊࡄࡗࡍࡋࡄࡠࡋࡇࠫᛓ")] + bstack1l1_opy_ (u"࠭࠮࡭ࡱࡪࠫᛔ"), bstack1l1_opy_ (u"ࠧࡢࠩᛕ")) as f:
            f.write(message + bstack1l1_opy_ (u"ࠨ࡞ࡱࠫᛖ"))
def bstack1ll111l1111_opy_():
    return os.environ[bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠬᛗ")].lower() == bstack1l1_opy_ (u"ࠪࡸࡷࡻࡥࠨᛘ")
def bstack11lll1ll1_opy_(bstack11lll1ll111_opy_):
    return bstack1l1_opy_ (u"ࠫࢀࢃ࠯ࡼࡿࠪᛙ").format(bstack11lll111l1l_opy_, bstack11lll1ll111_opy_)
def bstack11111l1l1_opy_():
    return bstack111l1111l1_opy_().replace(tzinfo=None).isoformat() + bstack1l1_opy_ (u"ࠬࡠࠧᛚ")
def bstack11ll1l1l1l1_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1l1_opy_ (u"࡚࠭ࠨᛛ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1l1_opy_ (u"࡛ࠧࠩᛜ")))).total_seconds() * 1000
def bstack11lll1111l1_opy_(timestamp):
    return bstack11llll111l1_opy_(timestamp).isoformat() + bstack1l1_opy_ (u"ࠨ࡜ࠪᛝ")
def bstack11lll1lllll_opy_(bstack11llll11l11_opy_):
    date_format = bstack1l1_opy_ (u"ࠩࠨ࡝ࠪࡳࠥࡥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࠲ࠪ࡬ࠧᛞ")
    bstack11lll1111ll_opy_ = datetime.datetime.strptime(bstack11llll11l11_opy_, date_format)
    return bstack11lll1111ll_opy_.isoformat() + bstack1l1_opy_ (u"ࠪ࡞ࠬᛟ")
def bstack11llll1l111_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᛠ")
    else:
        return bstack1l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᛡ")
def bstack11l1l11l11_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1l1_opy_ (u"࠭ࡴࡳࡷࡨࠫᛢ")
def bstack11ll11lll1l_opy_(val):
    return val.__str__().lower() == bstack1l1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ᛣ")
def bstack111l11l111_opy_(bstack11ll1111ll1_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11ll1111ll1_opy_ as e:
                print(bstack1l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡾࢁࠥ࠳࠾ࠡࡽࢀ࠾ࠥࢁࡽࠣᛤ").format(func.__name__, bstack11ll1111ll1_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11ll1111l11_opy_(bstack11ll1l1ll1l_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11ll1l1ll1l_opy_(cls, *args, **kwargs)
            except bstack11ll1111ll1_opy_ as e:
                print(bstack1l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡿࢂࠦ࠭࠿ࠢࡾࢁ࠿ࠦࡻࡾࠤᛥ").format(bstack11ll1l1ll1l_opy_.__name__, bstack11ll1111ll1_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11ll1111l11_opy_
    else:
        return decorator
def bstack11l1l1ll1l_opy_(bstack1111l1lll1_opy_):
    if os.getenv(bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ᛦ")) is not None:
        return bstack11l1l11l11_opy_(os.getenv(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠧᛧ")))
    if bstack1l1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᛨ") in bstack1111l1lll1_opy_ and bstack11ll11lll1l_opy_(bstack1111l1lll1_opy_[bstack1l1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᛩ")]):
        return False
    if bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᛪ") in bstack1111l1lll1_opy_ and bstack11ll11lll1l_opy_(bstack1111l1lll1_opy_[bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪ᛫")]):
        return False
    return True
def bstack1ll11ll1_opy_():
    try:
        from pytest_bdd import reporting
        bstack11llll1l1l1_opy_ = os.environ.get(bstack1l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡗࡖࡉࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠤ᛬"), None)
        return bstack11llll1l1l1_opy_ is None or bstack11llll1l1l1_opy_ == bstack1l1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢ᛭")
    except Exception as e:
        return False
def bstack1ll1l1ll11_opy_(hub_url, CONFIG):
    if bstack1l1lll11_opy_() <= version.parse(bstack1l1_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫᛮ")):
        if hub_url:
            return bstack1l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᛯ") + hub_url + bstack1l1_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥᛰ")
        return bstack1l1llll111_opy_
    if hub_url:
        return bstack1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤᛱ") + hub_url + bstack1l1_opy_ (u"ࠣ࠱ࡺࡨ࠴࡮ࡵࡣࠤᛲ")
    return bstack1l11lll1l1_opy_
def bstack11ll1ll111l_opy_():
    return isinstance(os.getenv(bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒ࡜ࡘࡊ࡙ࡔࡠࡒࡏ࡙ࡌࡏࡎࠨᛳ")), str)
def bstack1l111ll111_opy_(url):
    return urlparse(url).hostname
def bstack1lll1111l_opy_(hostname):
    for bstack1l1l1l1ll1_opy_ in bstack1lllll1l1_opy_:
        regex = re.compile(bstack1l1l1l1ll1_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11ll1lll11l_opy_(bstack11lll1l11ll_opy_, file_name, logger):
    bstack1l1l1l11_opy_ = os.path.join(os.path.expanduser(bstack1l1_opy_ (u"ࠪࢂࠬᛴ")), bstack11lll1l11ll_opy_)
    try:
        if not os.path.exists(bstack1l1l1l11_opy_):
            os.makedirs(bstack1l1l1l11_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1l1_opy_ (u"ࠫࢃ࠭ᛵ")), bstack11lll1l11ll_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1l1_opy_ (u"ࠬࡽࠧᛶ")):
                pass
            with open(file_path, bstack1l1_opy_ (u"ࠨࡷࠬࠤᛷ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack1l1llll11_opy_.format(str(e)))
def bstack11ll11l1l11_opy_(file_name, key, value, logger):
    file_path = bstack11ll1lll11l_opy_(bstack1l1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᛸ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1ll11lll1l_opy_ = json.load(open(file_path, bstack1l1_opy_ (u"ࠨࡴࡥࠫ᛹")))
        else:
            bstack1ll11lll1l_opy_ = {}
        bstack1ll11lll1l_opy_[key] = value
        with open(file_path, bstack1l1_opy_ (u"ࠤࡺ࠯ࠧ᛺")) as outfile:
            json.dump(bstack1ll11lll1l_opy_, outfile)
def bstack11llll11l1_opy_(file_name, logger):
    file_path = bstack11ll1lll11l_opy_(bstack1l1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ᛻"), file_name, logger)
    bstack1ll11lll1l_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1l1_opy_ (u"ࠫࡷ࠭᛼")) as bstack11l1l1l1l_opy_:
            bstack1ll11lll1l_opy_ = json.load(bstack11l1l1l1l_opy_)
    return bstack1ll11lll1l_opy_
def bstack1ll1l11111_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡩ࡭ࡱ࡫࠺ࠡࠩ᛽") + file_path + bstack1l1_opy_ (u"࠭ࠠࠨ᛾") + str(e))
def bstack1l1lll11_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1l1_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤ᛿")
def bstack11llll1l1_opy_(config):
    if bstack1l1_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧᜀ") in config:
        del (config[bstack1l1_opy_ (u"ࠩ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᜁ")])
        return False
    if bstack1l1lll11_opy_() < version.parse(bstack1l1_opy_ (u"ࠪ࠷࠳࠺࠮࠱ࠩᜂ")):
        return False
    if bstack1l1lll11_opy_() >= version.parse(bstack1l1_opy_ (u"ࠫ࠹࠴࠱࠯࠷ࠪᜃ")):
        return True
    if bstack1l1_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬᜄ") in config and config[bstack1l1_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ᜅ")] is False:
        return False
    else:
        return True
def bstack1ll1llll1_opy_(args_list, bstack11lll1l1lll_opy_):
    index = -1
    for value in bstack11lll1l1lll_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11llll111ll_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11llll111ll_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack11l1111l1l_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack11l1111l1l_opy_ = bstack11l1111l1l_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧᜆ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1l1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᜇ"), exception=exception)
    def bstack1111l11l1l_opy_(self):
        if self.result != bstack1l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᜈ"):
            return None
        if isinstance(self.exception_type, str) and bstack1l1_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࠨᜉ") in self.exception_type:
            return bstack1l1_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᜊ")
        return bstack1l1_opy_ (u"࡛ࠧ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࠨᜋ")
    def bstack11lll11111l_opy_(self):
        if self.result != bstack1l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᜌ"):
            return None
        if self.bstack11l1111l1l_opy_:
            return self.bstack11l1111l1l_opy_
        return bstack11l1llll1l1_opy_(self.exception)
def bstack11l1llll1l1_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11ll111l1l1_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l11l1l1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack1l111ll1l1_opy_(config, logger):
    try:
        import playwright
        bstack11ll11l1ll1_opy_ = playwright.__file__
        bstack11ll1l11l11_opy_ = os.path.split(bstack11ll11l1ll1_opy_)
        bstack11ll1l11l1l_opy_ = bstack11ll1l11l11_opy_[0] + bstack1l1_opy_ (u"ࠧ࠰ࡦࡵ࡭ࡻ࡫ࡲ࠰ࡲࡤࡧࡰࡧࡧࡦ࠱࡯࡭ࡧ࠵ࡣ࡭࡫࠲ࡧࡱ࡯࠮࡫ࡵࠪᜍ")
        os.environ[bstack1l1_opy_ (u"ࠨࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜ࠫᜎ")] = bstack11l1l1lll1_opy_(config)
        with open(bstack11ll1l11l1l_opy_, bstack1l1_opy_ (u"ࠩࡵࠫᜏ")) as f:
            bstack1ll1l11lll_opy_ = f.read()
            bstack11lll111111_opy_ = bstack1l1_opy_ (u"ࠪ࡫ࡱࡵࡢࡢ࡮࠰ࡥ࡬࡫࡮ࡵࠩᜐ")
            bstack11ll111l11l_opy_ = bstack1ll1l11lll_opy_.find(bstack11lll111111_opy_)
            if bstack11ll111l11l_opy_ == -1:
              process = subprocess.Popen(bstack1l1_opy_ (u"ࠦࡳࡶ࡭ࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡪࡰࡴࡨࡡ࡭࠯ࡤ࡫ࡪࡴࡴࠣᜑ"), shell=True, cwd=bstack11ll1l11l11_opy_[0])
              process.wait()
              bstack11ll1l1111l_opy_ = bstack1l1_opy_ (u"ࠬࠨࡵࡴࡧࠣࡷࡹࡸࡩࡤࡶࠥ࠿ࠬᜒ")
              bstack11ll11lll11_opy_ = bstack1l1_opy_ (u"ࠨࠢࠣࠢ࡟ࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴ࡝ࠤ࠾ࠤࡨࡵ࡮ࡴࡶࠣࡿࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠡࡿࠣࡁࠥࡸࡥࡲࡷ࡬ࡶࡪ࠮ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭ࠩ࠼ࠢ࡬ࡪࠥ࠮ࡰࡳࡱࡦࡩࡸࡹ࠮ࡦࡰࡹ࠲ࡌࡒࡏࡃࡃࡏࡣࡆࡍࡅࡏࡖࡢࡌ࡙࡚ࡐࡠࡒࡕࡓ࡝࡟ࠩࠡࡤࡲࡳࡹࡹࡴࡳࡣࡳࠬ࠮ࡁࠠࠣࠤࠥᜓ")
              bstack11ll1ll1lll_opy_ = bstack1ll1l11lll_opy_.replace(bstack11ll1l1111l_opy_, bstack11ll11lll11_opy_)
              with open(bstack11ll1l11l1l_opy_, bstack1l1_opy_ (u"ࠧࡸ᜔ࠩ")) as f:
                f.write(bstack11ll1ll1lll_opy_)
    except Exception as e:
        logger.error(bstack1l1l11l1_opy_.format(str(e)))
def bstack1ll11l1l11_opy_():
  try:
    bstack11llll1l11l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠨࡱࡳࡸ࡮ࡳࡡ࡭ࡡ࡫ࡹࡧࡥࡵࡳ࡮࠱࡮ࡸࡵ࡮ࠨ᜕"))
    bstack11l1llll11l_opy_ = []
    if os.path.exists(bstack11llll1l11l_opy_):
      with open(bstack11llll1l11l_opy_) as f:
        bstack11l1llll11l_opy_ = json.load(f)
      os.remove(bstack11llll1l11l_opy_)
    return bstack11l1llll11l_opy_
  except:
    pass
  return []
def bstack1l11ll11l1_opy_(bstack111l1ll1_opy_):
  try:
    bstack11l1llll11l_opy_ = []
    bstack11llll1l11l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠩࡲࡴࡹ࡯࡭ࡢ࡮ࡢ࡬ࡺࡨ࡟ࡶࡴ࡯࠲࡯ࡹ࡯࡯ࠩ᜖"))
    if os.path.exists(bstack11llll1l11l_opy_):
      with open(bstack11llll1l11l_opy_) as f:
        bstack11l1llll11l_opy_ = json.load(f)
    bstack11l1llll11l_opy_.append(bstack111l1ll1_opy_)
    with open(bstack11llll1l11l_opy_, bstack1l1_opy_ (u"ࠪࡻࠬ᜗")) as f:
        json.dump(bstack11l1llll11l_opy_, f)
  except:
    pass
def bstack1llll1l1l_opy_(logger, bstack11l1lllllll_opy_ = False):
  try:
    test_name = os.environ.get(bstack1l1_opy_ (u"ࠫࡕ࡟ࡔࡆࡕࡗࡣ࡙ࡋࡓࡕࡡࡑࡅࡒࡋࠧ᜘"), bstack1l1_opy_ (u"ࠬ࠭᜙"))
    if test_name == bstack1l1_opy_ (u"࠭ࠧ᜚"):
        test_name = threading.current_thread().__dict__.get(bstack1l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࡂࡥࡦࡢࡸࡪࡹࡴࡠࡰࡤࡱࡪ࠭᜛"), bstack1l1_opy_ (u"ࠨࠩ᜜"))
    bstack11ll1llll11_opy_ = bstack1l1_opy_ (u"ࠩ࠯ࠤࠬ᜝").join(threading.current_thread().bstackTestErrorMessages)
    if bstack11l1lllllll_opy_:
        bstack11l111l1l1_opy_ = os.environ.get(bstack1l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪ᜞"), bstack1l1_opy_ (u"ࠫ࠵࠭ᜟ"))
        bstack1l1ll11ll_opy_ = {bstack1l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᜠ"): test_name, bstack1l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᜡ"): bstack11ll1llll11_opy_, bstack1l1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᜢ"): bstack11l111l1l1_opy_}
        bstack11ll1ll11ll_opy_ = []
        bstack11ll11ll11l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡲࡳࡴࡤ࡫ࡲࡳࡱࡵࡣࡱ࡯ࡳࡵ࠰࡭ࡷࡴࡴࠧᜣ"))
        if os.path.exists(bstack11ll11ll11l_opy_):
            with open(bstack11ll11ll11l_opy_) as f:
                bstack11ll1ll11ll_opy_ = json.load(f)
        bstack11ll1ll11ll_opy_.append(bstack1l1ll11ll_opy_)
        with open(bstack11ll11ll11l_opy_, bstack1l1_opy_ (u"ࠩࡺࠫᜤ")) as f:
            json.dump(bstack11ll1ll11ll_opy_, f)
    else:
        bstack1l1ll11ll_opy_ = {bstack1l1_opy_ (u"ࠪࡲࡦࡳࡥࠨᜥ"): test_name, bstack1l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᜦ"): bstack11ll1llll11_opy_, bstack1l1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᜧ"): str(multiprocessing.current_process().name)}
        if bstack1l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪᜨ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l1ll11ll_opy_)
  except Exception as e:
      logger.warn(bstack1l1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡳࡽࡹ࡫ࡳࡵࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᜩ").format(e))
def bstack111lll1l_opy_(error_message, test_name, index, logger):
  try:
    bstack11ll111ll11_opy_ = []
    bstack1l1ll11ll_opy_ = {bstack1l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᜪ"): test_name, bstack1l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᜫ"): error_message, bstack1l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᜬ"): index}
    bstack11llll11l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠫࡷࡵࡢࡰࡶࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᜭ"))
    if os.path.exists(bstack11llll11l1l_opy_):
        with open(bstack11llll11l1l_opy_) as f:
            bstack11ll111ll11_opy_ = json.load(f)
    bstack11ll111ll11_opy_.append(bstack1l1ll11ll_opy_)
    with open(bstack11llll11l1l_opy_, bstack1l1_opy_ (u"ࠬࡽࠧᜮ")) as f:
        json.dump(bstack11ll111ll11_opy_, f)
  except Exception as e:
    logger.warn(bstack1l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡴࡲࡦࡴࡺࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᜯ").format(e))
def bstack11111111_opy_(bstack1lll1l1l1l_opy_, name, logger):
  try:
    bstack1l1ll11ll_opy_ = {bstack1l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᜰ"): name, bstack1l1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᜱ"): bstack1lll1l1l1l_opy_, bstack1l1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᜲ"): str(threading.current_thread()._name)}
    return bstack1l1ll11ll_opy_
  except Exception as e:
    logger.warn(bstack1l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥࡨࡥࡩࡣࡹࡩࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᜳ").format(e))
  return
def bstack11ll111llll_opy_():
    return platform.system() == bstack1l1_opy_ (u"ࠫ࡜࡯࡮ࡥࡱࡺࡷ᜴ࠬ")
def bstack1lll11ll1_opy_(bstack11l1lll1lll_opy_, config, logger):
    bstack11ll1ll1111_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack11l1lll1lll_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡰࡹ࡫ࡲࠡࡥࡲࡲ࡫࡯ࡧࠡ࡭ࡨࡽࡸࠦࡢࡺࠢࡵࡩ࡬࡫ࡸࠡ࡯ࡤࡸࡨ࡮࠺ࠡࡽࢀࠦ᜵").format(e))
    return bstack11ll1ll1111_opy_
def bstack11lll11l11l_opy_(bstack11llll11111_opy_, bstack11lll1ll1ll_opy_):
    bstack11lll1ll1l1_opy_ = version.parse(bstack11llll11111_opy_)
    bstack11ll1lll1ll_opy_ = version.parse(bstack11lll1ll1ll_opy_)
    if bstack11lll1ll1l1_opy_ > bstack11ll1lll1ll_opy_:
        return 1
    elif bstack11lll1ll1l1_opy_ < bstack11ll1lll1ll_opy_:
        return -1
    else:
        return 0
def bstack111l1111l1_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11llll111l1_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack11ll11ll1ll_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1lllll1l11_opy_(options, framework, config, bstack1l11l1111_opy_={}):
    if options is None:
        return
    if getattr(options, bstack1l1_opy_ (u"࠭ࡧࡦࡶࠪ᜶"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1l1ll1lll1_opy_ = caps.get(bstack1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ᜷"))
    bstack11l1llll1ll_opy_ = True
    bstack1lll1l111_opy_ = os.environ[bstack1l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭᜸")]
    bstack1ll11ll11ll_opy_ = config.get(bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ᜹"), False)
    if bstack1ll11ll11ll_opy_:
        bstack1lll111ll11_opy_ = config.get(bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ᜺"), {})
        bstack1lll111ll11_opy_[bstack1l1_opy_ (u"ࠫࡦࡻࡴࡩࡖࡲ࡯ࡪࡴࠧ᜻")] = os.getenv(bstack1l1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪ᜼"))
        bstack11llll1111l_opy_ = json.loads(os.getenv(bstack1l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ᜽"), bstack1l1_opy_ (u"ࠧࡼࡿࠪ᜾"))).get(bstack1l1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᜿"))
    if bstack11ll11lll1l_opy_(caps.get(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩ࡜࠹ࡃࠨᝀ"))) or bstack11ll11lll1l_opy_(caps.get(bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡥࡷ࠴ࡥࠪᝁ"))):
        bstack11l1llll1ll_opy_ = False
    if bstack11llll1l1_opy_({bstack1l1_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦᝂ"): bstack11l1llll1ll_opy_}):
        bstack1l1ll1lll1_opy_ = bstack1l1ll1lll1_opy_ or {}
        bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᝃ")] = bstack11ll11ll1ll_opy_(framework)
        bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᝄ")] = bstack1ll111l1111_opy_()
        bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᝅ")] = bstack1lll1l111_opy_
        bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᝆ")] = bstack1l11l1111_opy_
        if bstack1ll11ll11ll_opy_:
            bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᝇ")] = bstack1ll11ll11ll_opy_
            bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᝈ")] = bstack1lll111ll11_opy_
            bstack1l1ll1lll1_opy_[bstack1l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᝉ")][bstack1l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᝊ")] = bstack11llll1111l_opy_
        if getattr(options, bstack1l1_opy_ (u"࠭ࡳࡦࡶࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹࡿࠧᝋ"), None):
            options.set_capability(bstack1l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᝌ"), bstack1l1ll1lll1_opy_)
        else:
            options[bstack1l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᝍ")] = bstack1l1ll1lll1_opy_
    else:
        if getattr(options, bstack1l1_opy_ (u"ࠩࡶࡩࡹࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵࡻࠪᝎ"), None):
            options.set_capability(bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᝏ"), bstack11ll11ll1ll_opy_(framework))
            options.set_capability(bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᝐ"), bstack1ll111l1111_opy_())
            options.set_capability(bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᝑ"), bstack1lll1l111_opy_)
            options.set_capability(bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᝒ"), bstack1l11l1111_opy_)
            if bstack1ll11ll11ll_opy_:
                options.set_capability(bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᝓ"), bstack1ll11ll11ll_opy_)
                options.set_capability(bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᝔"), bstack1lll111ll11_opy_)
                options.set_capability(bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳ࠯ࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᝕"), bstack11llll1111l_opy_)
        else:
            options[bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫ᝖")] = bstack11ll11ll1ll_opy_(framework)
            options[bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ᝗")] = bstack1ll111l1111_opy_()
            options[bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧ᝘")] = bstack1lll1l111_opy_
            options[bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧ᝙")] = bstack1l11l1111_opy_
            if bstack1ll11ll11ll_opy_:
                options[bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭᝚")] = bstack1ll11ll11ll_opy_
                options[bstack1l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᝛")] = bstack1lll111ll11_opy_
                options[bstack1l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᝜")][bstack1l1_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ᝝")] = bstack11llll1111l_opy_
    return options
def bstack11lll1llll1_opy_(bstack11lll1l1111_opy_, framework):
    bstack1l11l1111_opy_ = bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠦࡕࡒࡁ࡚࡙ࡕࡍࡌࡎࡔࡠࡒࡕࡓࡉ࡛ࡃࡕࡡࡐࡅࡕࠨ᝞"))
    if bstack11lll1l1111_opy_ and len(bstack11lll1l1111_opy_.split(bstack1l1_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫ᝟"))) > 1:
        ws_url = bstack11lll1l1111_opy_.split(bstack1l1_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᝠ"))[0]
        if bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪᝡ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack11lll1l11l1_opy_ = json.loads(urllib.parse.unquote(bstack11lll1l1111_opy_.split(bstack1l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᝢ"))[1]))
            bstack11lll1l11l1_opy_ = bstack11lll1l11l1_opy_ or {}
            bstack1lll1l111_opy_ = os.environ[bstack1l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᝣ")]
            bstack11lll1l11l1_opy_[bstack1l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᝤ")] = str(framework) + str(__version__)
            bstack11lll1l11l1_opy_[bstack1l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᝥ")] = bstack1ll111l1111_opy_()
            bstack11lll1l11l1_opy_[bstack1l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᝦ")] = bstack1lll1l111_opy_
            bstack11lll1l11l1_opy_[bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᝧ")] = bstack1l11l1111_opy_
            bstack11lll1l1111_opy_ = bstack11lll1l1111_opy_.split(bstack1l1_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᝨ"))[0] + bstack1l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᝩ") + urllib.parse.quote(json.dumps(bstack11lll1l11l1_opy_))
    return bstack11lll1l1111_opy_
def bstack1l1l1lll_opy_():
    global bstack11l1111l_opy_
    from playwright._impl._browser_type import BrowserType
    bstack11l1111l_opy_ = BrowserType.connect
    return bstack11l1111l_opy_
def bstack1ll1l1111l_opy_(framework_name):
    global bstack1ll1lll11_opy_
    bstack1ll1lll11_opy_ = framework_name
    return framework_name
def bstack1111l1l1l_opy_(self, *args, **kwargs):
    global bstack11l1111l_opy_
    try:
        global bstack1ll1lll11_opy_
        if bstack1l1_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭ᝪ") in kwargs:
            kwargs[bstack1l1_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᝫ")] = bstack11lll1llll1_opy_(
                kwargs.get(bstack1l1_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᝬ"), None),
                bstack1ll1lll11_opy_
            )
    except Exception as e:
        logger.error(bstack1l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡥ࡯ࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡓࡅࡍࠣࡧࡦࡶࡳ࠻ࠢࡾࢁࠧ᝭").format(str(e)))
    return bstack11l1111l_opy_(self, *args, **kwargs)
def bstack11ll1lll111_opy_(bstack11lll11l111_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1lll1l11ll_opy_(bstack11lll11l111_opy_, bstack1l1_opy_ (u"ࠨࠢᝮ"))
        if proxies and proxies.get(bstack1l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᝯ")):
            parsed_url = urlparse(proxies.get(bstack1l1_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᝰ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡉࡱࡶࡸࠬ᝱")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡲࡶࡹ࠭ᝲ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡘࡷࡪࡸࠧᝳ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡦࡹࡳࠨ᝴")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11l1l1l111_opy_(bstack11lll11l111_opy_):
    bstack11ll111ll1l_opy_ = {
        bstack11ll1ll11l1_opy_[bstack11llll11ll1_opy_]: bstack11lll11l111_opy_[bstack11llll11ll1_opy_]
        for bstack11llll11ll1_opy_ in bstack11lll11l111_opy_
        if bstack11llll11ll1_opy_ in bstack11ll1ll11l1_opy_
    }
    bstack11ll111ll1l_opy_[bstack1l1_opy_ (u"ࠨࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࠨ᝵")] = bstack11ll1lll111_opy_(bstack11lll11l111_opy_, bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠢࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠢ᝶")))
    bstack11ll1l1l111_opy_ = [element.lower() for element in bstack11ll11111ll_opy_]
    bstack11ll1l11111_opy_(bstack11ll111ll1l_opy_, bstack11ll1l1l111_opy_)
    return bstack11ll111ll1l_opy_
def bstack11ll1l11111_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1l1_opy_ (u"ࠣࠬ࠭࠮࠯ࠨ᝷")
    for value in d.values():
        if isinstance(value, dict):
            bstack11ll1l11111_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack11ll1l11111_opy_(item, keys)
def bstack1l1llll11l1_opy_():
    bstack11ll1l1l11l_opy_ = [os.environ.get(bstack1l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡌࡐࡊ࡙࡟ࡅࡋࡕࠦ᝸")), os.path.join(os.path.expanduser(bstack1l1_opy_ (u"ࠥࢂࠧ᝹")), bstack1l1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ᝺")), os.path.join(bstack1l1_opy_ (u"ࠬ࠵ࡴ࡮ࡲࠪ᝻"), bstack1l1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭᝼"))]
    for path in bstack11ll1l1l11l_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack1l1_opy_ (u"ࠢࡇ࡫࡯ࡩࠥ࠭ࠢ᝽") + str(path) + bstack1l1_opy_ (u"ࠣࠩࠣࡩࡽ࡯ࡳࡵࡵ࠱ࠦ᝾"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack1l1_opy_ (u"ࠤࡊ࡭ࡻ࡯࡮ࡨࠢࡳࡩࡷࡳࡩࡴࡵ࡬ࡳࡳࡹࠠࡧࡱࡵࠤࠬࠨ᝿") + str(path) + bstack1l1_opy_ (u"ࠥࠫࠧក"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack1l1_opy_ (u"ࠦࡋ࡯࡬ࡦࠢࠪࠦខ") + str(path) + bstack1l1_opy_ (u"ࠧ࠭ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡪࡤࡷࠥࡺࡨࡦࠢࡵࡩࡶࡻࡩࡳࡧࡧࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴ࠰ࠥគ"))
            else:
                logger.debug(bstack1l1_opy_ (u"ࠨࡃࡳࡧࡤࡸ࡮ࡴࡧࠡࡨ࡬ࡰࡪࠦࠧࠣឃ") + str(path) + bstack1l1_opy_ (u"ࠢࠨࠢࡺ࡭ࡹ࡮ࠠࡸࡴ࡬ࡸࡪࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰ࠱ࠦង"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack1l1_opy_ (u"ࠣࡑࡳࡩࡷࡧࡴࡪࡱࡱࠤࡸࡻࡣࡤࡧࡨࡨࡪࡪࠠࡧࡱࡵࠤࠬࠨច") + str(path) + bstack1l1_opy_ (u"ࠤࠪ࠲ࠧឆ"))
            return path
        except Exception as e:
            logger.debug(bstack1l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡹࡵࠦࡦࡪ࡮ࡨࠤࠬࢁࡰࡢࡶ࡫ࢁࠬࡀࠠࠣជ") + str(e) + bstack1l1_opy_ (u"ࠦࠧឈ"))
    logger.debug(bstack1l1_opy_ (u"ࠧࡇ࡬࡭ࠢࡳࡥࡹ࡮ࡳࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠤញ"))
    return None
@measure(event_name=EVENTS.bstack11ll1l111l1_opy_, stage=STAGE.bstack1111lll11_opy_)
def bstack1lll1ll1ll1_opy_(binary_path, bstack1llll11l1ll_opy_, bs_config):
    logger.debug(bstack1l1_opy_ (u"ࠨࡃࡶࡴࡵࡩࡳࡺࠠࡄࡎࡌࠤࡕࡧࡴࡩࠢࡩࡳࡺࡴࡤ࠻ࠢࡾࢁࠧដ").format(binary_path))
    bstack11ll1ll1l11_opy_ = bstack1l1_opy_ (u"ࠧࠨឋ")
    bstack11ll111l111_opy_ = {
        bstack1l1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ឌ"): __version__,
        bstack1l1_opy_ (u"ࠤࡲࡷࠧឍ"): platform.system(),
        bstack1l1_opy_ (u"ࠥࡳࡸࡥࡡࡳࡥ࡫ࠦណ"): platform.machine(),
        bstack1l1_opy_ (u"ࠦࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠤត"): bstack1l1_opy_ (u"ࠬ࠶ࠧថ"),
        bstack1l1_opy_ (u"ࠨࡳࡥ࡭ࡢࡰࡦࡴࡧࡶࡣࡪࡩࠧទ"): bstack1l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧធ")
    }
    bstack11llll11lll_opy_(bstack11ll111l111_opy_)
    try:
        if binary_path:
            bstack11ll111l111_opy_[bstack1l1_opy_ (u"ࠨࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ន")] = subprocess.check_output([binary_path, bstack1l1_opy_ (u"ࠤࡹࡩࡷࡹࡩࡰࡰࠥប")]).strip().decode(bstack1l1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩផ"))
        response = requests.request(
            bstack1l1_opy_ (u"ࠫࡌࡋࡔࠨព"),
            url=bstack11lll1ll1_opy_(bstack11ll11l1l1l_opy_),
            headers=None,
            auth=(bs_config[bstack1l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧភ")], bs_config[bstack1l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩម")]),
            json=None,
            params=bstack11ll111l111_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack1l1_opy_ (u"ࠧࡶࡴ࡯ࠫយ") in data.keys() and bstack1l1_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡥࡡࡦࡰ࡮ࡥࡶࡦࡴࡶ࡭ࡴࡴࠧរ") in data.keys():
            logger.debug(bstack1l1_opy_ (u"ࠤࡑࡩࡪࡪࠠࡵࡱࠣࡹࡵࡪࡡࡵࡧࠣࡦ࡮ࡴࡡࡳࡻ࠯ࠤࡨࡻࡲࡳࡧࡱࡸࠥࡨࡩ࡯ࡣࡵࡽࠥࡼࡥࡳࡵ࡬ࡳࡳࡀࠠࡼࡿࠥល").format(bstack11ll111l111_opy_[bstack1l1_opy_ (u"ࠪࡧࡱ࡯࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨវ")]))
            if bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢ࡙ࡗࡒࠧឝ") in os.environ:
                logger.debug(bstack1l1_opy_ (u"࡙ࠧ࡫ࡪࡲࡳ࡭ࡳ࡭ࠠࡣ࡫ࡱࡥࡷࡿࠠࡥࡱࡺࡲࡱࡵࡡࡥࠢࡤࡷࠥࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡘࡊࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡗࡕࡐࠥ࡯ࡳࠡࡵࡨࡸࠧឞ"))
                data[bstack1l1_opy_ (u"࠭ࡵࡳ࡮ࠪស")] = os.environ[bstack1l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡕࡓࡎࠪហ")]
            bstack11ll1l1lll1_opy_ = bstack11ll11llll1_opy_(data[bstack1l1_opy_ (u"ࠨࡷࡵࡰࠬឡ")], bstack1llll11l1ll_opy_)
            bstack11ll1ll1l11_opy_ = os.path.join(bstack1llll11l1ll_opy_, bstack11ll1l1lll1_opy_)
            os.chmod(bstack11ll1ll1l11_opy_, 0o777) # bstack11ll1l11lll_opy_ permission
            return bstack11ll1ll1l11_opy_
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡥࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡴࡥࡸࠢࡖࡈࡐࠦࡻࡾࠤអ").format(e))
    return binary_path
def bstack11llll11lll_opy_(bstack11ll111l111_opy_):
    try:
        if bstack1l1_opy_ (u"ࠪࡰ࡮ࡴࡵࡹࠩឣ") not in bstack11ll111l111_opy_[bstack1l1_opy_ (u"ࠫࡴࡹࠧឤ")].lower():
            return
        if os.path.exists(bstack1l1_opy_ (u"ࠧ࠵ࡥࡵࡥ࠲ࡳࡸ࠳ࡲࡦ࡮ࡨࡥࡸ࡫ࠢឥ")):
            with open(bstack1l1_opy_ (u"ࠨ࠯ࡦࡶࡦ࠳ࡴࡹ࠭ࡳࡧ࡯ࡩࡦࡹࡥࠣឦ"), bstack1l1_opy_ (u"ࠢࡳࠤឧ")) as f:
                bstack11ll11ll111_opy_ = {}
                for line in f:
                    if bstack1l1_opy_ (u"ࠣ࠿ࠥឨ") in line:
                        key, value = line.rstrip().split(bstack1l1_opy_ (u"ࠤࡀࠦឩ"), 1)
                        bstack11ll11ll111_opy_[key] = value.strip(bstack1l1_opy_ (u"ࠪࠦࡡ࠭ࠧឪ"))
                bstack11ll111l111_opy_[bstack1l1_opy_ (u"ࠫࡩ࡯ࡳࡵࡴࡲࠫឫ")] = bstack11ll11ll111_opy_.get(bstack1l1_opy_ (u"ࠧࡏࡄࠣឬ"), bstack1l1_opy_ (u"ࠨࠢឭ"))
        elif os.path.exists(bstack1l1_opy_ (u"ࠢ࠰ࡧࡷࡧ࠴ࡧ࡬ࡱ࡫ࡱࡩ࠲ࡸࡥ࡭ࡧࡤࡷࡪࠨឮ")):
            bstack11ll111l111_opy_[bstack1l1_opy_ (u"ࠨࡦ࡬ࡷࡹࡸ࡯ࠨឯ")] = bstack1l1_opy_ (u"ࠩࡤࡰࡵ࡯࡮ࡦࠩឰ")
    except Exception as e:
        logger.debug(bstack1l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡧࡦࡶࠣࡨ࡮ࡹࡴࡳࡱࠣࡳ࡫ࠦ࡬ࡪࡰࡸࡼࠧឱ") + e)
@measure(event_name=EVENTS.bstack11ll1lll1l1_opy_, stage=STAGE.bstack1111lll11_opy_)
def bstack11ll11llll1_opy_(bstack11lll11llll_opy_, bstack11ll111lll1_opy_):
    logger.debug(bstack1l1_opy_ (u"ࠦࡉࡵࡷ࡯࡮ࡲࡥࡩ࡯࡮ࡨࠢࡖࡈࡐࠦࡢࡪࡰࡤࡶࡾࠦࡦࡳࡱࡰ࠾ࠥࠨឲ") + str(bstack11lll11llll_opy_) + bstack1l1_opy_ (u"ࠧࠨឳ"))
    zip_path = os.path.join(bstack11ll111lll1_opy_, bstack1l1_opy_ (u"ࠨࡤࡰࡹࡱࡰࡴࡧࡤࡦࡦࡢࡪ࡮ࡲࡥ࠯ࡼ࡬ࡴࠧ឴"))
    bstack11ll1l1lll1_opy_ = bstack1l1_opy_ (u"ࠧࠨ឵")
    with requests.get(bstack11lll11llll_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack1l1_opy_ (u"ࠣࡹࡥࠦា")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack1l1_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࡥࡱࡺࡲࡱࡵࡡࡥࡧࡧࠤࡸࡻࡣࡤࡧࡶࡷ࡫ࡻ࡬࡭ࡻ࠱ࠦិ"))
    with zipfile.ZipFile(zip_path, bstack1l1_opy_ (u"ࠪࡶࠬី")) as zip_ref:
        bstack11l1lllll11_opy_ = zip_ref.namelist()
        if len(bstack11l1lllll11_opy_) > 0:
            bstack11ll1l1lll1_opy_ = bstack11l1lllll11_opy_[0] # bstack11ll1l1llll_opy_ bstack11lll11ll11_opy_ will be bstack11lll111l11_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11ll111lll1_opy_)
        logger.debug(bstack1l1_opy_ (u"ࠦࡋ࡯࡬ࡦࡵࠣࡷࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡨࡼࡹࡸࡡࡤࡶࡨࡨࠥࡺ࡯ࠡࠩࠥឹ") + str(bstack11ll111lll1_opy_) + bstack1l1_opy_ (u"ࠧ࠭ࠢឺ"))
    os.remove(zip_path)
    return bstack11ll1l1lll1_opy_
def get_cli_dir():
    bstack11lll111ll1_opy_ = bstack1l1llll11l1_opy_()
    if bstack11lll111ll1_opy_:
        bstack1llll11l1ll_opy_ = os.path.join(bstack11lll111ll1_opy_, bstack1l1_opy_ (u"ࠨࡣ࡭࡫ࠥុ"))
        if not os.path.exists(bstack1llll11l1ll_opy_):
            os.makedirs(bstack1llll11l1ll_opy_, mode=0o777, exist_ok=True)
        return bstack1llll11l1ll_opy_
    else:
        raise FileNotFoundError(bstack1l1_opy_ (u"ࠢࡏࡱࠣࡻࡷ࡯ࡴࡢࡤ࡯ࡩࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡣࡹࡥ࡮ࡲࡡࡣ࡮ࡨࠤ࡫ࡵࡲࠡࡶ࡫ࡩ࡙ࠥࡄࡌࠢࡥ࡭ࡳࡧࡲࡺ࠰ࠥូ"))
def bstack1lll11l11ll_opy_(bstack1llll11l1ll_opy_):
    bstack1l1_opy_ (u"ࠣࠤࠥࡋࡪࡺࠠࡵࡪࡨࠤࡵࡧࡴࡩࠢࡩࡳࡷࠦࡴࡩࡧࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡖࡈࡐࠦࡢࡪࡰࡤࡶࡾࠦࡩ࡯ࠢࡤࠤࡼࡸࡩࡵࡣࡥࡰࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺ࠰ࠥࠦࠧួ")
    bstack11lll1l111l_opy_ = [
        os.path.join(bstack1llll11l1ll_opy_, f)
        for f in os.listdir(bstack1llll11l1ll_opy_)
        if os.path.isfile(os.path.join(bstack1llll11l1ll_opy_, f)) and f.startswith(bstack1l1_opy_ (u"ࠤࡥ࡭ࡳࡧࡲࡺ࠯ࠥើ"))
    ]
    if len(bstack11lll1l111l_opy_) > 0:
        return max(bstack11lll1l111l_opy_, key=os.path.getmtime) # get bstack11l1lllll1l_opy_ binary
    return bstack1l1_opy_ (u"ࠥࠦឿ")
def bstack11ll11l1111_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1l1lll11_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll1l1lll11_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d