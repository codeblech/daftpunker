import os
import sys
from mutagen.mp3 import MP3
from PyQt5.QtCore import Qt, QUrl, QDir
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QGridLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsView,
    QGraphicsScene,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QStyle,
    QListWidget,
    QFileDialog,
    QSlider,
    QVBoxLayout,
    QDial,
    QSpacerItem,
    QSizePolicy,
    QListWidgetItem,
)
from PyQt5.QtGui import QImage, QPalette, QBrush, QPainter
from PyQt5.QtCore import QSize, QTimer, QRect

from PyQt5.QtGui import QGradient, QFont, QColor, QCursor, QIcon, QPixmap
from PyQt5.QtMultimedia import (
    QMediaPlayer,
    QMediaContent,
    QMediaPlaylist,
    QMediaMetaData,
)


class ScrollingLabel(QLabel):
    def __init__(self, parent=None):
        super(ScrollingLabel, self).__init__(parent)
        self.offset = 0
        self.myTimer = QTimer(self)
        self.myTimer.timeout.connect(self.timerEvent)
        self.myTimer.start(15)  # Adjust speed as necessary

    def setText(self, text):
        super().setText(text)
        self.offset = 0  # Reset offset when text changes

    def timerEvent(self):
        self.offset -= 1  # Adjust scrolling speed and direction
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        text = self.text()
        metrics = painter.fontMetrics()
        width = metrics.width(text)

        if width > self.rect().width():
            # Ensure x is an integer
            x = int(self.offset % width)
            # Create the rectangles with integer coordinates
            rect1 = QRect(x, 0, width, self.rect().height())
            rect2 = QRect(x - width, 0, width, self.rect().height())

            painter.drawText(rect1, self.alignment(), text)
            painter.drawText(rect2, self.alignment(), text)
        else:
            # When centering the text, ensure x is an integer
            x = int((self.rect().width() - width) / 2)
            rect = QRect(x, 0, width, self.rect().height())
            painter.drawText(rect, self.alignment(), text)

        painter.end()


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Give Life Back To Music")

        self.setFixedSize(1600, 808)

        # Set the background image
        self.backgroundImage = QImage("PyQt5-Music-Player/daft_punk.png")
        self.updateBackground()

        # Create some variables
        self.url = QUrl()
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist(self.player)
        self.player.setPlaylist(self.playlist)

        # Create the status and track labels
        common_style = """
                        font-family: LED Dot-Matrix;
                        font-weight: bold;
                        font-size: 10pt;
                        color: white;
                       """
        self.track_title = ScrollingLabel()
        self.track_title.setAlignment(Qt.AlignCenter)
        self.track_title.setFixedHeight(60)
        self.track_title.setFixedWidth(400)
        self.track_title.setWordWrap(True)
        silver_helmet_style = """
                        font-family: LED Dot-Matrix;
                        font-weight: bold;
                        font-size: 40pt;
                        color: white;
                        """

        self.track_title.setStyleSheet(silver_helmet_style)
        # self.released = QLabel()
        # self.released.setStyleSheet(common_style)
        # self.genre = QLabel()
        # self.genre.setStyleSheet(common_style)
        # self.art = QLabel()
        # self.art.setContentsMargins(5, 170, 5, 5)

        # Timer Label
        self._timer = QLabel("Duration: 00:00:00 / 00:00:00")
        self._timer.setStyleSheet(common_style)

        # Define and create the listbox
        self.musiclist = QListWidget()
        self.musiclist.setFixedHeight(300)
        self.musiclist.setFixedWidth(370)
        self.musiclist.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide vertical scrollbar
        self.musiclist.setStyleSheet(
            "background-color: transparent; color: white; font-family: LED Dot-Matrix; font-weight: bold; font-size: 15pt;"
        )
        self.musiclist.setFrameShape(QFrame.NoFrame)
        self.musiclist.setFixedSize(310, 320)  # Adjust size to fit within the visor

        # Create the music list container widget
        self.musiclist_container = QWidget()
        self.musiclist_container_layout = QGridLayout()
        self.musiclist_container.setLayout(self.musiclist_container_layout)

        # Add spacers and music list to the container layout
        # horizontal_spacer_2 = QWidget()
        # horizontal_padding_2 = 100
        # horizontal_spacer_2.setFixedWidth(horizontal_padding_2)
        # horizontal_spacer_2.setFixedHeight(0)
        # self.musiclist_container_layout.addWidget(horizontal_spacer_2, 2, 1, 1, 1)
        # ... [previous code] ...

        # Add spacers and music list to the container layout
        horizontal_spacer_2 = QSpacerItem(
            120, 10, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.musiclist_container_layout.addItem(horizontal_spacer_2, 2, 1, 1, 1)

        # ... [rest of the code] ...

        vertical_spacer_2 = QWidget()
        vertical_padding_2 = 10
        vertical_spacer_2.setFixedHeight(vertical_padding_2)
        vertical_spacer_2.setFixedWidth(0)
        self.musiclist_container_layout.addWidget(vertical_spacer_2, 1, 0, 1, 1)

        self.musiclist_container_layout.addWidget(self.musiclist, 2, 0, 1, 1)

        # Create some containers
        btn_box = QHBoxLayout()

        slider_box = QVBoxLayout()
        slider_box.setContentsMargins(5, 80, 5, 5)
        dial_box = QVBoxLayout()
        dial_box.setAlignment(Qt.AlignCenter)
        container = QGridLayout()
        info_container = QGridLayout()
        info_container.setSpacing(8)

        frame = QFrame()
        frame.setMinimumWidth(800)
        frame.setFrameShape(QFrame.NoFrame)
        frame.setLayout(info_container)

        img_frame = QFrame()
        img_frame.setMinimumHeight(100)

        # Create slider frame and control
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.NoFrame)
        # slider_frame.setFrameShadow(QFrame.Sunken)
        slider_frame.setMinimumHeight(20)
        slider_frame.setLayout(slider_box)

        self.slider = QSlider(Qt.Horizontal)
        slider_box.addWidget(self._timer)
        slider_box.addWidget(self.slider)

        # Create volume frame and control
        dial_frame = QFrame()
        dial_frame.setStyleSheet(common_style)
        dial_frame.setFrameShape(QFrame.NoFrame)
        # dial_frame.setFrameShadow(QFrame.Sunken)

        self.dial = QDial()
        self.dial.setRange(0, 100)
        self.dial.setNotchesVisible(True)
        self.dial.setSliderPosition(70)
        self.dial.setValue(70)
        self.dial.setFixedHeight(100)
        self.dial.setFixedWidth(100)
        dial_box.addWidget(QLabel("Volume"))
        dial_box.addWidget(self.dial)
        dial_frame.setLayout(dial_box)

        # Used to update various aspects of gui
        self.playlist.currentIndexChanged.connect(self.update)
        self.dial.valueChanged.connect(self._volume, self.dial.value())
        self.player.metaDataChanged.connect(self.meta_data)
        self.musiclist.itemDoubleClicked.connect(self._doubleclick)
        self.player.positionChanged.connect(self.track_position)
        self.player.durationChanged.connect(self.duration)
        self.slider.valueChanged.connect(self.timer)

        vertical_spacer = QWidget()
        vertical_padding = 110
        vertical_spacer.setFixedHeight(vertical_padding)
        info_container.addWidget(
            vertical_spacer, 1, 0, 1, 1
        )  # Add this spacer in the row above the track title

        horizontal_spacer = QWidget()
        horizontal_padding = 100
        horizontal_spacer.setFixedWidth(horizontal_padding)
        info_container.addWidget(
            horizontal_spacer, 2, 0, 1, 1
        )  # Add this spacer in the column to the right of the track title

        info_container.addWidget(self.track_title, 2, 1, 1, 1, Qt.AlignCenter)

        btn_style = """
                        QPushButton{background-color: #ffffff;
                                    color: #000000;
                                    border: none;
                                    font-family: LED Dot-Matrix;
                                    font-size: 20px;
                                    padding: 8px 8px;

                                    }
                        QPushButton:hover{background-color: #ffffff;
                                        color: #000000;
                                        font-weight: bold;
                                        }"""
        btn_style_2 = """
                        QPushButton{background-color: #ffffff;
                                    color: #000000;
                                    border: none;
                                    font-family: LED Dot-Matrix;
                                    font-size: 20px;
                                    padding: 8px 8px;

                                    }
                        QPushButton:hover{background-color: #ffffff;
                                            color: #000000;
                                            font-weight: bold;
                                            }"""

        # Create buttons for getting audio files and clearing playlist
        top_buttons_width = 170
        top_buttons_height = 50
        file_btn = QPushButton("Add Music")
        file_btn.released.connect(self._files)
        file_btn.setCursor(Qt.PointingHandCursor)
        file_btn.setStyleSheet(btn_style_2)
        file_btn.setFixedSize(top_buttons_width, top_buttons_height)

        clear_btn = QPushButton("Clear List")
        clear_btn.released.connect(self._clear)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(btn_style_2)
        clear_btn.setFixedSize(top_buttons_width, top_buttons_height)

        # Create & style the control buttons
        self.play_btn = QPushButton("Play")
        self.play_btn.released.connect(self._state)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setStyleSheet(btn_style)
        self.play_btn.setFixedSize(top_buttons_width, top_buttons_height)

        self.prev_btn = QPushButton("Prev")
        self.prev_btn.released.connect(self._prev)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(btn_style)
        self.prev_btn.setFixedSize(top_buttons_width, top_buttons_height)

        self.next_btn = QPushButton("Next")
        self.next_btn.released.connect(self._next)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(btn_style)
        self.next_btn.setFixedSize(top_buttons_width, top_buttons_height)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.released.connect(sys.exit)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setFixedSize(top_buttons_width, top_buttons_height)
        self.exit_btn.setStyleSheet(
            """QPushButton{background-color: firebrick;
                           color: #000000;
                           border: none;
                           font-family: LED Dot-Matrix;
                           font-size: 20px;
                           padding: 8px 8px;

                           }
               QPushButton:hover{background-color: firebrick;
                                color: #000000;
                                font-weight: bold;
                                }"""
        )

        # Add the buttons to layout
        # btn_box.setSpacing(10)
        btn_box.addWidget(self.prev_btn)
        btn_box.addWidget(self.play_btn)
        btn_box.addWidget(self.next_btn)
        btn_box.addWidget(file_btn)
        btn_box.addWidget(clear_btn)
        btn_box.addWidget(self.exit_btn)

        container.addWidget(frame, 2, 0, 2, 1)  # For track info

        container.addWidget(self.musiclist_container, 2, 1, 1, 2)  # For the music list
        container.addLayout(
            btn_box, 1, 0, 1, 3
        )  # Move control buttons above the slider
        container.addWidget(
            slider_frame, 4, 0, 1, 2
        )  # Assign two columns for the slider
        container.addWidget(
            dial_frame, 4, 2, 1, 1
        )  # Place the volume control in the third column

        # Create and set the layout to container
        widget = QWidget()
        widget.setLayout(container)
        self.setCentralWidget(widget)

    def updateBackground(self):
        sImage = self.backgroundImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.updateBackground()
        super().resizeEvent(event)

    # Volume control
    def _volume(self, val=70):
        self.player.setVolume(val)

    # Sets position of slider
    def track_position(self, position):
        self.slider.setValue(position)

    # Duration of the track playing
    def duration(self, duration):
        self.slider.setRange(0, duration)

    # Updates duration of track playing
    def timer(self):
        total_milliseconds = self.player.duration()
        total_seconds, total_milliseconds = divmod(total_milliseconds, 1000)
        total_minutes, total_seconds = divmod(total_seconds, 60)
        total_hours, total_minutes = divmod(total_minutes, 60)

        elapsed_milliseconds = self.slider.value()
        elapsed_seconds, elapsed_milliseconds = divmod(elapsed_milliseconds, 1000)
        elapsed_minutes, elapsed_seconds = divmod(elapsed_seconds, 60)
        elapsed_hours, elapsed_minutes = divmod(elapsed_minutes, 60)

        self._timer.setText(
            f"Duration: {elapsed_hours:02d}:{elapsed_minutes:02d}:{elapsed_seconds:02d} / {total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"
        )

    # Shorten text that may be too long
    def _truncate(self, text, length=25):
        if text:
            if len(text) <= length:
                return text
            else:
                return f"{' '.join(text[:length+1].split(' ')[0:-1])} ...."

    # Get music metadata
    def meta_data(self):
        if self.player.isMetaDataAvailable():
            if self.player.metaData(QMediaMetaData.Title):
                self.track_title.setText(self.player.metaData(QMediaMetaData.Title))

        # if self.player.metaData(QMediaMetaData.Year):
        #     self.released.setText(f"{self.player.metaData(QMediaMetaData.Year)}")
        # if self.player.metaData(QMediaMetaData.Genre):
        #     self.genre.setText(self.player.metaData(QMediaMetaData.Genre))
        # if self.player.metaData(QMediaMetaData.Title):
        #     self.track.setText(
        #         f"Track: {self._truncate(self.player.me        # if self.player.metaData(QMediaMetaData.Year):
        #     self.released.setText(f"{self.player.metaData(QMediaMetaData.Year)}")
        # if self.player.metaData(QMediaMetaData.Genre):
        #     self.genre.setText(self.player.metaData(QMediaMetaData.Genre))
        # if self.player.metaData(QMediaMetaData.Title):
        #     self.track.setText(
        #         f"Track: {self._truncate(self.player.metaData(QMediaMetaData.Title),20)}"
        #     )
        # if self.player.metaData(QMediaMetaData.CoverArtImage):
        #     pixmap = QPixmap(self.player.metaData(QMediaMetaData.CoverArtImage))
        #     pixmap = pixmap.scaled(
        #         int(pixmap.width() / 3), int(pixmap.height() / 3)
        #     )
        #     self.art.setPixmap(pixmap)
        #     self.art.setContentsMargins(0, 32, 0, 5)taData(QMediaMetaData.Title),20)}"
        #     )
        # if self.player.metaData(QMediaMetaData.CoverArtImage):
        #     pixmap = QPixmap(self.player.metaData(QMediaMetaData.CoverArtImage))
        #     pixmap = pixmap.scaled(
        #         int(pixmap.width() / 3), int(pixmap.height() / 3)
        #     )
        #     self.art.setPixmap(pixmap)
        #     self.art.setContentsMargins(0, 32, 0, 5)

    def addScrollingItem(self, text):
        scrollingItem = QListWidgetItem(self.musiclist)
        scrollingLabel = ScrollingLabel()
        scrollingLabel.setText(text)
        # Set appropriate size and style for scrollingLabel here
        self.musiclist.setItemWidget(scrollingItem, scrollingLabel)

    # Create the header
    def _header_footer(self, minheight, maxheight, fontsize, text):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(3, 3)

        scene = QGraphicsScene()

        view = QGraphicsView()
        view.setMinimumSize(800, minheight)
        view.setMaximumHeight(maxheight)
        view.setScene(scene)

        gradient = QGradient(QGradient.RichMetal)

        scene.setBackgroundBrush(gradient)

        font = QFont("comic sans ms", fontsize, QFont.Bold)

        text = scene.addText(text)
        text.setDefaultTextColor(QColor(250, 250, 250))
        text.setFont(font)

        text.setGraphicsEffect(shadow)

        return view

    # Method for double clicking a track and play
    def _doubleclick(self):
        self.playlist.setCurrentIndex(self.musiclist.currentRow())
        self.player.play()

    # Method for clearing the playlist and musiclist
    def _clear(self):
        self.player.stop()
        self.musiclist.clear()
        self.playlist.clear()
        self.play_btn.setText("Play")
        self.status.setText("Status: ")
        pixmap = QPixmap()
        self.art.setPixmap(pixmap)
        self.dial.setSliderPosition(70)
        self.dial.setValue(70)

    # Method for adding tracks to the playlist and musiclist
    def _files(self):
        files = QFileDialog.getOpenFileNames(
            None, "Get Audio Files", filter="Audio Files (*.mp3 *.ogg *.wav)"
        )
        for file in files[0]:
            self.playlist.addMedia(QMediaContent(self.url.fromLocalFile(file)))
            try:
                track = MP3(file)
                track_name = str(track.get("TIT2", "Unlabeled Track"))
            except:
                track_name = file.rpartition("/")[2].rpartition(".")[0]

            self.addScrollingItem(str(track_name))

        self.musiclist.setCurrentRow(0)
        self.playlist.setCurrentIndex(0)

    # Methods for the control buttons
    def _prev(self):
        if self.playlist.previousIndex() == -1:
            self.playlist.setCurrentIndex(self.playlist.mediaCount() - 1)
        else:
            self.playlist.previous()

    def _next(self):
        self.playlist.next()
        if self.playlist.currentIndex() == -1:
            self.playlist.setCurrentIndex(0)
            self.player.play()

    def _stop(self):
        self.player.stop()
        self.play_btn.setText("Play")
        self.playlist.setCurrentIndex(0)
        self.musiclist.setCurrentRow(0)
        self.status.setText("Status: Now Stopped")

    def _state(self):
        if self.playlist.mediaCount() > 0:
            if self.player.state() != QMediaPlayer.PlayingState:
                self.play_btn.setText("Pause")
                # self.status.setText("Status: Now Playing")
                self.player.play()
            else:
                self.play_btn.setText("Play")
                self.player.pause()
                # self.status.setText("Status: Now Paused")

        else:
            pass

    # Method for updating the listbox when the playlist updates
    def update(self):
        self.musiclist.setCurrentRow(self.playlist.currentIndex())
        if self.playlist.currentIndex() < 0:
            self.musiclist.setCurrentRow(0)
            self.playlist.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
