import unittest
import numpy as np
import cv2
from v39_progressive_drawing import (
 PHASES,DURATION,frame_at,stage_at,validate_story,make_draw_map,
 title_mask,base_without_title,derive_pencil
)
class V39Tests(unittest.TestCase):
 def setUp(self):
  # Synthetic input in memory only: never export an image or frame.
  self.im=np.full((720,720,3),220,np.uint8)
  cv2.rectangle(self.im,(120,245),(500,600),(50,70,80),3)
  cv2.line(self.im,(180,700),(320,390),(50,70,80),3)
  cv2.line(self.im,(550,700),(320,390),(50,70,80),3)
  cv2.line(self.im,(510,70),(670,70),(35,40,50),4)
  self.clean=base_without_title(self.im)
  self.edges=derive_pencil(self.im)
  self.order=make_draw_map(self.im.shape)
 def frame(self,t):
  return frame_at(t,self.im,self.clean,self.edges,self.order)
 def test_story_connected(self):self.assertEqual(validate_story(),[])
 def test_blank_is_paper(self):
  f=self.frame(0)
  self.assertTrue(np.all(f==np.array([231,238,241],np.uint8)))
 def test_pause_is_actual_static_hold(self):
  self.assertTrue(np.array_equal(self.frame(115),self.frame(135)))
 def test_title_hidden_until_last_phase(self):
  self.assertEqual(stage_at(193),"full_jacket")
  self.assertEqual(stage_at(195),"title")
  self.assertGreater(int(title_mask(self.im).sum()),0)
 def test_final_uses_actual_original_title(self):
  early=self.frame(193.99)
  final=self.frame(DURATION)
  m=title_mask(self.im)>0
  self.assertGreater(float(np.mean(abs(final[m].astype(float)-early[m].astype(float)))),1)
 def test_temporal_progress_has_strokes(self):
  a=self.frame(16)
  b=self.frame(95)
  self.assertGreater(float(np.mean(np.abs(a.astype(float)-b.astype(float)))),.15)
 def test_unique_phases(self):
  self.assertEqual(len({x[0] for x in PHASES}),len(PHASES))
if __name__=="__main__":unittest.main()
