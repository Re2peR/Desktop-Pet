from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QGuiApplication, QPainter, QPixmap, QPolygon
from PySide6.QtWidgets import QApplication, QMenu, QWidget


APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
FRAME_DIR = APP_DIR / "assets" / "guofeng_frames"
FALLBACK_ASSET_PATH = APP_DIR / "assets" / "deer_sprite_16.png"
PET_SIZE = 112
FOOD_SIZE = 42
SPRITE_COLS = 4
SPRITE_ROWS = 4
ANIMATION_FRAME_MS = 190.0
ROAM_SPEED = 68
SEEK_SPEED = 105


def desktop_bounds() -> QRect:
    screens = QGuiApplication.screens()
    if not screens:
        return QRect(0, 0, 1280, 720)
    result = QRect(screens[0].availableGeometry())
    for screen in screens[1:]:
        result = result.united(screen.availableGeometry())
    return result


def activity_bounds() -> QRect:
    """Keep the pet inside a compact zone at the primary screen's bottom-right."""
    screen = QGuiApplication.primaryScreen()
    available = screen.availableGeometry() if screen else desktop_bounds()
    width = min(available.width(), max(360, min(620, int(available.width() * 0.38))))
    height = min(available.height(), max(300, min(440, int(available.height() * 0.42))))
    return QRect(available.right() - width + 1, available.bottom() - height + 1, width, height)


@dataclass(frozen=True)
class FoodInfo:
    kind: str
    name: str
    color: QColor
    liked: bool


FOODS = (
    FoodInfo("strawberry", "草莓", QColor("#ef5c68"), True),
    FoodInfo("cookie", "小饼干", QColor("#d99851"), True),
    FoodInfo("carrot", "胡萝卜", QColor("#f08b38"), True),
    FoodInfo("broccoli", "西兰花", QColor("#58a95e"), False),
    FoodInfo("lemon", "酸柠檬", QColor("#f3cf45"), False),
)


class FoodWidget(QWidget):
    def __init__(self, info: FoodInfo, position: QPoint):
        super().__init__(None)
        self.info = info
        self.phase = random.random() * math.tau
        self.setFixedSize(FOOD_SIZE, FOOD_SIZE)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.move(position)

    def center(self) -> QPointF:
        return QPointF(self.x() + FOOD_SIZE / 2, self.y() + FOOD_SIZE / 2)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(0, math.sin(self.phase) * 2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 35))
        p.drawEllipse(9, 32, 25, 5)
        p.setBrush(self.info.color)
        if self.info.kind == "cookie":
            p.drawEllipse(8, 7, 27, 27)
            p.setBrush(QColor("#70462f"))
            for x, y in ((15, 14), (26, 13), (20, 24), (29, 26)):
                p.drawEllipse(x, y, 4, 4)
        elif self.info.kind == "strawberry":
            p.drawEllipse(10, 10, 24, 25)
            p.setBrush(QColor("#55a85c"))
            p.drawPolygon(QPolygon([QPoint(14, 12), QPoint(21, 5), QPoint(28, 12)]))
        elif self.info.kind == "carrot":
            p.drawPolygon(QPolygon([QPoint(12, 11), QPoint(32, 15), QPoint(21, 35)]))
            p.setBrush(QColor("#57a95d"))
            p.drawEllipse(12, 6, 10, 10)
            p.drawEllipse(21, 5, 9, 11)
        elif self.info.kind == "broccoli":
            p.setBrush(QColor("#6fba67"))
            p.drawEllipse(8, 7, 16, 17)
            p.drawEllipse(19, 5, 17, 18)
            p.drawEllipse(14, 12, 18, 17)
            p.setBrush(QColor("#569056"))
            p.drawRoundedRect(18, 21, 9, 14, 3, 3)
        else:
            p.drawEllipse(8, 8, 28, 28)
            p.setPen(QColor("#e4ad28"))
            p.drawLine(13, 13, 31, 31)
        p.end()

    def tick(self):
        self.phase += 0.12
        self.update()


