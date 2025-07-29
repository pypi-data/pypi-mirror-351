import subprocess

def ask_ollama(model_name, prompt):
    """
    调用本地Ollama运行指定的模型。
    
    参数:
        model_name (str): 用户指定的模型名称。
        prompt (str): 提供给模型的输入提示。
    
    返回:
        str: 模型的输出结果。
    """
    try:
        # 构造Ollama命令
        command = ["ollama", "run", model_name, prompt]
        
        # 执行命令并捕获输出，显式指定编码为 utf-8 并忽略无法解码的字符
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="ignore"  # 忽略无法解码的字符
        )
        
        # 返回模型的输出
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，返回错误信息
        return f"Error: {e.stderr}"
    
def AI_help():
    print("以下是可用的函数:")
    print("- ask_ollama(model_name, prompt): 调用本地Ollama运行指定的模型。")
    print("- AI_help(): 显示帮助信息。")