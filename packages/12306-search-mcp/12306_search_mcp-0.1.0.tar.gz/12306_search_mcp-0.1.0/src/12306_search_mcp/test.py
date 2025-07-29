import asyncio  
import json  
from mcp.client.session import ClientSession  
from mcp.client.stdio import stdio_client, StdioServerParameters  
  
async def test_train_ticket_client():  
    """测试火车票查询 MCP 服务的简单客户端"""  
      
    # 配置服务器参数  
    server_params = StdioServerParameters(  
        command="uv",  
        args=["run","server.py"],  
        env=None  
    )  
      
    try:  
        # 建立与服务器的连接  
        async with stdio_client(server_params) as (read_stream, write_stream):  
            async with ClientSession(read_stream, write_stream) as session:  
                print("正在初始化客户端会话...")  
                  
                # 初始化会话  
                init_result = await session.initialize()  
                print(f"服务器初始化成功: {init_result.serverInfo.name}")  
                  
                # 列出可用工具  
                print("\n获取可用工具...")  
                tools_result = await session.list_tools()  
                print(f"可用工具数量: {len(tools_result.tools)}")  
                for tool in tools_result.tools:  
                    print(f"- {tool.name}: {tool.description}")  
                  
                # 测试火车票查询工具  
                print("\n测试火车票查询...")  
                try:  
                    # 调用搜索火车票工具  
                    result = await session.call_tool(  
                        "search_tickets",  
                        {  
                            "date": "2025-06-04",  # 测试日期  
                            "from_city": "杭州",     # 出发城市  
                            "to_city": "北京"       # 到达城市  
                        }  
                    )  
                      
                    print("查询结果:")  
                    if result.content:  
                        for content in result.content:  
                            if hasattr(content, 'text'):  
                                # 解析并格式化 JSON 结果  
                                try:  
                                    data = json.loads(content.text)  
                                    print(f"找到 {len(data)} 趟列车:")  
                                    for i, train in enumerate(data[:5]):  # 只显示前5趟  
                                        print(f"  {i+1}. {train.get('station_train_code', 'N/A')} "  
                                              f"{train.get('start_time', 'N/A')}-{train.get('arrive_time', 'N/A')} "  
                                              f"({train.get('lishi', 'N/A')})")  
                                        # 显示部分座位信息  
                                        tickets = train.get('tickets', {})  
                                        if '二等座' in tickets:  
                                            seat_info = tickets['二等座']  
                                            # print(seat_info)
                                            print(f"     二等座: 余票{seat_info.get('num', 'N/A')} 价格¥{seat_info.get('price', 'N/A')}")  
                                except json.JSONDecodeError:  
                                    print(content.text)  
                            else:  
                                print(content)  
                      
                    if result.isError:  
                        print("查询过程中出现错误")  
                          
                except Exception as e:  
                    print(f"调用工具时出错: {e}")  
                  
    except Exception as e:  
        print(f"客户端连接失败: {e}")  
        print("请确保:")  
        print("1. 服务器脚本文件存在且可执行")  
        print("2. 服务器脚本中包含正确的 FastMCP 实现")  
        print("3. 所有依赖包已安装")  
  
def main():  
    """运行测试客户端"""  
    print("火车票查询 MCP 服务测试客户端")  
    print("=" * 50)  
    asyncio.run(test_train_ticket_client())  
  
if __name__ == "__main__":  
    main()