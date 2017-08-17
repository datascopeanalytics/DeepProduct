import os
import shutil
import PIL
from PIL import Image, ImageDraw

'''
This script takes every possible image in the all_pairs.txt file, and 
writes a "bounding box" copy of that photo in the same directory.

That way, all ~8,300 potential images that would ever show up on dope
or nope and their bounding box copies are present in the same directory
for the web application to grab.

If we ever do any type of re-cropping of these photos for aesthetic
purposes, this is the script that can be modified and re-ran. 
'''

def get_bbox_coords(txt_file_path, bbox_lines):
        img_row = [v for v in bbox_lines if v[0] == txt_file_path]
        if not img_row:
                return None
        coords = img_row[0][1:]
        return [int(v) for v in coords]

def make_bbox_image(txt_file_path, bbox_coords, root_dir):
        in_img = os.path.join(root_dir, txt_file_path)
        base = PIL.Image.open(in_img).convert('RGBA')
        rect = PIL.Image.new('RGBA', base.size, (255,255,255,0))
        d = ImageDraw.Draw(base)
        lower_corner = tuple(bbox_coords[:2])
        upper_corner = tuple(bbox_coords[2:])
        d.rectangle((lower_corner, upper_corner), outline = 'red')
        return PIL.Image.alpha_composite(base, rect)

if __name__ == '__main__':
        SYMLINK_ROOT = 'static/to_dropbox/DeepFashion'
        PAIRS_FILE =  'all_pairs.txt'
        BBOX_FILE = os.path.join(SYMLINK_ROOT, 'list_bbox.txt')

        with open(PAIRS_FILE,'r') as f:
                pairs_lines = f.readlines()

        with open(BBOX_FILE,'r') as f:
                bbox_lines_raw = f.readlines()
                bbox_lines = [v.split() for v in bbox_lines_raw]
        
        i = 0
        for line in pairs_lines:
                imgs = line.split()[1:]
                for img in imgs:
                        i += 1
                        coordinates = get_bbox_coords(img, bbox_lines)
                        new_image = make_bbox_image(img, coordinates, SYMLINK_ROOT)
                        if os.path.exists(os.path.join(SYMLINK_ROOT,img)):
                                full_path = os.path.join(SYMLINK_ROOT,img)
                                fname, fext = os.path.splitext(full_path)
                                new_path =  '{}_bbox.png'.format(fname)
                                new_image.save(new_path)
                                print('Image Number: {}'.format(i+1))
                                print('Original Location: {}'.format(full_path))
                                print('Writing Bbox Version to: {}'.format(new_path)) 