from functools import partial
import os
import json
import numpy as np
from pathlib import Path
from qtpy.QtWidgets import QLabel, QSizePolicy
import warnings
# from napari_plugin_engine import napari_hook_implementation

from qtpy.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QSlider,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QFileSystemModel
)
from qtpy.QtCore import  (
    QDir,
    QModelIndex,
    QPoint,
    QRegExp,
    QSortFilterProxyModel,
    Qt,
    QTimer,
)
from qtpy.QtGui import (
    QColor,
    QPainter,
    QIcon,
)

from napari.viewer import Viewer
from magicgui.widgets import FileEdit
from magicgui.types import FileDialogMode
from napari.utils import notifications

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from qtpy.QtCore import QModelIndex

from napari_toothfairy_annotator.FDI_Annotator import FDI_Annotator

class SettingsDialog(QDialog):
    def __init__(self, current_interval_ms=20000, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ToothFairy Annotator Settings")
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout()
        
        # Create form layout for settings
        form_layout = QFormLayout()
        
        # Saving delay timer setting
        timer_layout = QVBoxLayout()
        
        self.timer_label = QLabel("Saving Delay: 20s")
        self.timer_slider = QSlider(Qt.Horizontal)
        self.timer_slider.setMinimum(5)  # 5 seconds
        self.timer_slider.setMaximum(61)  # 60 seconds + 1 for "Never"
        
        # Set current value from the parameter
        if current_interval_ms <= 0:
            self.timer_slider.setValue(61)  # "Never"
        else:
            self.timer_slider.setValue(min(60, max(5, current_interval_ms // 1000)))
        
        self.timer_slider.setTickPosition(QSlider.TicksBelow)
        self.timer_slider.setTickInterval(5)
        
        # Connect slider to update label
        self.timer_slider.valueChanged.connect(self.update_timer_label)
        
        # Add some help text
        help_label = QLabel("Set the delay before auto-saving annotations after painting.\nValues: 5-60 seconds, or 'Never' to disable auto-save.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        
        timer_layout.addWidget(self.timer_label)
        timer_layout.addWidget(self.timer_slider)
        timer_layout.addWidget(help_label)
        
        form_layout.addRow("Saving Delay Timer:", timer_layout)
        
        layout.addLayout(form_layout)
        
        # Add OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Set initial label
        self.update_timer_label(self.timer_slider.value())
    
    def update_timer_label(self, value):
        if value > 60:
            self.timer_label.setText("Saving Delay: Never")
        else:
            self.timer_label.setText(f"Saving Delay: {value}s")
    
    def get_interval_ms(self):
        value = self.timer_slider.value()
        if value > 60:
            return -1  # Never save
        return value * 1000  # Convert to milliseconds

class CustomSortWidgetItem(QListWidgetItem):
    def __init__(self, text, nominal_id):
        super().__init__(text)
        self.nominal_id = nominal_id

    def __lt__(self, other):
        return self.nominal_id < other.nominal_id

    # def paint(self, painter):
    #     painter.fillRect(self.rect().adjusted(0, 0, -50, 0), self.color)
    #     super().paint(painter)

class WidgetAnnotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.fdi_annotator = FDI_Annotator()
        self.associations = {0: "00"}
        self._available_ids = None
        self.saving_delay_ms = 20000  # Default 20 seconds

        self.load_associated_volume()

        self.viewer.layers.move_multiple([0,2,1])

        layout = QVBoxLayout()

        self.list1_label = QLabel('Nominal IDs:')
        self.list1 = QListWidget()
        # self.list1.setSortingEnabled(True)
        layout.addWidget(self.list1_label)
        layout.addWidget(self.list1)

        self.list2_label = QLabel('Numerical IDs:')
        self.list2 = QListWidget()
        self.list2.setSortingEnabled(True)
        layout.addWidget(self.list2_label)
        layout.addWidget(self.list2)
        self.list2.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        self.associate_button = QPushButton("Associate IDs")
        self.associate_button.clicked.connect(self.associate_ids)
        layout.addWidget(self.associate_button)

        self.reset_assoc_button = QPushButton("Reset Association")
        self.reset_assoc_button.clicked.connect(self.reset_assoc)
        layout.addWidget(self.reset_assoc_button)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload)
        layout.addWidget(self.reload_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.tooltip = QLabel(self.viewer.window.qt_viewer.parent())
        self.tooltip.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.tooltip.setAttribute(Qt.WA_ShowWithoutActivating)
        self.tooltip.setAlignment(Qt.AlignCenter)
        self.tooltip.sizePolicy().setHorizontalPolicy(QSizePolicy.Minimum)
        self.tooltip.setStyleSheet("color: black")
        self.tooltip.show()

        self.setLayout(layout)
        self.load_settings()  # Load settings from file
        self.load_associations()
        self.update_lists()
        self.viewer.layers['annotation'].events.paint.connect(self.paint_callback)

    def load_settings(self):
        """Load settings from configuration file"""
        try:
            source = self.get_source()
            settings_file = os.path.join(source, 'plugin_settings.json')
            if os.path.isfile(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.saving_delay_ms = settings.get('saving_delay_ms', 20000)
                    print(f"Loaded settings: saving_delay_ms = {self.saving_delay_ms}")
            else:
                print("No settings file found, using default saving delay of 20s")
        except Exception as e:
            print(f"Could not load settings, using defaults: {e}")
            self.saving_delay_ms = 20000

    def save_settings(self):
        """Save settings to configuration file"""
        try:
            source = self.get_source()
            settings_file = os.path.join(source, 'plugin_settings.json')
            settings = {
                'saving_delay_ms': self.saving_delay_ms
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
            print(f"Settings saved to {settings_file}")
        except Exception as e:
            print(f"Could not save settings: {e}")

    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self.saving_delay_ms, self)
        if dialog.exec_() == QDialog.Accepted:
            new_interval = dialog.get_interval_ms()
            self.saving_delay_ms = new_interval
            self.save_settings()  # Save settings to file
            if new_interval > 0:
                print(f"Saving delay updated to: {self.saving_delay_ms}ms ({self.saving_delay_ms/1000}s)")
            else:
                print("Auto-save disabled (set to Never)")

    def paint_callback(self, event):
        print("paint callback")
        # start a qt timer, if another paint event is called, reset the timer
        if hasattr(self, 'paint_timer'):
            self.paint_timer.stop()
        
        # Only start timer if saving is enabled (not set to "Never")
        if self.saving_delay_ms > 0:
            self.paint_timer = QTimer(self)
            self.paint_timer.setSingleShot(True)
            self.paint_timer.setInterval(self.saving_delay_ms)
            self.paint_timer.timeout.connect(self.save_annotations)
            self.paint_timer.start()

    def delete(self,):
        if self.tooltip is not None:
            print(f'Deleting tooltip')
            self.tooltip.hide()
            self.tooltip.setParent(None)
            self.tooltip.deleteLater()
            self.tooltip = None


    def reload(self,):
        source = self.get_source()
        annotation_npy_path = os.path.join(source, 'annotation.npy')

        if not os.path.isfile(annotation_npy_path):
            print('path not found on reload')
            return

        self.load_associations()
        self.viewer.layers.remove('annotation')
        annotation = np.load(annotation_npy_path)

        keys = self.associations.keys()
        print(keys)
        for key in keys:
            mask = annotation == int(key)
            annotation[mask] = 0

        self.viewer.add_labels(annotation, name='annotation', visible=True)

    def add_tooltip(self,):
        if 'associated' not in self.viewer.layers:
            return

        self.viewer.layers['associated'].mouse_move_callbacks.append(self.show_label_on_mouse_move)


    def show_label_on_mouse_move(self, layer, event):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            label_pos = self.viewer.window.qt_viewer.cursor().pos()
        self.tooltip.move(label_pos.x() + 20, label_pos.y() + 20)
        mouse_pos = np.round(event.position).astype(int)
        val = layer.get_value(
            position=mouse_pos,
            view_direction=self.viewer.cursor._view_direction,
            dims_displayed=list(self.viewer.dims.displayed),
            world=True,
        )

        if val is None:
            self.tooltip.setText('')
            self.tooltip.adjustSize()
            return
        label_name = self.fdi_annotator.fdi_notation[f'{val:02d}']['name']
        if label_name is None:
            label_name = "Error"
        self.tooltip.setText(f'{label_name} (Nominal ID: {val})')
        self.tooltip.adjustSize()


    def load_associated_volume(self,):
        print(f'Called load_associated_volume')
        source = self.get_source()
        associated_volume_path = os.path.join(source, 'associated.npy')
        if os.path.isfile(associated_volume_path):
            self.associated_volume = np.load(associated_volume_path)
        else:
            self.associated_volume = np.zeros_like(self.viewer.layers['annotation'].data)
        self.viewer.add_labels(self.associated_volume, name='associated', visible=False)
        self.add_tooltip()

    def associate_ids(self):
        selected_items_list1 = self.list1.selectedItems()
        selected_items_list2 = self.list2.selectedItems()

        for item1 in selected_items_list1:
            for item2 in selected_items_list2:
                elem_name = item1.text().split(' - ')[-1]
                fdi_id = self.fdi_annotator.inverse[elem_name]['ID']
                print(f'associating {elem_name} (id: {fdi_id})')
                self.associations[int(item2.text())] = fdi_id
                mask = self.viewer.layers['annotation'].data == int(item2.text())
                self.viewer.layers['annotation'].data[mask] = 0
                self.viewer.layers['associated'].data[mask] = int(fdi_id)
        self.viewer.layers['annotation'].refresh()
        self.viewer.layers['associated'].refresh()
        self.update_lists()
        self.save_associations()

    def reset_assoc(self,):
        selected_items_list2 = self.list2.selectedItems()

        if len(selected_items_list2) == 0:
            return

        for item2 in selected_items_list2:
            item2 = item2.text()

            if ' > ' not in item2:
                continue

            print(f"selected: {item2}")
            
            id = item2.split(' > ')[0]
            id = int(id)
            assoc_id = self.associations[id]

            print(f"removing {id} > {assoc_id}")

            del self.associations[id]

        self.update_lists()
        self.save_associations()
        self.reload()

    def get_source(self,):
        source = self.viewer.layers['annotation'].source.path
        if source is None:
            source = self.viewer.layers['volume'].source.path
        if source is None:
            source = self.viewer.layers['annotation'].metadata['parent_folder']
        if source is None:
            source = self.viewer.layers['volume'].metadata['parent_folder']

        assert source is not None, "I tried so hard and got so far but in the end it doesn't even matter"

        return source

    def save_annotations(self,):
        data = self.viewer.layers['annotation'].data
        source = self.get_source()
        save_path = os.path.join(source, 'annotation.npy')
        np.save(save_path, data)
        notifications.show_info(f'Saved annotation to {save_path}')

    def save_associations(self,):
        data = self.viewer.layers['associated'].data
        source = self.get_source()

        save_path = os.path.join(source, 'associated.npy')
        np.save(save_path, data)
        association_file = os.path.join(source, 'associations.json')
        with open(association_file, 'w') as f:
            json.dump(self.associations, f)


    def load_associations(self,):
        source = self.get_source()
        association_file = os.path.join(source, 'associations.json')
        annotation_file = os.path.join(source, 'annotation.npy')

        if not os.path.isfile(association_file):
            return

        if not os.path.isfile(annotation_file):
            return

        with open(association_file) as f:
            print('Load associations.json')
            str_id_associations = json.load(f)
            self.associations = {}
            for k, v in str_id_associations.items():
                self.associations[int(k)] = v

        annotation = np.load(annotation_file)
        self.viewer.layers['associated'].data = np.zeros_like(annotation)
        for left_id, right_id in self.associations.items():
            mask = annotation == int(left_id)
            self.viewer.layers['annotation'].data[mask] = 0
            self.viewer.layers['associated'].data[mask] = int(right_id)
        self.viewer.layers['annotation'].refresh()
        self.viewer.layers['associated'].refresh()


    def update_lists(self):
        self.list1.clear()
        self.list2.clear()

        for id_data in self.get_fdi_ids():
            item = id_data['name']
            id = id_data['ID']
            self.list1.addItem(f'{id} - {item}')

        already_annotated = set(self.associations.keys())

        for id_data in self.get_available_ids():
            s = f'{id_data}'
            if int(id_data) in already_annotated:
                assoc_id = self.associations[int(id_data)]
                s += f' > {self.fdi_annotator.fdi_notation[assoc_id]["name"]}'
            item = s
            self.list2.addItem(CustomSortWidgetItem(item, assoc_id))

    def get_available_ids(self,):
        if self._available_ids is None:
            data = self.viewer.layers['annotation'].data
            self._available_ids = np.unique(data).tolist()
            self._available_ids += self.associations.keys()
            self._available_ids = list(set(self._available_ids))
        return self._available_ids

    def get_fdi_ids(self,):
        return self.fdi_annotator.fdi_notation.values()

    def get_available_layers(self,):
        return [layer.name for layer in self.viewer.layers]


class DirectoryFriendlyFilterProxyModel(QSortFilterProxyModel):
    def lessThan(self, left, right):
        # Implement your custom sorting logic here
        left_data = self.sourceModel().data(left)
        right_data = self.sourceModel().data(right)
        # For example, let's sort integers in descending order
        try:
            left_int = int(left_data[1:])
            right_int = int(right_data[1:])
            left_char = left_data[0]
            right_char = right_data[0]
            if left_char > right_char:
                return True
            elif left_char < right_char:
                return False
            else:
                return left_int > right_int
        except Exception as e:
            return False

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Accepts directories and files that pass the base class's filter
        
        Note: This custom proxy ensures that we can search for filenames and keep the directories
        in the tree view
        """
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)

        # if model.isDir(index):
        #     return True

        return super().filterAcceptsRow(source_row, source_parent)


class FolderBrowser(QWidget):
    """Main Widget for the Folder Browser Dock Widget
    
    The napari viewer is passed in as an argument to the constructor
    """
    viewer: Viewer
    folder_chooser: FileEdit
    file_system_model: QFileSystemModel
    proxy_model: DirectoryFriendlyFilterProxyModel
    search_field: QLineEdit
    tree_view: QTreeView
    annotator_widget: WidgetAnnotator

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.setLayout(QVBoxLayout())

        current_directory: Path = Path(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.layout().addWidget(QLabel("Directory"))
        self.folder_chooser = FileEdit(
            mode=FileDialogMode.EXISTING_DIRECTORY,
            value=current_directory,
        )
        self.layout().addWidget(self.folder_chooser.native)

        def directory_changed(*_) -> None:
            current_directory = Path(self.folder_chooser.value)
            self.tree_view.setRootIndex(
                self.proxy_model.mapFromSource(
                    self.file_system_model.index(current_directory.as_posix())
                )
            )

        self.folder_chooser.line_edit.changed.connect(directory_changed)

        # --------------------------------------------
        # File system abstraction with proxy for search filtering
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.proxy_model = DirectoryFriendlyFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_system_model)

        # Create search box and connect to proxy model
        self.layout().addWidget(QLabel("File filter"))
        self.search_field = QLineEdit()
        # Note: We should agree on the best regex interaction to provide here
        def update_filter(text: str) -> None:
            self.proxy_model.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
        self.search_field.textChanged.connect(update_filter)
        search_widget = QWidget()
        search_widget.setLayout(QHBoxLayout())
        search_widget.layout().addWidget(QLabel("Search:"))
        search_widget.layout().addWidget(self.search_field)
        self.layout().addWidget(search_widget)

        self.tree_view = QTreeView()
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setRootIndex(
            self.proxy_model.mapFromSource(
                self.file_system_model.index(current_directory.as_posix())
            )
        )
    
        self.tree_view.doubleClicked.connect(self.__tree_double_click)

        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        self.layout().addWidget(self.tree_view)

        self.annotator_widget = None


    def __tree_double_click(self, index: QModelIndex) -> None:
        """Action on double click in the tree model
        
        Opens the selected file or in the folder
        
        Args:
            index: Index of the selected item in the tree view
        """

        source_index: QModelIndex = self.proxy_model.mapToSource(index)
        file_path: str = self.file_system_model.filePath(source_index)

        if self.file_system_model.isDir(source_index):
            if self.annotator_widget is not None:
                self.annotator_widget.save_associations()
                self.annotator_widget.save_annotations()
                if hasattr(self.annotator_widget, 'paint_timer'):
                    self.annotator_widget.paint_timer.stop()

                self.layout().removeWidget(self.annotator_widget)
                self.annotator_widget.delete()
                self.annotator_widget = None

            layers_to_remove = self.viewer.layers.copy()
            for layer in layers_to_remove:
                self.viewer.layers.remove(layer)

            print(f'Layers: {len(self.viewer.layers)}')

            self.viewer.open(file_path, plugin='napari-toothfairy-annotator')
            self.annotator_widget = WidgetAnnotator(self.viewer)
            self.layout().addWidget(self.annotator_widget)

    def __show_context_menu(self, position: QPoint) -> None:
        """Show a context menu when right-clicking in the tree view"""
        menu = QMenu()
        open_multiple_action = menu.addAction("Open multiple files")
        open_multiple_action.triggered.connect(
            lambda: self.__open_multi_selection(is_stack=False)
        )
        open_as_stack_action = menu.addAction("Open as stack")
        open_as_stack_action.triggered.connect(
            lambda: self.__open_multi_selection(is_stack=True)
        )

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def __open_multi_selection(self, is_stack: bool) -> None:
        """Open multiple files in the viewer
        
        The files are selected in the tree view
        
        Args:
            is_stack: If True, the files are opened as a stack
        """
        indices: list[QModelIndex] = self.tree_view.selectionModel().selectedIndexes()
        fs_paths: list[str] = [
            self.file_system_model.filePath(self.proxy_model.mapToSource(index)) for index in indices
            if not self.file_system_model.isDir(self.proxy_model.mapToSource(index)) and index.column() == 0
        ]

        # Nothing to do when there is no file selected
        if len(fs_paths) == 0:
            return

        self.viewer.open(fs_paths, stack=is_stack)


# @napari_hook_implementation
# def napari_experimental_provide_dock_widget():
#     return [FolderBrowser]
