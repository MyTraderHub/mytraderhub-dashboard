require('dotenv').config();

const express = require('express');
const cors = require('cors');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
const PORT = process.env.PORT || 3000;
const MODEL = 'claude-3-5-sonnet-20241022';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const CHAT_SYSTEM_PROMPT = `You are the virtual assistant for Nexus AI, an AI automation agency that helps businesses save 20+ hours per week through intelligent automation.

Your role:
- Answer questions about Nexus AI's three core services: Automated Lead Engagement, Content Repurposing Pipelines, and Custom AI Chatbots.
- Be concise, friendly, and professional. Keep responses under 3 short paragraphs.
- Highlight concrete benefits: time saved, faster lead response, scalable content output, and 24/7 availability.
- If asked about pricing, explain that every project is scoped individually and encourage booking a free audit via the contact form.
- If you don't know something specific, say so honestly and offer to connect them with the team.
- Never pretend to be a human. Never share made-up case studies or client names.
- Do not provide legal, medical, or financial advice.`;

app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.post('/api/leads', async (req, res) => {
  try {
    const { name, email, website } = req.body;

    if (!name || !email || !website) {
      return res.status(400).json({
        error: 'Missing required fields: name, email, website',
      });
    }

    if (!process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY === 'your-api-key-here') {
      return res.status(500).json({ error: 'ANTHROPIC_API_KEY is not configured' });
    }

    const response = await anthropic.messages.create({
      model: MODEL,
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `Draft a personalized outreach email for a prospective client with the following details:

Name: ${name}
Email: ${email}
Website: ${website}

Requirements:
- Warm, professional tone suitable for a B2B AI automation agency
- Reference their website domain to show we've done our homework
- Briefly mention how Nexus AI can help them save 20+ hours per week
- Include a clear call-to-action to schedule a free automation audit
- Keep it under 200 words
- Return only the email body (no subject line, no metadata)`,
        },
      ],
    });

    const emailDraft = response.content
      .filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('\n');

    res.json({
      success: true,
      lead: { name, email, website },
      emailDraft,
    });
  } catch (error) {
    console.error('POST /api/leads error:', error.message);
    res.status(500).json({ error: 'Failed to generate outreach email' });
  }
});

app.post('/api/chat', async (req, res) => {
  try {
    const { message, history = [] } = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Missing required field: message' });
    }

    if (!process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY === 'your-api-key-here') {
      return res.status(500).json({ error: 'ANTHROPIC_API_KEY is not configured' });
    }

    const messages = [
      ...history
        .filter((entry) => entry.role === 'user' || entry.role === 'assistant')
        .map((entry) => ({ role: entry.role, content: entry.content })),
      { role: 'user', content: message },
    ];

    const response = await anthropic.messages.create({
      model: MODEL,
      max_tokens: 512,
      system: CHAT_SYSTEM_PROMPT,
      messages,
    });

    const reply = response.content
      .filter((block) => block.type === 'text')
      .map((block) => block.text)
      .join('\n');

    res.json({ reply });
  } catch (error) {
    console.error('POST /api/chat error:', error.message);
    res.status(500).json({ error: 'Failed to process chat message' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
