# LiftLog

Workout smarter and harder.

A personal trainer agent that lives in your chat. It builds your program, tracks your progress, coaches you between sets, and adapts to who you are. You just show up and lift.

## How it works

1. **Meet your trainer** — a casual conversation about your goals, your experience, and how hard you want to be pushed
2. **Lift** — log your sets, ask what's next, or just lift and review later. The agent adapts to how you want to use it
3. **Get better** — the agent tracks progress, spots plateaus, adjusts your program, and coaches you when you need it

## What makes it different

- **It's an expert.** Knows form, technique, exercise selection, and how to program around lifts. Infers exercises from context.
- **Adapts to you.** How hard to push, how to handle a bad day, whether to proactively coach or stay quiet — based on who you are, not a template.
- **Lives in your chat.** Not a new app. Telegram, Discord, wherever your agent lives. You already have it open at the gym.
- **Your data is yours.** Plain text files you own. Works without the tool.

## Get started

Two ways in. Whatever you're already using.

**Agent users** (Hermes, Claude Code, Cursor, Codex, OpenCode):
```bash
npx skills add buckZz7/liftlog
```

**ChatGPT / Claude chat / any LLM:** Copy the prompt from [the website](https://buckzz7.github.io/liftlog/#get) and paste it in.

## Project structure

```
liftlog/
├── SKILL.md          # The personal trainer protocol — the product
├── NAPKIN.md         # Project vision
├── docs/
│   └── index.html    # Landing page
└── LICENSE           # MIT
```

## License

MIT
