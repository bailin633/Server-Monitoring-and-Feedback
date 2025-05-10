import openai

# 设置你的有效 API 密钥
openai.api_key = "sess-9HdVP8fM1P6MiWIzeb95BD86hLnq4Qv93igLH6oz"

# 测试调用
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好，帮我介绍一下OpenAI。"}
        ]
    )
    print("AI 回复：")
    print(response['choices'][0]['message']['content'])
except openai.error.AuthenticationError:
    print("认证失败，请检查 API 密钥。")
except openai.error.RateLimitError:
    print("请求太频繁，请稍后重试。")
except openai.error.OpenAIError as e:
    print(f"其他错误：{e}")
