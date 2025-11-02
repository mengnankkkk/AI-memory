const fs = require('fs');
const path = require('path');

// 基础路径
const imgDir = 'E:\\github\\AI-memory\\img';

// 角色文件夹列表
const characters = ['nagi', 'xuejian', 'zoe', 'shiyu', 'linzixi', 'kevin'];

// 图片格式
const extensions = ['jpeg', 'jpg', 'png'];

console.log('=== 开始整理图片文件 ===\n');

// 步骤1: 修复命名格式错误
console.log('步骤1: 修复命名格式错误');

// kevin: 1.jpeg -> 1-0.jpeg, 2.jpeg -> 2-0.jpeg
const kevinDir = path.join(imgDir, 'kevin');
if (fs.existsSync(path.join(kevinDir, '1.jpeg'))) {
  fs.renameSync(
    path.join(kevinDir, '1.jpeg'),
    path.join(kevinDir, '1-0.jpeg')
  );
  console.log('✅ kevin: 1.jpeg → 1-0.jpeg');
}
if (fs.existsSync(path.join(kevinDir, '2.jpeg'))) {
  fs.renameSync(
    path.join(kevinDir, '2.jpeg'),
    path.join(kevinDir, '2-0.jpeg')
  );
  console.log('✅ kevin: 2.jpeg → 2-0.jpeg');
}

// linzixi: 3-3.jpg -> 3-2.jpg
const linzixiDir = path.join(imgDir, 'linzixi');
if (fs.existsSync(path.join(linzixiDir, '3-3.jpg'))) {
  fs.renameSync(
    path.join(linzixiDir, '3-3.jpg'),
    path.join(linzixiDir, '3-2.jpg')
  );
  console.log('✅ linzixi: 3-3.jpg → 3-2.jpg');
}

// nagi: 4-3.jpg -> 4-2.jpg
const nagiDir = path.join(imgDir, 'nagi');
if (fs.existsSync(path.join(nagiDir, '4-3.jpg'))) {
  fs.renameSync(
    path.join(nagiDir, '4-3.jpg'),
    path.join(nagiDir, '4-2.jpg')
  );
  console.log('✅ nagi: 4-3.jpg → 4-2.jpg');
}

console.log('\n步骤2: 补全缺失的图片');

// 遍历每个角色
characters.forEach(character => {
  const charDir = path.join(imgDir, character);
  console.log(`\n处理角色: ${character}`);

  // 获取该文件夹中所有符合格式的图片
  const allFiles = fs.readdirSync(charDir);
  const validImages = allFiles.filter(file => {
    const match = file.match(/^(\d+)-(\d+)\.(jpeg|jpg|png)$/);
    return match && parseInt(match[1]) >= 1 && parseInt(match[1]) <= 4;
  });

  if (validImages.length === 0) {
    console.log(`  ⚠️ 没有找到有效的源图片，跳过`);
    return;
  }

  console.log(`  找到 ${validImages.length} 张有效源图片`);

  // 补全每个等级的图片 (1-7, 每级0-2三张)
  for (let level = 1; level <= 7; level++) {
    for (let index = 0; index <= 2; index++) {
      // 检查是否已存在任意格式的图片
      let exists = false;
      for (let ext of extensions) {
        const targetFile = `${level}-${index}.${ext}`;
        if (fs.existsSync(path.join(charDir, targetFile))) {
          exists = true;
          break;
        }
      }

      // 如果不存在，随机选一张复制
      if (!exists) {
        const randomImage = validImages[Math.floor(Math.random() * validImages.length)];
        const sourceExt = path.extname(randomImage).slice(1); // 去掉点号
        const targetFile = `${level}-${index}.${sourceExt}`;

        fs.copyFileSync(
          path.join(charDir, randomImage),
          path.join(charDir, targetFile)
        );
        console.log(`  ✅ 创建 ${targetFile} (来源: ${randomImage})`);
      }
    }
  }
});

console.log('\n=== 图片整理完成 ===');
