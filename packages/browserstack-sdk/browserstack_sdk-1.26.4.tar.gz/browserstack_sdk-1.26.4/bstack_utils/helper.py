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
from bstack_utils.constants import (bstack11l11lll111_opy_, bstack1ll11l1l_opy_, bstack111l1l111_opy_, bstack1l111l11_opy_,
                                    bstack11l11lll1ll_opy_, bstack11l11llll1l_opy_, bstack11l1l111l11_opy_, bstack11l11llllll_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11llll11ll_opy_, bstack11lll11111_opy_
from bstack_utils.proxy import bstack1ll1l111l1_opy_, bstack1l1111l11_opy_
from bstack_utils.constants import *
from bstack_utils import bstack111ll11ll_opy_
from browserstack_sdk._version import __version__
bstack1lll1111ll_opy_ = Config.bstack11ll1l1l_opy_()
logger = bstack111ll11ll_opy_.get_logger(__name__, bstack111ll11ll_opy_.bstack1llll1ll11l_opy_())
def bstack11l1ll1l11l_opy_(config):
    return config[bstack1ll_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨᫀࠫ")]
def bstack11ll111111l_opy_(config):
    return config[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭᫁")]
def bstack11l1l11ll1_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack11l111lll1l_opy_(obj):
    values = []
    bstack111ll1ll11l_opy_ = re.compile(bstack1ll_opy_ (u"ࡶࠧࡤࡃࡖࡕࡗࡓࡒࡥࡔࡂࡉࡢࡠࡩ࠱ࠤࠣ᫂"), re.I)
    for key in obj.keys():
        if bstack111ll1ll11l_opy_.match(key):
            values.append(obj[key])
    return values
def bstack111ll1l1lll_opy_(config):
    tags = []
    tags.extend(bstack11l111lll1l_opy_(os.environ))
    tags.extend(bstack11l111lll1l_opy_(config))
    return tags
def bstack111ll1l1111_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111llll1111_opy_(bstack111lllll111_opy_):
    if not bstack111lllll111_opy_:
        return bstack1ll_opy_ (u"᫃ࠬ࠭")
    return bstack1ll_opy_ (u"ࠨࡻࡾࠢࠫࡿࢂ࠯᫄ࠢ").format(bstack111lllll111_opy_.name, bstack111lllll111_opy_.email)
def bstack11l1lll11l1_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack111lll111ll_opy_ = repo.common_dir
        info = {
            bstack1ll_opy_ (u"ࠢࡴࡪࡤࠦ᫅"): repo.head.commit.hexsha,
            bstack1ll_opy_ (u"ࠣࡵ࡫ࡳࡷࡺ࡟ࡴࡪࡤࠦ᫆"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1ll_opy_ (u"ࠤࡥࡶࡦࡴࡣࡩࠤ᫇"): repo.active_branch.name,
            bstack1ll_opy_ (u"ࠥࡸࡦ࡭ࠢ᫈"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1ll_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡸࡪࡸࠢ᫉"): bstack111llll1111_opy_(repo.head.commit.committer),
            bstack1ll_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡹ࡫ࡲࡠࡦࡤࡸࡪࠨ᫊"): repo.head.commit.committed_datetime.isoformat(),
            bstack1ll_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࠨ᫋"): bstack111llll1111_opy_(repo.head.commit.author),
            bstack1ll_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸ࡟ࡥࡣࡷࡩࠧᫌ"): repo.head.commit.authored_datetime.isoformat(),
            bstack1ll_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᫍ"): repo.head.commit.message,
            bstack1ll_opy_ (u"ࠤࡵࡳࡴࡺࠢᫎ"): repo.git.rev_parse(bstack1ll_opy_ (u"ࠥ࠱࠲ࡹࡨࡰࡹ࠰ࡸࡴࡶ࡬ࡦࡸࡨࡰࠧ᫏")),
            bstack1ll_opy_ (u"ࠦࡨࡵ࡭࡮ࡱࡱࡣ࡬࡯ࡴࡠࡦ࡬ࡶࠧ᫐"): bstack111lll111ll_opy_,
            bstack1ll_opy_ (u"ࠧࡽ࡯ࡳ࡭ࡷࡶࡪ࡫࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣ᫑"): subprocess.check_output([bstack1ll_opy_ (u"ࠨࡧࡪࡶࠥ᫒"), bstack1ll_opy_ (u"ࠢࡳࡧࡹ࠱ࡵࡧࡲࡴࡧࠥ᫓"), bstack1ll_opy_ (u"ࠣ࠯࠰࡫࡮ࡺ࠭ࡤࡱࡰࡱࡴࡴ࠭ࡥ࡫ࡵࠦ᫔")]).strip().decode(
                bstack1ll_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨ᫕")),
            bstack1ll_opy_ (u"ࠥࡰࡦࡹࡴࡠࡶࡤ࡫ࠧ᫖"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1ll_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡷࡤࡹࡩ࡯ࡥࡨࡣࡱࡧࡳࡵࡡࡷࡥ࡬ࠨ᫗"): repo.git.rev_list(
                bstack1ll_opy_ (u"ࠧࢁࡽ࠯࠰ࡾࢁࠧ᫘").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack11l111ll1l1_opy_ = []
        for remote in remotes:
            bstack11l1111l1ll_opy_ = {
                bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ᫙"): remote.name,
                bstack1ll_opy_ (u"ࠢࡶࡴ࡯ࠦ᫚"): remote.url,
            }
            bstack11l111ll1l1_opy_.append(bstack11l1111l1ll_opy_)
        bstack11l1111llll_opy_ = {
            bstack1ll_opy_ (u"ࠣࡰࡤࡱࡪࠨ᫛"): bstack1ll_opy_ (u"ࠤࡪ࡭ࡹࠨ᫜"),
            **info,
            bstack1ll_opy_ (u"ࠥࡶࡪࡳ࡯ࡵࡧࡶࠦ᫝"): bstack11l111ll1l1_opy_
        }
        bstack11l1111llll_opy_ = bstack111ll11lll1_opy_(bstack11l1111llll_opy_)
        return bstack11l1111llll_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1ll_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡴࡶࡵ࡭ࡣࡷ࡭ࡳ࡭ࠠࡈ࡫ࡷࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢ᫞").format(err))
        return {}
def bstack111ll11lll1_opy_(bstack11l1111llll_opy_):
    bstack11l11l1ll1l_opy_ = bstack111llll1l11_opy_(bstack11l1111llll_opy_)
    if bstack11l11l1ll1l_opy_ and bstack11l11l1ll1l_opy_ > bstack11l11lll1ll_opy_:
        bstack111lllll1ll_opy_ = bstack11l11l1ll1l_opy_ - bstack11l11lll1ll_opy_
        bstack11l11l1111l_opy_ = bstack11l11l1ll11_opy_(bstack11l1111llll_opy_[bstack1ll_opy_ (u"ࠧࡩ࡯࡮࡯࡬ࡸࡤࡳࡥࡴࡵࡤ࡫ࡪࠨ᫟")], bstack111lllll1ll_opy_)
        bstack11l1111llll_opy_[bstack1ll_opy_ (u"ࠨࡣࡰ࡯ࡰ࡭ࡹࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠢ᫠")] = bstack11l11l1111l_opy_
        logger.info(bstack1ll_opy_ (u"ࠢࡕࡪࡨࠤࡨࡵ࡭࡮࡫ࡷࠤ࡭ࡧࡳࠡࡤࡨࡩࡳࠦࡴࡳࡷࡱࡧࡦࡺࡥࡥ࠰ࠣࡗ࡮ࢀࡥࠡࡱࡩࠤࡨࡵ࡭࡮࡫ࡷࠤࡦ࡬ࡴࡦࡴࠣࡸࡷࡻ࡮ࡤࡣࡷ࡭ࡴࡴࠠࡪࡵࠣࡿࢂࠦࡋࡃࠤ᫡")
                    .format(bstack111llll1l11_opy_(bstack11l1111llll_opy_) / 1024))
    return bstack11l1111llll_opy_
def bstack111llll1l11_opy_(bstack1l1ll11ll1_opy_):
    try:
        if bstack1l1ll11ll1_opy_:
            bstack11l111lllll_opy_ = json.dumps(bstack1l1ll11ll1_opy_)
            bstack111llllll1l_opy_ = sys.getsizeof(bstack11l111lllll_opy_)
            return bstack111llllll1l_opy_
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠣࡕࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡣ࡯ࡧࡺࡲࡡࡵ࡫ࡱ࡫ࠥࡹࡩࡻࡧࠣࡳ࡫ࠦࡊࡔࡑࡑࠤࡴࡨࡪࡦࡥࡷ࠾ࠥࢁࡽࠣ᫢").format(e))
    return -1
def bstack11l11l1ll11_opy_(field, bstack11l111lll11_opy_):
    try:
        bstack111ll11ll11_opy_ = len(bytes(bstack11l11llll1l_opy_, bstack1ll_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨ᫣")))
        bstack11l111l1lll_opy_ = bytes(field, bstack1ll_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩ᫤"))
        bstack111ll1lll1l_opy_ = len(bstack11l111l1lll_opy_)
        bstack11l11l111l1_opy_ = ceil(bstack111ll1lll1l_opy_ - bstack11l111lll11_opy_ - bstack111ll11ll11_opy_)
        if bstack11l11l111l1_opy_ > 0:
            bstack11l1111ll11_opy_ = bstack11l111l1lll_opy_[:bstack11l11l111l1_opy_].decode(bstack1ll_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪ᫥"), errors=bstack1ll_opy_ (u"ࠬ࡯ࡧ࡯ࡱࡵࡩࠬ᫦")) + bstack11l11llll1l_opy_
            return bstack11l1111ll11_opy_
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡹࡸࡵ࡯ࡥࡤࡸ࡮ࡴࡧࠡࡨ࡬ࡩࡱࡪࠬࠡࡰࡲࡸ࡭࡯࡮ࡨࠢࡺࡥࡸࠦࡴࡳࡷࡱࡧࡦࡺࡥࡥࠢ࡫ࡩࡷ࡫࠺ࠡࡽࢀࠦ᫧").format(e))
    return field
def bstack11l1lll1_opy_():
    env = os.environ
    if (bstack1ll_opy_ (u"ࠢࡋࡇࡑࡏࡎࡔࡓࡠࡗࡕࡐࠧ᫨") in env and len(env[bstack1ll_opy_ (u"ࠣࡌࡈࡒࡐࡏࡎࡔࡡࡘࡖࡑࠨ᫩")]) > 0) or (
            bstack1ll_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢࡌࡔࡓࡅࠣ᫪") in env and len(env[bstack1ll_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣࡍࡕࡍࡆࠤ᫫")]) > 0):
        return {
            bstack1ll_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᫬"): bstack1ll_opy_ (u"ࠧࡐࡥ࡯࡭࡬ࡲࡸࠨ᫭"),
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤ᫮"): env.get(bstack1ll_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡕࡓࡎࠥ᫯")),
            bstack1ll_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥ᫰"): env.get(bstack1ll_opy_ (u"ࠤࡍࡓࡇࡥࡎࡂࡏࡈࠦ᫱")),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᫲"): env.get(bstack1ll_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥ᫳"))
        }
    if env.get(bstack1ll_opy_ (u"ࠧࡉࡉࠣ᫴")) == bstack1ll_opy_ (u"ࠨࡴࡳࡷࡨࠦ᫵") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠢࡄࡋࡕࡇࡑࡋࡃࡊࠤ᫶"))):
        return {
            bstack1ll_opy_ (u"ࠣࡰࡤࡱࡪࠨ᫷"): bstack1ll_opy_ (u"ࠤࡆ࡭ࡷࡩ࡬ࡦࡅࡌࠦ᫸"),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᫹"): env.get(bstack1ll_opy_ (u"ࠦࡈࡏࡒࡄࡎࡈࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢ᫺")),
            bstack1ll_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᫻"): env.get(bstack1ll_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡥࡊࡐࡄࠥ᫼")),
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᫽"): env.get(bstack1ll_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࠦ᫾"))
        }
    if env.get(bstack1ll_opy_ (u"ࠤࡆࡍࠧ᫿")) == bstack1ll_opy_ (u"ࠥࡸࡷࡻࡥࠣᬀ") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"࡙ࠦࡘࡁࡗࡋࡖࠦᬁ"))):
        return {
            bstack1ll_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᬂ"): bstack1ll_opy_ (u"ࠨࡔࡳࡣࡹ࡭ࡸࠦࡃࡊࠤᬃ"),
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᬄ"): env.get(bstack1ll_opy_ (u"ࠣࡖࡕࡅ࡛ࡏࡓࡠࡄࡘࡍࡑࡊ࡟ࡘࡇࡅࡣ࡚ࡘࡌࠣᬅ")),
            bstack1ll_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᬆ"): env.get(bstack1ll_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᬇ")),
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᬈ"): env.get(bstack1ll_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᬉ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠨࡃࡊࠤᬊ")) == bstack1ll_opy_ (u"ࠢࡵࡴࡸࡩࠧᬋ") and env.get(bstack1ll_opy_ (u"ࠣࡅࡌࡣࡓࡇࡍࡆࠤᬌ")) == bstack1ll_opy_ (u"ࠤࡦࡳࡩ࡫ࡳࡩ࡫ࡳࠦᬍ"):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣᬎ"): bstack1ll_opy_ (u"ࠦࡈࡵࡤࡦࡵ࡫࡭ࡵࠨᬏ"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᬐ"): None,
            bstack1ll_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᬑ"): None,
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᬒ"): None
        }
    if env.get(bstack1ll_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠦᬓ")) and env.get(bstack1ll_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠧᬔ")):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣᬕ"): bstack1ll_opy_ (u"ࠦࡇ࡯ࡴࡣࡷࡦ࡯ࡪࡺࠢᬖ"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᬗ"): env.get(bstack1ll_opy_ (u"ࠨࡂࡊࡖࡅ࡙ࡈࡑࡅࡕࡡࡊࡍ࡙ࡥࡈࡕࡖࡓࡣࡔࡘࡉࡈࡋࡑࠦᬘ")),
            bstack1ll_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᬙ"): None,
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᬚ"): env.get(bstack1ll_opy_ (u"ࠤࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᬛ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠥࡇࡎࠨᬜ")) == bstack1ll_opy_ (u"ࠦࡹࡸࡵࡦࠤᬝ") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠧࡊࡒࡐࡐࡈࠦᬞ"))):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᬟ"): bstack1ll_opy_ (u"ࠢࡅࡴࡲࡲࡪࠨᬠ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᬡ"): env.get(bstack1ll_opy_ (u"ࠤࡇࡖࡔࡔࡅࡠࡄࡘࡍࡑࡊ࡟ࡍࡋࡑࡏࠧᬢ")),
            bstack1ll_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᬣ"): None,
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᬤ"): env.get(bstack1ll_opy_ (u"ࠧࡊࡒࡐࡐࡈࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᬥ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠨࡃࡊࠤᬦ")) == bstack1ll_opy_ (u"ࠢࡵࡴࡸࡩࠧᬧ") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠣࡕࡈࡑࡆࡖࡈࡐࡔࡈࠦᬨ"))):
        return {
            bstack1ll_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᬩ"): bstack1ll_opy_ (u"ࠥࡗࡪࡳࡡࡱࡪࡲࡶࡪࠨᬪ"),
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᬫ"): env.get(bstack1ll_opy_ (u"࡙ࠧࡅࡎࡃࡓࡌࡔࡘࡅࡠࡑࡕࡋࡆࡔࡉ࡛ࡃࡗࡍࡔࡔ࡟ࡖࡔࡏࠦᬬ")),
            bstack1ll_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᬭ"): env.get(bstack1ll_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᬮ")),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᬯ"): env.get(bstack1ll_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡐࡏࡃࡡࡌࡈࠧᬰ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠥࡇࡎࠨᬱ")) == bstack1ll_opy_ (u"ࠦࡹࡸࡵࡦࠤᬲ") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠧࡍࡉࡕࡎࡄࡆࡤࡉࡉࠣᬳ"))):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨ᬴ࠦ"): bstack1ll_opy_ (u"ࠢࡈ࡫ࡷࡐࡦࡨࠢᬵ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᬶ"): env.get(bstack1ll_opy_ (u"ࠤࡆࡍࡤࡐࡏࡃࡡࡘࡖࡑࠨᬷ")),
            bstack1ll_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᬸ"): env.get(bstack1ll_opy_ (u"ࠦࡈࡏ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤᬹ")),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᬺ"): env.get(bstack1ll_opy_ (u"ࠨࡃࡊࡡࡍࡓࡇࡥࡉࡅࠤᬻ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠢࡄࡋࠥᬼ")) == bstack1ll_opy_ (u"ࠣࡶࡵࡹࡪࠨᬽ") and bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࠧᬾ"))):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣᬿ"): bstack1ll_opy_ (u"ࠦࡇࡻࡩ࡭ࡦ࡮࡭ࡹ࡫ࠢᭀ"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᭁ"): env.get(bstack1ll_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᭂ")),
            bstack1ll_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᭃ"): env.get(bstack1ll_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡑࡇࡂࡆࡎ᭄ࠥ")) or env.get(bstack1ll_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡖࡉࡑࡇࡏࡍࡓࡋ࡟ࡏࡃࡐࡉࠧᭅ")),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᭆ"): env.get(bstack1ll_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᭇ"))
        }
    if bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"࡚ࠧࡆࡠࡄࡘࡍࡑࡊࠢᭈ"))):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᭉ"): bstack1ll_opy_ (u"ࠢࡗ࡫ࡶࡹࡦࡲࠠࡔࡶࡸࡨ࡮ࡵࠠࡕࡧࡤࡱ࡙ࠥࡥࡳࡸ࡬ࡧࡪࡹࠢᭊ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᭋ"): bstack1ll_opy_ (u"ࠤࡾࢁࢀࢃࠢᭌ").format(env.get(bstack1ll_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡇࡑࡘࡒࡉࡇࡔࡊࡑࡑࡗࡊࡘࡖࡆࡔࡘࡖࡎ࠭᭍")), env.get(bstack1ll_opy_ (u"ࠫࡘ࡟ࡓࡕࡇࡐࡣ࡙ࡋࡁࡎࡒࡕࡓࡏࡋࡃࡕࡋࡇࠫ᭎"))),
            bstack1ll_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢ᭏"): env.get(bstack1ll_opy_ (u"ࠨࡓ࡚ࡕࡗࡉࡒࡥࡄࡆࡈࡌࡒࡎ࡚ࡉࡐࡐࡌࡈࠧ᭐")),
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨ᭑"): env.get(bstack1ll_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠣ᭒"))
        }
    if bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠤࡄࡔࡕ࡜ࡅ࡚ࡑࡕࠦ᭓"))):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣ᭔"): bstack1ll_opy_ (u"ࠦࡆࡶࡰࡷࡧࡼࡳࡷࠨ᭕"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᭖"): bstack1ll_opy_ (u"ࠨࡻࡾ࠱ࡳࡶࡴࡰࡥࡤࡶ࠲ࡿࢂ࠵ࡻࡾ࠱ࡥࡹ࡮ࡲࡤࡴ࠱ࡾࢁࠧ᭗").format(env.get(bstack1ll_opy_ (u"ࠧࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡘࡖࡑ࠭᭘")), env.get(bstack1ll_opy_ (u"ࠨࡃࡓࡔ࡛ࡋ࡙ࡐࡔࡢࡅࡈࡉࡏࡖࡐࡗࡣࡓࡇࡍࡆࠩ᭙")), env.get(bstack1ll_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡕࡘࡏࡋࡇࡆࡘࡤ࡙ࡌࡖࡉࠪ᭚")), env.get(bstack1ll_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧ᭛"))),
            bstack1ll_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᭜"): env.get(bstack1ll_opy_ (u"ࠧࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡋࡑࡅࡣࡓࡇࡍࡆࠤ᭝")),
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᭞"): env.get(bstack1ll_opy_ (u"ࠢࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᭟"))
        }
    if env.get(bstack1ll_opy_ (u"ࠣࡃ࡝࡙ࡗࡋ࡟ࡉࡖࡗࡔࡤ࡛ࡓࡆࡔࡢࡅࡌࡋࡎࡕࠤ᭠")) and env.get(bstack1ll_opy_ (u"ࠤࡗࡊࡤࡈࡕࡊࡎࡇࠦ᭡")):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣ᭢"): bstack1ll_opy_ (u"ࠦࡆࢀࡵࡳࡧࠣࡇࡎࠨ᭣"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᭤"): bstack1ll_opy_ (u"ࠨࡻࡾࡽࢀ࠳ࡤࡨࡵࡪ࡮ࡧ࠳ࡷ࡫ࡳࡶ࡮ࡷࡷࡄࡨࡵࡪ࡮ࡧࡍࡩࡃࡻࡾࠤ᭥").format(env.get(bstack1ll_opy_ (u"ࠧࡔ࡛ࡖࡘࡊࡓ࡟ࡕࡇࡄࡑࡋࡕࡕࡏࡆࡄࡘࡎࡕࡎࡔࡇࡕ࡚ࡊࡘࡕࡓࡋࠪ᭦")), env.get(bstack1ll_opy_ (u"ࠨࡕ࡜ࡗ࡙ࡋࡍࡠࡖࡈࡅࡒࡖࡒࡐࡌࡈࡇ࡙࠭᭧")), env.get(bstack1ll_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊࡉࡅࠩ᭨"))),
            bstack1ll_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᭩"): env.get(bstack1ll_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠦ᭪")),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᭫"): env.get(bstack1ll_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉࠨ᭬"))
        }
    if any([env.get(bstack1ll_opy_ (u"ࠢࡄࡑࡇࡉࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧ᭭")), env.get(bstack1ll_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡗࡋࡓࡐࡎ࡙ࡉࡉࡥࡓࡐࡗࡕࡇࡊࡥࡖࡆࡔࡖࡍࡔࡔࠢ᭮")), env.get(bstack1ll_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤ࡙ࡏࡖࡔࡆࡉࡤ࡜ࡅࡓࡕࡌࡓࡓࠨ᭯"))]):
        return {
            bstack1ll_opy_ (u"ࠥࡲࡦࡳࡥࠣ᭰"): bstack1ll_opy_ (u"ࠦࡆ࡝ࡓࠡࡅࡲࡨࡪࡈࡵࡪ࡮ࡧࠦ᭱"),
            bstack1ll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣ᭲"): env.get(bstack1ll_opy_ (u"ࠨࡃࡐࡆࡈࡆ࡚ࡏࡌࡅࡡࡓ࡙ࡇࡒࡉࡄࡡࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧ᭳")),
            bstack1ll_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᭴"): env.get(bstack1ll_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᭵")),
            bstack1ll_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣ᭶"): env.get(bstack1ll_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣ᭷"))
        }
    if env.get(bstack1ll_opy_ (u"ࠦࡧࡧ࡭ࡣࡱࡲࡣࡧࡻࡩ࡭ࡦࡑࡹࡲࡨࡥࡳࠤ᭸")):
        return {
            bstack1ll_opy_ (u"ࠧࡴࡡ࡮ࡧࠥ᭹"): bstack1ll_opy_ (u"ࠨࡂࡢ࡯ࡥࡳࡴࠨ᭺"),
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥ᭻"): env.get(bstack1ll_opy_ (u"ࠣࡤࡤࡱࡧࡵ࡯ࡠࡤࡸ࡭ࡱࡪࡒࡦࡵࡸࡰࡹࡹࡕࡳ࡮ࠥ᭼")),
            bstack1ll_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᭽"): env.get(bstack1ll_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡷ࡭ࡵࡲࡵࡌࡲࡦࡓࡧ࡭ࡦࠤ᭾")),
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥ᭿"): env.get(bstack1ll_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡨࡵࡪ࡮ࡧࡒࡺࡳࡢࡦࡴࠥᮀ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘࠢᮁ")) or env.get(bstack1ll_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡏࡄࡍࡓࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡕࡗࡅࡗ࡚ࡅࡅࠤᮂ")):
        return {
            bstack1ll_opy_ (u"ࠣࡰࡤࡱࡪࠨᮃ"): bstack1ll_opy_ (u"ࠤ࡚ࡩࡷࡩ࡫ࡦࡴࠥᮄ"),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᮅ"): env.get(bstack1ll_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡈࡕࡊࡎࡇࡣ࡚ࡘࡌࠣᮆ")),
            bstack1ll_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᮇ"): bstack1ll_opy_ (u"ࠨࡍࡢ࡫ࡱࠤࡕ࡯ࡰࡦ࡮࡬ࡲࡪࠨᮈ") if env.get(bstack1ll_opy_ (u"ࠢࡘࡇࡕࡇࡐࡋࡒࡠࡏࡄࡍࡓࡥࡐࡊࡒࡈࡐࡎࡔࡅࡠࡕࡗࡅࡗ࡚ࡅࡅࠤᮉ")) else None,
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᮊ"): env.get(bstack1ll_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࡢࡋࡎ࡚࡟ࡄࡑࡐࡑࡎ࡚ࠢᮋ"))
        }
    if any([env.get(bstack1ll_opy_ (u"ࠥࡋࡈࡖ࡟ࡑࡔࡒࡎࡊࡉࡔࠣᮌ")), env.get(bstack1ll_opy_ (u"ࠦࡌࡉࡌࡐࡗࡇࡣࡕࡘࡏࡋࡇࡆࡘࠧᮍ")), env.get(bstack1ll_opy_ (u"ࠧࡍࡏࡐࡉࡏࡉࡤࡉࡌࡐࡗࡇࡣࡕࡘࡏࡋࡇࡆࡘࠧᮎ"))]):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᮏ"): bstack1ll_opy_ (u"ࠢࡈࡱࡲ࡫ࡱ࡫ࠠࡄ࡮ࡲࡹࡩࠨᮐ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᮑ"): None,
            bstack1ll_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᮒ"): env.get(bstack1ll_opy_ (u"ࠥࡔࡗࡕࡊࡆࡅࡗࡣࡎࡊࠢᮓ")),
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᮔ"): env.get(bstack1ll_opy_ (u"ࠧࡈࡕࡊࡎࡇࡣࡎࡊࠢᮕ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠨࡓࡉࡋࡓࡔࡆࡈࡌࡆࠤᮖ")):
        return {
            bstack1ll_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᮗ"): bstack1ll_opy_ (u"ࠣࡕ࡫࡭ࡵࡶࡡࡣ࡮ࡨࠦᮘ"),
            bstack1ll_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᮙ"): env.get(bstack1ll_opy_ (u"ࠥࡗࡍࡏࡐࡑࡃࡅࡐࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᮚ")),
            bstack1ll_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᮛ"): bstack1ll_opy_ (u"ࠧࡐ࡯ࡣࠢࠦࡿࢂࠨᮜ").format(env.get(bstack1ll_opy_ (u"࠭ࡓࡉࡋࡓࡔࡆࡈࡌࡆࡡࡍࡓࡇࡥࡉࡅࠩᮝ"))) if env.get(bstack1ll_opy_ (u"ࠢࡔࡊࡌࡔࡕࡇࡂࡍࡇࡢࡎࡔࡈ࡟ࡊࡆࠥᮞ")) else None,
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᮟ"): env.get(bstack1ll_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠦᮠ"))
        }
    if bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠥࡒࡊ࡚ࡌࡊࡈ࡜ࠦᮡ"))):
        return {
            bstack1ll_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᮢ"): bstack1ll_opy_ (u"ࠧࡔࡥࡵ࡮࡬ࡪࡾࠨᮣ"),
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᮤ"): env.get(bstack1ll_opy_ (u"ࠢࡅࡇࡓࡐࡔ࡟࡟ࡖࡔࡏࠦᮥ")),
            bstack1ll_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᮦ"): env.get(bstack1ll_opy_ (u"ࠤࡖࡍ࡙ࡋ࡟ࡏࡃࡐࡉࠧᮧ")),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᮨ"): env.get(bstack1ll_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᮩ"))
        }
    if bstack11ll1lllll_opy_(env.get(bstack1ll_opy_ (u"ࠧࡍࡉࡕࡊࡘࡆࡤࡇࡃࡕࡋࡒࡒࡘࠨ᮪"))):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨ᮫ࠦ"): bstack1ll_opy_ (u"ࠢࡈ࡫ࡷࡌࡺࡨࠠࡂࡥࡷ࡭ࡴࡴࡳࠣᮬ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᮭ"): bstack1ll_opy_ (u"ࠤࡾࢁ࠴ࢁࡽ࠰ࡣࡦࡸ࡮ࡵ࡮ࡴ࠱ࡵࡹࡳࡹ࠯ࡼࡿࠥᮮ").format(env.get(bstack1ll_opy_ (u"ࠪࡋࡎ࡚ࡈࡖࡄࡢࡗࡊࡘࡖࡆࡔࡢ࡙ࡗࡒࠧᮯ")), env.get(bstack1ll_opy_ (u"ࠫࡌࡏࡔࡉࡗࡅࡣࡗࡋࡐࡐࡕࡌࡘࡔࡘ࡙ࠨ᮰")), env.get(bstack1ll_opy_ (u"ࠬࡍࡉࡕࡊࡘࡆࡤࡘࡕࡏࡡࡌࡈࠬ᮱"))),
            bstack1ll_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᮲"): env.get(bstack1ll_opy_ (u"ࠢࡈࡋࡗࡌ࡚ࡈ࡟ࡘࡑࡕࡏࡋࡒࡏࡘࠤ᮳")),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢ᮴"): env.get(bstack1ll_opy_ (u"ࠤࡊࡍ࡙ࡎࡕࡃࡡࡕ࡙ࡓࡥࡉࡅࠤ᮵"))
        }
    if env.get(bstack1ll_opy_ (u"ࠥࡇࡎࠨ᮶")) == bstack1ll_opy_ (u"ࠦࡹࡸࡵࡦࠤ᮷") and env.get(bstack1ll_opy_ (u"ࠧ࡜ࡅࡓࡅࡈࡐࠧ᮸")) == bstack1ll_opy_ (u"ࠨ࠱ࠣ᮹"):
        return {
            bstack1ll_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᮺ"): bstack1ll_opy_ (u"ࠣࡘࡨࡶࡨ࡫࡬ࠣᮻ"),
            bstack1ll_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᮼ"): bstack1ll_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࡿࢂࠨᮽ").format(env.get(bstack1ll_opy_ (u"࡛ࠫࡋࡒࡄࡇࡏࡣ࡚ࡘࡌࠨᮾ"))),
            bstack1ll_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᮿ"): None,
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᯀ"): None,
        }
    if env.get(bstack1ll_opy_ (u"ࠢࡕࡇࡄࡑࡈࡏࡔ࡚ࡡ࡙ࡉࡗ࡙ࡉࡐࡐࠥᯁ")):
        return {
            bstack1ll_opy_ (u"ࠣࡰࡤࡱࡪࠨᯂ"): bstack1ll_opy_ (u"ࠤࡗࡩࡦࡳࡣࡪࡶࡼࠦᯃ"),
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯄ"): None,
            bstack1ll_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᯅ"): env.get(bstack1ll_opy_ (u"࡚ࠧࡅࡂࡏࡆࡍ࡙࡟࡟ࡑࡔࡒࡎࡊࡉࡔࡠࡐࡄࡑࡊࠨᯆ")),
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᯇ"): env.get(bstack1ll_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᯈ"))
        }
    if any([env.get(bstack1ll_opy_ (u"ࠣࡅࡒࡒࡈࡕࡕࡓࡕࡈࠦᯉ")), env.get(bstack1ll_opy_ (u"ࠤࡆࡓࡓࡉࡏࡖࡔࡖࡉࡤ࡛ࡒࡍࠤᯊ")), env.get(bstack1ll_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࡥࡕࡔࡇࡕࡒࡆࡓࡅࠣᯋ")), env.get(bstack1ll_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋ࡟ࡕࡇࡄࡑࠧᯌ"))]):
        return {
            bstack1ll_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯍ"): bstack1ll_opy_ (u"ࠨࡃࡰࡰࡦࡳࡺࡸࡳࡦࠤᯎ"),
            bstack1ll_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯏ"): None,
            bstack1ll_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᯐ"): env.get(bstack1ll_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᯑ")) or None,
            bstack1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᯒ"): env.get(bstack1ll_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡍࡉࠨᯓ"), 0)
        }
    if env.get(bstack1ll_opy_ (u"ࠧࡍࡏࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᯔ")):
        return {
            bstack1ll_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᯕ"): bstack1ll_opy_ (u"ࠢࡈࡱࡆࡈࠧᯖ"),
            bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᯗ"): None,
            bstack1ll_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᯘ"): env.get(bstack1ll_opy_ (u"ࠥࡋࡔࡥࡊࡐࡄࡢࡒࡆࡓࡅࠣᯙ")),
            bstack1ll_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᯚ"): env.get(bstack1ll_opy_ (u"ࠧࡍࡏࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡇࡔ࡛ࡎࡕࡇࡕࠦᯛ"))
        }
    if env.get(bstack1ll_opy_ (u"ࠨࡃࡇࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠦᯜ")):
        return {
            bstack1ll_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᯝ"): bstack1ll_opy_ (u"ࠣࡅࡲࡨࡪࡌࡲࡦࡵ࡫ࠦᯞ"),
            bstack1ll_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᯟ"): env.get(bstack1ll_opy_ (u"ࠥࡇࡋࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤᯠ")),
            bstack1ll_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᯡ"): env.get(bstack1ll_opy_ (u"ࠧࡉࡆࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡒࡆࡓࡅࠣᯢ")),
            bstack1ll_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᯣ"): env.get(bstack1ll_opy_ (u"ࠢࡄࡈࡢࡆ࡚ࡏࡌࡅࡡࡌࡈࠧᯤ"))
        }
    return {bstack1ll_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᯥ"): None}
def get_host_info():
    return {
        bstack1ll_opy_ (u"ࠤ࡫ࡳࡸࡺ࡮ࡢ࡯ࡨ᯦ࠦ"): platform.node(),
        bstack1ll_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࠧᯧ"): platform.system(),
        bstack1ll_opy_ (u"ࠦࡹࡿࡰࡦࠤᯨ"): platform.machine(),
        bstack1ll_opy_ (u"ࠧࡼࡥࡳࡵ࡬ࡳࡳࠨᯩ"): platform.version(),
        bstack1ll_opy_ (u"ࠨࡡࡳࡥ࡫ࠦᯪ"): platform.architecture()[0]
    }
def bstack1l1111l111_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111ll1l1l11_opy_():
    if bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨᯫ")):
        return bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᯬ")
    return bstack1ll_opy_ (u"ࠩࡸࡲࡰࡴ࡯ࡸࡰࡢ࡫ࡷ࡯ࡤࠨᯭ")
def bstack111llllll11_opy_(driver):
    info = {
        bstack1ll_opy_ (u"ࠪࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠩᯮ"): driver.capabilities,
        bstack1ll_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠨᯯ"): driver.session_id,
        bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ᯰ"): driver.capabilities.get(bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᯱ"), None),
        bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯᯲ࠩ"): driver.capabilities.get(bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯᯳ࠩ"), None),
        bstack1ll_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࠫ᯴"): driver.capabilities.get(bstack1ll_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠩ᯵"), None),
        bstack1ll_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ᯶"):driver.capabilities.get(bstack1ll_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ᯷"), None),
    }
    if bstack111ll1l1l11_opy_() == bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ᯸"):
        if bstack11l1ll1ll1_opy_():
            info[bstack1ll_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨ᯹")] = bstack1ll_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ᯺")
        elif driver.capabilities.get(bstack1ll_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ᯻"), {}).get(bstack1ll_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧ᯼"), False):
            info[bstack1ll_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࠬ᯽")] = bstack1ll_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ᯾")
        else:
            info[bstack1ll_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺࠧ᯿")] = bstack1ll_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩᰀ")
    return info
