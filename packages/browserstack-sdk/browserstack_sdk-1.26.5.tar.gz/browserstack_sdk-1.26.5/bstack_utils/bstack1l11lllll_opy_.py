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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l11l111l1_opy_, bstack11ll11111ll_opy_
import tempfile
import json
bstack11l11111l1l_opy_ = os.getenv(bstack1l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡏࡓࡌࡥࡆࡊࡎࡈࠦᲝ"), None) or os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡨࡪࡨࡵࡨ࠰࡯ࡳ࡬ࠨᲞ"))
bstack11l111111ll_opy_ = os.path.join(bstack1l1_opy_ (u"ࠧࡲ࡯ࡨࠤᲟ"), bstack1l1_opy_ (u"࠭ࡳࡥ࡭࠰ࡧࡱ࡯࠭ࡥࡧࡥࡹ࡬࠴࡬ࡰࡩࠪᲠ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1l1_opy_ (u"ࠧࠦࠪࡤࡷࡨࡺࡩ࡮ࡧࠬࡷࠥࡡࠥࠩࡰࡤࡱࡪ࠯ࡳ࡞࡝ࠨࠬࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠩࡴ࡟ࠣ࠱ࠥࠫࠨ࡮ࡧࡶࡷࡦ࡭ࡥࠪࡵࠪᲡ"),
      datefmt=bstack1l1_opy_ (u"ࠨࠧ࡜࠱ࠪࡳ࠭ࠦࡦࡗࠩࡍࡀࠥࡎ࠼ࠨࡗ࡟࠭Ტ"),
      stream=sys.stdout
    )
  return logger
def bstack1lllll11l1l_opy_():
  bstack111lllll1l1_opy_ = os.environ.get(bstack1l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡌࡒࡆࡘ࡙ࡠࡆࡈࡆ࡚ࡍࠢᲣ"), bstack1l1_opy_ (u"ࠥࡪࡦࡲࡳࡦࠤᲤ"))
  return logging.DEBUG if bstack111lllll1l1_opy_.lower() == bstack1l1_opy_ (u"ࠦࡹࡸࡵࡦࠤᲥ") else logging.INFO
def bstack1l1lll1ll1l_opy_():
  global bstack11l11111l1l_opy_
  if os.path.exists(bstack11l11111l1l_opy_):
    os.remove(bstack11l11111l1l_opy_)
  if os.path.exists(bstack11l111111ll_opy_):
    os.remove(bstack11l111111ll_opy_)
def bstack1ll11l1l1l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def bstack1ll1111l_opy_(config, log_level):
  bstack11l1111l1ll_opy_ = log_level
  if bstack1l1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᲦ") in config and config[bstack1l1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᲧ")] in bstack11l11l111l1_opy_:
    bstack11l1111l1ll_opy_ = bstack11l11l111l1_opy_[config[bstack1l1_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᲨ")]]
  if config.get(bstack1l1_opy_ (u"ࠨࡦ࡬ࡷࡦࡨ࡬ࡦࡃࡸࡸࡴࡉࡡࡱࡶࡸࡶࡪࡒ࡯ࡨࡵࠪᲩ"), False):
    logging.getLogger().setLevel(bstack11l1111l1ll_opy_)
    return bstack11l1111l1ll_opy_
  global bstack11l11111l1l_opy_
  bstack1ll11l1l1l_opy_()
  bstack111llll1l1l_opy_ = logging.Formatter(
    fmt=bstack1l1_opy_ (u"ࠩࠨࠬࡦࡹࡣࡵ࡫ࡰࡩ࠮ࡹࠠ࡜ࠧࠫࡲࡦࡳࡥࠪࡵࡠ࡟ࠪ࠮࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠫࡶࡡࠥ࠳ࠠࠦࠪࡰࡩࡸࡹࡡࡨࡧࠬࡷࠬᲪ"),
    datefmt=bstack1l1_opy_ (u"ࠪࠩ࡞࠳ࠥ࡮࠯ࠨࡨ࡙ࠫࡈ࠻ࠧࡐ࠾࡙࡚ࠪࠨᲫ"),
  )
  bstack11l1111l1l1_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack11l11111l1l_opy_)
  file_handler.setFormatter(bstack111llll1l1l_opy_)
  bstack11l1111l1l1_opy_.setFormatter(bstack111llll1l1l_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack11l1111l1l1_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡵࡩࡲࡵࡴࡦ࠰ࡵࡩࡲࡵࡴࡦࡡࡦࡳࡳࡴࡥࡤࡶ࡬ࡳࡳ࠭Წ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack11l1111l1l1_opy_.setLevel(bstack11l1111l1ll_opy_)
  logging.getLogger().addHandler(bstack11l1111l1l1_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack11l1111l1ll_opy_
def bstack11l111111l1_opy_(config):
  try:
    bstack111llll1ll1_opy_ = set(bstack11ll11111ll_opy_)
    bstack111llllll11_opy_ = bstack1l1_opy_ (u"ࠬ࠭Ჭ")
    with open(bstack1l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩᲮ")) as bstack111lllllll1_opy_:
      bstack111lllll11l_opy_ = bstack111lllllll1_opy_.read()
      bstack111llllll11_opy_ = re.sub(bstack1l1_opy_ (u"ࡲࠨࡠࠫࡠࡸ࠱ࠩࡀࠥ࠱࠮ࠩࡢ࡮ࠨᲯ"), bstack1l1_opy_ (u"ࠨࠩᲰ"), bstack111lllll11l_opy_, flags=re.M)
      bstack111llllll11_opy_ = re.sub(
        bstack1l1_opy_ (u"ࡴࠪࡢ࠭ࡢࡳࠬࠫࡂࠬࠬᲱ") + bstack1l1_opy_ (u"ࠪࢀࠬᲲ").join(bstack111llll1ll1_opy_) + bstack1l1_opy_ (u"ࠫ࠮࠴ࠪࠥࠩᲳ"),
        bstack1l1_opy_ (u"ࡷ࠭࡜࠳࠼ࠣ࡟ࡗࡋࡄࡂࡅࡗࡉࡉࡣࠧᲴ"),
        bstack111llllll11_opy_, flags=re.M | re.I
      )
    def bstack11l1111l111_opy_(dic):
      bstack111llll1lll_opy_ = {}
      for key, value in dic.items():
        if key in bstack111llll1ll1_opy_:
          bstack111llll1lll_opy_[key] = bstack1l1_opy_ (u"࡛࠭ࡓࡇࡇࡅࡈ࡚ࡅࡅ࡟ࠪᲵ")
        else:
          if isinstance(value, dict):
            bstack111llll1lll_opy_[key] = bstack11l1111l111_opy_(value)
          else:
            bstack111llll1lll_opy_[key] = value
      return bstack111llll1lll_opy_
    bstack111llll1lll_opy_ = bstack11l1111l111_opy_(config)
    return {
      bstack1l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪᲶ"): bstack111llllll11_opy_,
      bstack1l1_opy_ (u"ࠨࡨ࡬ࡲࡦࡲࡣࡰࡰࡩ࡭࡬࠴ࡪࡴࡱࡱࠫᲷ"): json.dumps(bstack111llll1lll_opy_)
    }
  except Exception as e:
    return {}
def bstack11l1111l11l_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1l1_opy_ (u"ࠩ࡯ࡳ࡬࠭Ჸ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111llllll1l_opy_ = os.path.join(log_dir, bstack1l1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡧࡴࡴࡦࡪࡩࡶࠫᲹ"))
  if not os.path.exists(bstack111llllll1l_opy_):
    bstack11l11111111_opy_ = {
      bstack1l1_opy_ (u"ࠦ࡮ࡴࡩࡱࡣࡷ࡬ࠧᲺ"): str(inipath),
      bstack1l1_opy_ (u"ࠧࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠢ᲻"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡣࡰࡰࡩ࡭࡬ࡹ࠮࡫ࡵࡲࡲࠬ᲼")), bstack1l1_opy_ (u"ࠧࡸࠩᲽ")) as bstack11l1111111l_opy_:
      bstack11l1111111l_opy_.write(json.dumps(bstack11l11111111_opy_))
def bstack11l11111l11_opy_():
  try:
    bstack111llllll1l_opy_ = os.path.join(os.getcwd(), bstack1l1_opy_ (u"ࠨ࡮ࡲ࡫ࠬᲾ"), bstack1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵ࠱࡮ࡸࡵ࡮ࠨᲿ"))
    if os.path.exists(bstack111llllll1l_opy_):
      with open(bstack111llllll1l_opy_, bstack1l1_opy_ (u"ࠪࡶࠬ᳀")) as bstack11l1111111l_opy_:
        bstack11l11111ll1_opy_ = json.load(bstack11l1111111l_opy_)
      return bstack11l11111ll1_opy_.get(bstack1l1_opy_ (u"ࠫ࡮ࡴࡩࡱࡣࡷ࡬ࠬ᳁"), bstack1l1_opy_ (u"ࠬ࠭᳂")), bstack11l11111ll1_opy_.get(bstack1l1_opy_ (u"࠭ࡲࡰࡱࡷࡴࡦࡺࡨࠨ᳃"), bstack1l1_opy_ (u"ࠧࠨ᳄"))
  except:
    pass
  return None, None
def bstack111lllll111_opy_():
  try:
    bstack111llllll1l_opy_ = os.path.join(os.getcwd(), bstack1l1_opy_ (u"ࠨ࡮ࡲ࡫ࠬ᳅"), bstack1l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵ࠱࡮ࡸࡵ࡮ࠨ᳆"))
    if os.path.exists(bstack111llllll1l_opy_):
      os.remove(bstack111llllll1l_opy_)
  except:
    pass
def bstack1ll1ll11l1_opy_(config):
  from bstack_utils.helper import bstack1ll11l111l_opy_
  global bstack11l11111l1l_opy_
  try:
    if config.get(bstack1l1_opy_ (u"ࠪࡨ࡮ࡹࡡࡣ࡮ࡨࡅࡺࡺ࡯ࡄࡣࡳࡸࡺࡸࡥࡍࡱࡪࡷࠬ᳇"), False):
      return
    uuid = os.getenv(bstack1l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩ᳈")) if os.getenv(bstack1l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪ᳉")) else bstack1ll11l111l_opy_.get_property(bstack1l1_opy_ (u"ࠨࡳࡥ࡭ࡕࡹࡳࡏࡤࠣ᳊"))
    if not uuid or uuid == bstack1l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ᳋"):
      return
    bstack11l11111lll_opy_ = [bstack1l1_opy_ (u"ࠨࡴࡨࡵࡺ࡯ࡲࡦ࡯ࡨࡲࡹࡹ࠮ࡵࡺࡷࠫ᳌"), bstack1l1_opy_ (u"ࠩࡓ࡭ࡵ࡬ࡩ࡭ࡧࠪ᳍"), bstack1l1_opy_ (u"ࠪࡴࡾࡶࡲࡰ࡬ࡨࡧࡹ࠴ࡴࡰ࡯࡯ࠫ᳎"), bstack11l11111l1l_opy_, bstack11l111111ll_opy_]
    bstack111lllll1ll_opy_, root_path = bstack11l11111l11_opy_()
    if bstack111lllll1ll_opy_ != None:
      bstack11l11111lll_opy_.append(bstack111lllll1ll_opy_)
    if root_path != None:
      bstack11l11111lll_opy_.append(os.path.join(root_path, bstack1l1_opy_ (u"ࠫࡨࡵ࡮ࡧࡶࡨࡷࡹ࠴ࡰࡺࠩ᳏")))
    bstack1ll11l1l1l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1l1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠲ࡲ࡯ࡨࡵ࠰ࠫ᳐") + uuid + bstack1l1_opy_ (u"࠭࠮ࡵࡣࡵ࠲࡬ࢀࠧ᳑"))
    with tarfile.open(output_file, bstack1l1_opy_ (u"ࠢࡸ࠼ࡪࡾࠧ᳒")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack11l11111lll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack11l111111l1_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111llllllll_opy_ = data.encode()
        tarinfo.size = len(bstack111llllllll_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111llllllll_opy_))
    bstack111l1l1ll_opy_ = MultipartEncoder(
      fields= {
        bstack1l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭᳓"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1l1_opy_ (u"ࠩࡵࡦ᳔ࠬ")), bstack1l1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰ࡺ࠰࡫ࡿ࡯ࡰࠨ᳕")),
        bstack1l1_opy_ (u"ࠫࡨࡲࡩࡦࡰࡷࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ᳖࠭"): uuid
      }
    )
    response = requests.post(
      bstack1l1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡵࡱ࡮ࡲࡥࡩ࠳࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡦࡰ࡮࡫࡮ࡵ࠯࡯ࡳ࡬ࡹ࠯ࡶࡲ࡯ࡳࡦࡪ᳗ࠢ"),
      data=bstack111l1l1ll_opy_,
      headers={bstack1l1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩ᳘ࠬ"): bstack111l1l1ll_opy_.content_type},
      auth=(config[bstack1l1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦ᳙ࠩ")], config[bstack1l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫ᳚")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1l1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡࡷࡳࡰࡴࡧࡤࠡ࡮ࡲ࡫ࡸࡀࠠࠨ᳛") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡩࡳࡪࡩ࡯ࡩࠣࡰࡴ࡭ࡳ࠻᳜ࠩ") + str(e))
  finally:
    try:
      bstack1l1lll1ll1l_opy_()
      bstack111lllll111_opy_()
    except:
      pass