from openai import OpenAI
from progress.bar import IncrementalBar
import os
import time

# os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=f'{os.getenv("API_KEY")}',
)
# DeepSeek预设
system_prompt = ""
with open('.github/workflows/AutoTransform/system_prompt.txt', 'r', encoding='utf-8') as f:
  system_prompt = f.read()

class Transform:
  def __init__(self, src, dst, name):
    self.src = src
    self.dst = dst
    self.name = name

input_dir='./dishes'
output_dir='./dishes/json_format'

total=0
success_count=0
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
        transforms.append(Transform(full_path, dst_path, file_name))
    else:
      traverse_folder(full_path)

# Markdown格式菜谱转换为JSON格式
def format(transform):
  src=transform.src
  dst=transform.dst

  if os.path.isfile(dst) :
    print(f'文件已转换: {dst}')
    return 1

  if not os.path.isfile(src) :
    print(f'未找到源文件: {src}')
    return 0

  user_prompt = ""
  with open(src, 'r', encoding='utf-8') as f:
    user_prompt = f.read()

  response = client.chat.completions.create(
    extra_body = {},
    model = "deepseek/deepseek-chat-v3-0324:free",
    messages = [
      { "role": "system", "content": system_prompt },
      { "role": "user", "content": user_prompt }
    ],
    response_format = {
      'type': 'json_object'
    }
  )

  # 请求失败
  if not response.choices:
    print('请求异常')
    return 0

  json_output = response.choices[0].message.content
  if len(json_output) == 0:
    print(f'输出结果为空，原因: {response.choices[0].finish_reason}')
    return 0
  
  # 输出结果转为json文件
  json_start=json_output.find('```json\n')
  if json_start != -1:
    json_output=json_output[json_start+8:]
  if json_output.endswith('\n```') :
    json_output=json_output[:-4]

  # 创建对应文件夹
  target_dir=dst[:-len(transform.name)]
  if not os.path.exists(target_dir):
    print(f'创建文件夹：{target_dir}')
    os.makedirs(target_dir)
    
  with open(dst, "w", encoding='utf-8') as file:
    file.write(json_output)
  # print(json_output)

  return 1


def main():
  if not os.path.exists(input_dir) :
    print(f'::error::未找到{input_dir}')
    exit(1)
  
  if not os.path.exists(output_dir) :
    print(f'创建{output_dir}')
    os.makedirs(output_dir)

  traverse_folder(input_dir)
  total=len(transforms)
  success_count=0
  error_count=0
  print(f'共计：{total}')

  bar = IncrementalBar('Countdown', max=total)

  for transform in transforms:
    start_time = time.time()
    print(f'开始转换 {transform.name}')
    result = format(transform)
    if result == 1:
      success_count += 1
    if result == 0:
      error_count += 1
    time.sleep(1)
    print(f'转换结束: {transform.name}, 耗时: {int(time.time() - start_time)}s')
    print(f'成功：{success_count}，失败：{error_count}')
    bar.next()
    print()
    break

  bar.finish()

main()
