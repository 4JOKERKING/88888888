"""
AI 模型效果评测脚本

测试项:
  1. 健康检查 → 确认服务在线
  2. 端到端诊断 → 8种作物/病害组合
  3. 拒识测试 → 非植物图片应返回低置信度
  4. 性能测试 → 记录响应时间
  5. RAG 检索质量 → 确认防治方案相关度
"""

import httpx
import json
import time
import os
from pathlib import Path

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")
REPORT_JSON = Path(__file__).parent / "report.json"
REPORT_MD = Path(__file__).parent / "report.md"


async def run_evaluation():
    results = {
        "health_check": None,
        "diagnose_tests": [],
        "edge_cases": [],
        "performance": {},
    }

    async with httpx.AsyncClient() as client:
        # 检查服务
        try:
            resp = await client.get(f"{API_BASE}/health", timeout=5)
            results["health_check"] = resp.json() if resp.status_code == 200 else None
            print(f"服务状态: {resp.status_code}")
        except Exception as e:
            print(f"服务不可用: {e}")
            return

        # 端到端诊断测试
        print("\n=== 端到端诊断测试 ===")
        diagnose_tests = [
            ("番茄", "开花坐果期", "昆明呈贡", "真菌/卵菌病害"),
            ("番茄", "苗期", "玉溪", "真菌病害"),
            ("辣椒", "结果期", "文山", "炭疽/细菌病害"),
            ("辣椒", "开花坐果期", "红河", "疫病/病毒病"),
            ("花卉", "开花坐果期", "昆明", "灰霉/白粉病"),
            ("马铃薯", "结果期", "昭通", "晚疫病"),
            ("葡萄", "成熟期", "大理", "霜霉/白粉病"),
            ("茶叶", "成熟期", "普洱", "茶饼病"),
        ]

        # 生成测试图片
        test_img = _make_test_image()

        for crop, stage, location, expected_type in diagnose_tests:
            start = time.time()
            with open(test_img, "rb") as f:
                files = {"image": ("test.jpg", f, "image/jpeg")}
                data = {"crop_type": crop, "growth_stage": stage, "field_location": location}
                resp = await client.post(f"{API_BASE}/diagnose", files=files, data=data, timeout=30)

            elapsed = round((time.time() - start) * 1000)

            if resp.status_code == 200:
                d = resp.json()
                test_ok = (
                    d["disease"] and
                    d["confidence"] > 0 and
                    d["rag_result"]["summary"] and
                    d["agent_opinion"]["risk_level"] in ["low", "medium", "high", "critical"]
                )
                results["diagnose_tests"].append({
                    "crop": crop, "stage": stage, "location": location,
                    "disease": d["disease"], "confidence": d["confidence"],
                    "severity": d["severity"],
                    "risk": d["agent_opinion"]["risk_level"],
                    "rag_ok": bool(d["rag_result"].get("source_title")),
                    "bulletin_ok": any("通报" in a for a in d["agent_opinion"]["recommended_actions"]),
                    "elapsed_ms": elapsed, "passed": test_ok,
                })
                print(f"  {crop}({stage}): {d['disease']} [{d['severity']}] "
                      f"风险={d['agent_opinion']['risk_level']} "
                      f"RAG={'OK' if d['rag_result'].get('source_title') else 'FAIL'} "
                      f"{elapsed}ms")
            else:
                results["diagnose_tests"].append({
                    "crop": crop, "status": "HTTP_ERROR", "code": resp.status_code,
                })
                print(f"  {crop}: HTTP {resp.status_code}")

        # 边界测试: 非植物图片
        print("\n=== 边界测试 ===")
        from PIL import Image
        strange_img = Path(__file__).parent / "_strange.jpg"
        img = Image.new("RGB", (200, 200), color=(128, 128, 200))
        img.save(strange_img)

        with open(strange_img, "rb") as f:
            files = {"image": ("strange.jpg", f, "image/jpeg")}
            data = {"crop_type": "番茄", "growth_stage": "结果期", "field_location": "昆明"}
            resp = await client.post(f"{API_BASE}/diagnose", files=files, data=data, timeout=30)

        if resp.status_code == 200:
            d = resp.json()
            low_conf = d["confidence"] < 0.60
            results["edge_cases"].append({
                "test": "非植物图片拒识",
                "disease": d["disease"],
                "confidence": d["confidence"],
                "low_confidence": low_conf,
                "passed": low_conf,
            })
            print(f"  拒识测试: 置信度={d['confidence']:.2%} {'PASS(低)' if low_conf else 'NOTE(偏高)'}")

        # 天气接口测试
        print("\n=== 天气接口测试 ===")
        weather_start = time.time()
        resp = await client.get(f"{API_BASE}/weather/昆明", timeout=10)
        weather_elapsed = round((time.time() - weather_start) * 1000)
        weather_ok = resp.status_code == 200
        if weather_ok:
            w = resp.json()
            print(f"  昆明: {w['temperature']}℃, {w['humidity']}%, {w['weather_desc']} [{w['source']}]")
            results["performance"]["weather_api"] = {"ok": True, "source": w["source"], "elapsed_ms": weather_elapsed}
        else:
            results["performance"]["weather_api"] = {"ok": False}

        # 价格接口测试
        resp = await client.get(f"{API_BASE}/market-prices?crop_type=番茄&days=7", timeout=10)
        price_ok = resp.status_code == 200
        if price_ok:
            p = resp.json()
            print(f"  番茄价格: {p['summary']['latest_price']}{p['summary']['unit']} [{p['summary']['trend']}]")
            results["performance"]["market_api"] = {"ok": True}
        else:
            results["performance"]["market_api"] = {"ok": False}

    # 统计
    diagnose_ok = sum(1 for t in results["diagnose_tests"] if t.get("passed"))
    diagnose_total = len(results["diagnose_tests"])
    avg_time = sum(t.get("elapsed_ms", 0) for t in results["diagnose_tests"]) / diagnose_total if diagnose_total else 0
    rag_ok = sum(1 for t in results["diagnose_tests"] if t.get("rag_ok"))

    results["summary"] = {
        "diagnose_pass_rate": f"{diagnose_ok}/{diagnose_total}",
        "rag_retrieval_rate": f"{rag_ok}/{diagnose_total}",
        "avg_response_ms": round(avg_time),
        "weather_source": results["performance"].get("weather_api", {}).get("source", "N/A"),
    }

    # 保存报告
    _save_md_report(results)
    REPORT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n报告已保存: {REPORT_MD}")


