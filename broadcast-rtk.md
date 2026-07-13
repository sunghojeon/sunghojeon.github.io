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
      <div class="cv-role">Three papers at IEEE BMSB 2026 — <a href="/IEEE_BMSB2026_JoaoPessoa/">Best Paper Award</a> <span class="cv-rank">João Pessoa, Brazil</span></div>
      <div class="cv-detail">The ETRI·MBC·KBS study on <strong>ATSC 3.0 end-to-end latency for emergency alerting</strong> won Best Paper — measured ~2.5 s end-to-end latency on the live network and showed it can be cut to ~0.25 s by operational tuning alone, without changing the standard. Also presented: coverage &amp; outage bounding in hybrid ATSC 3.0/LTE RTK delivery (first author) and nationwide time sourcing over broadcast (BPS); chaired Session 12 (ITCN, GSL and 6G Broadcasting).</div>
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

## Publications & talks

<div class="svc">
  <div class="svc-item"><span class="svc-label"><a href="/IEEE_BMSB2026_JoaoPessoa/">Coverage &amp; outage bounding in hybrid ATSC 3.0/LTE RTK delivery</a> — IEEE BMSB 2026</span><span class="svc-date">2026.07</span></div>
  <div class="svc-item"><span class="svc-label"><a href="/IEEE_BMSB2026_JoaoPessoa/">ATSC 3.0 end-to-end latency for emergency alert delivery</a> — IEEE BMSB 2026 <strong>(Best Paper Award)</strong></span><span class="svc-date">2026.07</span></div>
  <div class="svc-item"><span class="svc-label"><a href="/IEEE_BMSB2026_JoaoPessoa/">Nationwide time sourcing over terrestrial broadcast networks (BPS Project)</a> — IEEE BMSB 2026</span><span class="svc-date">2026.07</span></div>
  <div class="svc-item"><span class="svc-label"><a href="https://drive.google.com/file/d/1KYNJYx1FKDoI528iMg57-XRkMwc5wEFH/preview">Coverage overlap &amp; outage bounding in hybrid ATSC 3.0/LTE RTK delivery</a> — IEEE BMSB 2026 deck</span><span class="svc-date">2026.07</span></div>
  <div class="svc-item"><span class="svc-label"><a href="https://speakerdeck.com/sunghojeon/20260514-koba2026-keonpeoreonseu-anseongjunetri-jeonseonghombc-upload">Ultra-precise PNT infrastructure over terrestrial broadcast — BPS &amp; Broadcast RTK</a> — KOBA 2026 deck</span><span class="svc-date">2026.05</span></div>
  <div class="svc-item"><span class="svc-label"><a href="https://drive.google.com/file/d/1Hs1RZii6ePm6hQfI36hVfPl9xzAHaoqp/preview">Broadcast RTK &amp; global expansion (Global eGPS)</a> — KIBME TTA special session deck</span><span class="svc-date">2026.06</span></div>
  <div class="svc-item"><span class="svc-label"><a href="/TTAR-07-0048/">TTAR-07.0048 — drone-based DTV antenna pattern verification</a> — TTA technical report</span><span class="svc-date">2025.10</span></div>
</div>

<p class="news-more"><a href="/research/">All publications &rarr;</a> · <a href="/talks/">All presentation decks &rarr;</a></p>

<hr class="section-rule" />

## In the news