class SpeechBubble(QWidget):
    def __init__(self):
        super().__init__(None)
        self.text = ""
        self.remaining_ms = 0
        self.setFixedSize(230, 62)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def say(self, text: str, duration_ms: int = 2800):
        self.text = text
        self.remaining_ms = duration_ms
        self.show()
        self.raise_()
        self.update()

    def tick(self, dt_ms: int, pet: "PetWidget"):
        if not self.isVisible():
            return
        self.remaining_ms -= dt_ms
        if self.remaining_ms <= 0:
            self.hide()
            return
        bounds = desktop_bounds()
        x = int(pet.position.x() + PET_SIZE / 2 - self.width() / 2)
        y = int(pet.position.y() - self.height() + 14)
        x = max(bounds.left(), min(x, bounds.right() - self.width()))
        if y < bounds.top():
            y = int(pet.position.y() + PET_SIZE - 12)
        self.move(x, y)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("#9b704f"))
        p.setBrush(QColor(255, 252, 242, 245))
        p.drawRoundedRect(2, 2, self.width() - 5, self.height() - 14, 13, 13)
        p.drawPolygon(QPolygon([QPoint(self.width() // 2 - 7, self.height() - 13), QPoint(self.width() // 2 + 7, self.height() - 13), QPoint(self.width() // 2, self.height() - 2)]))
        p.setPen(QColor("#5d4032"))
        font_family = "PingFang SC" if sys.platform == "darwin" else "Microsoft YaHei UI"
        p.setFont(QFont(font_family, 9))
        p.drawText(QRect(11, 6, self.width() - 22, self.height() - 24), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.text)
        p.end()


class PetWidget(QWidget):
    LOCKED_STATES = {"happy", "cry", "wave", "headpat", "bellyrub", "sleepy", "ticklish"}

    def __init__(self, app_controller: "DesktopPetApp"):
        super().__init__(None)
        self.controller = app_controller
        self.frames: list[QPixmap] = []
        self.load_frames()
        self.setFixedSize(PET_SIZE, PET_SIZE)
        self.setWindowTitle("古风桌宠")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        bounds = activity_bounds()
        self.position = QPointF(bounds.center().x() - PET_SIZE / 2, bounds.bottom() - PET_SIZE)
        self.target = QPointF(self.position)
        self.state = "idle"
        self.state_until = 0
        self.focus_food: FoodWidget | None = None
        self.pending_food: FoodInfo | None = None
        self.facing_left = False
        self.dragging = False
        self.drag_moved = False
        self.drag_offset = QPoint()
        self.press_global = QPoint()
        self.press_local = QPoint()
        self.anim_phase = 0.0
        self.elapsed_ms = 0
        self.choose_new_target()
        self.move(self.position.toPoint())

    def load_frames(self):
        frame_paths = sorted(FRAME_DIR.glob("frame_*.png"))
        if len(frame_paths) == 60:
            for path in frame_paths:
                frame = QPixmap(str(path))
                self.frames.append(frame.scaled(PET_SIZE, PET_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            return
        sheet = QPixmap(str(FALLBACK_ASSET_PATH))
        if sheet.isNull():
            return
        cell_w = sheet.width() // SPRITE_COLS
        cell_h = sheet.height() // SPRITE_ROWS
        for row in range(SPRITE_ROWS):
            for col in range(SPRITE_COLS):
                frame = sheet.copy(col * cell_w, row * cell_h, cell_w, cell_h)
                self.frames.append(frame.scaled(PET_SIZE, PET_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def center(self) -> QPointF:
        return QPointF(self.position.x() + PET_SIZE / 2, self.position.y() + PET_SIZE / 2)

    @staticmethod
    def _distance(a: QPointF, b: QPointF) -> float:
        return math.hypot(a.x() - b.x(), a.y() - b.y())

    def choose_new_target(self):
        bounds = activity_bounds().adjusted(12, 12, -PET_SIZE - 12, -PET_SIZE - 12)
        if bounds.width() <= 0 or bounds.height() <= 0:
            return
        if random.random() < 0.45:
            edge = random.randrange(4)
            if edge == 0:
                point = QPointF(random.uniform(bounds.left(), bounds.right()), bounds.top())
            elif edge == 1:
                point = QPointF(bounds.right(), random.uniform(bounds.top(), bounds.bottom()))
            elif edge == 2:
                point = QPointF(random.uniform(bounds.left(), bounds.right()), bounds.bottom())
            else:
                point = QPointF(bounds.left(), random.uniform(bounds.top(), bounds.bottom()))
        else:
            point = QPointF(random.uniform(bounds.left(), bounds.right()), random.uniform(bounds.top(), bounds.bottom()))
        self.target = point
        self.state = "walk"

    def nearest_food(self):
        if not self.controller.foods:
            return None
        return min(self.controller.foods, key=lambda item: self._distance(self.center(), item.center()))

    def react(self, state: str, text: str, duration_ms: int = 2200):
        self.state = state
        self.state_until = self.elapsed_ms + duration_ms
        self.controller.bubble.say(text, duration_ms)
        self.update()

    def update_behavior(self, dt_ms: int):
        self.elapsed_ms += dt_ms
        self.anim_phase += dt_ms / ANIMATION_FRAME_MS
        if self.dragging or self.controller.paused:
            self.update()
            return
        if self.state in self.LOCKED_STATES:
            if self.elapsed_ms >= self.state_until:
                self.choose_new_target()
            self.update()
            return
        if self.state in ("pickup", "eat"):
            if self.elapsed_ms >= self.state_until:
                if self.state == "pickup":
                    self.state = "eat"
                    self.state_until = self.elapsed_ms + 1100
                else:
                    liked = bool(self.pending_food and self.pending_food.liked)
                    name = self.pending_food.name if self.pending_food else "食物"
                    if liked:
                        self.react("happy", f"最喜欢{name}啦！好幸福～", 2300)
                    else:
                        self.react("cry", f"呜……{name}不是我喜欢的味道。", 2400)
                    self.pending_food = None
            self.update()
            return
        if self.state == "spot":
            if self.elapsed_ms >= self.state_until:
                if self.focus_food in self.controller.foods:
                    self.state = "seek"
                else:
                    self.focus_food = None
                    self.choose_new_target()
            self.update()
            return
        food = self.nearest_food()
        if food and self._distance(self.center(), food.center()) < 470:
            if self.state != "seek" or self.focus_food is not food:
                self.focus_food = food
                self.state = "spot"
                self.state_until = self.elapsed_ms + 420
                self.controller.bubble.say(f"咦，是{food.info.name}！", 1300)
                self.update()
                return
            self.target = QPointF(food.x() - PET_SIZE / 2 + FOOD_SIZE / 2, food.y() - PET_SIZE / 2 + FOOD_SIZE / 2)
        elif self._distance(self.position, self.target) < 10:
            if self.state in ("walk", "seek"):
                self.state = "idle"
                self.state_until = self.elapsed_ms + random.randint(900, 2600)
            elif self.elapsed_ms >= self.state_until:
                self.choose_new_target()
        if self.state == "idle":
            if self.elapsed_ms >= self.state_until:
                self.choose_new_target()
            self.update()
            return
        delta = self.target - self.position
        distance = math.hypot(delta.x(), delta.y())
        if distance > 0:
            speed = SEEK_SPEED if self.state == "seek" else ROAM_SPEED
            step = min(distance, speed * dt_ms / 1000.0)
            self.facing_left = delta.x() < 0
            self.position += delta / distance * step
            self.move(self.position.toPoint())
        if self.state == "seek" and food and self._distance(self.center(), food.center()) < 66:
            self.pending_food = food.info
            self.controller.consume(food)
            self.state = "pickup"
            self.state_until = self.elapsed_ms + 650
        self.update()

    def frame_index(self) -> int:
        if self.state == "idle":
            return int(self.anim_phase / 4) % 6
        if self.state in ("walk", "seek"):
            return 6 + (int(self.anim_phase) % 12)
        sequences = {
            "spot": (18, 4, 1),
            "pickup": (22, 4, 1),
            "eat": (26, 6, 1),
            "happy": (32, 6, 1),
            "cry": (38, 6, 1),
            "wave": (44, 6, 1),
            "headpat": (50, 4, 1),
            "bellyrub": (54, 3, 1),
            "sleepy": (57, 2, 2),
            "ticklish": (59, 1, 1),
        }
        start, length, divisor = sequences.get(self.state, (0, 1, 1))
        return start + (int(self.anim_phase / divisor) % length)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bob = math.sin(self.anim_phase * 1.6) * (2.5 if self.state in ("walk", "seek") else 0.8)
        p.translate(PET_SIZE / 2, PET_SIZE / 2 + bob)
        if self.facing_left:
            p.scale(-1, 1)
        p.translate(-PET_SIZE / 2, -PET_SIZE / 2)
        if self.frames:
            p.drawPixmap(0, 0, self.frames[min(self.frame_index(), len(self.frames) - 1)])
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#bd7a45"))
            p.drawEllipse(25, 26, 98, 98)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_moved = False
            self.press_global = event.globalPosition().toPoint()
            self.press_local = event.position().toPoint()
            self.drag_offset = self.press_global - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            current = event.globalPosition().toPoint()
            if (current - self.press_global).manhattanLength() > 5:
                self.drag_moved = True
            if self.drag_moved:
                new_pos = current - self.drag_offset
                bounds = activity_bounds().adjusted(0, 0, -PET_SIZE, -PET_SIZE)
                new_pos.setX(max(bounds.left(), min(new_pos.x(), bounds.right())))
                new_pos.setY(max(bounds.top(), min(new_pos.y(), bounds.bottom())))
                self.position = QPointF(new_pos)
                self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if self.drag_moved:
                self.choose_new_target()
            else:
                self.controller.handle_touch(self.press_local)
            event.accept()

    def contextMenuEvent(self, event):
        self.show_context_menu(event.globalPos())

    def show_context_menu(self, global_pos: QPoint):
        menu = QMenu()
        pause_action = QAction("继续" if self.controller.paused else "暂停", menu)
        pause_action.triggered.connect(self.controller.toggle_pause)
        menu.addAction(pause_action)
        feed_menu = menu.addMenu("投喂")
        for info in FOODS:
            action = QAction(f"{'♥' if info.liked else '？'} {info.name}", feed_menu)
            action.triggered.connect(lambda _checked=False, chosen=info: self.controller.feed(chosen))
            feed_menu.addAction(action)
        spawn_action = QAction("随机生成食物", menu)
        spawn_action.triggered.connect(lambda: self.controller.spawn_food())
        menu.addAction(spawn_action)
        menu.addSeparator()
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        menu.exec(global_pos)


class DesktopPetApp:
    def __init__(self, qt_app: QApplication):
        self.qt_app = qt_app
        self.paused = False
        self.foods: list[FoodWidget] = []
        self.bubble = SpeechBubble()
        self.pet = PetWidget(self)
        self.pet.show()
        for _ in range(2):
            self.spawn_food()
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.tick)
        self.frame_timer.start(33)
        self.food_timer = QTimer()
        self.food_timer.timeout.connect(self.auto_spawn_food)
        self.food_timer.start(random.randint(9000, 15000))
        self.last_greeting_key = ""
        self.greeting_timer = QTimer()
        self.greeting_timer.timeout.connect(self.check_time_greeting)
        self.greeting_timer.start(60_000)
        QTimer.singleShot(1100, self.check_time_greeting)

    def tick(self):
        self.pet.update_behavior(33)
        self.bubble.tick(33, self.pet)
        if not self.paused:
            for food in tuple(self.foods):
                food.tick()

    def toggle_pause(self):
        self.paused = not self.paused
        self.bubble.say("我继续活动啦！" if not self.paused else "先休息一下～", 1700)

    def auto_spawn_food(self):
        if not self.paused and len(self.foods) < 5:
            self.spawn_food()
        self.food_timer.setInterval(random.randint(9000, 16000))

    def spawn_food(self, info: FoodInfo | None = None, near_pet: bool = False):
        bounds = activity_bounds().adjusted(22, 22, -FOOD_SIZE - 22, -FOOD_SIZE - 22)
        if near_pet:
            x = int(self.pet.position.x() + (-95 if self.pet.facing_left else PET_SIZE + 42))
            y = int(self.pet.position.y() + PET_SIZE - FOOD_SIZE)
            position = QPoint(max(bounds.left(), min(x, bounds.right())), max(bounds.top(), min(y, bounds.bottom())))
        else:
            position = QPoint(random.randint(bounds.left(), max(bounds.left(), bounds.right())), random.randint(bounds.top(), max(bounds.top(), bounds.bottom())))
        food = FoodWidget(info or random.choice(FOODS), position)
        self.foods.append(food)
        food.show()
        return food

    def feed(self, info: FoodInfo):
        food = self.spawn_food(info, near_pet=True)
        self.pet.focus_food = food
        self.pet.state = "spot"
        self.pet.state_until = self.pet.elapsed_ms + 300
        self.bubble.say(f"哇，是{info.name}！", 1200)

    def consume(self, food: FoodWidget):
        if food in self.foods:
            self.foods.remove(food)
            food.close()
            food.deleteLater()

    def handle_touch(self, local_pos: QPoint):
        if local_pos.y() < PET_SIZE * 0.42:
            self.pet.react("headpat", "摸摸头好舒服呀～", 2100)
        elif local_pos.y() < PET_SIZE * 0.76:
            self.pet.react("bellyrub", "嘿嘿，肚子痒痒的！", 2100)
        else:
            self.pet.react("ticklish", "呀！脚脚很怕痒！", 1900)

    def check_time_greeting(self):
        now = datetime.now()
        hour = now.hour
        if 5 <= hour < 11:
            period, text = "morning", "早安呀！今天也要元气满满～"
        elif 11 <= hour < 14:
            period, text = "lunch", "到午饭时间啦，记得好好吃饭！"
        elif 14 <= hour < 18:
            period, text = "afternoon", "下午也要加油，累了就休息一下～"
        elif 18 <= hour < 23:
            period, text = "evening", "晚上好呀，今天辛苦啦！"
        else:
            period, text = "night", "已经很晚啦，要早点休息哦～"
        key = f"{now.date().isoformat()}-{period}"
        if key != self.last_greeting_key:
            self.last_greeting_key = key
            self.pet.react("wave" if period != "night" else "sleepy", text, 3600)


def main() -> int:
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)
    qt_app.setApplicationName("古风桌宠")
    controller = DesktopPetApp(qt_app)
    qt_app.aboutToQuit.connect(lambda: controller.frame_timer.stop())
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
