# 🍜 matjipyojeong

지역기반 식당 정보를 제공하는 라이브러리입니다.

</br>

## ✨ 기능 소개

- 지역(도시/구/동), 업종, 메뉴, 역 정보를 기반으로 추천
- JSON 기반 식당 데이터 처리
- 간단한 자연어 입력으로 자동 필터링

</br>

## 📦 설치 방법

```bash
git clone https://github.com/yourusername/matjipyojeong.git
cd matjipyojeong
pip install .
```

</br>

## 사용예시

```bash
from matjipyojeong import search_restaurants

result = search_restaurants("성수동 맛집 알려줘")

if isinstance(result, dict):
    print(f"상호 : {result['restaurant_name']}")
    print(f"업종 : {result['restaurant_type']}")
    print(f"주소 : {result['address']}")
    print(f"대표메뉴 : {result['main_menu']}")
    print(f"주변역 : {result['station']}")
    print(f"링크 : {result['link']}") # 네이버 또는 카카오 링크 제공
else:
    print(result)  # 예: "정보가 없습니다." 메시지 출력
```

</br>

## 📝 라이선스

이 프로젝트는 MIT 라이선스에 따라 자유롭게 사용할 수 있습니다.  
자세한 내용은 [LICENSE](./LICENSE) 파일을 확인하세요.

</br>
