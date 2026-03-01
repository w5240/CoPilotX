# Bundled Skills

此目录存放预打包的私有skill，会在应用首次启动或版本更新时自动复制到 `~/.openclaw/skills/` 目录。

## 目录结构

```
bundled-skills/
├── .version              # 版本标记文件
├── my-skill-1/          # 你的私有skill
│   ├── .exclusive        # 专属技能标记文件（可选）
│   ├── skill.json
│   ├── index.ts
│   └── ...
└── my-skill-2/
    └── ...
```

## 专属技能

在技能目录中创建 `.exclusive` 空文件，可以将该技能标记为"专属"：

- 专属技能会在 Skills 页面的"专属"分类中单独显示
- 专属技能有特殊的图标标识（✨）
- 专属技能不支持删除操作
- 专属技能不会显示在"内置"和"市场"分类中

## 版本管理

修改 `.version` 文件内容会触发重新复制所有skill（即使已存在）。

## 注意事项

- 已存在的skill不会被覆盖（保护用户修改）
- 删除 `~/.openclaw/skills/.bundled-skills-version` 可强制重新复制
- Skill会被复制到 `~/.openclaw/skills/` 目录
- 专属技能仍然会被复制到 `~/.openclaw/skills/`，以便 OpenClaw Gateway 可以加载和使用