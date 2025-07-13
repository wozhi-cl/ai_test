#!/usr/bin/env python3
"""
调试页面内容，检查是否有form、input等元素
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_page_content():
    """调试页面内容"""
    print("开始调试页面内容...")

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

            # 检查是否有form元素
            form_count = await page.evaluate("document.querySelectorAll('form').length")
            print(f"form元素数量: {form_count}")

            # 检查是否有input元素
            input_count = await page.evaluate("document.querySelectorAll('input').length")
            print(f"input元素数量: {input_count}")

            # 检查是否有select元素
            select_count = await page.evaluate("document.querySelectorAll('select').length")
            print(f"select元素数量: {select_count}")

            # 检查是否有textarea元素
            textarea_count = await page.evaluate("document.querySelectorAll('textarea').length")
            print(f"textarea元素数量: {textarea_count}")

            # 检查是否有button元素
            button_count = await page.evaluate("document.querySelectorAll('button').length")
            print(f"button元素数量: {button_count}")

            # 检查是否有a元素
            a_count = await page.evaluate("document.querySelectorAll('a').length")
            print(f"a元素数量: {a_count}")

            # 获取所有form元素的详细信息
            forms_info = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    return Array.from(forms).map(form => ({
                        id: form.id,
                        name: form.name,
                        action: form.action,
                        method: form.method,
                        innerHTML: form.innerHTML.substring(0, 200) + '...'
                    }));
                }
            """)

            print(f"\nform元素详情:")
            for i, form in enumerate(forms_info):
                print(f"  Form {i+1}:")
                print(f"    ID: {form['id']}")
                print(f"    Name: {form['name']}")
                print(f"    Action: {form['action']}")
                print(f"    Method: {form['method']}")
                print(f"    HTML: {form['innerHTML']}")
                print()

            # 获取所有input元素的详细信息
            inputs_info = await page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input');
                    return Array.from(inputs).map(input => ({
                        id: input.id,
                        name: input.name,
                        type: input.type,
                        value: input.value,
                        placeholder: input.placeholder
                    }));
                }
            """)

            print(f"input元素详情:")
            for i, input_elem in enumerate(inputs_info):
                print(f"  Input {i+1}:")
                print(f"    ID: {input_elem['id']}")
                print(f"    Name: {input_elem['name']}")
                print(f"    Type: {input_elem['type']}")
                print(f"    Value: {input_elem['value']}")
                print(f"    Placeholder: {input_elem['placeholder']}")
                print()

            # 检查页面源码中是否包含form
            page_content = await page.content()
            if '<form' in page_content.lower():
                print("✓ 页面源码中包含form标签")
            else:
                print("✗ 页面源码中不包含form标签")

            if '<input' in page_content.lower():
                print("✓ 页面源码中包含input标签")
            else:
                print("✗ 页面源码中不包含input标签")

            # 等待用户查看
            print("\n页面已打开，请手动检查页面内容...")
            await asyncio.sleep(10)

        except Exception as e:
            print(f"调试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_page_content())
