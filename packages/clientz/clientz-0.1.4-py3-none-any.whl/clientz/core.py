""" core 需要修改"""
import re
import os
import importlib.resources
from typing import Dict, Any
import yaml
from llmada import BianXieAdapter
from querypipz.director import BuilderFactory,BuilderType,Director
director = Director(BuilderFactory(BuilderType.HistoryMemoryBuilder))

def load_config():
    """ load config """
    with importlib.resources.open_text('clientz', 'config.yaml') as f:
        return yaml.safe_load(f)

def format_node_for_chat(node_data: Dict[str, Any]) -> str:
    """
    解析节点数据，生成适合聊天窗口显示的格式化字符串。

    Args:
        node_data: 包含节点信息的字典结构。

    Returns:
        一个格式化的字符串，包含分数和节点文本内容。
        如果结构异常，返回错误提示。
    """
    node = node_data.get('node')
    score = node_data.get('score')

    if not node:
        return "Error: Could not find 'node' information."

    text_content = node.get('text')
    if not text_content:
        return "Error: 'text' content not found in node."

    # 移除 text 开头的 "topic:  content: \n\n\n" 或类似的元数据前缀
    # 根据你提供的样本，可能是固定的前缀，或者需要更灵活的处理
    # 这里简单移除已知的开头
    prefix_to_remove = "topic:  content: \n\n\n"
    if text_content.startswith(prefix_to_remove):
        text_content = text_content[len(prefix_to_remove):].strip()
    else:
        text_content = text_content.strip() # 或者只移除首尾空白

    # 构建输出字符串
    output = ""
    if score is not None:
        # 格式化分数，例如保留两位小数
        output += f"**Relevant Information (Score: {score:.2f})**:\n\n"
    else:
        output += "**Relevant Information:**\n\n"

    # 直接添加处理后的文本内容
    # 假设聊天窗口支持 Markdown，会渲染 #, ##, **, -, []() 等
    output += text_content

    # 你可以进一步处理 links，例如将它们提取出来单独列在末尾
    # link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # links_found = link_pattern.findall(text_content)
    # if links_found:
    #     output += "\n\n---\n*Links mentioned:*\n"
    #     for link_text, link_url in links_found:
    #         output += f"- [{link_text}]({link_url})\n" # 或其他格式

    return output

def extract_last_user_input(dialogue_text):
    """
    从多轮对话文本中提取最后一个 user 的输入内容。

    Args:
        dialogue_text: 包含多轮对话的字符串。

    Returns:
        最后一个 user 的输入内容字符串，如果未找到则返回 None。
    """
    # 修正后的正则表达式
    # (?s) 标志：使 . 匹配换行符
    # .* 匹配任意字符，直到最后一个 user:
    # user:\s* 匹配 "user:" 后面的零个或多个空白字符
    # (.*?) 非贪婪匹配任意字符，直到下一个 user: 或字符串末尾
    # (?=user:|$) 正向先行断言：断言后面是 "user:" 或者字符串末尾
    pattern = r"(?s).*user:\s*(.*?)(?=user:|$)"

    match = re.search(pattern, dialogue_text)

    if match:
        # group(1) 捕获的是最后一个 user: 到下一个 user: 或字符串末尾的内容
        return match.group(1).strip()
    else:
        return None

