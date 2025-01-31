# 패키지 불러오기
import pandas as pd
from flask import Flask, render_template, request, jsonify
import datetime
import folium
import json
from folium import Marker
from keras.models import load_model

app = Flask(__name__)
app.config["SECRET_KEY"] = 'd2707fea9778e085491e2dbbc73ff30e'

# 함수 선언 부분
def str_2words(word):
    word = str(word)
    if len(word)==1:
        word='0'+word
    return word

# 고정 변수 선언
start_coords = [35.8, 128.6]	# 지도 시작 좌표
region_fact = ['동인동', '삼덕동', '성내1동', '성내2동', '성내3동', '대신동', '남산1동', '남산2동', '남산3동', '남산4동', '대봉1동', '대봉2동',
 '신암1동', '신암2동', '신암3동', '신암4동', '신암5동', '신천1.2동', '신천3동', '신천4동', '효목1동', '효목2동', '도평동', '불로.봉무동',
 '지저동', '동촌동', '방촌동', '해안동', '안심1동', '안심2동', '안심3동', '안심3.4동', '안심4동', '혁신동', '공산동', '내당1동', '내당2.3동',
 '내당4동', '비산1동', '비산2.3동', '비산4동', '비산5동', '비산6동', '비산7동', '평리1동', '평리2동', '평리3동', '평리4동', '평리5동',
 '평리6동', '상중이동', '원대동', '이천동', '봉덕1동', '봉덕2동', '봉덕3동', '대명1동', '대명2동', '대명3동', '대명4동', '대명5동', '대명6동',
 '대명9동', '대명10동', '대명11동', '고성동', '칠성동', '침산1동', '침산2동', '침산3동', '산격1동', '산격2동', '산격3동', '산격4동', '대현동',
 '복현1동', '복현2동', '검단동', '무태조야동', '관문동', '태전1동', '태전2동', '구암동', '관음동', '읍내동', '동천동', '노원동', '국우동',
 '범어1동', '범어2동', '범어3동', '범어4동', '만촌1동', '만촌2동', '만촌3동', '수성1가동', '수성2.3가동', '수성4가동', '황금1동', '황금2동',
 '중동', '상동', '파동', '두산동', '지산1동', '지산2동', '범물1동', '범물2동', '고산1동', '고산2동', '고산3동', '성당동', '두류1.2동', '두류3동',
 '감삼동', '죽전동', '장기동', '용산1동', '용산2동', '이곡1동', '이곡2동', '신당동', '본리동', '월성1동', '월성2동', '진천동', '상인1동',
 '상인2동', '상인3동', '도원동', '송현1동', '송현2동', '본동', '화원읍', '논공읍', '다사읍', '유가읍', '옥포읍', '현풍읍', '가창면', '하빈면',
 '구지면']		# factorize 된 지역
model = load_model('model/model_2.0546_2.0417.h5')		# 미리 학습된 모델 불러오기

# 읍면동 드롭다운에서 사용할 목록을 불러오는 함수
def get_dropdown_values():
    class_entry_relations = {
		'중구':{'동인동','삼덕동','성내1동','성내2동','성내3동','대신동','남산1동','남산2동','남산3동','남산4동','대봉1동','대봉2동'},
		'동구':{'신암1동','신암2동','신암3동','신암4동','신암5동','신천1.2동','신천3동','신천4동','효목1동','효목2동','도평동',
				'불로.봉무동','지저동','동촌동','방촌동','해안동','안심1동','안심2동','안심3동','안심4동','혁신동','공산동'},
		'서구':{'내당1동','내당2.3동','내당4동','비산1동','비산2.3동','비산4동','비산5동','비산6동','비산7동','평리1동','평리2동',
				'평리3동','평리4동','평리5동','평리6동','상중이동','원대동'},
		'남구':{'이천동','봉덕1동','봉덕2동','봉덕3동','대명1동','대명2동','대명3동','대명4동','대명5동','대명6동','대명9동',
				'대명10동','대명11동'},
		'북구':{'고성동','칠성동','침산1동','침산2동','침산3동','산격1동','산격2동','산격3동','산격4동','대현동','복현1동','복현2동',
				'검단동','무태조야동','관문동','태전1동','태전2동','구암동','관음동','읍내동','동천동','노원동','국우동'},
		'수성구':{'범어1동','범어2동','범어3동','범어4동','만촌1동','만촌2동','만촌3동','수성1가동','수성2.3가동','수성4가동',
				'황금1동','황금2동','중동','상동','파동','두산동','지산1동','지산2동','범물1동','범물2동','고산1동','고산2동','고산3동'},
		'달서구':{'성당동','두류1.2동','두류3동','감삼동','죽전동','장기동','용산1동','용산2동','이곡1동','이곡2동','신당동','본리동',
				'월성1동','월성2동','진천동','유천동','상인1동','상인2동','상인3동','도원동','송현1동','송현2동','본동'},
		'달성군':{'화원읍','논공읍','다사읍','유가읍','옥포읍','현풍읍','가창면','하빈면','구지면'}
	}                        
    return class_entry_relations

