from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator, root_validator


class MCPServerConfig(BaseModel):
    """MCP服务器配置"""
    autoApprove: List[str] = Field(default_factory=list, description="自动批准的工具列表")
    disabled: bool = Field(default=False, description="是否禁用服务器")
    timeout: int = Field(default=60, description="超时时间（秒）")
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list, description="服务器启动参数")
    transportType: str = Field(default="stdio", description="传输类型")
    url: Optional[str] = Field(None, description="SSE服务器URL")
    type: Optional[str] = Field(None, description="服务器类型，会自动转换为transportType")

    @root_validator(pre=False, skip_on_failure=True)
    def normalize_config(cls, values):
        """规范化配置，处理type字段转换和字段验证"""
        # 处理type字段转换
        if 'type' in values and values['type']:
            type_value = values['type'].lower()
            if type_value == 'sse':
                values['transportType'] = 'sse'
            elif type_value == 'stdio':
                values['transportType'] = 'stdio'
        
        # 如果没有明确的transportType，根据配置推断
        if not values.get('transportType') or values.get('transportType') == 'stdio':
            if values.get('url'):
                values['transportType'] = 'sse'
            elif values.get('command'):
                values['transportType'] = 'stdio'
        
        # 验证必需字段
        transport_type = values.get('transportType', 'stdio')
        if transport_type == 'sse' and not values.get('url'):
            raise ValueError('SSE传输类型必须提供url字段')
        if transport_type == 'stdio' and not values.get('command'):
            raise ValueError('stdio传输类型必须提供command字段')
        
        return values

    def dict(self, **kwargs):
        """重写dict方法，根据传输类型过滤字段"""
        data = super().dict(**kwargs)
        
        transport_type = data.get('transportType', 'stdio')
        
        # 移除type字段
        if 'type' in data:
            del data['type']
        
        # 根据传输类型过滤字段
        if transport_type == 'sse':
            # SSE传输类型不需要command和args
            if 'command' in data:
                del data['command']
            if 'args' in data:
                del data['args']
        elif transport_type == 'stdio':
            # stdio传输类型不需要url
            if 'url' in data:
                del data['url']
        
        return data

    class Config:
        extra = "allow"


# 其余的类保持你原有的写法不变
class MCPConfig(BaseModel):
    """MCP配置"""
    mcpServers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict,
        description="MCP服务器配置，键为服务器名称"
    )


class ModelConfig(BaseModel):
    """模型配置"""
    name: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API基础URL")
    api_key: str = Field(..., description="API密钥")
    model: str = Field(..., description="模型标识符")

    @validator('name')
    def name_must_be_unique(cls, v, values, **kwargs):
        return v

    class Config:
        extra = "allow"


class ModelConfigList(BaseModel):
    """模型配置列表"""
    models: List[ModelConfig] = Field(default_factory=list)

