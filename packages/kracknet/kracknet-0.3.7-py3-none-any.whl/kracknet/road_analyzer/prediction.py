import numpy as np
import cv2
import json
from rs4.annotations import override
from ..utils import image_format
from ..prediction import BasePrediction

class Prediction (BasePrediction):
  @override
  def __init__ (self, img_path, response):
    super ().__init__ (img_path, response)
    if 'transformFactors' in self.result:
      self.transform_factors = self.result ['transformFactors']
    else:
      self.transform_factors = None
    self.code_table = None

  @override
  def get_summary (self) -> dict:
    summary = []
    for k, v in self.result ['summary'].items ():
      summary.append ({
        'type': k,
        'metric': 'Length' if k == 'crack' else 'Area',
        'unit': 'm' if k == 'crack' else '㎡',
        'value': v
      })
    return summary

  def plot (self, show_label = True) -> cv2.typing.MatLike:
    im = super ().plot (show_label)
    if not self.transform_factors:
      return im

    top = [None, None]
    bot = [None, None]
    for it in self:
      if it ['label'] == 'XPLMLN':
        top [0] = it ['points'][0]
        bot [0] = it ['points'][1]
      elif it ['label'] == 'XPRMLN':
        top [1] = it ['points'][0]
        bot [1] = it ['points'][1]

    if top [0] is not None and top [1] is not None:
      self.draw (im, {'label': 'XPLMLN', 'points': top, 'shape_type': "linestrip", 'severity': 'Minor', 'score': 0}, show_label = False)
      self.draw (im, {'label': 'XPRMLN', 'points': bot, 'shape_type': "linestrip", 'severity': 'Minor', 'score': 0}, show_label = False)

    return im

  def generate_bev (self, height, width = 'AUTO', plot = False, show_label = True) -> cv2.typing.MatLike:
    def translatep (M, p):
      r = M [2][0] * p [0] + M [2][1] * p [1] + M [2][2]
      px = (M [0][0] * p [0] + M [0][1] * p [1] + M [0][2]) / r
      py = (M [1][0] * p [0] + M [1][1] * p [1] + M [1][2]) / r
      return np.array ([px, py])

    def translate (M, ps):
      r = M [2][0] * ps [:,0] + M [2][1] * ps [:,1] + M [2][2]
      ps [:,0] = (M [0][0] * ps [:,0] + M [0][1] * ps [:,1] + M [0][2]) / r
      ps [:,1] = (M [1][0] * ps [:,0] + M [1][1] * ps [:,1] + M [1][2]) / r
      return ps

    assert self.transform_factors, "No transforming information"

    im = image_format.ensure_readable_image (self.img_path)
    M = np.array (self.transform_factors [:9]).reshape ((3, 3))
    dest_size = self.transform_factors [9:11]
    resize_for_analyzsis = self.transform_factors [11:13]
    scale = np.array ([resize_for_analyzsis [0] / dest_size [0], resize_for_analyzsis [1] / dest_size [1]])

    ratio = height / resize_for_analyzsis [1]
    if width == 'AUTO':
      ratio = (ratio, ratio)
    else:
      ratio = (width / resize_for_analyzsis [0], ratio)
    resize = (np.array (resize_for_analyzsis) * ratio).astype (int).tolist ()

    warped = cv2.warpPerspective (im, M, dest_size, flags = cv2.INTER_LINEAR)
    warped = cv2.resize (warped, resize, interpolation = cv2.INTER_CUBIC)

    if not plot:
      return warped

    for it in self:
      this = it.copy ()
      this ['points'] = np.array (translate (M, np.array (it ['points'])) * scale * ratio).astype (int)
      self.draw (warped, this, show_label = show_label)

    return warped
