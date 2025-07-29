import os
import re
from kevin_toolbox.data_flow.file import json_


class Env_Vars_Parser:
    """
        解释并替换字符串中${}形式指定的环境变量
            支持以下几种方式：
            - "${HOME}"                 家目录
            - "${SYS:<var_name>}"       其他系统环境变量
                                            在 linux 系统可以通过 env 命令来打印当前的环境变量，比如家目录也可以使用 ${SYS:HOME} 来表示
            - "${KVT_XXX<ndl_name>}"   读取配置文件 ~/.kvt_cfg/.xxx.json 中的变量（xxx将被自动转为小写）
                                            配置文件要求是 ndl 结构，比如当配置文件 ~/.kvt_cfg/.ndl.json 中保存的值为：
                                                {"dataset_dir":["~/data", "~/dataset"], ...}
                                            时，如果要指定使用 dataset_dir 下第二个路径，那么可以使用 ${KVT_NDL:dataset_dir@1} 来表示
            - "${/xxx.../xxx.json<ndl_name>}"  读取指定路径下的配置文件 /xxx.../xxx.json 中的变量
    """

    def __init__(self, home_dir=None):
        self.cfg_s = dict(
            SYS=dict(os.environ),
            HOME=home_dir if home_dir is not None else os.path.expanduser("~")
        )

    def __call__(self, *args, **kwargs):
        return self.parse(*args, **kwargs)

    def parse(self, text, **kwargs):
        """
            解释并替换

            参数：
                default:        默认之。
                                    当有设定时，若无法解释则返回该值。
                                    否则，若无法解释将报错。
        """
        if "default" in kwargs:
            try:
                return self.__parse(text=text)
            except:
                return kwargs["default"]
        else:
            return self.__parse(text=text)

    def __parse(self, text):
        temp_ls = []
        for it in self.split_string(text=text):
            if isinstance(it, str):
                temp_ls.append(it)
                continue
            root_node, method_ls, node_ls = it
            if root_node not in self.cfg_s:
                try:
                    if root_node.startswith("KVT_"):
                        t0, t1 = root_node.lower().split("_", 1)
                        root_node = os.path.expanduser(f'~/.{t0}_cfg/.{t1}.json')
                    assert os.path.isfile(root_node), f'file not exist: {root_node}'
                    cfg = json_.read(file_path=root_node, b_use_suggested_converter=True)
                    self.cfg_s[root_node] = cfg
                except Exception as e:
                    raise ValueError(f"invalid cfg_name: {root_node}, because: {e}")
            cfg = self.cfg_s.get(root_node, None)
            if cfg is None:
                raise ValueError(f"invalid cfg_name: {root_node}")
            #
            from kevin_toolbox.nested_dict_list import get_value
            temp_ls.append(get_value(var=cfg, name=it))

        return "".join([f'{i}' for i in temp_ls])

    @staticmethod
    def split_string(text):
        """
            将字符串中 ${<cfg_name>} 部分的内容分割出来
                比如对于 "666/123${SYS:HOME}/afasf/${/xxx.../xxx.json:111:222}336"
                应该分割为 ["666/123", ("SYS:HOME", ), "/afasf/", ("/xxx.../xxx.json:111:222", ), "336"]
                然后再对其中 tuple 部分使用 ndl.name_handler.parse_name 进行解释
        """
        from kevin_toolbox.nested_dict_list.name_handler import parse_name
        pattern = r'\$\{([^}]+)\}'
        matches = re.finditer(pattern, text)

        result = []
        last_end = 0

        for match in matches:
            start = match.start()
            if start > last_end:
                result.append(text[last_end:start])
            result.append(parse_name(name=match.group(1)))
            last_end = match.end()

        if last_end < len(text):
            result.append(text[last_end:])

        return result


if __name__ == '__main__':
    env_vars_parser = Env_Vars_Parser()
    # print(env_vars_parser.split_string("666/123${:VAR}/afasf/${/xxx.../xxx.json:111:222}336"))
    print(env_vars_parser.parse("${KVT_PATCHES:for_matplotlib:common_charts:font_settings:for_non-windows-platform}"))