# 읍면동 드롭다운의 자바스크립트 반응형 페이지
@app.route('/_update_dropdown')
def update_dropdown():
    # 자바스크립트에서 현재 선택된 항목 읽어옴
    selected_class = request.args.get('selected_class', type=str)
    # 선택된 항목에서 사용되는 dropdown의 항목을 읽어오기
    updated_values = get_dropdown_values()[selected_class]
    # 리스트 형식에서 JSON 형태로 변경
    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)
	# JSON으로 반환
    return jsonify(html_string_selected=html_string_selected)

# 예측된 데이터를 출력하기 위한 자바스크립트 반응형 페이지
@app.route('/_process_data')
def process_data():
	# 자바스크립트에서 현재 선택된 항목 읽어옴
	selected_entry = request.args.get('selected_entry', type=str)
	# 실시간 수집된 데이터 불러오기
	df = pd.read_csv('./output/Daegu_data.csv')
	df.drop(['long','lat'], axis=1, inplace=True)
	# 선택된 지역만 남기기
	df = df[df['region']==selected_entry]
	df['region'] = region_fact.index(selected_entry)
	# 예측을 위한 데이터 변형
	df = df.iloc[-73:,:]
	column_list = []
	for i in range(1, 73):
		for j in ['temp','rainfall','humidity','wind_speed','wind_direction']:
			col_temp = 'next_' + j + '_h' + str(i)
			column_list.append(col_temp)
			df[col_temp] = df[j].shift(i)
	df.dropna(inplace=True)
	# 예측
	y = model.predict(df)
	# 예측 된 값 출력을 위한 문자열 처리
	temps = list(y[0])
	now_hour = df.iloc[0,3]
	list_temp = []
	if now_hour == 23:
		now_hour = -1
	hour72 = 0
	for i in range(24):
		list_temp.append(str(i)+'h\t')
	for i in range(96):
		if now_hour >= 0:
			list_temp[i%24] = list_temp[i%24] + '\t\t'
			now_hour = now_hour - 1
		elif hour72 < 72:
			if i < 72:
				list_temp[i%24] = list_temp[i%24] + str(temps[hour72]) + '\t'
			else:
				list_temp[i%24] = list_temp[i%24] + str(temps[hour72])
			hour72 = hour72 + 1
		else:
			list_temp[i%24] = list_temp[i%24]
	text = ''
	for i in list_temp:
		text += i
		text += '\n'
	# JSON 형태로 반환
	return jsonify(result = text)

@app.route('/')
def home():
	# 실시간 수집된 데이터 불러오기
	df = pd.read_csv('./output/Daegu_data.csv')
	# 현재 시각
	now = str(datetime.datetime.now())
	# 드롭다운 기본 데이터
	default_classes = ['중구','동구','서구','남구','북구','수성구','달서구','달성군']
	default_value = get_dropdown_values()['중구']
	# 대구 지도 생성
	m = folium.Map(location=start_coords, zoom_start=10, tiles='cartodbpositron')
	# GeoJSON으로 대구 읍면동 지역 구분
	rr = json.load(open('dataset/HangJeongDong.geojson', encoding='utf-8'))
	folium.GeoJson(rr, name='지역구').add_to(m)
	# 제일 최신 데이터만 선택
	df_daegu=df.iloc[-142:,:]
	# 기온에 따라 핀의 색상을 바꿔가며 핀 새성
	for lat, long, region, temp in zip(df_daegu['lat'], df_daegu['long'], df_daegu['region'], df_daegu['temp']):
		if temp > 30:
			Marker([lat, long], icon = folium.Icon(color='red'), popup=str(temp)+'℃ '+region).add_to(m)
		elif temp > 25:
			Marker([lat, long], icon = folium.Icon(color='orange'), popup=str(temp)+'℃ '+region).add_to(m)
		elif temp > 20:
			Marker([lat, long], icon = folium.Icon(color='green'), popup=str(temp)+'℃ '+region).add_to(m)
		else:
			Marker([lat, long], icon = folium.Icon(color='blue'), popup=str(temp)+'℃ '+region).add_to(m)
	# '/'에 해당하는 html 반환
	return render_template('layout.html', 
							all_classes=default_classes,
							all_entries=default_value,
							now=now,
							map=m._repr_html_()
							)

if __name__ == '__main__':
	app.run(debug=True)