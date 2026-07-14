# LiftLog 🪵

## What this is

A personal trainer agent that lives in whatever chat app you already use. Meet your trainer before you ever get to the gym — a casual conversation about you, your goals, and how hard you want to be pushed. It builds your program, tracks your progress, adjusts over time, and coaches you between sets when you need it. You just show up and lift.

It's an expert in exercise — knows form, technique, how to program around lifts. It infers exercises from context and confirms when unsure. It adapts to how you want to use it: log silently and review later, ask for step-by-step guidance, or anything in between. It knows how hard to push you based on who you are, not a formula. It handles bad days by understanding the person.

## Who it's for

People who want a great workout but don't want to have to think about it. Some want to answer questions up front, some want to say "just make me stronger," some want to just start lifting and have it figure it out. The agent meets you wherever you are.

Starts as a personal tool, becomes a product if it works.

## Key decisions

- **The agent is an expert.** It knows form, technique, exercise selection, how to program around lifts. It infers from context and confirms when unsure. It doesn't need to be told what a bench press is.
- **It adapts to the person, not a template.** How hard to push, how to handle a bad day, whether to proactively tell you the next set or stay quiet — all based on who you are and what you need that day.
- **The interaction style is yours.** Log silently and talk after. Ask step-by-step what to do. Or anything in between or outside that. Same agent, different modes.
- **Everything is logged and retrievable.** The technical format is a build decision, but the data is yours and it persists.
- **It lives in any chat app where an agent lives.** Not just Telegram — wherever you already are.
- **Best-in-class by default.** The agent should be like being matched with the perfect personal trainer for you and your goals — not a generic workout app.

## MVP scope

**In:**
- Agent that meets you in conversation, learns your goals and preferences
- Program building — from questions, from a goal, or from observing what you do
- Workout logging — log sets, reps, weight via chat
- Progress tracking — sees trends, plateaus, progression over time
- Between-set coaching — when you need it, the agent responds
- Bad day handling — adapts to the person, not a rule
- Exercise expertise — form, technique, programming, infers from context
- Adaptive interaction — silent logging, step-by-step guidance, or anything between
- Everything logged and retrievable

**Out:**
- Rep-by-rep coaching (at least initially — no clear way to do that yet)
- A separate app — it lives in chat, not a new download
- Pre-built template programs — the agent builds your program, you don't pick from a list

## UX scenarios

1. **The casual start:** You're not at the gym. You message the agent for the first time. You have a conversation about working out — your goals, your experience, how hard you want to be pushed. The agent builds your first program. You go to the gym the next day knowing exactly what to do.

2. **The silent logger:** You're at the gym. You send "bench 225x8, 225x6, 225x5" between sets. The agent logs it, stays quiet, and adjusts next week's program based on how the set looked. You review the session after.

3. **The step-by-step:** You're at the gym and not sure what to do. You ask "what's next?" The agent tells you the exercise, weight, reps, and rest time. It explains form if you ask. You log what you actually did. It adjusts the next set if needed.

4. **The bad day:** You come in feeling off. You log a set and it's 20% below last week. The agent doesn't automatically drop the weight — it checks in with you, understands what's going on, and adjusts the session based on who you are and what you need.

## Open questions

- **Data format:** How is workout data stored? Plain text file, structured JSON, something else? The data needs to be retrievable and owned by the user.
- **Platform:** Which chat platforms first? Telegram is natural, but the agent should work anywhere an agent lives.
- **Exercise database:** Does the agent need a structured exercise database, or can it work purely from LLM knowledge of exercises, form, and technique?
- **Progression model:** How does the agent decide when to increase weight, volume, or intensity? Does it use a known progression model (linear progression, double progression, etc.) or infer its own approach?
