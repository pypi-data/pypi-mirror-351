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
import os
from uuid import uuid4
from bstack_utils.helper import bstack11ll111lll_opy_, bstack111ll1l1l1l_opy_
from bstack_utils.bstack1lll1l1l1l_opy_ import bstack111l1111l1l_opy_
class bstack111l1l111l_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1111ll11l11_opy_=None, bstack1111l1ll11l_opy_=True, bstack1l11l1111ll_opy_=None, bstack1ll1lll1l1_opy_=None, result=None, duration=None, bstack111ll1lll1_opy_=None, meta={}):
        self.bstack111ll1lll1_opy_ = bstack111ll1lll1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1111l1ll11l_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1111ll11l11_opy_ = bstack1111ll11l11_opy_
        self.bstack1l11l1111ll_opy_ = bstack1l11l1111ll_opy_
        self.bstack1ll1lll1l1_opy_ = bstack1ll1lll1l1_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l11llll_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111lllllll_opy_(self, meta):
        self.meta = meta
    def bstack11l11111ll_opy_(self, hooks):
        self.hooks = hooks
    def bstack1111ll1111l_opy_(self):
        bstack1111ll11ll1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1ll_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨṴ"): bstack1111ll11ll1_opy_,
            bstack1ll_opy_ (u"࠭࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠨṵ"): bstack1111ll11ll1_opy_,
            bstack1ll_opy_ (u"ࠧࡷࡥࡢࡪ࡮ࡲࡥࡱࡣࡷ࡬ࠬṶ"): bstack1111ll11ll1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1ll_opy_ (u"ࠣࡗࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡧࡲࡨࡷࡰࡩࡳࡺ࠺ࠡࠤṷ") + key)
            setattr(self, key, val)
    def bstack1111l1llll1_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧṸ"): self.name,
            bstack1ll_opy_ (u"ࠪࡦࡴࡪࡹࠨṹ"): {
                bstack1ll_opy_ (u"ࠫࡱࡧ࡮ࡨࠩṺ"): bstack1ll_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬṻ"),
                bstack1ll_opy_ (u"࠭ࡣࡰࡦࡨࠫṼ"): self.code
            },
            bstack1ll_opy_ (u"ࠧࡴࡥࡲࡴࡪࡹࠧṽ"): self.scope,
            bstack1ll_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭Ṿ"): self.tags,
            bstack1ll_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬṿ"): self.framework,
            bstack1ll_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧẀ"): self.started_at
        }
    def bstack1111ll11111_opy_(self):
        return {
         bstack1ll_opy_ (u"ࠫࡲ࡫ࡴࡢࠩẁ"): self.meta
        }
    def bstack1111l1lll1l_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡗ࡫ࡲࡶࡰࡓࡥࡷࡧ࡭ࠨẂ"): {
                bstack1ll_opy_ (u"࠭ࡲࡦࡴࡸࡲࡤࡴࡡ࡮ࡧࠪẃ"): self.bstack1111ll11l11_opy_
            }
        }
    def bstack1111l1lll11_opy_(self, bstack1111l1ll1l1_opy_, details):
        step = next(filter(lambda st: st[bstack1ll_opy_ (u"ࠧࡪࡦࠪẄ")] == bstack1111l1ll1l1_opy_, self.meta[bstack1ll_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧẅ")]), None)
        step.update(details)
    def bstack11l1l11l1l_opy_(self, bstack1111l1ll1l1_opy_):
        step = next(filter(lambda st: st[bstack1ll_opy_ (u"ࠩ࡬ࡨࠬẆ")] == bstack1111l1ll1l1_opy_, self.meta[bstack1ll_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩẇ")]), None)
        step.update({
            bstack1ll_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨẈ"): bstack11ll111lll_opy_()
        })
    def bstack111llll11l_opy_(self, bstack1111l1ll1l1_opy_, result, duration=None):
        bstack1l11l1111ll_opy_ = bstack11ll111lll_opy_()
        if bstack1111l1ll1l1_opy_ is not None and self.meta.get(bstack1ll_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫẉ")):
            step = next(filter(lambda st: st[bstack1ll_opy_ (u"࠭ࡩࡥࠩẊ")] == bstack1111l1ll1l1_opy_, self.meta[bstack1ll_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ẋ")]), None)
            step.update({
                bstack1ll_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭Ẍ"): bstack1l11l1111ll_opy_,
                bstack1ll_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫẍ"): duration if duration else bstack111ll1l1l1l_opy_(step[bstack1ll_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧẎ")], bstack1l11l1111ll_opy_),
                bstack1ll_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫẏ"): result.result,
                bstack1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭Ẑ"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1111l1ll111_opy_):
        if self.meta.get(bstack1ll_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬẑ")):
            self.meta[bstack1ll_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭Ẓ")].append(bstack1111l1ll111_opy_)
        else:
            self.meta[bstack1ll_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧẓ")] = [ bstack1111l1ll111_opy_ ]
    def bstack1111l1ll1ll_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠩࡸࡹ࡮ࡪࠧẔ"): self.bstack111l11llll_opy_(),
            **self.bstack1111l1llll1_opy_(),
            **self.bstack1111ll1111l_opy_(),
            **self.bstack1111ll11111_opy_()
        }
    def bstack1111l1l1ll1_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1ll_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨẕ"): self.bstack1l11l1111ll_opy_,
            bstack1ll_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬẖ"): self.duration,
            bstack1ll_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬẗ"): self.result.result
        }
        if data[bstack1ll_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ẘ")] == bstack1ll_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧẙ"):
            data[bstack1ll_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࡡࡷࡽࡵ࡫ࠧẚ")] = self.result.bstack1111l11ll1_opy_()
            data[bstack1ll_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪẛ")] = [{bstack1ll_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ẜ"): self.result.bstack11l1111111l_opy_()}]
        return data
    def bstack1111l1lllll_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠫࡺࡻࡩࡥࠩẝ"): self.bstack111l11llll_opy_(),
            **self.bstack1111l1llll1_opy_(),
            **self.bstack1111ll1111l_opy_(),
            **self.bstack1111l1l1ll1_opy_(),
            **self.bstack1111ll11111_opy_()
        }
    def bstack111ll1l1ll_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1ll_opy_ (u"࡙ࠬࡴࡢࡴࡷࡩࡩ࠭ẞ") in event:
            return self.bstack1111l1ll1ll_opy_()
        elif bstack1ll_opy_ (u"࠭ࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨẟ") in event:
            return self.bstack1111l1lllll_opy_()
    def bstack111l11111l_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l11l1111ll_opy_ = time if time else bstack11ll111lll_opy_()
        self.duration = duration if duration else bstack111ll1l1l1l_opy_(self.started_at, self.bstack1l11l1111ll_opy_)
        if result:
            self.result = result
class bstack111lll111l_opy_(bstack111l1l111l_opy_):
    def __init__(self, hooks=[], bstack11l1111l1l_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack11l1111l1l_opy_ = bstack11l1111l1l_opy_
        super().__init__(*args, **kwargs, bstack1ll1lll1l1_opy_=bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࠬẠ"))
    @classmethod
    def bstack1111l1l1l1l_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1ll_opy_ (u"ࠨ࡫ࡧࠫạ"): id(step),
                bstack1ll_opy_ (u"ࠩࡷࡩࡽࡺࠧẢ"): step.name,
                bstack1ll_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫả"): step.keyword,
            })
        return bstack111lll111l_opy_(
            **kwargs,
            meta={
                bstack1ll_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬẤ"): {
                    bstack1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪấ"): feature.name,
                    bstack1ll_opy_ (u"࠭ࡰࡢࡶ࡫ࠫẦ"): feature.filename,
                    bstack1ll_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬầ"): feature.description
                },
                bstack1ll_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪẨ"): {
                    bstack1ll_opy_ (u"ࠩࡱࡥࡲ࡫ࠧẩ"): scenario.name
                },
                bstack1ll_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩẪ"): steps,
                bstack1ll_opy_ (u"ࠫࡪࡾࡡ࡮ࡲ࡯ࡩࡸ࠭ẫ"): bstack111l1111l1l_opy_(test)
            }
        )
    def bstack1111l1l1lll_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫẬ"): self.hooks
        }
    def bstack1111ll111ll_opy_(self):
        if self.bstack11l1111l1l_opy_:
            return {
                bstack1ll_opy_ (u"࠭ࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠬậ"): self.bstack11l1111l1l_opy_
            }
        return {}
    def bstack1111l1lllll_opy_(self):
        return {
            **super().bstack1111l1lllll_opy_(),
            **self.bstack1111l1l1lll_opy_()
        }
    def bstack1111l1ll1ll_opy_(self):
        return {
            **super().bstack1111l1ll1ll_opy_(),
            **self.bstack1111ll111ll_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩẮ")
class bstack11l1111111_opy_(bstack111l1l111l_opy_):
    def __init__(self, hook_type, *args,bstack11l1111l1l_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1111ll111l1_opy_ = None
        self.bstack11l1111l1l_opy_ = bstack11l1111l1l_opy_
        super().__init__(*args, **kwargs, bstack1ll1lll1l1_opy_=bstack1ll_opy_ (u"ࠨࡪࡲࡳࡰ࠭ắ"))
    def bstack111l1l1lll_opy_(self):
        return self.hook_type
    def bstack1111ll11l1l_opy_(self):
        return {
            bstack1ll_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬẰ"): self.hook_type
        }
    def bstack1111l1lllll_opy_(self):
        return {
            **super().bstack1111l1lllll_opy_(),
            **self.bstack1111ll11l1l_opy_()
        }
    def bstack1111l1ll1ll_opy_(self):
        return {
            **super().bstack1111l1ll1ll_opy_(),
            bstack1ll_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡯ࡤࠨằ"): self.bstack1111ll111l1_opy_,
            **self.bstack1111ll11l1l_opy_()
        }
    def bstack111l11111l_opy_(self):
        return bstack1ll_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭Ẳ")
    def bstack111lll1l11_opy_(self, bstack1111ll111l1_opy_):
        self.bstack1111ll111l1_opy_ = bstack1111ll111l1_opy_