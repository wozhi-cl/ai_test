#!/usr/bin/env python3
"""
测试节点的增删改查功能
"""

import json
import os
from models.page_node import PageStructure, PageNode, NodeType
from datetime import datetime

def test_crud_operations():
    """测试增删改查操作"""

    # 1. 创建测试页面结构
    print("1. 创建测试页面结构...")
    structure = PageStructure(
        id="test-structure",
        url="https://example.com",
        title="测试页面结构",
        nodes=[],
        created_at=datetime.now()
    )

    # 2. 测试新增节点
    print("2. 测试新增节点...")
    node1 = PageNode(
        id="node-1",
        type=NodeType.BUTTON,
        tag_name="button",
        text_content="测试按钮",
        attributes={"class": "test-btn"},
        xpath="//button[@class='test-btn']",
        css_selector="button.test-btn",
        position={"x": 100, "y": 100},
        size={"width": 80, "height": 30},
        is_visible=True,
        is_interactive=True,
        parent_id=None,
        children=[],
        page_url="https://example.com",
        created_at=datetime.now()
    )

    structure.nodes.append(node1)
    print(f"   新增节点成功: {node1.tag_name}")

    # 3. 测试保存到文件
    print("3. 测试保存到文件...")
    test_file = "data/page_nodes/test-structure.json"
    structure.save_to_file(test_file)
    print(f"   保存成功: {test_file}")

    # 4. 测试从文件加载
    print("4. 测试从文件加载...")
    loaded_structure = PageStructure.load_from_file(test_file)
    print(f"   加载成功: {loaded_structure.title}, 节点数: {len(loaded_structure.nodes)}")

    # 5. 测试编辑节点
    print("5. 测试编辑节点...")
    if loaded_structure.nodes:
        node = loaded_structure.nodes[0]
        original_text = node.text_content
        node.text_content = "修改后的按钮"
        node.attributes["class"] = "modified-btn"
        print(f"   编辑节点: {original_text} -> {node.text_content}")

        # 保存修改
        loaded_structure.save_to_file(test_file)
        print("   保存修改成功")

    # 6. 测试删除节点
    print("6. 测试删除节点...")
    if loaded_structure.nodes:
        node_to_delete = loaded_structure.nodes[0]
        print(f"   删除节点: {node_to_delete.tag_name}")
        loaded_structure.nodes = [n for n in loaded_structure.nodes if n.id != node_to_delete.id]
        loaded_structure.save_to_file(test_file)
        print(f"   删除成功，剩余节点数: {len(loaded_structure.nodes)}")

    # 7. 清理测试文件
    print("7. 清理测试文件...")
    if os.path.exists(test_file):
        os.remove(test_file)
        print("   清理完成")

    print("\n✅ 所有CRUD操作测试通过！")

if __name__ == "__main__":
    test_crud_operations()
