#!/usr/bin/env python3
"""
Test to ensure consistency of Robohash image generation.
This test checks that the output of the Robohash generator matches
expected reference images for specific inputs.
"""

import os
import unittest
from PIL import Image, ImageChops
import io
from robohash import Robohash

class TestRobohashConsistency(unittest.TestCase):
    def setUp(self):
        self.reference_dir = os.path.join(os.path.dirname(__file__), 'reference')

    def test_pi_image_consistency(self):
        """Test that '3.14159' generates the expected image."""
        # Load the reference image
        reference_path = os.path.join(self.reference_dir, 'pi.png')
        reference_img = Image.open(reference_path)

        # Generate a new image using the same input
        rh = Robohash("3.14159")
        rh.assemble(sizex=300, sizey=300)
        
        # Convert the generated image to bytes for comparison
        img_buffer = io.BytesIO()
        rh.img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        generated_img = Image.open(img_buffer)

        # Compare the images
        diff = ImageChops.difference(reference_img.convert('RGBA'), generated_img.convert('RGBA'))
        
        # If the images are the same, the difference will be all black (0)
        self.assertFalse(diff.getbbox(), "Generated image doesn't match the reference image")

if __name__ == '__main__':
    unittest.main()