<!-- NEWS-TIMELINE:START -->
<p class="page-subtitle">ATSC 3.0 · DTV+ (TV 3.0) · Broadcast RTK · EdgeBeam — auto-collected news since June 01, 2026 (last updated 2026-07-13).</p>
<ol class="timeline">
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiqAFBVV95cUxNWmhUQ1I4QjVMRFBUc2F1czRoVTdzYUptdnprQ0FnSHh0M0loZlNoYi1UYTIteU5zNU51bzZHMGczdUdzUnRKMC1JZlVCNUwzRHhSMzYtTExQX0lmSFNhaG5icThnaFFIX1cxMWt5QTN5aFJFUjdkVW5lVFFVTUVUNWZEZUVWSFY3YkR0Z256Ni1UOVI2UGMwcE9LNjR6ejJ3Y29CWUFXQ0w?oc=5" target="_blank" rel="noopener">TV 3.0 sem conversor? Samsung, LG e TCL respondem quando a novidade chega</a> <span class="tl-cat">Canaltech · BR</span><div class="tl-date">2026.07.13</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMioAFBVV95cUxNMUxDOU1IbTNPTGdrOUtDNEYwZ2draFU3U0doZkVXNDI2Wm1iUFZ3SU1kMFg1aU90WUJOMkdvZk5KaFBmcWJsRHNNSGdWcHVkelh5Vk5MWDhfWENuWWFfZXlGTURibFpQc2lKMGx1YnhDbkNLZFl1MXh0Wkw0dnhDc016SC1vOWlOMmpPN09hMm45RWh2dEJTUkFWRlFFNVZR?oc=5" target="_blank" rel="noopener">Demos and Presentations | NextGen TV Day at WKAR</a> <span class="tl-cat">WKAR · US</span><div class="tl-date">2026.07.13</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiqAFBVV95cUxNT3Nlal9qQ0FyTFFNbGViazN6aEhqUkpTejhFMHY1amFnXzVmVGZmbGJ2Z3dDUU0xaFNKanpGMkpFX0EyVHZhbjhaQzVueFZKdkdoZWQ2U3o4NFFVdWJyLU1DNW04cU5XRHhqb0V3cV85cFRMcjl2bkVpbGxDWF81VEItekRvcWk5aUNvYktrZWpGRUlSblFYUGZNTDkwRVVkaTVsSEtpaUM?oc=5" target="_blank" rel="noopener">Quando a LG vai vender TV 3.0? Nós conversamos com a marca para descobrir</a> <span class="tl-cat">Canaltech · BR</span><div class="tl-date">2026.07.12</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMi6wFBVV95cUxNWmpZcWctdUhERTEyUVFBOGoyaVBId2xlUk5WWGlueGlycG41VElRMFN0SFB3SmtiT1F1MzNxbnQ1dFhqTGUyOVRjaE8zSFA3UF9STlBwR0IzTnB0M0s0cmtMb2tNd2VlTGJ0cHlidndGSWt0X3VTZV81Mm4weExKR0pEa2dPZXZaNkJkY0UxdS1PUUtGa1dpTUlnMTNocEJuVWhfMV9GNklldkpObFFOQUZnTE1OM1BXNnA1S2JtTHFmZERHQmdFaGRWdG12NFhVTy1DZGlOaGZIZTE0YWMxeWE3OFlVSVJXODdj0gHrAUFVX3lxTE1aallxZy11SERFMTJRUUE4ajJpUEh3bGVSTlZYaW54aXJwbjVUSVEwU3RIUHdKa2JPUXUzM3FudDV0WGpMZTI5VGNoTzNIUDdQX1JOUHBHQjNOcHQzSzRya0xva013ZWVMYnRweWJ2d0ZJa3RfdVNlXzUybjB4TEpHSkRrZ09ldlo2QmRjRTF1LU9RS0ZrV2lNSWcxM2hwQm5VaF8xX0Y2SWV2Sk5sUU5BRmdMTU4zUFc2cDVLYm1McWZkREdCZ0VoZFZ0bXY0WFVPLUNkaU5oZkhlMTRhYzF5YTc4WVVJUlc4N2M?oc=5" target="_blank" rel="noopener">Com a DTV+, é possível usar o controle remoto para acessar serviços públicos na tela da TV</a> <span class="tl-cat">G1 · BR</span><div class="tl-date">2026.07.11</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiswFBVV95cUxOTnRGRHB3OUtacGVxd3NfX25YZ1JGcXp3Q2RIVWN5bldjdE9nYVk1TFNTeDMzelcyWVF3Z1JlQXVQWXFNbmEycTdjS1ZPRGVDdGhsc1BSblBIRnNtWE5lRlF1NlhicU9qSVhVQmRITW42NUxYbGVJTHdTemVoZ0ZiRXFzM255cVVEaUJXRTA0VnlDV3RuTXJ0OUZ2NF8zb2w2Z3JKZTJSWFktcS11aHFjTm1ta9IBwgFBVV95cUxOZUpUejhVdS12WFlsQWI4RUJTYklsNGprMWJuU2JJQXg0dEJYSnY4bVdlaXBCelV2QzRVcmtpTGYwNkF4Ylp6VlZMUWtfTkdvejF1SEYycGwtTDZwWHFCeURoZ0hiZmN5NFN5N2dfQW0zdmltc0lmUkptYjJndGJndHpYUXA0OHZaSVV3YnVWLXZKbHEzejhzRmNLR3hYa3F3TFRKaENFUFQ5RnJiZ0xfY1BFNDZrYXFyak1ja0FZVmVrdw?oc=5" target="_blank" rel="noopener">DTV+ vai oferecer serviços públicos na tela da televisão</a> <span class="tl-cat">G1 · BR</span><div class="tl-date">2026.07.11</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiqAFBVV95cUxQTVlQU2g5Y3ZzZDdVa2Q5bk84Smc4NUJGSjVMRnR0clhtaF90QWVPMzhIeXVXVUo0eDNHV1ZxYzFXeENySW8xcjQ3M1ZEa2Q1dUhMOU5IOGxDcDZzMmF3TmgyUVh0VmRTNG9yVUdqalFrR2ZXT04tT2RtbjJ4UnJWWklTdHdPZlNXSERKN19Qa3p2QmJXb2Y3NDdaQ0hZdVNyY1FEODJiRVLSAagBQVVfeXFMUE1ZUFNoOWN2c2Q3VWtkOW5POEpnODVCRko1TEZ0dHJYbWhfdEFlTzM4SHl1V1VKNHgzR1dWcWMxV3hDcklvMXI0NzNWRGtkNXVITDlOSDhsQ3A2czJhd05oMlFYdFZkUzRvclVHampRa0dmV09OLU9kbW4yeFJyVlpJU3R3T2ZTV0hESjdfUGt6dkJiV29mNzQ3WkNIWXVTcmNRRDgyYkVS?oc=5" target="_blank" rel="noopener">João Pessoa no centro das discussões sobre o futuro da TV 3.0!</a> <span class="tl-cat">Turismo em foco · BR</span><div class="tl-date">2026.07.09</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiuAFBVV95cUxNLTVZeERIVnRpRFFycnM0OVpsQ3FsUVFyQ2k0bDlEanJ6YUVrZjliM0czWlFpRGN1YlU2amc0a0M5bk11ODNsWUlyX1NCYWVYakloY1NnV2UxcXZYS1RMOFFBQUdoblFnYmVEU1diTl9HdjZxazY1QWZadXNtMUxPSGV0T0ZlYTZpRlhLQXZLNkZxN2o4M2k1NkktbUF1TVpiTmZRblpULVV0UVdOMTc4Uk9ETUpoS0J1?oc=5" target="_blank" rel="noopener">PNID prevê uso da TV 3.0 para ampliar letramento digital da população</a> <span class="tl-cat">Associação Brasileira de Emissoras de Rádio e Televisão · BR</span><div class="tl-date">2026.07.09</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiiwFBVV95cUxNU3k4enhVZ2stUTNvRmxZMk1vUUI2cmhpOUw0MklFNXp0SXh4M0NlY2l6OGZkOEluaEJRRTFMQ2dtRnpZcTZvR295WUwwREdKbl9rMHRPamNZbFZrY0ZxTlB5Zy04R2hjcmlxM1JHSGdPUTlaUEllNFluYU5LTGxOY2pseExjNUZHMmRV?oc=5" target="_blank" rel="noopener">TV 3.0: Governo ainda define modelo de conversores para acesso</a> <span class="tl-cat">AMIRT · BR</span><div class="tl-date">2026.07.09</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMi9gFBVV95cUxPRTNycjV5ME1qTzlzUEFwM2VtSGZsbVU4ZTFlS0hPeTUzenlaLVpfNE1jNEd2VGRTUktDY0dnb1ZLcFdvNjVwb1dsTE1CYmVVQmhGOTdiRG8ycG1zSndWYVRIU1VqYURGYVJXQXpsNm9FT1JsVU55M2xRMmxfSmlKMUwwVXFxUTV4ME1OeVVZc09nU01iVlRDNUVQeTVXVWU2SGhOcjQ5X2RwTHlvXzhLUkpSSlZORDBHdnFJaXJMRmloVkJTSEYxWnNNTEVESTdVRUVqd3htM1ZTeXE2Zl9TM3pDemZXWXQwWXdRZGl4UnAwWHduR1E?oc=5" target="_blank" rel="noopener">A TV 3.0 se aproxima: entenda como a tecnologia mudará a TV aberta no Brasil</a> <span class="tl-cat">Diário do Nordeste · BR</span><div class="tl-date">2026.07.08</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiugFBVV95cUxOVXdwVzVpMnRFNzNGR3ItVjhsNzRBQW5VQnN3dk83NklDNlMxaVYyY0Y4el9VNnctTkdxS01CVXJPSVFTWUc1MVRSZVU0by1FS1FtUkJ3UzIzZWd6amgxMEdyY1RMMXREeFVYb1FUcUFsaFQxMjFiNTNIcWlsNGx5WlRnaEx4Si1kNzJvOExGeHU3NnYxaXQ2RTFYeUhpX0RwbmdJemJSb3plbmt0VXBjVU5qaGlZZDdyMmc?oc=5" target="_blank" rel="noopener">Digital Alert Systems enters ATSC 3.0 dispute, declines to take sides on DRM</a> <span class="tl-cat">NewscastStudio · US</span><div class="tl-date">2026.07.08</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifEFVX3lxTFBzVGxwSXNSY2ZXRzVGS3VMOW9sODg2RDZwbXNESWw1T1ZlWU5tTWVqaFhNdElYX1Fjam1uWWxpZ2lCWUM4cnpTZ2FQMVFzS054ck5rRnU3d3d6ZEw3cXBKMWo2WlhPT2tWemJBWHZqY2NoTUJvcGlPZXBZT04?oc=5" target="_blank" rel="noopener">삼성전자, 美 최대 방송사 그룹과 차세대 방송 표준(ATSC3.0) 협력 MOU 체결</a> <span class="tl-cat">Samsung Global Newsroom · KR</span><div class="tl-date">2026.07.07</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMirAFBVV95cUxPWEZUVUo0dGRndUpBZ3A5aUM0RktDem9YamVZbTFXRy1ubDR1TjhIWTFxNmp6eHllcnUwTHhVQWZ6RXpDZE1xQzkwWHJ3dXNQRV9uV2N0RFhSb3FBVURUZnpDOGlvWHhYQTh1VnFxSWFXUnFUUGJDOGFwMHBnLWdWc0lnaEMxaDJlX1JlT0JzZUVTal9jb3ozWTZaaFgzV1dvRW03bHN0THpscEp5?oc=5" target="_blank" rel="noopener">Digital Alert Systems Details ATSC 3.0 EAS Capabilities to FCC</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.07.06</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiugFBVV95cUxPX0ktbDNOelRJZlFYa2o1VzdndElIeE1UeG5iYjZpYkZwc3dMMTNha05TdWF5Y205VUJqbThxT3ZTTU13d2hvd01tcEpJZWl5VjJxTWlVQnlDZmRMZFZabWxRN2N2b1k0RUtiX1hzZk5MWjg4VEZybjAxUk5UTEpUVkNuYV96eUVZNFVFemVCbm1hSFpSWHA3MFR1akQ2UnI3OUFScFJmM0RKaEl5Nmw0Q2NEWEd6SW40M2c?oc=5" target="_blank" rel="noopener">Brasil inicia testes da TV 3.0 e dá largada à nova era da televisão aberta</a> <span class="tl-cat">Portal São Miguel Notícias · BR</span><div class="tl-date">2026.07.06</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMibkFVX3lxTFB6bndHVTVxSzVkamRtRy1ac1d1OTNnal82YXU0eVZ5V1JFNVYyNkVVaWwxOUU0cXhkS0tqN2p6cHZDaHRNTGhzTUg5dEx5SVl6VFNodE5vRUNOWUttT19zT1Qxb2psUmxpODVPb1ZB?oc=5" target="_blank" rel="noopener">TV 3.0 começa a operar no Brasil e promete integrar streaming e serviços públicos na televisão</a> <span class="tl-cat">NSC Total · BR</span><div class="tl-date">2026.07.05</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMic0FVX3lxTE1oNHBWMjZfOFNSMFl6eDREeWVTamV4TXNFVlJPcmllTE5FR2hrN3F4VlN3Y2gwUElBV01WYm5lOGJLLTBPYWRkcFVrRy1SMWk0dGZ4QjJXdm9iTjJvcko2R0xoZDZ3UDJ0X3hpbjVBNWFkNDA?oc=5" target="_blank" rel="noopener">DTV+ da Globo terá interação personalizada com apps móveis</a> <span class="tl-cat">Mobile Time · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiwAFBVV95cUxQOW1YOExzSXlyWHlSUEVBTUNQSHQ1TGJUMjRDN3R4T3dKOWMyT1FGNlA1NmJxX1NOZzlsWENJemJybV9tRWJxR2d0T2cxc1dFaEFtZTMwZXMwU2g5UWN0SmJ3WU9vOUk0SjlWNFRsWl9YX0k3a1FiemJ3cS1FLTdycnNCLUFnWDNaTlNsQ2JlSUFlT2h4eVNIRFg4YlNGS0Rsb2N1TjNHbzFFa3lVR3E1QnlFamxjRV85NXZhUDlES2I?oc=5" target="_blank" rel="noopener">TV 3.0 chega para reinventar a TV aberta no Brasil. Saiba como ela vai funcionar</a> <span class="tl-cat">Olhar Digital · BR</span><div class="tl-date">2026.07.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMivAFBVV95cUxPbVBZUzU0OUllcWJBTl9PR3d3WVRMQXBlV21kS0RJcHRwRU9KalNTSHdJQzhFVTVOTFRWbDFYRmZQd3liYWtnaFhQZmNaN2E0TUJKd09WcEo4RWRjbTAxNDRtdkdFNFVVTUttZkV6M1p2Vmk4NDlId2N4VEhEU092WHZDMW5EMG5iZ0JrOU9ncENIU3laMG0yVDhMN3lWYUQxckhqMkJ5anAtTTF1enNLSjJPTXhXdm9JSDFuNw?oc=5" target="_blank" rel="noopener">Jericho Receivers Launches Software Defined Atomic Clock – ATSC 3.0 Broadcast GPS-Independent Timing</a> <span class="tl-cat">01net · US</span><div class="tl-date">2026.07.01</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMimwFBVV95cUxOZkNURG1PSVRmeXZZUVo3WVBXZnJ0bFhqMUI2cWxlVGJYM1FpNWQ5YmRrQzl3anBVNml4OVpWMWNyOXNPMzJ6OUhvbHlHTTREbl83dWhUOHF6MERaQ2t0N2ZhS0JRX09yaHpISE0wdFpyM2FqbVFIclN5bE1kSFVBOV9GZkY0MW1mQ3hlbUVIeDRYVXNleHNUMkF2NA?oc=5" target="_blank" rel="noopener">Enter to Win a NextGen TV Equipment Package!</a> <span class="tl-cat">myfox28columbus.com · US</span><div class="tl-date">2026.06.26</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMilgFBVV95cUxQNXJKdVVXSGZDMDlLTWFnQnlvU1Nkc2dnRXExUmg4TnpCUlg1RWppMUkxMktuTlVwdXo2cHNvMTRNSHBiZEtJeVNIeTQ0UHVvWV8welNKSGFobFZRQTdlQUxQLVRNQ1l4VVNuRXFfMlVSR2Q4SGR3U3BVUUE4X0hfVUotN3B1XzZqbmk3bjM4RzJNQl9PQWc?oc=5" target="_blank" rel="noopener">NAB Updates FCC on ATSC 3.0 Alerting Advances</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.24</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiakFVX3lxTE5KYlRwLVpKYWFYMG1HZmtvYVBsMVlhaXVjWVRKcG9yQmRERGJzOFk0X3VRRnNyZ052Nkstdmk3MGlWbUh6LXMxZkRWdmduOFkwNWxZSFp2MlZqTkgxRVJhMnNIdENzS0dXRnc?oc=5" target="_blank" rel="noopener">Demoing The HDHomerun Quatro 4k ATSC 3.0 Tuner ! Tchouameni (GUrVfapuVl)</a> <span class="tl-cat">Fathom Journal · US</span><div class="tl-date">2026.06.22</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiiwFBVV95cUxNdTZEaHJmalBNR2xta3YwN0tpS3R4T09ENTJOWUVUNFZiblhOdGJJMl9oeFEwQ25SX24wRGtaZ2xyOTctT1VWdWZLQzR3dHlFM25YdWJzV1ZxdnRJZm9QanZCNHBwYWgwZ1dseHpZLVM0endRM2ZPN0FNUXowSTAxSHUwV1htYW1nek1V?oc=5" target="_blank" rel="noopener">Smarter Weather, Interactive News: NEXTGEN TV Benefits Touted By NAB</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.18</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMivwFBVV95cUxOX3hDVGx1LXdOaF9wUHluTWc2RVBiQ2hSSTRjUTZpRlJYaUpPMXVhR0txLUM0aG5jUFFucTZGcWJVRUNaZU4yS3BIMDFXRWxKbEEycnNkZy1tbW9ZYmk5YmdFeTBBZzlLOGcwUGRRZXFiT2JYdkVRWGU1dkZOU1hhalJvejdpUDkzUUw1Y0NEdlFxd0pIaXVlZ1p0QVJ1TVEtSDFxdUdibXl0Z0lNc2U3ZEh5Tkk2Z1FJYW9TUnBKRQ?oc=5" target="_blank" rel="noopener">NAB NextGen TV News Technology Lab Releases Report On 3.0-Based Emergency Alert Uses</a> <span class="tl-cat">TV News Check · US</span><div class="tl-date">2026.06.18</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifEFVX3lxTFB0aDgzX1NqVEFVSmVQaW5ELWpHRVd0THRmWUJNb2pNUGNxVUViWGZpamE4VE1aT1EwS29JNXVNT1RURmxUbDVuTkh1d3BIQ3dQdWc4UEUyX2dBUXVIdDd1THVJYjd6TmpMVnEwbUxzWjU1ekptZmNESm1qUy0?oc=5" target="_blank" rel="noopener">Sinclair’s One Media to host ATSC 3.0 event in Maryland</a> <span class="tl-cat">TheDesk.net · US</span><div class="tl-date">2026.06.16</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiSkFVX3lxTFBDVzVtQXVhUFF4MFBsekc1cVhaV3BMVzBMdVJsRGFyZGdJZnhOcUdkS05ob0EyZnZia3UtcjlacmhGSzN3c3pIN1JB?oc=5" target="_blank" rel="noopener">Coming Next Week: A NextGen TV Interoperability Event</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMickFVX3lxTE1Lc0tvMkRQWExVWHBPeUxpQjNMVldsQ3czM2dTNldvZ2p1U2g2bFJCRWk5OExMNTF0eWY1MWZSWm1qek5GZjhqNnF2RFNhM3VZUTJZcUdZV2gxa0JMU2VuSHp1SkkwbUwyR1ByM3YwVzR5QQ?oc=5" target="_blank" rel="noopener">지알엠·씨너렉스, 고정밀 측량시장 공략… ‘GNSS RTK 기반 범용 측량 솔루션’ 공동 추진</a> <span class="tl-cat">에너지데일리 · KR</span><div class="tl-date">2026.06.15</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMilgFBVV95cUxQTUdBWWw3MW5ORHduUnVhQThMc0hBaXlqTUNTblBjR01FWU1KcWtLbkxaVGIyajZQaVJQSXNCb1g1bUYzLXRKVWtqLUNQMlItUGhwLVRPVEdrWXdlajNOUlJwVnNkWko3d3l3NEN3bXR5STlvU1hNWnQ4N21VNHJsUWRCMzZUYkJKUFI3SVdlU2Y5UTNMR0E?oc=5" target="_blank" rel="noopener">Why Broadcasters Belong In America’s Resilience Future</a> <span class="tl-cat">TV News Check · US</span><div class="tl-date">2026.06.11</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMi3wFBVV95cUxPMjJ2dElsZHhkQ2sxSVllNE5Sc0NTSGRQVHpWSnFWWXQ2NHdyNTBzTVBoNXVlM1RXWVVUMll1elVhYXdVWld1V0hEU0lhdUhqcHB5VEFVcEw5bk5ISDZKbE5kR091R3hDMlk2VjJ3anVNc2psYTNvSDY5cktzYm16WThqdHNDUGlwM3VDSGFEX3B3OTFqSWtvNWlJZWtsTGdyZGhYM1p0N1pYSjB4U1pZNVpxSnl1TXpJMTR5OHhJdVE0NlgxMlMxOWRJSjNmMkpaOWF0RmkzUjg2LXNpSjVF?oc=5" target="_blank" rel="noopener">C&amp;T Hearing: Where Are We?: Examining Positioning, Navigation, and Timing Capabilities in the United States</a> <span class="tl-cat">House Committee on Energy and Commerce (.gov) · US</span><div class="tl-date">2026.06.04</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMirAFBVV95cUxNakpHOGxtSTZVOTlleF9KbGlaWUpWQkR5UVZYRHRrempDaUgyVTl2UUxVNE11NXpHX0RFSWpMSzVqY2dzY1M5UVJfZ2poVGRjSEt2cU9FcTQwYVk2eGhuazYyVzdraGFxZWNrSVp3NWlENFlPZ0JhQU81ZTFmVkRGQUt5RXlUZVJEOXpHMUpBS0hMNUQzSmowUEdEb3dqUzRHd2I3RllXS1gyUkFS?oc=5" target="_blank" rel="noopener">Merkhet’s Sam Matheny Urges Congress to Expedite BPS Deployment</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.04</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMimAFBVV95cUxNdVR4QU1nMnhoMFhOeVRqSHJibXJTcE8yQnAwT1ZVSkdPeU1YOTc5SWFSVVdxUWM5ZTRZRGNNNVhvN0plMzZ5QjN5RHJFWFFYelkzMF9jN25zRFMwT1IzRGpLOGJtYk5iRE9PbnplZWctOFB0VTlkUkhBYjlNUGVxUUN0alRMZHdMc0dkNUp0Vk1zdUl0NnZ3bw?oc=5" target="_blank" rel="noopener">Broadcasters launch company to advance Broadcast Positioning System</a> <span class="tl-cat">GPS World · US</span><div class="tl-date">2026.06.03</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMitgFBVV95cUxQZVlObXhFdWdOY0lyMXNqZERINmU4blU3ZTNldXB2TlZkUDEyaEJkQ21WVWZHcFJNVG1mT095R1RvbjBOenpTMzdSY2lXeFNNTEtyYjUxcFo0eDJTZ1hob0VBOG9wSFZSczlZZmtxNkx4SzJNdkNHT29nc3pVeGxjZXJNOElwUC1GbDh5NkVJSzlFOURHNWV3Ujl3Rlp6N0EtYmhEWVNNZjVqS2dmcUwyNWFSckxPdw?oc=5" target="_blank" rel="noopener">Merkhet Solutions Formed By NAB To Commercialize Broadcast Positioning System</a> <span class="tl-cat">TV News Check · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMiowFBVV95cUxPS2VNU0JEMFhDenNPaW9NeUwyQUx0eHpXODVxeU5vZU1fV01JSXAzNWtsWHI0eFdjYlpucW1QQUUwRFVRUDFoRHR2U2ozU2E1b2NxM3pqWWY0LUhLZGwteVpTbGZWUnkyRmlGWGVkdGIyNWZucEFXLWlTTVoxQnBPQ2RNV3NUZEwyTGxZTkJmWG12T3pmVDQ4YkxaOEwzRi1kT0w4?oc=5" target="_blank" rel="noopener">NAB Launches Merkhet Solutions to Advance BPS Deployment</a> <span class="tl-cat">radioworld.com · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOQ2YxZE93NjQ0WUZaWFRCZVM4Z2lHakZLbDFzUGk4QUNpdE5WbTV5MDlyODJNeUJxWEQ3SzlGLThhUFEtSGc4NVBYd0ZBTlc3UVlXMUl3em5TampZRnZpRkY3d0E2eHZMc2xUS3Y1NWlack1SZkxzZFhONUFjeV9POGQ2R1A3bV8temdmd2xjTVcwMXRpV2IxamdQMGZ2Z0FZeVdyeDM2cXp4QW5jZXAySg?oc=5" target="_blank" rel="noopener">NAB Launches Merkhet Solutions to Advance Deployment of BPS</a> <span class="tl-cat">TVTechnology · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMifEFVX3lxTE96UkxwaER0VnpEeDh5OGszcUxVVW0xVGExM0RsTUJVSzJLMzA5LU1kc1RTUjlyZ29QUG95Y0U3eXp1aW92ZGtkazgxNTdMOUNHTHVaOXBFam11V01uQVVjc0ctS09ySG9CUlNGVjB1RXBBN3JMaEdDcEhzZV8?oc=5" target="_blank" rel="noopener">NAB Ramps Up BPS Deployment Efforts With ‘Merkhet’ Launch</a> <span class="tl-cat">Radio &amp; Television Business Report · US</span><div class="tl-date">2026.06.02</div></li>
  <li class="tl-item"><a class="tl-title" href="https://news.google.com/rss/articles/CBMijAFBVV95cUxQN3NiVFRMeWo1bUlSSEVqSUx3MjlidnhNNUx4emExSDNVcXR3VF9BSXExYi0wOTIyLXJyMjJDdGpLSzRVM2Y1M0xwbm1LYnZ3aWFRMHA0dVR5cUZhc19CeGdKc2pqLTItNUZMZDU3czd1anZ4ZjhJekJncnUzSnZkWGJ4VmlrX2lXN0xGaw?oc=5" target="_blank" rel="noopener">NextNav, Opponents to Square Off at House GPS Hearing</a> <span class="tl-cat">Broadband Breakfast · US</span><div class="tl-date">2026.06.02</div></li>
</ol>
<!-- NEWS-TIMELINE:END -->
