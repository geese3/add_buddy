import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QSpinBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from auto_neighbor import NaverBlogAutomation

class Settings:
    def __init__(self):
        self.settings_file = 'settings.json'
        self.default_settings = {
            'naver_id': '',
            'naver_pw': '',
            'naver_client_id': '',
            'naver_client_secret': '',
            'default_message': '안녕하세요. 관심사가 비슷한 것 같아 서로이웃 신청드립니다. 앞으로 함께 성장해나가면 좋겠습니다.',
            'default_max_blogs': 50
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, naver_id, naver_pw, client_id, client_secret, keyword, max_blogs, message):
        super().__init__()
        self.naver_id = naver_id
        self.naver_pw = naver_pw
        self.client_id = client_id
        self.client_secret = client_secret
        self.keyword = keyword
        self.max_blogs = max_blogs
        self.message = message

    def run(self):
        try:
            bot = NaverBlogAutomation()
            bot.client_id = self.client_id
            bot.client_secret = self.client_secret
            
            # 로그인
            bot.login_naver(self.naver_id, self.naver_pw)
            
            # 이웃추가 진행
            bot.process_keyword(self.keyword, self.max_blogs, self.message)
            
        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
        finally:
            if 'bot' in locals():
                bot.close()
            self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.worker_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('네이버 블로그 이웃추가 프로그램')
        self.setGeometry(100, 100, 600, 500)

        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # API 설정
        api_group = QWidget()
        api_layout = QVBoxLayout(api_group)
        
        # 네이버 API 키
        client_id_layout = QHBoxLayout()
        client_id_label = QLabel('네이버 API Client ID:')
        self.client_id_input = QLineEdit()
        self.client_id_input.setText(self.settings.settings['naver_client_id'])
        client_id_layout.addWidget(client_id_label)
        client_id_layout.addWidget(self.client_id_input)
        api_layout.addLayout(client_id_layout)

        client_secret_layout = QHBoxLayout()
        client_secret_label = QLabel('네이버 API Client Secret:')
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setText(self.settings.settings['naver_client_secret'])
        client_secret_layout.addWidget(client_secret_label)
        client_secret_layout.addWidget(self.client_secret_input)
        api_layout.addLayout(client_secret_layout)

        layout.addWidget(api_group)

        # 로그인 정보
        login_group = QWidget()
        login_layout = QVBoxLayout(login_group)
        
        id_layout = QHBoxLayout()
        id_label = QLabel('네이버 아이디:')
        self.id_input = QLineEdit()
        self.id_input.setText(self.settings.settings['naver_id'])
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        login_layout.addLayout(id_layout)

        pw_layout = QHBoxLayout()
        pw_label = QLabel('네이버 비밀번호:')
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setText(self.settings.settings['naver_pw'])
        pw_layout.addWidget(pw_label)
        pw_layout.addWidget(self.pw_input)
        login_layout.addLayout(pw_layout)

        layout.addWidget(login_group)

        # 검색 설정
        search_group = QWidget()
        search_layout = QVBoxLayout(search_group)
        
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel('검색 키워드:')
        self.keyword_input = QLineEdit()
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        search_layout.addLayout(keyword_layout)

        max_blogs_layout = QHBoxLayout()
        max_blogs_label = QLabel('최대 이웃 추가 수:')
        self.max_blogs_input = QSpinBox()
        self.max_blogs_input.setRange(1, 1000)
        self.max_blogs_input.setValue(self.settings.settings['default_max_blogs'])
        max_blogs_layout.addWidget(max_blogs_label)
        max_blogs_layout.addWidget(self.max_blogs_input)
        search_layout.addLayout(max_blogs_layout)

        layout.addWidget(search_group)

        # 메시지 입력
        message_group = QWidget()
        message_layout = QVBoxLayout(message_group)
        
        message_label = QLabel('이웃추가 메시지:')
        self.message_input = QTextEdit()
        self.message_input.setText(self.settings.settings['default_message'])
        message_layout.addWidget(message_label)
        message_layout.addWidget(self.message_input)

        layout.addWidget(message_group)

        # 로그 출력
        log_label = QLabel('실행 로그:')
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(log_label)
        layout.addWidget(self.log_output)

        # 버튼
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton('설정 저장')
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.start_button = QPushButton('시작')
        self.start_button.clicked.connect(self.start_process)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('중지')
        self.stop_button.clicked.connect(self.stop_process)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

    def save_settings(self):
        self.settings.update_setting('naver_id', self.id_input.text())
        self.settings.update_setting('naver_pw', self.pw_input.text())
        self.settings.update_setting('naver_client_id', self.client_id_input.text())
        self.settings.update_setting('naver_client_secret', self.client_secret_input.text())
        self.settings.update_setting('default_message', self.message_input.toPlainText())
        self.settings.update_setting('default_max_blogs', self.max_blogs_input.value())
        
        QMessageBox.information(self, '설정 저장', '설정이 저장되었습니다.')

    def start_process(self):
        if not all([self.id_input.text(), self.pw_input.text(), 
                   self.client_id_input.text(), self.client_secret_input.text(),
                   self.keyword_input.text()]):
            QMessageBox.warning(self, '입력 오류', '모든 필수 항목을 입력해주세요.')
            return

        self.worker_thread = WorkerThread(
            self.id_input.text(),
            self.pw_input.text(),
            self.client_id_input.text(),
            self.client_secret_input.text(),
            self.keyword_input.text(),
            self.max_blogs_input.value(),
            self.message_input.toPlainText()
        )
        
        self.worker_thread.log_signal.connect(self.update_log)
        self.worker_thread.finished_signal.connect(self.process_finished)
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.worker_thread.start()

    def stop_process(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.update_log("프로세스가 중지되었습니다.")
            self.process_finished()

    def update_log(self, message):
        self.log_output.append(message)

    def process_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 