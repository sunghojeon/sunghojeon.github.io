---
layout: page
permalink: /broadcast-rtk/
title: Broadcast RTK (eGPS)
hide_page_title: true
---

<section class="page-intro">
  <h1 class="page-title">Broadcast RTK <span class="ko-gloss">eGPS · enhanced GPS</span></h1>
  <p class="page-subtitle">The world's first commercial centimeter-level positioning service delivered over terrestrial broadcast networks — 방송망 기반 세계 최초 cm급 정밀측위 상용 서비스.</p>
</section>

## Why broadcast?

RTK (Real-Time Kinematic) positioning needs a continuous stream of GNSS correction data. Today that stream is delivered almost exclusively over cellular unicast (NTRIP): every receiver opens its own connection, so cost and network load grow linearly with the number of users, and coverage follows the cellular grid.

A terrestrial broadcast network inverts that economics. One transmitter delivers the same correction stream to an **unlimited number of receivers** — vehicles, drones, IoT sensors — with no per-device connection, no congestion, and coverage engineered for reception at the edge of the service area. Combined with LTE/5G as a return and infill channel, the two networks hedge each other's outages: where cellular shadows, broadcast fills, and vice versa.

**Broadcast RTK** puts this into commercial practice: a hybrid architecture combining nationwide GNSS reference stations, DMB and ATSC 3.0 broadcast delivery, and LTE/5G — providing centimeter-level accuracy while cutting cellular data cost by ~98%. Its global service brand is **eGPS (enhanced GPS)**.

![Broadcast RTK — ATSC 3.0-based precise PNT infrastructure](/images/talks/2026-bje-tta-special.webp)

## Key facts

<div class="svc">
  <div class="svc-item"><span class="svc-label">Accuracy — centimeter-level (RTK fixed) via broadcast-delivered corrections</span></div>
  <div class="svc-item"><span class="svc-label">Infrastructure — ~100 GNSS reference stations nationwide, delivered over DMB &amp; ATSC 3.0 with LTE/5G hybrid</span></div>
  <div class="svc-item"><span class="svc-label">Economics — ~98% reduction in cellular data cost versus NTRIP unicast</span></div>
  <div class="svc-item"><span class="svc-label">Validation — 137,480 samples / 38.19 hours of cross-validation across four regions (Seoul–Gangneung, DC/Baltimore, Denver, Salt Lake City), demonstrating a bidirectional tail-risk hedge between broadcast and cellular</span></div>
  <div class="svc-item"><span class="svc-label">Global expansion — U.S. (EdgeBeam), India (D2M), Brazil (TV 3.0 / DTV+)</span></div>
  <div class="svc-item"><span class="svc-label">Applications — AI road-hazard sensing buses, geofencing, low-power IoT facility monitoring, drone operations</span></div>
</div>

## Milestones

