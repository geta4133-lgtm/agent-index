# Cara Dapet Uang dari Direktori Ini

Urutannya **wajib** begini. Nggak bisa dibalik.

```
SITUS  ->  TRAFFIC  ->  AUDIENCE  ->  UANG
  ok       belum        belum       belum
```

Situs tanpa visitor = Rp0. Jadi 80% kerjaan lo ke depan adalah **ngasih tau orang
kalau situs ini ada**.

---

## 1. Affiliate (bisa mulai hari ini, modal Rp0)

Situs ini nyebut 27 AI tool. Beberapa punya program affiliate yang bayar per signup.

**Cara aktifin:**

1. Daftar program di kolom `program` file `affiliates.json`.
2. Setelah di-approve, lo dapet link unik. Paste ke kolom `url` tool yang sama.
3. Jalanin `python3 pages4.py` lalu push. Selesai.

Link affiliate otomatis muncul di:
- tiap halaman detail use case yang pakai tool itu (78 halaman buat n8n)
- halaman `/tools` (27 baris tool, diurutkan berdasar pemakaian)

**Yang punya program (cek dulu, sering berubah):**

| Tool | Program | Catatan |
|---|---|---|
| n8n | n8n.io/affiliates | 78 use case di situs ini, paling banyak |
| Zapier | zapier.com/affiliate | recurring 20-30% |
| Make | make.com/en/affiliate-program | recurring |
| Lindy | lindy.ai/affiliates | AI assistant kantor |
| Replit | replit.com/refer | kredit per invite |

**Yang nggak punya affiliate:** Claude Code, ChatGPT, Devin, Copilot, GitHub.
Buat ini, monetisasinya lewat tutorial/konten, bukan link.

**Penting:** link affiliate wajib ada `rel="sponsored nofollow"` (udah otomatis)
dan harus ada disclosure (udah otomatis juga). Ini syarat Google + FTC.
Kalau nggak, bisa kena penalti SEO.

---

## 2. Auto-posting (mesin traffic)

### Telegram (gratis, jalan sekarang)

`post_telegram.py` — posting use case baru ke channel lo.

**Setup 3 langkah:**
1. Bikin channel Telegram (public, misal `@AIUseCasesID`).
2. Add bot `@Termuxkiritobot` sebagai **admin** channel (perlu izin post).
3. Isi di `social.json`:
   ```json
   "tg_token": "<token bot>",
   "tg_chat": "@namachannel"
   ```
4. Test: `python3 post_telegram.py`
5. Kalau jalan, masukin ke `daily.sh` biar otomatis.

Bot udah dites jalan (`sent 1, failed 0`). Antriannya 1.273 item, gak akan ngulang.

### X / Twitter (paling powerful, butuh API key)

`post_x.py` — auto-tweet, format udah di-budget pas **<= 280 char** (link dihitung 23 char).

**Setup:**
1. Daftar developer.x.com (free tier: ~500 post/bulan).
2. Bikin Project -> ambil 4 value: consumer key/secret, access token/secret.
   Pastikan app punya **write** permission.
3. Isi di `social.json`:
   ```json
   "x_consumer_key": "...", "x_consumer_secret": "...",
   "x_access_token": "...", "x_access_secret": "..."
   ```
4. Test: `python3 post_x.py`

Kenapa X penting: sumber aslinya (agentusecases.ai) dapet 238 dari 486 sumber dari X.
X itu mesin traffic-nya, bukan SEO.

---

## 3. Sponsor (target utama)

Sumber aslinya jual sponsor **$700/minggu** (naik $100 tiap ada sponsor baru).

**Kapan mulai jual:** setelah ada ~2.000 follower X atau 5.000 visitor/bulan.
Jangan lebih awal, sponsor bakal nolak kalau angka-nya belum ada.

**Cara aktifin di situs:**
```python
# gen.py, bagian CFG
"sponsor": {"name": "NamaSponsor", "pitch": "Apa yang mereka jual",
            "url": "https://link-sponsor", "live": True},
"sponsor_price": "$190",
```
`live: True` -> sponsor bar muncul di 1.300+ halaman.

**Pitch ke calon sponsor (kirim DM/email):**
> Halo, saya punya direktori berisi {N} use case AI agent nyata, dibaca {X} orang/bulan,
> mayoritas builder & operator. Saya buka 3 slot sponsor untuk kuartal ini,
> {harga}/minggu. Mau saya kirim media kit-nya?

---

## 4. Newsletter

Form newsletter udah nempel di setiap halaman. Sekarang masih lokal (`#`).

**Cara jadiin beneran:**
1. Daftar Buttondown atau MailerLite (gratis sampai 1.000 subscriber).
2. Ambil endpoint form-nya.
3. Set di `gen.py`:
   ```python
   "newsletter_action": "https://buttondown.email/api/emails/embed-subscribe/namalo",
   ```
4. Rebuild + push.

Nilai: 1.000 subscriber = $100-300/bulan dari iklan newsletter.

---

## 5. Jual situsnya (exit)

Direktori dengan traffic stabil laku di **Flippa / Acquire.com**: 30-40x profit bulanan.

Contoh: profit $200/bulan -> laku **$6.000-8.000** (~Rp100 juta).
Kuncinya traffic stabil + revenue tercatat rapi.

---

## Rencana 30 Hari

**Minggu 1**
- [ ] Daftar 3 program affiliate (n8n, Zapier, Make)
- [ ] Bikin channel Telegram + aktifin auto-posting
- [ ] Daftar developer.x.com + aktifin auto-tweet

**Minggu 2-4**
- [ ] Posting 3-5 use case/hari (otomatis lewat cron)
- [ ] Balas tiap reply/mention di X (manual, penting)
- [ ] Cek analytics tiap minggu

**Target hari ke-30:** 500 follower, 5.000 visitor/bulan.
Kalau kena -> baru mulai jual sponsor.

---

## Analytics

Isi di `gen.py`:
```python
"analytics": {"provider": "goatcounter", "code": "namalo"},
```
Support: `goatcounter` (gratis), `cloudflare`, `plausible`.

GoatCounter: daftar di goatcounter.com, pilih subdomain, isi kodenya.
Nanti keliatan visitor per halaman -> tau konten mana yang paling laku.

---

## Yang JANGAN dilakuin

- Jangan beli follower atau pakai bot engagement. X bakal nge-ban.
- Jangan taruh affiliate link tanpa disclosure. Kena penalti Google + ilegal (FTC).
- Jangan jual sponsor sebelum ada angka. Bakal ditolak + susah balik lagi.
- Jangan spam DM ke calon sponsor. Satu pesan, sopan, kasih angka.