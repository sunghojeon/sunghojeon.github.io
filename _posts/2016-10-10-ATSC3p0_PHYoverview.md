---
layout: post
title: 방송망 구축을 위한 ATSC 3.0 전송 기술 
---

**[알림] 본 원고는 한국정보통신기술협회 ['TTA 저널 2016년 09월 167호'](http://www.tta.or.kr/data/reporthosulist_view.jsp?kind_num=1&hosu=167)에 출판되었습니다.**

[본문 다운로드](www.tta.or.kr/data/reportDown.jsp?news_num=4619)

## 1. 머리말

  전송 기술은 장치로 보면 [그림 1] ATSC3.0 시스템 구성도 상에서 브로드캐스트 게이트웨이(Broadcast Gateway)와 송신기(Transmitter)를 말하며, [표 1]에 나열된 ATSC3.0 표준 기구 산하 TG3/S32 Specialist Group on Physical Layer에서 만든 A/320번대 표준 문서를 그 범위로 한다. 우리나라의 경우, KBS1/MBC/SBS의 경우 권역별 단일 주파수 방송망(SFN; Single Frequency Network)을, KBS2/EBS의 경우 전국 SFN으로 구축되므로, 브로드캐스트 게이트웨이에 다수 개의 송신기가 연결되는 SFN 형태가 기본이 된다.
  
  전송 파라미터 관점에서 기존 디지털 방송 표준들과 가장 큰 차이점은, 기존 ATSC1.0 DTV나 T-DMB와 같이 전송 파라미터가 단 한가지로 고정되어 있는 것이 아니라, 서비스 전송률이나 목표 수신 환경에 따라 각 방송사별로 다양하게 전송 파라미터를 조합해 사용할 수 있는 점이다.
  
  장치 연결 관점에서 큰 차이점은, 기존 MPEG2-TS(Transport Stream) 대신 IP Packet 형태로 스트림이 전달된다는 점이며, 이 때문에 BNC 동축 케이블 대신에 RJ-45 이더넷 케이블로 연결된다는 점이다. [그림 1]에서 보면, 브로드캐스트 게이트웨이는 Studio Interface를 통해 ALP(ATSC Link-Layer Protocol) 패킷을 입력받아 STL(Studio-to-Transmitter Link) Interface를 통해 BBP(BaseBand Packet)을 출력하는데, 이더넷 케이블을 통해서 입출력 가능하도록 RTP/UDP/IP 형태의 표준 인터넷 프로토콜 기반 전달 형식을 사용한다.
  
  본 원고에서는 2017년 본방송 시스템 구축에 필요한 내용을 중심으로 ATSC3.0 전송 표준 기술을 살펴보고자 한다.

![그림 1](/images/KOBA2016_Equipment_1.JPG)

![표 1]

| 문서번호  | 문서 이름과 의미                                  |
|----------|-------------------------------------------------|
| A/321    | System Discovery and Signaling                  |
|          | aaa                                             |
| A/322    | Physical Layer Protocol                         |
|          | bbb                                             |
| A/324    | Scheduler / Studio to Transmitter Link          |
|          | ccc                                             |
| A/325    | Recommended Practice: Lab Performance Test Plan |
|          | ddd                                             |
| A/326    | Recommended Practice: Field Test Plan           |
|          | eee                                             |