<div class="cv-timeline">
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">July 2026</span></div>
    <div class="cv-entry">
      <div class="cv-role">Three papers at IEEE BMSB 2026 <span class="cv-rank">João Pessoa, Brazil</span></div>
      <div class="cv-detail">Coverage &amp; outage bounding in hybrid ATSC 3.0/LTE RTK delivery · end-to-end latency for emergency alerting · nationwide time sourcing (BPS)</div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">June 2026</span></div>
    <div class="cv-entry">
      <div class="cv-role">KIBME Summer Conference — RAPA &amp; TTA special sessions</div>
      <div class="cv-detail"><a href="/BJE-Summer-TTA-RAPA-Special-Sessions/">Next-gen broadcast architecture (B2X, ATSC TG3/S44) and ultra-precise PNT infrastructure over ATSC 3.0</a></div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">May 2026</span></div>
    <div class="cv-entry">
      <div class="cv-role">KOBA 2026 Media Conference</div>
      <div class="cv-detail"><a href="/KOBA2026_Conference/">BPS and Broadcast RTK (eGPS) development trends</a> — four-region validation results published</div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">April 2026</span></div>
    <div class="cv-entry">
      <div class="cv-role">NAB Show 2026 — eGPS live demonstration <span class="cv-rank">Las Vegas</span></div>
      <div class="cv-detail"><a href="/NAB2026/">Korea broadcast-technology pavilion (RAPA)</a> — ATSC 3.0 cm-level positioning demo; BPS/Broadcast-PNT rises on the NextGen TV agenda</div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">February 2026</span></div>
    <div class="cv-entry">
      <div class="cv-role">ATSC IT-5 presentation — drone-based antenna verification</div>
      <div class="cv-detail"><a href="/ATSC-IT5-Drone-Measurement/">Field verification of DTV antenna patterns using RTK-equipped drones</a></div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">October 2025</span></div>
    <div class="cv-entry">
      <div class="cv-role">TTA Technical Report TTAR-07.0048</div>
      <div class="cv-detail"><a href="/TTAR-07-0048/">Drone-based field verification of terrestrial DTV antenna patterns</a> — measurement infrastructure underpinning broadcast-PNT deployment</div>
    </div>
  </div>
  <div class="cv-row">
    <div class="cv-period"><span class="cv-period-start">November 2023</span></div>
    <div class="cv-entry">
      <div class="cv-role">ITS Korea Fall Conference — ATSC 3.0 vehicle infotainment session</div>
      <div class="cv-detail"><a href="/ITS_2023_Fall_Conference/">cm-level ATSC 3.0-based RTK introduced alongside D2V field tests</a></div>
    </div>
  </div>
</div>

## In the news

