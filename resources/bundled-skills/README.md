# Bundled Skills

此目录存放预打包的私有skill，会在应用首次启动或版本更新时自动复制到 `~/.openclaw/skills/` 目录。

## 目录结构

```
bundled-skills/
├── .version              # 版本标记文件
├── my-skill-1/          # 你的私有skill
│   ├── skill.json
│   ├── index.ts
│   └── ...
└── my-skill-2/
    └── ...
```

## 版本管理

修改 `.version` 文件内容会触发重新复制所有skill（即使已存在）。

## 注意事项

- 已存在的skill不会被覆盖（保护用户修改）
- 删除 `~/.openclaw/skills/.bundled-skills-version` 可强制重新复制
- Skill会被复制到 `~/.openclaw/skills/` 目录