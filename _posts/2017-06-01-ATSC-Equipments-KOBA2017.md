---
layout: post
title: ATSC3.0 방송장비 동향 / KOBA2017 출품장비를 중심으로 
---

**[알림] 본 원고는 한국방송기술인연합회 ['방송과 기술' 2017년 6월호](http://tech.kobeta.com/ccccc/)에 출판되었습니다.**

## 송신장비 동향

송신장비 동향은 [그림 3]과 같이 크게, ① 브로드캐스트 게이트웨이(Broadcast Gateway)와 송신기 엑사이터(Exciter) 같이 송신 계통에 직접 설치되는 장치와 ② 송신망 운용 및 관리를 위한 STLTP(Studio-to-Transmitter Link Transport Protocol) 모니터링 장치와 RF 모니터링 장치로 나눠볼 수 있다.

![그림 1](/images/KOBA2017_Equipment1.jpg)

#### Broadcast Gateway와 Exciter

##### Broadcast Gateway

Broadcast Gateway 장비는 A/324 표준을 기반으로 구현되는 ‘SFN 송신기 제어기’이다. Broadcast Gateway에는 MMT/ROUTE 형태의 오디오/비디오 데이터와 시그널링 정보가 입력되고, 출력 신호는 마이크로웨이브망이나 유선 IP망을 통해서 각 송신소에 전달된다. 아직까지 후보표준(Candidate Standard) 단계인 A/324 문서는 현재 Maximum Network Delay(MND) 기능을 포함하는 몇 가지 기술에 대한 개정 작업이 논의 중에 있어서, 본방송 이후에도 지속적으로 기술 개정에 따른 펌웨어 업그레이드가 예상되고, 이에 따라 Exciter와의 정합에 있어서 문제가 발생하지 않는지 확인이 필요할 것으로 예측된다.
이번 KOBA 2017에는 [그림 4]과 같이, 3개 업체에서 Broadcast Gateway 장비를 전시하였다. 

##### Exciter

Exciter 장비의 경우, A/321과 A/322 표준에 따라 구현되는 데, Broadcast Gateway 출력 신호를 STLTP를 통해서 입력받아서 RF 신호로 변환하는 장치이다. 본방송을 위한 1단계 수도권 송신기 구축 결과를 보면, KBS/MBC/SBS 모두 관악산 5kW, 남산 5kW, 광교 2kW 송신기를 설치하였고, MBC는 추가로 용문산 2kW, SBS는 여기에 더해 목동 900W 송신기를 설치하였다. 우리나라 기술기준에 따르면(‘방송표준방식 및 방송업무용 무선설비의 기술기준’제4조제1항, 방송국에는 방송중단사고를 예방하고 송신신호를 안정하게 공급하는데 필요한 예비송신장치 및 예비전원장치를 비치하여야 한다. 다만, 안테나공급전력이 1 ㎾ 미만인 경우는 제외한다.), 지상파 UHD 방송의 경우 1kW 이상 출력을 내는 송신소에는 안정적인 방송 신호 공급을 위해서 ‘예비장치’를 의무적으로 두도록 하고 있어서, 1kW 이상 송신소용과 1kW 미만 중계소용으로 UHD 송신기를 분류할 수 있다.
이번 KOBA 2017에는 [그림 5]과 같이, 3개 업체에서 고출력 송신기를 전시하였다. 

#### STPTP 모니터링 장치와 RF 모니터링 장치



![그림 2](/images/KOBA2017_Equipment2.jpg)

## 공시청용 UHD 신호처리기 동향

![그림 3](/images/KOBA2017_Equipment3.jpg)
