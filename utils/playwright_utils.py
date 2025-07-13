import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, ElementHandle
from models.page_node import PageNode, NodeType, PageStructure
import uuid
from datetime import datetime


class PlaywrightUtils:
    """Playwright工具类"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def start_browser(self, headless: bool = False):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless, devtools=True)
        self.page = await self.browser.new_page()

    async def close_browser(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def navigate_to_page(self, url: str) -> str:
        """导航到页面"""
        if not self.page:
            raise Exception("浏览器未启动")

        await self.page.goto(url)
        title = await self.page.title()
        return title

    async def parse_page_structure(self, url: str, screenshot_dir: str = "data/screenshots") -> PageStructure:
        """解析页面结构"""
        if not self.page:
            raise Exception("浏览器未启动")

        try:
            # 导航到页面
            title = await self.navigate_to_page(url)

            # 创建截图目录
            os.makedirs(screenshot_dir, exist_ok=True)

            # 截图
            screenshot_filename = f"{uuid.uuid4()}.png"
            screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
            await self.page.screenshot(path=screenshot_path)

            # 解析页面节点
            nodes = await self._extract_page_nodes(url)

            # 创建页面结构
            page_structure = PageStructure(
                id=str(uuid.uuid4()),
                url=url,
                title=title,
                nodes=nodes,
                screenshot_path=screenshot_path
            )

            return page_structure

        except Exception as e:
            print(f"页面解析错误: {str(e)}")
            raise

    async def _extract_page_nodes(self, url: str) -> List[PageNode]:
        """提取页面节点 - 重点提取可测试的节点（表单、按钮、输入框等）"""
        if not self.page:
            return []

        try:
            # 只抓取表单内部的元素，过滤掉表单外部的元素
            elements_data = await self.page.evaluate("""
                () => {
                    const data = [];
                    let index = 0;

                    // 查找所有表单
                    const forms = document.querySelectorAll('form');
                    forms.forEach((form) => {
                        // 获取表单本身
                        const formRect = form.getBoundingClientRect();
                        const formComputedStyle = window.getComputedStyle(form);
                        const formIsVisible = formRect.width > 0 && formRect.height > 0 &&
                                              formComputedStyle.visibility !== 'hidden' &&
                                              formComputedStyle.display !== 'none' &&
                                              formComputedStyle.opacity !== '0';

                        // 获取表单属性
                        const formAttributes = {};
                        const importantAttrs = ['id', 'name', 'class', 'type', 'value', 'href', 'placeholder', 'title', 'alt', 'role', 'tabindex', 'action', 'method'];
                        for (let attr of form.attributes) {
                            if (importantAttrs.includes(attr.name) || attr.name.startsWith('data-')) {
                                formAttributes[attr.name] = attr.value;
                            }
                        }

                        // 生成表单的XPath
                        const getXPath = (element) => {
                            try {
                                if (!element || !element.parentNode) {
                                    return '';
                                }
                                if (element.id !== '') {
                                    return `//*[@id="${element.id}"]`;
                                }
                                if (element === document.body) {
                                    return '/html/body';
                                }
                                if (element === document.documentElement) {
                                    return '/html';
                                }
                                let ix = 0;
                                const siblings = element.parentNode.childNodes;
                                for (let sibling of siblings) {
                                    if (sibling === element) {
                                        const parentXPath = getXPath(element.parentNode);
                                        if (parentXPath) {
                                            return parentXPath + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                        } else {
                                            return '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                        }
                                    }
                                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                        ix++;
                                    }
                                }
                                return '';
                            } catch (error) {
                                return '';
                            }
                        };

                        // 生成表单的CSS选择器
                        const getCSSSelector = (element) => {
                            try {
                                if (element.id) {
                                    return `#${element.id}`;
                                }
                                let selector = element.tagName.toLowerCase();
                                if (element.className && typeof element.className === 'string') {
                                    const classes = element.className.split(' ').filter(c => c.trim());
                                    if (classes.length > 0) {
                                        selector += '.' + classes.join('.');
                                    }
                                }
                                if (element.name) {
                                    selector += `[name="${element.name}"]`;
                                }
                                return selector;
                            } catch (error) {
                                return element.tagName.toLowerCase();
                            }
                        };

                        // 添加表单本身
                        const formData = {
                            id: form.id || `form_${index}`,
                            tag_name: 'form',
                            text_content: (form.textContent || '').trim().substring(0, 200),
                            xpath: getXPath(form),
                            css_selector: getCSSSelector(form),
                            attributes: formAttributes,
                            is_visible: formIsVisible,
                            is_interactive: true,
                            size: {
                                width: Math.round(formRect.width),
                                height: Math.round(formRect.height)
                            },
                            position: {
                                x: Math.round(formRect.left),
                                y: Math.round(formRect.top)
                            },
                            parent_id: null,
                            children: []
                        };
                        data.push(formData);
                        const formId = formData.id;
                        index++;

                        // 获取表单内部的所有输入元素
                        const formElements = form.querySelectorAll('input, select, textarea, button');
                        formElements.forEach((element) => {
                            try {
                                const rect = element.getBoundingClientRect();
                                const computedStyle = window.getComputedStyle(element);

                                // 检查元素是否可见
                                const isVisible = rect.width > 0 && rect.height > 0 &&
                                                  computedStyle.visibility !== 'hidden' &&
                                                  computedStyle.display !== 'none' &&
                                                  computedStyle.opacity !== '0';

                                // 检查元素是否可交互
                                const isInteractive = ['button', 'input', 'select', 'textarea'].includes(element.tagName.toLowerCase());

                                // 获取元素属性
                                const attributes = {};
                                for (let attr of element.attributes) {
                                    if (importantAttrs.includes(attr.name) || attr.name.startsWith('data-')) {
                                        attributes[attr.name] = attr.value;
                                    }
                                }

                                // 生成元素的XPath
                                const elementXPath = getXPath(element);

                                // 生成元素的CSS选择器
                                const elementCSSSelector = getCSSSelector(element);

                                // 获取文本内容
                                let textContent = element.textContent || '';
                                textContent = textContent.replace(/\\s+/g, ' ').trim();
                                if (textContent.length > 200) {
                                    textContent = textContent.substring(0, 200) + '...';
                                }

                                // 获取子元素ID列表
                                const children = [];
                                for (let child of element.children) {
                                    if (child.id) {
                                        children.push(child.id);
                                    } else {
                                        children.push(`child_${index}_${children.length}`);
                                    }
                                }

                                const elementData = {
                                    id: element.id || `element_${index}`,
                                    tag_name: element.tagName.toLowerCase(),
                                    text_content: textContent,
                                    xpath: elementXPath,
                                    css_selector: elementCSSSelector,
                                    attributes: attributes,
                                    is_visible: isVisible,
                                    is_interactive: isInteractive,
                                    size: {
                                        width: Math.round(rect.width),
                                        height: Math.round(rect.height)
                                    },
                                    position: {
                                        x: Math.round(rect.left),
                                        y: Math.round(rect.top)
                                    },
                                    parent_id: formId,
                                    children: children
                                };

                                data.push(elementData);
                                index++;
                            } catch (error) {
                                // 忽略单个元素错误
                            }
                        });
                    });

                    return data;
                }
            """)

            nodes = []
            for element_data in elements_data:
                try:
                    node_type = self._determine_node_type(
                        element_data['tag_name'],
                        element_data['attributes']
                    )
                    node = PageNode(
                        id=element_data['id'],
                        type=node_type,
                        tag_name=element_data['tag_name'],
                        text_content=element_data['text_content'],
                        xpath=element_data['xpath'],
                        css_selector=element_data['css_selector'],
                        attributes=element_data['attributes'],
                        is_visible=element_data['is_visible'],
                        is_interactive=element_data['is_interactive'],
                        size=element_data['size'],
                        position=element_data['position'],
                        parent_id=element_data['parent_id'],
                        children=element_data['children'],
                        page_url=url
                    )
                    nodes.append(node)
                except Exception as e:
                    print(f"转换节点数据失败: {e}")
                    continue
            return nodes
        except Exception as e:
            print(f"提取页面节点失败: {str(e)}")
            return []

    def _determine_node_type(self, tag_name: str, attributes: Dict[str, str]) -> NodeType:
        """确定节点类型 - 重点识别表单和可测试元素"""
        tag_name_lower = tag_name.lower()

        # 表单元素
        if tag_name_lower == 'form':
            return NodeType.FORM
        elif tag_name_lower == 'input':
            input_type = attributes.get('type', '').lower()
            if input_type == 'checkbox':
                return NodeType.CHECKBOX
            elif input_type == 'radio':
                return NodeType.RADIO
            elif input_type in ['submit', 'button', 'reset']:
                return NodeType.BUTTON
            elif input_type in ['text', 'email', 'password', 'number', 'tel', 'url', 'search']:
                return NodeType.INPUT
            else:
                return NodeType.INPUT
        elif tag_name_lower == 'button':
            return NodeType.BUTTON
        elif tag_name_lower == 'select':
            return NodeType.SELECT
        elif tag_name_lower == 'textarea':
            return NodeType.INPUT
        elif tag_name_lower == 'a':
            # 检查是否是按钮样式的链接
            if attributes.get('role') == 'button' or 'button' in (attributes.get('class', '')).lower():
                return NodeType.BUTTON
            return NodeType.LINK
        elif tag_name_lower == 'img':
            return NodeType.IMAGE
        elif tag_name_lower == 'table':
            return NodeType.TABLE
        elif tag_name_lower == 'div':
            # 检查div是否是可交互的（如按钮样式的div）
            if (attributes.get('role') == 'button' or
                attributes.get('onclick') or
                attributes.get('tabindex') or
                'button' in (attributes.get('class', '')).lower()):
                return NodeType.BUTTON
            return NodeType.DIV
        elif tag_name_lower == 'span':
            # 检查span是否是可交互的
            if (attributes.get('role') == 'button' or
                attributes.get('onclick') or
                'button' in (attributes.get('class', '')).lower()):
                return NodeType.BUTTON
            return NodeType.SPAN
        else:
            # 其他元素，检查是否可交互
            if (attributes.get('role') == 'button' or
                attributes.get('onclick') or
                attributes.get('tabindex')):
                return NodeType.BUTTON
            return NodeType.OTHER

    async def execute_test_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试步骤"""
        if not self.page:
            raise Exception("浏览器未启动")

        action = step_data.get('action')
        target_selector = step_data.get('target_selector')
        input_data = step_data.get('input_data')
        wait_time = step_data.get('wait_time', 1)

        result = {
            'status': 'success',
            'message': '',
            'output_data': None,
            'screenshot_path': None
        }

        try:
            if action == 'click':
                await self.page.click(target_selector)
            elif action == 'fill':
                await self.page.fill(target_selector, input_data)
            elif action == 'type':
                await self.page.type(target_selector, input_data)
            elif action == 'select_option':
                await self.page.select_option(target_selector, input_data)
            elif action == 'check':
                await self.page.check(target_selector)
            elif action == 'uncheck':
                await self.page.uncheck(target_selector)
            elif action == 'navigate':
                await self.page.goto(input_data)
            elif action == 'wait':
                await self.page.wait_for_timeout(wait_time * 1000)
            elif action == 'wait_for_element':
                await self.page.wait_for_selector(target_selector)
            else:
                raise Exception(f"不支持的操作类型: {action}")

            # 等待指定时间
            if wait_time > 0:
                await self.page.wait_for_timeout(wait_time * 1000)

            # 获取输出数据
            if action in ['fill', 'type', 'select_option']:
                result['output_data'] = await self.page.input_value(target_selector)

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)

        # 截图
        screenshot_filename = f"step_{uuid.uuid4()}.png"
        screenshot_path = os.path.join("data/screenshots", screenshot_filename)
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        await self.page.screenshot(path=screenshot_path)
        result['screenshot_path'] = screenshot_path

        return result

    async def get_element_text(self, selector: str) -> str:
        """获取元素文本"""
        if not self.page:
            raise Exception("浏览器未启动")

        return await self.page.text_content(selector)

    async def get_element_attribute(self, selector: str, attribute: str) -> str:
        """获取元素属性"""
        if not self.page:
            raise Exception("浏览器未启动")

        return await self.page.get_attribute(selector, attribute)

    async def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        if not self.page:
            raise Exception("浏览器未启动")

        return await self.page.is_visible(selector)

    async def wait_for_element(self, selector: str, timeout: int = 30000):
        """等待元素出现"""
        if not self.page:
            raise Exception("浏览器未启动")

        await self.page.wait_for_selector(selector, timeout=timeout)

    async def highlight_element(self, selector: str) -> bool:
        """高亮页面上被选择器选中的节点（优先用 JS outline）"""
        if not self.page:
            raise Exception("浏览器未启动")
        try:
            element = await self.page.query_selector(selector)
            if not element:
                print(f"高亮失败：selector 未命中元素: {selector}")
                return False
            # 用 JS 给元素加红色 outline
            await self.page.eval_on_selector(selector, "el => el.style.outline = '3px solid red'")
            return True
        except Exception as e:
            print(f"高亮元素失败: {e}")
            return False

    async def extract_form_structure(self, url: str) -> Dict[str, Any]:
        """专门提取表单结构信息"""
        if not self.page:
            raise Exception("浏览器未启动")

        try:
            # 导航到页面
            await self.navigate_to_page(url)

            # 执行JavaScript提取表单信息
            form_data = await self.page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    const formStructures = [];

                    forms.forEach((form, formIndex) => {
                        const formStructure = {
                            formId: form.id || `form_${formIndex}`,
                            formName: form.name || '',
                            formAction: form.action || '',
                            formMethod: form.method || 'get',
                            formEnctype: form.enctype || 'application/x-www-form-urlencoded',
                            formFields: [],
                            formButtons: []
                        };

                        // 提取表单字段
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach((input, inputIndex) => {
                            const field = {
                                id: input.id || `field_${formIndex}_${inputIndex}`,
                                name: input.name || '',
                                type: input.type || input.tagName.toLowerCase(),
                                placeholder: input.placeholder || '',
                                required: input.required || false,
                                disabled: input.disabled || false,
                                value: input.value || '',
                                options: []
                            };

                            // 对于select元素，提取选项
                            if (input.tagName === 'SELECT') {
                                const options = input.querySelectorAll('option');
                                options.forEach(option => {
                                    field.options.push({
                                        value: option.value,
                                        text: option.textContent.trim(),
                                        selected: option.selected
                                    });
                                });
                            }

                            // 对于checkbox和radio，提取选项组
                            if (input.type === 'checkbox' || input.type === 'radio') {
                                const name = input.name;
                                if (name) {
                                    const sameNameInputs = form.querySelectorAll(`input[name="${name}"]`);
                                    if (sameNameInputs.length > 1) {
                                        field.group = Array.from(sameNameInputs).map(inp => ({
                                            value: inp.value,
                                            text: inp.nextElementSibling?.textContent?.trim() || inp.value,
                                            checked: inp.checked
                                        }));
                                    }
                                }
                            }

                            formStructure.formFields.push(field);
                        });

                        // 提取表单按钮
                        const buttons = form.querySelectorAll('button, input[type="submit"], input[type="button"], input[type="reset"]');
                        buttons.forEach((button, buttonIndex) => {
                            const buttonInfo = {
                                id: button.id || `button_${formIndex}_${buttonIndex}`,
                                name: button.name || '',
                                type: button.type || 'button',
                                text: button.textContent?.trim() || button.value || '',
                                disabled: button.disabled || false
                            };
                            formStructure.formButtons.push(buttonInfo);
                        });

                        formStructures.push(formStructure);
                    });

                    return formStructures;
                }
            """)

            return {
                'url': url,
                'title': await self.page.title(),
                'forms': form_data
            }

        except Exception as e:
            print(f"表单结构提取错误: {str(e)}")
            return {'url': url, 'title': '', 'forms': []}
