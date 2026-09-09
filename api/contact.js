import { supabase, resend, TEAM, FROM, SITE, clean, isEmail, meta, methodGuard, rateLimited, row, shell, confirmation, esc } from './_lib.js';

const AUDIENCE = { lab: 'Model lab', robot: 'Robotics company', hardware: 'AI hardware', supplier: 'Supply chain', investor: 'Investor', other: 'Other' };
const NEEDS = { data: 'Data', supply: 'Supply chain', prod: 'Production', motion: 'Motion Infra', compliance: 'Compliance', invest: 'Investment', other: 'Other' };

export default async function handler(req, res) {
  if (!methodGuard(req, res)) return;
  const m = meta(req);
  if (rateLimited(m.ip)) return res.status(429).json({ error: 'Too many requests. Try again later.' });

  const b = req.body || {};
  const rec = {
    audience: clean(b.audience, 40) || null,
    needs: Array.isArray(b.needs) ? b.needs.map(x => clean(x, 40)).filter(Boolean).slice(0, 10) : [],
    name: clean(b.name, 200), company: clean(b.company, 200) || null, email: clean(b.email, 200),
    role: clean(b.role, 200) || null, website: clean(b.website, 500) || null, linkedin: clean(b.linkedin, 500) || null,
    brief: clean(b.brief) || null, timeline: clean(b.timeline, 200) || null, budget: clean(b.budget, 200) || null,
    page: clean(b.page, 200) || null, ...m,
  };
  if (!rec.name || !isEmail(rec.email)) return res.status(400).json({ error: 'Name and a valid email are required.' });

  let id = null;
  try {
    const { data, error } = await supabase().from('contact_requests').insert(rec).select('id').single();
    if (error) throw error; id = data.id;
  } catch (err) {
    console.error('[contact] supabase', err);
    return res.status(500).json({ error: 'Could not save your request.' });
  }

  const rs = resend();
  if (rs) {
    const needsLabel = rec.needs.map(n => NEEDS[n] || n).join(', ');
    const rows = [
      row('Audience', AUDIENCE[rec.audience] || rec.audience), row('Needs', needsLabel),
      row('Name', rec.name), row('Company', rec.company), row('Email', rec.email), row('Role', rec.role),
      row('Website', rec.website), row('LinkedIn', rec.linkedin), row('Brief', rec.brief), row('Timeline', rec.timeline), row('Budget', rec.budget),
    ].join('');
    const subject = `[Contact] ${AUDIENCE[rec.audience] || 'Inquiry'} · ${rec.company || rec.name}`;
    try {
      await rs.emails.send({ from: FROM, to: TEAM, replyTo: rec.email, subject, html: shell('New contact request', rec.company || rec.name, needsLabel, rows, `Supabase id ${id} · ${new Date().toISOString()}`) });
      await rs.emails.send({ from: FROM, to: rec.email, subject: 'We received your request — FOUNTAIN', html: confirmation(rec.name.split(' ')[0], `We received your request and will reply within <strong>two business days</strong>. If anything changes, just reply to this email.`) }).catch(e => console.warn('[contact] confirm', e));
    } catch (err) { console.warn('[contact] resend', err); }
  }
  return res.status(200).json({ ok: true, id });
}
