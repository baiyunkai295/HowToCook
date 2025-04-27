from openai import OpenAI
import os
import time

class Transform:
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst
    

input_dir='./dishes'
output_dir='./dishes/json_format'

total=0
current_index=0
error_count=0
transforms=[]

# 遍历子文件夹
def traverse_folder(path):
  start=len(input_dir)
  for file_name in os.listdir(path):
    full_path = os.path.join(path, file_name)
    if os.path.isfile(full_path):
      # 处理文件
      dst_path=f'{output_dir}/{full_path[start:-3]}.json'
      if full_path.endswith('.md') and not os.path.exists(dst_path):
        transforms.append(Transform(full_path, dst_path))
    else:
      traverse_folder(full_path)


def main():
  if not os.path.exists(input_dir) :
    print(f'::error::未找到{input_dir}')
    exit(1)
  
  if not os.path.exists(output_dir) :
    print(f'创建{output_dir}')
    os.makedirs(output_dir)

  traverse_folder(input_dir)
  total=len(transforms)
  current_index=0
  error_count=0
  print(f'共计：{total}')

#   for transform in transforms:

main()