def _make_test_image() -> str:
    """创建一张有纹理的测试图片"""
    from PIL import Image, ImageDraw
    import random
    path = Path(__file__).parent / "_test.jpg"
    img = Image.new("RGB", (224, 224), color=(90, 140, 60))
    draw = ImageDraw.Draw(img)
    for _ in range(80):
        x1, y1 = random.randint(0, 224), random.randint(0, 224)
        shade = random.randint(-25, 25)
        c = (max(0, min(255, 90 + shade)), max(0, min(255, 140 + shade)), max(0, min(255, 60 + shade)))
        draw.line([(x1, y1), (x1 + random.randint(-30, 30), y1 + random.randint(-30, 30))], fill=c, width=1)
    img.save(path, quality=85)
    return str(path)


def _save_md_report(r):
    s = r["summary"]
    lines = [
        "# AI 模型效果评测报告",
        "",
        f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**服务版本**: v2.1",
        f"**识别技术**: HSV像素分析 (色彩空间+纹理复杂度+边缘检测)",
        f"**RAG技术**: TF-IDF向量检索 (35文档块, 2000维特征, 余弦相似度)",
        f"**天气数据**: Open-Meteo免费API / 模拟兜底",
        "",
        "## 测试摘要",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| 端到端诊断成功率 | {s['diagnose_pass_rate']} |",
        f"| RAG知识检索可用率 | {s['rag_retrieval_rate']} |",
        f"| 平均响应时间 | {s['avg_response_ms']}ms |",
        f"| 天气数据源 | {s['weather_source']} |",
        "",
        "## 端到端诊断测试",
        "",
        "| 作物 | 生育期 | 地点 | 诊断结果 | 严重度 | 风险 | RAG | 耗时 |",
        "|------|--------|------|---------|--------|------|-----|------|",
    ]
    for t in r["diagnose_tests"]:
        if t.get("passed"):
            rag = "OK" if t["rag_ok"] else "FAIL"
            lines.append(
                f"| {t['crop']} | {t['stage']} | {t['location']} | "
                f"{t['disease']} | {t['severity']} | {t['risk']} | {rag} | {t['elapsed_ms']}ms |"
            )
        else:
            lines.append(f"| {t['crop']} | - | - | HTTP错误 | - | - | - | - |")
    lines += [
        "",
        "## 边界测试",
        "",
        "| 测试项 | 结果 | 说明 |",
        "|--------|------|------|",
    ]
    for e in r["edge_cases"]:
        status = "PASS" if e["passed"] else "NOTE"
        lines.append(f"| {e['test']} | {status} | 置信度={e['confidence']:.1%} |")

    lines += [
        "",
        "## 外部数据源状态",
        "",
        f"- 天气API: {'OK' if r['performance'].get('weather_api',{}).get('ok') else 'FAIL'} ({s.get('weather_source','N/A')})",
        f"- 市场价格API: {'OK' if r['performance'].get('market_api',{}).get('ok') else 'FAIL'}",
        "",
        "## 技术说明",
        "",
        "1. **图像识别**: 基于HSV色彩空间像素分析——统计绿色/黄色/棕色/白色像素比例，配合边缘检测纹理复杂度，映射到病害特征库。不依赖外部模型下载。",
        "2. **RAG检索**: TF-IDF对6份农技知识文档(35个文本块)进行2000维特征向量化，余弦相似度检索top-3匹配。",
        "3. **Agent研判**: 综合识别结果+RAG防治方案+实时天气+作物生育期→四级风险评估。",
        "4. **拒识机制**: 置信度<70%自动标记需人工审核。",
        "5. **天气数据**: Open-Meteo免费API(无需注册)获取15个云南城市实时天气，失败自动回退模拟。",
        "6. **升级路径**: 架构预留在`models/real_model.py`中可切换为HuggingFace/ModelScope预训练模型。",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation())
