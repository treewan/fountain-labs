// Shared helpers for /api/contact and /api/apply
import { createClient } from '@supabase/supabase-js';
import { Resend } from 'resend';

export const TEAM = (process.env.TEAM_RECIPIENTS || 'tree@fountainbuild.ai,miki@fountainbuild.ai').split(',').map(s => s.trim()).filter(Boolean);
export const FROM = process.env.FROM_EMAIL || 'FOUNTAIN <onboarding@resend.dev>';
export const SITE = process.env.SITE_URL || 'https://fountainbuild.com';

export function supabase() {
  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error('Supabase not configured');
  return createClient(url, key, { auth: { persistSession: false } });
}
export function resend() {
  const key = process.env.RESEND_API_KEY;
  return key ? new Resend(key) : null;
}

export const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
export const isEmail = s => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(s || '').trim());
export const clean = (s, max = 4000) => String(s ?? '').trim().slice(0, max);

export function meta(req) {
  return {
    user_agent: clean(req.headers['user-agent'], 500) || null,
    ip: (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || null,
  };
}

export function methodGuard(req, res) {
  if (req.method === 'OPTIONS') { res.status(204).end(); return false; }
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); res.status(405).json({ error: 'Method not allowed' }); return false; }
  return true;
}

// Minimal in-memory rate limit per warm instance (belt-and-braces; Vercel WAF is the real guard).
const hits = new Map();
export function rateLimited(ip, limit = 5, windowMs = 10 * 60 * 1000) {
  if (!ip) return false;
  const now = Date.now(); const arr = (hits.get(ip) || []).filter(t => now - t < windowMs);
  arr.push(now); hits.set(ip, arr);
  return arr.length > limit;
}

export function row(label, value) {
  const v = value && String(value).trim() ? esc(value) : '<span style="color:#999">—</span>';
  return `<tr><td style="padding:8px 14px;border-bottom:1px solid #eee;color:#666;font-size:12px;letter-spacing:.04em;text-transform:uppercase;width:180px;vertical-align:top">${esc(label)}</td><td style="padding:8px 14px;border-bottom:1px solid #eee;color:#111;font-size:14px;line-height:1.6;white-space:pre-wrap">${v}</td></tr>`;
}
export function shell(eyebrow, title, sub, rows, footer) {
  return `<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#FCFCFB;padding:32px 0;color:#111"><table role="presentation" cellpadding="0" cellspacing="0" border="0" style="max-width:680px;margin:0 auto;background:#fff;border:1px solid #E6E6E2"><tr><td style="padding:28px 24px;border-bottom:1px solid #111"><div style="font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#1E48D8;font-weight:600">${esc(eyebrow)}</div><div style="margin-top:8px;font-size:22px;font-weight:600">${esc(title)}</div>${sub ? `<div style="margin-top:6px;font-size:13px;color:#55554F">${esc(sub)}</div>` : ''}</td></tr><tr><td><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse">${rows}</table></td></tr><tr><td style="padding:18px 24px;border-top:1px solid #E6E6E2;color:#8A8A85;font-size:11px;letter-spacing:.1em;text-transform:uppercase">${esc(footer)}</td></tr></table></div>`;
}
export function confirmation(firstName, body) {
  return `<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#FCFCFB;padding:40px 0;color:#111"><table role="presentation" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E6E6E2;padding:40px 32px"><tr><td><div style="font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#1E48D8;font-weight:600">FOUNTAIN</div><h1 style="margin:20px 0 16px;font-size:24px;font-weight:600;line-height:1.3">Thanks, ${esc(firstName)}.</h1><p style="margin:0 0 18px;font-size:15px;line-height:1.65;color:#3A3A38">${body}</p><hr style="border:none;border-top:1px solid #E6E6E2;margin:28px 0"><p style="margin:0;font-size:13px;line-height:1.6;color:#8A8A85">FOUNTAIN · Physical AI infrastructure<br>Silicon Valley · Shenzhen · Singapore · <a href="${SITE}" style="color:#1E48D8;text-decoration:none">${SITE.replace(/^https?:\/\//, '')}</a></p></td></tr></table></div>`;
}
