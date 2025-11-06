$characters = @('linzixi', 'xuejian', 'nagi', 'shiyu', 'zoe', 'kevin')
$levels = @('_stranger', '_acquaintance', '_friend', '_close_friend', '_special', '_romantic', '_lover')

foreach ($char in $characters) {
  $baseFile = "$char.png"
  if (Test-Path $baseFile) {
    Write-Host "处理角色: $char"
    foreach ($level in $levels) {
      $targetFile = "$char$level.png"
      if (-not (Test-Path $targetFile)) {
        Copy-Item $baseFile $targetFile
        Write-Host "  ✓ 已创建: $targetFile"
      } else {
        Write-Host "  - 已存在: $targetFile"
      }
    }
  } else {
    Write-Host "⚠ 找不到基础头像: $baseFile"
  }
}

Write-Host "`n完成！所有角色的等级头像已创建。"
