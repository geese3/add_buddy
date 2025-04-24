import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import time
import json
import urllib.request
import random
from datetime import datetime
import undetected_chromedriver as uc  
import pyperclip
import platform  

class NaverBlogAutomation:
    def __init__(self, log_callback=None):
        # OS 확인
        self.is_mac = platform.system() == 'Darwin'
        
        # Chrome 옵션 설정
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1')
        # chrome_options.add_argument('--headless')  # headless 모드 항상 사용
        
        self.driver = uc.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        load_dotenv()
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        
        # 로그 파일 설정
        self.log_file = f"neighbor_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.log_callback = log_callback

    def log_activity(self, message):
        """활동 로그를 파일에 저장"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        # 파일에도 저장
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        # 콜백이 있으면 GUI로도 전달
        if self.log_callback:
            self.log_callback(message)
        # print도 유지(필요시)
        print(log_message.strip())  # 콘솔 출력

    def search_blogs(self, keyword, display=100):
        """네이버 검색 API를 사용하여 블로그 검색"""
        try:
            encText = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={display}"
            
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)
            
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                response_body = response.read().decode('utf-8')
                return json.loads(response_body)
            
            self.log_activity(f"검색 API 오류: {response.getcode()}")
            return None
            
        except Exception as e:
            self.log_activity(f"검색 중 오류 발생: {str(e)}")
            return None

    def copy_paste_text(self, element, text):
        """OS에 따라 다른 단축키로 텍스트를 복사/붙여넣기하는 함수"""
        # 텍스트를 클립보드에 복사
        pyperclip.copy(text)
        time.sleep(0.5)
        
        # 요소 클릭
        element.click()
        time.sleep(0.5)
        
        # OS에 따라 다른 단축키 사용
        if self.is_mac:  # Mac OS
            # Command + V (붙여넣기)
            actions = ActionChains(self.driver)
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND)
            actions.perform()
        else:  # Windows
            # Ctrl + V (붙여넣기)
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
            actions.perform()
        
        time.sleep(0.5)

    def login_naver(self, id, password):
        """네이버 로그인"""
        try:
            self.driver.get('https://nid.naver.com/nidlogin.login')
            time.sleep(2)
            
            # 아이디 입력
            id_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_id")))
            self.copy_paste_text(id_input, id)
            
            # 비밀번호 입력
            pw_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_pw")))
            self.copy_paste_text(pw_input, password)
            
            # 로그인 버튼 클릭
            login_button = self.wait.until(EC.presence_of_element_located((By.ID, "log.login")))
            login_button.click()
            time.sleep(3)
            
            # 로그인 성공 확인
            try:
                current_title = self.driver.title
                if current_title and "로그인" in current_title:
                    self.log_activity("로그인 실패: 보안 문제 발생")
                    print("\n[알림] 캡차나 보안 문제가 발생했습니다.")
                    print("브라우저에서 직접 로그인을 진행해주세요.")
                    time.sleep(10)  # 10초 대기 후 자동 진행(필요시 조정)
            except Exception as e:
                self.log_activity(f"로그인 상태 확인 중 오류: {str(e)}")
                print("\n[알림] 로그인 상태 확인 중 문제가 발생했습니다.")
                print("브라우저에서 직접 로그인을 진행해주세요.")
                time.sleep(10)
            
            self.log_activity("로그인 성공")
            
        except Exception as e:
            self.log_activity(f"로그인 실패: {str(e)}")
            print("\n[알림] 자동 로그인 실패")
            print("브라우저에서 직접 로그인을 진행해주세요.")
            time.sleep(10)
            self.log_activity("수동 로그인 완료")

    def is_already_neighbor(self):
        """이미 이웃 관계인지 확인"""
        try:
            # 이미 이웃 상태 확인
            buddy_state = self.driver.find_elements(By.CLASS_NAME, 'buddy_state')
            if buddy_state and "서로이웃" in buddy_state[0].text:
                return True
            return False
        except:
            return False

    def add_neighbor(self, blog_id, message="안녕하세요. 관심사가 비슷한 것 같아 서로이웃 신청드립니다. 앞으로 함께 성장해나가면 좋겠습니다."):
        """블로그 이웃 추가"""
        try:
            # 모바일 버전 URL로 접근
            blog_url = f"http://m.blog.naver.com/BuddyAddForm.naver?blogId={blog_id}&returnUrl=https%253A%252F%252Fm.blog.naver.com%252F"
            self.driver.get(blog_url)
            time.sleep(random.uniform(2, 3))
            
            # 이미 진행 중인 이웃 신청 확인
            try:
                exceptional_text = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'dsc'))
                ).text
                
                if "진행중" in exceptional_text or "제한된" in exceptional_text:
                    self.log_activity(f"이미 이웃 신청이 진행 중입니다: {blog_id}")
                    return None  # None을 반환하여 다음 블로그로 넘어가도록 함
            except:
                pass
            
            # 서로이웃 체크박스 선택
            try:
                checkbox = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//label[contains(text(), "서로이웃")]/preceding-sibling::input'))
                )
                if not checkbox.is_enabled():
                    self.log_activity(f"서로이웃 추가가 불가능합니다: {blog_id}")
                    return None  # None을 반환하여 다음 블로그로 넘어가도록 함
                
                checkbox.click()
                time.sleep(random.uniform(1, 2))
                self.log_activity("서로이웃 체크박스 클릭 완료")
            except Exception as e:
                self.log_activity(f"서로이웃 체크박스 선택 실패: {str(e)}")
                return None  # None을 반환하여 다음 블로그로 넘어가도록 함
            
            # 메시지 입력
            try:
                textarea = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'textarea')))
                textarea.clear()
                textarea.send_keys(message)
                time.sleep(random.uniform(1, 2))
                self.log_activity("메시지 입력 완료")
            except Exception as e:
                self.log_activity(f"메시지 입력 실패: {str(e)}")
                return False
            
            # 확인 버튼 클릭
            try:
                confirm_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn_ok')))
                confirm_button.click()
                time.sleep(random.uniform(2, 3))
                self.log_activity(f"이웃 추가 성공: {blog_id}")
                return True
            except Exception as e:
                self.log_activity(f"확인 버튼 클릭 실패: {str(e)}")
                return False
            
        except Exception as e:
            self.log_activity(f"이웃 추가 실패 ({blog_id}): {str(e)}")
            return False

    def process_keyword(self, keyword, max_blogs=50, message=None):
        """키워드로 블로그 검색 및 이웃 추가 진행"""
        self.log_activity(f"키워드 '{keyword}' 처리 시작")
        
        # 블로그 검색
        search_results = self.search_blogs(keyword)
        if not search_results:
            self.log_activity("검색 결과를 가져오는데 실패했습니다.")
            return
        
        success_count = 0
        processed_count = 0
        for idx, item in enumerate(search_results['items'], 1):
            if processed_count >= max_blogs:
                break
                
            blog_url = item['link']
            try:
                blog_id = blog_url.split('/')[-2]
                self.log_activity(f"처리 중인 블로그 ({processed_count + 1}/{max_blogs}): {blog_id}")
                
                # 이웃 추가 시도
                result = self.add_neighbor(blog_id, message)
                if result is None:  # 이미 이웃이거나 처리 중인 경우
                    self.log_activity(f"다음 블로그로 넘어갑니다.")
                    continue
                elif result:  # 이웃추가 성공
                    success_count += 1
                    self.log_activity(f"이웃 추가 성공! (총 {success_count}개)")
                
                processed_count += 1
                # 네이버 정책 준수를 위한 대기
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                self.log_activity(f"블로그 처리 중 오류: {str(e)}")
                continue
        
        self.log_activity(f"작업 완료! 총 {success_count}개의 블로그와 이웃 맺기 성공")

    def close(self):
        """브라우저 종료"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception as e:
            print(f"브라우저 종료 중 오류 발생: {str(e)}")
        finally:
            self.log_activity("프로그램 종료")

def main():
    print("네이버 블로그 자동 이웃 추가 프로그램")
    print("-" * 50)
    
    bot = None
    try:
        print("[main 함수는 GUI 환경에서는 사용되지 않습니다]")
        return
        
        # 아래는 CLI 테스트용 코드(주석 처리)
        # naver_id = input("네이버 아이디를 입력하세요: ")
        # naver_pw = input("네이버 비밀번호를 입력하세요: ")
        # keyword = input("검색할 키워드를 입력하세요: ")
        # max_blogs = int(input("최대 몇 개의 블로그와 이웃을 맺을까요? (기본: 50): ") or "50")
        # message = input("이웃추가 메시지를 입력하세요 (기본: ...): ") or "..."
        
        # bot = NaverBlogAutomation()
        # bot.login_naver(naver_id, naver_pw)
        # bot.process_keyword(keyword, max_blogs, message)
        
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        pass

if __name__ == "__main__":
    main()