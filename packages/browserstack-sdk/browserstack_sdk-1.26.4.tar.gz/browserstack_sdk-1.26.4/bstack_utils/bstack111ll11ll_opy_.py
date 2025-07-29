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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1l11l1l1_opy_, bstack11l1l111l11_opy_
import tempfile
import json
bstack111l1lll11l_opy_ = os.getenv(bstack1ll_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡋࡤࡌࡉࡍࡇࠥᴡ"), None) or os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠧᴢ"))
bstack111l1l1ll1l_opy_ = os.path.join(bstack1ll_opy_ (u"ࠦࡱࡵࡧࠣᴣ"), bstack1ll_opy_ (u"ࠬࡹࡤ࡬࠯ࡦࡰ࡮࠳ࡤࡦࡤࡸ࡫࠳ࡲ࡯ࡨࠩᴤ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1ll_opy_ (u"࠭ࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩᴥ"),
      datefmt=bstack1ll_opy_ (u"࡛ࠧࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࡞ࠬᴦ"),
      stream=sys.stdout
    )
  return logger
def bstack1llll1ll11l_opy_():
  bstack111l1ll1l11_opy_ = os.environ.get(bstack1ll_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡅࡇࡅ࡙ࡌࠨᴧ"), bstack1ll_opy_ (u"ࠤࡩࡥࡱࡹࡥࠣᴨ"))
  return logging.DEBUG if bstack111l1ll1l11_opy_.lower() == bstack1ll_opy_ (u"ࠥࡸࡷࡻࡥࠣᴩ") else logging.INFO
def bstack1l1ll1l1lll_opy_():
  global bstack111l1lll11l_opy_
  if os.path.exists(bstack111l1lll11l_opy_):
    os.remove(bstack111l1lll11l_opy_)
  if os.path.exists(bstack111l1l1ll1l_opy_):
    os.remove(bstack111l1l1ll1l_opy_)
def bstack1l1lllll1l_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def bstack1l1l1ll1ll_opy_(config, log_level):
  bstack111l1ll111l_opy_ = log_level
  if bstack1ll_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ᴪ") in config and config[bstack1ll_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᴫ")] in bstack11l1l11l1l1_opy_:
    bstack111l1ll111l_opy_ = bstack11l1l11l1l1_opy_[config[bstack1ll_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᴬ")]]
  if config.get(bstack1ll_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩᴭ"), False):
    logging.getLogger().setLevel(bstack111l1ll111l_opy_)
    return bstack111l1ll111l_opy_
  global bstack111l1lll11l_opy_
  bstack1l1lllll1l_opy_()
  bstack111l1l1lll1_opy_ = logging.Formatter(
    fmt=bstack1ll_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫᴮ"),
    datefmt=bstack1ll_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧᴯ"),
  )
  bstack111l1ll1111_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l1lll11l_opy_)
  file_handler.setFormatter(bstack111l1l1lll1_opy_)
  bstack111l1ll1111_opy_.setFormatter(bstack111l1l1lll1_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l1ll1111_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1ll_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࠳ࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡴࡨࡱࡴࡺࡥ࠯ࡴࡨࡱࡴࡺࡥࡠࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲࠬᴰ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l1ll1111_opy_.setLevel(bstack111l1ll111l_opy_)
  logging.getLogger().addHandler(bstack111l1ll1111_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l1ll111l_opy_
def bstack111l1lll111_opy_(config):
  try:
    bstack111l1ll11ll_opy_ = set(bstack11l1l111l11_opy_)
    bstack111l1l1l11l_opy_ = bstack1ll_opy_ (u"ࠫࠬᴱ")
    with open(bstack1ll_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨᴲ")) as bstack111l1lll1l1_opy_:
      bstack111l1l11ll1_opy_ = bstack111l1lll1l1_opy_.read()
      bstack111l1l1l11l_opy_ = re.sub(bstack1ll_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠤ࠰࠭ࠨࡡࡴࠧᴳ"), bstack1ll_opy_ (u"ࠧࠨᴴ"), bstack111l1l11ll1_opy_, flags=re.M)
      bstack111l1l1l11l_opy_ = re.sub(
        bstack1ll_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠫࠫᴵ") + bstack1ll_opy_ (u"ࠩࡿࠫᴶ").join(bstack111l1ll11ll_opy_) + bstack1ll_opy_ (u"ࠪ࠭࠳࠰ࠤࠨᴷ"),
        bstack1ll_opy_ (u"ࡶࠬࡢ࠲࠻ࠢ࡞ࡖࡊࡊࡁࡄࡖࡈࡈࡢ࠭ᴸ"),
        bstack111l1l1l11l_opy_, flags=re.M | re.I
      )
    def bstack111l1l1l1ll_opy_(dic):
      bstack111l1ll11l1_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l1ll11ll_opy_:
          bstack111l1ll11l1_opy_[key] = bstack1ll_opy_ (u"ࠬࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩᴹ")
        else:
          if isinstance(value, dict):
            bstack111l1ll11l1_opy_[key] = bstack111l1l1l1ll_opy_(value)
          else:
            bstack111l1ll11l1_opy_[key] = value
      return bstack111l1ll11l1_opy_
    bstack111l1ll11l1_opy_ = bstack111l1l1l1ll_opy_(config)
    return {
      bstack1ll_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩᴺ"): bstack111l1l1l11l_opy_,
      bstack1ll_opy_ (u"ࠧࡧ࡫ࡱࡥࡱࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪᴻ"): json.dumps(bstack111l1ll11l1_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1ll1l1l_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1ll_opy_ (u"ࠨ࡮ࡲ࡫ࠬᴼ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack11llll11ll1_opy_ = os.path.join(log_dir, bstack1ll_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵࠪᴽ"))
  if not os.path.exists(bstack11llll11ll1_opy_):
    bstack111l1ll1ll1_opy_ = {
      bstack1ll_opy_ (u"ࠥ࡭ࡳ࡯ࡰࡢࡶ࡫ࠦᴾ"): str(inipath),
      bstack1ll_opy_ (u"ࠦࡷࡵ࡯ࡵࡲࡤࡸ࡭ࠨᴿ"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1ll_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠴ࡪࡴࡱࡱࠫᵀ")), bstack1ll_opy_ (u"࠭ࡷࠨᵁ")) as bstack111l1l1l1l1_opy_:
      bstack111l1l1l1l1_opy_.write(json.dumps(bstack111l1ll1ll1_opy_))
def bstack111l1lll1ll_opy_():
  try:
    bstack11llll11ll1_opy_ = os.path.join(os.getcwd(), bstack1ll_opy_ (u"ࠧ࡭ࡱࡪࠫᵂ"), bstack1ll_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧᵃ"))
    if os.path.exists(bstack11llll11ll1_opy_):
      with open(bstack11llll11ll1_opy_, bstack1ll_opy_ (u"ࠩࡵࠫᵄ")) as bstack111l1l1l1l1_opy_:
        bstack111l1l1llll_opy_ = json.load(bstack111l1l1l1l1_opy_)
      return bstack111l1l1llll_opy_.get(bstack1ll_opy_ (u"ࠪ࡭ࡳ࡯ࡰࡢࡶ࡫ࠫᵅ"), bstack1ll_opy_ (u"ࠫࠬᵆ")), bstack111l1l1llll_opy_.get(bstack1ll_opy_ (u"ࠬࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠧᵇ"), bstack1ll_opy_ (u"࠭ࠧᵈ"))
  except:
    pass
  return None, None
def bstack111l1l1l111_opy_():
  try:
    bstack11llll11ll1_opy_ = os.path.join(os.getcwd(), bstack1ll_opy_ (u"ࠧ࡭ࡱࡪࠫᵉ"), bstack1ll_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧᵊ"))
    if os.path.exists(bstack11llll11ll1_opy_):
      os.remove(bstack11llll11ll1_opy_)
  except:
    pass
def bstack11l111lll1_opy_(config):
  from bstack_utils.helper import bstack1lll1111ll_opy_
  global bstack111l1lll11l_opy_
  try:
    if config.get(bstack1ll_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫᵋ"), False):
      return
    uuid = os.getenv(bstack1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨᵌ")) if os.getenv(bstack1ll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᵍ")) else bstack1lll1111ll_opy_.get_property(bstack1ll_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢᵎ"))
    if not uuid or uuid == bstack1ll_opy_ (u"࠭࡮ࡶ࡮࡯ࠫᵏ"):
      return
    bstack111l1l11lll_opy_ = [bstack1ll_opy_ (u"ࠧࡳࡧࡴࡹ࡮ࡸࡥ࡮ࡧࡱࡸࡸ࠴ࡴࡹࡶࠪᵐ"), bstack1ll_opy_ (u"ࠨࡒ࡬ࡴ࡫࡯࡬ࡦࠩᵑ"), bstack1ll_opy_ (u"ࠩࡳࡽࡵࡸ࡯࡫ࡧࡦࡸ࠳ࡺ࡯࡮࡮ࠪᵒ"), bstack111l1lll11l_opy_, bstack111l1l1ll1l_opy_]
    bstack111l1ll1lll_opy_, root_path = bstack111l1lll1ll_opy_()
    if bstack111l1ll1lll_opy_ != None:
      bstack111l1l11lll_opy_.append(bstack111l1ll1lll_opy_)
    if root_path != None:
      bstack111l1l11lll_opy_.append(os.path.join(root_path, bstack1ll_opy_ (u"ࠪࡧࡴࡴࡦࡵࡧࡶࡸ࠳ࡶࡹࠨᵓ")))
    bstack1l1lllll1l_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1ll_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡱࡵࡧࡴ࠯ࠪᵔ") + uuid + bstack1ll_opy_ (u"ࠬ࠴ࡴࡢࡴ࠱࡫ࡿ࠭ᵕ"))
    with tarfile.open(output_file, bstack1ll_opy_ (u"ࠨࡷ࠻ࡩࡽࠦᵖ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1l11lll_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l1lll111_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1l1ll11_opy_ = data.encode()
        tarinfo.size = len(bstack111l1l1ll11_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1l1ll11_opy_))
    bstack11ll1lll11_opy_ = MultipartEncoder(
      fields= {
        bstack1ll_opy_ (u"ࠧࡥࡣࡷࡥࠬᵗ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1ll_opy_ (u"ࠨࡴࡥࠫᵘ")), bstack1ll_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯ࡹ࠯ࡪࡾ࡮ࡶࠧᵙ")),
        bstack1ll_opy_ (u"ࠪࡧࡱ࡯ࡥ࡯ࡶࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬᵚ"): uuid
      }
    )
    response = requests.post(
      bstack1ll_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡻࡰ࡭ࡱࡤࡨ࠲ࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡥ࡯࡭ࡪࡴࡴ࠮࡮ࡲ࡫ࡸ࠵ࡵࡱ࡮ࡲࡥࡩࠨᵛ"),
      data=bstack11ll1lll11_opy_,
      headers={bstack1ll_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫᵜ"): bstack11ll1lll11_opy_.content_type},
      auth=(config[bstack1ll_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨᵝ")], config[bstack1ll_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪᵞ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1ll_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡶࡲ࡯ࡳࡦࡪࠠ࡭ࡱࡪࡷ࠿ࠦࠧᵟ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1ll_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡲࡩ࡯࡮ࡨࠢ࡯ࡳ࡬ࡹ࠺ࠨᵠ") + str(e))
  finally:
    try:
      bstack1l1ll1l1lll_opy_()
      bstack111l1l1l111_opy_()
    except:
      pass