#  这个文件是一个简单的测试程序，用于测试 Gradio 的功能
import gradio as gr
import sys

def echo(message):
    print(f"Echo function called with message: {message}", flush=True)
    sys.stdout.flush()
    return f"You said: {message}"

def chatbot(input_text):
    print(f"收到输入: {input_text}")
    try:
        # 模拟一些处理时间
        time.sleep(2)
        
        # 这里是你原来的chatbot逻辑
        # response = your_chatbot_logic(input_text)
        
        # 暂时用一个简单的回复来测试
        response = f"你说的是：{input_text}"
        
        print(f"生成的回复: {response}")
        return response
    except Exception as e:
        print(f"chatbot函数发生错误: {e}")
        return f"抱歉，处理您的请求时出现了错误：{str(e)}"

def launch_gradio():
    print("启动 Gradio")
    demo = gr.Interface(
        fn=echo,
        inputs="text",
        outputs="text",
        title="简单回声测试"
    )
    print("Gradio interface created, about to launch")
    demo.launch(server_name="127.0.0.1", share=True)
    print("Gradio interface launched")

if __name__ == "__main__":
    print("Starting test program")
    launch_gradio()
    print("Test program ended")