class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.dicts = load_config()
        self.query_persist_dir = self.dicts.get('query_persist_dir')
        self.model_pool = self.dicts.get("ModelCards")
        self.file_path = 'clientz/config.yaml'
        self._last_modified_time = None
        self._update_last_modified_time()

    def _update_last_modified_time(self):
        """更新存储的最后修改时间"""
        try:
            self._last_modified_time = os.path.getmtime(self.file_path)
        except FileNotFoundError:
            self._last_modified_time = None # 文件不存在时设为None

    def check_and_trigger(self):
        """检查文件是否变化，如果变化则触发动作"""
        try:
            current_modified_time = os.path.getmtime(self.file_path)
            if current_modified_time != self._last_modified_time:
                print(f"文件 '{self.file_path}' 已发生变化。")
                self._trigger_action()
                self._last_modified_time = current_modified_time # 更新存储的时间
            else:
                print(f"文件 '{self.file_path}' 未发生变化。")
        except FileNotFoundError:
            print(f"文件 '{self.file_path}' 不存在。")
            self._last_modified_time = None # 文件不存在时重置状态
        except Exception as e:
            print(f"检查文件时发生错误: {e}")

    def _trigger_action(self):
        """当文件发生变化时触发的动作"""
        # 可以修改
        # 这里可以放置你想要执行的具体动作，例如：
        # - 读取文件内容
        # - 处理文件数据
        # - 调用其他函数
        print("触发预定动作...")
        # 示例：读取文件内容并打印
        try:
            self.dicts = load_config()

        except FileNotFoundError:
            print(f"触发动作时文件 '{self.file_path}' 不存在。")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def product(self,prompt_with_history: str, model: str) -> str:
        """ x """
        return ''

    def stream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        self.check_and_trigger()
        if model[4:] in self.model_pool:
            self.bx.set_model(model[4:])
            for word in self.bx.product_stream(prompt_with_history):
                yield word
        elif model == "config_info":
            yield f"query_dir: {self.query_persist_dir}, dicts {str(self.dicts)}"

        elif model == 'retriver_v1':
            pass

        elif model == 'chat_with_long_memory':
            # V1
            # 单纯的向量库的管理方式
            self.bx.set_model("gemini-2.5-flash-preview-04-17-nothinking")
            query = director.construct()
            prompt_no_history = extract_last_user_input(prompt_with_history)
            print('prompt_no_history->',prompt_no_history)
            print('############# prompt_no_history START #############')
            print(prompt_no_history)
            print('############# prompt_no_history END #############')


            if prompt_with_history == "->上传":
                print('上传')
                # 上传 (update)
                query.update('\n'.join(chat_history))

            relevant_memories = query.retrieve(prompt_no_history)
            memories_str = '\n'.join([i.text for i in relevant_memories])
            print('############# RETRIVER START #############')
            print(memories_str)
            print('############# RETRIVER END #############')
            our_messages = [{"role": "user", "content": prompt_no_history}]
            # prompt_with_history
            # prompt_no_history

            prompt = f"""
这是我们之前的聊天历史 你可以试做长期记忆, 里面的信息作为参考:

{memories_str}

---

{prompt_with_history}

"""
            # prompt_with_history = f"用户长期记忆: {memories_str}" + prompt_with_history

            assistant_info = ''
            for word in self.bx.product_stream(prompt):

                yield word
                assistant_info += word

            our_messages.append({"role": "assistant", "content": assistant_info})
            inbound_information = '\n'.join([f"{i['role']}:{i['content']}" for i in our_messages])
            print('############# Inbound START #############')
            print(inbound_information)
            print('############# Inbound END #############')
            query.update(inbound_information)

        elif model == 'chat_with_long_memory_v2_computer_mode':
            # V1
            # 单纯的向量库的管理方式
            # 电脑 内存就是对应chat_history
            # 硬盘 + 内置硬盘 其实就是 大模型潜意识与知识库维度
            # 还要再加一些 寄存器的方式
            self.bx.set_model("gemini-2.5-flash-preview-04-17-nothinking")
            query = director.construct()
            if len(prompt_with_history.split('\n')) == 1:
                query.retriever = None
            prompt_no_history = extract_last_user_input(prompt_with_history)
            print('prompt_no_history->',prompt_no_history)
            print('############# prompt_no_history START #############')
            print(prompt_no_history)
            print('############# prompt_no_history END #############')


            if prompt_no_history == "->上传":
                print('上传')
                # 上传 (update)
                query.update('\n'.join(prompt_with_history))

            relevant_memories = query.retrieve_search(prompt_no_history)
            memories_str = '\n'.join([i.text for i in relevant_memories])
            print('############# RETRIVER START #############')
            print(memories_str)
            print('############# RETRIVER END #############')
            our_messages = [{"role": "user", "content": prompt_no_history}]
            # prompt_with_history
            # prompt_no_history
            # prompt_with_history = f"用户长期记忆: {memories_str}" + prompt_with_history

            system_prompt = ""
            prompt = system_prompt +"\n"+ memories_str +"\n"+prompt_with_history

            assistant_info = ''
            for word in self.bx.product_stream(prompt):
                yield word
                assistant_info += word

            our_messages.append({"role": "assistant", "content": assistant_info})
            inbound_information = '\n'.join([f"{i['role']}:{i['content']}" for i in our_messages])
            print('############# Inbound START #############')
            print(inbound_information)
            print('############# Inbound END #############')
            query.update(inbound_information)
        else:
            yield 'pass'
