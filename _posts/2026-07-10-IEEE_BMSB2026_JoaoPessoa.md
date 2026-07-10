---
layout: post
category: paper
title: IEEE BMSB 2026 (João Pessoa) — ETRI·MBC·KBS 공동연구팀 최우수 논문상 수상
---

2026년 7월 8일부터 10일까지(현지시간) 브라질 주앙페소아(João Pessoa)에서 열린 IEEE BMSB 2026에 참가하여, 제1저자 논문 발표와 공저 논문 발표, 그리고 Session 12의 좌장을 맡았다. 함께 참여한 ETRI·MBC·KBS 공동연구팀의 ATSC 3.0 종단 간 지연 논문은 이번 학회에서 최우수 논문상(Best Paper Award)을 수상하였다.

**□ 개요**

- 학회명 : The 21st IEEE International Symposium on Broadband Multimedia Systems and Broadcasting (IEEE BMSB 2026)
- 일시/장소 : 2026년 7월 8일(수) ~ 10일(금), João Pessoa, Brazil
- 시상식 : 7월 9일(목) 밤 Banquet Dinner — Technical Program Report 및 Awards Ceremony

**□ 최우수 논문상 수상 — ATSC 3.0 종단 간 지연**

- 논문 : *ATSC 3.0 End-to-End Latency: Analysis, Measurement, and Optimization for Emergency Alert Delivery* (Paper 7)
- 저자 : Sung-Ik Park, **Sungho Jeon**, Seongman Min, Bomi Lim, Sunhyoung Kwon, Sungjun Ahn
- 세션 : Session 15 — Advanced PHY Techniques, MIMO Transmission, and Coverage Planning for TV 3.0 and ATSC 3.0 (7월 9일 16:00~17:00, Topazio Room)

국내 ATSC 3.0 본방송 환경에서 발생하는 약 2.5초 수준의 종단 간 지연을 영상 처리, 전송·다중화, 방송 게이트웨이, SFN 동기화, 수신기 버퍼링 등 기술 요소별로 정량 분석하였다. 이를 통해 지진·쓰나미 등 초를 다투는 재난경보 전송의 경우 기존 표준을 변경하지 않고도 운용 설정 최적화만으로 종단 간 지연을 약 0.25초 수준까지 줄일 수 있음을 제시하였다.

![IEEE BMSB 2026 최우수 논문상 수상](/images/BMSB2026_JoaoPessoa_Award.jpg)

<small>사진 = 방송기술저널</small>

**□ 언론 보도 — 방송기술저널**

