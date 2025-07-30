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
import threading
import logging
logger = logging.getLogger(__name__)
bstack1111llll1l1_opy_ = 1000
bstack1111lllll1l_opy_ = 2
class bstack1111llll11l_opy_:
    def __init__(self, handler, bstack1111llllll1_opy_=bstack1111llll1l1_opy_, bstack1111lllll11_opy_=bstack1111lllll1l_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1111llllll1_opy_ = bstack1111llllll1_opy_
        self.bstack1111lllll11_opy_ = bstack1111lllll11_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1111l11l11_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1111lll1lll_opy_()
    def bstack1111lll1lll_opy_(self):
        self.bstack1111l11l11_opy_ = threading.Event()
        def bstack1111llll1ll_opy_():
            self.bstack1111l11l11_opy_.wait(self.bstack1111lllll11_opy_)
            if not self.bstack1111l11l11_opy_.is_set():
                self.bstack1111llll111_opy_()
        self.timer = threading.Thread(target=bstack1111llll1ll_opy_, daemon=True)
        self.timer.start()
    def bstack1111lll1l11_opy_(self):
        try:
            if self.bstack1111l11l11_opy_ and not self.bstack1111l11l11_opy_.is_set():
                self.bstack1111l11l11_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1l1_opy_ (u"࡛࠭ࡴࡶࡲࡴࡤࡺࡩ࡮ࡧࡵࡡࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮࠻ࠢࠪḨ") + (str(e) or bstack1l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡧࡴࡻ࡬ࡥࠢࡱࡳࡹࠦࡢࡦࠢࡦࡳࡳࡼࡥࡳࡶࡨࡨࠥࡺ࡯ࠡࡵࡷࡶ࡮ࡴࡧࠣḩ")))
        finally:
            self.timer = None
    def bstack1111lll1l1l_opy_(self):
        if self.timer:
            self.bstack1111lll1l11_opy_()
        self.bstack1111lll1lll_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1111llllll1_opy_:
                threading.Thread(target=self.bstack1111llll111_opy_).start()
    def bstack1111llll111_opy_(self, source = bstack1l1_opy_ (u"ࠨࠩḪ")):
        with self.lock:
            if not self.queue:
                self.bstack1111lll1l1l_opy_()
                return
            data = self.queue[:self.bstack1111llllll1_opy_]
            del self.queue[:self.bstack1111llllll1_opy_]
        self.handler(data)
        if source != bstack1l1_opy_ (u"ࠩࡶ࡬ࡺࡺࡤࡰࡹࡱࠫḫ"):
            self.bstack1111lll1l1l_opy_()
    def shutdown(self):
        self.bstack1111lll1l11_opy_()
        while self.queue:
            self.bstack1111llll111_opy_(source=bstack1l1_opy_ (u"ࠪࡷ࡭ࡻࡴࡥࡱࡺࡲࠬḬ"))