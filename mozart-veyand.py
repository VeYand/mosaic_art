'''
Copyright 2022 VeYand inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import os
import random
import shutil
import time
import glob

from art import tprint
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
def resize(cols=100, rows=100, img_weight=100, img_height=100, max_image_count=5000):
    cur_x, cur_y = int(img_weight/cols), int(img_height/rows)
    files = os.listdir('input')
    random.shuffle(files)
    if len(files)>max_image_count:
        files = files[:max_image_count]
    for file in files:
        img = Image.open(f'input/{file}')
        x, y = img.size
        if x<cur_x or y<cur_y:
            k = int(max(cur_x/x, cur_y/y))
            img = img.resize((x*k, y*k))
            x, y = img.size
        k = min(x/cur_x, y/cur_y)
        x, y = int(x/k*1.05), int(y/k*1.05)
        img = img.resize((x, y))
        new_image = img.crop(((x-cur_x)//2,
                              (y - cur_y)//2,
                              (x + cur_x)//2,
                              (y + cur_y)//2
        ))
        new_image = new_image.resize((cur_x, cur_y))
        new_image.save(f'.output/{file}')


def avarage(picture_name):
    img = Image.open(picture_name)
    obj_for_count = img.load()

    with open(picture_name, "rb") as f:
        img_for_size = Image.open(f)
        sq = [0, 0, 0]
        count = img_for_size.size[0] * img_for_size.size[1]
        width = img_for_size.size[0]
        height = img_for_size.size[1]

    for i in range(width):
        for j in range(height):
            sq[0] += obj_for_count[i, j][0]
            sq[1] += obj_for_count[i, j][1]
            sq[2] += obj_for_count[i, j][2]

    rgb = list(map(int, [sq[0] / count, sq[1] / count, sq[2] / count]))
    img.close()
    return rgb

def avarage_dir(file_path = '.output'):
    input_images = {}
    for item in os.listdir(file_path):
        try: input_images[item] = [avarage(f'{file_path}\\{item}'), 0]
        except Exception as ex: pass
    return input_images
def comparsion(input_images, current_color, frequency):
    comp = {}
    rgb_1 = current_color

    for key in input_images:
        refresh = input_images[key]
        if input_images[key][1]>0:
            input_images[key] = [refresh[0], refresh[1] - 1]
            continue
        rgb_2 = input_images[key][0]
        delta = ((rgb_1[0]-rgb_2[0])**2 + (rgb_1[1]-rgb_2[1])**2 + (rgb_1[2]-rgb_2[2])**2)
        comp[key] = delta
    photo = min(comp, key=comp.get)
    refresh = input_images[photo]
    input_images[photo] = [refresh[0], random.randint(frequency[0], frequency[1])]
    return (input_images, photo)
def gluing(file='', cols=100, rows=100, new_x = 100, new_y = 100, input_images={}, frequency=(100, 300)):
    img = Image.open(file)
    img = img.resize((cols, rows))
    pixels = img.load()

    mask_im = Image.new('RGB', (new_x, new_y), 'white')

    offset_x_glob = new_x / cols
    offset_y_glob = new_y / rows
    y_goast = -offset_y_glob
    old_print = -1
    for y in range(0, rows):
        y_goast+=offset_y_glob
        y_goast-=1
        offset_y = int(y_goast)
        x_goast = 0
        offset_x = 0
        if int(y/cols*100)!=old_print:
            print(f'\r[INFO] Gluing an image... {int(y/cols*100)} % ', end='')
            old_print = int(y/cols)
        for x in range(0, cols):
            color_cur = pixels[x, y]
            try:
                input_images, file = comparsion(input_images, color_cur, frequency)
                file = f'.output\\{file}'
                im = Image.open(file)
                mask_im.paste(im, (offset_x, offset_y))
            except Exception: pass

            x_goast+=offset_x_glob
            x_goast-=1

            offset_x=int(x_goast)
    mask_im = mask_im.crop((0, 0, new_x-cols, new_y-rows))
    print(f'\r[INFO] Gluing an image... 100 % ', end='')
    mask_im.save(f'result.jpg')

def clear():
    clear_list = ['.output']
    for item in clear_list:
        try:
            os.remove(item)
        except:
            try:
                shutil.rmtree(item)
            except:
                pass

def many2one(quality=1, rows=100, cols=100, file='', frequency=(100, 300), max_image_count=5000):
    try:
        print('[INFO] Clearing...', end='')
        clear()
        for dir in ['enter', 'input', '.output', 'result']:
            if not os.path.isdir(dir): os.mkdir(dir)
        img = Image.open(file)
        x, y = img.size

        while x*y<quality:
            x, y = x*1.01, y*1.01
        x, y = int(x), int(y)

        start_time = time.time()
        print(f'\r[INFO] Preparing source images... ', end='')
        resize(cols=cols, rows=rows, img_weight=x, img_height=y, max_image_count=max_image_count)
        time_2 = time.time()
        print(f'[{int(time_2 - start_time)} s.]')
        print('[INFO] Reading source images... ', end='')
        input_images = avarage_dir()
        time_3 = time.time()
        print(f'[{int(time_3 - time_2)} s.]')
        print('[INFO] Gluing an image...', end='')
        gluing(file=file, cols=cols, rows=rows, new_x = x, new_y = y, input_images=input_images, frequency=frequency)
        time_4 = time.time()
        print(f'[{int(time_4-time_3)} s.]')
        print(f'\r[INFO] Image creation completed successfully in {int(time_4-start_time)} seconds!')
    except Exception as ex: print(f'\n{ex}')


def main():
    tprint('MozArt - VeYand', font='tarty1')
    print('Upload the input images to the "/enter" folder (press Enter to continue)')
    input()

    #Parametrs
    quality = 20000*20000 #(widght*height)
    rows = 100
    cols = 100
    frequency = (1000, 3000)#the minimum and maximum number of substitutions that do not have the same image
    max_image_count = 10000# maximum number of images used

    images = glob.glob('enter/*.jpg') + glob.glob('enter/*.jpeg') + glob.glob('enter/*.png')
    for image in images:
        print(f'{image} in processing...')
        many2one(quality=quality, rows=rows, cols=cols, file=image, frequency=frequency, max_image_count=max_image_count)
        i = 0
        while os.path.isdir(f'result/result_{i}'):
            i+=1
        os.mkdir(f'result/result_{i}')
        shutil.move(image, f'result/result_{i}/original.{image.split(".")[-1]}')
        shutil.move('result.jpg', f'result/result_{i}/result.jpg')
        print('[INFO] Clearing... ')
        clear()
        print()

if __name__ == '__main__':
    main()