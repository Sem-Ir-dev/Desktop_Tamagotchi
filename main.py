import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QWidget, QDialog, QVBoxLayout
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
import webbrowser


class MemeWindow(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Мем от котика")
        layout = QVBoxLayout(self)

        label = QLabel(self)
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        layout.addWidget(label)
        self.setLayout(layout)

class SpeechBubble(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.text = text
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self.font = QFont("Comic Sans MS", 14)
        self.padding = 26
        self.tail_size = 10

        # измерим текст и выставим размер окна
        metrics = QApplication.fontMetrics()
        text_width = metrics.width(text)
        text_height = metrics.height()
        w = text_width + self.padding * 8
        h = text_height + self.padding * 2 + self.tail_size
        self.resize(w, h)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # фон облачка
        p.setBrush(QColor(255, 255, 255))
        p.setPen(QColor(0, 0, 0))

        rect = self.rect().adjusted(0, 0, 0, -self.tail_size)
        p.drawRoundedRect(rect, 15, 15)

        # текст
        p.setFont(self.font)
        p.drawText(rect, Qt.AlignCenter, self.text)

class Cat(QLabel):
    def __init__(self):
        super().__init__()

        # окно без рамки, с прозрачным фоном, всегда сверху
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # запуск таймера мемов
        self.meme_timer = QTimer()
        self.meme_timer.timeout.connect(self.try_show_meme)
        self.set_random_interval()
        self.skin = 0 # 0 - чёрный, 1 - оранжевый

        # Загружаем все спрайты из папки Sprites
        self.sprites = [{
            "left": [QPixmap("Sprites/black_cat/left1.png"), QPixmap("Sprites/black_cat/left2.png")],
            "right": [QPixmap("Sprites/black_cat/right1.png"), QPixmap("Sprites/black_cat/right2.png")],
            "up": [QPixmap("Sprites/black_cat/up1.png"), QPixmap("Sprites/black_cat/up2.png")],
            "down": [QPixmap("Sprites/black_cat/down1.png"), QPixmap("Sprites/black_cat/down2.png")],
            "front_stand": QPixmap("Sprites/black_cat/front_stand.png"),
            "front_sit": QPixmap("Sprites/black_cat/front_sit.png"),
            "back_sit": QPixmap("Sprites/black_cat/back_sit.png")
        }, {
            "left": [QPixmap("Sprites/orange_cat/left1.png"), QPixmap("Sprites/orange_cat/left2.png")],
            "right": [QPixmap("Sprites/orange_cat/right1.png"), QPixmap("Sprites/orange_cat/right2.png")],
            "up": [QPixmap("Sprites/orange_cat/up1.png"), QPixmap("Sprites/orange_cat/up2.png")],
            "down": [QPixmap("Sprites/orange_cat/down1.png"), QPixmap("Sprites/orange_cat/down2.png")],
            "front_stand": QPixmap("Sprites/orange_cat/front_stand.png"),
            "front_sit": QPixmap("Sprites/orange_cat/front_sit.png"),
            "back_sit": QPixmap("Sprites/orange_cat/back_sit.png")
        }]

        self.cat_words = ['«Мяу!»', '«Мур-мур-мур… (^ ^)»', '*звуки трактора*',
                          '«Шшш… я охочусь за курсором!»', '«Погладь меня через экран 😺»',
                          '«Если не кормишь,\nя всё равно тебя люблю ♥»', '«Ты точно работаешь,\nа не прокрастинируешь? 👀»',
                          '«Эй, а что это у тебя за вкладка\nоткрыта? 🙀»', '«Ой, а это что за кнопочка? тык 😼»',
                          '«Мурр, дай мне погоняться за папками\nна рабочем столе!»',
                          '«Осторожно, я сейчас скину твои файлы\nс рабочего стола! 🙀»',
                          '«А если я сверну тебе окно?\nХе-хе!»', '(о_ О)', '=^o.o^=']

        # начальное состояние
        self.direction = random.choice(["left", "right", "up", "down"])
        self.frame_index = 0
        self.setPixmap(self.sprites[self.skin]["front_stand"])

        # стартовые координаты
        self.pos_x, self.pos_y = 300, 300
        self.speed = 5

        # таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cat)
        self.timer.start(150)

        self.move(self.pos_x, self.pos_y)
        self.show()

        self.setFixedSize(160, 160)
        self._bubbles = []

    # -------------- Таймер для мемов ---------------------------
    def set_random_interval(self):
        # следующее появление мема через 30–90 секунд
        self.meme_timer.start(random.randint(30000, 90000))

    def try_show_meme(self):
        folder = "Meme"
        if not os.path.exists(folder):
            return
        files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        if not files:
            return

        meme = random.choice(files)
        meme_path = os.path.join(folder, meme)

        self.meme_window = MemeWindow(meme_path)
        self.meme_window.show()

        # заново запускаем таймер
        self.set_random_interval()
    # ------------------------------------------------------------

    def update_cat(self):
        # Обновление кадра и позиции котика
        screen = QApplication.primaryScreen().size()

        # иногда котик меняет направление или садится
        if random.randint(0, 100) < 5:
            self.direction = random.choice(["left", "right", "up", "down", "sit_front", "sit_back", "stand"])

        if self.direction == "left":
            self.pos_x -= self.speed
            if self.pos_x < 0:
                self.pos_x = 0
                self.direction = "right"
            self.frame_index = (self.frame_index + 1) % 2
            self.setPixmap(self.sprites[self.skin]["left"][self.frame_index])

        elif self.direction == "right":
            self.pos_x += self.speed
            if self.pos_x > screen.width() - 160:
                self.pos_x = screen.width() - 160
                self.direction = "left"
            self.frame_index = (self.frame_index + 1) % 2
            self.setPixmap(self.sprites[self.skin]["right"][self.frame_index])

        elif self.direction == "up":
            self.pos_y -= self.speed
            if self.pos_y < 0:
                self.pos_y = 0
                self.direction = "down"
            self.frame_index = (self.frame_index + 1) % 2
            self.setPixmap(self.sprites[self.skin]["up"][self.frame_index])

        elif self.direction == "down":
            self.pos_y += self.speed
            if self.pos_y > screen.height() - 160:
                self.pos_y = screen.height() - 160
                self.direction = "up"
            self.frame_index = (self.frame_index + 1) % 2
            self.setPixmap(self.sprites[self.skin]["down"][self.frame_index])

        elif self.direction == "stand":
            self.setPixmap(self.sprites[self.skin]["front_stand"])

        elif self.direction == "sit_front":
            self.setPixmap(self.sprites[self.skin]["front_sit"])

        elif self.direction == "sit_back":
            self.setPixmap(self.sprites[self.skin]["back_sit"])

        # применяем позицию
        self.move(self.pos_x, self.pos_y)

    def show_speech(self, text, timeout_ms=2000):
        # Облачко с текстом над котиком
        bubble = SpeechBubble(text)
        # позиция над котиком
        top_left = self.mapToGlobal(self.rect().topLeft())
        x = top_left.x() + (self.width() - bubble.width()) // 2
        y = top_left.y() - bubble.height() - 5
        bubble.move(x, y)
        bubble.show()
        self._bubbles.append(bubble)

        def cleanup(b=bubble):
            # Стирает облако
            b.close()
            if b in self._bubbles:
                self._bubbles.remove(b)

        QTimer.singleShot(timeout_ms, cleanup)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        elif event.button() == Qt.LeftButton:
            speech = random.choice(self.cat_words)
            self.show_speech(speech)
            QSound.play("meow.wav")  # звук мяуканья

    def change_skin(self):
        if self.skin == 0:
            self.skin = 1
        else:
            self.skin = 0

    def developer(self):
        webbrowser.open("https://github.com/Sem-Ir-dev/")

    def show_context_menu(self, pos):
        menu = QMenu()
        actions = {
            "Поменять скин": self.change_skin,
            "Разработчик": self.developer,
            "Выход": QApplication.quit
        }
        for name, func in actions.items():
            act = menu.addAction(name)
            act.triggered.connect(func)
        menu.exec_(pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Не будет закрывать приложение, при закрытии доп окон
    cat = Cat()
    sys.exit(app.exec_())
