# -*- coding: utf-8 -*-
"""
用户礼物库存数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from app.core.database import Base


class UserGiftInventory(Base):
    """用户礼物库存"""
    __tablename__ = "user_gift_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False, comment="用户ID")
    gift_id = Column(String, index=True, nullable=False, comment="礼物ID")
    quantity = Column(Integer, default=0, nullable=False, comment="库存数量")
    max_quantity = Column(Integer, default=10, nullable=False, comment="最大库存")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<UserGiftInventory(user_id={self.user_id}, gift_id={self.gift_id}, quantity={self.quantity})>"
