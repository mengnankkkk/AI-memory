# -*- coding: utf-8 -*-
"""
礼物系统配置
定义所有礼物类型、属性和效果
"""
from typing import List, Dict, Any

# 礼物类型配置
GIFT_CONFIGS: List[Dict[str, Any]] = [
    # 普通礼物 (5-10好感度)
    {
        "gift_id": "rose",
        "gift_type": "flower",
        "name": "红玫瑰",
        "emoji": "🌹",
        "description": "经典的爱情象征，表达深深的爱意",
        "rarity": "common",
        "affinity_bonus": 8,
        "trust_bonus": 2,
        "tension_bonus": 0,
        "price": 50,
        "currency": "coins",
        "initial_quantity": 5,  # 初始库存
        "max_quantity": 10     # 最大库存
    },
    {
        "gift_id": "tulip",
        "gift_type": "flower",
        "name": "郁金香",
        "emoji": "🌷",
        "description": "优雅的花朵，代表着纯洁的爱情",
        "rarity": "common",
        "affinity_bonus": 6,
        "trust_bonus": 1,
        "tension_bonus": 0,
        "price": 30,
        "currency": "coins",
        "initial_quantity": 8,
        "max_quantity": 15
    },
    {
        "gift_id": "sunflower",
        "gift_type": "flower",
        "name": "向日葵",
        "emoji": "🌻",
        "description": "阳光般的花朵，带来温暖和快乐",
        "rarity": "common",
        "affinity_bonus": 5,
        "trust_bonus": 2,
        "tension_bonus": -1,
        "price": 20,
        "currency": "coins",
        "initial_quantity": 10,
        "max_quantity": 20
    },

    # 稀有礼物 (10-20好感度)
    {
        "gift_id": "chocolate_box",
        "gift_type": "chocolate",
        "name": "精致巧克力礼盒",
        "emoji": "🍫",
        "description": "甜蜜的巧克力，融化你的心",
        "rarity": "rare",
        "affinity_bonus": 12,
        "trust_bonus": 3,
        "tension_bonus": 0,
        "price": 100,
        "currency": "coins",
        "initial_quantity": 3,
        "max_quantity": 8
    },
    {
        "gift_id": "cake",
        "gift_type": "dessert",
        "name": "草莓蛋糕",
        "emoji": "🍰",
        "description": "甜蜜的蛋糕，甜到心里",
        "rarity": "rare",
        "affinity_bonus": 10,
        "trust_bonus": 2,
        "tension_bonus": -1,
        "price": 80,
        "currency": "coins",
        "initial_quantity": 4,
        "max_quantity": 10
    },
    {
        "gift_id": "teddy_bear",
        "gift_type": "plushie",
        "name": "泰迪熊",
        "emoji": "🧸",
        "description": "可爱的泰迪熊，陪伴你每一天",
        "rarity": "rare",
        "affinity_bonus": 15,
        "trust_bonus": 5,
        "tension_bonus": -2,
        "price": 150,
        "currency": "coins",
        "initial_quantity": 2,
        "max_quantity": 5
    },

    # 史诗礼物 (20-30好感度)
    {
        "gift_id": "jewelry_necklace",
        "gift_type": "jewelry",
        "name": "心形项链",
        "emoji": "💎",
        "description": "精致的心形项链，象征永恒的爱",
        "rarity": "epic",
        "affinity_bonus": 25,
        "trust_bonus": 8,
        "tension_bonus": 0,
        "price": 500,
        "currency": "coins",
        "initial_quantity": 1,
        "max_quantity": 3
    },
    {
        "gift_id": "perfume",
        "gift_type": "cosmetic",
        "name": "高级香水",
        "emoji": "💐",
        "description": "优雅的香水，让你更加迷人",
        "rarity": "epic",
        "affinity_bonus": 22,
        "trust_bonus": 6,
        "tension_bonus": 0,
        "price": 400,
        "currency": "coins",
        "initial_quantity": 1,
        "max_quantity": 4
    },
    {
        "gift_id": "book_collection",
        "gift_type": "book",
        "name": "精装书籍",
        "emoji": "📚",
        "description": "精心挑选的书籍，分享知识与思想",
        "rarity": "epic",
        "affinity_bonus": 20,
        "trust_bonus": 10,
        "tension_bonus": -3,
        "price": 300,
        "currency": "coins",
        "initial_quantity": 2,
        "max_quantity": 6
    },

    # 传说礼物 (30+好感度)
    {
        "gift_id": "diamond_ring",
        "gift_type": "jewelry",
        "name": "钻石戒指",
        "emoji": "💍",
        "description": "璀璨的钻石戒指，承诺一生一世",
        "rarity": "legendary",
        "affinity_bonus": 50,
        "trust_bonus": 20,
        "tension_bonus": 0,
        "price": 1000,
        "currency": "coins",
        "initial_quantity": 1,
        "max_quantity": 1
    },
    {
        "gift_id": "bouquet_99roses",
        "gift_type": "flower",
        "name": "99朵玫瑰",
        "emoji": "💐",
        "description": "99朵玫瑰，代表天长地久的爱",
        "rarity": "legendary",
        "affinity_bonus": 40,
        "trust_bonus": 15,
        "tension_bonus": -5,
        "price": 999,
        "currency": "coins",
        "initial_quantity": 1,
        "max_quantity": 2
    }
]


def get_gift_by_id(gift_id: str) -> Dict[str, Any] | None:
    """根据礼物ID获取礼物配置"""
    for gift in GIFT_CONFIGS:
        if gift["gift_id"] == gift_id:
            return gift
    return None


def get_gifts_by_type(gift_type: str) -> List[Dict[str, Any]]:
    """根据类型获取礼物列表"""
    return [gift for gift in GIFT_CONFIGS if gift["gift_type"] == gift_type]


def get_gifts_by_rarity(rarity: str) -> List[Dict[str, Any]]:
    """根据稀有度获取礼物列表"""
    return [gift for gift in GIFT_CONFIGS if gift["rarity"] == rarity]


def get_all_gifts() -> List[Dict[str, Any]]:
    """获取所有礼物配置"""
    return GIFT_CONFIGS
