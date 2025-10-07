"""
动态回复系统测试示例
演示如何使用动态回复系统处理不同好感度等级的用户消息
"""
import asyncio
from app.services.dynamic_response_system import dynamic_response_system
from app.config.affinity_levels import get_level_by_score, get_level_config


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


async def test_message_processing():
    """测试消息处理"""

    # 测试场景
    scenarios = [
        {
            "name": "陌生阶段 - 礼貌问候",
            "affinity_score": 50,
            "message": "你好，初次见面，请多关照。",
            "mood": "平静"
        },
        {
            "name": "陌生阶段 - 过于亲密(违规)",
            "affinity_score": 80,
            "message": "宝贝，亲亲抱抱！爱你！",
            "mood": "平静"
        },
        {
            "name": "朋友阶段 - 积极分享",
            "affinity_score": 300,
            "message": "今天发生了一件超级开心的事！我想和你分享一下，我终于完成了那个项目，真的太高兴了！谢谢你之前给我的建议。",
            "mood": "开心"
        },
        {
            "name": "好友阶段 - 感谢与赞美",
            "affinity_score": 500,
            "message": "你真的很厉害，总能在我需要的时候帮助我，有你这个朋友真好！",
            "mood": "感动"
        },
        {
            "name": "特别的人 - 微妙情感",
            "affinity_score": 650,
            "message": "和你聊天的时候，总感觉时间过得特别快...说实话，你对我来说很特别。",
            "mood": "害羞"
        },
        {
            "name": "心动阶段 - 表达思念",
            "affinity_score": 800,
            "message": "最近几天没见到你，有点想你了...不知道你在干什么呢？",
            "mood": "想念"
        },
        {
            "name": "恋人阶段 - 爱的表达",
            "affinity_score": 950,
            "message": "亲爱的，爱你！今天也要开开心心的哦！么么哒~",
            "mood": "幸福"
        },
        {
            "name": "负面情绪 - 生气抱怨",
            "affinity_score": 400,
            "message": "今天真的很烦，什么事都不顺利，讨厌死了！",
            "mood": "生气"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print_section(f"测试场景 {i}: {scenario['name']}")

        # 显示初始状态
        level = get_level_by_score(scenario["affinity_score"])
        level_config = get_level_config(level)
        print(f"\n📊 初始状态:")
        print(f"   好感度分数: {scenario['affinity_score']}")
        print(f"   当前等级: {level_config.name}")
        print(f"   心情: {scenario['mood']}")
        print(f"\n💬 用户消息: {scenario['message']}")

        # 处理消息
        result = dynamic_response_system.process_user_message(
            user_message=scenario["message"],
            current_affinity_score=scenario["affinity_score"],
            user_id="test_user",
            companion_id=1,
            current_mood=scenario["mood"]
        )

        # 显示检测结果
        print(f"\n🔍 内容检测:")
        detection = result["detection"]
        print(f"   是否合适: {'✓ 是' if detection['is_appropriate'] else '✗ 否'}")
        if not detection['is_appropriate']:
            print(f"   违规类型: {detection['violation_type']}")
            print(f"   严重程度: {detection['violation_severity']}")
            print(f"   建议: {detection['suggestion']}")
        print(f"   检测到的情感: {', '.join(detection['detected_emotions']) if detection['detected_emotions'] else '无'}")
        print(f"   关键词: {', '.join(detection['detected_keywords'][:5])}")

        # 显示好感度变化
        print(f"\n📈 好感度变化:")
        affinity = result["affinity_change"]
        state = result["affinity_state"]
        print(f"   原始变化: {affinity['original_change']:+d}")
        print(f"   调整后变化: {affinity['adjusted_change']:+d}")
        print(f"   调整速率: {affinity['applied_rate']:.2f}x")
        print(f"   保护原因: {affinity['protection_reason']}")
        if affinity['warnings']:
            print(f"   ⚠️  警告: {', '.join(affinity['warnings'])}")

        # 显示等级状态
        print(f"\n🎯 等级状态:")
        print(f"   变化前: {state['before_level']} ({state['before_score']}分)")
        print(f"   变化后: {state['after_level']} ({state['after_score']}分)")
        if state['level_changed']:
            change_type = "⬆️ 升级" if state['level_up'] else "⬇️ 降级"
            print(f"   状态: {change_type}")
        else:
            print(f"   状态: ➡️ 维持")

        # 显示回复指导
        print(f"\n💡 回复指导:")
        guidance = result["response_guidance"]
        print(f"   称呼: {guidance['addressing_style']}")
        print(f"   正式度: {guidance['formality']}")
        print(f"   亲密度: {guidance['intimacy_level']}/10")
        print(f"   表情使用: {guidance['emoji_usage']}")
        print(f"   建议语气: {guidance['suggested_tone']}")
        print(f"   建议回复: {guidance['suggested_response'][:50]}...")

        # 显示趋势分析
        print(f"\n📊 趋势分析:")
        print(f"   当前趋势: {result['trend']}")
        summary = result['history_summary']
        if summary['total_interactions'] > 0:
            print(f"   历史互动: {summary['total_interactions']}次")
            print(f"   净变化: {summary['net_change']:+d}")
            print(f"   平均变化: {summary['average_change']:+.2f}")

        # 生成示例回复
        print(f"\n🤖 AI回复示例:")
        base_response = "我明白你的感受，谢谢你愿意和我分享。"
        adjusted_response = dynamic_response_system.generate_ai_response(
            base_response,
            guidance
        )
        print(f"   原始: {base_response}")
        print(f"   调整后: {adjusted_response}")

        # 显示系统提示词增强
        if i == 1 or i == 3 or i == 7:  # 只显示几个示例
            print(f"\n📝 系统提示词增强片段:")
            enhanced_prompt = dynamic_response_system.get_system_prompt_enhancement(
                "你是一个友好的AI助手。",
                level,
                scenario['mood'],
                state['after_score']
            )
            # 只显示前300字符
            print(f"   {enhanced_prompt[:300]}...")

        print("\n" + "-"*60)


async def test_protection_mechanism():
    """测试保护机制"""
    print_section("保护机制测试")

    test_cases = [
        {
            "name": "单次大幅增加",
            "score": 500,
            "change": 100,  # 超过限制
        },
        {
            "name": "单次大幅减少",
            "score": 500,
            "change": -50,  # 超过限制
        },
        {
            "name": "低分保护",
            "score": 30,  # 低于安全值
            "change": -10,
        },
        {
            "name": "高分减速",
            "score": 960,  # 高于安全值
            "change": 20,
        }
    ]

    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"   当前分数: {case['score']}")
        print(f"   原始变化: {case['change']:+d}")

        from app.services.affinity_protector import AffinityProtector
        protector = AffinityProtector()
        result = protector.protect_and_adjust(
            case['score'],
            case['change'],
            case['name']
        )

        print(f"   调整后变化: {result.adjusted_change:+d}")
        print(f"   应用速率: {result.applied_rate:.2f}x")
        print(f"   保护原因: {result.protection_reason}")
        if result.warnings:
            print(f"   ⚠️  {', '.join(result.warnings)}")


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "动态回复系统测试" + " "*15 + "║")
    print("╚" + "="*58 + "╝")

    # 运行消息处理测试
    await test_message_processing()

    # 运行保护机制测试
    await test_protection_mechanism()

    print_section("测试完成")
    print("\n✓ 所有测试场景已执行完成！")
    print("\n系统已成功集成到主应用中。")
    print("你可以通过 /api/chat 接口使用完整的动态回复功能。\n")


if __name__ == "__main__":
    asyncio.run(main())
