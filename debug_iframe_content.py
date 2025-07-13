#!/usr/bin/env python3
"""
调试iframe内容，检查是否有form、input等元素
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_iframe_content():
    """调试iframe内容"""
    print("开始调试iframe内容...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 测试URL
        test_url = "https://www.tutorialspoint.com/selenium/practice/nestedframes.php"

        try:
            print(f"正在访问页面: {test_url}")
            await page.goto(test_url)
            await page.wait_for_load_state('networkidle')

            # 检查页面标题
            title = await page.title()
            print(f"页面标题: {title}")

            # 检查iframe数量
            iframe_count = await page.evaluate("document.querySelectorAll('iframe').length")
            print(f"iframe元素数量: {iframe_count}")

            # 获取所有iframe的信息
            iframes_info = await page.evaluate("""
                () => {
                    const iframes = document.querySelectorAll('iframe');
                    return Array.from(iframes).map((iframe, index) => ({
                        index: index,
                        id: iframe.id,
                        name: iframe.name,
                        src: iframe.src,
                        width: iframe.width,
                        height: iframe.height
                    }));
                }
            """)

            print(f"\niframe元素详情:")
            for iframe in iframes_info:
                print(f"  iframe {iframe['index']+1}:")
                print(f"    ID: {iframe['id']}")
                print(f"    Name: {iframe['name']}")
                print(f"    Src: {iframe['src']}")
                print(f"    Size: {iframe['width']}x{iframe['height']}")
                print()

            # 尝试访问第一个iframe的内容
            if iframe_count > 0:
                print("尝试访问第一个iframe的内容...")

                # 等待iframe加载
                await page.wait_for_timeout(2000)

                # 获取iframe的frame对象
                frames = page.frames
                print(f"页面中的frames数量: {len(frames)}")

                for i, frame in enumerate(frames):
                    if i == 0:  # 跳过主frame
                        continue

                    print(f"\n检查frame {i}:")
                    try:
                        # 检查frame中的元素
                        form_count = await frame.evaluate("document.querySelectorAll('form').length")
                        input_count = await frame.evaluate("document.querySelectorAll('input').length")
                        button_count = await frame.evaluate("document.querySelectorAll('button').length")
                        a_count = await frame.evaluate("document.querySelectorAll('a').length")

                        print(f"  form元素数量: {form_count}")
                        print(f"  input元素数量: {input_count}")
                        print(f"  button元素数量: {button_count}")
                        print(f"  a元素数量: {a_count}")

                        # 获取frame中的form元素详情
                        if form_count > 0:
                            forms_info = await frame.evaluate("""
                                () => {
                                    const forms = document.querySelectorAll('form');
                                    return Array.from(forms).map(form => ({
                                        id: form.id,
                                        name: form.name,
                                        action: form.action,
                                        method: form.method
                                    }));
                                }
                            """)

                            print(f"  form元素详情:")
                            for j, form in enumerate(forms_info):
                                print(f"    Form {j+1}:")
                                print(f"      ID: {form['id']}")
                                print(f"      Name: {form['name']}")
                                print(f"      Action: {form['action']}")
                                print(f"      Method: {form['method']}")

                        # 获取frame中的input元素详情
                        if input_count > 0:
                            inputs_info = await frame.evaluate("""
                                () => {
                                    const inputs = document.querySelectorAll('input');
                                    return Array.from(inputs).map(input => ({
                                        id: input.id,
                                        name: input.name,
                                        type: input.type,
                                        value: input.value
                                    }));
                                }
                            """)

                            print(f"  input元素详情:")
                            for j, input_elem in enumerate(inputs_info):
                                print(f"    Input {j+1}:")
                                print(f"      ID: {input_elem['id']}")
                                print(f"      Name: {input_elem['name']}")
                                print(f"      Type: {input_elem['type']}")
                                print(f"      Value: {input_elem['value']}")

                    except Exception as e:
                        print(f"  访问frame {i}失败: {e}")

            # 等待用户查看
            print("\n页面已打开，请手动检查iframe内容...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"调试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_iframe_content())