class AgentNode(BaseModel):
    """Agent节点配置"""
    name: str = Field(..., description="节点名称")
    description: Optional[str] = Field(default="", description="节点描述，用于工具选择提示")
    model_name: Optional[str] = Field(default=None, description="使用的模型名称")
    mcp_servers: List[str] = Field(default_factory=list, description="使用的MCP服务器名称列表")
    system_prompt: str = Field(default="", description="系统提示词")
    user_prompt: str = Field(default="", description="用户提示词")
    input_nodes: List[str] = Field(default_factory=list, description="输入节点列表")
    output_nodes: List[str] = Field(default_factory=list, description="输出节点列表")
    handoffs: Optional[int] = Field(default=None, description="节点可以执行的选择次数，用于支持循环流程")
    global_output: bool = Field(default=False, description="是否全局管理此节点的输出")
    context: List[str] = Field(default_factory=list, description="需要引用的全局管理节点列表")
    context_mode: str = Field(default="all", description="全局内容获取模式，可选值：all, latest, latest_n")
    context_n: int = Field(default=1, description="获取最新的n次输出，当context_mode为latest_n时有效")
    is_start: bool = Field(default=False, description="是否为起始节点")
    is_end: bool = Field(default=False, description="是否为结束节点")
    output_enabled: bool = Field(default=True, description="是否输出回复")
    is_subgraph: bool = Field(default=False, description="是否为子图节点")
    subgraph_name: Optional[str] = Field(default=None, description="子图名称")
    position: Optional[Dict[str, float]] = Field(default=None, description="节点在画布中的位置")
    level: Optional[int] = Field(default=None, description="节点在图中的层级，用于确定执行顺序")
    save: Optional[str] = Field(default=None, description="输出保存的文件扩展名，如md、html、py、txt等")

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or '/' in v or '\\' in v or '.' in v:
            raise ValueError('名称不能包含特殊字符 (/, \\, .)')
        return v

    @validator('model_name')
    def validate_model_name(cls, v, values):
        is_subgraph = values.get('is_subgraph', False)
        if not is_subgraph and not v and values.get('name'):
            raise ValueError(f"普通节点 '{values['name']}' 必须指定模型名称")
        return v

    @validator('subgraph_name')
    def validate_subgraph_name(cls, v, values):
        if values.get('is_subgraph', False) and not v and values.get('name'):
            raise ValueError(f"子图节点 '{values['name']}' 必须指定子图名称")
        return v

    @validator('level')
    def validate_level(cls, v):
        if v is None:
            return None  # 允许为None，由后端计算
        try:
            return int(v)  # 尝试将其转换为整数
        except (ValueError, TypeError):
            return None  # 如果转换失败，返回None

    @validator('save')
    def validate_save(cls, v):
        if v is None:
            return None
        v = v.strip().lower()
        # 可以添加扩展名验证逻辑
        if v and not v.isalnum():
            # 简单验证，确保只包含字母数字
            v = ''.join(c for c in v if c.isalnum())
        return v


class GraphConfig(BaseModel):
    """图配置"""
    name: str = Field(..., description="图名称")
    description: str = Field(default="", description="图描述")
    nodes: List[AgentNode] = Field(default_factory=list, description="节点列表")
    end_template: Optional[str] = Field(default=None, description="终止节点输出模板，支持{node_name}格式的占位符引用其他节点的输出")

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or '/' in v or '\\' in v or '.' in v:
            raise ValueError('名称不能包含特殊字符 (/, \\, .)')
        return v


class GraphInput(BaseModel):
    """图执行输入"""
    graph_name: Optional[str] = Field(None, description="图名称")
    input_text: Optional[str] = Field(None, description="输入文本")
    conversation_id: Optional[str] = Field(None, description="会话ID，用于继续现有会话")
    parallel: bool = Field(default=False, description="是否启用并行执行")
    continue_from_checkpoint: bool = Field(default=False, description="是否从断点继续执行")


class NodeResult(BaseModel):
    """节点执行结果"""
    node_name: str = Field(..., description="节点名称")
    input: str = Field(..., description="输入内容")
    output: str = Field(..., description="输出内容")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用")
    tool_results: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用结果")
    is_subgraph: Optional[bool] = Field(default=False, description="是否为子图节点")
    subgraph_name: Optional[str] = Field(default=None, description="子图名称")
    subgraph_conversation_id: Optional[str] = Field(default=None, description="子图会话ID")
    subgraph_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="子图执行结果")
    error: Optional[str] = Field(default=None, description="错误信息（如果有）")
    is_start_input: Optional[bool] = Field(default=None, description="是否为起始输入")


class GraphResult(BaseModel):
    """图执行结果"""
    graph_name: str = Field(..., description="图名称")
    conversation_id: str = Field(..., description="会话ID")
    input: str = Field(..., description="输入内容")
    output: str = Field(..., description="最终输出内容")
    node_results: List[NodeResult] = Field(default_factory=list, description="节点执行结果")
    completed: bool = Field(default=False, description="是否完成执行")
    error: Optional[str] = Field(default=None, description="错误信息（如果有）")