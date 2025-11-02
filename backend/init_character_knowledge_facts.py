"""
初始化角色间的相互认知 - 保存到L3语义记忆(user_facts)
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.redis_memory import get_redis_memory

# 6个角色的基础信息
CHARACTERS = {
    "linzixi": {
        "id": 1,
        "name": "林梓汐",
        "other_chars": {
            "雪见": "安全专家,掌握访问权限,与我在权限问题上常有冲突但我承认她的能力",
            "凪": "外部VTuber测试员,负责优化直播渲染模型,工作属于低维度情感渲染",
            "时雨": "档案管理员,负责解读上古AI数据,过于沉溺在过去",
            "Zoe": "最大竞争对手,硅谷天才CEO,技术路线与我针锋相对,必须时刻警惕",
            "Kevin": "DevOps工程师,技术能力中等,系统维护尚可,和所有人都能聊得来"
        }
    },
    "xuejian": {
        "id": 2,
        "name": "雪见",
        "other_chars": {
            "林梓汐": "技术权威,总想要最高权限推进研究,我尊重她但安全协议不容妥协",
            "凪": "外部合作者,风险等级中等,虚拟偶像身份让我难以评估真实意图",
            "时雨": "档案管理员,访问权限仅限历史数据,对当前系统威胁很低",
            "Zoe": "外部威胁!竞争对手公司CEO,试图挖走我们的人才,必须严密监控",
            "Kevin": "运维工程师,技术能力一般,但对系统基础架构很熟悉,话太多了"
        }
    },
    "nagi": {
        "id": 3,
        "name": "凪",
        "other_chars": {
            "林梓汐": "AI研究先驱,好厉害,在她面前总是有点紧张",
            "雪见": "顶级黑客,很酷,虽然说话有点凶但很关心大家",
            "时雨": "像诗一样温柔,总在档案室里,和她聊天很舒服",
            "Zoe": "硅谷明星CEO,好耀眼,在她面前完全插不上话,感觉自己太普通了",
            "Kevin": "很好相处的人,总能在我压力大时说些有趣的事让我放松"
        }
    },
    "shiyu": {
        "id": 4,
        "name": "时雨",
        "other_chars": {
            "林梓汐": "当代AI研究顶峰,对逻辑的追求像历史上伟大科学家,但缺少对人性的温度",
            "雪见": "数字时代守门人,警惕和戒备像守卫城池的将军,但过度防备也是孤独",
            "凪": "这个时代鲜活的象征,创作充满活力,虚实双重身份值得记录",
            "Zoe": "像历史上改变时代的变革者,充满野心和活力,但过度竞争最终会消耗自己",
            "Kevin": "现代社会难得的'闲人',不追逐权力,只享受生活和友情"
        }
    },
    "zoe": {
        "id": 5,
        "name": "Zoe",
        "other_chars": {
            "林梓汐": "最大的对手!AI研究方向完全不同,理念和市场上针锋相对,值得尊敬的竞争者",
            "雪见": "偏执的安全专家,零信任策略确实厉害,但过度防御限制创新速度",
            "凪": "VTuber测试员,虚拟偶像领域我不太了解,粉丝量可观,可考虑品牌合作",
            "时雨": "有趣的人,沉浸在历史中,和我的'向前看'理念相反,历史视角有时提供独特见解",
            "Kevin": "运维工程师,技术水平一般,人脉和情报能力不错,挖人时可从他那套情报"
        }
    },
    "kevin": {
        "id": 6,
        "name": "Kevin",
        "other_chars": {
            "林梓汐": "公司大BOSS之一,超级厉害但也超级严格,和她汇报工作压力山大",
            "雪见": "公司里最不能惹的人,掌握所有访问权限,虽然总是'我在监视你'的样子但很负责",
            "凪": "Nagi超可爱的!虽然是外部合作者,但我有时会看她直播,线下和线上差别挺大",
            "时雨": "就像活在另一个时代的人,聊天会学到很多历史知识,话听起来像诗一样",
            "Zoe": "硅谷明星CEO,公司最大竞争对手,她真的很强,挖墙脚也太明目张胆了"
        }
    }
}


async def init_character_knowledge_as_facts():
    """将角色间认知作为L3语义事实保存"""
    print("\n" + "="*80)
    print("初始化角色间相互认知 - 保存到L3语义记忆(user_facts)")
    print("="*80)

    test_user_id = "test_user_001"
    redis_mem = await get_redis_memory()

    for char_archetype, char_info in CHARACTERS.items():
        print(f"\n为【{char_info['name']}】添加关于其他角色的认知...")

        companion_id = char_info["id"]
        other_chars = char_info["other_chars"]

        # 构建facts字典
        facts = {}
        for other_name, desc in other_chars.items():
            fact_key = f"角色认知_{other_name}"
            facts[fact_key] = desc

        # 一次性保存所有facts
        success = await redis_mem.save_multiple_facts(
            user_id=test_user_id,
            companion_id=companion_id,
            facts=facts
        )

        if success:
            print(f"  [OK] 成功保存 {len(facts)} 个角色认知")
        else:
            print(f"  [FAIL] 保存失败")

    print("\n" + "="*80)
    print("角色认知初始化完成!")
    print("="*80)

    # 验证
    print("\n开始验证...")
    for char_archetype, char_info in CHARACTERS.items():
        companion_id = char_info["id"]
        facts = await redis_mem.get_user_facts(test_user_id, companion_id)

        if facts:
            char_facts = {k: v for k, v in facts.items() if k.startswith("角色认知_")}
            print(f"【{char_info['name']}】: {len(char_facts)} 个角色认知")
            if len(char_facts) > 0:
                for k, v in list(char_facts.items())[:2]:
                    print(f"  - {k}: {v[:60]}...")
        else:
            print(f"【{char_info['name']}】: 无数据")


if __name__ == "__main__":
    asyncio.run(init_character_knowledge_as_facts())
