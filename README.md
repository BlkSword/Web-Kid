# Web-Kid

## 概述
Web-Kid 集成了一套面向 CTF 反序列化（pop 链）题目的 MCP 服务器与分析工具，支持 PHP 为主的链路审计、候选链生成、payload 构造与静态模拟。现已引入可选的 tree-sitter-php AST 解析以提升识别精度与数据流感知。

## 主要功能
- 代码审计：扫描类、魔术方法与危险调用，输出结构化报告。
- 链路发现：按触发类型与可达 sink 生成候选链，并排序。
- 约束校验：环境与配置提示（PHP 版本、autoload 等）。
- Payload 生成：输出 PHP `serialize()` 字符串与结构化描述。
- 静态模拟：模拟 `unserialize` 触发序列标注到达情况。
- 知识库检索：按框架或 Composer 包匹配常见 gadget 提示。

## 快速开始
- 作为库使用：
  - `from mcp_popchain.analyzer import analyze_php_repo`
  - `summary = analyze_php_repo("path/to/challenge", [])`
- 启动 MCP 服务器（stdio）：
  - `python -c "from mcp_popchain.server import run; run()"`
- 启动 MCP 服务器（streamable-http）：
  - `python -m mcp_popchain.app_http`

## MCP 工具
- `analyze_php_repo_tool(rootPath, includes=[])`
- `list_magic_methods_tool(summary)`
- `find_gadgets_tool(summary, targetSink)`
- `build_chain_tool(summary, sources, sink)`
- `generate_payload_tool(className, properties)`
- `simulate_unserialize_tool(spec)`
- `check_constraints_tool(env)`
- `kb_search_tool(keyword, version=None)`
- `kb_match_by_packages_tool(summary)`

## AST 解析
- 默认尝试使用 `tree-sitter-php`（通过 `tree_sitter_languages` 包）进行 AST 级解析与基础数据流识别；如未安装则自动回退到启发式静态扫描。
- 建议安装：
  - `pip install tree-sitter tree-sitter-languages`

## 示例测试
- 运行内置基础测试：
  - `python -c "import os,sys; sys.path.append(os.getcwd()); from tests.test_popchain import test_analyze, test_chain, test_payload; test_analyze(); test_chain(); test_payload(); print('OK')"`

## 注意事项
- 默认不执行用户代码或危险函数，分析以静态/半静态为主。
- 如需更真实验证，请在隔离环境下启用动态检查并严格限制权限。

## 接入方法（JSON）
- 将以下片段添加到 MCP 客户端配置（如 Claude Desktop 的 `claude_desktop_config.json`）中，用于以 `stdio` 方式接入本服务器：

```json
{
  "mcpServers": {
    "ctf-popchain": {
      "command": "python",
      "args": [
        "-c",
        "from mcp_popchain.server import run; run()"
      ]
    }
  }
}
```

- 直接以文件路径运行：

```json
{
  "mcpServers": {
    "ctf-popchain": {
      "command": "python",
      "args": [
        "d:/project/Web-Kid/mcp_popchain/server.py"
      ]
    }
  }
}
```

