/**
 * 图片加载工具函数
 * 用于智能加载角色好感度等级对应的图片
 */

import { LEVEL_ORDER } from '@/config/affinity-config'

/**
 * 将好感度等级key转换为对应的数字（1-7）
 * @param levelKey - 等级key（如 'stranger', 'friend' 等）
 * @returns 等级数字 1-7
 */
export function getLevelNumber(levelKey: string): number {
  const index = LEVEL_ORDER.indexOf(levelKey)
  return index >= 0 ? index + 1 : 1
}

/**
 * 获取随机的等级图片路径
 * @param companionId - 角色ID
 * @param levelKey - 好感度等级key
 * @param affinity - 当前好感度分数（用于判断是否显示视频）
 * @returns 图片路径或视频路径
 */
export function getRandomLevelImage(
  companionId: number,
  levelKey: string,
  affinity: number
): string {
  // 角色ID到文件夹名的映射
  const characterFolderMap: Record<number, string> = {
    1: 'linzixi',   // 林梓汐
    2: 'xuejian',   // 雪见
    3: 'nagi',      // 凪
    4: 'shiyu',     // 时雨
    5: 'zoe',       // Zoe
    6: 'kevin'      // 凯文
  }

  const folder = characterFolderMap[companionId] || 'nagi'

  // 好感度达到1000时，返回end.mp4视频路径
  if (affinity >= 1000) {
    return `/img/${folder}/end.mp4`
  }

  // 获取等级数字
  const levelNumber = getLevelNumber(levelKey)

  // 随机选择图片编号（支持0-3，大多数角色有0-2三张图片）
  const randomIndex = Math.floor(Math.random() * 4)

  // 构建图片路径（优先尝试指定等级的图片）
  const levelImage = `/img/${folder}/${levelNumber}-${randomIndex}.jpeg`

  return levelImage
}

/**
 * 获取备用图片路径（当指定等级图片不存在时使用）
 * @param companionId - 角色ID
 * @param levelKey - 当前等级key
 * @returns 备用图片路径数组
 */
export function getFallbackImages(
  companionId: number,
  levelKey: string
): string[] {
  const characterFolderMap: Record<number, string> = {
    1: 'linzixi',
    2: 'xuejian',
    3: 'nagi',
    4: 'shiyu',
    5: 'zoe',
    6: 'kevin'
  }

  const folder = characterFolderMap[companionId] || 'nagi'
  const levelNumber = getLevelNumber(levelKey)

  // 生成备用图片路径列表
  const fallbacks: string[] = []

  // 首先尝试当前等级的其他编号
  for (let i = 0; i < 4; i++) {
    fallbacks.push(`/img/${folder}/${levelNumber}-${i}.jpeg`)
    fallbacks.push(`/img/${folder}/${levelNumber}-${i}.jpg`)
    fallbacks.push(`/img/${folder}/${levelNumber}-${i}.png`)
  }

  // 然后尝试相邻等级的图片
  const adjacentLevels = [levelNumber - 1, levelNumber + 1].filter(n => n >= 1 && n <= 7)
  for (const adjLevel of adjacentLevels) {
    for (let i = 0; i < 4; i++) {
      fallbacks.push(`/img/${folder}/${adjLevel}-${i}.jpeg`)
      fallbacks.push(`/img/${folder}/${adjLevel}-${i}.jpg`)
    }
  }

  // 最后尝试任意等级的图片
  for (let level = 1; level <= 7; level++) {
    for (let i = 0; i < 4; i++) {
      fallbacks.push(`/img/${folder}/${level}-${i}.jpeg`)
    }
  }

  return fallbacks
}

/**
 * 检查资源是否为视频
 * @param url - 资源URL
 * @returns 是否为视频
 */
export function isVideoUrl(url: string): boolean {
  return url.toLowerCase().endsWith('.mp4') ||
         url.toLowerCase().endsWith('.webm') ||
         url.toLowerCase().endsWith('.mov')
}
