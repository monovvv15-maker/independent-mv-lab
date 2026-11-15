import unittest
import numpy as np
import cv2
from v39_progressive_drawing import base_without_title,derive_pencil,make_draw_map,DURATION
from v41_redraw_engine import action_state,frame_at,quality_gate

class V41Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  im=np.full((720,720,3),220,np.uint8)
  cv2.line(im,(180,699),(310,389),(75,76,78),3)
  cv2.line(im,(590,699),(350,389),(75,76,78),3)
  cv2.line(im,(510,70),(665,70),(35,40,50),4)
  cls.im=im
  cls.clean=base_without_title(im)
  cls.pencil=derive_pencil(im)
  cls.order=make_draw_map(im.shape)
 def frame(self,t):
  return frame_at(t,self.im,clean=self.clean,pencil=self.pencil,order=self.order)
 def test_sequence_gate(self):self.assertEqual(quality_gate()["errors"],[])
 def test_blank(self):self.assertTrue(np.all(self.frame(0)==[231,238,241]))
 def test_eraser_reduces_incorrect_stroke(self):
  self.assertGreater(action_state(51)["wrong"],action_state(56)["wrong"])
  self.assertGreater(action_state(56)["ghost"],0)
 def test_redraw_after_erase(self):
  self.assertEqual(action_state(55)["corrected"],0)
  self.assertGreater(action_state(65)["corrected"],0)
 def test_pause_exact_pixel_hold(self):
  self.assertTrue(np.array_equal(self.frame(115),self.frame(135)))
 def test_single_mistake(self):
  self.assertEqual(action_state(35)["wrong"],0)
  self.assertGreater(action_state(49)["wrong"],0)
  self.assertEqual(action_state(90)["wrong"],0)
 def test_final_has_no_pencil_overlay(self):
  from v39_progressive_drawing import frame_at as original
  self.assertTrue(np.array_equal(self.frame(DURATION),
                 original(DURATION,self.im,self.clean,self.pencil,self.order)))
 def test_photo_restore_fades_ghost(self):
  self.assertGreater(action_state(165)["ghost"],action_state(185)["ghost"])
 def test_no_media_export(self):self.assertFalse(quality_gate()["video_generated"])
if __name__=="__main__":unittest.main()