<!-- NEWS-TIMELINE:START -->
<p class="page-subtitle">ATSC 3.0 · DTV+ (TV 3.0) · Broadcast RTK · EdgeBeam — auto-collected news since June 01, 2026 (last updated 2026-07-04).</p>
<ol class="timeline">
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiowFBVV95cUxOY2JxbWVMT3BraDBVLWVwYmZkM3hVYzB4MUJST0JlTVY2N3pOTUpjRVpLN25lWVBMdm5kM2ZxWmMySXBRMlZvRlh5N29ScnlPUzg4TW5mbnJHLXRYbHEtLTNBel95MlFSNDl6OVk2cDR0OElUV29KcWpwNHloVmxiSE1jakhCeW93Vjk3ZktvR010T21mVE9wczVJMDdfRFN5N25R?oc=5" target="_blank" rel="noopener">TV 3.0: Globo terá integração com aplicativos de celulares em tempo real</a> <span class="tl-cat">TudoCelular.com · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMic0FVX3lxTE1oNHBWMjZfOFNSMFl6eDREeWVTamV4TXNFVlJPcmllTE5FR2hrN3F4VlN3Y2gwUElBV01WYm5lOGJLLTBPYWRkcFVrRy1SMWk0dGZ4QjJXdm9iTjJvcko2R0xoZDZ3UDJ0X3hpbjVBNWFkNDA?oc=5" target="_blank" rel="noopener">DTV+ da Globo terá interação personalizada com apps móveis</a> <span class="tl-cat">Mobile Time · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiogFBVV95cUxQUC0wR1ZyTWI1cjhEU2Z4b1IxOEZrc1JVbVZPU1BRTHZYTGs2cGppaTVNcmM1cVh4Tl9NZVd3ZTk4UXh2UUozc0JJM2VKa1hqR1I4bElpVnRCTDRPOEhqd3pmSjJyY0F2RV9QcWxybmJ4c2NVejk1S2QzYThNdHA2Mk1Zd3RocjB5VWxVak5qX214X2tiYmluRnE5a0ktMU40c3c?oc=5" target="_blank" rel="noopener">SET Expo 2026 revela primeiros painéis sobre IA, streaming e TV 3.0</a> <span class="tl-cat">jwave.com.br · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMilwFBVV95cUxOOHVWT00wMk9meVRvRTMtSXQzTFY0Y0JEWDZGMjJUSjhMajRWWS1pX0hfb3lMTzZHeUlEWFA5bnBDX1hRaUhXS190Y0xFY2lfd3RvSjRybl9PNUJVbW9RLW5DNkJsRDhaUWVORHdQNVplR1hsT0Q3T25QeUh5YlNYQWVwQy1kZWdZa3JWaFBSUVlTN2RaQnFB?oc=5" target="_blank" rel="noopener">EBC Lança TV 3.0: Uma Nova Era para a Comunicação Pública no Brasil</a> <span class="tl-cat">Metrô News Jornal · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMigAFBVV95cUxNekxnREV5Vk1RNUkwd1lwdEE5SURiTy1EMGVoMmpaRzAtcC0xSDAtX0V4ZmFyWXROQkFwZG9JX2tGUmd0NEFUYzliQUFWbnd0OEEtUFVnajlHWjlPSnRRY2NLUEVmWXZreFh3aDlNWENLdjlYaTlRY0Q5WmtHUmZTcA?oc=5" target="_blank" rel="noopener">Anatel aprova reorganização do espectro para viabilizar a TV 3.0</a> <span class="tl-cat">DPL News · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiugFBVV95cUxQWFVJVDNwblVKaVlYOXRreGlwbDZXbHBSYnJhZ1pXS0V5MDlKdkVkd0hWV3l6MmgwckVqYlpoMDVqRktOUllkNnRBQWxFZXM3WlgxMEh0RER5Y3g5V1JlaG00MnloNk0yeDNYbmYtLVhBZkNZODY5bE1VcUdPVm92QVdxdzdzRUNjQXA1alhPbE41QTZFSE1KSFdTWlVKbFQwSEZHQVB0VTM1d1l0U3NMaUFLb3NKWVpEdUE?oc=5" target="_blank" rel="noopener">TV Tarobá lança nova programação e aposta em interatividade e TV 3.0</a> <span class="tl-cat">Tarobá · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMingFBVV95cUxNZjZPbV9DaUlrbDBzSkpLaU9XeURZSnJqQU5WZGF1aGR1SzQ1QWIyOGVfZ2tIYjhQdUlnNllFWHU1QmExWWlCb1FjTVRmb2JxSHlFLTY4c3EyVmNVQmdjWVJoYW1OTndNZEJyVEZVOFBiZXBQRHowOE1EXy1YM1ZhSlczLUg5aWMzZFlrQVdYckdiaThBUDNXX3JfUFZ6UQ?oc=5" target="_blank" rel="noopener">TV 3.0 permitirá usar gov.br e SUS Digital pela televisão</a> <span class="tl-cat">Poder360 · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiiAFBVV95cUxQUmRFNjBlUkc2c0lUTkJ2VExaSmpsYVV2ZFBma1RvTzJuTG9Md0h4Vno1VHF5dEdvWEphRm9NWFNNaHhXUDE0M3c1VktXT0JVOUlBa1lQTkNNRlBMNFJ0MjRfNmV1d1lkcVZVYzV6UkFzenhZdDFsZUx5Zlg5UEJUWUpOT0E1OWJS?oc=5" target="_blank" rel="noopener">EBC lidera implementação da TV 3.0 para integrar serviços públicos e tecnologia</a> <span class="tl-cat">Fato Paulista · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMi0gFBVV95cUxOT0hpMktNZ1RaZ2Juc2F5ankyVERiSWFjcDd0ejlyeGtCOEVKQmZ2M1hOOHhjckd1akV6bnNUTGdsZjNGVHlJclVoWVRMSWQ1Zld1ZklfMVFsdi05STlhaTRvV0lsZnI3bHBSWG05VHJrbzNDbElkYmxHQ3VfWjNoM2NoemkwTVp0OWloUmpCanZicGc2b01mckNoUjg1eUR6OGRRSm9SNnFmRlEyMW85RXlOc21kaG5HVUVDS1F5c1VrZFhFb3lZSEFncV9kMUFRaWc?oc=5" target="_blank" rel="noopener">Jericho Receivers Unveils Software-Defined Atomic Clock With ATSC 3.0/BPS Source Support</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMirAFBVV95cUxOSE5IckprUkJ5Q21YM3VwVFhjWDNYSmZ1ZFo2Qzc4RU9vS002UXk2Mm9vQ1NVaF9ZTE15anFFSE5qOTFUdl80UjE3WmhmYkZwNUptLV9tSFlUSUFkMlZvcGpfWTVfT2RDVG5lZlVGRUFLbVRPSkR5eHlJTkRJdlFPd0lzNHFqVzdnN0d2SWJLYUR5OS1raU5zaGhQSUhCemZlaHZjcWlRRTVHWkpr?oc=5" target="_blank" rel="noopener">TV 3.0 passa por "ajustes" antes de lançamento oficial no Brasil, diz ministro</a> <span class="tl-cat">Canaltech · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiuwFBVV95cUxNUTZfcTdiQlBhOXpTOUN3dDVEMWQ5Z3BabVpsbTJzWFVBNHRRWDN6YnNKTnZTbVZycUFVemZ6S2V3WEFiVlFmbXFWQlJ4RGdkX3VYUXdDM1JfcXktaEJRTnhHY1JKQlpKSzZfOG4tTGxrclNuZndNUXk5elFvb0dwbHNpR2tnYlA5dW5zU0U4YnlSdkNETmJCbmNQQzFHRDhqeDgxSTBYTV85a2U1ck41VU1HZEEwN2tPSFFr?oc=5" target="_blank" rel="noopener">TV 3.0 começa a chegar ao Brasil e amplia integração entre televisão e serviços digitais</a> <span class="tl-cat">Capital Digital · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMimgFBVV95cUxQcUlDNWV4b0c3Vk1fX3N3aXJYb1A1Mi1EVHVheXI4X3JpTDFEeWdpSmhTM2ZUUWFTaFZNa2NVb0hXUkRLRmdQajVVUlVhaWFaSzRaWWo4NmZlNVhnWnJYOVdLTWVieXg2dkhnM0FHZzdrT1d1Uk45czJxMmVmdTFkR2FXaVVzQy1VRlRIZ2U3UDBPTFRBb0hLMmN3?oc=5" target="_blank" rel="noopener">TV 3.0 vai sincronizar rádio e TV sem atraso, diz especialista</a> <span class="tl-cat">Canaltech · BR</span><div class="tl-date">2026.07.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMi6wFBVV95cUxQYUQxdzJyTWR1VWsweE56aTIwUkxHNXpHNHcwVkNqbFRkcHc2OTk2b3NCcVNmZEJCOU5QSjR5eUNPTTlNUGFJYlV1LTlESktTamJjelZBQTlDblRxRWdsQTRSU25VYklUNzVzamFOd3RZQmQweWh4MzZkdHJ0N3RGbUJMUi1ubnhVVW1ZMnFXb0QzeDFwN0FHN3dtbDEtRUgzQWZ1SDI5dF9DWkFTT0lvYmMzVFBtQ1N4SS1jUl9MY19RVVVkZExtS3d1UUtpeWZLeXdXY2lOdDBrc1R0UERuWHQ5UVE2c1pTRjNj?oc=5" target="_blank" rel="noopener">Jericho Receivers Launches Software Defined Atomic Clock – ATSC 3.0 Broadcast GPS-Independent Timing</a> <span class="tl-cat">Business Wire · US</span><div class="tl-date">2026.07.01</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiqwFBVV95cUxQVm5xbmNkajE2OUw1Tm9VN1I0RS1GS2Ffa1BUVWVSQTFnQUdpcnJpMmhtTWxBNFU3Z1BJNF9KV3hSRjh5Sm9GQXNRUHJaaTZ4OXMzWjZDRTB1UVZDazltZDRsZGhFdFl2X21GcnYwbWJxNTlDNGdfSE5GVEJ3WWpvS2RVdXo5c0RxQV9sQVQ3R3JVT1V2Ym04TnJpWnJjWl92d0ljQjFxbGJRR2M?oc=5" target="_blank" rel="noopener">A3SA Disputes Weigel Assertions that NextGen TV Threatens EAS</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.30</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiekFVX3lxTFAyNjhjVzdVUjg4N2VjSGtRak9JWGx6SGphXzEta04tZTAzMk96OXA3SV91VGtxTDNwRTU2NnctcTVaRTA1LTZGSlFGX29lTGxHOVBoQ2tXQVhqS1FuYnhrWVNkdm9uaDJkWWFKRFNSWG1GNFUwMVZ0d2RR?oc=5" target="_blank" rel="noopener">삼성전자, 美 NAB서 차세대 방송 핵심 기술 시연</a> <span class="tl-cat">Samsung Global Newsroom · KR</span><div class="tl-date">2026.06.29</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMimwFBVV95cUxOZkNURG1PSVRmeXZZUVo3WVBXZnJ0bFhqMUI2cWxlVGJYM1FpNWQ5YmRrQzl3anBVNml4OVpWMWNyOXNPMzJ6OUhvbHlHTTREbl83dWhUOHF6MERaQ2t0N2ZhS0JRX09yaHpISE0wdFpyM2FqbVFIclN5bE1kSFVBOV9GZkY0MW1mQ3hlbUVIeDRYVXNleHNUMkF2NA?oc=5" target="_blank" rel="noopener">Enter to Win a NextGen TV Equipment Package!</a> <span class="tl-cat">myfox28columbus.com · US</span><div class="tl-date">2026.06.26</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiYkFVX3lxTE1FS2ZlYUoweHRkc3pUSHBDaEJnMDVHbVJaZ19RbEdpc1R1aXhiOXNnYWNUREFyYXlmbUZWZWpIM18xUWNoTzRoUW9qLUtCSlE3QXo2UmJQbElMTnZsdUJ5WENB?oc=5" target="_blank" rel="noopener">삼성전자, 美 최대 방송사 그룹과 차세대 방송 표준(ATSC3.0) 협력 MOU 체결</a> <span class="tl-cat">Samsung Global Newsroom · KR</span><div class="tl-date">2026.06.24</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMizAFBVV95cUxPcl9weDY1MDZaalpIdzhlR01Fd3ZwM2RSUXRvdjQ3d3ZQVFRKNU5wS2s5eC1QeDdZYnJram1CYm1DNllLVFVHSXBjdGtCd0U3WjEyVEJ5RGRJUWVEME1uM3RQVmNETWtFYlozZlp5YktGSDJhUUxLaXJZS3U3VmpLYVMtbVNzZlVzeDdIWll3b1lfbm5rMHVmbXdGV0tRd296SmE0QmpxekpDWWotS3hGMTV0SDB1bHRzV0RtMWxRTGo0amdMUVJ0aGdOZk4?oc=5" target="_blank" rel="noopener">NAB NextGen TV News Technology Lab Releases Report On 3.0-Based Emergency Alert Uses</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.17</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifEFVX3lxTFB0aDgzX1NqVEFVSmVQaW5ELWpHRVd0THRmWUJNb2pNUGNxVUViWGZpamE4VE1aT1EwS29JNXVNT1RURmxUbDVuTkh1d3BIQ3dQdWc4UEUyX2dBUXVIdDd1THVJYjd6TmpMVnEwbUxzWjU1ekptZmNESm1qUy0?oc=5" target="_blank" rel="noopener">Sinclair’s One Media to host ATSC 3.0 event in Maryland</a> <span class="tl-cat">TheDesk.net · US</span><div class="tl-date">2026.06.16</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiSkFVX3lxTFBDVzVtQXVhUFF4MFBsekc1cVhaV3BMVzBMdVJsRGFyZGdJZnhOcUdkS05ob0EyZnZia3UtcjlacmhGSzN3c3pIN1JB?oc=5" target="_blank" rel="noopener">Coming Next Week: A NextGen TV Interoperability Event</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMibEFVX3lxTE04S1YydW50SmtRUGgwWkpFdFlPbjdGcmVzZjNYSUMyRkhtUlYyWkRTeWZ2dVFYWkY3VE1yRWRCNWhGOFNGSmdycDVTM0xYcUNiOGtPVE9YcS1zQUpOdERPX01jZHhUNTQ0TnE0RNIBcEFVX3lxTE5NR3BPaDFGUjNUSmF0YmFMWmN2MVVBVVFWb1EyNE1aZENMblFwcEgtYmJUN2pfTVNkSzhneUpFam9vd2lmVXRURnVaX0NTenlOVFZlS3hHbHV1VHVtVzNYaUg2RzVYb3JqengtSzFLVEY?oc=5" target="_blank" rel="noopener">지알엠·씨너렉스, 고정밀 위치정보 활용 측량 솔루션 사업화 나서</a> <span class="tl-cat">에너지플랫폼뉴스 · KR</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiowFBVV95cUxNRDg0eHJBXzFaSjMxYXoyTWhpRWtob3dpa0pHRGNlaGNGdFVCTENieWZ0YVNzVUhSb1pQYU56VTUycUtQb05VRzRaUUlVVlRzS2lOc05wMGpncUZCWldZN25MMTN3Z2YxcWZLU3FReXQtek0zRFVJR2RZbGQyaE1LRFFoUFBobUlYWnh0YmVxcWJlcHhwdDJWbHFUcGJjUnNGdExB?oc=5" target="_blank" rel="noopener">Sinclair's ONE Media Technologies to Host ATSC 3.0 NextGen TV Interoperability Event</a> <span class="tl-cat">Sinclair, Inc · US</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMickFVX3lxTE1Lc0tvMkRQWExVWHBPeUxpQjNMVldsQ3czM2dTNldvZ2p1U2g2bFJCRWk5OExMNTF0eWY1MWZSWm1qek5GZjhqNnF2RFNhM3VZUTJZcUdZV2gxa0JMU2VuSHp1SkkwbUwyR1ByM3YwVzR5QQ?oc=5" target="_blank" rel="noopener">지알엠·씨너렉스, 고정밀 측량시장 공략… ‘GNSS RTK 기반 범용 측량 솔루션’ 공동 추진</a> <span class="tl-cat">에너지데일리 · KR</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMigAFBVV95cUxPV3ZuTVNIQlBIWjY4SUM3R3MyMHZqR3VieGh2dFlQY2VSTk5kZEwyN3ZFb2Z4QXpDdnVXaElnc1lodDAwT2d4RU1FbDViSWI4XzdZZUUzbTFycGpST2pRZEd3Z2lTMkcxcGQ2LUFiaS0xaWZwWjVmM2V5U25ndi05Vw?oc=5" target="_blank" rel="noopener">Weigel To FCC: ATSC 3.0 Corrupts Free and Simple TV Service</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.05</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifkFVX3lxTE8tNUVrRGZpdkZmR20yNkcwaC1kUEdZelVsYzJXTDEtLUxBX09Kdk9ubU90Tmw3UTItM05VaV8tdS1faTdHck11c0lsU19NdTBrNXhIVC1xYWpuTnd3cjRpcDM3dzZwa0pEUkRhdlRyTnpTLVpTVHljUjJLcGRMdw?oc=5" target="_blank" rel="noopener">Weigel to FCC: NextGen TV may disrupt free access to broadcast TV</a> <span class="tl-cat">TheDesk.net · US</span><div class="tl-date">2026.06.05</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMipgFBVV95cUxPZkZTVFlFUlN5bkVRZjVESkhBZDZwSUdaa2dOZUxGeDJXOFc3Z3pvV0JxMnpYcUxMcE5IWXByYlBlV3VGWFhDMXhGZkRrenI0RjdhQ3dzM1BVamEzcXhiekUzZmRwY0RPNTdFMnN4WTJfMTNrejhHMlBOMHVmSjJJcDM2UWxuTjFrVnV2Ym5EWHdvN0QxMXVoTnMxY3pwNEVkRkRRSjBB?oc=5" target="_blank" rel="noopener">Congress Weighs the State of U.S. PNT: GPS Modernization, Interference Enforcement and the Search for Complementary Architecture</a> <span class="tl-cat">Inside GNSS · US</span><div class="tl-date">2026.06.05</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMipAFBVV95cUxNWTc0RHY0b256T2E5OTNoQ3hjdHprazlGeXNpRS1ZdFdITXAtWEhRdkNRbU1lLUlGb1BidXNzN2F6Y2liZGJVeE1ZYTl3MG41bXpDbWVWRERDRVBXVl92ZEE1bW96NlVVeFVLSVlTYmMya3ZyUUF4YnUzZjZoZDhucDR2U1dsczY3YUYxX1JJdGJFMWlOdWsxNEc5WElPUGh5cEZYdA?oc=5" target="_blank" rel="noopener">Sinclair Launches NextGen TV Campaign in Columbus, Ohio</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.04</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMivwFBVV95cUxQTkZWZWRCSk9ESHRQa1VqVXo3N19VaWVUa01FazdZenBCcnkyN0JpaklBMnhnU1NPbnFZcTNpcXNzZnBZQkg1U3pheEd2Y3ZjeGRhSVlvYUMzSThJSkFib25IX0xrdjMwU1hRN0thVkhMcGNMejI0OUhjSXBSYUx1LUFVZTlQeVdYd2VOclRxZmI0a0tlUzFWRGZGbktFX3M4ckpDYVM5ZGNHVlJtMDl5dENHMENEVEp3dXJrTDJFTQ?oc=5" target="_blank" rel="noopener">Broadcast alliance pushes back on LPTV 5G standard petition, backs ATSC 3.0 path</a> <span class="tl-cat">NewscastStudio · US</span><div class="tl-date">2026.06.04</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMirAFBVV95cUxNakpHOGxtSTZVOTlleF9KbGlaWUpWQkR5UVZYRHRrempDaUgyVTl2UUxVNE11NXpHX0RFSWpMSzVqY2dzY1M5UVJfZ2poVGRjSEt2cU9FcTQwYVk2eGhuazYyVzdraGFxZWNrSVp3NWlENFlPZ0JhQU81ZTFmVkRGQUt5RXlUZVJEOXpHMUpBS0hMNUQzSmowUEdEb3dqUzRHd2I3RllXS1gyUkFS?oc=5" target="_blank" rel="noopener">Merkhet’s Sam Matheny Urges Congress to Expedite BPS Deployment</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.04</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMimAFBVV95cUxNdVR4QU1nMnhoMFhOeVRqSHJibXJTcE8yQnAwT1ZVSkdPeU1YOTc5SWFSVVdxUWM5ZTRZRGNNNVhvN0plMzZ5QjN5RHJFWFFYelkzMF9jN25zRFMwT1IzRGpLOGJtYk5iRE9PbnplZWctOFB0VTlkUkhBYjlNUGVxUUN0alRMZHdMc0dkNUp0Vk1zdUl0NnZ3bw?oc=5" target="_blank" rel="noopener">Broadcasters launch company to advance Broadcast Positioning System</a> <span class="tl-cat">GPS World · US</span><div class="tl-date">2026.06.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMitgFBVV95cUxQZVlObXhFdWdOY0lyMXNqZERINmU4blU3ZTNldXB2TlZkUDEyaEJkQ21WVWZHcFJNVG1mT095R1RvbjBOenpTMzdSY2lXeFNNTEtyYjUxcFo0eDJTZ1hob0VBOG9wSFZSczlZZmtxNkx4SzJNdkNHT29nc3pVeGxjZXJNOElwUC1GbDh5NkVJSzlFOURHNWV3Ujl3Rlp6N0EtYmhEWVNNZjVqS2dmcUwyNWFSckxPdw?oc=5" target="_blank" rel="noopener">Merkhet Solutions Formed By NAB To Commercialize Broadcast Positioning System</a> <span class="tl-cat">TV News Check · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiowFBVV95cUxPS2VNU0JEMFhDenNPaW9NeUwyQUx0eHpXODVxeU5vZU1fV01JSXAzNWtsWHI0eFdjYlpucW1QQUUwRFVRUDFoRHR2U2ozU2E1b2NxM3pqWWY0LUhLZGwteVpTbGZWUnkyRmlGWGVkdGIyNWZucEFXLWlTTVoxQnBPQ2RNV3NUZEwyTGxZTkJmWG12T3pmVDQ4YkxaOEwzRi1kT0w4?oc=5" target="_blank" rel="noopener">NAB Launches Merkhet Solutions to Advance BPS Deployment</a> <span class="tl-cat">radioworld.com · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOQ2YxZE93NjQ0WUZaWFRCZVM4Z2lHakZLbDFzUGk4QUNpdE5WbTV5MDlyODJNeUJxWEQ3SzlGLThhUFEtSGc4NVBYd0ZBTlc3UVlXMUl3em5TampZRnZpRkY3d0E2eHZMc2xUS3Y1NWlack1SZkxzZFhONUFjeV9POGQ2R1A3bV8temdmd2xjTVcwMXRpV2IxamdQMGZ2Z0FZeVdyeDM2cXp4QW5jZXAySg?oc=5" target="_blank" rel="noopener">NAB Launches Merkhet Solutions to Advance Deployment of BPS</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifEFVX3lxTE96UkxwaER0VnpEeDh5OGszcUxVVW0xVGExM0RsTUJVSzJLMzA5LU1kc1RTUjlyZ29QUG95Y0U3eXp1aW92ZGtkazgxNTdMOUNHTHVaOXBFam11V01uQVVjc0ctS09ySG9CUlNGVjB1RXBBN3JMaEdDcEhzZV8?oc=5" target="_blank" rel="noopener">NAB Ramps Up BPS Deployment Efforts With ‘Merkhet’ Launch</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMijAFBVV95cUxQN3NiVFRMeWo1bUlSSEVqSUx3MjlidnhNNUx4emExSDNVcXR3VF9BSXExYi0wOTIyLXJyMjJDdGpLSzRVM2Y1M0xwbm1LYnZ3aWFRMHA0dVR5cUZhc19CeGdKc2pqLTItNUZMZDU3czd1anZ4ZjhJekJncnUzSnZkWGJ4VmlrX2lXN0xGaw?oc=5" target="_blank" rel="noopener">NextNav, Opponents to Square Off at House GPS Hearing</a> <span class="tl-cat">Broadband Breakfast · US</span><div class="tl-date">2026.06.02</div></li>
</ol>
<!-- NEWS-TIMELINE:END -->

