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

<p class="news-more"><a href="/research/">All publications &rarr;</a> · <a href="/presentations/">All presentation decks &rarr;</a> · <a href="/news/">In the news &rarr;</a></p>