방송기술저널(백선하 기자, 2026년 7월 10일)은 이번 수상을 「[ETRI·MBC·KBS 공동연구팀, IEEE BMSB 최우수 논문상 수상](http://journal.kobeta.com/etri%C2%B7mbc%C2%B7kbs-%EC%97%B0%EA%B5%AC%ED%8C%80-ieee-bmsb-%EC%B5%9C%EC%9A%B0%EC%88%98-%EB%85%BC%EB%AC%B8%EC%83%81-%EC%88%98%EC%83%81/)」으로 보도하였다. 기사의 요지는 다음과 같다.

- 세계 최초로 ATSC 3.0 UHD 본방송을 시작하고 전국 단일주파수망(SFN)을 운영해 온 한국 방송계의 축적된 운용 경험을 바탕으로, 실제 본방송망의 종단 간 지연 특성을 실측 기반으로 규명한 연구 성과라는 점에서 의미가 크다.
- 이번 연구는 ATSC 3.0 실방송망의 지연 특성을 실제 운용 관점에서 확인하고, 향후 방송망 기반 데이터 서비스의 성능 요구사항을 검토할 수 있는 기술적 기준을 마련하였다는 평가다.
- 공동연구팀은 이번 성과를 바탕으로 MBC가 추진 중인 방송망 기반 고정밀 위치보정정보(RTK) 전송 기술과 연계하여, ATSC 3.0 데이터캐스팅(Datacasting) 저지연 전송 최적화 연구를 지속적으로 심화·발전시켜 나갈 계획이다.
- IEEE BMSB는 IEEE Broadcast Technology Society(BTS)가 매년 개최하는 학술대회로, 방송·광대역 통신·가전·네트워킹 기술의 융합과 관련된 최신 기술 트렌드를 공유하는 대표적인 장이다.

**□ 제1저자 구두 발표 — Hybrid ATSC 3.0/LTE RTK**

- 논문 : *Coverage Overlap & Outage Bounding in Hybrid ATSC3.0/LTE RTK Delivery — A Four-Region Field Digest* (Paper 107)
- 저자 : **Sungho Jeon**, Hong-Gi Shin, Doo-Kyung Park, Dong-Kwan Lee, Seung-Ho Lee (MBC), Sung-Ik Park (ETRI)
- 세션 : Session 17 — Advanced Physical Layer Performance and Interference Studies for ATSC 3.0 and TV 3.0 (7월 10일 10:30~12:10, Topazio Room)

핵심 주장은 "Hybrid ATSC/LTE RTK는 단순 이중화가 아니라 양방향 tail-risk 헤지"라는 것이다. 2개 대륙 4개 지역(한국, Washington DC, Denver, Salt Lake City)에서 137,480 샘플, 38.19시간을 수집하여 다음을 확인하였다.

- ATSC 3.0 방송 커버리지가 부분적인 지역(SLC 30.6%)에서도 either-path lock이 96.3~100%로 유지되며, 두 경로의 동시 실패는 3.67% 이하였다. 즉 두 경로의 실패가 충분히 비상관적이다.
- 서비스 레벨 outage의 꼬리(tail)가 크게 짧아진다. Denver 기준 P99 outage가 LTE-only 582.9초에서 Hybrid 39.9초로 감소하였다.
- 보완 방향은 지역에 따라 자동으로 뒤바뀐다. 한국(터널·협곡 등 방송 음영)에서는 LTE가 ATSC를 보완하고, Denver·SLC(셀룰러 취약 지형)에서는 ATSC가 LTE를 보완한다.
- 잔존 outage의 67~91%는 커버리지 공백이 아니라 RTCM integrity/timeout 처리에서 비롯되어, 추가 인프라 없이 펌웨어 개선만으로도 개선 여지가 크다.
- 방송 커버리지에 비례한 셀룰러 오프로딩이 이루어져, Washington DC에서는 셀룰러 트래픽의 89.9%를 방송으로 대체하였다.

**□ 공저 발표 — BPS 기반 전국 시각 동기**

- 논문 : *Nationwide Time Sourcing Based on Terrestrial Broadcast Networks: BPS Project* (Paper 27)
- 저자 : Sungjun Ahn, **Sungho Jeon**, Jaekwon Lee, Sunhyoung Kwon, Sung-Ik Park
- 세션 : Session 4 — BPS, Antenna Array and Heterogeneous SFN (7월 8일 14:00~15:40, Topazio Room)

**□ 좌장 — Session 12: ITCN, GSL and 6G Broadcasting**

- 일시/장소 : 7월 9일(목) 10:30~12:10, Rubi Room
- 좌장 : Josemar Cruz, **Sungho Jeon**
- 발표 논문 5편 : ATSC 3.0 ITCN 데이터 시그널링(Paper 26), ITCN full-duplex 루프백 신호 제거 하드웨어 프로토타입(Paper 44), SFN 지역 콘텐츠 삽입(LCI) 프로토타입 및 동일채널 간섭 시험(Paper 96), ATSC 3.0 저복잡도·학습 기반 자기간섭 제거(Paper 112), 6G Multicast/Broadcast와 NTN 기회(Paper 147)

**□ 발표자료**

- [IEEE BMSB 2026 발표자료 — *Coverage Overlap & Outage Bounding in Hybrid ATSC3.0/LTE RTK Delivery — A Four-Region Field Digest*](https://drive.google.com/file/d/1KYNJYx1FKDoI528iMg57-XRkMwc5wEFH/preview)
