"""Generate test Excel data for OpenExtract."""
import pandas as pd
from pathlib import Path

# Create test directory
output_dir = Path("data/test")
output_dir.mkdir(parents=True, exist_ok=True)

# Test data
data = {
    "Id": [1, 2, 3],
    "articleTitle": [
        "关于加强网络安全管理的通知",
        "推进绿色能源发展实施方案",
        "优化营商环境若干措施"
    ],
    "articleContent": [
        "为进一步加强网络安全管理，保护用户数据安全，现就有关事项通知如下：一、建立健全网络安全管理制度。二、加强技术防护措施。三、定期开展安全评估。",
        "为推动绿色能源产业高质量发展，制定本实施方案。主要目标：到2025年，可再生能源占比达到30%。重点任务：1.加快风电、光伏项目建设；2.完善绿色金融支持政策；3.培育龙头企业。",
        '为深化"放管服"改革，持续优化营商环境，提出以下措施：1.压缩企业开办时间至1个工作日；2.推行"一网通办"；3.建立企业诉求快速响应机制；4.加强事中事后监管。'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = output_dir / "test_policies.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")

print(f"✓ Test Excel file created: {output_file}")
print(f"✓ Contains {len(df)} test policy documents")
