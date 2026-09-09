import { supabase, resend, TEAM, FROM, clean, isEmail, meta, methodGuard, rateLimited, row, shell, confirmation } from './_lib.js';

const STAGE = { idea: 'Idea', proto: 'Prototype', users: 'Early users', shipped: 'Shipped' };
const APPLY_TO = (process.env.APPLY_RECIPIENTS || '').split(',').map(s => s.trim()).filter(Boolean);

export default async function handler(req, res) {
  if (!methodGuard(req, res)) return;
  const m = meta(req);
  if (rateLimited(m.ip, 3)) return res.status(429).json({ error: 'Too many requests. Try again later.' });

  const b = req.body || {};
  const rec = {
    name: clean(b.name, 200), email: clean(b.email, 200), linkedin: clean(b.linkedin, 500) || null, location: clean(b.location, 200) || null,
    company: clean(b.company, 200) || null, website: clean(b.website, 500) || null, one_liner: clean(b.oneLiner, 500) || null,
    pitch: clean(b.pitch) || null, deck_link: clean(b.link, 500) || null, demo_link: clean(b.demo, 500) || null,
    why: clean(b.why) || null, source: clean(b.source, 300) || null, stage: clean(b.stage, 40) || null,
    page: clean(b.page, 200) || null, ...m,
  };
  if (!rec.name || !isEmail(rec.email)) return res.status(400).json({ error: 'Name and a valid email are required.' });

  let id = null;
  try {
    const { data, error } = await supabase().from('applications').insert(rec).select('id').single();
    if (error) throw error; id = data.id;
  } catch (err) {
    console.error('[apply] supabase', err);
    return res.status(500).json({ error: 'Could not save your application.' });
  }

  const rs = resend();
  if (rs) {
    const rows = [
      row('Name', rec.name), row('Email', rec.email), row('LinkedIn', rec.linkedin), row('Location', rec.location),
      row('Company', rec.company), row('Website', rec.website), row('One-liner', rec.one_liner), row('Pitch', rec.pitch),
      row('Deck', rec.deck_link), row('Demo', rec.demo_link), row('Stage', STAGE[rec.stage] || rec.stage), row('Why FOUNTAIN', rec.why), row('Heard via', rec.source),
    ].join('');
    const subject = `[Apply] ${rec.company || rec.name} · ${STAGE[rec.stage] || 'Stage n/a'}`;
    try {
      await rs.emails.send({ from: FROM, to: APPLY_TO.length ? APPLY_TO : TEAM, replyTo: rec.email, subject, html: shell('New accelerator application', rec.company || rec.name, rec.one_liner, rows, `Supabase id ${id} · ${new Date().toISOString()}`) });
      await rs.emails.send({ from: FROM, to: rec.email, subject: 'We received your FOUNTAIN application', html: confirmation(rec.name.split(' ')[0], `We received your application${rec.company ? ` for <strong>${rec.company}</strong>` : ''} and will respond within <strong>one week</strong>, with an invite to a first call or with substantive feedback. If anything changes, reply to this email.`) }).catch(e => console.warn('[apply] confirm', e));
    } catch (err) { console.warn('[apply] resend', err); }
  }
  return res.status(200).json({ ok: true, id });
}
