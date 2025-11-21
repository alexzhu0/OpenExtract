"""Display test results in a readable format."""
import json
from pathlib import Path

results_file = Path("output/test_results/results.json")

if not results_file.exists():
    print("❌ Results file not found!")
    exit(1)

with open(results_file, "r", encoding="utf-8") as f:
    results = json.load(f)

print(f"{'='*70}")
print(f"测试结果汇总 - 共处理 {len(results)} 篇文档")
print(f"{'='*70}\n")

for i, result in enumerate(results, 1):
    print(f"📄 文档 {i}: {result['title']}")
    print(f"   ID: {result['doc_id']}")
    
    if result['errors']:
        print(f"   ⚠️  错误: {result['errors']}")
    else:
        print(f"   ✓ 处理成功")
    
    print(f"\n   提取结果:")
    for section, data in result['structured_tags'].items():
        print(f"   [{section}]")
        if isinstance(data, dict) and 'content' in data:
            # Try to parse nested JSON
            try:
                nested = json.loads(data['content'])
                for key, value in nested.items():
                    if isinstance(value, list):
                        print(f"     • {key}:")
                        for item in value:
                            print(f"       - {item}")
                    else:
                        print(f"     • {key}: {value}")
            except:
                print(f"     {data['content']}")
        else:
            print(f"     {json.dumps(data, ensure_ascii=False, indent=6)}")
    
    print(f"\n{'-'*70}\n")

print(f"✅ 测试完成！结果已保存至: {results_file}")
