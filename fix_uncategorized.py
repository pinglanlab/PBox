import json
import os

TOOLS_FILE = "config/tools.json"

def fix_uncategorized():
    try:
        with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
            tools = json.load(f)
        
        count = 0
        for tool in tools:
            if tool.get('category') == '网页工具/未分类':
                tool['category'] = '网页工具/其他工具'
                count += 1
        
        with open(TOOLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tools, f, ensure_ascii=False, indent=2)
        
        print(f"成功将 {count} 个工具从'网页工具/未分类'改为'网页工具/其他工具'")
        
    except Exception as e:
        print(f"修改分类失败: {e}")

if __name__ == "__main__":
    fix_uncategorized()