## Publications & talks

<div class="svc">
  <div class="svc-item"><span class="svc-label">Coverage &amp; outage bounding in hybrid ATSC 3.0/LTE RTK delivery — IEEE BMSB 2026 <em>(to appear)</em></span></div>
  <div class="svc-item"><span class="svc-label">ATSC 3.0 end-to-end latency for emergency alert delivery — IEEE BMSB 2026 <strong>(Best Paper Award)</strong></span></div>
  <div class="svc-item"><span class="svc-label">Nationwide time sourcing over terrestrial broadcast networks (BPS Project) — IEEE BMSB 2026 <em>(to appear)</em></span></div>
  <div class="svc-item"><span class="svc-label"><a href="https://speakerdeck.com/sunghojeon/20260514-koba2026-keonpeoreonseu-anseongjunetri-jeonseonghombc-upload">Ultra-precise PNT infrastructure over terrestrial broadcast — BPS &amp; Broadcast RTK</a> — KOBA 2026 deck</span><span class="svc-date">2026.05</span></div>
  <div class="svc-item"><span class="svc-label"><a href="https://drive.google.com/file/d/1Hs1RZii6ePm6hQfI36hVfPl9xzAHaoqp/preview">Broadcast RTK &amp; global expansion (Global eGPS)</a> — KIBME TTA special session deck</span><span class="svc-date">2026.06</span></div>
  <div class="svc-item"><span class="svc-label"><a href="/TTAR-07-0048/">TTAR-07.0048 — drone-based DTV antenna pattern verification</a> — TTA technical report</span><span class="svc-date">2025.10</span></div>
</div>

<p class="news-more"><a href="/research/">All publications &rarr;</a> · <a href="/talks/">All presentation decks &rarr;</a></p>
