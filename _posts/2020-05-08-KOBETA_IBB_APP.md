---
layout: post
title: KBS1 UHD 채널 재난정보 부가서비스(IBB App) 개발
---

**[알림] 본 원고는 한국방송기술인연합회 ['방송과 기술' 2020년 5월호](http://tech.kobeta.com/%eb%b0%a9%ec%86%a1%ea%b3%bc%ea%b8%b0%ec%88%a0-2017%eb%85%84-5%ec%9b%94%ed%98%b8vol-257-%ec%95%88%eb%82%b4-2/)에 출판되었습니다.**

* 글쓴이 : 정다운, 남진솔, 이우형, 전성호, 이병호 (KBS 미디어송출부)

※ IBB(Integrated Broadcast Broadband)는 사용자가 지상파 UHD 실시간 방송을 시청하면서, 방송망(Broadcast)과 브로드밴드(Broadband)를 통해 풍성한 부가 서비스를 제공하기 위한 서비스 표준임.

  KBS에서는 코로나19 확산 억제를 위해 정확한 정보를 신속하게 전파하기 위한 창구로 IBB 앱을 개발하고 수도권은 4월 6일, 광역시권은 4월 13일부터 서비스를 KBS 1TV를 통해 개시하였다. 지상파 UHD 방송은 IP(Internet Protocol) 기반의 ATSC 3.0 표준을 채택함으로써 ‘방송망(Broadcast)’과 ‘통신망(Broadband)’ 연동이 쉬운데, 특히 국내에서는 TTA ‘지상파 UHD IBB 서비스’ 표준에서 방송망과 통신망을 연동하는 기술을 규정하고 있다.  본 원고는 국내 IBB 표준을 기반으로 개발하고 실제 본방송에 적용한 서비스 개발 내용을 공유하고자 한다.
