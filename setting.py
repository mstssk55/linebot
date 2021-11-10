detail_selector_list=[
    ['物件名','#item-detail_header > h1 > span.name'],
    ['住所','#item-detai_basic > div:nth-child(3) > dl:nth-child(2) > dd'],
    ['交通','#item-detai_basic > div:nth-child(3) > dl:nth-child(1) > dd'],
    ['価格','#item-detail > div.liner.gradient.sideline > div > div.paymentInfo.typeLoanSimulation > dl > dd > span'],
    ['専有面積','#item-detai_basic > div:nth-child(2) > dl:nth-child(2) > dd:nth-child(4)'],
    ['築年数','#item-detai_basic > div:nth-child(2) > dl:nth-child(2) > dd:nth-child(2)'],
    # ['階建・階','#item-detai_basic > div:nth-child(2) > dl:nth-child(1) > dd.cell04'],
    # ['間取り','#item-detai_basic > div:nth-child(2) > dl:nth-child(2) > dd.cell04'],
]


kind = [
    "中古マンション",
    "中古戸建て",
    "土地"
]
send_categories = {
    kind[0]:['物件名','所在地','交通','価格','専有面積','築年月'],
    kind[1]:['物件名','所在地','交通','価格','土地面積','築年月'],
    kind[2]:['物件名','所在地','交通','価格','土地面積'],
}

filter_col = {
    kind[0]:[4,5,3,8], #[所在地、交通、価格、専有面積]
    kind[1]:[4,5,3,8], #[所在地、交通、価格、土地面積]
    kind[2]:[4,5,3,6]  #[所在地、交通、価格、土地面積]
}