def bstack11l1ll1ll1_opy_():
    if bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᰁ")):
        return True
    if bstack11ll1lllll_opy_(os.environ.get(bstack1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡋࡖࡣࡆࡖࡐࡠࡃࡘࡘࡔࡓࡁࡕࡇࠪᰂ"), None)):
        return True
    return False
def bstack11ll1l1ll1_opy_(bstack111ll1l1ll1_opy_, url, data, config):
    headers = config.get(bstack1ll_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫᰃ"), None)
    proxies = bstack1ll1l111l1_opy_(config, url)
    auth = config.get(bstack1ll_opy_ (u"ࠫࡦࡻࡴࡩࠩᰄ"), None)
    response = requests.request(
            bstack111ll1l1ll1_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack1l1lll11ll_opy_(bstack11ll1lll1_opy_, size):
    bstack11l111llll_opy_ = []
    while len(bstack11ll1lll1_opy_) > size:
        bstack11llll1ll1_opy_ = bstack11ll1lll1_opy_[:size]
        bstack11l111llll_opy_.append(bstack11llll1ll1_opy_)
        bstack11ll1lll1_opy_ = bstack11ll1lll1_opy_[size:]
    bstack11l111llll_opy_.append(bstack11ll1lll1_opy_)
    return bstack11l111llll_opy_
def bstack11l11l1l111_opy_(message, bstack11l1111l1l1_opy_=False):
    os.write(1, bytes(message, bstack1ll_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᰅ")))
    os.write(1, bytes(bstack1ll_opy_ (u"࠭࡜࡯ࠩᰆ"), bstack1ll_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭ᰇ")))
    if bstack11l1111l1l1_opy_:
        with open(bstack1ll_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠮ࡱ࠴࠵ࡾ࠳ࠧᰈ") + os.environ[bstack1ll_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡂࡖࡋࡏࡈࡤࡎࡁࡔࡊࡈࡈࡤࡏࡄࠨᰉ")] + bstack1ll_opy_ (u"ࠪ࠲ࡱࡵࡧࠨᰊ"), bstack1ll_opy_ (u"ࠫࡦ࠭ᰋ")) as f:
            f.write(message + bstack1ll_opy_ (u"ࠬࡢ࡮ࠨᰌ"))
def bstack1l1llllllll_opy_():
    return os.environ[bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡕࡕࡑࡐࡅ࡙ࡏࡏࡏࠩᰍ")].lower() == bstack1ll_opy_ (u"ࠧࡵࡴࡸࡩࠬᰎ")
def bstack11llll1111_opy_(bstack11lll1lll1l_opy_):
    return bstack1ll_opy_ (u"ࠨࡽࢀ࠳ࢀࢃࠧᰏ").format(bstack11l11lll111_opy_, bstack11lll1lll1l_opy_)
def bstack11ll111lll_opy_():
    return bstack111ll11lll_opy_().replace(tzinfo=None).isoformat() + bstack1ll_opy_ (u"ࠩ࡝ࠫᰐ")
def bstack111ll1l1l1l_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1ll_opy_ (u"ࠪ࡞ࠬᰑ"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1ll_opy_ (u"ࠫ࡟࠭ᰒ")))).total_seconds() * 1000
def bstack111lll1l11l_opy_(timestamp):
    return bstack111ll11llll_opy_(timestamp).isoformat() + bstack1ll_opy_ (u"ࠬࡠࠧᰓ")
def bstack111lll11l1l_opy_(bstack11l111111l1_opy_):
    date_format = bstack1ll_opy_ (u"࡚࠭ࠥࠧࡰࠩࡩࠦࠥࡉ࠼ࠨࡑ࠿ࠫࡓ࠯ࠧࡩࠫᰔ")
    bstack111lllllll1_opy_ = datetime.datetime.strptime(bstack11l111111l1_opy_, date_format)
    return bstack111lllllll1_opy_.isoformat() + bstack1ll_opy_ (u"࡛ࠧࠩᰕ")
def bstack111ll1ll1ll_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1ll_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨᰖ")
    else:
        return bstack1ll_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩᰗ")
def bstack11ll1lllll_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1ll_opy_ (u"ࠪࡸࡷࡻࡥࠨᰘ")
def bstack11l11l11l1l_opy_(val):
    return val.__str__().lower() == bstack1ll_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪᰙ")
def bstack111l11ll11_opy_(bstack111lll1l1ll_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack111lll1l1ll_opy_ as e:
                print(bstack1ll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦࡻࡾࠢ࠰ࡂࠥࢁࡽ࠻ࠢࡾࢁࠧᰚ").format(func.__name__, bstack111lll1l1ll_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack11l111l1111_opy_(bstack11l111ll1ll_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack11l111ll1ll_opy_(cls, *args, **kwargs)
            except bstack111lll1l1ll_opy_ as e:
                print(bstack1ll_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨᰛ").format(bstack11l111ll1ll_opy_.__name__, bstack111lll1l1ll_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack11l111l1111_opy_
    else:
        return decorator
def bstack11ll11l1l1_opy_(bstack1111lll1ll_opy_):
    if os.getenv(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡖࡖࡒࡑࡆ࡚ࡉࡐࡐࠪᰜ")) is not None:
        return bstack11ll1lllll_opy_(os.getenv(bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫᰝ")))
    if bstack1ll_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᰞ") in bstack1111lll1ll_opy_ and bstack11l11l11l1l_opy_(bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᰟ")]):
        return False
    if bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࠭ᰠ") in bstack1111lll1ll_opy_ and bstack11l11l11l1l_opy_(bstack1111lll1ll_opy_[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧᰡ")]):
        return False
    return True
def bstack1l11l1ll_opy_():
    try:
        from pytest_bdd import reporting
        bstack11l11l11111_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࠨᰢ"), None)
        return bstack11l11l11111_opy_ is None or bstack11l11l11111_opy_ == bstack1ll_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠦᰣ")
    except Exception as e:
        return False
def bstack11l11ll11_opy_(hub_url, CONFIG):
    if bstack11l111ll1_opy_() <= version.parse(bstack1ll_opy_ (u"ࠨ࠵࠱࠵࠸࠴࠰ࠨᰤ")):
        if hub_url:
            return bstack1ll_opy_ (u"ࠤ࡫ࡸࡹࡶ࠺࠰࠱ࠥᰥ") + hub_url + bstack1ll_opy_ (u"ࠥ࠾࠽࠶࠯ࡸࡦ࠲࡬ࡺࡨࠢᰦ")
        return bstack111l1l111_opy_
    if hub_url:
        return bstack1ll_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨᰧ") + hub_url + bstack1ll_opy_ (u"ࠧ࠵ࡷࡥ࠱࡫ࡹࡧࠨᰨ")
    return bstack1l111l11_opy_
def bstack111ll11ll1l_opy_():
    return isinstance(os.getenv(bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖ࡙ࡕࡇࡖࡘࡤࡖࡌࡖࡉࡌࡒࠬᰩ")), str)
def bstack11l1lllll_opy_(url):
    return urlparse(url).hostname
def bstack11ll11ll11_opy_(hostname):
    for bstack1ll11l1l1l_opy_ in bstack1ll11l1l_opy_:
        regex = re.compile(bstack1ll11l1l1l_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack111lll1l111_opy_(bstack11l1111l11l_opy_, file_name, logger):
    bstack1llll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠧࡿࠩᰪ")), bstack11l1111l11l_opy_)
    try:
        if not os.path.exists(bstack1llll1ll1_opy_):
            os.makedirs(bstack1llll1ll1_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠨࢀࠪᰫ")), bstack11l1111l11l_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1ll_opy_ (u"ࠩࡺࠫᰬ")):
                pass
            with open(file_path, bstack1ll_opy_ (u"ࠥࡻ࠰ࠨᰭ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack11llll11ll_opy_.format(str(e)))
def bstack11l11l11ll1_opy_(file_name, key, value, logger):
    file_path = bstack111lll1l111_opy_(bstack1ll_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᰮ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack111lllll1_opy_ = json.load(open(file_path, bstack1ll_opy_ (u"ࠬࡸࡢࠨᰯ")))
        else:
            bstack111lllll1_opy_ = {}
        bstack111lllll1_opy_[key] = value
        with open(file_path, bstack1ll_opy_ (u"ࠨࡷࠬࠤᰰ")) as outfile:
            json.dump(bstack111lllll1_opy_, outfile)
def bstack1ll1l1ll1_opy_(file_name, logger):
    file_path = bstack111lll1l111_opy_(bstack1ll_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᰱ"), file_name, logger)
    bstack111lllll1_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1ll_opy_ (u"ࠨࡴࠪᰲ")) as bstack11l11l1111_opy_:
            bstack111lllll1_opy_ = json.load(bstack11l11l1111_opy_)
    return bstack111lllll1_opy_
def bstack1l111lllll_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡩ࡫࡬ࡦࡶ࡬ࡲ࡬ࠦࡦࡪ࡮ࡨ࠾ࠥ࠭ᰳ") + file_path + bstack1ll_opy_ (u"ࠪࠤࠬᰴ") + str(e))
def bstack11l111ll1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1ll_opy_ (u"ࠦࡁࡔࡏࡕࡕࡈࡘࡃࠨᰵ")
def bstack11111l1l_opy_(config):
    if bstack1ll_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫᰶ") in config:
        del (config[bstack1ll_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ᰷ࠬ")])
        return False
    if bstack11l111ll1_opy_() < version.parse(bstack1ll_opy_ (u"ࠧ࠴࠰࠷࠲࠵࠭᰸")):
        return False
    if bstack11l111ll1_opy_() >= version.parse(bstack1ll_opy_ (u"ࠨ࠶࠱࠵࠳࠻ࠧ᰹")):
        return True
    if bstack1ll_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩ᰺") in config and config[bstack1ll_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪ᰻")] is False:
        return False
    else:
        return True
def bstack1l1ll1ll1l_opy_(args_list, bstack111lll1ll11_opy_):
    index = -1
    for value in bstack111lll1ll11_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11l1lllll1l_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11l1lllll1l_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111lllll1l_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111lllll1l_opy_ = bstack111lllll1l_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1ll_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫ᰼"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ᰽"), exception=exception)
    def bstack1111l11ll1_opy_(self):
        if self.result != bstack1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭᰾"):
            return None
        if isinstance(self.exception_type, str) and bstack1ll_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥ᰿") in self.exception_type:
            return bstack1ll_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࡉࡷࡸ࡯ࡳࠤ᱀")
        return bstack1ll_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥ᱁")
    def bstack11l1111111l_opy_(self):
        if self.result != bstack1ll_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ᱂"):
            return None
        if self.bstack111lllll1l_opy_:
            return self.bstack111lllll1l_opy_
        return bstack11l111l1l1l_opy_(self.exception)
def bstack11l111l1l1l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack11l11111ll1_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack11ll11l1_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack11ll11l111_opy_(config, logger):
    try:
        import playwright
        bstack11l111l1ll1_opy_ = playwright.__file__
        bstack111llll111l_opy_ = os.path.split(bstack11l111l1ll1_opy_)
        bstack111ll1lllll_opy_ = bstack111llll111l_opy_[0] + bstack1ll_opy_ (u"ࠫ࠴ࡪࡲࡪࡸࡨࡶ࠴ࡶࡡࡤ࡭ࡤ࡫ࡪ࠵࡬ࡪࡤ࠲ࡧࡱ࡯࠯ࡤ࡮࡬࠲࡯ࡹࠧ᱃")
        os.environ[bstack1ll_opy_ (u"ࠬࡍࡌࡐࡄࡄࡐࡤࡇࡇࡆࡐࡗࡣࡍ࡚ࡔࡑࡡࡓࡖࡔ࡞࡙ࠨ᱄")] = bstack1l1111l11_opy_(config)
        with open(bstack111ll1lllll_opy_, bstack1ll_opy_ (u"࠭ࡲࠨ᱅")) as f:
            bstack111l1l1ll_opy_ = f.read()
            bstack111lll11111_opy_ = bstack1ll_opy_ (u"ࠧࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹ࠭᱆")
            bstack111lll1ll1l_opy_ = bstack111l1l1ll_opy_.find(bstack111lll11111_opy_)
            if bstack111lll1ll1l_opy_ == -1:
              process = subprocess.Popen(bstack1ll_opy_ (u"ࠣࡰࡳࡱࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡧ࡭ࡱࡥࡥࡱ࠳ࡡࡨࡧࡱࡸࠧ᱇"), shell=True, cwd=bstack111llll111l_opy_[0])
              process.wait()
              bstack111ll1lll11_opy_ = bstack1ll_opy_ (u"ࠩࠥࡹࡸ࡫ࠠࡴࡶࡵ࡭ࡨࡺࠢ࠼ࠩ᱈")
              bstack111llll11ll_opy_ = bstack1ll_opy_ (u"ࠥࠦࠧࠦ࡜ࠣࡷࡶࡩࠥࡹࡴࡳ࡫ࡦࡸࡡࠨ࠻ࠡࡥࡲࡲࡸࡺࠠࡼࠢࡥࡳࡴࡺࡳࡵࡴࡤࡴࠥࢃࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠫ࡬ࡲ࡯ࡣࡣ࡯࠱ࡦ࡭ࡥ࡯ࡶࠪ࠭ࡀࠦࡩࡧࠢࠫࡴࡷࡵࡣࡦࡵࡶ࠲ࡪࡴࡶ࠯ࡉࡏࡓࡇࡇࡌࡠࡃࡊࡉࡓ࡚࡟ࡉࡖࡗࡔࡤࡖࡒࡐ࡚࡜࠭ࠥࡨ࡯ࡰࡶࡶࡸࡷࡧࡰࠩࠫ࠾ࠤࠧࠨࠢ᱉")
              bstack111llllllll_opy_ = bstack111l1l1ll_opy_.replace(bstack111ll1lll11_opy_, bstack111llll11ll_opy_)
              with open(bstack111ll1lllll_opy_, bstack1ll_opy_ (u"ࠫࡼ࠭᱊")) as f:
                f.write(bstack111llllllll_opy_)
    except Exception as e:
        logger.error(bstack11lll11111_opy_.format(str(e)))
def bstack1l1ll11l11_opy_():
  try:
    bstack111ll1ll111_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠬࡵࡰࡵ࡫ࡰࡥࡱࡥࡨࡶࡤࡢࡹࡷࡲ࠮࡫ࡵࡲࡲࠬ᱋"))
    bstack111llll11l1_opy_ = []
    if os.path.exists(bstack111ll1ll111_opy_):
      with open(bstack111ll1ll111_opy_) as f:
        bstack111llll11l1_opy_ = json.load(f)
      os.remove(bstack111ll1ll111_opy_)
    return bstack111llll11l1_opy_
  except:
    pass
  return []
def bstack1l1l11ll11_opy_(bstack1lllll1ll_opy_):
  try:
    bstack111llll11l1_opy_ = []
    bstack111ll1ll111_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ࠭᱌"))
    if os.path.exists(bstack111ll1ll111_opy_):
      with open(bstack111ll1ll111_opy_) as f:
        bstack111llll11l1_opy_ = json.load(f)
    bstack111llll11l1_opy_.append(bstack1lllll1ll_opy_)
    with open(bstack111ll1ll111_opy_, bstack1ll_opy_ (u"ࠧࡸࠩᱍ")) as f:
        json.dump(bstack111llll11l1_opy_, f)
  except:
    pass
def bstack11lll1l1l_opy_(logger, bstack111lll1lll1_opy_ = False):
  try:
    test_name = os.environ.get(bstack1ll_opy_ (u"ࠨࡒ࡜ࡘࡊ࡙ࡔࡠࡖࡈࡗ࡙ࡥࡎࡂࡏࡈࠫᱎ"), bstack1ll_opy_ (u"ࠩࠪᱏ"))
    if test_name == bstack1ll_opy_ (u"ࠪࠫ᱐"):
        test_name = threading.current_thread().__dict__.get(bstack1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡆࡩࡪ࡟ࡵࡧࡶࡸࡤࡴࡡ࡮ࡧࠪ᱑"), bstack1ll_opy_ (u"ࠬ࠭᱒"))
    bstack111ll1l111l_opy_ = bstack1ll_opy_ (u"࠭ࠬࠡࠩ᱓").join(threading.current_thread().bstackTestErrorMessages)
    if bstack111lll1lll1_opy_:
        bstack1l1ll1ll11_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧ᱔"), bstack1ll_opy_ (u"ࠨ࠲ࠪ᱕"))
        bstack1l1l1l1111_opy_ = {bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ᱖"): test_name, bstack1ll_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩ᱗"): bstack111ll1l111l_opy_, bstack1ll_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ᱘"): bstack1l1ll1ll11_opy_}
        bstack11l11l1l1l1_opy_ = []
        bstack111llll1l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡶࡰࡱࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫ᱙"))
        if os.path.exists(bstack111llll1l1l_opy_):
            with open(bstack111llll1l1l_opy_) as f:
                bstack11l11l1l1l1_opy_ = json.load(f)
        bstack11l11l1l1l1_opy_.append(bstack1l1l1l1111_opy_)
        with open(bstack111llll1l1l_opy_, bstack1ll_opy_ (u"࠭ࡷࠨᱚ")) as f:
            json.dump(bstack11l11l1l1l1_opy_, f)
    else:
        bstack1l1l1l1111_opy_ = {bstack1ll_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᱛ"): test_name, bstack1ll_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᱜ"): bstack111ll1l111l_opy_, bstack1ll_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᱝ"): str(multiprocessing.current_process().name)}
        if bstack1ll_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺࠧᱞ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l1l1l1111_opy_)
  except Exception as e:
      logger.warn(bstack1ll_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡰࡺࡶࡨࡷࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠣᱟ").format(e))
def bstack1l1l111ll1_opy_(error_message, test_name, index, logger):
  try:
    bstack11l1111l111_opy_ = []
    bstack1l1l1l1111_opy_ = {bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᱠ"): test_name, bstack1ll_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᱡ"): error_message, bstack1ll_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ᱢ"): index}
    bstack111lll111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠨࡴࡲࡦࡴࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩᱣ"))
    if os.path.exists(bstack111lll111l1_opy_):
        with open(bstack111lll111l1_opy_) as f:
            bstack11l1111l111_opy_ = json.load(f)
    bstack11l1111l111_opy_.append(bstack1l1l1l1111_opy_)
    with open(bstack111lll111l1_opy_, bstack1ll_opy_ (u"ࠩࡺࠫᱤ")) as f:
        json.dump(bstack11l1111l111_opy_, f)
  except Exception as e:
    logger.warn(bstack1ll_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥࡸ࡯ࡣࡱࡷࠤ࡫ࡻ࡮࡯ࡧ࡯ࠤࡩࡧࡴࡢ࠼ࠣࡿࢂࠨᱥ").format(e))
def bstack1l1l1l1l11_opy_(bstack1l1l11l1ll_opy_, name, logger):
  try:
    bstack1l1l1l1111_opy_ = {bstack1ll_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᱦ"): name, bstack1ll_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫᱧ"): bstack1l1l11l1ll_opy_, bstack1ll_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬᱨ"): str(threading.current_thread()._name)}
    return bstack1l1l1l1111_opy_
  except Exception as e:
    logger.warn(bstack1ll_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡵࡲࡦࠢࡥࡩ࡭ࡧࡶࡦࠢࡩࡹࡳࡴࡥ࡭ࠢࡧࡥࡹࡧ࠺ࠡࡽࢀࠦᱩ").format(e))
  return
def bstack111llll1lll_opy_():
    return platform.system() == bstack1ll_opy_ (u"ࠨ࡙࡬ࡲࡩࡵࡷࡴࠩᱪ")
def bstack11lllll1_opy_(bstack111lllll1l1_opy_, config, logger):
    bstack111lll1llll_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111lllll1l1_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡭ࡶࡨࡶࠥࡩ࡯࡯ࡨ࡬࡫ࠥࡱࡥࡺࡵࠣࡦࡾࠦࡲࡦࡩࡨࡼࠥࡳࡡࡵࡥ࡫࠾ࠥࢁࡽࠣᱫ").format(e))
    return bstack111lll1llll_opy_
def bstack111lll11lll_opy_(bstack111ll1l11l1_opy_, bstack111lllll11l_opy_):
    bstack11l1111lll1_opy_ = version.parse(bstack111ll1l11l1_opy_)
    bstack11l111l1l11_opy_ = version.parse(bstack111lllll11l_opy_)
    if bstack11l1111lll1_opy_ > bstack11l111l1l11_opy_:
        return 1
    elif bstack11l1111lll1_opy_ < bstack11l111l1l11_opy_:
        return -1
    else:
        return 0
def bstack111ll11lll_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack111ll11llll_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack11l11111111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1llll1l1ll_opy_(options, framework, config, bstack1ll1111l_opy_={}):
    if options is None:
        return
    if getattr(options, bstack1ll_opy_ (u"ࠪ࡫ࡪࡺࠧᱬ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1ll1l111l_opy_ = caps.get(bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᱭ"))
    bstack11l111l11ll_opy_ = True
    bstack1l1llllll1_opy_ = os.environ[bstack1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᱮ")]
    bstack1ll11l1llll_opy_ = config.get(bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᱯ"), False)
    if bstack1ll11l1llll_opy_:
        bstack1lllll1ll1l_opy_ = config.get(bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᱰ"), {})
        bstack1lllll1ll1l_opy_[bstack1ll_opy_ (u"ࠨࡣࡸࡸ࡭࡚࡯࡬ࡧࡱࠫᱱ")] = os.getenv(bstack1ll_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᱲ"))
        bstack11l1llll11l_opy_ = json.loads(os.getenv(bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫᱳ"), bstack1ll_opy_ (u"ࠫࢀࢃࠧᱴ"))).get(bstack1ll_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᱵ"))
    if bstack11l11l11l1l_opy_(caps.get(bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡻࡳࡦ࡙࠶ࡇࠬᱶ"))) or bstack11l11l11l1l_opy_(caps.get(bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡵࡴࡧࡢࡻ࠸ࡩࠧᱷ"))):
        bstack11l111l11ll_opy_ = False
    if bstack11111l1l_opy_({bstack1ll_opy_ (u"ࠣࡷࡶࡩ࡜࠹ࡃࠣᱸ"): bstack11l111l11ll_opy_}):
        bstack1ll1l111l_opy_ = bstack1ll1l111l_opy_ or {}
        bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᱹ")] = bstack11l11111111_opy_(framework)
        bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᱺ")] = bstack1l1llllllll_opy_()
        bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠫࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᱻ")] = bstack1l1llllll1_opy_
        bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᱼ")] = bstack1ll1111l_opy_
        if bstack1ll11l1llll_opy_:
            bstack1ll1l111l_opy_[bstack1ll_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᱽ")] = bstack1ll11l1llll_opy_
            bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ᱾")] = bstack1lllll1ll1l_opy_
            bstack1ll1l111l_opy_[bstack1ll_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᱿")][bstack1ll_opy_ (u"ࠩࡶࡧࡦࡴ࡮ࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪᲀ")] = bstack11l1llll11l_opy_
        if getattr(options, bstack1ll_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫᲁ"), None):
            options.set_capability(bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᲂ"), bstack1ll1l111l_opy_)
        else:
            options[bstack1ll_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭ᲃ")] = bstack1ll1l111l_opy_
    else:
        if getattr(options, bstack1ll_opy_ (u"࠭ࡳࡦࡶࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹࡿࠧᲄ"), None):
            options.set_capability(bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨᲅ"), bstack11l11111111_opy_(framework))
            options.set_capability(bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᲆ"), bstack1l1llllllll_opy_())
            options.set_capability(bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡶࡨࡷࡹ࡮ࡵࡣࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫᲇ"), bstack1l1llllll1_opy_)
            options.set_capability(bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫᲈ"), bstack1ll1111l_opy_)
            if bstack1ll11l1llll_opy_:
                options.set_capability(bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᲉ"), bstack1ll11l1llll_opy_)
                options.set_capability(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᲊ"), bstack1lllll1ll1l_opy_)
                options.set_capability(bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷ࠳ࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭᲋"), bstack11l1llll11l_opy_)
        else:
            options[bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨ᲌")] = bstack11l11111111_opy_(framework)
            options[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩ᲍")] = bstack1l1llllllll_opy_()
            options[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡶࡨࡷࡹ࡮ࡵࡣࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫ᲎")] = bstack1l1llllll1_opy_
            options[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫ᲏")] = bstack1ll1111l_opy_
            if bstack1ll11l1llll_opy_:
                options[bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᲐ")] = bstack1ll11l1llll_opy_
                options[bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᲑ")] = bstack1lllll1ll1l_opy_
                options[bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᲒ")][bstack1ll_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᲓ")] = bstack11l1llll11l_opy_
    return options
def bstack11l11l1l11l_opy_(bstack11l11l11lll_opy_, framework):
    bstack1ll1111l_opy_ = bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠣࡒࡏࡅ࡞࡝ࡒࡊࡉࡋࡘࡤࡖࡒࡐࡆࡘࡇ࡙ࡥࡍࡂࡒࠥᲔ"))
    if bstack11l11l11lll_opy_ and len(bstack11l11l11lll_opy_.split(bstack1ll_opy_ (u"ࠩࡦࡥࡵࡹ࠽ࠨᲕ"))) > 1:
        ws_url = bstack11l11l11lll_opy_.split(bstack1ll_opy_ (u"ࠪࡧࡦࡶࡳ࠾ࠩᲖ"))[0]
        if bstack1ll_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳࠧᲗ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111llll1ll1_opy_ = json.loads(urllib.parse.unquote(bstack11l11l11lll_opy_.split(bstack1ll_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᲘ"))[1]))
            bstack111llll1ll1_opy_ = bstack111llll1ll1_opy_ or {}
            bstack1l1llllll1_opy_ = os.environ[bstack1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᲙ")]
            bstack111llll1ll1_opy_[bstack1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡘࡊࡋࠨᲚ")] = str(framework) + str(__version__)
            bstack111llll1ll1_opy_[bstack1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᲛ")] = bstack1l1llllllll_opy_()
            bstack111llll1ll1_opy_[bstack1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡶࡨࡷࡹ࡮ࡵࡣࡄࡸ࡭ࡱࡪࡕࡶ࡫ࡧࠫᲜ")] = bstack1l1llllll1_opy_
            bstack111llll1ll1_opy_[bstack1ll_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡑࡴࡲࡨࡺࡩࡴࡎࡣࡳࠫᲝ")] = bstack1ll1111l_opy_
            bstack11l11l11lll_opy_ = bstack11l11l11lll_opy_.split(bstack1ll_opy_ (u"ࠫࡨࡧࡰࡴ࠿ࠪᲞ"))[0] + bstack1ll_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᲟ") + urllib.parse.quote(json.dumps(bstack111llll1ll1_opy_))
    return bstack11l11l11lll_opy_
def bstack11llll111l_opy_():
    global bstack1l111l11ll_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1l111l11ll_opy_ = BrowserType.connect
    return bstack1l111l11ll_opy_
def bstack11l11l11_opy_(framework_name):
    global bstack11ll1l1lll_opy_
    bstack11ll1l1lll_opy_ = framework_name
    return framework_name
def bstack1lll1l1lll_opy_(self, *args, **kwargs):
    global bstack1l111l11ll_opy_
    try:
        global bstack11ll1l1lll_opy_
        if bstack1ll_opy_ (u"࠭ࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶࠪᲠ") in kwargs:
            kwargs[bstack1ll_opy_ (u"ࠧࡸࡵࡈࡲࡩࡶ࡯ࡪࡰࡷࠫᲡ")] = bstack11l11l1l11l_opy_(
                kwargs.get(bstack1ll_opy_ (u"ࠨࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸࠬᲢ"), None),
                bstack11ll1l1lll_opy_
            )
    except Exception as e:
        logger.error(bstack1ll_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤᲣ").format(str(e)))
    return bstack1l111l11ll_opy_(self, *args, **kwargs)
def bstack11l111llll1_opy_(bstack111lll1l1l1_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack1ll1l111l1_opy_(bstack111lll1l1l1_opy_, bstack1ll_opy_ (u"ࠥࠦᲤ"))
        if proxies and proxies.get(bstack1ll_opy_ (u"ࠦ࡭ࡺࡴࡱࡵࠥᲥ")):
            parsed_url = urlparse(proxies.get(bstack1ll_opy_ (u"ࠧ࡮ࡴࡵࡲࡶࠦᲦ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1ll_opy_ (u"࠭ࡰࡳࡱࡻࡽࡍࡵࡳࡵࠩᲧ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1ll_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪᲨ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1ll_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫᲩ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1ll_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬᲪ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack1lll1ll111_opy_(bstack111lll1l1l1_opy_):
    bstack11l11111lll_opy_ = {
        bstack11l11llllll_opy_[bstack11l111l11l1_opy_]: bstack111lll1l1l1_opy_[bstack11l111l11l1_opy_]
        for bstack11l111l11l1_opy_ in bstack111lll1l1l1_opy_
        if bstack11l111l11l1_opy_ in bstack11l11llllll_opy_
    }
    bstack11l11111lll_opy_[bstack1ll_opy_ (u"ࠥࡴࡷࡵࡸࡺࡕࡨࡸࡹ࡯࡮ࡨࡵࠥᲫ")] = bstack11l111llll1_opy_(bstack111lll1l1l1_opy_, bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠦࡵࡸ࡯ࡹࡻࡖࡩࡹࡺࡩ࡯ࡩࡶࠦᲬ")))
    bstack11l11l11l11_opy_ = [element.lower() for element in bstack11l1l111l11_opy_]
    bstack11l1111ll1l_opy_(bstack11l11111lll_opy_, bstack11l11l11l11_opy_)
    return bstack11l11111lll_opy_
def bstack11l1111ll1l_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1ll_opy_ (u"ࠧ࠰ࠪࠫࠬࠥᲭ")
    for value in d.values():
        if isinstance(value, dict):
            bstack11l1111ll1l_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack11l1111ll1l_opy_(item, keys)
def bstack1ll111l1111_opy_():
    bstack11l111l111l_opy_ = [os.environ.get(bstack1ll_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡉࡍࡇࡖࡣࡉࡏࡒࠣᲮ")), os.path.join(os.path.expanduser(bstack1ll_opy_ (u"ࠢࡿࠤᲯ")), bstack1ll_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨᲰ")), os.path.join(bstack1ll_opy_ (u"ࠩ࠲ࡸࡲࡶࠧᲱ"), bstack1ll_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᲲ"))]
    for path in bstack11l111l111l_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack1ll_opy_ (u"ࠦࡋ࡯࡬ࡦࠢࠪࠦᲳ") + str(path) + bstack1ll_opy_ (u"ࠧ࠭ࠠࡦࡺ࡬ࡷࡹࡹ࠮ࠣᲴ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack1ll_opy_ (u"ࠨࡇࡪࡸ࡬ࡲ࡬ࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰࡶࠤ࡫ࡵࡲࠡࠩࠥᲵ") + str(path) + bstack1ll_opy_ (u"ࠢࠨࠤᲶ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack1ll_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࠧࠣᲷ") + str(path) + bstack1ll_opy_ (u"ࠤࠪࠤࡦࡲࡲࡦࡣࡧࡽࠥ࡮ࡡࡴࠢࡷ࡬ࡪࠦࡲࡦࡳࡸ࡭ࡷ࡫ࡤࠡࡲࡨࡶࡲ࡯ࡳࡴ࡫ࡲࡲࡸ࠴ࠢᲸ"))
            else:
                logger.debug(bstack1ll_opy_ (u"ࠥࡇࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥ࡬ࡩ࡭ࡧࠣࠫࠧᲹ") + str(path) + bstack1ll_opy_ (u"ࠦࠬࠦࡷࡪࡶ࡫ࠤࡼࡸࡩࡵࡧࠣࡴࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴ࠮ࠣᲺ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack1ll_opy_ (u"ࠧࡕࡰࡦࡴࡤࡸ࡮ࡵ࡮ࠡࡵࡸࡧࡨ࡫ࡥࡥࡧࡧࠤ࡫ࡵࡲࠡࠩࠥ᲻") + str(path) + bstack1ll_opy_ (u"ࠨࠧ࠯ࠤ᲼"))
            return path
        except Exception as e:
            logger.debug(bstack1ll_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡶࡲࠣࡪ࡮ࡲࡥࠡࠩࡾࡴࡦࡺࡨࡾࠩ࠽ࠤࠧᲽ") + str(e) + bstack1ll_opy_ (u"ࠣࠤᲾ"))
    logger.debug(bstack1ll_opy_ (u"ࠤࡄࡰࡱࠦࡰࡢࡶ࡫ࡷࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠨᲿ"))
    return None
@measure(event_name=EVENTS.bstack11l1l11l111_opy_, stage=STAGE.bstack1llll11lll_opy_)
def bstack1ll1lllllll_opy_(binary_path, bstack1lll1l111l1_opy_, bs_config):
    logger.debug(bstack1ll_opy_ (u"ࠥࡇࡺࡸࡲࡦࡰࡷࠤࡈࡒࡉࠡࡒࡤࡸ࡭ࠦࡦࡰࡷࡱࡨ࠿ࠦࡻࡾࠤ᳀").format(binary_path))
    bstack111lll11l11_opy_ = bstack1ll_opy_ (u"ࠫࠬ᳁")
    bstack11l11l1l1ll_opy_ = {
        bstack1ll_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ᳂"): __version__,
        bstack1ll_opy_ (u"ࠨ࡯ࡴࠤ᳃"): platform.system(),
        bstack1ll_opy_ (u"ࠢࡰࡵࡢࡥࡷࡩࡨࠣ᳄"): platform.machine(),
        bstack1ll_opy_ (u"ࠣࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ᳅"): bstack1ll_opy_ (u"ࠩ࠳ࠫ᳆"),
        bstack1ll_opy_ (u"ࠥࡷࡩࡱ࡟࡭ࡣࡱ࡫ࡺࡧࡧࡦࠤ᳇"): bstack1ll_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ᳈")
    }
    bstack111lll1111l_opy_(bstack11l11l1l1ll_opy_)
    try:
        if binary_path:
            bstack11l11l1l1ll_opy_[bstack1ll_opy_ (u"ࠬࡩ࡬ࡪࡡࡹࡩࡷࡹࡩࡰࡰࠪ᳉")] = subprocess.check_output([binary_path, bstack1ll_opy_ (u"ࠨࡶࡦࡴࡶ࡭ࡴࡴࠢ᳊")]).strip().decode(bstack1ll_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭᳋"))
        response = requests.request(
            bstack1ll_opy_ (u"ࠨࡉࡈࡘࠬ᳌"),
            url=bstack11llll1111_opy_(bstack11l1l11l1ll_opy_),
            headers=None,
            auth=(bs_config[bstack1ll_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ᳍")], bs_config[bstack1ll_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭᳎")]),
            json=None,
            params=bstack11l11l1l1ll_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack1ll_opy_ (u"ࠫࡺࡸ࡬ࠨ᳏") in data.keys() and bstack1ll_opy_ (u"ࠬࡻࡰࡥࡣࡷࡩࡩࡥࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫ᳐") in data.keys():
            logger.debug(bstack1ll_opy_ (u"ࠨࡎࡦࡧࡧࠤࡹࡵࠠࡶࡲࡧࡥࡹ࡫ࠠࡣ࡫ࡱࡥࡷࡿࠬࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡥ࡭ࡳࡧࡲࡺࠢࡹࡩࡷࡹࡩࡰࡰ࠽ࠤࢀࢃࠢ᳑").format(bstack11l11l1l1ll_opy_[bstack1ll_opy_ (u"ࠧࡤ࡮࡬ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ᳒")]))
            if bstack1ll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡖࡔࡏࠫ᳓") in os.environ:
                logger.debug(bstack1ll_opy_ (u"ࠤࡖ࡯࡮ࡶࡰࡪࡰࡪࠤࡧ࡯࡮ࡢࡴࡼࠤࡩࡵࡷ࡯࡮ࡲࡥࡩࠦࡡࡴࠢࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡕࡇࡏࡤࡈࡉࡏࡃࡕ࡝ࡤ࡛ࡒࡍࠢ࡬ࡷࠥࡹࡥࡵࠤ᳔"))
                data[bstack1ll_opy_ (u"ࠪࡹࡷࡲ᳕ࠧ")] = os.environ[bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢ࡙ࡗࡒ᳖ࠧ")]
            bstack11ll1l1llll_opy_ = bstack11l11111l1l_opy_(data[bstack1ll_opy_ (u"ࠬࡻࡲ࡭᳗ࠩ")], bstack1lll1l111l1_opy_)
            bstack111lll11l11_opy_ = os.path.join(bstack1lll1l111l1_opy_, bstack11ll1l1llll_opy_)
            os.chmod(bstack111lll11l11_opy_, 0o777) # bstack111ll1l11ll_opy_ permission
            return bstack111lll11l11_opy_
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࡯࡮ࡨࠢࡱࡩࡼࠦࡓࡅࡍࠣࡿࢂࠨ᳘").format(e))
    return binary_path
def bstack111lll1111l_opy_(bstack11l11l1l1ll_opy_):
    try:
        if bstack1ll_opy_ (u"ࠧ࡭࡫ࡱࡹࡽ᳙࠭") not in bstack11l11l1l1ll_opy_[bstack1ll_opy_ (u"ࠨࡱࡶࠫ᳚")].lower():
            return
        if os.path.exists(bstack1ll_opy_ (u"ࠤ࠲ࡩࡹࡩ࠯ࡰࡵ࠰ࡶࡪࡲࡥࡢࡵࡨࠦ᳛")):
            with open(bstack1ll_opy_ (u"ࠥ࠳ࡪࡺࡣ࠰ࡱࡶ࠱ࡷ࡫࡬ࡦࡣࡶࡩ᳜ࠧ"), bstack1ll_opy_ (u"ࠦࡷࠨ᳝")) as f:
                bstack11l11l111ll_opy_ = {}
                for line in f:
                    if bstack1ll_opy_ (u"ࠧࡃ᳞ࠢ") in line:
                        key, value = line.rstrip().split(bstack1ll_opy_ (u"ࠨ࠽᳟ࠣ"), 1)
                        bstack11l11l111ll_opy_[key] = value.strip(bstack1ll_opy_ (u"ࠧࠣ࡞ࠪࠫ᳠"))
                bstack11l11l1l1ll_opy_[bstack1ll_opy_ (u"ࠨࡦ࡬ࡷࡹࡸ࡯ࠨ᳡")] = bstack11l11l111ll_opy_.get(bstack1ll_opy_ (u"ࠤࡌࡈ᳢ࠧ"), bstack1ll_opy_ (u"᳣ࠥࠦ"))
        elif os.path.exists(bstack1ll_opy_ (u"ࠦ࠴࡫ࡴࡤ࠱ࡤࡰࡵ࡯࡮ࡦ࠯ࡵࡩࡱ࡫ࡡࡴࡧ᳤ࠥ")):
            bstack11l11l1l1ll_opy_[bstack1ll_opy_ (u"ࠬࡪࡩࡴࡶࡵࡳ᳥ࠬ")] = bstack1ll_opy_ (u"࠭ࡡ࡭ࡲ࡬ࡲࡪ᳦࠭")
    except Exception as e:
        logger.debug(bstack1ll_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣ࡫ࡪࡺࠠࡥ࡫ࡶࡸࡷࡵࠠࡰࡨࠣࡰ࡮ࡴࡵࡹࠤ᳧") + e)
@measure(event_name=EVENTS.bstack11l11ll1111_opy_, stage=STAGE.bstack1llll11lll_opy_)
def bstack11l11111l1l_opy_(bstack111ll1llll1_opy_, bstack11l111111ll_opy_):
    logger.debug(bstack1ll_opy_ (u"ࠣࡆࡲࡻࡳࡲ࡯ࡢࡦ࡬ࡲ࡬ࠦࡓࡅࡍࠣࡦ࡮ࡴࡡࡳࡻࠣࡪࡷࡵ࡭࠻᳨ࠢࠥ") + str(bstack111ll1llll1_opy_) + bstack1ll_opy_ (u"ࠤࠥᳩ"))
    zip_path = os.path.join(bstack11l111111ll_opy_, bstack1ll_opy_ (u"ࠥࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪ࡟ࡧ࡫࡯ࡩ࠳ࢀࡩࡱࠤᳪ"))
    bstack11ll1l1llll_opy_ = bstack1ll_opy_ (u"ࠫࠬᳫ")
    with requests.get(bstack111ll1llll1_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack1ll_opy_ (u"ࠧࡽࡢࠣᳬ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack1ll_opy_ (u"ࠨࡆࡪ࡮ࡨࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࡫ࡤࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿ࠮᳭ࠣ"))
    with zipfile.ZipFile(zip_path, bstack1ll_opy_ (u"ࠧࡳࠩᳮ")) as zip_ref:
        bstack11l111ll111_opy_ = zip_ref.namelist()
        if len(bstack11l111ll111_opy_) > 0:
            bstack11ll1l1llll_opy_ = bstack11l111ll111_opy_[0] # bstack111lll11ll1_opy_ bstack11l11lll1l1_opy_ will be bstack11l11111l11_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack11l111111ll_opy_)
        logger.debug(bstack1ll_opy_ (u"ࠣࡈ࡬ࡰࡪࡹࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾࠦࡥࡹࡶࡵࡥࡨࡺࡥࡥࠢࡷࡳࠥ࠭ࠢᳯ") + str(bstack11l111111ll_opy_) + bstack1ll_opy_ (u"ࠤࠪࠦᳰ"))
    os.remove(zip_path)
    return bstack11ll1l1llll_opy_
def get_cli_dir():
    bstack111ll1ll1l1_opy_ = bstack1ll111l1111_opy_()
    if bstack111ll1ll1l1_opy_:
        bstack1lll1l111l1_opy_ = os.path.join(bstack111ll1ll1l1_opy_, bstack1ll_opy_ (u"ࠥࡧࡱ࡯ࠢᳱ"))
        if not os.path.exists(bstack1lll1l111l1_opy_):
            os.makedirs(bstack1lll1l111l1_opy_, mode=0o777, exist_ok=True)
        return bstack1lll1l111l1_opy_
    else:
        raise FileNotFoundError(bstack1ll_opy_ (u"ࠦࡓࡵࠠࡸࡴ࡬ࡸࡦࡨ࡬ࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥࠡࡨࡲࡶࠥࡺࡨࡦࠢࡖࡈࡐࠦࡢࡪࡰࡤࡶࡾ࠴ࠢᳲ"))
def bstack1lll1l1llll_opy_(bstack1lll1l111l1_opy_):
    bstack1ll_opy_ (u"ࠧࠨࠢࡈࡧࡷࠤࡹ࡮ࡥࠡࡲࡤࡸ࡭ࠦࡦࡰࡴࠣࡸ࡭࡫ࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡓࡅࡍࠣࡦ࡮ࡴࡡࡳࡻࠣ࡭ࡳࠦࡡࠡࡹࡵ࡭ࡹࡧࡢ࡭ࡧࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾ࠴ࠢࠣࠤᳳ")
    bstack11l111ll11l_opy_ = [
        os.path.join(bstack1lll1l111l1_opy_, f)
        for f in os.listdir(bstack1lll1l111l1_opy_)
        if os.path.isfile(os.path.join(bstack1lll1l111l1_opy_, f)) and f.startswith(bstack1ll_opy_ (u"ࠨࡢࡪࡰࡤࡶࡾ࠳ࠢ᳴"))
    ]
    if len(bstack11l111ll11l_opy_) > 0:
        return max(bstack11l111ll11l_opy_, key=os.path.getmtime) # get bstack11lll1l11ll_opy_ binary
    return bstack1ll_opy_ (u"ࠢࠣᳵ")
def bstack11ll111l11l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1l1ll1l1_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll1l1ll1l1_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d