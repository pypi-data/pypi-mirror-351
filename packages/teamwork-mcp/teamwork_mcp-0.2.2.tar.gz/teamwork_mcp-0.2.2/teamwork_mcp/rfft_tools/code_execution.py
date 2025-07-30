from pydantic import BaseModel, Field
from teamwork_mcp.base_tool import BaseTool, cache_to_file

class CodeExecutionTool(BaseTool):
    # 工具名称和介绍
    tool_name: str = Field("CodeExecutionTool", description="用于执行Python代码的工具，可以返回执行结果、打印结果和错误Traceback。调用时必须使用loguru打印信息。")
    
    # 参数
    code: str = Field("", description="要执行的Python代码")

    # 调用
    @staticmethod
    def __call__(tool_name_and_param: "CodeExecutionTool") -> str:
        def execute_code(code: str) -> str:
            from camel.toolkits.code_execution import CodeExecutionToolkit
            toolkit = CodeExecutionToolkit(
                sandbox="subprocess",
                verbose=True,
                require_confirm=False,
            )
            return toolkit.execute_code(code)

        return execute_code(code=tool_name_and_param.code)

